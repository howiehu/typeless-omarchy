#!/usr/bin/python
"""GUI regression: simulate Status focus, commit only to an isolated GTK receiver."""
import json,os,socket,subprocess,tempfile,time
from pathlib import Path
root=Path(__file__).resolve().parent.parent
def hypr(*args):return subprocess.check_output(['hyprctl',*args],text=True)
original=json.loads(hypr('activewindow','-j')).get('address')
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'received';p=subprocess.Popen(['python',str(root/'tests/input-probe.py'),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for _ in range(50):
   clients=json.loads(hypr('clients','-j'));probe=next((c for c in clients if c['pid']==p.pid),None)
   if probe:break
   time.sleep(.1)
  assert probe,'no isolated input probe'
  status=next(c for c in clients if c.get('class')=='Typeless' and c.get('title')=='Status')
  hypr('dispatch',f'hl.dsp.focus({{window="address:{probe["address"]}"}})');time.sleep(.25)
  hypr('dispatch',f'hl.dsp.focus({{window="address:{status["address"]}"}})');time.sleep(.2)
  active=json.loads(hypr('activewindow','-j')).get('address')
  token='Omarchy-HUD-focus-probe-42'
  with socket.socket(socket.AF_UNIX) as c:
   c.connect(os.environ['XDG_RUNTIME_DIR']+'/typeless-voice-ime/inject.sock');c.sendall(json.dumps({'op':'commit','text':token}).encode());c.shutdown(socket.SHUT_WR);reply=c.recv(100).decode()
  time.sleep(.2)
  received=out.read_text() if out.exists() else ''
  passed=active==probe['address'] and received==token
  print(('PASS' if passed else 'FAIL')+': Status focus transition -> original input restored -> exact synthetic commit; reply='+reply)
  raise SystemExit(0 if passed else 1)
 finally:
  p.terminate();p.wait(timeout=3)
  if original:hypr('dispatch',f'hl.dsp.focus({{window="address:{original}"}})')
