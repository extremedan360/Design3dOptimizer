"""Run exactly one small stage; no global installs or repository mutations."""
import argparse,subprocess,sys,time,os,shutil,json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--blender',default='blender')
    parser.add_argument('--stage',choices=['model','groom','rig','preview'],required=True)
    parser.add_argument('--device',choices=['auto','cpu','cuda'],default='auto')
    parser.add_argument('--output',type=Path,default=Path('artifacts/cuy'))
    parser.add_argument('--timeout',type=float,default=180)
    parser.add_argument('--max-gpu-mib',type=int,default=3200)
    parser.add_argument('--max-ram-mib',type=int,default=4096)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    expected=out/(args.stage+'-mediciones.json')
    before=expected.stat().st_mtime_ns if expected.exists() else None
    cmd=[args.blender,'--background','--factory-startup','--disable-autoexec','--python-exit-code','2',
         '--threads','4','--python',str(Path(__file__).with_name('generate.py')),'--','--output',str(out),'--stage',args.stage,'--device',args.device]
    smi=shutil.which('nvidia-smi');start=time.monotonic();peak_gpu=None;peak_ram=None
    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    with (out/(args.stage+'.log')).open('w',encoding='utf-8') as log:
        process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,creationflags=creationflags)
        try:
            while process.poll() is None:
                if time.monotonic()-start>args.timeout:raise RuntimeError('Stage exceeded timeout')
                if smi:
                    usage=subprocess.run([smi,'--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=3,creationflags=creationflags)
                    values=[int(v.strip()) for v in usage.stdout.splitlines() if v.strip().isdigit()]
                    if values:
                        peak_gpu=max(peak_gpu or 0,max(values))
                        if peak_gpu>args.max_gpu_mib:raise RuntimeError('Whole GPU observed usage exceeded limit')
                if os.name=='nt':
                    # GetProcessMemoryInfo measures the child working set, not exclusive physical RAM.
                    import ctypes
                    from ctypes import wintypes
                    class PMC(ctypes.Structure):
                        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
                    counters=PMC();counters.cb=ctypes.sizeof(counters)
                    fn=ctypes.windll.psapi.GetProcessMemoryInfo;fn.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD]
                    if fn(wintypes.HANDLE(int(process._handle)),ctypes.byref(counters),counters.cb):
                        peak_ram=max(peak_ram or 0,counters.WorkingSetSize/1048576)
                        if peak_ram>args.max_ram_mib:raise RuntimeError('Blender working set exceeded limit')
                time.sleep(.5)
        except BaseException:
            process.terminate();process.wait();raise
    if process.returncode:raise RuntimeError('Blender failed; inspect stage log')
    if not expected.exists() or expected.stat().st_mtime_ns==before:raise RuntimeError('Missing fresh completion report; do not infer success from exit code')
    result=json.loads(expected.read_text(encoding='utf-8'))
    assert isinstance(result,dict) and result
    resources={'stage':args.stage,'peak_whole_gpu_mib_observed':peak_gpu,'peak_blender_working_set_mib_observed':round(peak_ram,1) if peak_ram else None,'elapsed_seconds':round(time.monotonic()-start,2),
               'note':'Periodic samples may miss peaks; GPU includes other apps. RAM sampled only on Windows.'}
    (out/(args.stage+'-resources.json')).write_text(json.dumps(resources,indent=2),encoding='utf-8');print(json.dumps(resources,indent=2))

if __name__=='__main__':main()
