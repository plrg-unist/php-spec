#!/usr/bin/env python3
"""Check actual quiet stdClass Notice ownership, reference return and throw cleanup."""
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
dec $stdn_output(pevent*) : ptbytes
def $stdn_output(eps) = eps
def $stdn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $stdn_output(pevent*)
dec $stdn_stage(pstate, nat) : bool
def $stdn_stage(S, 0) = $positional_reference_notice_pending(S)
def $stdn_stage(S, 1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* 1 poperand* porigin? z) :: ptask*
def $stdn_stage(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $acquire_call_valid(S)
def $stdn_stage(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $stdn_stage(S, n) = false -- otherwise
dec $stdn_seek(pstate, nat, nat) : pstate
def $stdn_seek(S, n_stage, n) = S
  -- if $stdn_stage(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $stdn_seek(S, n_stage, n) = $stdn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$stdn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $stdn_seek(S, n_stage, n) = $stdn_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if ~$stdn_stage(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if $throwable_pending(S.COMPLETION)
def $stdn_seek(S, n_stage, n) = S -- otherwise
'''

NORMAL_PREFIX = r'''
S_pre = $stdn_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)
n_copy =/= n_source
S_pre.STORE[n_source] = DEFINED (POBJECT n_object)
S_pre.STORE[n_copy] = DEFINED (POBJECT n_object)
S_pre.OBJECTS[n_object] = STDINSTANCE
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_pre)
pobjectprops_pre.SLOTS = [{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}]
pobjectprops_pre.MATERIALIZED
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps
$node_children(S_pre, HOBJECT n_object) = eps
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HCELL n_source) = 1
$heap_owners(H_pre, HCELL n_copy) = 1
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) (porigin_call) z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
$node_children(S_notice, HOBJECT n_object) = eps
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HOBJECT n_object) = 3
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S_pre.HELD
$named_reference_notice_operand(S_notice, REFERENCE n_private)
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
'''.strip().splitlines()

THROW = r'''
S_pre = $stdn_seek(S_initial, 0, 512)[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
$lookup(S_pre.ENV, $ptascii("weak")) = (n_weak_cell)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_source] = DEFINED (POBJECT n_object)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
S_pre.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S_pre.OBJECTS[n_object] = STDINSTANCE
S_pre.OBJECTS[n_weak] = WEAKREFERENCE (n_object)
$node_children(S_pre, HOBJECT n_weak) = eps
$weakref_get(S_pre, n_weak) = POBJECT n_object
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HOBJECT n_object) = 2
$call_descriptors_valid(S_pre) /\ $heap_valid(H_pre)
n_private = |S_pre.STORE|
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (POBJECT n_object)
$node_children(S_notice, HCELL n_private) = [HOBJECT n_object]
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1
$heap_owners(H_notice, HOBJECT n_object) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid(H_notice)
S_throw = $stdn_seek(S_notice, 3, 512)[.COMPLETION = NORMAL]
$stdn_stage(S_throw, 3)
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail_throw*
perrorcall_entered.RESUME = perrorcall.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
S_throw.STORE[n_private] = DEFINED (POBJECT n_object)
$weakref_get(S_throw, n_weak) = POBJECT n_object
H_throw = $heap_graph(S_throw)
$heap_owners(H_throw, HCELL n_private) = 1
$heap_owners(H_throw, HOBJECT n_object) = 1
$call_descriptors_valid(S_throw) /\ $heap_valid(H_throw)
S_full = $drive(S_throw, 1000)
S_full.COMPLETION = NORMAL
$stdn_output(S_full.EVENTS) = $ptascii("P;C:1:1:1;E;")
S_full.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
S_full.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S_full, n_weak) = PNULL
$node_children(S_full, HOBJECT n_weak) = eps
H_full = $heap_graph(S_full)
$heap_owners(H_full, HCELL n_private) = 0
$heap_owners(H_full, HOBJECT n_object) = 0
~((HCELL n_private) <- S_full.ALLOCATIONS)
~((HOBJECT n_object) <- S_full.ALLOCATIONS)
$throwable_live(S_full, n_saved)
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid(H_full)
'''.strip().splitlines()

GUARDS = r'''
$named_reference_notice_object(S_pre, POBJECT n_object)
~$named_reference_notice_object(S_pre, POBJECT (|S_pre.OBJECTS|))
S_dead = S_pre[.ALLOCATIONS = $call_remove_owner(S_pre.ALLOCATIONS, HOBJECT n_object)]
~$named_reference_notice_object(S_dead, POBJECT n_object)
S_kind = S_pre[.OBJECTS[n_object] = WEAKREFERENCE eps]
~$named_reference_notice_object(S_kind, POBJECT n_object)
S_missing = S_pre[.OBJECTPROPS = eps]
~$named_reference_notice_object(S_missing, POBJECT n_object)
S_empty = S_pre[.OBJECTPROPS = [pobjectprops_pre[.SLOTS = eps][.MATERIALIZED = false]]]
$named_reference_notice_object(S_empty, POBJECT n_object)
S_unmaterialized = S_pre[.OBJECTPROPS = [pobjectprops_pre[.MATERIALIZED = false]]]
~$named_reference_notice_object(S_unmaterialized, POBJECT n_object)
S_duplicate = S_pre[.OBJECTPROPS = [pobjectprops_pre[.SLOTS = pobjectprops_pre.SLOTS ++ pobjectprops_pre.SLOTS]]]
~$named_reference_notice_object(S_duplicate, POBJECT n_object)
S_table = S_pre[.OBJECTTABLES = [{OBJECT n_object, TABLE 0}]]
~$named_reference_notice_object(S_table, POBJECT n_object)
S_called = S_pre[.DESTRUCTION.CALLED = [n_object]]
~$named_reference_notice_object(S_called, POBJECT n_object)
pinstancestorage_guard = {OBJECT n_object, HANDLE 0, SLOTS pobjectprops_pre.SLOTS, NEXT 0, NOTIFY eps, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, USER false}
S_freeing = S_pre[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage_guard]]
$instance_storage_freeing(S_freeing, n_object)
~$named_reference_notice_object(S_freeing, POBJECT n_object)
S_object_unit = S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HOBJECT n_object]]
~$named_reference_notice_object(S_object_unit, POBJECT n_object)
S_worker = S_pre[.GC.WORKER = (0)]
~$named_reference_notice_object(S_worker, POBJECT n_object)
pgccall_guard = {NONCE 0, CALL {SITE porigin_call, KIND INTRINSIC_SET_ERROR_HANDLER, INDEX 0, SENT eps, NAMED false, OWNER eps, SELECTION eps, LINE 0, PACKS eps}, CALLER eps, ORIGIN eps, CONSTCONTEXT eps, PASS 0, TOTAL 0, PENDING eps, COUNT_SOURCE eps}
S_active = S_pre[.GC.ACTIVE = (pgccall_guard)]
~$named_reference_notice_object(S_active, POBJECT n_object)
pgcplan_guard = {CALL pgccall_guard, GRAPH H_pre, EXCESS eps, TABLES eps, CALLED eps, PROXIES eps, WEAK eps, COUNTED eps, BUFFER eps, CANDIDATES eps, DTORS eps, FREESET eps, SCAN eps, INDEX 0, STEPS eps, DONE eps}
S_plan = S_pre[.GC.PLAN = (pgcplan_guard)]
~$named_reference_notice_object(S_plan, POBJECT n_object)
S_unmarked = S_notice[.REFCELLS = eps]
~$named_reference_notice_operand(S_unmarked, REFERENCE n_private)
S_cell_dead = S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_private)]
~$named_reference_notice_operand(S_cell_dead, REFERENCE n_private)
S_undefined = S_notice[.STORE[n_private] = UNDEFINED]
~$named_reference_notice_operand(S_undefined, REFERENCE n_private)
S_propref = S_notice[.PROPREFS = [{CELL n_private, SOURCES eps}]]
~$named_reference_notice_operand(S_propref, REFERENCE n_private)
S_coercion = S_notice[.REFCOERCIONS = [{CELL n_private, SITE porigin_call, LINE 0, VALUE eps}]]
~$named_reference_notice_operand(S_coercion, REFERENCE n_private)
S_backed = S_notice[.PARAMETERBACKINGS = [{FUNCTION porigin_call, INDEX 0, CELL n_private, LINE 0, VALUE eps}]]
~$named_reference_notice_operand(S_backed, REFERENCE n_private)
S_container = S_notice[.CONTAINERINITS = [{CELL n_private, ARRAY 0, SITE porigin_call, LINE 0}]]
~$named_reference_notice_operand(S_container, REFERENCE n_private)
S_retained = S_notice[.LITERALREFRETAINED = [n_private]]
~$named_reference_notice_operand(S_retained, REFERENCE n_private)
S_debt = S_notice[.LITERALREFDEBTS = [n_private]]
~$named_reference_notice_operand(S_debt, REFERENCE n_private)
S_cell_unit = S_notice[.NATIVEEXCESS = S_notice.NATIVEEXCESS ++ [HCELL n_private]]
~$named_reference_notice_operand(S_cell_unit, REFERENCE n_private)
'''.strip().splitlines()

# Each row changes one local field or name in the actual complete record.
for label, slot in (
    ('declared', '{DECL (INTERNAL_PROPERTY "stdClass" ($ptascii("v"))), NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PINT 5)))}'),
    ('unset', '{DECL eps, NAME ($ptascii("v")), STATE PROP_UNSET}'),
    ('initial', '{DECL eps, NAME ($ptascii("v")), STATE PROP_INITIAL}'),
    ('alias', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (ALIAS n_copy))}'),
    ('indirect', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (INDIRECT 0 eps))}'),
    ('owning', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (POBJECT n_object)))}'),
    ('nul_name', '{DECL eps, NAME [0], STATE (PROP_VALUE (DIRECT (PINT 5)))}'),
    ('wide_name', '{DECL eps, NAME [256], STATE (PROP_VALUE (DIRECT (PINT 5)))}'),
    ('raw', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("x")))))}'),
    ('request', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("x")))))}'),
    ('nul', '{DECL eps, NAME ($ptascii("v")), STATE (PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING [0])))}'),
):
    GUARDS += [f'S_{label} = S_pre[.OBJECTPROPS = [pobjectprops_pre[.SLOTS = [{slot}]]]]',
               f'~$named_reference_notice_object(S_{label}, POBJECT n_object)']

GROUPS = {
    'throw': ('positional-stdclass-last-owner-throw', THROW, []),
    'guards': ('positional-stdclass-shared-mutation-cell-rebind', NORMAL_PREFIX, GUARDS),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS, required=True)
    parser.add_argument('--native-report', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    case, reached, derived = GROUPS[args.group]
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='stdclass-reference-notice-' + args.group + '-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    catalogue = ROOT / 'tests/semantics/stdclass_reference_notice_cases.json'
    row, = [row for row in json.loads(catalogue.read_bytes()) if row['id'] == case]
    source = directory / (case + '.php')
    native_path = args.native_report.resolve() if args.native_report else None
    if native_path:
        native = json.loads(native_path.read_bytes())
        native_row, = [item for item in native['rows'] if item['id'] == case]
        source = Path(native_row['process']['command'][-1])
        assert native['passed'] and native_row['passed']
        assert source.read_bytes() == row['source'].encode()
    elif not args.prepared:
        source.write_bytes(row['source'].encode())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [ROOT / 'spec/semantics/modules.json', runner, Path(__file__), catalogue, source,
        ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
        'frontend/target.php', 'frontend/wire.php', 'tests/semantics/error_handler_run.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]
    if native_path:
        paths.append(native_path)
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
        assert prepared['group'] == args.group
    else:
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks = ['S_initial = ' + initial] + reached + derived
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        prepared = {'revision': revision, 'inputs': before, 'group': args.group,
            'conditions': len(checks), 'reached_conditions': len(reached) + 1,
            'derived_controls': len(derived), 'heap_projections': sum(check.startswith('H_') for check in reached),
            'source_sha256': row['source_sha256'], 'source_file': str(source),
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}
        (directory / 'prepared.json').write_text(json.dumps(prepared, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    assert fixture_sha256 == prepared['fixture_sha256']
    process = recorder.recorded([str(runner), *map(str, modules), str(directory / 'state.watsup')], directory / 'run', 480)
    head_after = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
        and stable and head_after == revision and (directory / 'run.stdout').read_bytes() == b'true\n'
        and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({**prepared, 'inputs_stable': stable,
        'head_stable': head_after == revision, 'module_count': len(modules),
        'mode': 'AL/cache=false/det=true', 'process': process, 'passed': passed,
        'scope': 'Actual source-reached quiet stdClass cell/object ownership and cleanup; derived refusals keep separate credit.'}, indent=2) + '\n')
    print('stdclass', args.group, passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
