"""Check documentation links, Python syntax, text encoding and imported hashes."""
from pathlib import Path
import re,json,hashlib,ast

root=Path(__file__).resolve().parents[1];errors=[];count=0
ignored={'.git','.venv','__pycache__','artifacts','outputs','work'}
for p in root.rglob('*'):
    if not p.is_file() or any(part in ignored for part in p.relative_to(root).parts):continue
    count+=1
    if p.stat().st_size>5*1024*1024:errors.append('File over repository budget: '+str(p.relative_to(root)))
    if p.suffix not in {'.md','.py','.json','.yaml'}:continue
    try:text=p.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:errors.append('Invalid UTF-8: '+str(p.relative_to(root)));continue
    if re.search(r'C:[/\\]Users[/\\]',text,re.I):errors.append('Personal absolute path: '+str(p.relative_to(root)))
    if p.suffix=='.py':ast.parse(text)
    if p.suffix=='.md':
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in link or link.startswith('#'):continue
            if not (p.parent/link.split('#')[0].replace('%20',' ')).resolve().exists():errors.append('Broken link: '+str(p.relative_to(root))+' -> '+link)
manifest=json.loads((root/'docs/library/manifest.json').read_text(encoding='utf-8'))
for source in manifest['archives']:
    for item in source['entries']:
        p=root/'docs/library'/item['canonical']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('Imported document hash mismatch: '+item['path'])
print('Checked',count,'files and',manifest['total_entries'],'source entries')
print('\n'.join(errors) if errors else 'Repository checks passed')
raise SystemExit(bool(errors))
