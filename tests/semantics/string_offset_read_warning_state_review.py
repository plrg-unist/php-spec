#!/usr/bin/env python3
"""Fixed bounds survive retired names; CAST needs an authenticated surviving provider."""
import base64
import json

import string_offset_read_warning_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases
from string_offset_read_warning_protocol import HELPERS as BASE_HELPERS, dispatch, source_checks, finish

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 20) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 21) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("C1:")
dec $string_review_warning(pevent, nat*, int) : nat
def $string_review_warning(DIAGNOSTIC "Warning" n_message* z_found, n_target*, z) = 1
  -- if n_message* = n_target* /\ z_found = z
def $string_review_warning(pevent, n_target*, z) = 0 -- otherwise
dec $string_review_warnings(pevent*, nat*, int) : nat
def $string_review_warnings(eps, n_target*, z) = 0
def $string_review_warnings(pevent :: pevent_tail*, n_target*, z) = $($string_review_warning(pevent, n_target*, z) + $string_review_warnings(pevent_tail*, n_target*, z))
'''


def expected_stderr(name, path):
    if name.endswith('default-bounds'):
        return b'Warning: Uninitialized string offset 7 in ' + bytes(path) + b' on line 9\n'
    if name.endswith('supplied-throw'):
        return b'Warning: Uninitialized string offset 3 in ' + bytes(path) + b' on line 22\n'
    return b''


def warning_count(state, offset, line, count):
    return (f'$string_review_warnings({state}.EVENTS, '
            f'$ptascii("Uninitialized string offset {offset}"), {line}) = {count}')


def throw_checks(start, desc, suffix, emits):
    state = f'S_discard_{suffix}'
    popped = f'S_popped_{suffix}'
    restored = f'S_restored_{suffix}'
    released = f'S_released_{suffix}'
    discarded = f'S_discarded_{suffix}'
    return seek(start, 20, state) + [
        f'{state}.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_{suffix}) :: ptask_{suffix}*',
        f'perrorcall_{suffix}.RESUME = STRING_READ_RESULT {desc}',
        f'{state}.STORE[n_dest] = DEFINED (PINT 99)', f'{state}.STORE[n_later] = DEFINED (PINT 7)',
        f'{state}.STORE[n_key] = DEFINED (PINT 3)',
        f'$string_read_source({state}, {desc})', f'$string_read_ready({state}, {desc})',
        f'$string_read_key_current({state}, {desc}) = (PINT 3)',
        f'$string_read_offset(PINT 3) = (3)', f'~$string_read_in_range({desc}.READ.BASE, 3)',
        f'~$error_handler_eligible({state}, 2)',
        f'{popped} = {state}[.TODO = (THROW_SEARCH n_second) :: ptask_{suffix}*]',
        f'{restored} = $error_handler_restore({popped}, perrorcall_{suffix}.CALLBACK)',
        ('' if not emits else '~') + f'$error_handler_eligible({restored}, 2)',
        f'{discarded} = $error_read_discard({restored}, STRING_READ_RESULT {desc})',
        f'{discarded}.COMPLETION = NORMAL',
        f'{discarded}.TODO = {restored}.TODO',
        f'{discarded}.STORE = {restored}.STORE',
        warning_count(discarded, 3, 22 if emits else 12, int(emits)),
        f'PhpStep: {state} ~> {released}',
        f'{released}.STORE = {state}.STORE',
        warning_count(released, 3, 22 if emits else 12, int(emits)),
    ] + driven(state, released, f'S_release_driven_{suffix}')


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    dropped = name.endswith('borrowed-drop')
    retired = name.endswith('borrowed-bounds-unset')
    cast = thrown or dropped
    line = 12 if thrown else 9
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$string_read_plan(S) = (pstringread)',
        'pstringread.PHASE = STRING_CAST' if cast else 'pstringread.PHASE = STRING_BOUNDS 7',
        f'pstringread.READ.LINE = {line}',
        'pstringread.READ.BASE = PSTRING_CARRIER pstringidentity ($ptascii("abc"))',
        'pstringread.READ.VALUE = PFLOAT 4609434218613702656' if cast else 'pstringread.READ.VALUE = PINT 7',
        '$lookup(S.ENV, $ptascii("text")) = (n_text)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'pstringread.BASECELL = (n_text)', 'pstringread.KEYCELL = (n_key)',
        'S.STORE[n_text] = DEFINED pstringread.READ.BASE',
        '$heap_owners($heap_graph(S), HCELL n_text) = 1', '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '~$string_read_source(S, pstringread[.PHASE = STRING_BOUNDS 0])',
        '$string_read_plan(S[.STORE[n_key] = DEFINED (PINT 0)]) = eps',
    ] + source_checks('S', 'pstringread')
    if dropped or retired:
        checks += ['pstringidentity = REQUEST_STRING n_identity', 'S.STRINGDATA[n_identity] = $ptascii("abc")']
    else:
        checks += ['pstringidentity = INTERNED_STRING']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
            '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
        ]
    else:
        checks += ['$lookup(S.ENV, $ptascii("got")) = (n_got)', 'S.STORE[n_got] = DEFINED (PINT 100)']
    checks += dispatch('S', 'pstringread', 'S_dispatch') + driven('S', 'S_dispatch', 'S_driven')
    checks += seek('S_driven', 13, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*',
        'perrorcall_entered.RESUME = STRING_READ_RESULT pstringread',
        '$task_nodes(perrorcall_entered.RESUME) = eps',
        '$heap_owners($heap_graph(S_entered), HCELL n_text) = 1',
        '$heap_owners($heap_graph(S_entered), HCELL n_key) = 1',
    ]
    if thrown:
        checks += throw_checks('S_entered', 'pstringread', 'first', False)
        checks += seek('S_release_driven_first', 21, 'S_catch_first') + [
            'S_catch_first.STORE[n_dest] = DEFINED (PINT 99)',
            'S_catch_first.STORE[n_later] = DEFINED (PINT 7)',
            'S_catch_first.STORE[n_calls] = DEFINED (PINT 1)',
            '$throwable_previous_id(S_catch_first, n_second) = eps',
        ] + seek('S_catch_first', 10, 'S_tmp') + [
            '$string_read_plan(S_tmp) = (pstringread_tmp)',
            'pstringread_tmp.PHASE = STRING_CAST', 'pstringread_tmp.READ.LINE = 22',
            'pstringread_tmp.READ.VALUE = PNULL',
            'pstringread_tmp.BASECELL = eps', 'pstringread_tmp.KEYCELL = (n_key)',
            'pstringread_tmp.READ.OWNERS = BASE_VALUE (KNOWN pstringread_tmp.READ.BASE)',
            'pstringread_tmp.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_tmp) ($ptascii("abc"))',
            '$string_read_provider_ready(S_tmp[.ENV = eps], pstringread_tmp)',
            'S_tmp.STORE[n_dest] = DEFINED (PINT 101)',
        ] + source_checks('S_tmp', 'pstringread_tmp') + dispatch('S_tmp', 'pstringread_tmp', 'S_tmp_dispatch')
        checks += driven('S_tmp', 'S_tmp_dispatch', 'S_tmp_driven')
        checks += throw_checks('S_tmp_driven', 'pstringread_tmp', 'second', True)
        checks += finish('S_release_driven_second', stdout) + [
            'S_read.STORE[n_dest] = DEFINED (PINT 99)', 'S_read.STORE[n_later] = DEFINED (PINT 7)',
            'S_read.STORE[n_calls] = DEFINED (PINT 2)',
            '$lookup(S_read.ENV, $ptascii("e")) = eps',
            '$throwable_previous_id(S_read, n_second) = eps',
            warning_count('S_read', 3, 12, 0), warning_count('S_read', 3, 22, 1),
            '~((HOBJECT n_second) <- S_done.ALLOCATIONS)',
            '~((HCELL n_dest) <- S_done.ALLOCATIONS)', '~((HCELL n_later) <- S_done.ALLOCATIONS)',
        ]
        return checks
    checks += seek('S_entered', 11 if cast else 12, 'S_resume') + [
        'S_resume.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*',
        '$string_read_source(S_resume, pstringread)',
        '$string_carrier_valid(S_resume, pstringread.READ.BASE)',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_valid($heap_graph(S_resume))', '$call_descriptors_valid(S_resume)',
    ]
    if dropped:
        checks += [
            'S_resume.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))',
            'S_resume.STORE[n_key] = DEFINED (PINT 99)',
            'S_resume.STRINGDATA[n_identity] = $ptascii("abc")',
            '~$string_read_provider_ready(S_resume, pstringread)', '~$string_read_ready(S_resume, pstringread)',
            '$string_read_key_current(S_resume, pstringread) = (PINT 99)',
            'S_same_bytes = S_resume[.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))]',
            '$string_carrier_valid(S_same_bytes, pstringread.READ.BASE)',
            '$string_plain(pstringread.READ.BASE) = PSTRING ($ptascii("abc"))',
            '~$string_read_provider_ready(S_same_bytes, pstringread)',
            '~$string_read_ready(S_same_bytes, pstringread)', '$string_read_source(S_same_bytes, pstringread)',
            '$error_read_discard(S_resume, STRING_READ_RESULT pstringread).COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"',
            'PhpStep: S_resume ~> S_boundary',
            'S_boundary.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"',
            'S_boundary.STORE = S_resume.STORE', 'S_boundary.STRINGDATA = S_resume.STRINGDATA',
            'S_boundary.STORE[n_got] = DEFINED (PINT 100)',
            '$lookup(S_boundary.ENV, $ptascii("later")) = (n_later)',
            'S_boundary.STORE[n_later] = DEFINED (PINT 7)',
            '$list_warning_outputs(S_boundary.EVENTS) = ([' + ','.join(map(str, stdout.split(b'R:', 1)[0])) + '])',
            '$call_descriptors_valid(S_boundary)', '$heap_valid($heap_graph(S_boundary))',
        ] + empty_biases('S_boundary')
        return checks
    checks += [
        'pstringread.PHASE = STRING_BOUNDS 7',
        '$string_read_ready(S_resume, pstringread)',
        '$string_read_ready(S_resume[.ENV = eps], pstringread)',
        '$error_read_discard(S_resume, STRING_READ_RESULT pstringread) = S_resume',
    ]
    if retired:
        checks += [
            '$lookup(S_resume.ENV, $ptascii("text")) = eps', '$lookup(S_resume.ENV, $ptascii("key")) = eps',
            '~((HCELL n_text) <- S_resume.ALLOCATIONS)', '~((HCELL n_key) <- S_resume.ALLOCATIONS)',
            '~$string_read_provider_ready(S_resume, pstringread)',
            '$string_read_key_current(S_resume, pstringread) = eps',
            'S_resume.STRINGDATA[n_identity] = $ptascii("abc")',
            warning_count('S_resume', 7, 9, 0),
        ]
    else:
        checks += [
            'S_resume.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))',
            'S_resume.STORE[n_key] = DEFINED (PINT 0)',
            warning_count('S_resume', 7, 9, 1),
        ]
    checks += [
        'PhpStep: S_resume ~> S_empty', 'S_empty.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)',
        'S_empty.STORE = S_resume.STORE', 'S_empty.STRINGDATA = S_resume.STRINGDATA',
        'S_empty.BASE = BASE_VALUE (KNOWN PNULL)',
    ] + driven('S_resume', 'S_empty', 'S_empty_driven') + finish('S_empty_driven', stdout) + [
        'S_read.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)',
        '~((HCELL n_text) <- S_done.ALLOCATIONS)', '~((HCELL n_key) <- S_done.ALLOCATIONS)',
        '~((HCELL n_got) <- S_done.ALLOCATIONS)', '~((HCELL n_calls) <- S_done.ALLOCATIONS)',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr) else 1)
