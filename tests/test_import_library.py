import unittest,tempfile,hashlib,json,sys
from pathlib import Path
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from import_library import ingest

class LibraryTests(unittest.TestCase):
    def test_deduplicates_but_keeps_both_provenance_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);a=root/'a.zip';b=root/'b.zip';raw=b'# Notes\nhttps://example.com/manual\n'
            with ZipFile(a,'w') as z:z.writestr('pack/guide.md',raw)
            with ZipFile(b,'w') as z:z.writestr('other/renamed.md',raw)
            result=ingest([a,b],root/'library')
            self.assertEqual(result['total_entries'],2);self.assertEqual(result['unique_documents'],1)
            entries=[x['entries'][0] for x in result['archives']]
            self.assertEqual(entries[0]['canonical'],entries[1]['canonical'])
            self.assertEqual(hashlib.sha256((root/'library'/entries[0]['canonical']).read_bytes()).hexdigest(),entries[0]['sha256'])
    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);a=root/'bad.zip'
            with ZipFile(a,'w') as z:z.writestr('../escape.md','not an instruction')
            with self.assertRaises(ValueError):ingest([a],root/'library')
            self.assertFalse((root/'escape.md').exists())

if __name__=='__main__':unittest.main()
