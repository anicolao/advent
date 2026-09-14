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
OUT=ROOT/'runs/christmas-room-numbered-grid'
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
        navigate(OUT/'index.html','Boolean(window.numberedGrid)')
        assert js('numberedGrid.state.segments') == 0
        assert js('document.getElementById("draw").disabled') is True
        blank = js('document.getElementById("canvas").toDataURL()')
        (OUT/'blank.png').write_bytes(base64.b64decode(blank.split(',')[1]))
        js('document.getElementById("fill").click()')
        assert js('document.getElementById("draw").disabled') is False
        js('document.getElementById("draw").click()')
        time.sleep(.5)
        assert js('numberedGrid.state.segments') > 0
        js('document.getElementById("reset").click()')
        assert js('document.getElementById("canvas").toDataURL()') == blank
        # Real browser clicks connect numbers, including the start-only click.
        def click_node(node):
            position=js(f"(()=>{{const node={node},r=document.getElementById('canvas').getBoundingClientRect();return {{x:r.left+(100+node%61*36)*r.width/2360,y:r.top+(100+Math.floor(node/61)*36)*r.height/2360}}}})()")
            call('Input.dispatchMouseEvent',dict(type='mousePressed',button='left',clickCount=1,**position))
            call('Input.dispatchMouseEvent',dict(type='mouseReleased',button='left',clickCount=1,**position))
        route=js('numberedGrid.data.real_paths[0]')
        click_node(route[0])
        assert js('numberedGrid.state.segments') == 0
        for node in route[1:]:
            click_node(node)
        assert js('numberedGrid.state.segments') == len(route)-1
        assert js('numberedGrid.state.manual') == 0
        js('document.getElementById("next").click()')
        second=js('numberedGrid.data.real_paths[1]')
        click_node(second[0])
        assert js('numberedGrid.state.segments') == len(route)-1
        click_node(second[1])
        assert js('numberedGrid.state.segments') == len(route)
        # A wrong Sudoku digit really draws the corresponding decoy.
        js('document.getElementById("reset").click();document.getElementById("key").value=0;document.getElementById("key").dispatchEvent(new Event("change"));(()=>{const cell=numberedGrid.data.instructions[0].cell,input=document.querySelectorAll(".cell input")[cell];input.value=numberedGrid.data.solution[cell]%9+1;input.dispatchEvent(new Event("input"))})()')
        js('document.getElementById("draw").click()')
        time.sleep(1.5)
        assert js('JSON.stringify(numberedGrid.drawn.get(0)) === JSON.stringify(numberedGrid.data.instructions[0].choices[numberedGrid.entries[numberedGrid.data.instructions[0].cell]-1].nodes)')
        js('document.getElementById("all").click()')
        assert js('numberedGrid.state.segments') == 213
        # Save the same canvas rendering used by the interaction.
        for mode, labels, filename in [('puzzle',True,'connected'),('answer',False,'answer'),('original',False,'original')]:
            js(f'document.getElementById("view").value="{mode}";document.getElementById("labels").checked={str(labels).lower()};numberedGrid.render()')
            uri=js('document.getElementById("canvas").toDataURL()')
            (OUT/f'{filename}.png').write_bytes(base64.b64decode(uri.split(',')[1]))
        js('document.getElementById("labels").checked=true;document.getElementById("fill").click();document.getElementById("reset").click()')
        for w,h in [(1380,900),(1280,720),(390,844)]:
            call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
            js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            assert js('(()=>{const r=document.getElementById("canvas").getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1&&document.documentElement.scrollHeight<=innerHeight+1})()')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':950,'deviceScaleFactor':1,'mobile':False})
        js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        shot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-preview.png').write_bytes(base64.b64decode(shot['data']))
        js('document.getElementById("locate").click()')
        assert js('Number(document.getElementById("zoom").value)') == 3
        shot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-zoom.png').write_bytes(base64.b64decode(shot['data']))
        navigate(OUT/'review.html','Array.from(document.images).every(im=>im.complete && im.naturalWidth>0)')
        shot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'comparison.png').write_bytes(base64.b64decode(shot['data']))
        print('Passed: zero-line initial state; manual numbering and pen lifts; wrong answer draws decoy; animation; reset; all 213 correct lines; viewport fit; zoom locator.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
