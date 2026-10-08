"""Render only; the developer owns compiler and strict-SL execution."""
from pathlib import Path
import base64
import json
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
prepared_path = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / 'tests/semantics'))
from arrayaccess_reference_consumer_reached import CASES, render

prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
sources = {r['id']: r for r in prepared['records']}
store = root / '.tools/arrayaccess-reference-consumers'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='review-reached-', dir=store))
rows = []
for name, source_id in CASES:
    row = sources[source_id]
    source = Path(row['source'])
    filename = json.dumps(base64.b64encode(bytes(source)).decode())
    rendered, checks = render(name, Path(row['fixture']).read_text(), filename, row['expected_stdout'])
    path = out / (name + '.watsup')
    path.write_text(rendered)
    rows.append({'id': name, 'source_id': source_id, 'source': str(source),
                 'program': row['fixture'], 'fixture': str(path), 'assertions': len(checks)})
(out / 'manifest.json').write_text(json.dumps({
    'revision': prepared['revision'], 'preparation': str(prepared_path),
    'renderer': str(Path(__file__).with_name('arrayaccess_reference_consumer_reached.py')),
    'records': rows, 'scope': 'New326 exact-source rendering only; no compiler or execution credit'
}, indent=2) + '\n')
print(out)
for row in rows:
    print(row['id'], row['assertions'])
