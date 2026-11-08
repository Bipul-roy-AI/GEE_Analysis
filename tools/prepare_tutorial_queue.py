"""Update legacy tutorial export CRS before the first tutorial batch.

Download into tools/ of the original ZIP checkout. No authentication, computation
or export occurs. Existing outputs/venv are retained and changed files backed up.
"""
from pathlib import Path
import os
import tempfile
import uuid
from bdgee.batch import ROOT
from bdgee.state import exclusive_lock


def prepare(root):
    root=Path(root).resolve()
    if (root/'outputs/tutorials_state.json').exists():
        raise RuntimeError('A tutorial state already exists. Do not change its sources; resume or diagnose that run first.')
    paths=sorted((root/'themes').rglob('*.js'))+[root/'tools/js_header.txt']
    changes=[]
    for path in paths:
        if not path.exists():continue
        if not path.resolve().is_relative_to(root):raise RuntimeError('Source path escapes checkout')
        before=path.read_bytes()
        after=before.replace(b'EPSG:6933',b'EPSG:4326')
        if before!=after:changes.append((path,before,after))
    backup=root/'outputs'/('before_tutorial_crs_'+uuid.uuid4().hex[:8])
    for path,before,after in changes:
        saved=backup/path.relative_to(root)
        saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(before)
        fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.',suffix='.tmp')
        try:
            with os.fdopen(fd,'wb') as handle:
                handle.write(after);handle.flush();os.fsync(handle.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
    print(f'Updated {len(changes)} legacy tutorial/template files to EPSG:4326.')
    if changes:print('Original files backed up at:',backup)
    print('Completed national exports and their saved state were not changed.')
    print('Now run: .\\run_sequential.bat tutorials')
    return len(changes)


def main():
    if Path(__file__).resolve().parents[1]!=ROOT.resolve():
        raise RuntimeError('Save this tool in tools/ of your installed checkout')
    with exclusive_lock(ROOT/'outputs/.sequential.lock'):prepare(ROOT)


if __name__=='__main__':main()
