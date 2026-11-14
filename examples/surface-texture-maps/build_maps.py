"""Neutral material modulation + artistic tangent normal from a local AI swatch.

Not measured PBR, photometric de-lighting or a high-to-low bake. No inference,
download, Blender, Unity or production edits. Python + NumPy + Pillow only.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import numpy as np
from PIL import Image

PROFILES={
    'fabric':{'color':[1.,1.,1.,1.],'center':.965,'amplitude':.035,'detail_sigma':.50,'broad_sigma':16.,'normal_sigma':.70,'normal_rms':3.5,'normal_max':10.,'roughness':.90},
    'wood':{'color':[1.,1.,1.,1.],'center':.95,'amplitude':.05,'detail_sigma':.65,'broad_sigma':24.,'normal_sigma':.90,'normal_rms':2.,'normal_max':6.,'roughness':.78},
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def srgb_to_linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def linear_to_srgb(c):return np.where(c<=.0031308,c*12.92,1.055*np.maximum(c,0)**(1/2.4)-.055)

def blur_float(value,sigma):
    """Separable Gaussian in float32; do not quantize to L8 before high-pass."""
    if sigma<=0:return value.astype(np.float32,copy=True)
    radius=max(1,int(math.ceil(3*sigma)));x=np.arange(-radius,radius+1,dtype=np.float32)
    kernel=np.exp(-.5*(x/sigma)**2);kernel/=kernel.sum()
    out=np.apply_along_axis(lambda row:np.convolve(row,kernel,mode='valid'),1,np.pad(value,((0,0),(radius,radius)),mode='reflect'))
    return np.apply_along_axis(lambda row:np.convolve(row,kernel,mode='valid'),0,np.pad(out,((radius,radius),(0,0)),mode='reflect')).astype(np.float32)

def gradient(value):
    # One-sided edge derivatives, central interior; no wrapping across image edges.
    gy,gx=np.gradient(value.astype(np.float32))
    return gx,gy

def normal_from_height(height,target_rms_degrees,max_degrees):
    gx,gy=gradient(height)
    magnitude=np.sqrt(gx*gx+gy*gy)
    rms=float(np.sqrt(np.mean(magnitude*magnitude)))
    gain=0.0 if rms<1e-8 else math.tan(math.radians(target_rms_degrees))/rms
    dx=gx*gain
    # Image row +Y points down; UV +V points up. Tangent normal is (-dH/dU,-dH/dV,+1).
    dv=-gy*gain
    length=np.sqrt(dx*dx+dv*dv);limit=math.tan(math.radians(max_degrees))
    clamp=np.minimum(1.,limit/np.maximum(length,1e-12));dx*=clamp;dv*=clamp
    normals=np.stack((-dx,-dv,np.ones_like(dx)),axis=-1)
    normals/=np.linalg.norm(normals,axis=-1,keepdims=True)
    if not np.isfinite(normals).all():raise ValueError('Nonfinite normal field')
    encoded=np.rint(np.clip(normals*.5+.5,0,1)*255).astype(np.uint8)
    decoded=encoded.astype(np.float32)/255*2-1;decoded/=np.linalg.norm(decoded,axis=-1,keepdims=True)
    error=np.degrees(np.arccos(np.clip(np.sum(normals*decoded,axis=-1),-1,1)))
    float_angle=np.degrees(np.arccos(np.clip(normals[:,:,2],-1,1)))
    return encoded,{'gradientRmsBeforeGain':rms,'unitlessGradientGain':gain,'targetRmsDegrees':target_rms_degrees,'maximumDegrees':max_degrees,'pixelsSlopeClamped':int(np.count_nonzero(clamp<1)),
                    'floatNormalsRmsTiltDegrees':float(np.sqrt(np.mean(float_angle*float_angle))),'rgb8AngularQuantizationRmsDegrees':float(np.sqrt(np.mean(error*error))),'allFinite':True}

def scalar_stats(value):
    return {'minimum':float(value.min()),'p01':float(np.percentile(value,1)),'mean':float(value.mean()),'std':float(value.std()),'p99':float(np.percentile(value,99)),'maximum':float(value.max())}

def normal_stats(encoded):
    value=encoded.astype(np.float32)/255*2-1;length=np.linalg.norm(value,axis=-1,keepdims=True);value/=length
    angles=np.degrees(np.arccos(np.clip(value[:,:,2],-1,1)))
    hist,bins=np.histogram(angles,bins=[0,2,4,6,8,10,12,90])
    return {'rmsTiltDegrees':float(np.sqrt(np.mean(angles*angles))),'p95TiltDegrees':float(np.percentile(angles,95)),'maximumTiltDegrees':float(angles.max()),'meanX':float(value[:,:,0].mean()),'meanY':float(value[:,:,1].mean()),
            'encodedVectorLengthBeforeRenormalization':{'minimum':float(length.min()),'mean':float(length.mean()),'maximum':float(length.max())},'tiltHistogram':{'edgesDegrees':bins.tolist(),'pixelCounts':hist.tolist()}}

def mip_metrics(albedo,normal):
    rows=[]
    color=srgb_to_linear(albedo.astype(np.float32)/255)[:,:,0]
    n=normal.astype(np.float32)/255*2-1
    for size in (albedo.shape[0],256,128,64,32):
        if size>albedo.shape[0] or any(r['size']==size for r in rows):continue
        if size==albedo.shape[0]:factor=color;sample=n
        else:
            # Diagnostic filtering in linear/data space, not a claim of Unity's importer result.
            factor=np.asarray(Image.fromarray(color,'F').resize((size,size),Image.Resampling.BOX))
            sample=np.stack([np.asarray(Image.fromarray(n[:,:,i],'F').resize((size,size),Image.Resampling.BOX)) for i in range(3)],axis=-1)
        sample/=np.maximum(np.linalg.norm(sample,axis=-1,keepdims=True),1e-8)
        angle=np.degrees(np.arccos(np.clip(sample[:,:,2],-1,1)))
        rows.append({'size':size,'linearAlbedoMean':float(factor.mean()),'linearAlbedoStd':float(factor.std()),'normalRmsTiltDegrees':float(np.sqrt(np.mean(angle*angle)))})
    return rows

def storage_estimate(size):
    # Conservative RGBA32 and optional 16-byte/block BC7/BC5, every mip including tiny levels.
    rgba=bc=0;w=h=size;levels=0
    while True:
        rgba+=w*h*4;bc+=math.ceil(w/4)*math.ceil(h/4)*16;levels+=1
        if w==h==1:break
        w=max(1,w//2);h=max(1,h//2)
    return {'mipLevels':levels,'rgba32BytesPerMap':rgba,'rgba32MiBTwoMaps':2*rgba/1048576,'optionalBC7orBC5BytesPerMap':bc,'optionalBC7plusBC5MiBTwoMaps':2*bc/1048576,'includesCPUReadableCopy':False,'measuredResidentGPU':False}

def build(source,output,material,size=512,center=None,amplitude=None,normal_rms=None,normal_max=None,compare_albedo=None,base_color=None):
    generator_sha=sha(Path(__file__))
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists():raise FileExistsError('Preserve previous candidates: fresh output folder required')
    if size not in (128,256,512):raise ValueError('Use a bounded power-of-two size, at most 512')
    image=Image.open(source)
    if image.width!=image.height or image.width<128 or image.width>4096:raise ValueError('Expected a square material swatch, 128-4096 source pixels')
    if 'A' in image.getbands() and image.getchannel('A').getextrema()!=(255,255):raise ValueError('Transparent source requires a reviewed background treatment')
    image=image.convert('RGB')
    if image.size!=(size,size):image=image.resize((size,size),Image.Resampling.LANCZOS)
    profile=dict(PROFILES[material])
    if base_color is not None:
        if len(base_color)!=3 or not all(0<=c<=1 for c in base_color):raise ValueError('Base color must be three shader-space values in [0,1]')
        profile['color']=[float(c) for c in base_color]+[1.]
    for key,value in (('center',center),('amplitude',amplitude),('normal_rms',normal_rms),('normal_max',normal_max)):
        if value is not None:profile[key]=float(value)
    if not 0<=profile['amplitude']<=.15 or not .75<=profile['center']<=1 or profile['center']+profile['amplitude']>1.000001:raise ValueError('Neutral modulation bounds')
    if not 0<=profile['normal_rms']<=profile['normal_max']<=20:raise ValueError('Normal angle bounds')
    rgb=np.asarray(image,dtype=np.float32)/255
    linear=srgb_to_linear(rgb);luma=linear[:,:,0]*.2126+linear[:,:,1]*.7152+linear[:,:,2]*.0722
    detail=blur_float(luma,profile['detail_sigma'])-blur_float(luma,profile['broad_sigma'])
    robust=float(np.percentile(np.abs(detail),97))
    normalized=np.zeros_like(detail) if robust<1e-8 else np.clip(detail/robust,-1,1)
    factor=np.clip(profile['center']+profile['amplitude']*normalized,profile['center']-profile['amplitude'],1.)
    if not np.isfinite(factor).all():raise ValueError('Nonfinite albedo field')
    code=np.rint(np.clip(linear_to_srgb(factor),0,1)*255).astype(np.uint8)
    albedo=np.repeat(code[:,:,None],3,axis=2)
    height=blur_float(luma,profile['normal_sigma'])-blur_float(luma,profile['broad_sigma'])
    normal,normal_parameters=normal_from_height(height,profile['normal_rms'],profile['normal_max'])
    output.mkdir(parents=True)
    albedo_path=output/(material+'-albedo-mod.png');normal_path=output/(material+'-normal.png')
    Image.fromarray(albedo,'RGB').save(albedo_path);Image.fromarray(normal,'RGB').save(normal_path)
    decoded=srgb_to_linear(albedo.astype(np.float32)/255)[:,:,0]
    spec={'schemaVersion':1,'material':material,'shaderBaseColor':profile['color'],'baseColorMustNotBeBakedIntoModulation':True,
          'albedo':{'file':albedo_path.name,'format':'RGB8 PNG, neutral grayscale','sRGBTexture':True,'alpha':'none; opaque material','wrap':'Clamp','mipmaps':True,'filter':'Trilinear','anisotropy':2},
          'normal':{'file':normal_path.name,'format':'RGB8 PNG tangent normal, data/linear','textureType':'NormalMap','convertToNormalmap':False,'sRGBTexture':False,'flipGreenChannel':False,'wrap':'Clamp','mipmaps':True,'filter':'Trilinear','anisotropy':2,'greenConvention':'+Y/+V (OpenGL), image rows inverted when computing V derivative','shaderProperty':'_BumpMap','shaderKeyword':'_NORMALMAP','bumpScale':1.,'mustRecalculateMeshTangents':True,'shaderVariantMustBeRetained':True},
          'roughness':{'constant':profile['roughness'],'urpSmoothness':1-profile['roughness'],'physicallyMeasured':False,'extraMapGenerated':False,'reason':'A single RGB AI swatch cannot determine roughness; retain the existing artistic constant rather than invent an extra PBR texture.'},
          'unityAcceptance':['Import encoded RGB as a normal map; do not bind a raw runtime LoadImage texture to UnpackNormal without verifying platform packing.','Recalculate tangents after final UV/normals/triangles.','Check an asymmetric height convention in the actual tangent basis, with flipGreenChannel initially false.','Retain URP Lit _NORMALMAP material variant for build; verify day/night and Apply/Start ownership.','Compare in the normal game camera; authoring metrics do not prove readable finish.'],
          'notPhysicallyMeasuredPBR':True,'notHighToLowBake':True,'uniqueAtlas':False,'seamlessValidated':False,'periodicTilingIntroduced':False}
    codes,counts=np.unique(code,return_counts=True)
    metrics={'sourceFile':source.name,'sourceSha256':sha(source),'size':[size,size],'method':'Linear-light luminance band-pass; percentile-bounded neutral albedo and smoothed gradient artistic tangent normal','profile':profile,'albedoFactorBeforeEncoding':scalar_stats(factor),'albedoFactorAfterRGB8sRGBDecode':scalar_stats(decoded),'uniqueEncodedAlbedoLevels':int(np.unique(code).size),'encodedAlbedoHistogram':{'values':codes.tolist(),'pixelCounts':counts.tolist()},'normalParameters':normal_parameters,'normalAfterRGB8Decode':normal_stats(normal),'mipDiagnostic':mip_metrics(albedo,normal),'memoryEstimate':storage_estimate(size),'files':{p.name:{'sha256':sha(p),'diskBytes':p.stat().st_size} for p in (albedo_path,normal_path)},'imageSource':'Local swatch supplied by the caller; provenance must be checked separately','measuredPBR':False,'heightUnits':'Unitless luminance proxy; no millimetre/displacement claim','nativeUnityTested':False,'artApproved':False}
    metrics['generatorSha256']=generator_sha
    if compare_albedo:
        previous=Image.open(compare_albedo).convert('RGB')
        previous=np.asarray(previous,dtype=np.float32)/255
        previous=srgb_to_linear(previous)[:,:,0]
        metrics['previousAlbedo']={'file':Path(compare_albedo).name,'sha256':sha(compare_albedo),'linearFactor':scalar_stats(previous),'newStdToPreviousStd':float(decoded.std()/max(float(previous.std()),1e-8))}
    (output/'material-spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    return metrics

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output','--outputdir',dest='output',type=Path,required=True);ap.add_argument('--material',choices=PROFILES,required=True);ap.add_argument('--size',type=int,default=512)
    ap.add_argument('--center',type=float);ap.add_argument('--amplitude',type=float);ap.add_argument('--normal-rms',type=float);ap.add_argument('--normal-max',type=float);ap.add_argument('--compare-albedo',type=Path)
    ap.add_argument('--base-color',type=float,nargs=3,help='Shader-space RGB multiplier; sets a separate material multiplier; does not modify map pixels')
    a=ap.parse_args();r=build(a.input,a.output,a.material,a.size,a.center,a.amplitude,a.normal_rms,a.normal_max,a.compare_albedo,a.base_color)
    print(json.dumps({k:r[k] for k in ('size','uniqueEncodedAlbedoLevels','albedoFactorAfterRGB8sRGBDecode','normalAfterRGB8Decode','memoryEstimate')}))
