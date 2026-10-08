"""Render334 only; developer owns the sole compiler/strict-SL actor."""
from pathlib import Path
import base64
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from arrayaccess_stringable_compound_protocol import CASES, COMPILER_CASES, render

prepared_path = Path(sys.argv[1]).resolve()
prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
sources = {row['id']: row for row in prepared['records']}
store = ROOT / '.tools/arrayaccess-stringable-compound'
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
controls = []
for name, text, message in COMPILER_CASES:
    source = out / (name + '.php')
    source.write_text(text)
    controls.append({'id': name, 'source': str(source), 'message': message})
(out / 'manifest.json').write_text(json.dumps({
    'revision': prepared['revision'], 'preparation': str(prepared_path),
    'renderer': str(Path(__file__).with_name('arrayaccess_stringable_compound_protocol.py')),
    'records': rows, 'compiler_controls': controls,
    'scope': 'New334 exact-source pure rendering; no compiler/execution credit'
}, indent=2) + '\n')
print(out)
for row in rows:
    print(row['id'], row['assertions'])
