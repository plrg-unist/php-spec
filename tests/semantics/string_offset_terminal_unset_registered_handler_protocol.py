#!/usr/bin/env python3
"""Registered handlers stay idle at source-reached terminal string unsets."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as prior
import string_offset_terminal_unset_registered_handler_cases as cases

INDEX = 0
recorded_prior = prior.recorded


def recorded(command, stem, cap):
    runner = str(prior.ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
    if command[0] == runner:
        command = [command[0], '--sl', *command[1:]]
    return recorded_prior(command, stem, cap)


def conditions(program, path):
    line = (10, 12)[INDEX]
    base = ('PSTRING_CARRIER INTERNED_STRING ($ptascii("ab"))',
            'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcd"))')[INDEX]
    key = ('PFLOAT 9218868437227405312',
           'PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))')[INDEX]
    output = cases.OUTPUTS[tuple(cases.CASES)[INDEX]].decode()
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')']
    checks += prior.lines(r'''
S_initial.COMPLETION = BUDGET
S_found = $nested_unset_seek(S_initial, 512)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
S.TODO = UNSET_ARRAY :: ptask_tail*
S.BASE = BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) LINE)) (VARIABLE ($ptascii("key")) LINE) LINE
S.ORIGIN = (PORIGIN 0 pcpath)
S.REQUEST = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
S.EVENTS = eps /\ S.ERRORHANDLER.CALLBACK =/= eps
$lookup(S.ENV, $ptascii("base")) = (n_base)
$lookup(S.ENV, $ptascii("key")) = (n_key)
n_base =/= n_key
S.STORE[n_base] = DEFINED pvalue_base
S.STORE[n_key] = DEFINED pvalue_key
~(n_base <- S.REFCELLS) /\ ~(n_key <- S.REFCELLS)
$string_carrier_valid(S, pvalue_base)
$unset_terminal_key(S, pvalue_key)
$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S)
ptbytes_message = $ptascii("Cannot unset string offsets")
ptbytes_generic = $ptascii("Cannot unset offset in a non-array variable")
PhpStep: S ~> S_raw
S_raw = S[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_base][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ptbytes_message LINE]
S_raw.ERRORHANDLER = S.ERRORHANDLER /\ S_raw.EVENTS = eps
S_raw.STORE = S.STORE /\ S_raw.STRINGDATA = S.STRINGDATA
$heap_graph(S_raw) = $heap_graph(S[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL])
$drive(S, 0) = S[.COMPLETION = BUDGET]
S_public = $drive(S, 1)
S_public.COMPLETION = BUDGET /\ S_public.EVENTS = eps
S_public.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_public.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "Error"
S_public.ERRORHANDLER = S.ERRORHANDLER /\ S_public.FRAMES = eps
S_done = $drive_steps(S_public[.COMPLETION = NORMAL], 1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_base] = S.STORE[n_base] /\ S_done.STORE[n_key] = S.STORE[n_key]
S_done.STRINGDATA = S.STRINGDATA ++ [$ptascii("LINE")] /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
S_done.ERRORHANDLER = S.ERRORHANDLER /\ S_done.ERRORHANDLERS = S.ERRORHANDLERS
$nested_unset_outputs(S_done.EVENTS) = $ptascii("OUTPUT")
$nested_unset_diagnostics(S_done.EVENTS) = eps
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S, 1000) = S_done
'''.replace('LINE', str(line)).replace('OUTPUT', output))
    checks[checks.index('S.STORE[n_base] = DEFINED pvalue_base'):checks.index('S.STORE[n_base] = DEFINED pvalue_base')] = [
        'pvalue_base = ' + base, 'pvalue_key = ' + key]
    reached = len(checks)
    checks += prior.lines(r'''
S_key = S[.RESULT = KNOWN pvalue_key]
$unset_terminal_nonarray(S_key, pvalue_base, 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_message 9]
S_no_handler = S_key[.ERRORHANDLER.CALLBACK = eps]
$unset_terminal_nonarray(S_no_handler, pvalue_base, 9) = S_no_handler[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_nonarray(S_key, pvalue_base, 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER INTERNED_STRING ([0]), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER INTERNED_STRING ([256]), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_terminal_nonarray(S_key, PSTRING_CARRIER (REQUEST_STRING 99) ($ptascii("ab")), 9) = S_key[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_terminal_nonarray(S[.RESULT = KNOWN PUNDEFINED], pvalue_base, 9) = S[.RESULT = KNOWN PUNDEFINED][.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_terminal_nonarray(S[.RESULT = REFERENCE n_key], pvalue_base, 9) = S[.RESULT = REFERENCE n_key][.COMPLETION = THROWN "Error" ptbytes_generic 9]
S_legacy = S_key[.STRINGDATA = [$ptascii("ab")]][.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("heldHandler")))][.ERRORHANDLER.LEVELS = 2]
$unset_terminal_nonarray(S_legacy, PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")), 9) = S_legacy[.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_terminal_nonarray(S_legacy, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("ab")), 9) = S_legacy[.COMPLETION = THROWN "Error" ptbytes_message 9]
''')
    checks += [f'$stringify(S, PINT {line}, {line}) = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("{line}")]][.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("{line}")))]']
    return checks, len(checks) - reached


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded = cases, conditions, recorded
    passed = prior.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['mode'] = 'SL'
    report['raw_unset_steps'] = 1
    report['inputs'][str(own)] = before
    report['scope'] = 'Genuine checked source/php_run0 reaches one terminal UNSET_DIM with an authenticated non-NUL string carrier, defined admitted CV key and registered handler. Exact raw step/public Error allocation/catch/budget continuation preserve handler, source state, key and base without invoking a callback or casting the key. Fixture source0/native0; native observations reused once. Generic unset, invalid/NUL carriers, unsupported keys, ownership and held lanes remain unchanged.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
