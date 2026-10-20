#!/usr/bin/python
"""GUI regression: one real click on our own GTK button under the idle HUD.
Requires ydotool/ydotoold and /dev/uinput access; closes its private daemon.
Do not move the mouse during the short test; unrelated activity aborts it.
"""
import json,subprocess as sp,time,tempfile,os
from pathlib import Path
def h(*a):return sp.check_output(['hyprctl',*a],text=True).strip()
def j(*a):return json.loads(h(*a,'-j'))
def focus(a):h('eval',f'local old=hl.get_config("cursor:no_warps"); hl.config({{cursor={{no_warps=true}}}}); hl.dispatch(hl.dsp.focus({{window="address:{a}"}})); hl.config({{cursor={{no_warps=old}}}})')
root=Path(__file__).resolve().parent.parent
original=j('activewindow').get('address');cursor=j('cursorpos')
with tempfile.TemporaryDirectory(prefix='typeless-pointer-') as d:
 sock=d+'/ydotool.sock';env={**os.environ,'YDOTOOL_SOCKET':sock};out=Path(d)/'clicks'
 daemon=sp.Popen(['ydotoold','--socket-path='+sock],stdout=sp.DEVNULL,stderr=sp.DEVNULL)
 p=sp.Popen(['python',str(root/'tests/input-probe.py'),str(out),'--click-target'],stdout=sp.DEVNULL,stderr=sp.DEVNULL)
 try:
  for _ in range(60):
   clients=j('clients');probe=next((w for w in clients if w['pid']==p.pid),None)
   if probe and Path(sock).exists():break
   time.sleep(.1)
  assert probe and Path(sock).exists(),'test fixtures not ready'
  time.sleep(1)
  focus(probe['address']);time.sleep(.3)
  clients=j('clients');probe=next(w for w in clients if w['pid']==p.pid);status=next(w for w in clients if w['class']=='Typeless' and w['title'].startswith('Status'))
  x=max(probe['at'][0],status['at'][0])+80;y=max(probe['at'][1],status['at'][1])+80
  assert x<min(probe['at'][0]+probe['size'][0],status['at'][0]+status['size'][0]) and y<min(probe['at'][1]+probe['size'][1],status['at'][1]+status['size'][1]),'no safe overlapping test point'
  h('dispatch',f'hl.dsp.cursor.move({{x={x},y={y}}})');time.sleep(.01)
  actual=j('cursorpos'); print('test point',x,y,'actual',actual,flush=True); assert actual=={'x':x,'y':y},'cursor changed before click'
  assert j('activewindow').get('address')==probe['address'],'focus changed before click'
  assert next(w for w in j('clients') if w['address']==status['address'])['title']==status['title'], 'HUD changed; click aborted'
  sp.run(['ydotool','click','0xC0'],env=env,check=True,stdout=sp.DEVNULL);time.sleep(.3)
  after=j('cursorpos');n=int(out.read_text()) if out.exists() else 0
  stable=after=={"x":x,"y":y} and j("activewindow").get("address")==probe["address"]
  print(f'{"PASS" if n==1 and stable else "FAIL"}: real pointer click reaches underlying GTK button: {n}; cursor stayed={after=={"x":x,"y":y}}; after={after}; active={j("activewindow").get("class")}')
  raise SystemExit(0 if n==1 and stable else 1)
 finally:
  p.terminate();p.wait(timeout=3);daemon.terminate();daemon.wait(timeout=3)
  if original:focus(original)
  h('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
