#!/usr/bin/env python3
"""A compiler failure cannot excuse a different or unreviewed frontend failure."""
import base64
import copy
import json
from corpus import ROOT, phpt
from validate import classify_phase_difference

entry = json.loads((ROOT / 'tests/phase-discrepancies.json').read_text())[0]
record = phpt(ROOT / entry['id'])
result = {
    'status': 'unreviewed_phase_difference',
    'frontend_detail': {'message': base64.b64encode(entry['frontend_message'].encode()).decode()},
    'lint': {'accepted': False, 'diagnostic_b64': base64.b64encode(entry['lint_contains'].encode()).decode()},
}
assert classify_phase_difference(record, result)['status'] == 'compile_phase_difference'
for key, value in [('id', 'unreviewed.php'), ('sha256', '0' * 64), ('ini', {'short_open_tag': '1'})]:
    assert classify_phase_difference({**record, key: value}, result)['status'] == 'unreviewed_phase_difference'
for branch, key in [('frontend_detail', 'message'), ('lint', 'diagnostic_b64')]:
    changed = copy.deepcopy(result)
    changed[branch][key] = base64.b64encode(b'An unrelated restriction').decode()
    assert classify_phase_difference(record, changed)['status'] == 'unreviewed_phase_difference'
assert classify_phase_difference(record, {**result, 'status': 'acceptance_mismatch'})['status'] == 'acceptance_mismatch'
changed = copy.deepcopy(result)
changed['lint']['accepted'] = True
assert classify_phase_difference(record, changed)['status'] == 'unreviewed_phase_difference'
print('phase ledger: known case accepted; seven unrelated observations remain failures')
