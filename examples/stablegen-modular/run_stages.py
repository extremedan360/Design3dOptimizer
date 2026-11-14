"""Checkpointed StableGen/TRELLIS.2 proof on an 18GiB Apple Silicon machine."""
from pathlib import Path
import importlib.util,copy,json,os,requests,shutil,subprocess,sys,time,psutil,hashlib
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--comfy',type=Path,required=True)
parser.add_argument('--stablegen',type=Path,required=True)
parser.add_argument('--comfy-python',type=Path,required=True)
parser.add_argument('--reference',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--prepare-only',action='store_true',help='Write graphs only; no server or inference')
a=parser.parse_args()
COMFY=a.comfy.resolve();OUT=a.output.resolve();BASE=OUT/'runtime';ROOT=BASE
LOCAL=OUT/'local-cache';INP=BASE/'comfy-input';GEN=BASE/'comfy-output';URL='http://127.0.0.1:8190'
for directory in [OUT,BASE,LOCAL,INP,GEN]:directory.mkdir(parents=True,exist_ok=True)
reference=INP/'referencia-cuy-modular.jpg'
if reference.exists() and reference.read_bytes()!=a.reference.read_bytes():
 raise RuntimeError('Reference changed: use a fresh output folder; previous run preserved')
shutil.copyfile(a.reference,reference)
spec=importlib.util.spec_from_file_location('stablegen_graph',a.stablegen.resolve()/'stablegen/mesh_gen/trellis2_graph.py')
sg=importlib.util.module_from_spec(spec);spec.loader.exec_module(sg)

base,roles=sg.build_trellis2_prompt('referencia-cuy-modular.jpg',resolution='512',seed=13112026,ss_steps=12,shape_steps=12,texture=False,remove_background=True,background='black',remesh=False,target_faces=None,prefix='cuy_stablegen_modular_13112026')
base[roles['unet']]['inputs']['unet_name']='trellis_2_int8_convrot.safetensors'
def custom(cls,**inputs):return {'class_type':cls,'inputs':inputs}
def keep(graph,outputs):
 seen=set()
 def visit(n):
  if n in seen:return
  seen.add(n)
  for value in graph[n]['inputs'].values():
   if isinstance(value,list) and len(value)==2 and isinstance(value[0],str) and isinstance(value[1],int) and value[0] in graph:visit(value[0])
 for n in outputs:visit(n)
 return {n:graph[n] for n in graph if n in seen}
def stage(number):
 g=copy.deepcopy(base)
 if number==1:
  g['90']=custom('CuySaveConditioning',value=[roles['conditioning'],0],checkpoint='image_positive')
  g['91']=custom('CuySaveConditioning',value=[roles['conditioning'],1],checkpoint='image_negative')
  g['92']=custom('SaveImage',images=[roles['crop'],0],filename_prefix='modular/recorte')
  return keep(g,['90','91','92'])
 if number==2:
  g['71']=custom('CuyLoadConditioning',checkpoint='image_positive');g['72']=custom('CuyLoadConditioning',checkpoint='image_negative')
  g[roles['ss_sampler']]['inputs'].update(positive=['71',0],negative=['72',0])
  g['90']=custom('SaveLatent',samples=[roles['ss_sampler'],0],filename_prefix='modular/estructura')
  return keep(g,['90'])
 if number==3:
  g['71']=custom('LoadLatent',latent='modular_structure.latent')
  g['72']=custom('CuyLoadConditioning',checkpoint='image_positive');g['73']=custom('CuyLoadConditioning',checkpoint='image_negative')
  g[roles['structure']]['inputs']['samples']=['71',0]
  g[roles['shape_stage']]['inputs'].update(positive=['72',0],negative=['73',0])
  g['90']=custom('CuySaveConditioning',value=[roles['shape_stage'],0],checkpoint='shape_positive')
  g['91']=custom('CuySaveConditioning',value=[roles['shape_stage'],1],checkpoint='shape_negative')
  g['92']=custom('CuySaveLatent',value=[roles['shape_stage'],2],checkpoint='shape_initial')
  return keep(g,['90','91','92'])
 if number==4:
  g['71']=custom('CuyLoadLatent',checkpoint='shape_initial')
  g['72']=custom('CuyLoadConditioning',checkpoint='shape_positive');g['73']=custom('CuyLoadConditioning',checkpoint='shape_negative')
  g[roles['shape_sampler']]['inputs'].update(positive=['72',0],negative=['73',0],latent_image=['71',0])
  g['90']=custom('CuySaveLatent',value=[roles['shape_sampler'],0],checkpoint='shape_sampled')
  return keep(g,['90'])
 if number==5:
  g['71']=custom('CuyLoadLatent',checkpoint='shape_sampled')
  g[roles['shape']]['inputs']['samples']=['71',0]
  return keep(g,[roles['export']])
 raise ValueError(number)
(OUT/'etapas').mkdir(exist_ok=True);(OUT/'checkpoints').mkdir(exist_ok=True)
graphs=[stage(n) for n in range(1,6)]
parts=[(INP/'referencia-cuy-modular.jpg').read_bytes(),Path(spec.origin).read_bytes(),(COMFY/'custom_nodes/cuy_checkpoints/__init__.py').read_bytes(),json.dumps(graphs,sort_keys=True).encode()]
signature=hashlib.sha256(b''.join(parts)).hexdigest()
manifest=OUT/'entorno/ensayo.json'
if manifest.exists() and json.loads(manifest.read_text())['signature']!=signature:
 raise RuntimeError('Reference, graph or checkpoint adapter changed. Preserve this experiment and create a separate run; do not reuse its checkpoints.')
manifest.parent.mkdir(parents=True,exist_ok=True)
manifest.write_text(json.dumps({'signature':signature,'seed':13112026,'reference':'local reference (not redistributed)','resolution':512,'steps':12,'texture':False,'provenance':'StableGen upstream graph; local checkpoint orchestration; INT8 weight-only MPS.'},indent=2))
# Input is already copied to the isolated input directory by setup.
for n,graph in enumerate(graphs,1):(OUT/'etapas'/f'{n}-grafo.json').write_text(json.dumps(graph,indent=2)+'\n')
if a.prepare_only:
 print('PREPARED_ONLY',signature);sys.exit(0)
def server(number):
 try:
  requests.get(URL+'/system_stats',timeout=2)
 except requests.RequestException:pass
 else:raise RuntimeError('Port 8190 already has a server; refusing to use or modify another session')
 env=os.environ.copy();env.update(PYTORCH_ENABLE_MPS_FALLBACK='1',PYTORCH_MPS_HIGH_WATERMARK_RATIO='1.0',PYTORCH_MPS_LOW_WATERMARK_RATIO='0.8',HF_HOME=str(LOCAL/'cache/huggingface'),XDG_CACHE_HOME=str(LOCAL/'cache'),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',VECLIB_MAXIMUM_THREADS='4',NUMEXPR_NUM_THREADS='4')
 log=(BASE/f'stage-{number}-server.log').open('w')
 cmd=[str(a.comfy_python.resolve()),'-u',str(COMFY/'main.py'),'--listen','127.0.0.1','--port','8190','--output-directory',str(GEN),'--input-directory',str(INP),'--user-directory',str(BASE/'comfy-user'),'--disable-auto-launch','--reserve-vram','4','--preview-method','none']
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 for _ in range(120):
  if proc.poll() is not None:raise RuntimeError('Server exited before health check')
  try:
   if requests.get(URL+'/system_stats',timeout=2).ok:return proc,log
  except requests.RequestException:pass
  time.sleep(1)
 proc.terminate();raise TimeoutError('Server startup')
def stop(proc,log):
 proc.terminate()
 try:proc.wait(timeout=20)
 except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
 log.close()
for number in range(1,6):
 resultfile=OUT/'etapas'/f'{number}-resultado.json'
 if resultfile.exists() and json.loads(resultfile.read_text()).get('success') and json.loads(resultfile.read_text()).get('signature')==signature:
  print('REUSE_STAGE',number,flush=True);continue
 print('START_STAGE',number,flush=True)
 proc,log=server(number)
 start=time.monotonic();swap0=psutil.swap_memory().used;peak_swap=swap0;min_available=psutil.virtual_memory().available
 try:
  r=requests.post(URL+'/prompt',json={'prompt':stage(number),'client_id':f'cuy-stablegen-stage-{number}'},timeout=60)
  submit=r.json();(OUT/'etapas'/f'{number}-submit.json').write_text(json.dumps(submit,indent=2)+'\n');r.raise_for_status()
  pid=submit['prompt_id'];print('PROMPT',number,pid,flush=True)
  with (OUT/'etapas'/f'{number}-memoria.jsonl').open('w') as mon:
   while time.monotonic()-start<3600:
    if proc.poll() is not None:raise RuntimeError('Server process exited')
    h=requests.get(URL+'/history/'+pid,timeout=30).json();m=psutil.virtual_memory();sw=psutil.swap_memory();peak_swap=max(peak_swap,sw.used);min_available=min(min_available,m.available)
    sample={'stage':number,'elapsed_s':round(time.monotonic()-start),'available_gib':round(m.available/1024**3,2),'swap_gib':round(sw.used/1024**3,2),'new_swap_gib':round((sw.used-swap0)/1024**3,2)}
    mon.write(json.dumps(sample)+'\n');mon.flush();print('STATUS',sample,flush=True)
    if h:
     (OUT/'etapas'/f'{number}-history.json').write_text(json.dumps(h,indent=2)+'\n')
     if h[pid]['status'].get('status_str')!='success':raise RuntimeError('ComfyUI execution failed: '+json.dumps(h[pid]['status']))
     break
    if sw.used-swap0>4*1024**3 or (m.available<0.8*1024**3 and sw.used-swap0>2*1024**3):
     requests.post(URL+'/interrupt',json={'prompt_id':pid},timeout=10);raise RuntimeError('Memory safety threshold exceeded')
    time.sleep(15)
   else:
    requests.post(URL+'/interrupt',json={'prompt_id':pid},timeout=10);raise TimeoutError('Stage exceeded one hour')
  result={'success':True,'signature':signature,'stage':number,'prompt_id':pid,'seconds':round(time.monotonic()-start,2),'peak_swap_gib':round(peak_swap/1024**3,2),'min_available_gib':round(min_available/1024**3,2)}
  resultfile.write_text(json.dumps(result,indent=2)+'\n');print('DONE_STAGE',number,flush=True)
 finally:stop(proc,log)
 if number==2:
  latents=sorted((GEN/'modular').glob('estructura_*.latent'),key=lambda p:p.stat().st_mtime)
  shutil.copyfile(latents[-1],INP/'modular_structure.latent');shutil.copyfile(latents[-1],OUT/'checkpoints/estructura.latent')
 for f in (GEN/'cuy-checkpoints').glob('*.safetensors'):shutil.copyfile(f,OUT/'checkpoints'/f.name)
 time.sleep(3)
files=sorted(GEN.glob('cuy_stablegen_modular_13112026*.glb'),key=lambda p:p.stat().st_mtime)
if not files:raise RuntimeError('No GLB exported')
shutil.copyfile(files[-1],OUT/'cuy-stablegen-modular-original.glb')
print('ALL_STAGES_COMPLETE',OUT/'cuy-stablegen-modular-original.glb',flush=True)
