#!/usr/bin/env python3
"""A genuine recursive lookup keeps two full cache rows and two array owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_cache_chain_review_cases.json')
SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source']

CASES = {
    'recursive-imported-array-caches-retain-two-owners': {
        'source': SOURCE,
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': [
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            '$call_descriptors_valid(S)',
            '$class_constant_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$call_task_valid(S, DECL_NOTICES pdeclnoticebatch)',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            '$class_constant_desc(pclassdesc_c.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            '$class_constant_desc(pclassdesc_c.CONSTANTS, $ptascii("Z")) = (pclassconstantdesc_z)',
            'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
            'pclassconstantdesc_z.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_z_source',
            'porigin_y_source =/= porigin_z_source',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_z)',
            'S.CLASSCONSTANTCACHE = [pdefaultcache_z, pdefaultcache_y]',
            'pdefaultcache_z.VALUE = PARRAY n_array',
            'pdefaultcache_y.VALUE = PARRAY n_array',
            'pdefaultcache_z.CLASS = pdefaultcache_y.CLASS',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
            '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc_z.ORIGIN) = (ptraitcachecause_z)',
            'ptraitcachecause_y.CLASS = porigin_c',
            'ptraitcachecause_z.CLASS = porigin_c',
            'ptraitcachecause_z.ROOT = ptraitcachecause_y.ROOT',
            'ptraitcachecause_z.TABLE = ptraitcachecause_y.TABLE',
            'ptraitcachecause_y.LOOKUPS = [ptraitcachecause_y.ROOT]',
            'ptraitcachecause_z.LOOKUPS = ptraitcachecause_y.LOOKUPS ++ [pclassconstantdesc_y.INITIALIZER]',
            '$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '$trait_cache_cause_valid(S, pclassconstantdesc_z.ORIGIN, ptraitcachecause_z)',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_z.ORIGIN, ptraitcachecause_z[.LOOKUPS = ptraitcachecause_y.LOOKUPS])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = ptraitcachecause_z.LOOKUPS])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_z.ORIGIN, ptraitcachecause_z[.LOOKUPS = ptraitcachecause_y.LOOKUPS ++ [pclassconstantdesc_z.INITIALIZER]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_y, pdefaultcache_z]])',
            '$heap_count(HARRAY n_array, $class_constant_roots(S.CLASSCONSTANTCACHE)) = 2',
            '$heap_count(HARRAY n_array, $class_static_roots(S.CLASSSTATICS)) = 0',
            '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_z)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 2',
            'S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$ppproperty_desc_at(pclassdesc_c.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
            '$class_static_at(S_done.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x)',
            'pclassstatic_x.STATE = PROP_VALUE (DIRECT (PARRAY n_x))',
            'n_x =/= n_array',
            'S_done.ARRAYS[n_x].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("W")))]',
            '$heap_owners($heap_graph(S_done), HARRAY n_x) = 1',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
