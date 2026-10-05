#!/usr/bin/env python3
"""A real failed trait use retains only its published dependency owner."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_data_failed_trait_cache_cases.json'
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'published-array-cache-survives-raw-trait-composition-error')

CASES = {
    'failed-trait-use-keeps-published-array-with-authentic-kind-and-cause': {
        'source': SOURCE,
        'stage': ('S.TODO = (STMT (NStmtTrait phpType14 phpType3 phpType23 metadata)) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin_u) '
                  '-- if $class_at(S.CLASSES, porigin_u) = (pclassdesc_u) '
                  '-- if pclassdesc_u.NAME = $ptascii("U")'),
        'checks': [
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$class_named(S.CLASSNAMES, $ptascii("u")) = eps',
            'pclassdesc_u.KIND = "trait"',
            '$trait_failed_cache_source(S, pclassdesc_u)',
            '~$trait_failed_cache_source(S, pclassdesc_u[.KIND = "class"])',
            '~$trait_failed_cache_source(S, pclassdesc_u[.KIND = "interface"])',
            '~$trait_failed_cache_source(S[.SOURCES = eps], pclassdesc_u)',
            '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
            '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
            '$trait_failed_cache_source(S, pclassdesc_p)',
            '~$trait_failed_cache_source(S, pclassdesc_p[.KIND = "trait"])',
            '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.OWNER = porigin_p',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            'pdeclcause = $declaration_cause(S)',
            'ptraitplan = $trait_plan(S, pclassdesc_u)',
            'ptraitfetch = $trait_fetch(S, ptraitplan.TRAITS, eps)',
            'ptraitfetch = TRAITFETCHED pclassdesc_traits*',
            '|pclassdesc_traits*| = 1',
            'S_link = $trait_fetched(S, pclassdesc_u, ptraitplan, ptraitfetch)',
            'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") preqbytes_fatal pclassdesc_u.LINE',
            '$trait_failed_cache_ready(S, S_link)',
            '$trait_failed_cache_class(S, S_link) = (porigin_u)',
            '$runtime_class_replay_fatal(S, S_link[.CLASSES = S.CLASSES], pclassdesc_u)',
            '~$trait_failed_cache_ready(S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.KIND = "class"])], S_link)',
            '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'pdefaultcache_y.VALUE = PARRAY n_y',
            'S_link.ARRAYS[n_y].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$heap_owners($heap_graph(S_link), HARRAY n_y) = 1',
            '$trait_cache_event_at(S_link.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
            'ptraitcachecause_y.CLASS = porigin_u',
            'ptraitcachecause_y.PREFIX = |S.DECLARATIONS|',
            'ptraitcachecause_y.USERPREFIX = |S.USERCONSTANTS|',
            'ptraitcachecause_y.TABLE = eps',
            'ptraitcachecause_y.LOOKUPS = [ptraitcachecause_y.ROOT]',
            '$trait_cache_cause_selected(S_link, ptraitcachecause_y) = (pclassconstantdesc_y)',
            'S_failed = $activate_class(S[.TODO = ptask_tail*], pclassdesc_u)',
            'S_failed.COMPLETION = S_link.COMPLETION',
            'S_failed.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_u pdeclcause]',
            'S_failed.CLASSES = S.CLASSES',
            'S_failed.CLASSNAMES = S.CLASSNAMES',
            '$class_named(S_failed.CLASSNAMES, $ptascii("u")) = eps',
            '$trait_failed_cache_index(S_failed.DECLARATIONS, porigin_u, 0) = (ptraitcachecause_y.PREFIX)',
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_y]',
            'S_failed.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY',
            '$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '$heap_count(HARRAY n_y, $class_constant_roots(S_failed.CLASSCONSTANTCACHE)) = 1',
            '$heap_owners($heap_graph(S_failed), HARRAY n_y) = 1',
            '$declaration_history_valid(S_failed)',
            '$call_descriptors_valid(S_failed)',
            '$class_constant_state_valid(S_failed)',
            '$heap_valid($heap_graph(S_failed))',
            '~$class_constant_state_valid(S_failed[.DECLARATIONS = S.DECLARATIONS])',
            '~$declaration_history_valid(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_p pdeclcause]])',
            '~$declaration_history_valid(S_failed[.CLASSES = $trait_class_set(S_failed.CLASSES, pclassdesc_u[.KIND = "class"])])',
            'S_done = $drive(S_failed, 3000)',
            'S_done.COMPLETION = S_failed.COMPLETION',
            'S_done.ARRAYS[n_y].ITEMS = S_failed.ARRAYS[n_y].ITEMS',
            '$class_named(S_done.CLASSNAMES, $ptascii("u")) = eps',
            '$heap_owners($heap_graph(S_done), HARRAY n_y) = 1',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
