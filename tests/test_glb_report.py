import unittest,tempfile,struct,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from glb_report import read_glb,report

class GLBTests(unittest.TestCase):
    def test_rejects_truncated_header_and_declared_length(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'bad.glb';p.write_bytes(b'glTF')
            with self.assertRaises(ValueError):read_glb(p)
            p.write_bytes(struct.pack('<4sII',b'glTF',2,100))
            with self.assertRaises(ValueError):read_glb(p)
    def test_counts_triangle_list_and_morphs(self):
        data={'asset':{'version':'2.0'},'accessors':[{'count':4},{'count':6}],
              'meshes':[{'extras':{'targetNames':['Blink']},'primitives':[{'attributes':{'POSITION':0},'indices':1}]}]}
        raw=json.dumps(data).encode();raw+=b' '*((-len(raw))%4)
        raw=struct.pack('<4sII',b'glTF',2,20+len(raw))+struct.pack('<II',len(raw),0x4E4F534A)+raw
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'small.glb';p.write_bytes(raw);r=report(p)
            self.assertEqual(r['triangles'],2);self.assertEqual(r['exported_vertices_across_primitives'],4);self.assertEqual(r['morph_names'],['Blink'])

if __name__=='__main__':unittest.main()
