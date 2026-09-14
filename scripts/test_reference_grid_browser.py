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
OUT=ROOT/'runs/christmas-room-reference-grid'
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
        navigate(OUT/'index.html','Boolean(window.referenceGrid)')
        assert js('referenceGrid.state.progress')==0
        assert js('referenceGrid.state.n')==61
        assert js('referenceGrid.state.renderedSegments')==0
        assert js('document.getElementById("hint").checked') is False
        blank=js('document.getElementById("blank").toDataURL()')
        assert js('document.getElementById("drawing").toDataURL()')==blank
        # Every tile starts with precisely the same visible pixels and labels.
        for day in range(1,26):
            js(f'document.getElementById("tile").value="{day}";document.getElementById("tile").dispatchEvent(new Event("change"))')
            assert js('document.getElementById("blank").toDataURL()')==blank
            assert js('document.getElementById("drawing").toDataURL()')==blank
        js('document.getElementById("tile").value="14";document.getElementById("tile").dispatchEvent(new Event("change"))')
        js('document.getElementById("complete").click()')
        assert js('referenceGrid.state.renderedSegments')==js('referenceGrid.state.total')
        assert js('document.getElementById("drawing").toDataURL()')!=blank
        js('document.getElementById("reset").click();document.getElementById("manual").click()')
        def click_node(node):
            position=js(f"(()=>{{const n=referenceGrid.state.n,p={node}-1,x=100+(p%n)*1000/(n-1),y=100+Math.floor(p/n)*1000/(n-1),r=document.getElementById('drawing').getBoundingClientRect();return {{x:r.left+x*r.width/1200,y:r.top+y*r.height/1200}}}})()")
            call('Input.dispatchMouseEvent',dict(type='mousePressed',button='left',clickCount=1,**position))
            call('Input.dispatchMouseEvent',dict(type='mouseReleased',button='left',clickCount=1,**position))
        first=js('referenceGrid.state.days[0].strokes[0].points')
        second=js('referenceGrid.state.days[0].strokes[1].points')
        for node in first:click_node(node)
        boundary=len(first)-1
        assert js('referenceGrid.state.progress')==boundary
        assert js('referenceGrid.state.started') is False
        click_node(second[0])
        assert js('referenceGrid.state.progress')==boundary
        assert js('referenceGrid.state.started') is True
        click_node(second[1])
        assert js('referenceGrid.state.progress')==boundary+1
        js('document.getElementById("undo").click()')
        assert js('referenceGrid.state.progress')==boundary
        js('document.getElementById("reset").click();document.getElementById("play").click()')
        time.sleep(.4)
        js('document.getElementById("play").click()')
        assert js('referenceGrid.state.progress')>0
        for w,h in [(1380,900),(1280,720),(390,844)]:
            call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
            js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            assert js('Array.from(document.querySelectorAll("canvas")).every(c=>{const r=c.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1;})')
        call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':950,'deviceScaleFactor':1,'mobile':False})
        js('document.getElementById("tile").value="all";document.getElementById("tile").dispatchEvent(new Event("change"));document.getElementById("showGrid").click();document.getElementById("complete").click()')
        js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        shot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-preview.png').write_bytes(base64.b64decode(shot['data']))
        print('Browser passed: all 25 blank sheets pixel-identical; only snapped edges revealed; manual pen lifts add no connector; undo, animation, reset and viewport fit.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
