#!/usr/bin/env python3
"""Independent reached string-key representation and last-owner list snapshots."""
import base64
import json

import list_missing_warning_review_cases as cases
import list_missing_warning_protocol as shared

SELECTED = (
    'list-missing-review-earlier-target-throw',
    'list-missing-review-shared-owner-retirement',
)


def conditions(name, program, path, stdout):
    shared_owner = name.endswith('shared-owner-retirement')
    line = 4 if shared_owner else 10
    key = 'KINT 1' if shared_owner else 'KINT 3'
    source = 'KNOWN (PARRAY n_array)'
    marker = f'LIST_MISSING_RESULT ({source}) 1 expression phpType13* {line} ({key})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        f'S_entry.TODO = (LIST_FETCH ({source}) 1 expression false phpType13* {line}) :: ptask_tail*',
        f'$list_missing_plan(S_entry) = ((({source}), 1, expression, phpType13*, {line}, {key}))',
        '$list_missing_pending(S_entry)',
        'S_entry.ORIGIN = (porigin)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)',
        'S_entry.STORE[n_x] = DEFINED (PINT 7)',
        'S_entry.STORE[n_y] = DEFINED (PINT 8)',
    ]
    if shared_owner:
        checks += [
            'S_entry.RESULT = KNOWN (PINT 1)',
            '$lookup(S_entry.ENV, $ptascii("before")) = (n_before)',
            'S_entry.STORE[n_before] = DEFINED (PINT 5)',
            '$lookup(S_entry.ENV, $ptascii("q")) = (n_q)',
            'n_q <- S_entry.REFCELLS',
            'S_entry.STORE[n_q] = DEFINED (PINT 2)',
            'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5)), ENTRY (KINT 2) (ALIAS n_q)]',
            '(HARRAY n_array) <- S_entry.ALLOCATIONS',
            '~$array_immutable(S_entry, n_array)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_q) = 2',
        ]
    else:
        checks += [
            'S_entry.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("3")))',
            '$origin_child(S_entry.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 0]) = (porigin_key)',
            '$compiled_read(S_entry, porigin_key) = (PSTRING ($ptascii("3")))',
            '$compiled_string_value(S_entry, porigin_key, PSTRING ($ptascii("3"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("3"))',
            '$list_missing_plan(S_entry[.RESULT = KNOWN (PSTRING ($ptascii("3")))]) = eps',
            '$list_missing_plan(S_entry[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("4")))]) = eps',
            '$lookup(S_entry.ENV, $ptascii("dest")) = (n_dest)',
            'S_entry.STORE[n_x] = DEFINED (PINT 1)',
            'S_entry.STORE[n_dest] = DEFINED (PINT 100)',
        ]
        # The selected x target already holds 1 before this later warning.
        checks.remove('S_entry.STORE[n_x] = DEFINED (PINT 7)')
    checks += [
        'PhpStep: S_entry ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        'perrorcall.LEVEL = 2', f'perrorcall.LINE = {line}',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_array]',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
    ]
    if shared_owner:
        checks += [
            'S_resume_found = $list_warning_seek(S_dispatch, 2, 2000)',
            r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
            'S_resume = S_resume_found[.COMPLETION = NORMAL]',
            'S_resume.TODO = (' + marker + ') :: ptask_tail*',
            'S_resume.CURRENT = eps', 'S_resume.FRAMES = eps',
            '$lookup(S_resume.ENV, $ptascii("a")) = eps',
            '$lookup(S_resume.ENV, $ptascii("q")) = eps',
            'S_resume.STORE[n_q] = DEFINED (PINT 33)',
            'S_resume.STORE[n_x] = DEFINED (PINT 7)',
            'S_resume.STORE[n_y] = DEFINED (PINT 8)',
            'S_resume.STORE[n_before] = DEFINED (PINT 5)',
            'S_resume.ARRAYS[n_array] = S_entry.ARRAYS[n_array]',
            f'$list_missing_source(S_resume, ({source}), 1, expression, phpType13*, {line}, {key})',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HCELL n_q) = 1',
            '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
            'PhpStep: S_resume ~> S_schedule',
            'S_schedule.RESULT = KNOWN PNULL',
            'S_schedule.STORE = S_resume.STORE',
            'S_schedule.ARRAYS = S_resume.ARRAYS',
            'S_schedule.TODO = $list_fetched_tasks(S_resume[.RESULT = KNOWN PNULL], (' + source + '), 1, expression, false, phpType13*, 4) ++ ptask_tail*',
            '$heap_owners($heap_prune($heap_graph(S_schedule)), HARRAY n_array) = 1',
            '$call_descriptors_valid(S_schedule)', '$heap_valid($heap_graph(S_schedule))',
            'S_done = $drive_steps(S_schedule, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL',
            'S_done.STORE[n_y] = DEFINED (PINT 33)',
            'S_done.STORE[n_before] = DEFINED (PINT 5)',
            '$lookup(S_done.ENV, $ptascii("a")) = eps',
            '$lookup(S_done.ENV, $ptascii("q")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 0',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_q) = 0',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            '~((HCELL n_q) <- S_done.ALLOCATIONS)',
            '$drive_steps(S_resume, 2000) = S_done',
        ]
    else:
        checks += [
            'S_done = $drive_steps(S_dispatch, 2000)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)',
            'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_entry, 2000) = S_done',
    ]
    return checks


if __name__ == '__main__':
    cases.CASES = {name: cases.CASES[name] for name in SELECTED}
    raise SystemExit(0 if shared.run(cases, conditions) else 1)
