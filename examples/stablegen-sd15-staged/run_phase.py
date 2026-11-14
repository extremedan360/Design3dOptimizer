"""One prepared phase on a fresh local server; run through run_guard.py."""
from pathlib import Path
import argparse,json,urllib.request,urllib.error,time,subprocess,sys,os,hashlib
import psutil

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('run',type=Path,help='Prepared isolated run directory')
parser.add_argument('stage',choices=('1','2','3'))
args=parser.parse_args()
if os.name!='nt':parser.error('This process runner is Windows-only')
root=args.run.resolve();stage=args.stage
job=json.loads((root/'run.json').read_text());settings=json.loads((root/'commands.json').read_text())[stage]
out=root/('phase'+stage);out.mkdir(exist_ok=False)
graphfile=Path(settings['graph']);assert hashlib.sha256(graphfile.read_bytes()).hexdigest()==job['graphSha256'][stage]
plugin=root/'custom_nodes/design3d_staged_sd15/__init__.py';assert hashlib.sha256(plugin.read_bytes()).hexdigest()==job['pluginSha256']
graph=json.loads(graphfile.read_text());command=settings['command'];port=command[command.index('--port')+1]
api='http://127.0.0.1:'+port;opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def request(path,data=None,timeout=4):
    payload=None if data is None else json.dumps(data).encode()
    try:
        with opener.open(urllib.request.Request(api+path,data=payload,headers={'Content-Type':'application/json'}),timeout=timeout) as r:return json.load(r)
    except urllib.error.HTTPError as error:raise RuntimeError('HTTP '+str(error.code)+' '+error.read(12000).decode(errors='replace')) from error
try:request('/system_stats',timeout=1)
except (urllib.error.URLError,TimeoutError):pass
else:raise RuntimeError('Existing backend preserved; not creating a duplicate')
env=os.environ.copy();env.pop('SSLKEYLOGFILE',None);env.update(settings['env']);env['PYTHONUNBUFFERED']='1'
start=time.monotonic();server=None;owned={};report={'stage':stage,'passed':False,'graphSha256':job['graphSha256'][stage],'sourceSha256':job['sourceSha256']}
try:
    with (out/'server.log').open('w',encoding='utf-8') as log:
        server=subprocess.Popen(command,cwd=settings['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        process=psutil.Process(server.pid);owned[(process.pid,process.create_time())]=process
        ready=False
        while time.monotonic()-start<100:
            for child in process.children(recursive=True):owned[(child.pid,child.create_time())]=child
            if server.poll() is not None:raise RuntimeError('Backend startup exit '+str(server.returncode))
            try:request('/system_stats');ready=True;break
            except (urllib.error.URLError,TimeoutError):time.sleep(.5)
        assert ready,'Readiness timeout'
        schema=request('/object_info',timeout=20);missing={n['class_type'] for n in graph.values()}-schema.keys();assert not missing,missing
        queued=request('/prompt',{'prompt':graph,'client_id':'staged-sd15-phase'+stage},timeout=20)
        assert 'prompt_id' in queued,queued;pid=queued['prompt_id'];report['promptId']=pid;print('PHASE_QUEUED',stage,pid,flush=True)
        while time.monotonic()-start<600:
            history=request('/history/'+pid)
            if pid in history:
                result=history[pid];report['status']=result.get('status')
                if result.get('status',{}).get('status_str')=='error':raise RuntimeError('Inference failed; see status messages')
                if result.get('status',{}).get('completed'):
                    report['outputs']=result['outputs'];report['passed']=True;break
            time.sleep(.75)
        assert report['passed'],'Phase timeout'
except Exception as error:report['error']=repr(error)
finally:
    if server:
        try:request('/free',{'unload_models':True,'free_memory':True},timeout=8)
        except Exception:pass
        for (pid,birth),process in reversed(list(owned.items())):
            try:
                if process.is_running() and process.create_time()==birth:process.terminate()
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
        try:server.wait(timeout=8)
        except subprocess.TimeoutExpired:server.kill();server.wait(timeout=8)
        # Windows venv launchers can finish before their interpreter child.
        _,alive=psutil.wait_procs(list(owned.values()),timeout=8)
        for process in alive:
            try:
                birth=next(b for (pid,b) in owned if pid==process.pid)
                if process.create_time()==birth:process.kill();process.wait(timeout=4)
            except (psutil.NoSuchProcess,psutil.TimeoutExpired):pass
    report['seconds']=round(time.monotonic()-start,3)
    report['ownedProcessTreeClosed']=all(not p.is_running() for p in owned.values())
    (out/'result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PHASE_RESULT',stage,report['passed'],report.get('error'),flush=True)
raise SystemExit(0 if report['passed'] else 1)
