#!/usr/bin/env python3
"""Independent STRING-key Error priority with a registered unset handler."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_registered_string_error_protocol as source

prior, cases = source.prior, source.cases


def conditions(program, path):
    checks, derived = source.conditions(program, path)
    guards = []
    errors = ('PSTRING eps', 'PSTRING ($ptascii("bad"))',
              'PSTRING ($ptascii("1.0"))', 'PSTRING ($ptascii("1e0"))',
              'PSTRING ($ptascii("9223372036854775808"))',
              'PSTRING ($ptascii("-9223372036854775809"))',
              'PSTRING ($ptascii("NAN"))', 'PSTRING ($ptascii("INF"))',
              'PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))')
    quiet = ('PINT $(-9223372036854775808)', 'PINT 9223372036854775807',
             'PINT 99', 'PSTRING ($ptascii("0x"))',
             'PSTRING ($ptascii("-0"))', 'PSTRING ($ptascii("99tail"))')
    refused = ('PINT $(-9223372036854775809)', 'PINT 9223372036854775808',
               'PSTRING ([49, 0])', 'PSTRING ([256])',
               'PSTRING_CARRIER INTERNED_STRING ([49, 0])',
               'PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("1.5"))',
               'PARRAY 0', 'POBJECT 0', 'PUNDEFINED')
    for values, message in ((errors, 'Cannot unset string offsets'),
                            (quiet, 'Cannot use string offset as an array')):
        for value in values:
            guards += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.RESULT = KNOWN ({value})][.COMPLETION = THROWN "Error" ($ptascii("{message}")) 9]']
    for value in refused:
        guards += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]']
    guards += prior.lines(r'''
S_peer_muted = S_base[.REPORTING = 0][.ERRORHANDLER.LEVELS = 0][.ERRORFATALTRACE = eps]
S_peer_muted.ERRORHANDLER.CALLBACK = S_base.ERRORHANDLER.CALLBACK
$unset_intermediate(S_peer_muted, pvalue_base, ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_peer_muted[.RESULT = KNOWN (PSTRING ($ptascii("bad")))][.COMPLETION = THROWN "Error" ($ptascii("Cannot unset string offsets")) 9]
''')
    for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 0',
                  'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560'):
        guards += [f'$unset_string_key(S_peer_muted, {value}, 9) = S_peer_muted',
                   f'$unset_intermediate(S_peer_muted, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_peer_muted[.COMPLETION = THROWN "Error" ptbytes_generic 9]']
    guards += prior.lines(r'''
S_peer_request = S_base[.STRINGDATA = S_base.STRINGDATA ++ [$ptascii("1.5")]]
pvalue_peer_request_key = PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("1.5"))
$string_carrier_valid(S_peer_request, pvalue_peer_request_key)
$unset_intermediate(S_peer_request, pvalue_base, ROOT n_base, KNOWN pvalue_peer_request_key, 9) = S_peer_request[.RESULT = KNOWN pvalue_peer_request_key][.COMPLETION = THROWN "Error" ($ptascii("Cannot unset string offsets")) 9]
$unset_intermediate(S_peer_request, pvalue_base, ROOT n_base, KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_base.STRINGDATA|)) ($ptascii("bad"))), 9) = S_peer_request[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_intermediate(S_peer_request, pvalue_peer_request_key, ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_peer_request[.RESULT = KNOWN (PSTRING ($ptascii("bad")))][.COMPLETION = THROWN "Error" ($ptascii("Cannot unset string offsets")) 9]
S_peer_unregistered = S_base[.ERRORHANDLER.CALLBACK = eps]
$unset_intermediate(S_peer_unregistered, pvalue_base, ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_peer_unregistered[.RESULT = KNOWN (PSTRING ($ptascii("bad")))][.COMPLETION = THROWN "Error" ($ptascii("Cannot unset string offsets")) 9]
$unset_intermediate(S_base, PSTRING ($ptascii("ab")), ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_base, PSTRING_CARRIER INTERNED_STRING ([0]), ROOT n_base, KNOWN (PSTRING ($ptascii("bad"))), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]
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
    report['scope'] = 'Independent genuine registered-handler nested-UNSET source fronts retain exact own-Error priority, public Error kind, missing-CV laziness, delayed key assignment, cleanup and split budgets. Constructed empty/nonnumeric/fractional/exponent/overflow-text STRING keys keep Cannot unset string offsets while quiet signed64 and leading-integer keys keep the distinct nested Error. Suppressed NULL/BOOL/FLOAT stay type-refused even when their converter is quiet. Exact REQUEST keys/base authenticate registry bytes; malformed/NUL/nonprimitive/range/header and raw-string fences remain bounded. Controls are source0/native0 and reuse the same saved native originals without execution; no undefined-key callback or owning/lifetime breadth is added.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
