"""Exercise the standalone puzzle in Chrome over its local DevTools connection."""
import base64
import json
import re
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

import websocket

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.site-review'
OUT.mkdir(exist_ok=True)

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'_site'),**kwargs)
    def do_GET(self):
        if self.path.startswith('/advent/'):
            self.path=self.path[len('/advent'):]
        try:return super().do_GET()
        except (BrokenPipeError,ConnectionResetError):return
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
Thread(target=server.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{server.server_port}/'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

with tempfile.TemporaryDirectory(prefix='dot-browser-') as profile:
    process=subprocess.Popen([CHROME,'--headless','--disable-gpu','--remote-debugging-port=0',
                              f'--user-data-dir={profile}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        portfile=Path(profile)/'DevToolsActivePort'
        for _ in range(100):
            if portfile.exists():break
            time.sleep(.1)
        port=portfile.read_text().splitlines()[0]
        pages=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
        page=next(p for p in pages if p['type']=='page')
        connection=websocket.create_connection(page['webSocketDebuggerUrl'],suppress_origin=True,timeout=15)
        counter=0
        def call(method,params=None):
            global counter
            counter+=1
            connection.send(json.dumps({'id':counter,'method':method,'params':params or {}}))
            while True:
                response=json.loads(connection.recv())
                if response.get('method')=='Runtime.exceptionThrown':
                    raise AssertionError(response)
                if response.get('id')==counter:
                    if 'error' in response:raise AssertionError(response)
                    return response.get('result',{})
        def js(expression):
            result=call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
            if 'exceptionDetails' in result:raise AssertionError(result)
            return result.get('result',{}).get('value')
        call('Runtime.enable')
        call('Page.enable')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':1100,'deviceScaleFactor':1,'mobile':False})
        def navigate(path,ready):
            call('Page.navigate',{'url':BASE+path})
            for _ in range(100):
                if js(f'location.href === {json.dumps(BASE+path)} && document.readyState === \"complete\" && ({ready})'):return
                time.sleep(.1)
            raise AssertionError(f'Page failed to load: {path}')
        navigate('2026/','Boolean(window.advent)')
        assert js('document.querySelectorAll(".calendar a").length')==25
        assert js('document.querySelector(".calendar a").textContent.includes("25")')
        assert js('document.querySelectorAll("#sceneImage img").length')==0
        js('document.querySelector("#fullScene summary").click()')
        js('new Promise(resolve=>setTimeout(resolve,100))')
        assert js('document.querySelectorAll("#sceneImage img").length')==1
        js('document.querySelector("#fullScene summary").click()')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':1000,'deviceScaleFactor':1,'mobile':False})
        (OUT/'calendar.png').write_bytes(base64.b64decode(call('Page.captureScreenshot',{'format':'png'})['data']))
        for day in range(1,26):
            navigate(f'2026/day/{day:02}/','Boolean(window.advent) && document.getElementById("tileImage").complete')
            assert js('advent.mode')=='dots'
            assert js('document.getElementById("tileImage").naturalWidth')>0
            assert js('document.querySelectorAll(".sudoku td").length')==0
            assert js('document.querySelectorAll(".commands tbody tr").length')==0
            assert js('document.querySelectorAll(".day-sidebar")[0].textContent.includes("six-inch")')
            for mode in ('solved','art','dots'):
                js(f'document.querySelector("[data-mode={mode}]").click()')
                js('document.getElementById("tileImage").decode()')
                assert js('advent.mode')==mode
                assert js('document.getElementById("download").href').endswith(f'/{mode}.svg')
            js('document.querySelector("#sudokuAnswer summary").click()')
            js('new Promise(resolve=>setTimeout(resolve,20))')
            assert js('document.querySelectorAll(".sudoku td").length')==81
            assert js('Array.from(document.querySelectorAll(".sudoku td")).map(x=>Number(x.textContent)).join("")')==js(f'advent.data.days[{day-1}].sudoku.solution.flat().join("")')
        for width,height in [(1380,900),(390,844)]:
            call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
            js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            assert js('document.documentElement.scrollWidth<=innerWidth+1')
            assert js('(()=>{const r=document.getElementById("drawingPanel").getBoundingClientRect();return r.width<=innerWidth&&r.height<=innerHeight})()')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':1000,'deviceScaleFactor':1,'mobile':False})
        navigate('2026/day/01/','Boolean(window.advent)')
        js('document.querySelector("[data-mode=solved]").click();document.getElementById("tileImage").decode()')
        (OUT/'day-solved.png').write_bytes(base64.b64decode(call('Page.captureScreenshot',{'format':'png'})['data']))
        # Exercise the visible print form and ensure it routes to the selected mode.
        js('document.getElementById("printForm").elements.to.value=2;document.querySelector("#printForm button").click()')
        for _ in range(100):
            if js('Boolean(window.printReady)'):break
            time.sleep(.1)
        assert js('location.pathname').endswith('/2026/print/')
        assert js('new URLSearchParams(location.search).get("mode")')=='solved'
        assert js('document.querySelectorAll(".print-sheet").length')==2
        for mode,count in [('dots',3),('solved',3),('art',25)]:
            navigate(f'2026/print/?from=1&to={count}&mode={mode}','Boolean(window.printReady)')
            call('Emulation.setEmulatedMedia',{'media':'print'})
            assert abs(js('document.querySelector(".print-sheet img").getBoundingClientRect().width')-633.6)<.1
            result=call('Page.printToPDF',{'paperWidth':8.5,'paperHeight':11,'printBackground':True,'displayHeaderFooter':False,'scale':1})
            pdf=base64.b64decode(result['data'])
            assert len(re.findall(rb'/Type\s*/Page\b',pdf))==count
            (OUT/f'{mode}.pdf').write_bytes(pdf)
            call('Emulation.setEmulatedMedia',{'media':''})
        navigate('2026/print/?from=20&to=1&mode=art','document.readyState === "complete"')
        assert js('document.getElementById("print").hidden')
        assert js('document.querySelectorAll(".print-sheet").length')==0
        for path in ('', '2026/', '2026/day/01/', 'experiments/'):
            navigate(path, 'document.readyState === "complete"')
            assert not js('Array.from(document.querySelectorAll("a")).some(a=>/\\/(experiments|runs)\\//.test(a.href))')
        links=json.load(urllib.request.urlopen(BASE+'links/2026-days.json'))
        assert len(links)==25
        for day,link in enumerate(links,1):
            assert link=={'day':day,'url':f'https://advent.annasdadpress.com/2026/day/{day:02}/'}
        # Relative assets also survive the old project-prefix layout.
        navigate('advent/2026/day/01/', 'Boolean(window.advent) && document.getElementById("tileImage").naturalWidth>0')
        assert js('document.querySelector("link[rel=canonical]").href')==links[0]['url']
        print('Passed: 25 deep links, exact Sudoku answers, explicit spoilers, all drawing modes, no experiment navigation, QR targets, both host layouts, mobile layout, print form and 3/3/25-page PDFs at six-inch scale.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
        server.shutdown()
