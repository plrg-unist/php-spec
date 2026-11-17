#!/usr/bin/env python3
"""Quiet registered-handler nested unsets retain their real delayed keys."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as prior
import string_offset_nested_unset_registered_quiet_key_cases as cases

INDEX = 0
recorded_prior = prior.recorded


def recorded(command, stem, cap):
    runner = str(prior.ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
    if command[0] == runner:
        command = [command[0], '--sl', *command[1:]]
    return recorded_prior(command, stem, cap)


def conditions(program, path):
    line = (5, 6)[INDEX]
    base = ('PSTRING_CARRIER INTERNED_STRING ($ptascii("ab"))',
            'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcd"))')[INDEX]
    key = ('PINT 99', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))')[INDEX]
    inner = ('KNOWN (PINT 99)', 'VARIABLE ($ptascii("key")) 6')[INDEX]
    final = ('VARIABLE ($ptascii("missing")) 5', 'KNOWN (' + key + ')')[INDEX]
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')']
    checks += prior.lines(r'''
S_initial.COMPLETION = BUDGET
S_found = $nested_unset_seek(S_initial, 512)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
S.TODO = UNSET_ARRAY :: ptask_tail*
poperand_inner = INNER
poperand_final = FINAL
S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) LINE)) poperand_inner LINE) poperand_final LINE
S.ORIGIN = (PORIGIN 0 pcpath)
S.REQUEST = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
S.EVENTS = eps /\ S.ERRORHANDLER.CALLBACK =/= eps
$lookup(S.ENV, $ptascii("base")) = (n_base)
pvalue_base = BASE
pvalue_key = KEY
S.STORE[n_base] = DEFINED pvalue_base
~(n_base <- S.REFCELLS)
$string_carrier_valid(S, pvalue_base)
$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S)
S_base = $base_find(S, BASE_VALUE (VARIABLE ($ptascii("base")) LINE), LINE)
S_base = S[.LOCATION = ROOT n_base][.RESULT = KNOWN pvalue_base]
S_key = S_base[.RESULT = KNOWN pvalue_key]
$resolve_at(S_base, poperand_inner, LINE) = S_key
$type_bytes(pvalue_key) <- [$ptascii("int"), $ptascii("string")]
$unset_terminal_key(S_key, pvalue_key)
$unset_string_key(S_key, pvalue_key, LINE) = S_key
ptbytes_message = $ptascii("Cannot use string offset as an array")
ptbytes_generic = $ptascii("Cannot unset offset in a non-array variable")
$unset_intermediate(S_base, pvalue_base, ROOT n_base, poperand_inner, LINE) = S_key[.COMPLETION = THROWN "Error" ptbytes_message LINE]
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
S_done.STORE[n_base] = S.STORE[n_base]
S_done.STRINGDATA = S.STRINGDATA /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
S_done.ERRORHANDLER = S.ERRORHANDLER /\ S_done.ERRORHANDLERS = S.ERRORHANDLERS
$nested_unset_outputs(S_done.EVENTS) = $ptascii("OUTPUT")
$nested_unset_diagnostics(S_done.EVENTS) = eps
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S, 1000) = S_done
'''.replace('INNER', inner).replace('FINAL', final).replace('LINE', str(line))
       .replace('pvalue_base = BASE', 'pvalue_base = ' + base)
       .replace('pvalue_key = KEY', 'pvalue_key = ' + key)
       .replace('OUTPUT', cases.OUTPUTS[tuple(cases.CASES)[INDEX]].decode()))
    if INDEX == 0:
        checks += ['$lookup(S.ENV, $ptascii("missing")) = eps',
                   '$lookup(S_done.ENV, $ptascii("missing")) = eps']
    else:
        checks += ['$lookup(S.ENV, $ptascii("key")) = (n_key)',
                   'S.STORE[n_key] = DEFINED pvalue_key',
                   'S_done.STORE[n_key] = S.STORE[n_key]']
    reached = len(checks)
    for value in ('PNULL', 'PBOOL false', 'PFLOAT 0', 'PINT 9223372036854775808',
                  'PSTRING_CARRIER INTERNED_STRING ([0])'):
        checks += [f'$unset_intermediate(S_base, pvalue_base, ROOT n_base, KNOWN ({value}), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]']
    checks += prior.lines(r'''
S_muted = S_base[.REPORTING = 0][.ERRORHANDLER.LEVELS = 0]
$unset_intermediate(S_muted, pvalue_base, ROOT n_base, KNOWN PNULL, 9) = S_muted[.COMPLETION = THROWN "Error" ptbytes_generic 9]
S_legacy = S_base[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("heldHandler")))][.ERRORHANDLER.LEVELS = 2]
$unset_intermediate(S_legacy, PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")), ROOT n_base, KNOWN (PINT 0), 9) = S_legacy[.RESULT = KNOWN (PINT 0)][.COMPLETION = THROWN "Error" ptbytes_message 9]
$unset_intermediate(S_base, PSTRING ($ptascii("ab")), ROOT n_base, KNOWN (PINT 0), 9) = S_base[.COMPLETION = UNSUPPORTED "intermediate string offset unset"]
$unset_intermediate(S_base, PSTRING_CARRIER INTERNED_STRING ([0]), ROOT n_base, KNOWN (PINT 0), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]
$unset_intermediate(S_base, PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("ab")), ROOT n_base, KNOWN (PINT 0), 9) = S_base[.COMPLETION = THROWN "Error" ptbytes_generic 9]
S_budget = S_base[.COMPLETION = BUDGET]
$unset_intermediate(S_budget, pvalue_base, ROOT n_base, KNOWN (PINT 0), 9) = S_budget
''')
    checks += [f'$stringify(S, PINT {line}, {line}) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("{line}")))]']
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
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['inputs'][str(own)] = before
    report['scope'] = 'Genuine checked source/php_run0 reaches nested string UNSET under a registered handler with quiet int/text key, exact source carrier and full-state quiet resolve/key certificates. Exact raw/public/catch/budget behavior preserves base/handler/storage; integer99 checks no bounds or final missing-CV read, while current key0x retains the final assignment before delayed inner read. NULL/BOOL/FLOAT, malformed/NUL/raw/REQUEST and BUDGET fences remain literal, including suppression; one affected old helper expectation promotes without old campaign renewal. Fixture source0/native0 and saved native observations reused once.'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
