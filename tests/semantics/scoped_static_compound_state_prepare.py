"""Render fresh keyword selection controls without numeric execution."""
from pathlib import Path
import base64
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from scoped_static_compound_protocol import CASES, render

prepared_path = Path(sys.argv[1]).resolve()
prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
source_rows = {row['id']: row for row in prepared['records']}
store = ROOT / '.tools/scoped-static-compounds'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='review-reached-', dir=store))
rows = []
for name, source_ids in CASES:
    sources = {}
    for source_id in source_ids:
        row = source_rows[source_id]
        sources[source_id] = {
            'fixture': Path(row['fixture']).read_text(),
            'filename': json.dumps(base64.b64encode(row['source'].encode()).decode()),
            'expected_stdout': row['expected_stdout'],
        }
    rendered, checks = render(name, sources)
    path = out / (name + '.watsup')
    path.write_text(rendered)
    first = source_rows[source_ids[0]]
    rows.append({'id': name, 'source_id': source_ids[0], 'source': first['source'],
                 'program': first['fixture'], 'fixture': str(path),
                 'assertions': len(checks), 'source_ids': source_ids})
(out / 'manifest.json').write_text(json.dumps({
    'revision': prepared['revision'], 'preparation': str(prepared_path),
    'renderer': str(Path(__file__).with_name('scoped_static_compound_protocol.py')),
    'records': rows,
    'scope': 'Fresh keyword static selection pure rendering; no compiler/execution credit'
}, indent=2) + '\n')
print(out)
for row in rows:
    print(row['id'], row['assertions'])
