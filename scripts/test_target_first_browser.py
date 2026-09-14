"""Exercise the standalone puzzle in Chrome over its local DevTools connection."""
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

import websocket

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/christmas-room-proof'
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
            call('Page.navigate',{'url':path.as_uri()})
            for _ in range(100):
                if js(f'location.href === {json.dumps(path.as_uri())} && document.readyState === \"complete\" && ({ready})'):return
                time.sleep(.1)
            raise AssertionError(f'Page failed to load: {path}')
        navigate(OUT/'index.html','Boolean(window.reductionProof)')
        js('new Promise(resolve=>{if(document.getElementById("before").width===1500)setTimeout(resolve,300);else resolve();})')
        assert js('reductionProof.data.days.length')==25
        assert js('reductionProof.data.days.every(d=>d.points.length===243)')
        lines=js('document.getElementById("after").toDataURL()')
        source=js('document.getElementById("before").toDataURL()')
        assert source!=lines
        js('document.getElementById("dots").click()')
        assert js('document.getElementById("after").toDataURL()')!=lines
        js('document.getElementById("lines").click()')
        assert js('document.getElementById("after").toDataURL()')==lines
        js('document.getElementById("tile").value="14";document.getElementById("tile").dispatchEvent(new Event("change"))')
        assert js('document.getElementById("after").width')==1200
        assert '243 used dots' in js('document.getElementById("afterHeading").textContent')
        js('document.getElementById("numbers").click()')
        for w,h in [(1380,900),(1280,720),(390,844)]:
            call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
            js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            assert js('Array.from(document.querySelectorAll("canvas")).every(c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1;})')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':1000,'deviceScaleFactor':1,'mobile':False})
        js('document.getElementById("tile").value="all";document.getElementById("tile").dispatchEvent(new Event("change"));document.getElementById("grid").click()')
        js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        screenshot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-comparison.png').write_bytes(base64.b64decode(screenshot['data']))
        print('Source/reduction browser checks passed: source isolation, line/dot toggles, 243-dot tile view, numbering and three viewport sizes.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
