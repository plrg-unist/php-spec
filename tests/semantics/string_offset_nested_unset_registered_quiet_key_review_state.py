#!/usr/bin/env python3
"""Independent quiet-key bounds at genuine registered-handler nested unsets."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_registered_quiet_key_protocol as source

prior, cases = source.prior, source.cases


def conditions(program, path):
    checks, derived = source.conditions(program, path)
    guards = []
    admitted = ('PINT $(-9223372036854775808)', 'PINT 9223372036854775807',
                'PINT (-999)', 'PINT 0', 'PINT 99',
                'PSTRING ($ptascii("0"))', 'PSTRING ($ptascii("-999"))',
                'PSTRING ($ptascii("  +99tail"))',
                'PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))')
    refused = ('PINT $(-9223372036854775809)', 'PINT 9223372036854775808',
               'PSTRING eps', 'PSTRING ($ptascii("bad"))',
               'PSTRING ($ptascii("1.0"))', 'PSTRING ([48, 0])',
               'PSTRING ([256])', 'PSTRING_CARRIER INTERNED_STRING ([48, 0])',
               'PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("0x"))',
               'PARRAY 0', 'POBJECT 0', 'PUNDEFINED')
    for value in admitted:
        guards += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.RESULT = KNOWN ({value})][.COMPLETION = THROWN "Error" ptbytes_message 9]']
    for value in refused:
        guards += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]']
    guards += prior.lines(r'''
S_peer_muted = S_base[.REPORTING = 0][.ERRORHANDLER.LEVELS = 0][.ERRORFATALTRACE = eps]
S_peer_muted.ERRORHANDLER.CALLBACK = S_base.ERRORHANDLER.CALLBACK
$unset_intermediate(S_peer_muted, pvalue_base, ROOT n_base, KNOWN (PINT 99), 9) = S_peer_muted[.RESULT = KNOWN (PINT 99)][.COMPLETION = THROWN "Error" ptbytes_message 9]
''')
    for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 0',
                  'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560'):
        guards += [f'$unset_string_key(S_peer_muted, {value}, 9) = S_peer_muted',
                   f'$unset_intermediate(S_peer_muted, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_peer_muted[.COMPLETION = THROWN "Error" ptbytes_generic 9]']
    guards += prior.lines(r'''
S_peer_request = S_base[.STRINGDATA = S_base.STRINGDATA ++ [$ptascii("0x")]]
pvalue_peer_request_key = PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("0x"))
$string_carrier_valid(S_peer_request, pvalue_peer_request_key)
$unset_intermediate(S_peer_request, pvalue_base, ROOT n_base, KNOWN pvalue_peer_request_key, 9) = S_peer_request[.RESULT = KNOWN pvalue_peer_request_key][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_peer_request, pvalue_base, ROOT n_base, KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("99"))), 9) = S_peer_request[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_intermediate(S_peer_request, PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("0x")), ROOT n_base, KNOWN (PINT 99), 9) = S_peer_request[.RESULT = KNOWN (PINT 99)][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_peer_request, PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("99")), ROOT n_base, KNOWN (PINT 99), 9) = S_peer_request[.COMPLETION = THROWN "Error" ptbytes_generic 9]
S_peer_unregistered = S_base[.ERRORHANDLER.CALLBACK = eps]
$unset_intermediate(S_peer_unregistered, pvalue_base, ROOT n_base, KNOWN (PINT 99), 9) = S_peer_unregistered[.RESULT = KNOWN (PINT 99)][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_base, PSTRING ($ptascii("ab")), ROOT n_base, KNOWN (PINT 99), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_base, PSTRING_CARRIER INTERNED_STRING ([256]), ROOT n_base, KNOWN (PINT 99), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]
''')
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = (own, Path(source.__file__).resolve())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    source.INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert source.INDEX in (0, 1)
    prior.NAME = tuple(cases.CASES)[source.INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded = cases, conditions, source.recorded
    passed = prior.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['mode'], report['raw_unset_steps'] = 'fixture SL', 1
    report['inputs'].update(before)
    report['scope'] = 'Independent source-reached registered-handler nested-UNSET fixtures preserve the exact raw/public/catch/budget front. Constructed quiet signed64 endpoints, unchecked offset magnitudes and integer numeric/leading text retain the nested Error without handler effects. Suppressed NULL/BOOL/FLOAT conversions are explicitly quiet yet still refused by the type gate. Invalid numeric/nonprimitive/NUL/byte/range and request-header values retain their prior refusal; authenticated request keys and bases retain exact registry identity. Empty-handler and raw-string routes stay bounded. Controls are source0/native0, reuse the same saved native originals without execution, and add no undefined-key callback, owning-key or lifetime breadth.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
