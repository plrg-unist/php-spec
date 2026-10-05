#!/usr/bin/env python3
"""Reached Error reports retain public caches and retire unpublished imports."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
ARRAY = HERE / 'trait_data_failed_cache_requestfatal_review_cases.json'
ERRORS = HERE / 'trait_data_failed_cache_error_cases.json'
ARRAY_SOURCE = json.loads(ARRAY.read_text())['cases'][0]['source']
IMPORT_SOURCE = next(row['source'] for row in json.loads(ERRORS.read_text())['cases']
                     if row['id'] == 'imported-cache-retired-after-later-endogenous-collision-error')

STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

BINDING = [
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
    'pclassdesc_c.ORIGIN = PORIGIN n_source pcpath_c',
    'pdeclcause = $declaration_cause(S)',
    'ptraitplan = $trait_plan(S, pclassdesc_c)',
    'ptraitfetch = $trait_fetch(S, ptraitplan.TRAITS, eps)',
    'ptraitfetch = TRAITFETCHED pclassdesc_traits*',
    'pclassdesc_traits* = [pclassdesc_t]',
    'S_link = $trait_fetched(S, pclassdesc_c, ptraitplan, ptraitfetch)',
    'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") preqbytes_fatal z_fatal',
    'z_fatal = pclassdesc_c.LINE',
    '~$iterator_notice_link_fatal(S_link.COMPLETION)',
    'S_link.TRACE = eps',
    'S_link.ERRORFATALTRACE = eps',
    'S_link.ERRORHANDLER = S.ERRORHANDLER',
    'S_link.ERRORORIGIN = $compiled_error_origin(S.ERRORORIGIN, STATICBYTES preqbytes_fatal z_fatal, n_source)',
    '$runtime_class_replay_fatal(S, S_link[.CLASSES = S.CLASSES], pclassdesc_c)',
    '$trait_failed_cache_ready(S, S_link)',
    '~$trait_failed_cache_ready(S, S_link[.COMPLETION = NORMAL])',
    '~$trait_failed_cache_ready(S, S_link[.COMPLETION = REQUESTFATAL $ptascii("Error") preqbytes_fatal z_fatal])',
    '~$trait_failed_cache_ready(S, S_link[.ERRORORIGIN = (porigin_t)])',
    'ptraceframe_wrong = {FILE $ptascii("forged.php"), LINE 1, FUNCTION $ptascii("forged"), CLASS eps, TYPE eps, ARGS eps, HASARGS false}',
    '~$trait_failed_cache_ready(S, S_link[.TRACE = [ptraceframe_wrong]])',
    '~$trait_failed_cache_ready(S, S_link[.ERRORFATALTRACE = [ptraceframe_wrong]])',
    'n_error = |S.OBJECTS|',
    'S_link.OBJECTS[n_error] = THROWABLE pthrowable_error',
    'pthrowable_error.KIND = "Error"',
    '~((HOBJECT n_error) <- S_link.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_link), HOBJECT n_error) = 0',
]

PAIR = [
    '~pclassconstantdesc_y.FOLDED',
    '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
    'S_link.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_y]',
    '$trait_cache_event_at(S_link.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
    'S_link.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN ptraitcachecause_y)]',
    'ptraitcachecause_y.CLASS = porigin_c',
    'ptraitcachecause_y.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause_y.USERPREFIX = |S.USERCONSTANTS|',
    '$trait_cache_cause_selected(S_link, ptraitcachecause_y) = (pclassconstantdesc_y)',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY])',
]

RESTORED = [
    'S_failed = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
    'S_failed.COMPLETION = S_link.COMPLETION',
    'S_failed.EVENTS = S_link.EVENTS',
    'S_failed.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause]',
    'S_failed.CLASSES = S.CLASSES',
    'S_failed.CLASSNAMES = S.CLASSNAMES',
    'S_failed.ERRORHANDLER = S.ERRORHANDLER',
    'S_failed.CURRENT = S.CURRENT',
    'S_failed.FRAMES = S.FRAMES',
    'S_failed.TRACE = eps',
    'S_failed.ERRORFATALTRACE = eps',
    '$iterator_notice_seeds(S_failed.TODO) = eps',
    '$class_named(S_failed.CLASSNAMES, $ptascii("c")) = eps',
    '$trait_failed_cache_index(S_failed.DECLARATIONS, porigin_c, 0) = (ptraitcachecause_y.PREFIX)',
    '$declaration_history_valid(S_failed)',
    '$call_descriptors_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$heap_valid($heap_graph(S_failed))',
    '$heap_owners($heap_graph(S_failed), HOBJECT n_error) = 0',
    '~$declaration_history_valid(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_t pdeclcause]])',
]

CASES = {
    'reported-error-keeps-one-public-array-cache-and-drops-throwable': {
        'source': ARRAY_SOURCE,
        'stage': STAGE,
        'checks': BINDING + [
            '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
            '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
            '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.OWNER = porigin_p',
            '$trait_failed_cache_keep(S, pclassconstantdesc_y.ORIGIN)',
        ] + PAIR + [
            'pdefaultcache_y.VALUE = PARRAY n_y',
            'pdefaultcache_y.CLASS = PVARRAY b_array ([(KINT 2048, PVSTRING b_string)])',
            'ptraitcachecause_y.TABLE = eps',
            'ptraitcachecause_y.LOOKUPS = [ptraitcachecause_y.ROOT]',
            'S_link.ARRAYS[n_y].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$heap_owners($heap_graph(S_link), HARRAY n_y) = 1',
            'S_link.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_y]',
        ] + RESTORED + [
            'S_failed.CLASSCONSTANTCACHE = S_link.CLASSCONSTANTCACHE',
            'S_failed.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY',
            '$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '~$class_constant_state_valid(S_failed[.DECLARATIONS = S.DECLARATIONS])',
            '$heap_count(HARRAY n_y, $class_constant_roots(S_failed.CLASSCONSTANTCACHE)) = 1',
            '$heap_count(HARRAY n_y, $pools_nodes(S_failed.POOLS)) = 0',
            '$heap_owners($heap_graph(S_failed), HARRAY n_y) = 1',
            'S_done = $drive(S_failed, 3000)',
            'S_done.COMPLETION = S_failed.COMPLETION',
            'S_done.ARRAYS[n_y].ITEMS = S_failed.ARRAYS[n_y].ITEMS',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            '$heap_owners($heap_graph(S_done), HARRAY n_y) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'reported-error-retires-full-import-cache-and-pending-throwable': {
        'source': IMPORT_SOURCE,
        'stage': STAGE,
        'checks': BINDING + [
            '$class_at(S_link.CLASSES, porigin_c) = (pclassdesc_composed)',
            '$class_constant_desc(pclassdesc_composed.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
            'pclassconstantdesc_y.OWNER = porigin_c',
            '~$trait_failed_cache_keep(S, pclassconstantdesc_y.ORIGIN)',
        ] + PAIR + [
            'pdefaultcache_y.VALUE = PINT 2048',
            'pdefaultcache_y.CLASS = PVSCALAR',
            'ptraitcachecause_y.TABLE = pclassdesc_composed.CONSTANTS',
        ] + RESTORED + [
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_failed.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            'S_failed.ALLOCATIONS = S.ALLOCATIONS',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTCACHE = [pdefaultcache_y]][.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY])',
            'S_done = $drive(S_failed, 3000)',
            'S_done.COMPLETION = S_failed.COMPLETION',
            'S_done.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_done.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
            '$class_named(S_done.CLASSNAMES, $ptascii("c")) = eps',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), ARRAY, ERRORS))
