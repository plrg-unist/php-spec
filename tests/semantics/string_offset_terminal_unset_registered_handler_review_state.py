#!/usr/bin/env python3
"""Independent terminal-unset key priority and unchanged handler bounds."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_terminal_unset_registered_handler_protocol as source

prior, cases = source.prior, source.cases


def conditions(program, path):
    checks, derived = source.conditions(program, path)
    guards = []
    admitted = ('PNULL', 'PBOOL false', 'PBOOL true',
                'PINT $(-9223372036854775808)', 'PINT 9223372036854775807',
                'PFLOAT 0', 'PFLOAT 9218868437227405312',
                'PFLOAT 9221120237041090560', 'PSTRING eps',
                'PSTRING ($ptascii("bad"))')
    refused = ('PINT $(-9223372036854775809)', 'PINT 9223372036854775808',
               'PFLOAT 18446744073709551616', 'PUNDEFINED',
               'PARRAY 0', 'POBJECT 0', 'PSTRING ([0])', 'PSTRING ([256])',
               'PSTRING_CARRIER INTERNED_STRING ([0])',
               'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad"))')
    for prefix, values, message in (('admitted', admitted, 'ptbytes_message'),
                                    ('refused', refused, 'ptbytes_generic')):
        for index, value in enumerate(values):
            state = 'S_peer_unset_' + prefix + '_' + str(index)
            guards += [state + ' = S[.RESULT = KNOWN (' + value + ')]',
                       ('~' if prefix == 'refused' else '') + '$unset_terminal_key(' + state + ', ' + value + ')',
                       '$unset_terminal_nonarray(' + state + ', pvalue_base, 99) = ' + state + '[.COMPLETION = THROWN "Error" ' + message + ' 99]']
    guards += prior.lines(r'''
S_peer_unset_masked = S_key[.ERRORHANDLER.LEVELS = 0]
S_peer_unset_masked.ERRORHANDLER.CALLBACK = S_key.ERRORHANDLER.CALLBACK
$unset_terminal_nonarray(S_peer_unset_masked, pvalue_base, 99) = S_peer_unset_masked[.COMPLETION = THROWN "Error" ptbytes_message 99]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad")), 99) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 99]
$unset_intermediate(S_key, pvalue_base, ROOT n_base, KNOWN pvalue_key, 99) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 99]
''')
    if source.INDEX == 1:
        old = '$unset_intermediate(S_key, pvalue_base, ROOT n_base, KNOWN pvalue_key, 99) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 99]'
        assert guards.count(old) == 1
        guards[guards.index(old)] = old.replace('ptbytes_generic', 'ptbytes_message')
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
    report['scope'] = 'Independent source-reached registered-handler terminal UNSET fixtures retain exact raw/public/catch behavior and add full-state key-priority controls. Ten admitted scalar keys, including signed64 endpoints, NaN and infinity, throw the string-offset Error without conversion or handler effects; ten malformed/unsupported/NUL keys retain prior generic refusal. An out-of-range REQUEST carrier stays refused. The intermediate FLOAT control stays generic while the invalid STRING control keeps its own Error. A zero handler mask leaves terminal Error unchanged. These controls add source0/native0, make no undefined-key callback or owner expansion, and reuse the same saved native originals without execution. Prelaw NORMAL wrong-Error mismatches stay separate; no old campaign is replayed.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
