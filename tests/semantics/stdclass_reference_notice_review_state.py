#!/usr/bin/env python3
"""Check named private-cell ownership while the producer changes object identity."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
from stdclass_reference_notice_review_cases import CASES

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $stdr_output(pevent*) : ptbytes
def $stdr_output(eps) = eps
def $stdr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $stdr_output(pevent*)
dec $stdr_stage(pstate, nat) : bool
def $stdr_stage(S, 0) = $named_reference_notice_pending(S)
def $stdr_stage(S, 1) = true
  -- if S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask*
def $stdr_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $stdr_output(S.EVENTS) = $ptascii("1:5;")
def $stdr_stage(S, n) = false -- otherwise
dec $stdr_seek(pstate, nat, nat) : pstate
def $stdr_seek(S, n_stage, n) = S
  -- if $stdr_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $stdr_seek(S, n_stage, n) = $stdr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$stdr_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $stdr_seek(S, n_stage, n) = S -- otherwise
'''

REACHED = r'''
S_pre = $stdr_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$stdr_stage(S_pre, 0)
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_old)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_pre.ENV, $ptascii("alias")) = (n_copy)
n_copy =/= n_source
S_pre.STORE[n_source] = DEFINED (POBJECT n_old)
S_pre.STORE[n_copy] = DEFINED (POBJECT n_old)
$call_reference_operand_valid(S_pre, REFERENCE n_copy)
$objectprops_record_at(S_pre.OBJECTPROPS, n_old) = (pobjectprops_old)
pobjectprops_old.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}]
pobjectprops_old.MATERIALIZED
$object_table_at(S_pre.OBJECTTABLES, n_old) = eps
$node_children(S_pre, HOBJECT n_old) = eps
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HOBJECT n_old) = 3
$heap_owners(H_pre, HCELL n_copy) = 2
$heap_owners(H_pre, HCELL n_source) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
n_private =/= n_copy /\ n_private =/= n_source
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after = {SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps}
S_notice.STORE[n_private] = DEFINED (POBJECT n_old)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HOBJECT n_old]
$node_children(S_notice, HOBJECT n_old) = eps
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HOBJECT n_old) = 3
$heap_owners(H_notice, HCELL n_copy) = 2
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_resume = $stdr_seek(S_notice, 1, 512)[.COMPLETION = NORMAL]
$stdr_stage(S_resume, 1)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("source")) = (n_source)
S_resume.STORE[n_source] = DEFINED (POBJECT n_new)
n_new =/= n_old
$objectprops_at(S_resume.OBJECTPROPS, n_new) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 77)))}])
S_resume.STORE[n_private] = DEFINED (POBJECT n_old)
S_resume.STORE[n_copy] = DEFINED (POBJECT n_old)
$objectprops_at(S_resume.OBJECTPROPS, n_old) = (pobjectprops_old.SLOTS)
$node_children(S_resume, HCELL n_private) = [HOBJECT n_old]
H_resume = $heap_graph(S_resume)
$heap_owners(H_resume, HCELL n_private) = 1
$heap_owners(H_resume, HOBJECT n_old) = 2
$heap_owners(H_resume, HOBJECT n_new) = 1
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid(H_resume)
S_returned = $stdr_seek(S_resume, 2, 512)[.COMPLETION = NORMAL]
$stdr_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (POBJECT n_old)
S_returned.STORE[n_copy] = DEFINED (POBJECT n_old)
$objectprops_at(S_returned.OBJECTPROPS, n_old) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 9)))}])
$objectprops_at(S_returned.OBJECTPROPS, n_new) = ([{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 77)))}])
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HCELL n_private) = 1
$heap_owners(H_returned, HOBJECT n_old) = 2
$heap_owners(H_returned, HOBJECT n_new) = 1
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
S_full = $drive(S_returned, 1000)
S_full.COMPLETION = NORMAL
$stdr_output(S_full.EVENTS) = $ptascii("1:5;9:77:1;9:13;")
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
$lookup(S_full.ENV, $ptascii("copy")) = (n_copy)
$lookup(S_full.ENV, $ptascii("alias")) = (n_copy)
S_full.STORE[n_private] = DEFINED (PINT 13)
S_full.STORE[n_copy] = DEFINED (POBJECT n_old)
S_full.STORE[n_source] = DEFINED (POBJECT n_new)
$node_children(S_full, HCELL n_private) = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_private) = 1
$heap_owners(H_full, HCELL n_copy) = 2
$heap_owners(H_full, HOBJECT n_old) = 1
$heap_owners(H_full, HOBJECT n_new) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
S_eof = $stdr_seek(S_full, 2, 512)
S_eof = S_full
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_notice, 1)
S_split = $drive(S_one[.COMPLETION = NORMAL], 1)
S_direct = $drive(S_notice, 2)
S_split = S_direct
'''.strip().splitlines()

DERIVED = r'''
~$named_reference_notice_entries(S_pre, [ENTRY (KINT 0) (DIRECT (POBJECT n_old))])
~$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (ALIAS n_private)])
n_map = |S_notice.OBJECTS|
S_map = S_notice[.OBJECTS = S_notice.OBJECTS ++ [WEAKMAP ({KEY n_old, VALUE (PINT 0), BEFORE eps, ORDER 0})]][.ALLOCATIONS = S_notice.ALLOCATIONS ++ [HOBJECT n_map]]
$node_children(S_map, HOBJECT n_old) = eps
$weakmap_key_waiting(S_map, n_old)
~$named_reference_notice_object(S_map, POBJECT n_old)
~$named_reference_notice_operand(S_map, KNOWN (POBJECT n_old))
~$named_reference_notice_operand(S_map, REFERENCE n_private)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    native_path = args.native_provenance.resolve()
    native = json.loads(native_path.read_bytes())
    source = Path(native['command'][-1])
    assert source.read_bytes() == CASES[native['id']]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='stdclass-reference-review-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), native_path, source,
        ROOT / 'tests/semantics/stdclass_reference_notice_review_cases.py',
        ROOT / 'tests/semantics/stdclass_reference_notice_review_cases.json',
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
        'frontend/target.php', 'frontend/wire.php', 'tests/semantics/error_handler_run.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
            base64.b64encode(os.fsencode(source)).decode()) + ')'
        checks = [initial] + REACHED + DERIVED
        fixture = directory / 'state.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'source': str(source),
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'conditions': len(checks), 'reached_conditions': len(REACHED) + 1,
            'derived_conditions': len(DERIVED), 'heap_bindings': 5,
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture = directory / 'state.watsup'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 480)
    stable = before == fingerprints() and hashlib.sha256(fixture.read_bytes()).hexdigest() == prepared['fixture_sha256']
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_stable and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable,
        module_count=len(modules), mode='AL/cache=false/det=true',
        process=process, passed=passed, source_agreements=0)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('named stdClass ownership/refusals/budget', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
