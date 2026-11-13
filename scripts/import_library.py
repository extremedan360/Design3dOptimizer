"""Import a user-authorized textual bibliography without executing embedded files.

Preserves original bytes, deduplicates by SHA-256 and records every source entry.
The caller must review publication rights. Remote linked pages are not downloaded.
"""
import argparse,hashlib,json,re,unicodedata
from pathlib import Path,PurePosixPath
from zipfile import ZipFile

def ingest(archives,destination):
    root=Path(destination).resolve();root.mkdir(parents=True,exist_ok=True)
    seen={};catalog={};sources=[]
    for archive in archives:
        archive=Path(archive);record={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'entries':[]}
        slug=unicodedata.normalize('NFKD',archive.stem).encode('ascii','ignore').decode().lower()
        slug=re.sub(r'[^a-z0-9]+','-',slug).strip('-')
        with ZipFile(archive) as z:
            if sum(i.file_size for i in z.infolist())>100_000_000:raise ValueError('Archive exceeds text-library budget')
            for info in z.infolist():
                name=PurePosixPath(info.filename)
                if name.is_absolute() or '..' in name.parts or ':' in str(name) or '\\' in str(name):raise ValueError('Unsafe archive path')
                if info.is_dir():continue
                if name.suffix.lower() not in {'.md','.txt','.url','.json'}:raise ValueError('Non-text file requires separate review: '+str(name))
                data=z.read(info);text=data.decode('utf-8-sig');digest=hashlib.sha256(data).hexdigest();duplicate=digest in seen
                if not duplicate:
                    relative=Path('originals')/slug/Path(*name.parts[1:]);target=root/relative
                    if not target.resolve().is_relative_to(root):raise ValueError('Destination escapes library root')
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if target.exists() and target.read_bytes()!=data:raise ValueError('Refusing to replace a different imported document')
                    target.write_bytes(data);seen[digest]=relative.as_posix()
                record['entries'].append({'path':str(name),'bytes':len(data),'sha256':digest,'canonical':seen[digest],'duplicate':duplicate})
                for url in re.findall(r'https://[^\s<>;]+',text):
                    url=url.rstrip(').,');catalog.setdefault(url,[]).append({'archive':archive.name,'document':seen[digest]})
        sources.append(record)
    manifest={'archives':sources,'total_entries':sum(len(s['entries']) for s in sources),'unique_documents':len(seen),'duplicate_entries':sum(e['duplicate'] for s in sources for e in s['entries'])}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    (root/'links.json').write_text(json.dumps([{'url':u,'source_documents':list({r['document']:r for r in refs}.values()),'status':'catalogued; see review for verification scope'} for u,refs in sorted(catalog.items())],indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in manifest.items() if k!='archives'}));print('Unique external links:',len(catalog))
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archives',nargs='+');p.add_argument('--output',required=True);a=p.parse_args();ingest(a.archives,a.output)
