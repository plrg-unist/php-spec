#!/usr/bin/env python3
"""Check static-source transfer, real roots and explicit-CV singleton COW."""
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

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $tsan_output(pevent*) : ptbytes
def $tsan_output(eps) = eps
def $tsan_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $tsan_output(pevent*)
dec $tsan_stage(pstate, nat) : bool
def $tsan_stage(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
  -- if S.RESULT = KNOWN (PARRAY n_root)
def $tsan_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tsan_output(S.EVENTS) = $ptascii("A;R;")
def $tsan_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tsan_output(S.EVENTS) = $ptascii("R;")
def $tsan_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $tsan_output(S.EVENTS) = $ptascii("R;V;")
def $tsan_stage(S, 4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tsan_output(S.EVENTS) = $ptascii("A;R;T;F;")
def $tsan_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("take")
  -- if $tsan_output(S.EVENTS) = $ptascii("R;V;U;")
def $tsan_stage(S, 6) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $tsan_output(S.EVENTS) = $ptascii("R;V;U;")
def $tsan_stage(S, n) = false -- otherwise
dec $tsan_seek(pstate, nat, nat) : pstate
def $tsan_seek(S, n_stage, n) = S
  -- if $tsan_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $tsan_seek(S, n_stage, n) = $tsan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$tsan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $tsan_seek(S, n_stage, n) = $tsan_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$tsan_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $tsan_seek(S, n_stage, n) = S -- otherwise
'''

SHARED = r'''
S_pre = $tsan_seek(S_initial, 0, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_pre, 0)
$tsan_output(S_pre.EVENTS) = $ptascii("A;")
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_old_cell)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_new_cell)
$lookup(S_pre.ENV, $ptascii("old")) = (n_old_cv)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_pre.STORE[n_old_cv] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cell] = DEFINED (POBJECT n_new)
n_old_cell =/= n_new_cell /\ n_old =/= n_new
$propref_at(S_pre.PROPREFS, n_old_cell) = ({CELL n_old_cell, SOURCES ([CLASS_PROP_SOURCE ppropertyid])})
$propref_source_valid(S_pre, n_old_cell, CLASS_PROP_SOURCE ppropertyid)
$class_static_at(S_pre.CLASSSTATICS, ppropertyid) = ({DECL ppropertyid, STATE PROP_VALUE (ALIAS n_old_cell)})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_old_cell]
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_old_cell), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_old_cell)]
$named_reference_notice_object_static_source(S_pre, n_old_cell)
$named_reference_notice_array(S_pre, PARRAY n_root)
$positional_reference_notice_pending(S_pre)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 3
$heap_owners(H_pre, HCELL n_old_cell) = 4
$heap_owners(H_pre, HOBJECT n_old) = 2
$heap_owners(H_pre, HOBJECT n_new) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HCELL n_old_cell) = 4
$class_static_roots(S_notice.CLASSSTATICS) = [HCELL n_old_cell]
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice) /\ $heap_valid(H_notice)
S_rebound = $tsan_seek(S_notice, 1, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_rebound, 1)
S_rebound.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_rebound.STORE[n_new_cell] = DEFINED (POBJECT n_new)
$propref_at(S_rebound.PROPREFS, n_old_cell) = eps
$propref_at(S_rebound.PROPREFS, n_new_cell) = ({CELL n_new_cell, SOURCES ([CLASS_PROP_SOURCE ppropertyid])})
$class_static_at(S_rebound.CLASSSTATICS, ppropertyid) = ({DECL ppropertyid, STATE PROP_VALUE (ALIAS n_new_cell)})
$class_static_roots(S_rebound.CLASSSTATICS) = [HCELL n_new_cell]
$node_children(S_rebound, HCELL n_old_cell) = [HOBJECT n_old]
$node_children(S_rebound, HCELL n_new_cell) = [HOBJECT n_new]
$named_reference_notice_object_static_source(S_rebound, n_new_cell)
$named_reference_notice_array(S_rebound, PARRAY n_root)
H_rebound = $heap_graph(S_rebound)
$heap_owners(H_rebound, HCELL n_old_cell) = 3
$heap_owners(H_rebound, HCELL n_new_cell) = 3
$heap_owners(H_rebound, HOBJECT n_old) = 2
$heap_owners(H_rebound, HOBJECT n_new) = 1
$call_descriptors_valid(S_rebound) /\ $heap_valid(H_rebound)
S_returned = $tsan_seek(S_rebound, 4, 1024)[.COMPLETION = NORMAL]
$tsan_stage(S_returned, 4)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
S_returned.STORE[n_old_cell] = DEFINED (PINT 17)
S_returned.STORE[n_new_cell] = DEFINED (POBJECT n_new)
$propref_at(S_returned.PROPREFS, n_old_cell) = eps
$propref_source_valid(S_returned, n_new_cell, CLASS_PROP_SOURCE ppropertyid)
$class_static_roots(S_returned.CLASSSTATICS) = [HCELL n_new_cell]
$node_children(S_returned, HCELL n_old_cell) = eps
$node_children(S_returned, HCELL n_new_cell) = [HOBJECT n_new]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_old_cell) = 5
$heap_owners(H_returned, HCELL n_new_cell) = 2
$heap_owners(H_returned, HOBJECT n_old) = 1
$heap_owners(H_returned, HOBJECT n_new) = 1
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

UNWRAP = r'''
S_pre = $tsan_seek(S_initial, 0, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_pre, 0)
$positional_reference_notice_pending(S_pre)
S_pre.RESULT = KNOWN (PARRAY n_root)
$lookup(S_pre.ENV, $ptascii("shared")) = (n_old_cell)
$lookup(S_pre.ENV, $ptascii("replacement")) = (n_new_cell)
$lookup(S_pre.ENV, $ptascii("held")) = (n_held)
S_pre.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_pre.STORE[n_held] = DEFINED (POBJECT n_old)
S_pre.STORE[n_new_cell] = DEFINED (POBJECT n_new)
n_old_cell =/= n_new_cell /\ n_old =/= n_new
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_old_cell)]
$propref_at(S_pre.PROPREFS, n_old_cell) = ({CELL n_old_cell, SOURCES ([CLASS_PROP_SOURCE ppropertyid])})
$class_static_roots(S_pre.CLASSSTATICS) = [HCELL n_old_cell]
$named_reference_notice_object_static_source(S_pre, n_old_cell)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_old_cell) = 3
$heap_owners(H_pre, HOBJECT n_old) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
S_rebound = $tsan_seek(S_pre, 2, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_rebound, 2)
$propref_at(S_rebound.PROPREFS, n_old_cell) = eps
$propref_source_valid(S_rebound, n_new_cell, CLASS_PROP_SOURCE ppropertyid)
$class_static_roots(S_rebound.CLASSSTATICS) = [HCELL n_new_cell]
S_rebound.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_rebound.STORE[n_new_cell] = DEFINED (POBJECT n_new)
H_rebound = $heap_graph(S_rebound)
$heap_owners(H_rebound, HCELL n_old_cell) = 2
$heap_owners(H_rebound, HCELL n_new_cell) = 3
$heap_owners(H_rebound, HOBJECT n_old) = 2
$call_descriptors_valid(S_rebound) /\ $heap_valid(H_rebound)
S_unset = $tsan_seek(S_rebound, 3, 512)[.COMPLETION = NORMAL]
$tsan_stage(S_unset, 3)
S_unset.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("shared")) = eps
$propref_at(S_unset.PROPREFS, n_old_cell) = eps
$class_static_roots(S_unset.CLASSSTATICS) = [HCELL n_new_cell]
H_unset = $heap_graph(S_unset)
$heap_owners(H_unset, HCELL n_old_cell) = 1
$heap_owners(H_unset, HCELL n_new_cell) = 3
$heap_owners(H_unset, HOBJECT n_old) = 2
$call_descriptors_valid(S_unset) /\ $heap_valid(H_unset)
S_copied = $tsan_seek(S_unset, 5, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_copied, 5)
$lookup(S_copied.ENV, $ptascii("v")) = (n_private)
S_copied.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
S_copied.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_copied.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_old)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$node_children(S_copied, HARRAY n_root) = [HCELL n_old_cell]
$node_children(S_copied, HARRAY n_copied) = [HOBJECT n_old]
H_copied = $heap_graph(S_copied)
$heap_owners(H_copied, HCELL n_old_cell) = 1
$heap_owners(H_copied, HCELL n_new_cell) = 2
$heap_owners(H_copied, HOBJECT n_old) = 3
$heap_owners(H_copied, HARRAY n_root) = 1
$heap_owners(H_copied, HARRAY n_copied) = 1
$call_descriptors_valid(S_copied) /\ $heap_valid(H_copied)
S_returned = $tsan_seek(S_copied, 6, 768)[.COMPLETION = NORMAL]
$tsan_stage(S_returned, 6)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_old_cell] = DEFINED (POBJECT n_old)
S_returned.STORE[n_new_cell] = DEFINED (POBJECT n_new)
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (PINT 17)), ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$propref_at(S_returned.PROPREFS, n_old_cell) = eps
$propref_source_valid(S_returned, n_new_cell, CLASS_PROP_SOURCE ppropertyid)
$class_static_roots(S_returned.CLASSSTATICS) = [HCELL n_new_cell]
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 1
$heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_old_cell) = 1
$heap_owners(H_returned, HCELL n_new_cell) = 2
$heap_owners(H_returned, HOBJECT n_old) = 2
$heap_owners(H_returned, HOBJECT n_new) = 1
$heap_owners(H_returned, HCELL n_private) = 1
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
S_returned.HELD = eps /\ S_returned.RETIREDOWNERS = eps
$call_descriptors_valid(S_returned) /\ $heap_valid(H_returned)
'''.strip().splitlines()

GROUPS = {
    'shared': ('positional-static-typed-old-cell-detach-shared-cow', SHARED),
    'unwrap': ('positional-static-typed-old-cell-explicit-cv-unset-unwrap', UNWRAP),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS, required=True)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    case, reached = GROUPS[args.group]
    catalogue = Path(__file__).with_name('typed_static_alias_stdclass_reference_notice_cases.json')
    row, = [row for row in json.loads(catalogue.read_bytes()) if row['id'] == case]
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    native_row, = [item for item in native['records'] if item['id'] == case]
    source = Path(native_row['command'][-1])
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['passed'] and native['mode'] == 'native-first' and native_row['passed']
    assert native['profile'] == profile and source.read_bytes() == row['source'].encode()
    assert native['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    assert native_row['cwd'] == str(ROOT)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    directory = args.output or Path(tempfile.mkdtemp(prefix='typed-static-alias-stdclass-reference-state-' + args.group + '-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__), catalogue, native_path, source,
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php', 'frontend/target.php',
        'frontend/wire.php', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], directory / 'frontend')
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
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    checks = [initial] + reached
    fixture = directory / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    prepared = {'revision': revision, 'inputs': before, 'group': args.group, 'case': case, 'source': str(source),
        'conditions': len(checks), 'reached_conditions': len(checks), 'derived_conditions': 0,
        'heap_bindings': sum(check.startswith('H_') for check in reached),
        'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
    (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], directory / 'run', 360)
    stable = before == fingerprints() and prepared['fixture_sha256'] == hashlib.sha256(fixture.read_bytes()).hexdigest()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (directory / 'run.stdout').read_bytes() == b'true\n' and not (directory / 'run.stderr').read_bytes())
    report = dict(prepared, inputs_stable=stable, head_stable=head_stable, module_count=len(modules),
        mode='AL/cache=false/det=true', process=process, source_agreements=0, passed=passed)
    (directory / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(args.group, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
