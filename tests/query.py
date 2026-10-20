"""Exercise the actual interposer against a fake GIO backend and private socket."""
import ctypes,os,socket,subprocess,sys,tempfile,threading
from pathlib import Path
if '--child' not in sys.argv:
    build=Path(os.environ['TYPELESS_TEST_QUERY_BUILD'])
    env={**os.environ,'LD_PRELOAD':str(build/'libtypeless-query.so')+':'+str(build/'libquery-backend.so')}
    subprocess.run([sys.executable,__file__,'--child'],env=env,check=True)
    raise SystemExit()
lib=ctypes.CDLL(None)
call=lib.g_dbus_connection_call_sync
call.argtypes=[ctypes.c_void_p]+[ctypes.c_char_p]*4+[ctypes.c_void_p]*2+[ctypes.c_int]*2+[ctypes.c_void_p]*2
call.restype=ctypes.c_void_p
lib.g_variant_get_child_value.argtypes=[ctypes.c_void_p,ctypes.c_size_t];lib.g_variant_get_child_value.restype=ctypes.c_void_p
lib.g_variant_get_string.argtypes=[ctypes.c_void_p,ctypes.c_void_p];lib.g_variant_get_string.restype=ctypes.c_char_p
lib.g_variant_unref.argtypes=[ctypes.c_void_p]
with tempfile.TemporaryDirectory() as d:
    os.environ.update(TYPELESS_OMARCHY_ACTIVE='1',TYPELESS_OMARCHY_PID=str(os.getpid()),XDG_RUNTIME_DIR=d)
    folder=Path(d)/'typeless-voice-ime';folder.mkdir();server=socket.socket(socket.AF_UNIX);server.bind(str(folder/'inject.sock'));server.listen()
    stop=threading.Event();server.settimeout(.1)
    reply=[b'FOCUSED_EDITABLE']
    def serve():
        while not stop.is_set():
            try:c,_=server.accept()
            except socket.timeout:continue
            with c:
                assert c.recv(64)==b'{"op":"ping"}'
                c.sendall(reply[0])
    worker=threading.Thread(target=serve);worker.start()
    def query(parameters=None,reply_type=None,cancellable=None,**changes):
        args=dict(bus=b'org.fcitx.Fcitx5',path=b'/controller',interface=b'org.fcitx.Fcitx.Controller1',method=b'CurrentInputMethod')
        args.update(changes)
        result=call(None,*args.values(),parameters,reply_type,0,800,cancellable,None)
        child=lib.g_variant_get_child_value(result,0);value=lib.g_variant_get_string(child,None).decode()
        lib.g_variant_unref(child);lib.g_variant_unref(result);return value
    try:
        for status in [b'FOCUSED_EDITABLE',b'UNFOCUSED',b'FOCUSED',b'PASSWORD']:
            reply[0]=status;assert query()=='typeless-voice'
        for changes in [dict(bus=b'other'),dict(path=b'/other'),dict(interface=b'other'),dict(method=b'SetCurrentIM')]:assert query(**changes)=='real-engine'
        lib.g_variant_new_string.argtypes=[ctypes.c_char_p];lib.g_variant_new_string.restype=ctypes.c_void_p
        parameter=lib.g_variant_new_string(b'not-an-empty-tuple')
        assert query(parameters=parameter)=='real-engine';lib.g_variant_unref(parameter)
        lib.g_variant_type_new.argtypes=[ctypes.c_char_p];lib.g_variant_type_new.restype=ctypes.c_void_p
        lib.g_variant_type_free.argtypes=[ctypes.c_void_p]
        result_type=lib.g_variant_type_new(b'(u)')
        assert query(reply_type=result_type)=='real-engine';lib.g_variant_type_free(result_type)
        lib.g_cancellable_new.restype=ctypes.c_void_p;lib.g_cancellable_cancel.argtypes=[ctypes.c_void_p];lib.g_object_unref.argtypes=[ctypes.c_void_p]
        cancellable=lib.g_cancellable_new();lib.g_cancellable_cancel(cancellable)
        assert query(cancellable=cancellable)=='real-engine';lib.g_object_unref(cancellable)
        os.environ['TYPELESS_OMARCHY_PID']='-1' ;assert query()=='real-engine'
        os.environ['TYPELESS_OMARCHY_PID']=str(os.getpid());os.environ['TYPELESS_OMARCHY_ACTIVE']='0';assert query()=='real-engine'
        os.environ['TYPELESS_OMARCHY_ACTIVE']='1';reply[0]=b'INVALID';assert query()=='real-engine'
        os.environ['XDG_RUNTIME_DIR']=d+'/missing';assert query()=='real-engine'
    finally:
        stop.set();worker.join();server.close()
print('PASS native GIO query scope, all endpoint states, foreign PID, other methods, disabled mode and missing/invalid bridge')
