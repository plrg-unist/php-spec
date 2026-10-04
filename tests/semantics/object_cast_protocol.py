#!/usr/bin/env python3
"""Source-derived stdClass table, cast operand and foreach callback controls."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('object_casts')
b64 = lambda value: base64.b64encode(value).decode()

HELPERS = r'''
dec $object_control_ready(pstate, nat) : bool
def $object_control_ready(S, 0) = true
  -- if S.TODO = (CLONE_RESULT porigin z) :: ptask_tail*
def $object_control_ready(S, 1) = true
  -- if S.TODO = (CAST_RESULT CASTARRAY z) :: ptask_tail*
def $object_control_ready(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_CAST_RESULT pobjectcast
def $object_control_ready(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_CAST_RESULT pobjectcast
def $object_control_ready(S, 4) = true
  -- if S.TODO = (OBJECT_CAST_RESULT pobjectcast) :: ptask_tail*
def $object_control_ready(S, 5) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach
def $object_control_ready(S, 6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach
def $object_control_ready(S, 7) = true
  -- if S.TODO = (OBJECT_FOREACH_KEY pobjectforeach) :: ptask_tail*
def $object_control_ready(S, 8) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach
def $object_control_ready(S, n) = false -- otherwise
dec $object_control_seek(pstate, nat, nat) : pstate
def $object_control_seek(S, n_stage, n) = S -- if $object_control_ready(S, n_stage)
def $object_control_seek(S, n_stage, n) = S
  -- if ~$object_control_ready(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_control_seek(S, n_stage, 0) = S
  -- if ~$object_control_ready(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $object_control_seek(S, n_stage, n) = $object_control_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$object_control_ready(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''

CHECKS = {
    'table': [
        'S_initial = $php_run($object_control_table_program(), 0, "@TABLE@")',
        'S_shared = $object_control_seek(S_initial, 0, 256)',
        '$object_control_ready(S_shared, 0)',
        '$call_descriptors_valid(S_shared)',
        '$heap_valid($heap_graph(S_shared))',
        '$lookup(S_shared.ENV, $ptascii("a")) = (n_array_cell)',
        'S_shared.STORE[n_array_cell] = DEFINED (PARRAY n_table)',
        '$lookup(S_shared.ENV, $ptascii("o")) = (n_object_cell)',
        'S_shared.STORE[n_object_cell] = DEFINED (POBJECT n_object)',
        'S_shared.OBJECTTABLES = [{OBJECT n_object, TABLE n_table}]',
        'S_shared.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING $ptascii("x")) (ALIAS n_ref)]',
        '$heap_owners($heap_graph(S_shared), HCELL n_ref) = 1',
        '$heap_owners($heap_graph(S_shared), HARRAY n_table) = 2',
        '(HEDGE (HOBJECT n_object) (HARRAY n_table)) <- $heap_graph(S_shared).EDGES',
        '~((HEDGE (HOBJECT n_object) (HCELL n_ref)) <- $heap_graph(S_shared).EDGES)',
        '~$object_tables_valid(S_shared[.OBJECTTABLES = S_shared.OBJECTTABLES ++ S_shared.OBJECTTABLES])',
        '~$heap_valid($heap_graph(S_shared[.ALLOCATIONS = $call_remove_owner(S_shared.ALLOCATIONS, HARRAY n_table)]))',
        'S_cloned = $drive_steps(S_shared[.COMPLETION = NORMAL], 1)',
        'S_cloned.RESULT = KNOWN (POBJECT n_clone)',
        '$object_table_at(S_cloned.OBJECTTABLES, n_clone) = (n_table)',
        '$heap_owners($heap_graph(S_cloned), HCELL n_ref) = 1',
        '$heap_owners($heap_graph(S_cloned), HARRAY n_table) = 3',
        '$call_descriptors_valid(S_cloned)',
        '$heap_valid($heap_graph(S_cloned))',
        'S_written = $object_control_seek(S_cloned, 1, 256)',
        '$object_control_ready(S_written, 1)',
        '$object_table_at(S_written.OBJECTTABLES, n_object) = (n_separate)',
        'n_separate =/= n_table',
        'S_written.ARRAYS[n_separate].ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 2))]',
        '$object_table_at(S_written.OBJECTTABLES, n_clone) = (n_table)',
        'S_written.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING $ptascii("x")) (ALIAS n_ref)]',
        '$heap_owners($heap_graph(S_written), HCELL n_ref) = 1',
        '$call_descriptors_valid(S_written)',
        '$heap_valid($heap_graph(S_written))',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.OBJECTTABLES = eps',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '~((HARRAY n_table) <- S_done.ALLOCATIONS)',
        '~((HCELL n_ref) <- S_done.ALLOCATIONS)',
    ],
    'nan': [
        'S_initial = $php_run($object_control_nan_program(), 0, "@NAN@")',
        'S_pending = $object_control_seek(S_initial, 2, 256)',
        '$object_control_ready(S_pending, 2)',
        '$call_descriptors_valid(S_pending)',
        '$heap_valid($heap_graph(S_pending))',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = OBJECT_CAST_RESULT pobjectcast',
        'S_pending.OBJECTCAST = (pobjectcast)',
        '~pobjectcast.REFERENCED',
        'pobjectcast.CELL = (n_input)',
        'pobjectcast.INPUT = VARIABLE ($ptascii("x")) pobjectcast.LINE',
        '$task_nodes(perrorcall.RESUME) = [HOBJECT pobjectcast.OBJECT]',
        '$heap_owners($heap_graph(S_pending), HOBJECT pobjectcast.OBJECT) = 1',
        '$objectprops_at(S_pending.OBJECTPROPS, pobjectcast.OBJECT) = (eps)',
        '~$call_task_valid(S_pending, OBJECT_CAST_RESULT pobjectcast[.LINE = $(pobjectcast.LINE + 1)])',
        '~$call_task_valid(S_pending, OBJECT_CAST_RESULT pobjectcast[.INPUT = KNOWN (PFLOAT 9221120237041090560)])',
        '~$call_descriptors_valid(S_pending[.OBJECTCAST = eps])',
        '~$heap_valid($heap_graph(S_pending[.ALLOCATIONS = $call_remove_owner(S_pending.ALLOCATIONS, HOBJECT pobjectcast.OBJECT)]))',
        'S_entered = $object_control_seek(S_pending, 3, 256)',
        '$object_control_ready(S_entered, 3)',
        '$call_descriptors_valid(S_entered)',
        '$heap_valid($heap_graph(S_entered))',
        'S_entered.OBJECTCAST = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.OBJECTCAST = (pobjectcast)',
        '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.OBJECTCAST = eps] :: pframe_tail*])',
        'S_result = $object_control_seek(S_entered, 4, 256)',
        '$object_control_ready(S_result, 4)',
        '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        '$lookup(S_result.ENV, $ptascii("x")) = eps',
        '$object_cast_after_item(S_result, pobjectcast) = (UNINITIALIZED)',
        '$drive_steps(S_result[.COMPLETION = NORMAL], 0) = S_result[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_result[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.OBJECTCAST = eps',
        'S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$lookup(S_done.ENV, $ptascii("a")) = (n_raw_cell)',
        'S_done.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)',
        '$lookup(S_done.ENV, $ptascii("n")) = (n_null_cell)',
        'S_done.STORE[n_null_cell] = DEFINED (PARRAY n_null)',
        'S_done.ARRAYS[n_raw].ITEMS = [ENTRY (KSTRING $ptascii("scalar")) UNINITIALIZED]',
        '$entry_read_value(S_done, UNINITIALIZED) = PUNDEFINED',
        '$entry_read_value(S_done, UNINITIALIZED) =/= PNULL',
        '$value_order(S_done, PARRAY n_raw, PARRAY n_null, eps) = ORDER 0',
        '$value_order(S_done, PARRAY n_null, PARRAY n_raw, eps) = ORDER 1',
        '$value_order_effect(S_done, PARRAY n_raw, PARRAY n_null, eps, 3) = (S_done, ORDER 0)',
        '$value_order_effect(S_done, PARRAY n_null, PARRAY n_raw, eps, 3) = (S_done, ORDER 1)',
        '$lookup(S_done.ENV, $ptascii("p")) = (n_plain_cell)',
        'S_done.STORE[n_plain_cell] = DEFINED (POBJECT n_plain)',
        '$objectprops_at(S_done.OBJECTPROPS, pobjectcast.OBJECT) = (ppropertyslot_raw*)',
        '$objectprops_at(S_done.OBJECTPROPS, n_plain) = (ppropertyslot_null*)',
        '$property_hash_order(S_done, ppropertyslot_raw*, ppropertyslot_null*, eps) = ORDER 0',
        '$property_hash_order(S_done, ppropertyslot_null*, ppropertyslot_raw*, eps) = ORDER 1',
        '$property_hash_order_effect(S_done, ppropertyslot_raw*, ppropertyslot_null*, eps, 3) = (S_done, ORDER 0)',
        '$property_hash_order_effect(S_done, ppropertyslot_null*, ppropertyslot_raw*, eps, 3) = (S_done, ORDER 1)',
        '$lookup(S_done.ENV, $ptascii("hit")) = (n_hit)',
        'S_done.STORE[n_hit] = DEFINED (PBOOL true)',
        '$lookup(S_done.ENV, $ptascii("again")) = (n_again_cell)',
        'S_done.STORE[n_again_cell] = DEFINED (POBJECT n_again)',
        '$stdclass_raw_undefined(S_done, POBJECT n_again, $ptascii("scalar"))',
        '$coerce_number(PUNDEFINED) = BADNUMBER',
    ],
    'nul': [
        'S_initial = $php_run($object_control_nul_program(), 0, "@NUL@")',
        'S_pending = $object_control_seek(S_initial, 5, 1000)',
        '$object_control_ready(S_pending, 5)',
        '$call_descriptors_valid(S_pending)',
        '$heap_valid($heap_graph(S_pending))',
        'S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach',
        'pobjectforeach.REF',
        '$task_nodes(perrorcall.RESUME) = [HOBJECT pobjectforeach.OBJECT]',
        '$object_foreach_bucket(S_pending, pobjectforeach) = (DIRECT (PINT 2))',
        '$lookup(S_pending.ENV, $ptascii("copy")) = (n_clone_cell)',
        'S_pending.STORE[n_clone_cell] = DEFINED (POBJECT n_clone)',
        '$object_table_at(S_pending.OBJECTTABLES, n_clone) = (pobjectforeach.TABLE)',
        '$iterator_lookup(S_pending.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION true pobjectforeach.TABLE pobjectforeach.SERIAL)',
        '$lookup(S_pending.ENV, $ptascii("source")) = (n_source_cell)',
        'S_pending.STORE[n_source_cell] = DEFINED (PARRAY n_source_table)',
        'n_source_table =/= pobjectforeach.TABLE',
        '$position_lookup(S_pending.ARRAYS[n_source_table].POSITIONS, KSTRING pobjectforeach.KEY) = (pobjectforeach.SERIAL)',
        '$entry_lookup(S_pending.ARRAYS[n_source_table].ITEMS, KSTRING pobjectforeach.KEY) = (DIRECT (PINT 2))',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.TABLE = n_source_table])',
        '~$call_descriptors_valid(S_pending[.ITERATORS = $iterator_remove(S_pending.ITERATORS, pobjectforeach.ITERATOR)])',
        '~$call_task_valid(S_pending[.ITERATORS = $iterator_set(S_pending.ITERATORS, OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION true n_source_table pobjectforeach.SERIAL)], OBJECT_FOREACH_KEY pobjectforeach)',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.LINE = $(pobjectforeach.LINE + 1)])',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.KEY = $ptascii("other")])',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.POSITION = $(pobjectforeach.POSITION + 1)])',
        'pobjectforeach.SERIAL = 1',
        'S_pending.ARRAYS[pobjectforeach.TABLE].SERIAL = 2',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.SERIAL = 0])',
        '~$call_task_valid(S_pending, OBJECT_FOREACH_KEY pobjectforeach[.REF = false])',
        '~$heap_valid($heap_graph(S_pending[.ALLOCATIONS = $call_remove_owner(S_pending.ALLOCATIONS, HOBJECT pobjectforeach.OBJECT)]))',
        '$origin_node(S_pending.SOURCES, pobjectforeach.SITE) = (NStmtForeach expression phpType5 (BOOLEAN b_ref) expression_value phpType23 (BOOLEAN false) metadata)',
        '$object_foreach_notice(NStmtForeach expression ABSENT (BOOLEAN b_ref) expression_value phpType23 (BOOLEAN false) metadata, pobjectforeach.KEY) = eps',
        '$object_member_name([0,65,0,110]) = (eps, $ptascii("n"))',
        '$object_member_name([0,120]) = ($object_member_warning("Illegal member variable name"), ([0,120]))',
        'S_entered = $object_control_seek(S_pending, 6, 256)',
        '$object_control_ready(S_entered, 6)',
        '$call_descriptors_valid(S_entered)',
        '$heap_valid($heap_graph(S_entered))',
        '$iterator_lookup(S_entered.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION true pobjectforeach.TABLE pobjectforeach.SERIAL)',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = OBJECT_FOREACH_KEY pobjectforeach',
        '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_entered[.RESUME = OBJECT_FOREACH_KEY pobjectforeach[.TABLE = n_source_table]]) :: ptask_saved*] :: pframe_tail*])',
        'S_result = $object_control_seek(S_entered, 7, 256)',
        '$object_control_ready(S_result, 7)',
        '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        '$object_foreach_bucket(S_result, pobjectforeach) = (DIRECT (PINT 2))',
        '$iterator_lookup(S_result.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION true pobjectforeach.TABLE pobjectforeach.SERIAL)',
        '$drive_steps(S_result[.COMPLETION = NORMAL], 0) = S_result[.COMPLETION = BUDGET]',
        'S_promote = $drive_steps(S_result[.COMPLETION = NORMAL], 1)',
        '$iterator_lookup(S_promote.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION true)',
        '$entry_lookup(S_promote.ARRAYS[pobjectforeach.TABLE].ITEMS, KSTRING pobjectforeach.KEY) = (ALIAS n_promoted)',
        '$objectprops_at(S_promote.OBJECTPROPS, pobjectforeach.OBJECT) = (ppropertyslot_object*)',
        '$objectprops_at(S_promote.OBJECTPROPS, n_clone) = (ppropertyslot_clone*)',
        '$property_slot_at(ppropertyslot_object*, pobjectforeach.KEY) = (ppropertyslot_value)',
        '$property_slot_at(ppropertyslot_clone*, pobjectforeach.KEY) = (ppropertyslot_value)',
        'ppropertyslot_value.STATE = PROP_VALUE (ALIAS n_promoted)',
        '$call_descriptors_valid(S_promote)',
        '$heap_valid($heap_graph(S_promote))',
        'S_done = $drive_steps(S_promote[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.ITERATORS = eps',
        'S_done.FRAMES = eps',
        'S_done.STORE[n_promoted] = DEFINED (PINT 3)',
        '$heap_owners($heap_graph(S_done), HCELL n_promoted) = 1',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ],
    'throw': [
        'S_initial = $php_run($object_control_throw_program(), 0, "@THROW@")',
        'S_entered = $object_control_seek(S_initial, 6, 256)',
        '$object_control_ready(S_entered, 6)',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
        'perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach',
        '$iterator_lookup(S_entered.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION false pobjectforeach.TABLE pobjectforeach.SERIAL)',
        'pobjectforeach.ITERATOR <- $error_saved_iterators(S_entered.FRAMES)',
        '$error_release_iterators(S_entered).ITERATORS = S_entered.ITERATORS',
        '$call_descriptors_valid(S_entered)',
        '$heap_valid($heap_graph(S_entered))',
        'S_raise = $object_control_seek(S_entered, 8, 256)',
        '$object_control_ready(S_raise, 8)',
        'S_raise.TODO = [THROW_SEARCH n_exception]',
        '$iterator_lookup(S_raise.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION false pobjectforeach.TABLE pobjectforeach.SERIAL)',
        '$error_release_iterators(S_raise).ITERATORS = S_raise.ITERATORS',
        '$call_descriptors_valid(S_raise)',
        '$heap_valid($heap_graph(S_raise))',
        '$drive_steps(S_raise[.COMPLETION = NORMAL], 0) = S_raise[.COMPLETION = BUDGET]',
        'S_restore = $drive_steps(S_raise[.COMPLETION = NORMAL], 1)',
        'S_restore.FRAMES = eps',
        'S_restore.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
        '$iterator_lookup(S_restore.ITERATORS, pobjectforeach.ITERATOR) = (OBJECTKEYITER pobjectforeach.ITERATOR pobjectforeach.OBJECT pobjectforeach.POSITION false pobjectforeach.TABLE pobjectforeach.SERIAL)',
        '$call_descriptors_valid(S_restore)',
        '$heap_valid($heap_graph(S_restore))',
        'S_discard = $drive_steps(S_restore[.COMPLETION = NORMAL], 1)',
        '$iterator_lookup(S_discard.ITERATORS, pobjectforeach.ITERATOR) = eps',
        'S_done = $drive_steps(S_discard[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.ITERATORS = eps',
        'S_done.FRAMES = eps',
        'S_done.ERRORHANDLER.CALLBACK = eps',
        'S_done.EVENTS = [OUTPUT $ptascii("stop"), OUTPUT $ptascii("|"), OUTPUT $ptascii("END")]',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ],
}

def render(fixtures, paths, name):
    setup = ('dec $object_control_' + name + '_program() : program\n'
             + 'def $object_control_' + name + '_program() = ' + fixtures[name] + '\n')
    checks = [check.replace('@' + name.upper() + '@', b64(bytes(paths[name]))) for check in CHECKS[name]]
    return (setup + HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', choices=CHECKS)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    selected = (args.group,) if args.group else tuple(CHECKS)
    out = Path(tempfile.mkdtemp(prefix='object-cast-protocol-', dir=R / '.tools')); print(out, flush=True)
    paths = {name: SOURCES / ('control-' + name + '.php') for name in selected}
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': b64(path.read_bytes())}) for name, path in paths.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'adapter')
    try:
        fixtures = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture']
                    for name, row in parsed.items()}
    finally:
        adapter.close()
    for name in selected:
        (out / (name + '.watsup')).write_text(render(fixtures, paths, name))
    report = {'selection': selected, 'conditions': {name: len(CHECKS[name]) for name in selected}, 'rows': [],
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    if args.prepare_only:
        report['execution'] = 'none'
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        return True
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', runner, Path(__file__),
               R / 'tests/semantics/error_handler_run.py', R / 'tests/semantics/profile.json',
               *paths.values(), *[out / (name + '.watsup') for name in selected]]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    for name in selected:
        process = recorded([str(runner), *map(str, modules), str(out / (name + '.watsup'))], out / name, 90)
        passed = (process['exit'] == 0 and not process['timeout'] and (out / (name + '.stdout')).read_bytes() == b'true\n'
                  and not (out / (name + '.stderr')).read_bytes())
        report['rows'].append({'id': name, 'conditions': len(CHECKS[name]), 'process': process, 'passed': passed})
        print(name, passed, flush=True)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report.update(revision=revision, inputs=before)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return all(row['passed'] for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
