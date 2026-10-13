#!/usr/bin/env python3
"""Independent reached-state checks for old cells and surviving owners."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import sys
import tempfile

import incdec_restoration_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CASES = ('review-old-cell-caller-rebind-throw', 'review-surviving-wrapper-pre',
         'review-destructor-new-object-write', 'review-array-destructor-write')
ISSET_HELPERS = r'''
def $restore_frontier(S, 5) = true
  -- if S.TODO = (KEY_READ_GLOBAL (KNOWN (PSTRING ptbytes)) z (KEY_TEST false)) :: ptask_tail*
  -- if $update_released_array_name($global_table_view(S), ptbytes)
'''


def isset_conditions(program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_restore = $restore_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]',
        'S_restore.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_tail*',
        '$call_descriptors_valid(S_restore)',
        '$update_restore_capture(S_restore, pupdatewarning) = (pupdaterestore)',
        'pupdaterestore.VALUE = PARRAY n_array',
        'pupdatewarning.INPUT = PBOOL true',
        'pupdatewarning.POINTER = UPDATE_CELL pupdaterestore.CELL',
        'pupdatewarning.PENDING = eps',
        'S_record = $drive_steps(S_restore, 1)[.COMPLETION = NORMAL]',
        'S_record.TODO = (UPDATE_WARNING_RELEASE pupdaterestore) :: ptask_tail*',
        'S_released = $drive_steps(S_record, 1)[.COMPLETION = NORMAL]',
        '$destructor_operation_for(S_released) = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore',
        'S_key = $restore_seek(S_released, 5, 3000)[.COMPLETION = NORMAL]',
        '$restore_frontier(S_key, 5)', '$call_descriptors_valid(S_key)',
        'S_key.TODO = (KEY_READ_GLOBAL (KNOWN (PSTRING ptbytes)) z (KEY_TEST false)) :: ptask_key*',
        'ptbytes = $ptascii("x")', 'S_key.ORIGIN = (porigin)',
        '$global_read_source(S_key, {SITE porigin, NAME ptbytes, LINE z})',
        '$key_context_tasks(S_key, S_key.TODO, porigin, KEY_TEST false)',
        '~$key_context_tasks(S_key, S_key.TODO, porigin, KEY_IS)',
        'S_global = $global_table_view(S_key)',
        '$lookup(S_global.ENV, ptbytes) = (pupdaterestore.CELL)',
        'S_key.STORE[pupdaterestore.CELL] = DEFINED (PARRAY n_array)',
        '~((HARRAY n_array) <- S_key.ALLOCATIONS)',
        '$update_released_cell(S_key, pupdaterestore.CELL)',
        '$node_children(S_key, HCELL pupdaterestore.CELL) = eps',
        '$heap_owners($heap_prune($heap_graph(S_key)), HARRAY n_array) = 0',
        '$update_released_key_isset(S_key, KNOWN (PSTRING ptbytes), ptbytes, z, KEY_TEST false)',
        '~$update_released_key_isset(S_key, KNOWN (PSTRING ptbytes), ptbytes, z, KEY_IS)',
        '~$update_released_key_isset(S_key, KNOWN (PSTRING ptbytes), ptbytes, z, KEY_TEST true)',
        '~$update_released_key_isset(S_key, KNOWN (PSTRING ptbytes), ptbytes, $(z + 1), KEY_TEST false)',
        '~$update_released_key_isset(S_key[.ORIGIN = eps], KNOWN (PSTRING ptbytes), ptbytes, z, KEY_TEST false)',
        '~$update_released_key_isset(S_key[.CODE = eps], KNOWN (PSTRING ptbytes), ptbytes, z, KEY_TEST false)',
        '$quiet_name(S_global, ptbytes).COMPLETION = UNSUPPORTED "increment/decrement released array payload read"',
        'PhpStep: S_key ~> S_exist', 'S_exist.RESULT = KNOWN (PBOOL true)',
        'S_exist.TODO = ptask_key*', 'S_exist.STORE = S_key.STORE',
        'S_exist.EVENTS = S_key.EVENTS', 'S_exist.ALLOCATIONS = S_key.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_exist)), HARRAY n_array) = 0',
        '$heap_valid($heap_graph(S_exist))',
        'S_budget = $drive_steps(S_key, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.RESULT = S_exist.RESULT', 'S_budget.STORE = S_exist.STORE',
        'S_done = $drive_steps(S_exist, 3000)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.STORE[pupdaterestore.CELL] = DEFINED (PBOOL true)',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 3000) = S_done',
    ]


def conditions(name, program, path, stdout):
    if name == 'review-array-destructor-write':
        return isset_conditions(program, path, stdout)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $update_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_entry) = (pupdatewarning_entry)',
        '$call_descriptors_valid(S_entry)',
        'S_restore = $restore_seek(S_entry, 0, 3000)[.COMPLETION = NORMAL]',
        'S_restore.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_tail*',
        '$call_descriptors_valid(S_restore)',
        '$update_restore_capture(S_restore, pupdatewarning) = (pupdaterestore)',
        'pupdatewarning.SITE = pupdatewarning_entry.SITE',
        'pupdatewarning.INPUT = pupdatewarning_entry.INPUT',
        'pupdatewarning.POINTER = pupdatewarning_entry.POINTER',
        'pupdaterestore.VALUE = POBJECT n_old_object',
        '$task_nodes(UPDATE_WARNING_RELEASE pupdaterestore) = $instance_roots(pupdatewarning.PENDING)',
        '$task_nodes(UPDATE_WARNING_COMMIT pupdaterestore) = eps',
        'PhpStep: S_restore ~> S_record',
        'S_record.TODO = (UPDATE_WARNING_RELEASE pupdaterestore) :: ptask_tail*',
        'S_record.STORE = S_restore.STORE', 'S_record.EVENTS = S_restore.EVENTS',
        '$drive_steps(S_record, 0) = S_record[.COMPLETION = BUDGET]',
        'S_released = $drive_steps(S_record, 1)[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
        '$destructor_operation_for(S_released) = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore',
        'pdestructionoperation.PENDING = pupdatewarning.PENDING',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = $instance_roots(pupdatewarning.PENDING)',
        '$update_restore_commit_count(S_released.TODO, pupdaterestore) = 1',
        '$call_task_valid(S_released, UPDATE_WARNING_COMMIT pupdaterestore)',
        '$node_children(S_released, HCELL pupdaterestore.CELL) = eps',
        'S_duplicate = S_released[.TODO = (UPDATE_WARNING_COMMIT pupdaterestore) :: S_released.TODO]',
        '$update_restore_commit_count(S_duplicate.TODO, pupdaterestore) = 2',
        '~$eager_operation_source_guard(S_duplicate, pdestructionoperation)',
        '~$update_released_cell(S_duplicate, pupdaterestore.CELL)',
        '~$call_descriptors_valid(S_duplicate)',
        '$scope_codes_valid(S_duplicate, S_duplicate.CODE)',
        'S_rejected = $drive(S_duplicate, 1)',
        'S_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_finish = $restore_seek(S_released, 2, 3000)[.COMPLETION = NORMAL]',
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_finish) :: (UPDATE_WARNING_COMMIT pupdaterestore) :: ptask_tail*',
        '$call_descriptors_valid(S_finish)',
        '$update_restore_record_valid(S_finish, pupdaterestore)',
        '$destructor_operation_valid(S_finish, pdestructionoperation_finish)',
    ]
    if name == 'review-destructor-new-object-write':
        return checks + [
            'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
            'S_finish.STORE[pupdaterestore.CELL] = DEFINED (POBJECT n_new_object)',
            'n_new_object =/= n_old_object',
            '(HOBJECT n_new_object) <- S_finish.ALLOCATIONS',
            '~(n_new_object <- S_finish.DESTRUCTION.CALLED)',
            '~$update_released_cell(S_finish, pupdaterestore.CELL)',
            '$node_children(S_finish, HCELL pupdaterestore.CELL) = [HOBJECT n_new_object]',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_new_object) = 1',
            '~$update_restore_payload_valid(S_finish, pupdaterestore)',
            'PhpStep: S_finish ~> S_failure',
            'S_failure.COMPLETION = UNSUPPORTED "increment/decrement destructor changed restored target ownership"',
            'S_failure.STORE = S_finish.STORE', 'S_failure.EVENTS = S_finish.EVENTS',
            '$heap_owners($heap_prune($heap_graph(S_failure)), HOBJECT n_new_object) = 1',
            'S_closed = $drive_steps(S_finish, 3000)',
            'S_closed.COMPLETION = UNSUPPORTED "increment/decrement destructor changed restored target ownership"',
        ]
    if name == 'review-old-cell-caller-rebind-throw':
        checks += [
            'pupdatewarning_entry.INPUT = PBOOL true',
            'pupdatewarning_entry.POINTER = UPDATE_CELL pupdaterestore.CELL',
            'pupdaterestore.WRAPPER = eps',
            '$lookup(S_entry.ENV, $ptascii("x")) = (pupdaterestore.CELL)',
            '$lookup(S_entry.ENV, $ptascii("keep")) = (pupdaterestore.CELL)',
            '$lookup(S_released.ENV, $ptascii("keep")) = (pupdaterestore.CELL)',
            '$lookup(S_released.ENV, $ptascii("x")) = (n_peer)',
            '$lookup(S_released.ENV, $ptascii("peer")) = (n_peer)',
            'n_peer =/= pupdaterestore.CELL',
            'S_released.STORE[n_peer] = DEFINED (PINT 41)',
            '$heap_owners($heap_prune($heap_graph(S_released)), HCELL pupdaterestore.CELL) = 1',
            'pupdatewarning.PENDING = (n_first)',
            '$lookup(S_restore.ENV, $ptascii("first")) = (n_first_cell)',
            'S_restore.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
            '$heap_owners($heap_prune($heap_graph(S_record)), HOBJECT n_first) = 2',
            '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_first) = 2',
            'S_finish.STORE[pupdaterestore.CELL] = DEFINED (PINT 99)',
            'S_finish.STORE[n_peer] = S_released.STORE[n_peer]',
            'pdestructionoperation_finish.PENDING = (n_first)',
        ]
    else:
        assert name == 'review-surviving-wrapper-pre'
        checks += [
            'pupdatewarning_entry.POINTER = UPDATE_CV ($ptascii("x"))',
            'pupdatewarning.PENDING = eps',
            'pupdaterestore.WRAPPER = (n_wrapper)',
            'pupdaterestore.CELL = |S_record.STORE|',
            '$lookup(S_record.ENV, $ptascii("x")) = (n_wrapper)',
            '$lookup(S_record.ENV, $ptascii("peer")) = (n_wrapper)',
            '$heap_owners($heap_prune($heap_graph(S_record)), HCELL n_wrapper) = 2',
            '$lookup(S_released.ENV, $ptascii("x")) = (pupdaterestore.CELL)',
            '$lookup(S_released.ENV, $ptascii("peer")) = (n_wrapper)',
            '~(pupdaterestore.CELL <- S_released.REFCELLS)',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HCELL n_wrapper) = 1',
            'S_released.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_released*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_wrapper)]',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_old_object) = 1',
            'S_finish.STORE[n_wrapper] = DEFINED (POBJECT n_old_object)',
            '(HOBJECT n_old_object) <- S_finish.ALLOCATIONS',
            '~(n_old_object <- S_finish.DESTRUCTION.CALLED)',
            'S_finish.STORE[pupdaterestore.CELL] = DEFINED (POBJECT n_old_object)',
            'S_finish.EVENTS = S_restore.EVENTS',
            'pdestructionoperation_finish.PENDING = eps',
        ]
    checks += [
        'PhpStep: S_finish ~> S_commit',
        'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning_done) :: ptask_tail*',
        'pupdatewarning_done = pupdatewarning[.PENDING = pdestructionoperation_finish.PENDING]',
        'S_commit.STORE[pupdaterestore.CELL] = DEFINED (PBOOL true)',
        '$task_nodes(UPDATE_WARNING_DONE pupdatewarning_done) = $instance_roots(pdestructionoperation_finish.PENDING)',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_commit.EVENTS = S_finish.EVENTS',
        '$drive_steps(S_finish, 1) = ' + protocol.update_runner.transitioned('S_finish', 'S_commit') + '[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
    ]
    if name == 'review-old-cell-caller-rebind-throw':
        checks += [
            '$lookup(S_commit.ENV, $ptascii("x")) = (n_peer)',
            'S_commit.STORE[n_peer] = S_finish.STORE[n_peer]',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_first) = 2',
            'PhpStep: S_commit ~> S_throw',
            'S_throw.TODO = (THROW_SEARCH n_first) :: ptask_tail*',
            'S_throw.RESULT = KNOWN PNULL',
        ]
    else:
        checks += [
            'S_commit.STORE[n_wrapper] = S_finish.STORE[n_wrapper]',
            '~(n_old_object <- S_commit.DESTRUCTION.CALLED)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_old_object) = 1',
        ]
    return checks + [
        'S_done = $drive_steps(S_commit, 3000)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 3000) = S_done',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-restoration-state-review-', dir=ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    protocol.CASES, protocol.conditions = CASES, conditions
    protocol.HELPERS += ISSET_HELPERS
    passed = protocol.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'][str(wrapper)] = before
    for row in report['rows']:
        row['boundary_control'] = row['id'] == 'review-destructor-new-object-write'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
