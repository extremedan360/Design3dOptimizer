"""Lightweight public-package checks: synthetic bytes only, no model or GPU."""
from pathlib import Path
import ast,copy,hashlib,json,struct,subprocess,sys,tempfile

EXAMPLE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(EXAMPLE))
import split_checkpoint as splitter
import prepare_stages as preparer

checks=[]
def check(label,condition):
    if not condition:raise AssertionError(label)
    checks.append(label)

def rejected(label,fn,errors=(ValueError,FileExistsError)):
    try:fn()
    except errors:checks.append(label);return
    raise AssertionError(label)

def tensor_file(path,rows):
    table={};payload=b''
    for name,dtype,shape,data in rows:
        table[name]={'dtype':dtype,'shape':shape,'data_offsets':[len(payload),len(payload)+len(data)]}
        payload+=data
    encoded=json.dumps(table,separators=(',',':')).encode()
    encoded+=b' '*((-len(encoded))%8)
    path.write_bytes(struct.pack('<Q',len(encoded))+encoded+payload)

for source in EXAMPLE.rglob('*.py'):
    ast.parse(source.read_text(encoding='utf-8'),filename=source.name)
    checks.append('AST: '+source.relative_to(EXAMPLE).as_posix())
for script,args in [('split_checkpoint.py',[]),('prepare_stages.py',[]),('prepare_stages.py',['prepare']),('prepare_stages.py',['bind-latent']),('run_phase.py',[]),('run_guard.py',[])]:
    result=subprocess.run([sys.executable,'-B',str(EXAMPLE/script),*args,'--help'],capture_output=True,text=True,timeout=20)
    check('CLI help: '+script+' '+','.join(args),result.returncode==0 and 'usage:' in result.stdout)

with tempfile.TemporaryDirectory(prefix='design3d-synthetic-') as temporary:
    root=Path(temporary).resolve();source_dir=root/'source';source_dir.mkdir()
    source=source_dir/'synthetic.safetensors'
    rows=[('cond_stage_model.transformer.text_model.encoder.layers.0.mlp.fc1.weight','F16',[2,2],bytes(range(8))),
          ('model.diffusion_model.input_blocks.0.0.weight','F16',[2],b'abcd'),
          ('first_stage_model.decoder.conv_in.weight','F16',[2],b'efgh'),
          ('model_ema.decay','F16',[],b'ij')]
    tensor_file(source,rows);original=source.read_bytes()
    models=root/'split'
    report=splitter.split(source,models,splitter.digest(source))
    check('Split preserves original bytes',source.read_bytes()==original)
    check('All four tensor groups retained',len(report['files'])==4 and report['sourceTensorCount']==4)
    check('Split tensor bytes and dtype verified',report['tensorBytesVerified'] and all(t['dtype']=='F16' for f in report['files'] for t in f['tensors']))
    rejected('Wrong source hash rejected before output',lambda:splitter.split(source,root/'wrong-hash','0'*64))
    check('Wrong hash creates no output',not(root/'wrong-hash').exists())
    rejected('Existing split not overwritten',lambda:splitter.split(source,models,splitter.digest(source)))
    comfy=root/'comfy';comfy.mkdir()
    for name in ('nodes.py','comfy/sd.py','comfy/sd1_clip.py','utils/extra_config.py','comfy/cli_args.py'):
        target=comfy/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# synthetic fixture\n')
    baseline=json.loads((EXAMPLE/'baseline.json').read_text(encoding='utf-8-sig'))
    baseline_path=root/'baseline.json';baseline_path.write_text(json.dumps(baseline))
    pin=preparer.PIN;preparer.PIN=report['sourceSha256']
    try:
        run=root/'full';job=preparer.prepare(baseline_path,models,comfy,sys.executable,run,8188)
        graphs=[json.loads((run/'graphs'/f'{i}.json').read_text()) for i in (1,2,3)]
        check('Full decode is default',job['vaeDecode']=='full' and graphs[2]['6']=={'class_type':'VAEDecode','inputs':{'samples':['4',0],'vae':['1',0]}})
        names=[{n['class_type'] for n in graph.values()} for graph in graphs]
        check('Phase1 excludes diffusion and VAE',not names[0]&{'UNETLoader','VAELoader','KSampler'})
        check('Phase2 excludes text and VAE',not names[1]&{'CLIPLoader','CLIPTextEncode','VAELoader'})
        check('Phase3 excludes text and diffusion',not names[2]&{'CLIPLoader','CLIPTextEncode','UNETLoader','KSampler'})
        check('Prompts preserved',all(graphs[0][k]['inputs']['text']==baseline[k]['inputs']['text'] for k in ('2','3')))
        check('Sampling preserved',all(graphs[1]['5']['inputs'][key]==baseline['5']['inputs'][key] for key in ('seed','steps','cfg','sampler_name','scheduler','denoise')))
        check('Generic output prefix preserved',graphs[2]['7']['inputs']['filename_prefix']=='generated-linen-sd15')
        tiled=root/'tiled';preparer.prepare(baseline_path,models,comfy,sys.executable,tiled,8188,'tiled128')
        tile_graph=json.loads((tiled/'graphs/3.json').read_text())
        check('Tiled128 remains explicit',tile_graph['6']['class_type']=='VAEDecodeTiled' and tile_graph['6']['inputs']['tile_size']==128 and tile_graph['6']['inputs']['overlap']==32)
        changed=copy.deepcopy(tile_graph);changed['6']=graphs[2]['6']
        check('Full versus tiled differs only in decode node',changed==graphs[2])
        commands=json.loads((run/'commands.json').read_text())
        check('CPU FP32 VAE command',all(flag in commands['3']['command'] for flag in ('--cpu','--fp32-vae')))
        check('Text and diffusion remain GPU FP16','--fp16-text-enc' in commands['1']['command'] and '--fp16-unet' in commands['2']['command'])
        check('Isolated cache and offline environment',commands['1']['env']['HF_HUB_OFFLINE']=='1' and commands['1']['env']['PYTHONDONTWRITEBYTECODE']=='1')
        latent=run/'output/synthetic.latent'
        tensor_file(latent,[('latent_tensor','F32',[1,4,64,64],b'\0'*65536),('latent_format_version_0','F32',[0],b'')])
        binding=preparer.bind_latent(run,latent)
        check('Native latent bytes and scale marker preserved',binding['nativeScaleMarkerPreserved'] and splitter.digest(latent)==splitter.digest(run/'input/sampled.latent'))
        rejected('Existing latent binding not overwritten',lambda:preparer.bind_latent(run,latent))
        rejected('Invalid decode option rejected',lambda:preparer.prepare(baseline_path,models,comfy,sys.executable,root/'bad-decode',8188,'other'))
        altered=copy.deepcopy(baseline);altered['5']['inputs']['seed']+=1
        bad=root/'changed.json';bad.write_text(json.dumps(altered))
        rejected('Changed seed rejected',lambda:preparer.prepare(bad,models,comfy,sys.executable,root/'bad-seed',8188))
    finally:preparer.PIN=pin

proof={'passed':True,'scope':'AST, CLI help and synthetic split/prepare/bind only; no real weights, Torch import, native server, GPU call or inference',
       'checks':len(checks),'details':checks,'expectedModelPinInjectedOnlyInTestMemory':True}
print(json.dumps(proof,indent=2))
