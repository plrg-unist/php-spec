#!/usr/bin/env python3
"""Genuine Iterator-unpack cursor, cache, warning and abrupt-owner frontiers."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
          '$useriter_instance(S, n_data)', '$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]']
TEMP = ['piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        '$operand_nodes(piteratorunpack.INPUT) = [HOBJECT n_data]',
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2']
FAILURE = ['$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
           'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
           '$throwable_live(S, n_error)',
           '$lookup(S.ENV, $ptascii("entered")) = (n_entered)',
           'S.STORE[n_entered] = DEFINED (PINT 0)',
           '$lookup(S.ENV, $ptascii("r")) = (n_r)',
           'S.STORE[n_r] = DEFINED (PINT 41)']
INVOKE = ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
          '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"')
BYREF = 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*'
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_fiber) '
        '-- if $fiber_at(S, n_fiber) = (pfiber) '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base]')
KEY_PARK = PARK + (' -- if pframe_unpack.TODO = (ITERATOR_UNPACK piteratorunpack "key") '
                   ':: ptask_unpack*')
WARNING_PARK = PARK + (' -- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) '
                       ':: ptask_unpack* -- if perrorcall.RESUME = '
                       'ITERATOR_UNPACK piteratorunpack "byref"')
PARK_VIEW = ['S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
             'pfiber.STATUS = FIBER_SUSPENDED',
             'pfibervm.CURRENT = (pcallcontext_saved)',
             'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
             'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
             'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
             '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
             '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
             '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)']


OP_AFTER = ['pdestructionoperation.PENDING = (n_error)',
 'pdestructionoperation.CALLER = S.CURRENT',
 'pdestructionoperation.ORIGIN = piteratorunpack.CALL.CALLSITE',
 'pdestructionoperation.CONSTCONTEXT = S.CONSTCONTEXT',
 'pdestructionoperation.COMPLETION = NORMAL',
 'pdestructionoperation.VALUE = KNOWN PNULL',
 'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_one.DESTRUCTION.OPERATIONS = pdestructionoperation :: S.DESTRUCTION.OPERATIONS',
 '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
 '$heap_count(HOBJECT n_error, $tasks_nodes(S_one.TODO)) = 1',
 '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
 '$eager_operation_source_valid(S_one, pdestructionoperation)',
 '$destructor_operation_valid(S_one, pdestructionoperation)']

CASES = {
    'cv-prepare-borrows-source-and-allocates-one-real-cursor': {
        'source': SOURCES['iterator-call-unpack-positional-prefix-named-tail'],
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail*',
        'checks': [
            'S.RESULT = VARIABLE ($ptascii("it")) z',
            '$lookup(S.ENV, $ptascii("it")) = (n_it)',
            'S.STORE[n_it] = DEFINED (POBJECT n_data)',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            'punpackcall.INDEX = 1',
            'punpackcall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 11))]',
            'punpackcall.SENT.NAMED = eps',
            '$operand_nodes(S.RESULT) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'n_cursor = S.NEXTITER', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall', 'piteratorunpack.OBJECT = n_data',
            'piteratorunpack.ITERATOR = n_cursor', 'piteratorunpack.INPUT = S.RESULT',
            'piteratorunpack.CURRENT = KNOWN PNULL', 'piteratorunpack.KEY = KNOWN PNULL',
            '~piteratorunpack.NAMED',
            'S_one.ITERATORS = S.ITERATORS ++ [OBJECTITER n_cursor n_data 0 false]',
            'S_one.NEXTITER = $(n_cursor + 1)',
            '$task_nodes(ITERATOR_UNPACK piteratorunpack "rewind-start") = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$iterator_unpack_result_valid(S_one, piteratorunpack, "rewind-start")',
            'piteratorunpack_bad = piteratorunpack[.INPUT = KNOWN PNULL]',
            'S_bad = S_one[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "rewind-start") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S_one)',
            '~$iterator_unpack_result_valid(S_bad, piteratorunpack_bad, "rewind-start")',
            '~$call_descriptors_valid(S_bad)', *POST,
        ],
    },
    'temporary-input-and-data-stay-owned-through-borrowed-rewind-selection': {
        'source': SOURCES['iterator-call-unpack-temporary-data-before-body'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
        'checks': [
            *HEADER, *TEMP, 'S.CURRENT = eps', 'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$iterator_unpack_result_valid(S, piteratorunpack, "rewind-start")',
            '~$iterator_unpack_result_valid(S, piteratorunpack[.NAMED = true], "rewind-start")',
            'piteratorunpack_bad = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.LINE = $(piteratorunpack.CALL.LINE + 1)]]',
            'S_bad = S[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "rewind-start") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$iterator_unpack_result_valid(S_bad, piteratorunpack_bad, "rewind-start")',
            '~$call_descriptors_valid(S_bad)',
            'S_wrong_origin = S[.ORIGIN = piteratorunpack.CALL.CALLSITE]',
            '$heap_graph(S_wrong_origin) = $heap_graph(S)',
            '~$iterator_unpack_result_valid(S_wrong_origin, piteratorunpack, "rewind-start")',
            '~$call_descriptors_valid(S_wrong_origin)', *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_site) z) :: '
            '(ITERATOR_UNPACK piteratorunpack "rewind") :: ptask_tail*',
            'pcalltarget = UNPACK_ITERATOR_TARGET n_data porigin_method',
            'S_one.ORIGIN = (porigin_site)',
            '$unpack_origin(S_one, piteratorunpack.CALL) = (porigin_site)',
            'z = $unpack_line(S_one, piteratorunpack.CALL)',
            '$target_nodes(pcalltarget) = eps', '$target_instance(pcalltarget) = eps',
            '$useriter_pending(S_one, pcalltarget, porigin_site)',
            '$call_selected_valid(S_one, pcalltarget, (porigin_site))',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2', *POST,
        ],
    },
    'entered-implicit-frame-has-no-receiver-owner-or-source-call-authority': {
        'source': SOURCES['iterator-call-unpack-temporary-data-before-body'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = '
                  'UNPACK_ITERATOR_TARGET n_data porigin_method -- if S.FRAMES = '
                  'pframe_unpack :: pframe_tail* -- if pframe_unpack.TODO = '
                  '(ITERATOR_UNPACK piteratorunpack "rewind") :: ptask_unpack*'),
        'checks': [
            'piteratorunpack.OBJECT = n_data',
            'pcallcontext.RECEIVER = (n_data)', 'pcallcontext.INSTANCE = eps',
            'pcallcontext.ARGC = 0', 'pcallcontext.EXTRA = eps', 'pcallcontext.NAMED = eps',
            '$call_receiver_roots(pcallcontext) = eps',
            '$heap_count(HOBJECT n_data, $call_context_roots(S.CURRENT)) = 0',
            '$iterator_unpack_frame(S, pcallcontext, pframe_unpack)',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$heap_count(HOBJECT n_data, $tasks_nodes(pframe_unpack.TODO)) = 2',
            *ADMISSION,
            'pcallcontext_bad = pcallcontext[.TARGET = METHOD_TARGET n_data porigin_method]',
            'S_bad = S[.CURRENT = (pcallcontext_bad)]',
            '$heap_valid($heap_graph(S_bad))',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_data) = 3',
            '~$iterator_unpack_frame(S_bad, pcallcontext_bad, pframe_unpack)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'owning-original-reference-retires-cell-after-data-with-keeper-protected': {
        'source': SOURCES['iterator-call-unpack-reference-original-operand'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "finish") :: ptask_tail*',
        'checks': [
            *HEADER, 'piteratorunpack.INPUT = REFERENCE n_input',
            '$lookup(S.ENV, $ptascii("it")) = (n_input)',
            'S.STORE[n_input] = DEFINED (POBJECT n_data)',
            '$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)',
            'S.STORE[n_keeper] = DEFINED (POBJECT n_data)', 'n_input =/= n_keeper',
            '$heap_owners($heap_graph(S), HCELL n_input) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 3',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(UNPACK_ARGS punpackcall_next) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HCELL n_input)]',
            'punpackcall_next = $unpack_advance(piteratorunpack.CALL, piteratorunpack.CALL.SENT)',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_count(HCELL n_input, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'current-reference-rereads-key-rewrite-before-send-and-cache-retirement': {
        'source': SOURCES['iterator-call-unpack-current-reference-key-rewrite'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 9)', 'piteratorunpack.KEY = KNOWN (PINT 0)',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$heap_owners($heap_graph(S), HCELL n_value) = 2', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_value)]',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 9))]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            '~piteratorunpack_next.NAMED',
            'S_one.STORE[n_value] = DEFINED (PINT 9)',
            'S_one.RESULT = KNOWN PNULL', 'S_one.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'key-reference-unwrap-keeps-current-reference-live-until-send': {
        'source': SOURCES['iterator-call-unpack-key-reference-unwrapped'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                  '-- if S.RESULT = REFERENCE n_key'),
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            '$lookup(S.ENV, $ptascii("keyCell")) = (n_key)',
            'S.STORE[n_value] = DEFINED (PINT 9)', 'S.STORE[n_key] = DEFINED (PINT 11)',
            'n_key =/= n_value', *ADMISSION, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack[.KEY = KNOWN (PINT 11)] '
            '"send") :: ptask_tail*',
            '$heap_count(HCELL n_key, $tasks_nodes(S_one.TODO)) = 0',
            '$heap_count(HCELL n_value, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_key) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_value) = 2', *POST,
        ],
    },
    'valid-object-retval-retires-before-current-start': {
        'source': SOURCES['iterator-call-unpack-valid-object-retval-retirement'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "valid") :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (POBJECT n_retval)'),
        'checks': [
            *HEADER, *TEMP, 'n_retval =/= n_data',
            '$heap_owners($heap_graph(S), HOBJECT n_retval) = 1',
            'S.EVENTS = [OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack "current-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_retval)]',
            '~(n_retval <- S_one.DESTRUCTION.CALLED)',
            'S_one.RESULT = KNOWN PNULL',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'empty-finish-releases-two-data-occurrences-before-default-entry': {
        'source': SOURCES['iterator-call-unpack-empty-temporary-before-default'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "finish") :: ptask_tail*',
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CALL.SENT.SLOTS = eps',
            'piteratorunpack.CALL.SENT.NAMED = eps',
            'S.EVENTS = [OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(UNPACK_ARGS punpackcall_next) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            'punpackcall_next.SENT.SLOTS = eps', 'punpackcall_next.SENT.NAMED = eps',
            'S_one.ORIGIN = piteratorunpack.CALL.CALLSITE',
            'S_one.CURRENT = eps', 'S_one.EVENTS = S.EVENTS',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'numeric-string-key-becomes-position-and-leading-zero-keeps-variadic-name': {
        'source': SOURCES['iterator-call-unpack-numeric-string-and-variadic-name'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "finish") :: ptask_tail*',
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.NAMED',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            'piteratorunpack.CALL.SENT.NAMED = [($ptascii("01"), KNOWN (PINT 8))]',
            '$iterator_unpack_result_valid(S, piteratorunpack, "finish")',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(UNPACK_ARGS punpackcall_next) :: ptask_tail*',
            'punpackcall_next.SENT = piteratorunpack.CALL.SENT',
            '$unpack_call_roots(punpackcall_next) = eps',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps', *POST,
        ],
    },
    'positional-after-named-preserves-error-marker-and-already-sent-slot': {
        'source': SOURCES['iterator-call-unpack-positional-after-named'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.NAMED -- if piteratorunpack.KEY = KNOWN (PINT 0)'),
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = KNOWN (PINT 8)',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail*',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Cannot use positional argument after named argument during unpacking"))',
            '$throwable_field(S_one, n_error, "line") = PINT '
            '$unpack_line(S_one, piteratorunpack.CALL)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S_one.TODO)) = 1', *POST,
        ],
    },
    'invalid-object-key-discard-retires-key-before-unsent-cache-and-data': {
        'source': SOURCES['iterator-call-unpack-invalid-object-key-retirement'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail* '
                  '-- if piteratorunpack.KEY = KNOWN (POBJECT n_key) '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current)'),
        'checks': [
            *HEADER, *TEMP, 'n_key =/= n_current', 'n_current =/= n_data',
            '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$string_bytes($throwable_field(S, n_error, "message")) = '
            '($ptascii("Keys must be of type int|string during argument unpacking"))',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_key), '
            'DESTRUCTION_VALUE (HOBJECT n_current), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error"',
            *OP_AFTER,
        ],
    },
    'key-throw-drops-unsent-cache-before-iterator-and-original': {
        'source': SOURCES['iterator-call-unpack-key-throw-unsent-current'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail*'),
        'checks': [
            *HEADER, *TEMP, *FAILURE, 'piteratorunpack.CURRENT = KNOWN (POBJECT n_current)',
            'piteratorunpack.KEY = KNOWN PNULL', 'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_current), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data)]',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "key"',
            *OP_AFTER,
        ],
    },
    'next-throw-retires-iterator-before-already-sent-object': {
        'source': SOURCES['iterator-call-unpack-next-throw-sent-current'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(ITERATOR_UNPACK piteratorunpack "next") :: ptask_tail*'),
        'checks': [
            *HEADER, *TEMP, *FAILURE,
            'piteratorunpack.CURRENT = KNOWN PNULL', 'piteratorunpack.KEY = KNOWN PNULL',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_current))]',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_current)]',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "next"',
            *OP_AFTER,
        ],
    },
    'throwing-valid-retval-keeps-original-exception-before-current': {
        'source': SOURCES['iterator-call-unpack-valid-object-retval-destructor-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(ITERATOR_UNPACK piteratorunpack "current-start") :: ptask_tail*'),
        'checks': [
            *HEADER, *TEMP, *FAILURE,
            'piteratorunpack.CURRENT = KNOWN PNULL', 'piteratorunpack.KEY = KNOWN PNULL',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            'S.EVENTS = [OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("R|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 2',
            '$throwable_live(S_one, n_error)', 'S_one.EVENTS = S.EVENTS', *POST,
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "current-start"',
            *OP_AFTER,
        ],
    },
    'same-source-reentry-uses-distinct-frame-cursors-and-data': {
        'source': SOURCES['iterator-call-unpack-same-source-reentrant-key'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail* '
                  '-- if S.FRAMES = pframe_key :: pframe_outer :: pframe_tail* '
                  '-- if pframe_outer.TODO = (ITERATOR_UNPACK piteratorunpack_outer "key") '
                  ':: ptask_outer*'),
        'checks': [
            *HEADER, *TEMP, 'n_outer = piteratorunpack_outer.ITERATOR',
            'n_data_outer = piteratorunpack_outer.OBJECT', 'n_cursor =/= n_outer',
            'n_data =/= n_data_outer',
            'piteratorunpack.CALL.CALLSITE = piteratorunpack_outer.CALL.CALLSITE',
            '$unpack_origin(S, piteratorunpack.CALL) = '
            '$unpack_origin(S, piteratorunpack_outer.CALL)',
            '$useriter_frames_ids(S.FRAMES) = [n_outer]',
            '$useriter_ids_unique([n_cursor, n_outer])',
            '$heap_owners($heap_graph(S), HOBJECT n_data_outer) = 2',
            '$useriter_chain_valid(S, S.CURRENT, S.FRAMES)', *ADMISSION,
            'piteratorunpack_foreign = piteratorunpack[.INPUT = KNOWN (POBJECT n_data_outer)]',
            'S_foreign = S[.TODO = (ITERATOR_UNPACK piteratorunpack_foreign "rewind-start") :: ptask_tail*]',
            '$iterator_unpack_input(S_foreign, piteratorunpack_foreign.CALL, piteratorunpack_foreign.INPUT)',
            '~$iterator_unpack_original(piteratorunpack_foreign)',
            '$heap_valid($heap_graph(S_foreign))',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_data_outer) = 3',
            '~$iterator_unpack_result_valid(S_foreign, piteratorunpack_foreign, "rewind-start")',
            '~$call_descriptors_valid(S_foreign)',
            'pframe_duplicate = pframe_outer[.TODO = '
            '(ITERATOR_UNPACK piteratorunpack_outer "key") :: '
            '(ITERATOR_UNPACK piteratorunpack_outer "key") :: ptask_outer*]',
            'S_duplicate = S[.FRAMES = pframe_key :: pframe_duplicate :: pframe_tail*]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data_outer) = 4',
            '$useriter_frames_ids(S_duplicate.FRAMES) = [n_outer, n_outer]',
            '~$useriter_chain_valid(S_duplicate, S_duplicate.CURRENT, S_duplicate.FRAMES)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'parked-key-keeps-cache-and-borrowed-context-before-any-send': {
        'source': SOURCES['iterator-call-unpack-key-parks-before-send'],
        'stage': KEY_PARK,
        'checks': [
            *PARK_VIEW, 'piteratorunpack.CURRENT = KNOWN (PINT 7)',
            'piteratorunpack.KEY = KNOWN PNULL', 'piteratorunpack.CALL.SENT.SLOTS = eps',
            'pcallcontext_saved.TARGET = UNPACK_ITERATOR_TARGET n_data porigin_method',
            'pcallcontext_saved.RECEIVER = (n_data)',
            '$call_receiver_roots(pcallcontext_saved) = eps',
            '$heap_count(HOBJECT n_data, $call_context_roots((pcallcontext_saved))) = 0',
            '$iterator_unpack_frame(S_view, pcallcontext_saved, pframe_unpack)',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "key")',
            '$heap_count(HOBJECT n_data, $task_nodes(ITERATOR_UNPACK piteratorunpack "key")) = 2',
            *ADMISSION, *ZERO, 'S_zero.OBJECTS[n_fiber] = FIBER pfiber',
        ],
    },
    'parked-key-rejects-line-forgery-and-duplicate-real-marker': {
        'source': SOURCES['iterator-call-unpack-key-parks-before-send'],
        'stage': KEY_PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pcallcontext_bad = pcallcontext_saved[.LINE = $(pcallcontext_saved.LINE + 1)]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_bad)]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
            'pframe_duplicate = pframe_unpack[.TODO = '
            '(ITERATOR_UNPACK piteratorunpack "key") :: '
            '(ITERATOR_UNPACK piteratorunpack "key") :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'byref-warning-dispatch-authenticates-parameter-line-and-level': {
        'source': SOURCES['iterator-call-unpack-byref-warning-live-reference'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*'),
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            'S.STORE[n_value] = DEFINED (PINT 7)',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 0',
            '$iterator_unpack_scalar_operand(S, piteratorunpack.CURRENT)',
            *ADMISSION, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"',
            'perrorcall.SITE = porigin_site',
            '$unpack_origin(S_one, piteratorunpack.CALL) = (porigin_site)',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 18',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 1 of '
            'CallUnpackWarningRefTarget20() by unpacking a Traversable, passing by-value instead")',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 18',
            '$error_call_valid(S_one, perrorcall)',
            '$useriter_task_ids(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_value, $task_nodes(perrorcall.RESUME)) = 1',
            'perrorcall_bad = perrorcall[.LEVEL = 512]',
            'S_bad = S_one[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S_one)',
            '~$error_call_valid(S_bad, perrorcall_bad)', '~$call_descriptors_valid(S_bad)',
            'perrorcall_wrong = perrorcall[.LINE = 19]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 19]',
            'S_wrong = S_one[.TODO = (ERROR_HANDLER_INVOKE perrorcall_wrong) :: ptask_tail*]',
            '$heap_graph(S_wrong) = $heap_graph(S_one)',
            '~$error_call_valid(S_wrong, perrorcall_wrong)',
            '~$call_descriptors_valid(S_wrong)', *POST,
        ],
    },
    'byref-reference-rereads-handler-write-into-fresh-private-cell': {
        'source': SOURCES['iterator-call-unpack-byref-warning-live-reference'],
        'stage': BYREF,
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            '$iterator_unpack_result_valid(S, piteratorunpack, "byref")',
            'n_private = |S.STORE|', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_value)]',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'n_private =/= n_value', 'S_one.STORE[n_private] = DEFINED (PINT 9)',
            'n_private <- S_one.REFCELLS',
            'S_one.STORE[n_value] = DEFINED (PINT 9)',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$heap_count(HCELL n_private, $tasks_nodes(S_one.TODO)) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'byref-copied-current-keeps-seven-in-fresh-cell-after-handler-write': {
        'source': SOURCES['iterator-call-unpack-byref-warning-copied-current'],
        'stage': BYREF,
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = KNOWN (PINT 7)',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            'n_private = |S.STORE|', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'n_private =/= n_value', 'S_one.STORE[n_private] = DEFINED (PINT 7)',
            'S_one.STORE[n_value] = DEFINED (PINT 9)',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL', *POST,
        ],
    },
    'operational-warning-clean-retains-one-cursor-and-cache-owner': {
        'source': SOURCES['iterator-call-unpack-byref-warning-live-reference'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            'S.STORE[n_value] = DEFINED (PINT 9)', '$destructor_operational(S)',
            '$error_cleanup_valid(S, perrorcall)',
            '$useriter_task_ids(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_value, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = perrorcall.RESUME :: ptask_tail*',
            '$useriter_tasks_ids(S_one.TODO) = [n_cursor]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2', *POST,
        ],
    },
    'parked-warning-keeps-raw-reference-data-input-and-handler-context': {
        'source': SOURCES['iterator-call-unpack-byref-warning-handler-parks'],
        'stage': WARNING_PARK,
        'checks': [
            *PARK_VIEW, 'piteratorunpack.CURRENT = REFERENCE n_value',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            '$error_context_valid(S_view, pcallcontext_saved)',
            '$error_entered_call_valid(S_scope, perrorcall)',
            'pcallcontext_saved.LINE = 19', 'perrorcall.LINE = 19',
            'pcallcontext_saved.CALLSITE = (perrorcall.SITE)',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$heap_count(HCELL n_value, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_value) = 2',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
            *ADMISSION, *ZERO, 'S_zero.OBJECTS[n_fiber] = FIBER pfiber',
        ],
    },
    'parked-warning-rejects-coherent-line-shift-and-duplicate-wrapper': {
        'source': SOURCES['iterator-call-unpack-byref-warning-handler-parks'],
        'stage': WARNING_PARK,
        'checks': [
            *PARK_VIEW, 'piteratorunpack.CURRENT = REFERENCE n_value', *ADMISSION,
            'piteratorunpack_bad = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.LINE = 20]]',
            'perrorcall_bad = perrorcall[.LINE = 20]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 20]'
            '[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
            'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_saved[.LINE = 20])]'
            '[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
            'pframe_duplicate = pframe_unpack[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '$heap_owners($heap_graph(S_duplicate), HCELL n_value) = 3',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'thrown-warning-discards-cursor-and-preserves-original-exception': {
        'source': SOURCES['iterator-call-unpack-byref-warning-handler-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: '
                  'ptask_tail* -- if S.CURRENT = eps -- if perrorcall.RESUME = '
                  'ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            *HEADER, *TEMP, *FAILURE, 'piteratorunpack.CURRENT = REFERENCE n_value',
            'S.STORE[n_value] = DEFINED (PINT 9)', 'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_count(HCELL n_value, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 2',
            'S_one.STORE[n_value] = DEFINED (PINT 9)', '$throwable_live(S_one, n_error)',
            'S_one.EVENTS = S.EVENTS', *POST,
            '$heap_count(HOBJECT n_error, $tasks_nodes(S_one.TODO)) = 1',
        ],
    },
    'thrown-warning-reaches-real-cache-before-data-and-input-release': {
        'source': SOURCES['iterator-call-unpack-byref-warning-handler-throws'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.PENDING = (n_error) '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref" '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_value), '
                  'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data)]'),
        'checks': [
            *FAILURE, 'S.STORE[n_value] = DEFINED (PINT 9)',
            'S.ITERATORS = eps', 'S.CURRENT = eps',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$heap_count(HCELL n_value, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 2',
            '$heap_owners($heap_graph(S), HCELL n_value) = 2',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION,
            'pdestructionoperation.CALLER = S.CURRENT',
            'pdestructionoperation.ORIGIN = S.ORIGIN',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
        ],
    },
    'named-variadic-warning-uses-second-argument-and-a-fresh-extra-cell': {
        'source': SOURCES['iterator-call-unpack-named-variadic-byref-warning'],
        'stage': BYREF,
        'checks': [
            *HEADER, *TEMP, 'piteratorunpack.CURRENT = REFERENCE n_value',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("label")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_EXTRA ($ptascii("label"))',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 11))]',
            'piteratorunpack.CALL.SENT.NAMED = eps',
            '$unpack_line(S, piteratorunpack.CALL) = 24',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 2 of '
            'callUnpackNamedVariadicRefTarget20() by unpacking a Traversable, passing by-value instead")',
            'n_private = |S.STORE|', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_value)]',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 11))]',
            'piteratorunpack_next.CALL.SENT.NAMED = [($ptascii("label"), REFERENCE n_private)]',
            'S_one.STORE[n_private] = DEFINED (PINT 9)', 'n_private =/= n_value',
            'piteratorunpack_next.NAMED',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
}


KEY_ABORT_SOURCE = SOURCES['iterator-call-unpack-invalid-key-destructor-throws']
KEY_ABORT_JOBS = '[DESTRUCTION_VALUE (HOBJECT n_key), DESTRUCTION_VALUE (HOBJECT n_current), DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data)]'
KEY_ABORT_EVENTS = '[OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("K|"), OUTPUT $ptascii("J|")]'

CASES.update({
    'invalid-key-abort-operation-owns-error-and-authenticates-nonowning-source': {
        'source': KEY_ABORT_SOURCE,
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (ITERATOR_UNPACK piteratorunpack "error") '
                  ':: ptask_tail* -- if piteratorunpack.KEY = KNOWN (POBJECT n_key) '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current)'),
        'checks': [
            *HEADER, *TEMP,
            'n_key =/= n_current', 'n_current =/= n_data',
            '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            'piteratorunpack.CALL.SENT.NAMED = eps',
            '$string_bytes($throwable_field(S, n_error, "message")) = '
            '($ptascii("Keys must be of type int|string during argument unpacking"))',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = ' + KEY_ABORT_JOBS,
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error"',
            *OP_AFTER,
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'piteratorunpack_bad = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.LINE = $(piteratorunpack.CALL.LINE + 1)]]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack_bad "error"]',
            'S_bad = S_one[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: '
            'S.DESTRUCTION.OPERATIONS][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S_one)',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)',
            'piteratorunpack_foreign = piteratorunpack[.INPUT = KNOWN (POBJECT n_current)]',
            'pdestructionoperation_foreign = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack_foreign "error"]',
            'S_foreign = S_one[.DESTRUCTION.OPERATIONS = pdestructionoperation_foreign :: '
            'S.DESTRUCTION.OPERATIONS][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_foreign) :: ptask_tail*]',
            '$heap_graph(S_foreign) = $heap_graph(S_one)',
            '~$eager_operation_source_valid(S_foreign, pdestructionoperation_foreign)',
            '~$call_descriptors_valid(S_foreign)',
            *POST,
        ],
    },
    'replacement-key-exception-keeps-cache-and-data-retirement-pending': {
        'source': KEY_ABORT_SOURCE,
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                  '-- if pdestructionoperation.PENDING = (n_error) '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current) '
                  '-- if piteratorunpack.KEY = KNOWN (POBJECT n_key) '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_current), '
                  'DESTRUCTION_VALUE (HOBJECT piteratorunpack.OBJECT), '
                  'DESTRUCTION_VALUE (HOBJECT piteratorunpack.OBJECT)]'),
        'checks': [
            *FAILURE, 'n_data = piteratorunpack.OBJECT',
            'S.EVENTS = ' + KEY_ABORT_EVENTS,
            'S.ITERATORS = eps', 'S.CURRENT = eps',
            '$throwable_field(S, n_error, "previous") = POBJECT n_previous',
            'S.OBJECTS[n_previous] = THROWABLE pthrowable_previous',
            'pthrowable_previous.KIND = "Error"',
            '$string_bytes($throwable_field(S, n_previous, "message")) = '
            '($ptascii("Keys must be of type int|string during argument unpacking"))',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S.TODO)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_previous) = 1',
            '$heap_count(HOBJECT n_current, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 2',
            'n_key <- S.DESTRUCTION.CALLED', '~(n_current <- S.DESTRUCTION.CALLED)',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)',
            *ADMISSION, *ZERO,
        ],
    },
    'retired-data-keeps-source-receipt-valid-before-original-exception-search': {
        'source': KEY_ABORT_SOURCE,
        'stage': ('S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                  '-- if pdestructionoperation.PENDING = (n_error)'),
        'checks': [
            *FAILURE, 'n_data = piteratorunpack.OBJECT',
            'S.EVENTS = ' + KEY_ABORT_EVENTS[:-1] + ', OUTPUT $ptascii("D|"), OUTPUT $ptascii("I|")]',
            'S.ITERATORS = eps', 'S.CURRENT = eps',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            *ADMISSION,
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.INDEX = $(piteratorunpack.CALL.INDEX + 1)]] "error"]',
            'S_bad = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: '
            'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)',
            'pdestructionoperation_mode = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack[.INPUT = KNOWN PNULL] "error"]',
            'S_mode = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_mode :: '
            'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_mode) :: ptask_tail*]',
            '$heap_graph(S_mode) = $heap_graph(S)',
            '~$eager_operation_source_valid(S_mode, pdestructionoperation_mode)',
            '~$call_descriptors_valid(S_mode)',
            *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S_one.TODO)) = 1',
            '$throwable_live(S_one, n_error)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 0',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys(), 'unknown Iterator unpack state case'
    review.ROOT = ROOT
    review.CASES = CASES
    passed = True
    for name in args.case or list(CASES):
        passed = review.run([name])
        assert all(path.read_bytes() == data for path, data in INPUT_BYTES.items()), \
            'Iterator unpack review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
