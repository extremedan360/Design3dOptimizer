"""CPU-only synthetic contract checks; no inference or source assets."""
import tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
import build_maps as m

class MapContracts(unittest.TestCase):
 def test_gamma_roundtrip(self):
  x=np.array([0,.001,.0031308,.05,.18,.5,1],dtype=np.float64)
  np.testing.assert_allclose(m.srgb_to_linear(m.linear_to_srgb(x)),x,atol=2e-8)
 def test_asymmetric_positive_v_height(self):
  # V increases upward, while array row increases downward.
  y,x=np.mgrid[:32,:32];height=(-2*y+.3*x).astype(np.float32)
  encoded,_=m.normal_from_height(height,3.5,10)
  n=encoded.astype(np.float32)/255*2-1
  self.assertTrue(np.all(n[:,:,0]<0))
  self.assertTrue(np.all(n[:,:,1]<0))
  self.assertTrue(np.isfinite(n).all())
  self.assertLess(float(np.abs(np.linalg.norm(n,axis=-1)-1).max()),.007)
 def test_uniform_source_stays_uniform(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);Image.new('RGB',(128,128),(117,117,117)).save(p/'uniform.png')
   result=m.build(p/'uniform.png',p/'out','fabric',size=128)
   a=np.asarray(Image.open(p/'out/fabric-albedo-mod.png'));n=np.asarray(Image.open(p/'out/fabric-normal.png'))
   self.assertEqual(np.unique(a.reshape(-1,3),axis=0).shape[0],1)
   self.assertTrue(np.all(n==np.array([128,128,255],dtype=np.uint8)))
   self.assertFalse(result['measuredPBR'])
 def test_two_base_colors_do_not_change_maps(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);y,x=np.mgrid[:128,:128];v=np.uint8(np.clip(128+30*np.sin(x*.31)+18*np.cos(y*.17),0,255))
   Image.fromarray(np.repeat(v[:,:,None],3,axis=2)).save(p/'synthetic.png')
   m.build(p/'synthetic.png',p/'a','wood',size=128,base_color=[.8,.3,.2])
   m.build(p/'synthetic.png',p/'b','wood',size=128,base_color=[.2,.7,.9])
   for name in ['wood-albedo-mod.png','wood-normal.png']:
    self.assertEqual((p/'a'/name).read_bytes(),(p/'b'/name).read_bytes())
   with self.assertRaises(FileExistsError):m.build(p/'synthetic.png',p/'a','wood',size=128)

if __name__=='__main__':unittest.main()
