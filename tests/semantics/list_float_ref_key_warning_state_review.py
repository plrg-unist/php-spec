#!/usr/bin/env python3
"""Reached surviving old tables, detached source cells and later ref binding."""
import base64
import hashlib
import json
from pathlib import Path

import list_float_ref_key_warning_review_cases as cases
import list_float_ref_key_warning_protocol as author
import list_missing_warning_protocol as shared

HELPERS = author.HELPERS


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def conditions(name, program, path, stdout):
    held = name.endswith('cow-copy-survives')
    index, line, integer, q_key = (1, 15, 2, '2') if held else (0, 27, -2, '1')
    args = f'n_source, n_array, {index}, expression, phpType13*, z, n_bits, i'
    marker = lambda phase: f'LIST_KEY_FLOAT_REF_RESULT n_source n_array {index} expression phpType13* z n_bits i {phase}'
    missing = f'LIST_MISSING_RESULT (REFERENCE n_source) {index} expression phpType13* z (KINT i)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        f'$list_float_ref_key_plan(S) = (({args}))',
        f'S.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', f'i = {integer}', 'S.ORIGIN = (porigin)',
        f'S.RESULT = VARIABLE ($ptascii("key")) {line}',
        '$list_float_key_pending(S)', '$list_float_key_plan(S) = eps', '$list_missing_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("a")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        'n_source <- S.REFCELLS', '$list_missing_array(S, REFERENCE n_source) = (n_array)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)', 'S.STORE[n_key_cell] = DEFINED (PFLOAT n_bits)',
        '$float_long(n_bits, true) = (i, [PRECISIONLOSS])',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
        f'$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT {q_key}) = (ALIAS n_q)',
        '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 2',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 3',
        '$list_float_ref_key_source(S, ' + args + ', 0)',
        '$task_nodes(' + marker(0) + ') = [HCELL n_source, HARRAY n_array]',
        '$task_nodes(' + marker(1) + ') = [HCELL n_source]',
        '~$list_float_ref_key_source(S, ' + args + ', 2)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, z, n_bits, $(i + 1), 0)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, $(z + 1), n_bits, i, 0)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, eps, z, n_bits, i, 0)',
        f'~$list_float_ref_key_source(S, n_source, (|S.ARRAYS|), {index}, expression, phpType13*, z, n_bits, i, 1)',
        f'~$list_float_ref_key_source(S, n_source, n_array, {index}, expression, phpType13*, z, 18446744073709551616, i, 0)',
        '~$list_float_ref_key_source(S[.ORIGIN = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.SOURCES = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.CODE = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.REFCELLS = eps], ' + args + ', 0)',
        '~$list_float_ref_key_source(S[.ALLOCATIONS = eps], ' + args + ', 0)',
        '$list_float_ref_key_plan(S[.RESULT = KNOWN (PFLOAT n_bits)]) = eps',
        '$list_float_ref_key_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4611686018427387904)]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 9221120237041090560)]) = eps',
        '$list_float_ref_key_plan(S[.STORE[n_source] = DEFINED PNULL]) = eps',
        f'$list_float_ref_key_plan(S[.TODO = (LIST_FETCH (REFERENCE n_source) {index} expression true phpType13* z) :: ptask_tail*]) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if held:
        checks += [
            '$lookup(S.ENV, $ptascii("copy")) = (n_copy_cell)', 'S.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            'n_copy =/= n_array', '$entry_lookup(S.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (PINT 9))',
            '$lookup(S.ENV, $ptascii("early")) = (n_early)', 'S.STORE[n_early] = DEFINED (PINT 9)',
            '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = (ALIAS n_early)',
            '$entry_lookup(S.ARRAYS[n_copy].ITEMS, KINT 2) = (ALIAS n_q)',
        ]
    else:
        checks += [
            '$lookup(S.ENV, $ptascii("key_alias")) = (n_key_cell)',
            '$lookup(S.ENV, $ptascii("q_alias")) = (n_q)',
            '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
            '$lookup(S.ENV, $ptascii("key_replacement")) = (n_key_replacement)',
            '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT $(-2)) = eps',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(0), 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $list_float_key_message(n_bits)',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ' + marker(1) + '])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
    ] + seek('S_dispatch', 13, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker(0), 'perrorcall_entered.TARGET =/= eps',
        '$heap_count(HCELL n_source, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker(0) + ') :: ptask_tail*',
        '$list_float_ref_key_source(S_resume, ' + args + ', 0)',
        'S_resume.STORE[n_q] = DEFINED (PINT 33)', 'S_resume.STORE[n_y] = DEFINED (PINT 8)',
        'S_resume.STORE[n_dest] = DEFINED (PINT 200)',
        '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 2',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
    ]
    if held:
        checks += [
            'S_resume.ERRORHANDLER = S.ERRORHANDLER',
            '$lookup(S_resume.ENV, $ptascii("hold")) = (n_hold)', 'S_resume.STORE[n_hold] = DEFINED (PARRAY n_array)',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 2) = (DIRECT (PINT 22))',
            '$entry_lookup(S_resume.ARRAYS[n_live].ITEMS, KINT 1) = (DIRECT (PINT 44))',
            'S_resume.STORE[n_key_cell] = DEFINED (PBOOL false)', 'S_resume.STORE[n_x] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 2',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 3',
        ]
    else:
        checks += [
            'S_resume.ERRORHANDLER =/= S.ERRORHANDLER',
            '~((HCELL n_key_cell) <- S_resume.ALLOCATIONS)',
            '$lookup(S_resume.ENV, $ptascii("key_alias")) = eps',
            '$lookup(S_resume.ENV, $ptascii("key")) = (n_key_replacement)',
            'n_key_replacement =/= n_key_cell',
            'S_resume.STORE[n_key_replacement] = DEFINED (PFLOAT n_live_bits)',
            '$float_long(n_live_bits, true) = (9, [PRECISIONLOSS])',
            '$lookup(S_resume.ENV, $ptascii("a")) = (n_replacement)', 'n_replacement =/= n_source',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
            'S_resume.STORE[n_replacement] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
            '$lookup(S_resume.ENV, $ptascii("q")) = (n_other)', 'n_other =/= n_q',
            'S_resume.STORE[n_other] = DEFINED (PINT 44)', 'S_resume.STORE[n_x] = DEFINED (PINT 77)',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_source) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 2',
        ]
    checks += [
        'PhpStep: S_resume ~> S_release', 'S_release.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_release.STORE = S_resume.STORE', 'S_release.ARRAYS = S_resume.ARRAYS',
        'S_release.ALLOCATIONS = S_resume.ALLOCATIONS',
        'S_phase_found = $drive_steps(S_resume, 1)', 'S_phase_found.COMPLETION = BUDGET',
        'S_phase = S_phase_found[.COMPLETION = NORMAL]',
        'S_phase.TODO = S_release.TODO', 'S_phase.STORE = S_release.STORE', 'S_phase.ARRAYS = S_release.ARRAYS',
        '(HARRAY n_array) <- S_phase.ALLOCATIONS', '(HCELL n_source) <- S_phase.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_phase)), HARRAY n_array) = 1',
        '$list_float_ref_key_source(S_phase, ' + args + ', 1)',
        '$call_descriptors_valid(S_phase)', '$heap_valid($heap_graph(S_phase))',
        'PhpStep: S_phase ~> S_lookup',
    ]
    if held:
        checks += [
            f'S_lookup.TODO = (AT porigin_x (LIST_STORE expression (KNOWN (PINT 33)) false z_x)) :: (LIST_NEXT (REFERENCE n_source) {index + 1} phpType13* z_next) :: ptask_tail*',
            'S_lookup.EVENTS = S_phase.EVENTS',
        ]
    else:
        checks += [
            'S_lookup.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
            'perrorcall_warning.RESUME = ' + missing, 'perrorcall_warning.LEVEL = 2',
            'perrorcall_warning.LINE = z', 'perrorcall_warning.MESSAGE = $ptascii("Undefined array key -2")',
            '$error_call_valid(S_lookup, perrorcall_warning)',
        ]
    checks += [
        'S_lookup.STORE = S_phase.STORE', 'S_lookup.ARRAYS = S_phase.ARRAYS',
        'S_lookup_driven_found = $drive_steps(S_phase, 1)', 'S_lookup_driven_found.COMPLETION = BUDGET',
        'S_lookup_driven = S_lookup_driven_found[.COMPLETION = NORMAL]',
        'S_lookup_driven.TODO = S_lookup.TODO', 'S_lookup_driven.STORE = S_lookup.STORE',
        'S_lookup_driven.ARRAYS = S_lookup.ARRAYS',
    ]
    if held:
        checks += ['S_after = S_lookup_driven']
    else:
        checks += seek('S_lookup_driven', 3, 'S_warning_entered') + [
            'S_warning_entered.CURRENT =/= eps', 'S_warning_entered.ERRORHANDLER.CALLBACK = eps',
            'S_warning_entered.FRAMES = pframe_warning :: pframe_warning_tail*',
            'pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall_warning_entered) :: ptask_warning*',
            'perrorcall_warning_entered.RESUME = ' + missing, 'perrorcall_warning_entered.TARGET =/= eps',
        ] + seek('S_warning_entered', 2, 'S_warning_resume') + [
            'S_warning_resume.TODO = (' + missing + ') :: ptask_tail*',
            'S_warning_resume.ERRORHANDLER = S_resume.ERRORHANDLER',
            'S_warning_resume.STORE[n_x] = DEFINED (PINT 99)', 'S_warning_resume.STORE[n_q] = DEFINED (PINT 55)',
            'S_warning_resume.STORE[n_source] = DEFINED (PARRAY n_array)',
            '$lookup(S_warning_resume.ENV, $ptascii("next")) = (n_next_cell)',
            'S_warning_resume.STORE[n_next_cell] = DEFINED (PINT 1)',
            'S_warning_resume.STORE[n_replacement] = DEFINED (PARRAY n_written)',
            '$entry_lookup(S_warning_resume.ARRAYS[n_written].ITEMS, KINT $(-2)) = (DIRECT (PINT 77))',
            '$entry_lookup(S_warning_resume.ARRAYS[n_array].ITEMS, KINT $(-2)) = eps',
            '$list_missing_source(S_warning_resume, REFERENCE n_source, 0, expression, phpType13*, z, KINT i)',
            'PhpStep: S_warning_resume ~> S_null_store',
            'S_null_store.TODO = (AT porigin_x (LIST_STORE expression (KNOWN PNULL) false z_x)) :: (LIST_NEXT (REFERENCE n_source) 1 phpType13* z_next) :: ptask_tail*',
            'S_null_store.STORE = S_warning_resume.STORE', 'S_null_store.ARRAYS = S_warning_resume.ARRAYS',
            'S_after = S_warning_resume',
        ]
    checks += seek('S_after', 14, 'S_next') + [
        f'S_next.TODO = (LIST_FETCH (REFERENCE n_source) {index + 1} expression_y true eps z_y) :: ptask_y*',
        f'z_y = {line + 1}',
        'S_next.RESULT = KNOWN (PINT 1)' if held else f'S_next.RESULT = VARIABLE ($ptascii("next")) {line + 1}',
        'S_next.STORE[n_x] = DEFINED (PINT 33)' if held else 'S_next.STORE[n_x] = DEFINED PNULL',
        'S_next.STORE[n_y] = DEFINED (PINT 8)',
        'PhpStep: S_next ~> S_read',
        f'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (REFERENCE n_slot) true z_target)) :: (LIST_NEXT (REFERENCE n_source) {index + 2} eps z_end) :: ptask_y*',
        'S_read.STORE[n_source] = DEFINED (PARRAY n_after)',
        '$entry_lookup(S_read.ARRAYS[n_after].ITEMS, KINT 1) = (ALIAS n_slot)',
        '$heap_count(HARRAY n_after, $pools_nodes(S_read.POOLS)) = 0',
        'S_read.STORE[n_slot] = DEFINED (PINT 44)' if held else 'S_read.STORE[n_slot] = DEFINED (PINT 55)',
        'n_after =/= n_array' if held else 'n_after = n_array',
        'n_slot =/= n_q' if held else 'n_slot = n_q',
        'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
        'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]',
        'S_read_driven.TODO = S_read.TODO', 'S_read_driven.STORE = S_read.STORE',
        'S_read_driven.ARRAYS = S_read.ARRAYS',
        'S_target_found = $drive_steps(S_read_driven, 1)', 'S_target_found.COMPLETION = BUDGET',
        'S_target = S_target_found[.COMPLETION = NORMAL]',
        'S_target.TODO = (LIST_STORE expression_y (REFERENCE n_slot) true z_target) :: ptask_bound*',
        'PhpStep: S_target ~> S_bound_raw', '$lookup(S_bound_raw.ENV, $ptascii("y")) = (n_slot)',
        '$heap_owners($heap_prune($heap_graph(S_bound_raw)), HCELL n_y) = 0',
        'S_bound_found = $drive_steps(S_target, 1)', 'S_bound_found.COMPLETION = BUDGET',
        'S_bound = S_bound_found[.COMPLETION = NORMAL]', '~((HCELL n_y) <- S_bound.ALLOCATIONS)',
        '$call_descriptors_valid(S_bound)', '$heap_valid($heap_graph(S_bound))',
        'S_done = $drive_steps(S_bound, 2000)',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HARRAY n_after) <- S_done.ALLOCATIONS)',
        '~((HCELL n_slot) <- S_done.ALLOCATIONS)',
    ]
    if held:
        checks += ['~((HARRAY n_copy) <- S_done.ALLOCATIONS)', '~((HCELL n_early) <- S_done.ALLOCATIONS)']
    else:
        checks += ['~((HCELL n_key_cell) <- S_done.ALLOCATIONS)']
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_resume, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
