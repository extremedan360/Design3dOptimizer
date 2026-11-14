"""Local safe checkpoints for isolated StableGen stages; no upstream modifications."""
from pathlib import Path
import json,torch
import safetensors
import safetensors.torch
import folder_paths
NAMES=['image_positive','image_negative','shape_positive','shape_negative','shape_initial','shape_sampled']
def path_for(name):
 if name not in NAMES:raise ValueError('Unknown checkpoint')
 root=Path(folder_paths.get_output_directory())/'cuy-checkpoints';root.mkdir(parents=True,exist_ok=True)
 return root/(name+'.safetensors')
def encode(value,tensors):
 if isinstance(value,torch.Tensor):
  key='tensor_'+str(len(tensors));tensors[key]=value.detach().to('cpu',copy=True).contiguous();return ['tensor',key]
 if isinstance(value,dict):
  if not all(isinstance(k,str) for k in value):raise TypeError('Checkpoint dictionary keys must be strings')
  return ['dict',[[k,encode(v,tensors)] for k,v in value.items()]]
 if isinstance(value,list):return ['list',[encode(v,tensors) for v in value]]
 if isinstance(value,tuple):return ['tuple',[encode(v,tensors) for v in value]]
 if value is None or isinstance(value,(bool,int,float,str)):return ['value',value]
 raise TypeError('Unsupported checkpoint type: '+type(value).__name__)
def decode(tree,tensors):
 tag,value=tree
 if tag=='tensor':return tensors[value]
 if tag=='dict':return {k:decode(v,tensors) for k,v in value}
 if tag=='list':return [decode(v,tensors) for v in value]
 if tag=='tuple':return tuple(decode(v,tensors) for v in value)
 if tag=='value' and (value is None or isinstance(value,(bool,int,float,str))):return value
 raise ValueError('Invalid checkpoint schema')
def save(value,name):
 tensors={};tree=encode(value,tensors);path=path_for(name);temp=path.with_suffix('.tmp')
 safetensors.torch.save_file(tensors,str(temp),metadata={'schema':'cuy-checkpoint-v1','tree':json.dumps(tree)})
 temp.replace(path);return path
def load(name):
 path=path_for(name)
 with safetensors.safe_open(str(path),framework='pt',device='cpu') as f:
  meta=f.metadata();tensors={k:f.get_tensor(k) for k in f.keys()}
 if meta.get('schema')!='cuy-checkpoint-v1':raise ValueError('Unknown schema')
 return decode(json.loads(meta['tree']),tensors)
def node_classes(kind):
 class Save:
  @classmethod
  def INPUT_TYPES(cls):return {'required':{'value':(kind,), 'checkpoint':(NAMES,)}}
  RETURN_TYPES=(kind,);FUNCTION='run';OUTPUT_NODE=True;CATEGORY='cuy/laboratorio'
  def run(self,value,checkpoint):save(value,checkpoint);return (value,)
 class Load:
  @classmethod
  def INPUT_TYPES(cls):return {'required':{'checkpoint':(NAMES,)}}
  RETURN_TYPES=(kind,);FUNCTION='run';CATEGORY='cuy/laboratorio'
  def run(self,checkpoint):return (load(checkpoint),)
 return Save,Load
SaveLatent,LoadLatent=node_classes('LATENT');SaveCond,LoadCond=node_classes('CONDITIONING')
NODE_CLASS_MAPPINGS={'CuySaveLatent':SaveLatent,'CuyLoadLatent':LoadLatent,'CuySaveConditioning':SaveCond,'CuyLoadConditioning':LoadCond}
