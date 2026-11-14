"""Isolated SD1.5 CPU conditioning cache.

Adapted from Design3dOptimizer/examples/stablegen-modular/checkpoint_nodes:
typed containers + safetensors; no pickle, upstream edit or shared cache.
"""
from pathlib import Path
import hashlib,json,math,os,re,uuid
import torch
import safetensors
import safetensors.torch

SCHEMA='design3d-sd15-conditioning-v1'
MAX_FILE=16*1024*1024
MAX_VALUES=2*1024*1024

def context(name):
    if not re.fullmatch(r'[a-z0-9_-]{1,64}\.safetensors',name):raise ValueError('Use a simple conditioning cache filename')
    root=Path(os.environ['DESIGN3D_SD15_RUN_ROOT']).resolve()
    if not root.is_absolute() or not(root/'run.json').is_file():raise ValueError('Prepared isolated run required')
    job=json.loads((root/'run.json').read_text(encoding='utf-8'))
    identity={'baselineSha256':job['baselineSha256'],'sourceSha256':job['sourceSha256']}
    if not all(re.fullmatch(r'[0-9a-f]{64}',v) for v in identity.values()):raise ValueError('Invalid run identity')
    cache=root/'cache';cache.mkdir(exist_ok=True)
    path=cache/name
    if path.is_symlink() or not path.resolve().is_relative_to(cache.resolve()):raise ValueError('Cache path outside isolated root')
    return path,identity

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()

def encode(value,tensors,depth=0):
    if depth>8:raise ValueError('Container depth limit')
    if isinstance(value,torch.Tensor):
        if value.layout!=torch.strided or value.is_quantized or value.numel()>MAX_VALUES or value.ndim>4:raise ValueError('Conditioning tensor limit')
        copy=value.detach().to('cpu',copy=True).contiguous()
        if copy.dtype not in (torch.float16,torch.float32,torch.float64,torch.bfloat16,torch.int32,torch.int64,torch.bool):raise ValueError('Conditioning dtype')
        if copy.is_floating_point() and not torch.isfinite(copy).all().item():raise ValueError('Nonfinite conditioning')
        key='tensor_'+str(len(tensors));tensors[key]=copy
        if sum(t.numel() for t in tensors.values())>MAX_VALUES:raise ValueError('Combined tensor limit')
        return ['tensor',key]
    if isinstance(value,dict):
        if len(value)>64 or not all(isinstance(k,str) and len(k)<=128 for k in value):raise ValueError('Dictionary limit')
        return ['dict',[[k,encode(v,tensors,depth+1)] for k,v in value.items()]]
    if isinstance(value,(list,tuple)):
        if len(value)>64:raise ValueError('Sequence limit')
        return ['tuple' if isinstance(value,tuple) else 'list',[encode(v,tensors,depth+1) for v in value]]
    if value is None or type(value) in (bool,int,float,str):
        if isinstance(value,str) and len(value)>1024 or isinstance(value,float) and not math.isfinite(value):raise ValueError('Scalar limit')
        return ['value',value]
    raise TypeError('Unsupported conditioning container')

def decode(tree,tensors,depth=0):
    if depth>8 or not isinstance(tree,list) or len(tree)!=2:raise ValueError('Invalid tree')
    tag,value=tree
    if tag=='tensor':return tensors[value]
    if tag=='dict':
        if not isinstance(value,list) or len(value)>64:raise ValueError('Dictionary limit')
        if len({k for k,_ in value})!=len(value) or not all(isinstance(k,str) for k,_ in value):raise ValueError('Dictionary keys')
        return {k:decode(v,tensors,depth+1) for k,v in value}
    if tag in ('list','tuple'):
        if not isinstance(value,list) or len(value)>64:raise ValueError('Sequence limit')
        values=[decode(v,tensors,depth+1) for v in value]
        return tuple(values) if tag=='tuple' else values
    if tag=='value' and (value is None or type(value) in (bool,int,float,str)):return value
    raise ValueError('Invalid tree tag')

def conditioning(value):
    if not isinstance(value,list) or not 1<=len(value)<=8:raise ValueError('Invalid conditioning list')
    for pair in value:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2 or not isinstance(pair[0],torch.Tensor) or not isinstance(pair[1],dict):raise ValueError('Invalid conditioning pair')
        tensor=pair[0]
        if tensor.ndim!=3 or tensor.shape[0]!=1 or not 1<=tensor.shape[1]<=512 or tensor.shape[2]!=768:raise ValueError('Expected SD1 CLIP-L batch-one conditioning')
    return value

def load(name):
    path,identity=context(name);receipt=path.with_suffix('.json')
    if not path.is_file() or path.stat().st_size>MAX_FILE or not receipt.is_file():raise ValueError('Missing or oversized cache/receipt')
    saved=json.loads(receipt.read_text(encoding='utf-8'))
    if saved['identity']!=identity or saved['sha256']!=digest(path):raise ValueError('Conditioning identity/hash mismatch')
    with safetensors.safe_open(str(path),framework='pt',device='cpu') as f:
        meta=f.metadata()
        if meta.get('schema')!=SCHEMA or json.loads(meta['identity'])!=identity or len(meta['tree'])>65536:raise ValueError('Conditioning schema/identity')
        keys=list(f.keys())
        if not 1<=len(keys)<=64:raise ValueError('Tensor count')
        tensors={k:f.get_tensor(k) for k in keys}
    data=decode(json.loads(meta['tree']),tensors)
    if not isinstance(data,dict) or set(data)!={'positive','negative'}:raise ValueError('Cache payload')
    # Revalidate containers/tensor limits without duplicating their CPU data.
    if sum(t.numel() for t in tensors.values())>MAX_VALUES:raise ValueError('Combined tensor limit')
    for t in tensors.values():
        if t.device.type!='cpu' or t.layout!=torch.strided or t.is_floating_point() and not torch.isfinite(t).all().item():raise ValueError('Invalid CPU tensor')
    return conditioning(data['positive']),conditioning(data['negative'])

class SaveConditioning:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'positive':('CONDITIONING',),'negative':('CONDITIONING',),'cache_name':('STRING',{'default':'conditioning.safetensors'})}}
    RETURN_TYPES=();FUNCTION='run';OUTPUT_NODE=True;CATEGORY='design3d/staged-sd15'
    def run(self,positive,negative,cache_name):
        conditioning(positive);conditioning(negative)
        path,identity=context(cache_name);receipt=path.with_suffix('.json')
        if path.exists() or receipt.exists():raise FileExistsError('Preserve completed cache; use a fresh run')
        tensors={};tree=encode({'positive':positive,'negative':negative},tensors)
        pending=path.with_name(path.name+'.'+uuid.uuid4().hex+'.pending')
        safetensors.torch.save_file(tensors,str(pending),metadata={'schema':SCHEMA,'tree':json.dumps(tree,separators=(',',':')),'identity':json.dumps(identity,sort_keys=True)})
        if pending.stat().st_size>MAX_FILE:raise ValueError('Cache too large')
        os.replace(pending,path)
        proof={'schema':SCHEMA,'identity':identity,'sha256':digest(path),'tensorCount':len(tensors),'cpuOnly':True,'pickle':False}
        with receipt.open('x',encoding='utf-8') as f:json.dump(proof,f,indent=2)
        load(cache_name)
        return {'ui':{'staged_sd15':[{'file':cache_name,'sha256':proof['sha256'],'cpuOnly':True}]},'result':()}

class LoadConditioning:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'cache_name':('STRING',{'default':'conditioning.safetensors'})}}
    RETURN_TYPES=('CONDITIONING','CONDITIONING');RETURN_NAMES=('positive','negative');FUNCTION='run';CATEGORY='design3d/staged-sd15'
    def run(self,cache_name):return load(cache_name)
    @classmethod
    def IS_CHANGED(cls,cache_name):return digest(context(cache_name)[0])

NODE_CLASS_MAPPINGS={'Design3DSD15SaveConditioning':SaveConditioning,'Design3DSD15LoadConditioning':LoadConditioning}
