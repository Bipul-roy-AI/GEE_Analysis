"""Validate every adapted source, notebook schema and original hash offline."""
import ast
import hashlib
import json
from pathlib import Path
import esprima
import nbformat

root=Path(__file__).resolve().parents[1]
records=json.loads((root/'catalog.json').read_text())
assert len(records)==245
counts={'python':0,'javascript':0,'notebooks':0}
for record in records:
    assert record['status']=='adapted_unverified',record
    assert hashlib.sha256((root/'originals'/record['source']).read_bytes()).hexdigest()==record['sha256']
    path=root/record['adapted']
    source=path.read_text()
    if path.suffix=='.py':
        ast.parse(source)
        book=nbformat.read(path.with_suffix('.ipynb'),as_version=4)
        nbformat.validate(book)
        for cell in book.cells:
            if cell.cell_type=='code':
                ast.parse(cell.source)
                assert not cell.outputs
        counts['notebooks']+=1
    else:esprima.parseScript(source)
    counts[record['language']]+=1
print('PASS: 245 sources, original hashes, syntax and notebook schemas;',counts)
