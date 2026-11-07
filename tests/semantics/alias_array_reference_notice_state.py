#!/usr/bin/env python3
"""Check repeated scalar aliases and last-owner retirement through array Notices."""
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
syntax pnrefstage = NR_PRE | NR_HANDLER | NR_RETURN | NR_THROW
dec $nr_output(pevent*) : ptbytes
def $nr_output(eps) = eps
def $nr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nr_output(pevent*)
dec $nr_stage(pstate, pnrefstage) : bool
def $nr_stage(S, NR_PRE) = $positional_reference_notice_pending(S)
def $nr_stage(S, NR_HANDLER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;")
def $nr_stage(S, NR_RETURN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = ACQUIRE_CALL :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if $nr_output(S.EVENTS) = $ptascii("P;H;F:17:17;")
def $nr_stage(S, NR_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $nr_stage(S, pnrefstage) = false -- otherwise
dec $nr_seek(pstate, pnrefstage, nat) : pstate
def $nr_seek(S, pnrefstage, n) = S
  -- if $nr_stage(S, pnrefstage) \/ n = 0
def $nr_seek(S, pnrefstage, n) = $nr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pnrefstage, $nabs($(n - 1)))
  -- if ~$nr_stage(S, pnrefstage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nr_seek(S, pnrefstage, n) = $nr_seek($drive_steps(S, 1), pnrefstage, $nabs($(n - 1)))
  -- if ~$nr_stage(S, pnrefstage) /\ $(n > 0)
  -- if $throwable_pending(S.COMPLETION)
def $nr_seek(S, pnrefstage, n) = S -- otherwise
'''

CHECKS = r'''

S_repeat_found = $nr_seek(S_normal_initial, NR_PRE, 1000)
S_repeat = S_repeat_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_repeat)
S_repeat.TODO = (CALL_SEND pcalltarget_repeat phpType7_repeat* n_argument_repeat poperand_repeat* porigin_repeat? z_repeat) :: ptask_repeat*
S_repeat.RESULT = KNOWN (PARRAY n_old)
$lookup(S_repeat.ENV, $ptascii("leaf")) = (n_repeat_leaf)
$lookup(S_repeat.ENV, $ptascii("source")) = (n_repeat_source)
$lookup(S_repeat.ENV, $ptascii("copy")) = (n_copy)
S_repeat.STORE[n_repeat_leaf] = DEFINED (PINT 5)
S_repeat.STORE[n_copy] = DEFINED (PARRAY n_old)
S_repeat.STORE[n_repeat_source] = DEFINED (PARRAY n_old)
S_repeat.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (ALIAS n_repeat_leaf), ENTRY (KSTRING ($ptascii("j"))) (ALIAS n_repeat_leaf)]
$node_children(S_repeat, HARRAY n_old) = [HCELL n_repeat_leaf, HCELL n_repeat_leaf]
$heap_owners($heap_graph(S_repeat), HARRAY n_old) = 3
$heap_owners($heap_graph(S_repeat), HCELL n_repeat_leaf) = 3
$heap_count(HCELL n_repeat_leaf, S_repeat.NATIVEEXCESS) = 0
$call_descriptors_valid(S_repeat) /\ $heap_valid($heap_graph(S_repeat))
n_repeat_private = |S_repeat.STORE|
S_repeat_step = $drive(S_repeat, 1)
S_repeat_step.COMPLETION = BUDGET
S_repeat_notice = S_repeat_step[.COMPLETION = NORMAL]
S_repeat_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_repeat) :: ptask_repeat*
perrorcall_repeat.RESUME = CALL_ARGS pcalltarget_repeat phpType7_repeat* $(n_argument_repeat + 1) (poperand_repeat* ++ [REFERENCE n_repeat_private]) porigin_repeat? z_repeat
S_repeat_notice.STORE[n_repeat_private] = DEFINED (PARRAY n_old)
$node_children(S_repeat_notice, HCELL n_repeat_private) = [HARRAY n_old]
$heap_owners($heap_graph(S_repeat_notice), HCELL n_repeat_private) = 1
$heap_owners($heap_graph(S_repeat_notice), HARRAY n_old) = 3
$heap_owners($heap_graph(S_repeat_notice), HCELL n_repeat_leaf) = 3
S_repeat_notice.RESULT = KNOWN PNULL /\ S_repeat_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_repeat_notice.HELD = S_repeat.HELD
$error_call_valid(S_repeat_notice, perrorcall_repeat)
$call_descriptors_valid(S_repeat_notice) /\ $heap_valid($heap_graph(S_repeat_notice))
S_repeat_handler_found = $nr_seek(S_repeat_notice, NR_HANDLER, 1000)
S_repeat_handler = S_repeat_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_repeat_handler, NR_HANDLER)
S_repeat_handler.GLOBALTABLE = (psymboltable_repeat)
$lookup(psymboltable_repeat.ENV, $ptascii("leaf")) = eps
$lookup(psymboltable_repeat.ENV, $ptascii("source")) = eps
S_repeat_handler.STORE[n_repeat_leaf] = DEFINED (PINT 7)
$heap_owners($heap_graph(S_repeat_handler), HARRAY n_old) = 2
$heap_owners($heap_graph(S_repeat_handler), HCELL n_repeat_leaf) = 2
$heap_count(HCELL n_repeat_leaf, S_repeat_handler.NATIVEEXCESS) = 0
$duplicate_item(S_repeat_handler, n_old, ALIAS n_repeat_leaf) = ALIAS n_repeat_leaf
$call_descriptors_valid(S_repeat_handler) /\ $heap_valid($heap_graph(S_repeat_handler))
S_returned_found = $nr_seek(S_repeat_handler, NR_RETURN, 1000)
S_returned = S_returned_found[.COMPLETION = NORMAL]
$nr_stage(S_returned, NR_RETURN)
S_returned.RESULT = REFERENCE n_repeat_private
S_returned.STORE[n_repeat_private] = DEFINED (PARRAY n_new)
n_new =/= n_old
S_returned.STORE[n_copy] = DEFINED (PARRAY n_old)
S_returned.STORE[n_repeat_leaf] = DEFINED (PINT 17)
S_returned.ARRAYS[n_new].ITEMS = S_repeat.ARRAYS[n_old].ITEMS
S_returned.ARRAYS[n_old].ITEMS = S_repeat.ARRAYS[n_old].ITEMS
$node_children(S_returned, HARRAY n_old) = [HCELL n_repeat_leaf, HCELL n_repeat_leaf]
$node_children(S_returned, HARRAY n_new) = [HCELL n_repeat_leaf, HCELL n_repeat_leaf]
$heap_owners($heap_graph(S_returned), HCELL n_repeat_private) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_old) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new) = 1
$heap_owners($heap_graph(S_returned), HCELL n_repeat_leaf) = 4
$heap_count(HCELL n_repeat_leaf, S_returned.NATIVEEXCESS) = 0
$call_descriptors_valid(S_returned) /\ $heap_valid($heap_graph(S_returned))
S_pre_found = $nr_seek(S_initial, NR_PRE, 1000)
S_pre = S_pre_found[.COMPLETION = NORMAL]
$positional_reference_notice_pending(S_pre)
S_pre.TODO = (CALL_SEND pcalltarget phpType7* n_argument poperand* porigin? z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_array)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
S_pre.STORE[n_leaf] = DEFINED (PINT 5)
S_pre.STORE[n_source] = DEFINED (PARRAY n_array)
S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (ALIAS n_leaf)]
$heap_owners($heap_graph(S_pre), HARRAY n_array) = 2
$heap_owners($heap_graph(S_pre), HCELL n_leaf) = 2
$heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
$propref_at(S_pre.PROPREFS, n_leaf) = eps /\ $reference_coercion_at(S_pre.REFCOERCIONS, n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf)
$call_descriptors_valid(S_pre) /\ $heap_valid($heap_graph(S_pre))
$lookup(S_pre.ENV, $ptascii("saved")) = (n_saved_cell)
S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$lookup(S_pre.ENV, $ptascii("r")) = (n_r)
S_pre.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
n_private = |S_pre.STORE|
n_private =/= n_leaf /\ n_private =/= n_source
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* $(n_argument + 1) (poperand* ++ [REFERENCE n_private]) porigin? z
S_notice.STORE[n_private] = DEFINED (PARRAY n_array)
$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_array]
$node_children(S_notice, HARRAY n_array) = [HCELL n_leaf]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_array) = 2
$heap_owners($heap_graph(S_notice), HCELL n_leaf) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_handler_found = $nr_seek(S_notice, NR_HANDLER, 1000)
S_handler = S_handler_found[.COMPLETION = NORMAL]
$nr_stage(S_handler, NR_HANDLER)
S_handler.GLOBALTABLE = (psymboltable)
$lookup(psymboltable.ENV, $ptascii("leaf")) = eps
$lookup(psymboltable.ENV, $ptascii("source")) = eps
S_handler.STORE[n_private] = DEFINED (PARRAY n_array)
S_handler.STORE[n_leaf] = DEFINED (PINT 5)
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$heap_owners($heap_graph(S_handler), HARRAY n_array) = 1
$heap_owners($heap_graph(S_handler), HCELL n_leaf) = 1
$call_descriptors_valid(S_handler) /\ $heap_valid($heap_graph(S_handler))
S_throw_found = $nr_seek(S_handler, NR_THROW, 1000)
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
perrorcall_entered.RESUME = perrorcall.RESUME
$error_entered_call_valid(S_throw, perrorcall_entered)
$throwable_live(S_throw, n_saved)
$heap_owners($heap_graph(S_throw), HCELL n_private) = 1
$heap_owners($heap_graph(S_throw), HARRAY n_array) = 1
$heap_owners($heap_graph(S_throw), HCELL n_leaf) = 1
S_cancel_step = $drive(S_throw, 1)
S_cancel_step.COMPLETION = BUDGET
S_cancel = S_cancel_step[.COMPLETION = NORMAL]
S_cancel.TODO = (THROW_SEARCH n_saved) :: ptask_tail*
S_cancel.ERRORHANDLER = S_pre.ERRORHANDLER
S_cancel.RESULT = KNOWN PNULL /\ S_cancel.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_cancel), HCELL n_private) = 0
$heap_owners($heap_graph(S_cancel), HARRAY n_array) = 0
$heap_owners($heap_graph(S_cancel), HCELL n_leaf) = 0
~((HCELL n_private) <- S_cancel.ALLOCATIONS)
~((HARRAY n_array) <- S_cancel.ALLOCATIONS)
~((HCELL n_leaf) <- S_cancel.ALLOCATIONS)
~$call_reference_operand_valid(S_cancel, REFERENCE n_leaf)
$heap_valid($heap_graph(S_cancel)) /\ $call_descriptors_valid(S_cancel)
$throwable_live(S_cancel, n_saved)
S_cancel.STORE[n_r] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("old-target")))
$nr_output(S_cancel.EVENTS) = $ptascii("P;H;")
'''.strip().splitlines()

PURE = r'''

$named_reference_notice_entries(S_notice, S_notice.ARRAYS[n_array].ITEMS)
$named_reference_notice_entries(S_notice, [ENTRY (KINT 0) (DIRECT PNULL), ENTRY (KINT 1) (ALIAS n_leaf), ENTRY (KINT 2) (DIRECT (PSTRING_CARRIER INTERNED_STRING ($ptascii("mixed"))))])
$target_function(S_notice, pcalltarget) = (pfunction)
S_null = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED PNULL)]
$named_reference_notice_entries(S_null, S_null.ARRAYS[n_array].ITEMS)
S_bool = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PBOOL true))]
$named_reference_notice_entries(S_bool, S_bool.ARRAYS[n_array].ITEMS)
S_float = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PFLOAT 0))]
$named_reference_notice_entries(S_float, S_float.ARRAYS[n_array].ITEMS)
S_string = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PSTRING_CARRIER INTERNED_STRING eps))]
$named_reference_notice_entries(S_string, S_string.ARRAYS[n_array].ITEMS)
S_cycle = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PARRAY n_array))]
~$named_reference_notice_entries(S_cycle, S_cycle.ARRAYS[n_array].ITEMS)
~$named_reference_notice_array(S_cycle, PARRAY n_array)
S_object = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (POBJECT n_saved))]
~$named_reference_notice_entries(S_object, S_object.ARRAYS[n_array].ITEMS)
S_undefined = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, UNDEFINED)]
~$named_reference_notice_entries(S_undefined, S_undefined.ARRAYS[n_array].ITEMS)
S_raw = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PSTRING ($ptascii("x"))))]
~$named_reference_notice_entries(S_raw, S_raw.ARRAYS[n_array].ITEMS)
S_request = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("x"))))]
~$named_reference_notice_entries(S_request, S_request.ARRAYS[n_array].ITEMS)
S_nul = S_notice[.STORE = $set_cell(S_notice.STORE, n_leaf, DEFINED (PSTRING_CARRIER INTERNED_STRING ([0])))]
~$named_reference_notice_entries(S_nul, S_nul.ARRAYS[n_array].ITEMS)
S_unmarked = S_notice[.REFCELLS = eps]
~$named_reference_notice_entries(S_unmarked, S_unmarked.ARRAYS[n_array].ITEMS)
S_retired = S_notice[.ALLOCATIONS = $call_remove_owner(S_notice.ALLOCATIONS, HCELL n_leaf)]
~$named_reference_notice_entries(S_retired, S_retired.ARRAYS[n_array].ITEMS)
S_backed = S_notice[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]]
~$named_reference_notice_entries(S_backed, S_backed.ARRAYS[n_array].ITEMS)
S_container = S_notice[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_array, SITE pfunction.ORIGIN, LINE 0}]]
~$named_reference_notice_entries(S_container, S_container.ARRAYS[n_array].ITEMS)
S_propref = S_notice[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_entries(S_propref, S_propref.ARRAYS[n_array].ITEMS)
S_coercion = S_notice[.REFCOERCIONS = [{CELL n_leaf, SITE pfunction.ORIGIN, LINE 0, VALUE eps}]]
~$named_reference_notice_entries(S_coercion, S_coercion.ARRAYS[n_array].ITEMS)
S_retained = S_notice[.LITERALREFRETAINED = [n_leaf]]
~$named_reference_notice_entries(S_retained, S_retained.ARRAYS[n_array].ITEMS)
S_debt = S_notice[.LITERALREFDEBTS = [n_leaf]]
~$named_reference_notice_entries(S_debt, S_debt.ARRAYS[n_array].ITEMS)
S_unit = S_notice[.NATIVEEXCESS = S_notice.NATIVEEXCESS ++ [HCELL n_leaf]]
~$named_reference_notice_entries(S_unit, S_unit.ARRAYS[n_array].ITEMS)
$named_reference_notice_entries(S_unit, [ENTRY (KINT 0) (DIRECT (PINT 9))])
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--prepared', type=Path)
    args = parser.parse_args()
    directory = args.prepared or args.output or Path(tempfile.mkdtemp(
        prefix='alias-array-reference-notice-state-', dir=ROOT / '.tools'))
    directory.mkdir(parents=True, exist_ok=True)
    print(directory, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), ROOT / 'tests/semantics/alias_array_reference_notice_cases.json',
                       ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / name for name in ('tests/semantics/profile.json', 'frontend/worker.php',
                                     'frontend/target.php', 'frontend/wire.php')]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.prepared:
        prepared = json.loads((directory / 'prepared.json').read_bytes())
        assert prepared['inputs'] == before and prepared['revision'] == revision
    else:
        rows = json.loads((ROOT / 'tests/semantics/alias_array_reference_notice_cases.json').read_bytes())
        assert {row['id'] for row in rows} == {'positional-repeated-alias-array-cow', 'positional-alias-array-throw'}
        initials, sources = {}, {}
        frontend = adapter = None
        try:
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            for row in rows:
                source = directory / (row['id'] + '.php')
                source.write_bytes(row['source'].encode())
                assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
                sources[row['id']] = row['source_sha256']
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                initials[row['id']] = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
                    base64.b64encode(os.fsencode(source)).decode()) + ')'
        finally:
            try:
                if frontend:
                    frontend.close()
            finally:
                if adapter:
                    adapter.close()
        checks = ['S_normal_initial = ' + initials['positional-repeated-alias-array-cow'],
                  'S_initial = ' + initials['positional-alias-array-throw']] + CHECKS + PURE
        (directory / 'state.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                                               + ''.join('  -- if ' + check + '\n' for check in checks))
        (directory / 'prepared.json').write_text(json.dumps({'revision': revision, 'inputs': before,
            'conditions': len(checks), 'reached_conditions': len(CHECKS) + 2, 'derived_controls': len(PURE), 'sources': sources,
            'fixture_sha256': hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()}, indent=2) + '\n')
    if args.prepare_only:
        return True
    fixture_sha256 = hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    prepared = json.loads((directory / 'prepared.json').read_bytes())
    assert fixture_sha256 == prepared['fixture_sha256']
    command = [str(runner), *map(str, modules), str(directory / 'state.watsup')]
    process = recorder.recorded(command, directory / 'run', 480)
    stable = before == fingerprints() and fixture_sha256 == hashlib.sha256((directory / 'state.watsup').read_bytes()).hexdigest()
    passed = (process['exit'] == 0 and not process['timeout'] and stable
              and (directory / 'run.stdout').read_bytes() == b'true\n'
              and not (directory / 'run.stderr').read_bytes())
    (directory / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before,
        'inputs_stable': stable, 'module_count': len(modules), 'mode': 'AL/cache=false/det=true',
        'conditions': prepared['conditions'], 'reached_conditions': prepared['reached_conditions'], 'derived_controls': prepared['derived_controls'], 'fixture_sha256': fixture_sha256,
        'process': process, 'passed': passed,
        'scope': 'Actual repeated-ALIA physical3-to2-to4, shared wrapper copying and scalar mutation, plus last-owner private-cell/table/leaf cancellation. Derived quiet-leaf and cycle controls have zero native credit; no GC82 header/callback proof or generic tail renewal.'}, indent=2) + '\n')
    print('repeated alias ownership/cancellation', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
