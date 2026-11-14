"""Run only an owned process tree; retain resource failures and never stop user apps."""
import argparse,json,subprocess,time,os
from pathlib import Path
import psutil

ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--timeout',type=int,default=240);ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
if a.command and a.command[0]=='--':a.command=a.command[1:]
if os.name!='nt':ap.error('This resource guard is Windows-only')
if a.timeout<=0:ap.error('Timeout must be positive')
assert a.command and not a.out.exists();a.out.mkdir(parents=True)
rows=[];p=None;owned={};failed=None;code=None;t=time.monotonic()
def sample():
    ram=psutil.virtual_memory().available
    r=subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert r.returncode==0,'GPU monitor unavailable'
    gpu=max(int(x) for x in r.stdout.splitlines() if x.strip())
    row={'seconds':round(time.monotonic()-t,3),'availableRamBytes':ram,'wholeGpuMiB':gpu};rows.append(row)
    if ram<2*1024**3:raise RuntimeError('RAM below 2 GiB')
    if gpu>3600:raise RuntimeError('Total GPU above 3600 MiB')
    if time.monotonic()-t>a.timeout:raise RuntimeError('Owned task timeout')
try:
    sample()
    with (a.out/'process.log').open('w',encoding='utf-8') as log:
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        p=subprocess.Popen(a.command,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
        root=psutil.Process(p.pid);owned[(root.pid,root.create_time())]=root
        while p.poll() is None:
            for child in root.children(recursive=True):owned[(child.pid,child.create_time())]=child
            sample();time.sleep(.75)
        code=p.returncode
        if code:raise RuntimeError('Owned process exit '+str(code))
except Exception as error:failed=str(error)
finally:
    if p:
        for (pid,birth),proc in reversed(list(owned.items())):
            try:
                if proc.is_running() and proc.create_time()==birth:proc.terminate()
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
        try:p.wait(timeout=8)
        except subprocess.TimeoutExpired:p.kill();p.wait(timeout=8)
        _,alive=psutil.wait_procs(list(owned.values()),timeout=8)
        for proc in alive:
            try:
                birth=next(b for (pid,b) in owned if pid==proc.pid)
                if proc.create_time()==birth:proc.kill();proc.wait(timeout=4)
            except (psutil.NoSuchProcess,psutil.TimeoutExpired):pass
    closed=all(not proc.is_running() for proc in owned.values())
    if not closed:failed=failed or 'Owned process tree did not close'
    report={'ownedProcessTreeClosed':closed,'passed':failed is None,'failure':failed,'exitCode':code,'seconds':round(time.monotonic()-t,3),'minAvailableRamBytes':min((r['availableRamBytes'] for r in rows),default=None),'peakWholeGpuMiBObserved':max((r['wholeGpuMiB'] for r in rows),default=None),'sampling':'0.75s delay plus query overhead; whole GPU includes other processes; short peaks may be missed','readings':rows,'command':a.command,'ownedProcesses':[{'pid':pid,'birth':birth} for pid,birth in owned]}
    (a.out/'resources.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('readings','command','ownedProcesses')}),flush=True)
raise SystemExit(0 if failed is None else 1)
