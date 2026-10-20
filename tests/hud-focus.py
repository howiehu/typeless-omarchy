#!/usr/bin/python
"""GUI regression: simulate Status focus, commit only to an isolated GTK receiver."""
import json,os,socket,subprocess,tempfile,time
from pathlib import Path
root=Path(__file__).resolve().parent.parent
def hypr(*args):return subprocess.check_output(['hyprctl',*args],text=True)
original=json.loads(hypr('activewindow','-j')).get('address')
def focus_without_warp(address):
 # Scope the test's own focus transitions too; the delayed production callback
 # runs after this setting has already been restored.
 hypr('eval', 'local old=hl.get_config("cursor:no_warps"); '
      'hl.config({cursor={no_warps=true}}); '
      f'hl.dispatch(hl.dsp.focus({{window="address:{address}"}})); '
      'hl.config({cursor={no_warps=old}})')
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'received';p=subprocess.Popen(['python',str(root/'tests/input-probe.py'),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for _ in range(50):
   clients=json.loads(hypr('clients','-j'));probe=next((c for c in clients if c['pid']==p.pid),None)
   if probe:break
   time.sleep(.1)
  assert probe,'no isolated input probe'
  status=next((c for c in clients if c.get('class')=='Typeless' and c.get('title','').startswith('Status [') or c.get('class')=='Typeless' and c.get('title')=='Status'),None)
  assert status, 'active HUD required; idle HUD must remain excluded from pointer focus'
  focus_without_warp(probe["address"]);time.sleep(.25)
  cursor_before=json.loads(hypr('cursorpos','-j'))
  cursor_policy_before=hypr('getoption','cursor:no_warps','-j')
  focus_without_warp(status["address"]);time.sleep(.2)
  cursor_after=json.loads(hypr('cursorpos','-j'))
  assert cursor_before==cursor_after, 'Status focus restoration warped the cursor'
  assert cursor_policy_before==hypr('getoption','cursor:no_warps','-j'), 'cursor policy changed'
  active=json.loads(hypr('activewindow','-j')).get('address')
  assert active in [probe['address'], status['address']], 'user focus changed; no commit attempted'
  token='Omarchy-HUD-focus-probe-42'
  with socket.socket(socket.AF_UNIX) as c:
   c.connect(os.environ['XDG_RUNTIME_DIR']+'/typeless-voice-ime/inject.sock');c.sendall(json.dumps({'op':'commit','text':token}).encode());c.shutdown(socket.SHUT_WR);reply=c.recv(100).decode()
  time.sleep(.2)
  received=out.read_text() if out.exists() else ''
  passed=active==probe['address'] and received==token
  print(('PASS' if passed else 'FAIL')+': Status focus transition -> original input restored without cursor warp -> exact synthetic commit; reply='+reply)
  raise SystemExit(0 if passed else 1)
 finally:
  p.terminate();p.wait(timeout=3)
  if original:focus_without_warp(original)
