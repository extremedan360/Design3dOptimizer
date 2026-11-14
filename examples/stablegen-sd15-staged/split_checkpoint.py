"""Stream an SD1 checkpoint into independent native ComfyUI model files.

Standard library only. Tensor bytes/dtypes are copied exactly; this is not
quantization, inference, a new checkpoint, or proof that a phase will fit RAM.
"""
from pathlib import Path
import argparse,collections,hashlib,json,math,os,struct

PREFIXES={'clip': 'cond_stage_model.transformer.', 'unet':'model.diffusion_model.', 'vae':'first_stage_model.'}
FILES={'clip':'text_encoders/sd15-clip-l.safetensors','unet':'diffusion_models/sd15-unet.safetensors','vae':'vae/sd15-vae.safetensors','extras':'extras/training-metadata.safetensors'}
BITS={'F16':16,'BF16':16,'F32':32,'F64':64,'I64':64,'I32':32,'I16':16,'I8':8,'U8':8,'U16':16,'U32':32,'U64':64,'BOOL':8,'F8_E4M3':8,'F8_E4M3FN':8,'F8_E5M2':8}
CHUNK=4*1024*1024

def no_duplicates(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('Duplicate JSON field: '+k)
        out[k]=v
    return out

def header(path):
    path=Path(path);size=path.stat().st_size
    with path.open('rb') as f:
        prefix=f.read(8)
        if len(prefix)!=8:raise ValueError('Missing safetensors header')
        length=struct.unpack('<Q',prefix)[0]
        if length<2 or length>16*1024*1024 or length+8>size:raise ValueError('Header length limit')
        raw=f.read(length);data=json.loads(raw,object_pairs_hook=no_duplicates)
    if not isinstance(data,dict) or len(data)>20000:raise ValueError('Tensor table limit')
    entries=[]
    for name,desc in data.items():
        if name=='__metadata__':
            if not isinstance(desc,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in desc.items()):raise ValueError('Metadata must contain strings')
            continue
        if not isinstance(name,str) or not name or len(name)>1024 or not isinstance(desc,dict):raise ValueError('Invalid tensor entry')
        if set(desc)!={'dtype','shape','data_offsets'}:raise ValueError('Unexpected tensor descriptor fields')
        dtype=desc['dtype'];shape=desc['shape'];offsets=desc['data_offsets']
        if dtype not in BITS or not isinstance(shape,list) or len(shape)>16 or any(type(n)!=int or n<0 or n>2**32 for n in shape):raise ValueError('Unsupported dtype/shape')
        if not isinstance(offsets,list) or len(offsets)!=2 or any(type(n)!=int for n in offsets):raise ValueError('Invalid offsets')
        start,end=offsets;expected=math.prod(shape)*BITS[dtype]//8
        if start<0 or end<start or end-start!=expected or end>size-length-8:raise ValueError('Tensor range/shape mismatch')
        entries.append((start,end,name,desc))
    entries.sort()
    cursor=0
    for start,end,name,_ in entries:
        if start!=cursor:raise ValueError('Overlapping or non-contiguous tensor data: '+name)
        cursor=end
    if cursor!=size-length-8:raise ValueError('Trailing/missing tensor bytes')
    return data,8+length,entries

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while block:=f.read(CHUNK):h.update(block)
    return h.hexdigest()

def range_digest(f,start,count):
    f.seek(start);h=hashlib.sha256()
    while count:
        block=f.read(min(CHUNK,count))
        if not block:raise ValueError('Unexpected EOF')
        h.update(block);count-=len(block)
    return h.hexdigest()

def split(source,destination,expected_sha256):
    source=Path(source).resolve();destination=Path(destination).resolve()
    if destination.exists():raise FileExistsError('Use a fresh destination; preserve earlier attempts')
    if destination.is_relative_to(source.parent):raise ValueError('Destination must be outside source checkpoint directory')
    if len(expected_sha256)!=64 or any(c not in '0123456789abcdef' for c in expected_sha256):raise ValueError('Expected original SHA256 required')
    data,base,entries=header(source)
    actual=digest(source)
    if actual!=expected_sha256:raise ValueError('Original checkpoint SHA256 mismatch; no output written')
    source_stat=source.stat();groups=collections.defaultdict(list)
    for start,end,name,desc in entries:
        group=next((g for g,prefix in PREFIXES.items() if name.startswith(prefix)),'extras')
        renamed=name[len(PREFIXES[group]):] if group!='extras' else name
        groups[group].append((start,end,name,renamed,desc))
    if not all(groups[g] for g in PREFIXES):raise ValueError('Missing CLIP/UNet/VAE group')
    if not any(row[3]=='text_model.encoder.layers.0.mlp.fc1.weight' for row in groups['clip']):raise ValueError('Native CLIP-L detection key absent')
    destination.mkdir(parents=True)
    report={'schemaVersion':1,'sourceFile':source.name,'sourceSha256':actual,'sourceBytes':source_stat.st_size,'method':'Stream byte-preserving SD1 prefix partition; no Torch, no dtype conversion','sourceTensorCount':len(entries),'sourceDtypes':dict(collections.Counter(x[3]['dtype'] for x in entries)),'files':[]}
    with source.open('rb') as original:
        for group,rows in groups.items():
            path=destination/FILES[group];path.parent.mkdir(parents=True,exist_ok=True)
            target_header={'__metadata__':{**data.get('__metadata__',{}),'format':'pt','source_sha256':actual,'partition':group}}
            cursor=0
            for start,end,name,renamed,desc in rows:
                if renamed in target_header:raise ValueError('Renamed tensor collision')
                target_header[renamed]={'dtype':desc['dtype'],'shape':desc['shape'],'data_offsets':[cursor,cursor+end-start]};cursor+=end-start
            encoded=json.dumps(target_header,separators=(',',':'),ensure_ascii=False).encode('utf-8')
            encoded+=b' '*((-len(encoded))%8)
            pending=path.with_suffix(path.suffix+'.pending')
            tensors=[]
            with pending.open('xb') as out:
                out.write(struct.pack('<Q',len(encoded)));out.write(encoded)
                for start,end,name,renamed,desc in rows:
                    original.seek(base+start);left=end-start;h=hashlib.sha256()
                    while left:
                        block=original.read(min(CHUNK,left))
                        if not block:raise ValueError('Unexpected source EOF')
                        out.write(block);h.update(block);left-=len(block)
                    tensors.append({'sourceKey':name,'key':renamed,'dtype':desc['dtype'],'shape':desc['shape'],'bytes':end-start,'sha256':h.hexdigest()})
                out.flush();os.fsync(out.fileno())
            os.replace(pending,path)
            _,out_base,out_entries=header(path)
            by_key={name:(start,end) for start,end,name,_ in out_entries}
            with path.open('rb') as verify:
                for tensor in tensors:
                    start,end=by_key[tensor['key']]
                    if range_digest(verify,out_base+start,end-start)!=tensor['sha256']:raise ValueError('Output tensor differs from original bytes')
            report['files'].append({'group':group,'path':FILES[group],'bytes':path.stat().st_size,'sha256':digest(path),'tensorCount':len(tensors),'dtypes':dict(collections.Counter(t['dtype'] for t in tensors)),'tensors':tensors})
    after=source.stat()
    if after.st_size!=source_stat.st_size or after.st_mtime_ns!=source_stat.st_mtime_ns:raise ValueError('Original changed while splitting; outputs not approved')
    report['originalUnmodifiedByTool']=True;report['tensorBytesVerified']=True
    (destination/'split-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--expected-sha256',required=True)
    args=ap.parse_args();r=split(args.source,args.output,args.expected_sha256.lower())
    print(json.dumps({k:r[k] for k in ('sourceSha256','sourceTensorCount','sourceDtypes','tensorBytesVerified')}))
    print(json.dumps([{k:f[k] for k in ('group','bytes','tensorCount','sha256')} for f in r['files']]))
