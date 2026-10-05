#!/usr/bin/env python3
"""Reached failed links retain published caches and retire unpublished imports."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
PUBLIC = HERE / 'trait_data_failed_cache_review_cases.json'
IMPORTED = HERE / 'trait_data_collision_cache_array_review_cases.json'
PUBLIC_SOURCE = json.loads(PUBLIC.read_text())['cases'][0]['source']
IMPORTED_SOURCE = next(row['source'] for row in json.loads(IMPORTED.read_text())['cases']
                       if row['id'] == 'imported-array-dependency-fill-survives-later-strict-collision-fatal')

STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

BEFORE = [
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    'ptraitplan = $trait_plan(S, pclassdesc_c)',
    'ptraitfetch = $trait_fetch(S, ptraitplan.TRAITS, eps)',
    'ptraitfetch = TRAITFETCHED pclassdesc_traits*',
    'pclassdesc_traits* = [pclassdesc_t]',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
    'pdeclcause = $declaration_cause(S)',
    'S_link = $trait_fetched(S, pclassdesc_c, ptraitplan, ptraitfetch)',
    'S_link.COMPLETION = STATICBYTES preqbytes_fatal z_fatal',
    'z_fatal = pclassdesc_c.LINE',
    '$trait_failed_cache_ready(S, S_link)',
    '$trait_failed_cache_class(S, S_link) = (porigin_c)',
]

PAIR = [
    '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
    'S_link.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_y]',
    'pdefaultcache_y.VALUE = PARRAY n_y',
    'pdefaultcache_y.CLASS = PVARRAY b_array ([(KINT 2048, PVSTRING b_string)])',
    'S_link.ARRAYS[n_y].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
    '$trait_cache_event_at(S_link.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
    'S_link.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN ptraitcachecause_y)]',
    'ptraitcachecause_y.CLASS = porigin_c',
    'ptraitcachecause_y.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause_y.USERPREFIX = |S.USERCONSTANTS|',
    'ptraitcachecause_y.LOOKUPS = [ptraitcachecause_y.ROOT]',
    '$trait_cache_cause_selected(S_link, ptraitcachecause_y) = (pclassconstantdesc_y)',
    '~$trait_cache_cause_valid(S_link, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
    '$heap_count(HARRAY n_y, $class_constant_roots(S_link.CLASSCONSTANTCACHE)) = 1',
    '$heap_owners($heap_graph(S_link), HARRAY n_y) = 1',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY])',
    '~$trait_failed_cache_ready(S, S_link[.COMPLETION = NORMAL])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN (ptraitcachecause_y[.CLASS = porigin_t]))]])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN (ptraitcachecause_y[.PREFIX = $nabs($(|S.DECLARATIONS| + 1))]))]])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN (ptraitcachecause_y[.USERPREFIX = $nabs($(|S.USERCONSTANTS| + 1))]))]])',
]

RESTORED = [
    'S_restored = $trait_restore(S, S_link)',
    '$iterator_notice_seeds(S_restored.TODO) =/= eps',
    '~$call_tasks_valid(S_restored, S_restored.TODO)',
    'S_failed = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
    '$iterator_notice_seeds(S_failed.TODO) = eps',
    'S_failed.COMPLETION = S_link.COMPLETION',
    'S_failed.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause]',
    'S_failed.CLASSES = S.CLASSES',
    'S_failed.CLASSNAMES = S.CLASSNAMES',
    'S_failed.LINKEDPARENTS = S.LINKEDPARENTS',
    'S_failed.LINKEDINTERFACES = S.LINKEDINTERFACES',
    'S_failed.CLASSSTATICS = S.CLASSSTATICS',
    'S_failed.ERRORHANDLER = S.ERRORHANDLER',
    'S_failed.CURRENT = S.CURRENT',
    'S_failed.FRAMES = S.FRAMES',
    '$class_named(S_failed.CLASSNAMES, $ptascii("c")) = eps',
    '$iterator_notice_publication_index(S_failed.DECLARATIONS, porigin_c, 0) = eps',
    '$trait_failed_cache_index(S_failed.DECLARATIONS, porigin_c, 0) = (ptraitcachecause_y.PREFIX)',
    '$declaration_history_valid(S_failed)',
    '$call_descriptors_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$heap_valid($heap_graph(S_failed))',
    '~$declaration_history_valid(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_t pdeclcause]])',
    '~$declaration_history_valid(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c (pdeclcause[.UNIT = $nabs($(|S.SOURCES| + 1))])]])',
]

CASES = {
    'published-array-cache-survives-failed-link-and-remains-one-owner': {
        'source': PUBLIC_SOURCE,
        'stage': STAGE,
        'checks': BEFORE + [
            '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
            '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
            '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.OWNER = porigin_p',
            '~pclassconstantdesc_y.FOLDED',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            '$trait_failed_cache_keep(S, pclassconstantdesc_y.ORIGIN)',
            '~$trait_failed_cache_keep(S[.CLASSNAMES = eps], pclassconstantdesc_y.ORIGIN)',
        ] + PAIR + [
            'ptraitcachecause_y.TABLE = eps',
            '~$trait_failed_cache_ready(S, S_link[.CLASSES = $trait_class_set(S_link.CLASSES, pclassdesc_p[.CONSTANTS = [pclassconstantdesc_y[.TYPE = eps]]])])',
        ] + RESTORED + [
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_y]',
            'S_failed.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY',
            '$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '$trait_cache_notice_prefix(S_failed, S_failed.CLASSCONSTANTHISTORY, porigin_c, ptraitcachecause_y.PREFIX) = eps',
            '$heap_count(HARRAY n_y, $class_constant_roots(S_failed.CLASSCONSTANTCACHE)) = 1',
            '$heap_count(HARRAY n_y, $pools_nodes(S_failed.POOLS)) = 0',
            '$heap_owners($heap_graph(S_failed), HARRAY n_y) = 1',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.CLASS = porigin_p])',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.ROOT = porigin_c])',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.TABLE = [pclassconstantdesc_y]])',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = eps])',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = [pclassconstantdesc_y.INITIALIZER]])',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.PREFIX = $nabs($(ptraitcachecause_y.PREFIX + 1))])',
            '~$class_constant_state_valid(S_failed[.DECLARATIONS = S.DECLARATIONS])',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTCACHE = eps])',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTCACHE = [pdefaultcache_y, pdefaultcache_y]])',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTCACHE = [pdefaultcache_y[.VALUE = PINT 0]]])',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY])',
            'S_done = $drive(S_failed, 3000)',
            'S_done.COMPLETION = REQUESTFATAL ptbytes_fatal_class preqbytes_fatal z_fatal',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$class_named(S_done.CLASSNAMES, $ptascii("c")) = eps',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'S_done.ARRAYS[n_y].ITEMS = S_failed.ARRAYS[n_y].ITEMS',
            '$heap_owners($heap_graph(S_done), HARRAY n_y) = 1',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'failed-import-retires-array-cache-and-its-source-event': {
        'source': IMPORTED_SOURCE,
        'stage': STAGE,
        'checks': BEFORE + [
            '$class_at(S_link.CLASSES, porigin_c) = (pclassdesc_composed)',
            '$class_constant_desc(pclassdesc_composed.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
            'pclassconstantdesc_y.OWNER = porigin_c',
            '~pclassconstantdesc_y.FOLDED',
            '~$trait_failed_cache_keep(S, pclassconstantdesc_y.ORIGIN)',
        ] + PAIR + [
            'ptraitcachecause_y.TABLE = pclassdesc_composed.CONSTANTS',
        ] + RESTORED + [
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_failed.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
            '$default_cache_at(S_failed.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            '$trait_cache_event_at(S_failed.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = eps',
            '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '~((HARRAY n_y) <- S_failed.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_failed), HARRAY n_y) = 0',
            'S_failed.ALLOCATIONS = S.ALLOCATIONS',
            '~$class_constant_state_valid(S_failed[.CLASSCONSTANTCACHE = [pdefaultcache_y]][.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY])',
            'S_done = $drive(S_failed, 2000)',
            'S_done.COMPLETION = STATICBYTES preqbytes_fatal z_fatal',
            'S_done.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_done.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
            '$heap_owners($heap_graph(S_done), HARRAY n_y) = 0',
            '$class_named(S_done.CLASSNAMES, $ptascii("c")) = eps',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), PUBLIC, IMPORTED))
