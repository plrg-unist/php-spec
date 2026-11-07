#!/usr/bin/env python3
"""Check real quiet queries and a mutable scalar key selecting the byte zero."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker
import string_offset_quiet_carriers_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAME = 'string-offset-quiet-interned-key'
DIGEST = '98e6fd9fb06ba7c90972a8078d5380d54f1f427e3738f14b8b5c749d763ff5d5'
PREFIX = r'''
dec $test_quiet_string_front(pstate, nat) : bool
def $test_quiet_string_front(S, 0) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask*
def $test_quiet_string_front(S, 1) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask*
def $test_quiet_string_front(S, n_stage) = false -- otherwise
dec $test_quiet_string_seek(pstate, nat, nat) : pstate
def $test_quiet_string_seek(S, n_stage, 0) = S
def $test_quiet_string_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_quiet_string_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_quiet_string_seek(S, n_stage, n) = $test_quiet_string_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_quiet_string_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_quiet_string_seek({start}, {stage}, 512)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_quiet_string_front({state}, {stage})']


def checks(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += lines(r'''
S_before.TODO = (ISSET_RESULT false z) :: ptask_after*
S_before.BASE = BASE_DIM pbase_source poperand_key z_key
pbase_source = BASE_VALUE (VARIABLE ptbytes_s z_s)
poperand_key = VARIABLE ptbytes_key z_key_name
ptbytes_s = $ptascii("s") /\ ptbytes_key = $ptascii("key")
S_before.CURRENT = eps /\ S_before.FRAMES = eps /\ S_before.GLOBALTABLE = eps
$lookup(S_before.ENV, ptbytes_s) = (n_s)
$lookup(S_before.ENV, ptbytes_key) = (n_key)
S_before.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("a0")))
S_before.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
~(n_s <- S_before.REFCELLS) /\ ~(n_key <- S_before.REFCELLS)
$heap_owners($heap_graph(S_before), HCELL n_s) = 1
$heap_owners($heap_graph(S_before), HCELL n_key) = 1
S_base = $quiet_base(S_before, pbase_source, z_key)
S_base.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("a0")))
S_key = $quiet_operand(S_base, poperand_key)
S_key.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
$value_nodes(PSTRING_CARRIER INTERNED_STRING ($ptascii("a0"))) = eps
$base_nodes(S_before.BASE) = eps
S_step = $isset_base(S_before, S_before.BASE, false, z)[.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S_before ~> S_step
S_step.COMPLETION = NORMAL /\ S_step.RESULT = KNOWN (PBOOL true)
S_step.ENV = S_before.ENV /\ S_step.STORE = S_before.STORE
S_step.STRINGDATA = S_before.STRINGDATA /\ S_step.EVENTS = S_before.EVENTS
$heap_graph(S_step) = $heap_graph(S_before)
S_pause = $drive(S_before, 0)
S_pause = S_before[.COMPLETION = BUDGET]
S_one = $drive(S_before, 1)
S_one = S_step[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
S_zero_key = S_before[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))]
S_zero_presence = $isset_base(S_zero_key, S_zero_key.BASE, false, z)
S_zero_presence.COMPLETION = NORMAL /\ S_zero_presence.RESULT = KNOWN (PBOOL true)
S_zero_empty = $isset_base(S_zero_key, S_zero_key.BASE, true, z)
S_zero_empty.COMPLETION = NORMAL /\ S_zero_empty.RESULT = KNOWN (PBOOL true)
S_zero_empty.STORE = S_zero_key.STORE /\ S_zero_empty.EVENTS = S_zero_key.EVENTS
S_nonempty = $isset_base(S_before, S_before.BASE, true, z)
S_nonempty.RESULT = KNOWN (PBOOL false)
$isset_string(S_before, $ptascii("a0"), PSTRING_CARRIER INTERNED_STRING ($ptascii("0")), false, z) = $isset_string(S_before, $ptascii("a0"), PSTRING ($ptascii("0")), false, z)
$quiet_dimension_value(S_before, PSTRING_CARRIER INTERNED_STRING ([97,0]), PINT 0, z) = S_before[.RESULT = KNOWN PNULL]
$isset_dimension_value(S_before, PSTRING_CARRIER INTERNED_STRING ([256]), PINT 0, false, z) = S_before[.RESULT = KNOWN (PBOOL false)]
''')
    values += reach('S_coalesce', 'S_step', 1)
    values += lines(r'''
S_coalesce.TODO = (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*
S_coalesce.BASE = BASE_DIM pbase_source poperand_key z_key
S_selected = $quiet_base(S_coalesce, S_coalesce.BASE, z_left)
S_selected.RESULT = KNOWN (PSTRING ($ptascii("a")))
S_out = $coalesce_result($constant_quiet_capture(S_selected)[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)], expression_right, z_left, z_right)
PhpStep: S_coalesce ~> S_out
S_out.COMPLETION = NORMAL /\ S_out.RESULT = KNOWN (PSTRING ($ptascii("a")))
S_out.TODO = ptask_tail* /\ S_out.STORE = S_coalesce.STORE
S_out.EVENTS = S_coalesce.EVENTS /\ S_out.STRINGDATA = S_coalesce.STRINGDATA
S_coalesce_zero = S_coalesce[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))]
S_selected_zero = $quiet_base(S_coalesce_zero, S_coalesce_zero.BASE, z_left)
S_selected_zero.COMPLETION = NORMAL /\ S_selected_zero.RESULT = KNOWN (PSTRING ($ptascii("0")))
S_out_zero = $coalesce_result($constant_quiet_capture(S_selected_zero)[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)], expression_right, z_left, z_right)
PhpStep: S_coalesce_zero ~> S_out_zero
S_out_zero.COMPLETION = NORMAL /\ S_out_zero.RESULT = KNOWN (PSTRING ($ptascii("0")))
S_out_zero.TODO = ptask_tail* /\ S_out_zero.EVENTS = S_coalesce.EVENTS
S_out_zero.STORE = S_coalesce_zero.STORE /\ S_out_zero.STRINGDATA = S_coalesce.STRINGDATA
$call_descriptors_valid(S_coalesce_zero)
''')
    return values


def run(out=None, process_seconds=180):
    source_bytes = cases.CASES[NAME]
    assert hashlib.sha256(source_bytes).hexdigest() == DIGEST
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='string-offset-quiet-peer-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'source.php'
    source.write_bytes(source_bytes)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        adapter.close()
    conditions = checks(checked['fixture'], source)
    fixture = out / 'test.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (x if x.startswith('PhpStep:') else 'if ' + x) + '\n' for x in conditions))
    (out / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], out, 'model', environment, process_seconds)
    passed = process['exit'] == 0 and not process['timeout'] and (out / 'model.stdout').read_bytes() == b'true\n' and (out / 'model.stderr').read_bytes() == b''
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': [NAME], 'assertions': len(conditions), 'source_sha256': DIGEST, 'process': process, 'passed': passed}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(NAME, len(conditions), 'PASS' if passed else 'FAIL', flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
