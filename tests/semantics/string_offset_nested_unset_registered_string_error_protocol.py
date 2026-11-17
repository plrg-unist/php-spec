#!/usr/bin/env python3
"""Invalid STRING keys preserve their Error before the nested-string Error."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_registered_quiet_key_protocol as source
import string_offset_nested_unset_registered_string_error_cases as cases

prior, recorded = source.prior, source.recorded
INDEX = 0


def conditions(program, path):
    source.INDEX, source.cases = INDEX, cases
    checks, derived = source.conditions(program, path)
    line = (5, 6)[INDEX]
    bad = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))'
    floatlike = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))'
    replacements = {
        'ptbytes_message = $ptascii("Cannot use string offset as an array")':
            'ptbytes_message = $ptascii("Cannot unset string offsets")',
        f'$unset_string_key(S_key, pvalue_key, {line}) = S_key':
            f'$unset_string_key(S_key, pvalue_key, {line}) = S_key[.COMPLETION = THROWN "Error" ($ptascii("Cannot unset string offsets")) {line}]',
    }
    if INDEX == 0:
        replacements.update({'poperand_inner = KNOWN (PINT 99)': 'poperand_inner = KNOWN (' + bad + ')',
                             'pvalue_key = PINT 99': 'pvalue_key = ' + bad})
    else:
        replacements.update({'poperand_final = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")))': 'poperand_final = KNOWN (' + floatlike + ')',
                             'pvalue_key = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))': 'pvalue_key = ' + floatlike})
    for old, new in replacements.items():
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    old = next(check for check in checks if check.startswith('$unset_intermediate(S_legacy,'))
    assert checks.count(old) == 1 and old.endswith('ptbytes_message 9]')
    checks[checks.index(old)] = old.replace('ptbytes_message', '($ptascii("Cannot use string offset as an array"))')
    guards = []
    for value in ('PSTRING eps', 'PSTRING ($ptascii("bad"))', 'PSTRING ($ptascii("1.0"))'):
        guards += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.RESULT = KNOWN ({value})][.COMPLETION = THROWN "Error" ptbytes_message 9]']
    guards += prior.lines(r'''
S_error_key = S_base[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")))]
$unset_string_key(S_error_key, PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")), 9) = S_error_key[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_error_key, pvalue_base, ROOT n_base, KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))), 99) = S_error_key[.COMPLETION = THROWN "Error" ptbytes_message 99]
$unset_intermediate(S_muted, pvalue_base, ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_muted[.RESULT = KNOWN (PSTRING ($ptascii("bad")))][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))), 9) = S_base[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")))][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 9]
''')
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = (own, Path(source.__file__).resolve())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded = cases, conditions, recorded
    passed = prior.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['inputs'].update(before)
    report['scope'] = 'Genuine checked source/php_run0 reaches a registered-handler nested string UNSET with valid non-NUL STRING key whose existing key helper throws the exact own Error without callbacks. Exact raw/public/catch/budget states preserve Error priority, base/handler/storage/registry/CODE/POOLS, missing final-CV laziness and the final1.5 assignment before delayed inner read; native TypeError observer stays false. Three old quiet-string refusals and the old terminal INDEX1 helper promote through isolated controls without old campaign renewal. Quiet INT/STRING behavior and NULL/BOOL/FLOAT/range/header/NUL/undefined/BUDGET fences remain; source0/native0 and same saved native originals reused once.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
