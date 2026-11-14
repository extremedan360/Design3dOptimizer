"""Prepare only: fresh graphs/config/commands. Does not launch or infer."""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,sys,ast
from split_checkpoint import digest,header

HERE=Path(__file__).resolve().parent
PIN='e9476a13728cd75d8279f6ec8bad753a66a1957ca375a1464dc63b37db6e3916'

def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def prepare(baseline,models,comfy,python,run,port,vae_decode='full'):
    if vae_decode not in ('full','tiled128'):raise ValueError('Expected full or tiled128 VAE decode')
    baseline=Path(baseline).resolve();models=Path(models).resolve();comfy=Path(comfy).resolve();python=Path(python).resolve();run=Path(run).resolve()
    if run.exists():raise FileExistsError('Fresh run directory required')
    if run.is_relative_to(comfy):raise ValueError('Do not place stage output in shared ComfyUI')
    split=models/'split-manifest.json';manifest=json.loads(split.read_text(encoding='utf-8'))
    if manifest['sourceSha256']!=PIN or not manifest['tensorBytesVerified']:raise ValueError('Expected byte-preserving original SD15 split')
    files={row['group']:row for row in manifest['files']}
    for row in manifest['files']:
        path=models/row['path']
        if not path.resolve().is_relative_to(models) or digest(path)!=row['sha256']:raise ValueError('Split model path/hash changed')
    base=json.loads(baseline.read_text(encoding='utf-8-sig'))
    expected={'1':'CheckpointLoaderSimple','2':'CLIPTextEncode','3':'CLIPTextEncode','4':'EmptyLatentImage','5':'KSampler','6':'VAEDecode','7':'SaveImage'}
    if {k:v['class_type'] for k,v in base.items()}!=expected:raise ValueError('Unexpected baseline graph; inspect rather than guessing')
    if base['4']['inputs']!={'width':512,'height':512,'batch_size':1}:raise ValueError('Only reviewed batch-one 512 baseline')
    sampler=base['5']['inputs']
    if (sampler['seed'],sampler['steps'],sampler['cfg'],sampler['sampler_name'],sampler['scheduler'],sampler['denoise'])!=(131113,20,5.5,'euler','normal',1.0):raise ValueError('Baseline sampling parameters changed')
    run.mkdir(parents=True)
    for sub in ('input','output','cache','temp','user','models','custom_nodes/design3d_staged_sd15','graphs'):(run/sub).mkdir(parents=True,exist_ok=True)
    plugin=run/'custom_nodes/design3d_staged_sd15/__init__.py';shutil.copy2(HERE/'checkpoint_nodes/__init__.py',plugin)
    ast.parse(plugin.read_text(encoding='utf-8'))
    paths={'design3d_staged_sd15':{'text_encoders':str((models/files['clip']['path']).parent),'diffusion_models':str((models/files['unet']['path']).parent),'vae':str((models/files['vae']['path']).parent),'custom_nodes':str(run/'custom_nodes')}}
    # JSON is valid YAML, avoiding a preparer dependency on PyYAML.
    dump(run/'extra-model-paths.yaml',paths)
    first={'1':{'class_type':'CLIPLoader','inputs':{'clip_name':Path(files['clip']['path']).name,'type':'stable_diffusion','device':'default'}},'2':copy.deepcopy(base['2']),'3':copy.deepcopy(base['3']),
           '8':{'class_type':'Design3DSD15SaveConditioning','inputs':{'positive':['2',0],'negative':['3',0],'cache_name':'conditioning.safetensors'}}}
    first['2']['inputs']['clip']=['1',0];first['3']['inputs']['clip']=['1',0]
    second={'1':{'class_type':'UNETLoader','inputs':{'unet_name':Path(files['unet']['path']).name,'weight_dtype':'default'}},
            '8':{'class_type':'Design3DSD15LoadConditioning','inputs':{'cache_name':'conditioning.safetensors'}},'4':copy.deepcopy(base['4']),'5':copy.deepcopy(base['5']),
            '9':{'class_type':'SaveLatent','inputs':{'samples':['5',0],'filename_prefix':'staged-sd15/sampled'}}}
    second['5']['inputs'].update(model=['1',0],positive=['8',0],negative=['8',1])
    third={'1':{'class_type':'VAELoader','inputs':{'vae_name':Path(files['vae']['path']).name}},'4':{'class_type':'LoadLatent','inputs':{'latent':'sampled.latent'}},
           '6':{'class_type':'VAEDecodeTiled','inputs':{'samples':['4',0],'vae':['1',0],'tile_size':128,'overlap':32,'temporal_size':64,'temporal_overlap':8}},'7':copy.deepcopy(base['7'])}
    if vae_decode=='full':third['6']={'class_type':'VAEDecode','inputs':{'samples':['4',0],'vae':['1',0]}}
    graphs=[first,second,third]
    for number,graph in enumerate(graphs,1):dump(run/'graphs'/f'{number}.json',graph)
    job={'schemaVersion':1,'sourceSha256':PIN,'baselineSha256':digest(baseline),'baselineGraph':base,'splitManifestSha256':digest(split),'pluginSha256':digest(plugin),
         'nativeSourceHashes':{name:digest(comfy/name) for name in ('nodes.py','comfy/sd.py','comfy/sd1_clip.py','utils/extra_config.py','comfy/cli_args.py')},
         'graphSha256':{str(n):digest(run/'graphs'/f'{n}.json') for n in (1,2,3)},'classification':'StableGen common SD15 graph adapted to three native loader phases; not the full StableGen panel',
         'conditioningFormat':'Tagged containers + CPU safetensors, adapted from Design3dOptimizer modular checkpoint example; no pickle','vaeDecode':vae_decode,'inferenceExecuted':False}
    dump(run/'run.json',job)
    common=[str(python),'-u',str(comfy/'main.py'),'--listen','127.0.0.1','--port',str(port),'--base-directory',str(run),'--extra-model-paths-config',str(run/'extra-model-paths.yaml'),
            '--input-directory',str(run/'input'),'--output-directory',str(run/'output'),'--temp-directory',str(run/'temp'),'--user-directory',str(run/'user'),'--disable-all-custom-nodes','--whitelist-custom-nodes','design3d_staged_sd15',
            '--disable-dynamic-vram','--disable-pinned-memory','--disable-async-offload','--disable-assets','--disable-partner-nodes','--disable-auto-launch','--preview-method','none','--cache-none','--reserve-vram','0.9','--use-pytorch-cross-attention']
    options=[['--gpu-only','--fp16-text-enc'],['--gpu-only','--fp16-unet'],['--cpu','--fp32-vae']]
    commands={str(n):{'command':common+options[n-1],'cwd':str(comfy),'env':{'DESIGN3D_SD15_RUN_ROOT':str(run),'OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4',
                      'PYTHONDONTWRITEBYTECODE':'1','HF_HOME':str(run/'cache/huggingface'),'TORCH_HOME':str(run/'cache/torch'),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'},'graph':str(run/'graphs'/f'{n}.json'),
                      'requires':['fresh owned server','2GiB RAM / 3600MiB whole-GPU guard','previous stage complete and its server terminated']} for n in (1,2,3)}
    dump(run/'commands.json',commands)
    return job

def bind_latent(run,source):
    run=Path(run).resolve();source=Path(source).resolve();dest=run/'input/sampled.latent'
    if dest.exists() or (run/'latent-binding.json').exists():raise FileExistsError('Latent binding already exists; preserve it')
    if not source.is_relative_to((run/'output').resolve()) or not source.is_file() or source.stat().st_size>2*1024*1024:raise ValueError('Expected native latent from this isolated output directory')
    table,_,entries=header(source)
    if table.get('latent_tensor',{}).get('shape')!=[1,4,64,64] or table['latent_tensor']['dtype']!='F32':raise ValueError('Expected batch-one SD15 512 latent')
    if 'latent_format_version_0' not in table:raise ValueError('Missing native scale marker; do not apply an accidental 1/0.18215 multiplier')
    if set(table)-{'__metadata__'}!={'latent_tensor','latent_format_version_0'}:raise ValueError('Unexpected native latent keys')
    shutil.copy2(source,dest)
    if digest(source)!=digest(dest):raise ValueError('Latent copy mismatch')
    proof={'source':str(source.relative_to(run)),'destination':'input/sampled.latent','sha256':digest(dest),'shape':[1,4,64,64],'nativeScaleMarkerPreserved':True}
    dump(run/'latent-binding.json',proof);return proof

if __name__=='__main__':
    ap=argparse.ArgumentParser();subs=ap.add_subparsers(dest='operation',required=True)
    prep=subs.add_parser('prepare')
    for key in ('baseline','models','comfy','python','run'):prep.add_argument('--'+key,type=Path,required=True)
    prep.add_argument('--port',type=int,default=8188)
    prep.add_argument('--vae-decode',choices=('full','tiled128'),default='full',help='CPU VAE decode; full is the accepted default, tiled128 is a diagnostic comparison')
    bind=subs.add_parser('bind-latent');bind.add_argument('--run',type=Path,required=True);bind.add_argument('--source',type=Path,required=True)
    a=ap.parse_args()
    if a.operation=='prepare':r=prepare(a.baseline,a.models,a.comfy,a.python,a.run,a.port,a.vae_decode);print('PREPARED ONLY',r['baselineSha256'])
    else:print(json.dumps(bind_latent(a.run,a.source)))
