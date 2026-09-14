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
OUT=ROOT/'runs/dot-to-dot-reindeer'
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
        call('Page.navigate',{'url':(OUT/'index.html').as_uri()})
        for _ in range(100):
            if js('Boolean(window.dotPuzzle)'):break
            time.sleep(.1)
        assert js('dotPuzzle.data.points.length')==243
        assert js('dotPuzzle.state.renderedSegments')==0
        before=js('drawing.toDataURL()')
        fingerprint=js('JSON.stringify(dotPuzzle.data.points)')
        js("document.getElementById('answerTab').click()")
        assert js('dotPuzzle.state.progress')==243
        assert js('dotPuzzle.state.renderedSegments')==243
        complete=js('drawing.toDataURL()')
        assert before!=complete
        (OUT/'canvas-connected.png').write_bytes(base64.b64decode(complete.split(',')[1]))
        js("document.getElementById('reset').click()")
        assert js('drawing.toDataURL()')==before
        (OUT/'canvas-dots.png').write_bytes(base64.b64decode(before.split(',')[1]))
        js("document.getElementById('progress').value=81;document.getElementById('progress').dispatchEvent(new Event('input'))")
        assert js('dotPuzzle.state.renderedSegments')==81
        js("document.getElementById('reset').click();document.getElementById('manual').click()")
        def click_point(index):
            js("drawing.scrollIntoView({block:'end'})")
            position=js(f"(()=>{{const p=dotPuzzle.data.points[{index}],r=drawing.getBoundingClientRect();return {{x:r.left+p.x*r.width/1200,y:r.top+p.y*r.height/1200}}}})()")
            call('Input.dispatchMouseEvent',dict(type='mousePressed',button='left',clickCount=1,**position))
            call('Input.dispatchMouseEvent',dict(type='mouseReleased',button='left',clickCount=1,**position))
        click_point(0)
        assert js('dotPuzzle.state.started') is True
        click_point(1)
        assert js('dotPuzzle.state.progress')==1
        click_point(10)
        assert js('dotPuzzle.state.progress')==1
        js("document.getElementById('undo').click()")
        assert js('dotPuzzle.state.progress')==0
        js("document.getElementById('play').click()")
        time.sleep(.35)
        assert 0<js('dotPuzzle.state.progress')<243
        js("document.getElementById('play').click()")
        stopped=js('dotPuzzle.state.progress')
        time.sleep(.15)
        assert js('dotPuzzle.state.progress')==stopped
        js("document.getElementById('sourceTab').click()")
        assert js("document.getElementById('source').hidden") is False
        assert js('drawing.hidden') is True
        js("document.getElementById('puzzleTab').click()")
        assert js('dotPuzzle.state.renderedSegments')==0
        assert js('JSON.stringify(dotPuzzle.data.points)')==fingerprint
        js('window.scrollTo(0,0)')
        screenshot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-preview.png').write_bytes(base64.b64decode(screenshot['data']))
        print('Browser checks passed: 243 points; reveal/reset; scrub; real pointer drawing; wrong-point rejection; undo; animation/pause; source isolation; unchanged point data.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
