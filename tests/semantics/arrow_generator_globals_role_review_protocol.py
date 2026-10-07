#!/usr/bin/env python3
"""One genuine GLOBALS cached-key source-role counterexample, prepared separately."""
import base64
import json
import os
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
import arrow_generator_prepare as source
import arrow_generator_warning_review_protocol as warning
import generator_force_close_protocol as driver
from request_environment_state import request_fixture

OWN = str(Path(__file__).resolve().relative_to(ROOT))
CASES = {'globals-cached-scalar-source-role': source.CASES['missing-value-preserves-globals-snapshot-key']}
plain_run = source.run


def request_native_run(argv, stem, timeout):
    if stem.name != 'native':
        return plain_run(argv, stem, timeout)
    path = stem.parent / 'source.php'
    b64 = driver.driver.b64
    request = {'env': [[b64(b'LC_ALL'), b64(b'C')], [b64(b'TZ'), b64(b'UTC')]],
               'argv': [b64(os.fsencode(path))], 'file': b64(os.fsencode(path)),
               'seconds': '1700000000', 'microseconds': 125000,
               'variables': b64(b'EGPCS'), 'jit': True, 'cwd': b64(os.fsencode(ROOT))}
    (stem.parent / 'request.json').write_text(json.dumps(request) + '\n')
    (stem.parent / 'request-profile.json').write_text(json.dumps({**driver.driver.types.PROFILE,
        'variables_order': 'EGPCS', 'auto_globals_jit': '1'}) + '\n')
    entries = [base64.b64decode(k) + b'=' + base64.b64decode(v) for k, v in request['env']]
    payload = stem.parent / 'request-input.bin'
    payload.write_bytes(b'PHPRQ001' + struct.pack('<qII', int(request['seconds']), request['microseconds'], len(entries))
                        + b''.join(struct.pack('<I', len(e)) + e for e in entries))
    argv = argv[:-1] + ['-d', 'variables_order=EGPCS', '-d', 'auto_globals_jit=1', argv[-1]]
    return plain_run([sys.executable, '-c', source.driver.REQUEST_EXEC, *argv, str(ROOT),
                      str(ROOT / '.tools/request-clock.so'), str(payload)], stem, timeout)


def assertions(checked, path, directory, name):
    q = request_fixture(json.loads((directory / 'request.json').read_text()))
    initial = '$php_request_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ',' + q + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += warning.seek('S_returned', 'S_initial', 1)
    checks += r'''
S_returned.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*
perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin (KNOWN (PARRAY n_snapshot))
perrorread.TASK = perrorread.ORIGINAL
S_returned.REQUEST = (Q)
$request_valid(Q)
$error_read_valid(S_returned,perrorread)
$origin_node(S_returned.SOURCES,porigin) = (NExprYield expression_key phpType5_value metadata)
$ppglobals_base(expression_key)
$generator_yield_read_key_source(S_returned,porigin,(KNOWN (PARRAY n_snapshot)))
perrorread_bad = perrorread[.ORIGINAL = GENERATOR_YIELD_STORE porigin (KNOWN (PINT 7))][.TASK = GENERATOR_YIELD_STORE porigin (KNOWN (PINT 7))]
S_bad = S_returned[.TODO = (ERROR_READ_RESULT perrorread_bad) :: ptask_tail*]
S_bad.SOURCES = S_returned.SOURCES
S_bad.CODE = S_returned.CODE
S_bad.CLOSURETEMPLATES = S_returned.CLOSURETEMPLATES
S_bad.FRAMES = S_returned.FRAMES
S_bad.CURRENT = S_returned.CURRENT
S_bad.REQUEST = S_returned.REQUEST
$heap_valid($heap_graph(S_bad))
~$error_read_valid(S_bad,perrorread_bad)
~$call_descriptors_valid(S_bad)
'''.strip().splitlines()
    return checks


def main():
    source.WATCHED = source.WATCHED + [OWN, 'tests/semantics/arrow_generator_warning_review_protocol.py',
        'tests/semantics/request_environment_state.py', 'tests/semantics/destructuring.py',
        'native/request_clock.c', 'scripts/build-request-provider.sh', '.tools/request-clock.so']
    source.run = request_native_run
    driver.source = source
    driver.CASES = CASES
    driver.PREFIX = warning.PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
