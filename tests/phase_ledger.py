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
# Retired array-hole exemptions are literal regressions, not active allowlist entries.
RETIRED_ARRAY_HOLES = [('vendor/php-src/Zend/tests/bug75426.phpt',
  '144cc5b3d4a7d343ec580e455ca766b3b2854c3685ab6dfbe6dba65fde90711c',
  'Cannot use empty array elements in arrays on line 6',
  'Cannot use empty array elements in arrays'),
 ('vendor/php-src/Zend/tests/constexpr/gh9138.phpt',
  'ab9e15a9e8fe26ea91284b20456428b99946fa188b516c96535761fee617de88',
  'Cannot use empty array elements in arrays on line 3',
  'Cannot use empty array elements in arrays'),
 ('vendor/php-src/Zend/tests/constexpr/gh9138_2.phpt',
  '1217cdf9e390079614e80d1ac31fac060f24782e98f7dab865ad1518e9223862',
  'Cannot use empty array elements in arrays on line 3',
  'Cannot use empty array elements in arrays'),
 ('vendor/php-src/Zend/tests/list/list_012.phpt',
  '18f7e93bd6eac07c9d88e29bfedf8c4d0afd3a5f4e7e5aed5d7a792ddb3a2295',
  'Cannot use empty array elements in arrays on line 3',
  'Cannot use empty array elements in arrays'),
 ('vendor/php-src/Zend/tests/list/list_013.phpt',
  '31ae3197341d97eed174082c4abc18b73e709c65f6fc08bf80c28366489dee98',
  'Cannot use empty array elements in arrays on line 3',
  'Cannot use empty array elements in arrays')]
# Retired foreach key exemptions must also remain observable failures.
RETIRED_FOREACH_KEYS = [('vendor/php-src/Zend/tests/errmsg/errmsg_042.phpt',
  'c573f18a068c48e0fc809bbc7dd6bfda42bca28577889f1d6984a87f05795b62',
  "Syntax error, unexpected T_DOUBLE_ARROW, expecting '[' or T_OBJECT_OPERATOR or T_NULLSAFE_OBJECT_OPERATOR "
  'on line 4',
  'Key element cannot be a reference'),
 ('vendor/php-src/Zend/tests/foreach/foreach_list_003.phpt',
  '9fd5d7b0468789dd8e8bd8782a4c64d94c43136e18ff7ddc87ee36330e6ede82',
  "Syntax error, unexpected T_DOUBLE_ARROW, expecting ')' on line 5",
  'Cannot use list as key element'),
 ('vendor/php-src/tests/lang/foreachLoop.006.phpt',
  'effe54fd3e9d9b1542a869eb87a4520578291ad4f10ea68e952f18f50e29423c',
  "Syntax error, unexpected T_DOUBLE_ARROW, expecting '[' or T_OBJECT_OPERATOR or T_NULLSAFE_OBJECT_OPERATOR "
  'on line 3',
  'Key element cannot be a reference')]
for source_id, source_hash, frontend_message, lint_message in RETIRED_ARRAY_HOLES + RETIRED_FOREACH_KEYS:
    retired_record = {'id': source_id, 'sha256': source_hash, 'ini': {}}
    retired_result = {
        'status': 'unreviewed_phase_difference',
        'frontend_detail': {'message': base64.b64encode(frontend_message.encode()).decode()},
        'lint': {'accepted': False, 'diagnostic_b64': base64.b64encode(lint_message.encode()).decode()},
    }
    assert classify_phase_difference(retired_record, retired_result)['status'] == 'unreviewed_phase_difference'
print('phase ledger: known case accepted; seven unrelated and eight retired observations remain failures')
