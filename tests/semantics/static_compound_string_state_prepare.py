"""Render fresh static compound controls; execution requires the numeric actor."""
from pathlib import Path
import base64
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from static_compound_string_protocol import CASES, render

prepared_path = Path(sys.argv[1]).resolve()
prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
sources = {row['id']: row for row in prepared['records']}
store = ROOT / '.tools/static-stringable-compounds'
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
                 'program': row['fixture'], 'fixture': str(path), 'assertions': len(checks),
                 'source_ids': [source_id]})
(out / 'manifest.json').write_text(json.dumps({
    'revision': prepared['revision'], 'preparation': str(prepared_path),
    'renderer': str(Path(__file__).with_name('static_compound_string_protocol.py')),
    'records': rows,
    'scope': 'New356 exact-source pure rendering; no compiler/execution credit'
}, indent=2) + '\n')
print(out)
for row in rows:
    print(row['id'], row['assertions'])
