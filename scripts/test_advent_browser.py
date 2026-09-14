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
OUT=ROOT/'runs/advent-organic-village'
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
        navigate(OUT/'index.html','Boolean(window.adventCalendar)')
        def assert_viewport_fit(element):
            for width,height in [(1440,900),(1280,720),(1024,768),(390,844),(844,390)]:
                call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
                js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                box=js(f"(()=>{{const r=document.getElementById('{element}').getBoundingClientRect();return {{left:r.left,right:r.right,top:r.top,bottom:r.bottom}}}})()")
                assert box['left']>=0 and box['right']<=width+1, (element,width,height,box)
                assert box['top']>=0 and box['bottom']<=height+1, (element,width,height,box)
            call('Emulation.setDeviceMetricsOverride',{'width':1380,'height':900,'deviceScaleFactor':1,'mobile':False})
            js('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        assert_viewport_fit('scene')
        assert js('adventCalendar.data.days.length')==25
        total=js('adventCalendar.data.days.reduce((s,d)=>s+d.edges.length,0)')
        assert js('adventCalendar.state.renderedSegments')==total
        complete=js('scene.toDataURL()')
        (OUT/'canvas-full-scene.png').write_bytes(base64.b64decode(complete.split(',')[1]))
        js("document.getElementById('dots').click()")
        assert js('adventCalendar.state.renderedSegments')==0
        dots=js('scene.toDataURL()')
        assert dots!=complete
        js('adventCalendar.setProgress(12.5)')
        expected=js('adventCalendar.data.days.slice(0,12).reduce((s,d)=>s+d.edges.length,0)+Math.floor(adventCalendar.data.days[12].edges.length*.5)')
        assert js('adventCalendar.state.renderedSegments')==expected
        js("document.getElementById('reset').click()")
        assert js('scene.toDataURL()')==dots
        js("document.getElementById('play').click()")
        time.sleep(.25)
        js("document.getElementById('play').click()")
        paused=js('adventCalendar.state.progress')
        assert paused>0
        time.sleep(.12)
        assert js('adventCalendar.state.progress')==paused
        js("document.getElementById('source').click()")
        assert js('scene.hidden') is True
        js("document.getElementById('answer').click()")
        assert js('scene.toDataURL()')==complete
        shot=call('Page.captureScreenshot',{'format':'png'})
        (OUT/'browser-preview.png').write_bytes(base64.b64decode(shot['data']))
        for number in [1,13,25]:
            directory=OUT/f'day-{number:02}'
            navigate(directory/'index.html',f'Boolean(window.dotPuzzle && dotPuzzle.data.day=={number})')
            assert_viewport_fit('drawing')
            assert js('dotPuzzle.data.points.length')==243
            assert js('dotPuzzle.state.renderedSegments')==0
            assert js("document.getElementById('hint').checked") is False
            initial=js('drawing.toDataURL()')
            fingerprint=js('JSON.stringify(dotPuzzle.data.points)')
            count=js('dotPuzzle.data.edges.length')
            js("document.getElementById('answerTab').click()")
            assert js('dotPuzzle.state.renderedSegments')==count
            js("document.getElementById('reset').click()")
            assert js('drawing.toDataURL()')==initial
            js("document.getElementById('manual').click()")
            def click_point(index):
                position=js(f"(()=>{{const p=dotPuzzle.data.points[{index}],r=drawing.getBoundingClientRect();window.scrollBy(0,r.top+p.y*r.height/1200-500);const a=drawing.getBoundingClientRect();return {{x:a.left+p.x*a.width/1200,y:a.top+p.y*a.height/1200}}}})()")
                call('Input.dispatchMouseEvent',dict(type='mousePressed',button='left',clickCount=1,**position))
                call('Input.dispatchMouseEvent',dict(type='mouseReleased',button='left',clickCount=1,**position))
            first=js('dotPuzzle.data.strokes[0].points')
            second=js('dotPuzzle.data.strokes[1].points')
            for point in first:click_point(point-1)
            boundary=len(first)-1
            assert js('dotPuzzle.state.progress')==boundary
            assert js('dotPuzzle.state.started') is False
            click_point(second[0]-1)
            assert js('dotPuzzle.state.progress')==boundary
            assert js('dotPuzzle.state.started') is True
            click_point(second[1]-1)
            assert js('dotPuzzle.state.progress')==boundary+1
            js("document.getElementById('undo').click()")
            assert js('dotPuzzle.state.progress')==boundary
            assert js('JSON.stringify(dotPuzzle.data.points)')==fingerprint
        for name in ['puzzles','solutions','stroke-guides','assembly']:
            navigate(OUT/f'{name}.html',"document.readyState==='complete'")
            js('document.fonts.ready.then(()=>true)')
            call('Emulation.setEmulatedMedia',{'media':'print'})
            overflow=js("Array.from(document.querySelectorAll('.sheet')).map((e,i)=>({day:i+1,over:e.scrollHeight-e.clientHeight})).filter(x=>x.over>2)")
            assert not overflow, (name,overflow)
            pdf=call('Page.printToPDF',{'printBackground':True,'preferCSSPageSize':True,'displayHeaderFooter':False})
            (OUT/f'{name}.pdf').write_bytes(base64.b64decode(pdf['data']))
        print(f'Browser checks passed: 25 days, {total} assembled segments; exact reveal/reset; animation/pause; source isolation; days 1/13/25 manual pen lifts and undo. Four PDFs exported without HTML overflow.')
        connection.close()
    finally:
        process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill();process.wait()
