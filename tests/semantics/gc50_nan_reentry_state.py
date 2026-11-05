#!/usr/bin/env python3
"""A genuine warning handler updates the borrowed row without a float owner."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc50_peer_nan_child_throw.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.RESULT = KNOWN (PINT $(-9223372036854775808)) '
    '-- if $access_set_plan(S) = (paccess_plan) '
    '-- if paccess_plan.OBJECT = (n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_nan, pweakmapentry_next]) '
    '-- if pweakmapentry_nan.VALUE = PFLOAT n_nan '
    '-- if $access_truth_warning(PFLOAT n_nan) '
    '-- if $weakmap_nan_guard(S, n_map)')
CHECKS = [
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'n_key = pweakmapentry_nan.KEY',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = PINT $(-9223372036854775808)][.OFFSET = POBJECT n_key]',
    'paccess.RHS = S.RESULT',
    '$operand_nodes(paccess.RHS) = eps',
    '$weakmap_value_nodes(pweakmapentry_nan.VALUE) = eps',
    '$value_nodes(paccess.VALUE) = eps',
    'S.FRAMES = pframe_emitter :: pframe_tail*',
    'pframe_emitter.TODO = ptask_emitter :: ptask_emitter_tail*',
    '$source_operand_marker(ptask_emitter) = WEAKMAP_NAN pweakmapnan',
    'S_emitter = $constant_frame_view(S, pframe_emitter, pframe_tail*)',
    '$weakmap_nan_receipt(S_emitter, pweakmapnan)',
    'pweakmapnan.ACCESS.OBJECT = (n_map)',
    'pweakmapnan.ACCESS.OFFSET = POBJECT n_key',
    'pweakmapnan.ENTRY = pweakmapentry_nan',
    '$task_nodes(WEAKMAP_NAN pweakmapnan) = eps',
    '~$weakmap_nan_tasks(S, S.TODO, n_map)',
    '$weakmap_nan_frames(S, S.FRAMES, n_map)',
    '$weakmap_nan_live(S_emitter, pweakmapnan) = (n_nan)',
    'pweakmapnan_bad = pweakmapnan[.OWNER = $(pweakmapnan.OWNER + 1)]',
    'S_bad = S_emitter[.TODO = (WEAKMAP_NAN pweakmapnan_bad) :: pweakmapnan_bad.TAIL]',
    '~$weakmap_nan_receipt(S_bad, pweakmapnan_bad)',
    'pweakmapnan_mode = pweakmapnan[.ACCESS = pweakmapnan.ACCESS[.MODE = ACCESS_READ (KEY_TEST false)]]',
    'S_mode = S_emitter[.TODO = (WEAKMAP_NAN pweakmapnan_mode) :: pweakmapnan_mode.TAIL]',
    '~$weakmap_nan_receipt(S_mode, pweakmapnan_mode)',
    '$weakmap_scalar_value(S, PFLOAT n_nan)',
    '$weakmap_entries_property_value_free(S, PFLOAT n_nan)',
    '$weakmap_scalar_value(S, PFLOAT 18446744073709551615)',
    '$weakmap_entries_property_value_free(S, PFLOAT 18446744073709551615)',
    '~$weakmap_scalar_value(S, PFLOAT 18446744073709551616)',
    '~$weakmap_entries_property_value_free(S, PFLOAT 18446744073709551616)',
    '~$weakmap_reference_value_allowed(S, PFLOAT n_nan)',
    '~$weakmap_entries_child_value_free(S, ALIAS 0)',
    '~$weakmap_entries_child_value_free(S, PARRAY 0)',
    '$weakmap_nan_word(PBOOL false) = eps',
    '$weakmap_nan_word(PNULL) = eps',
    '$weakmap_nan_word(PINT $(-9223372036854775808)) = (9223372036854775808)',
    '$truth(S, PINT $(-9223372036854775808))',
    '~$truth(S, PFLOAT 9223372036854775808)',
    '$weakmap_entries_child_storage(S, n_map)',
    '$weakmap_entries_write_allowed(S, paccess)',
    '~$weakmap_replace_allowed(S, paccess)',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_map) = 2',
    'pweakmapentry_next.VALUE = POBJECT n_next',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_next]',
    '$heap_owners(H, HOBJECT n_next) = 1',
    'S_absent = S[.OBJECTS[n_map] = WEAKMAP (pweakmapentry_next)]',
    '$heap_valid($heap_graph(S_absent))',
    '$weakmap_nan_guard(S_absent, n_map)',
    '$weakmap_entries_child_storage(S_absent, n_map)',
    '$weakmap_key_maps(S_absent, S_absent.ALLOCATIONS, n_key) = eps',
    '$access_valid(S_absent, paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")])',
    '~$weakmap_entries_teardown_table(S_absent, n_map)',
    '~$weakmap_entries_write_allowed(S_absent, paccess)',
    'S_missing = S_emitter[.OBJECTS[n_map] = WEAKMAP (pweakmapentry_next)]',
    '$weakmap_nan_receipt(S_missing, pweakmapnan)',
    '$weakmap_nan_live(S_missing, pweakmapnan) = eps',
    'S_tag = S_emitter[.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_nan[.VALUE = PBOOL false], pweakmapentry_next])]',
    '$weakmap_nan_guard(S_tag, n_map)',
    '$weakmap_nan_live(S_tag, pweakmapnan) = eps',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_written = S_paused[.COMPLETION = NORMAL]',
    'S_written.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_nan[.VALUE = PINT $(-9223372036854775808)], pweakmapentry_next])',
    'S_written.TODO = (ACCESS_RESUME paccess_called) :: ptask_tail*',
    'paccess_called = paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    '$task_nodes(ACCESS_RESUME paccess_called) = [HOBJECT n_map]',
    'S_written.FRAMES = S.FRAMES',
    '$weakmap_nan_guard(S_written, n_map)',
    '$node_children(S_written, HOBJECT n_map) = [HOBJECT n_next]',
    '$heap_owners($heap_graph(S_written), HOBJECT n_map) = 3',
    '$heap_owners($heap_graph(S_written), HOBJECT n_next) = 1',
    'S_written.GC = S.GC',
    'S_written.EVENTS = S.EVENTS',
    'S_written_emitter = $constant_frame_view(S_written, pframe_emitter, pframe_tail*)',
    '$weakmap_nan_live(S_written_emitter, pweakmapnan) = (9223372036854775808)',
    '$heap_valid($heap_graph(S_written))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_written, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_next) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'nan-handler-borrowed-row': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
