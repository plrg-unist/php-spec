#!/usr/bin/env python3
"""A real dynamic-key public FCC array keeps its cache owner through static COW."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_data_public_object_dependency_cases.json'
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'property-collision-keeps-public-private-fcc-array-cache-and-cow')

CASES = {
    'public-fcc-array-proves-runtime-key-and-keeps-cache-object-through-static-cow': {
        'source': SOURCE,
        'stage': ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin_c) '
                  '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
                  '-- if pclassdesc_c.NAME = $ptascii("C")'),
        'checks': [
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
            '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
            '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            'S_after = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
            'S_after.COMPLETION = NORMAL',
            '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'pdefaultcache_y.VALUE = PARRAY n_array',
            'pdefaultcache_y.CLASS = PVARRAY b_array ([(KINT 2048, PVCLOSURE n_fcc porigin_site)])',
            'S_after.ARRAYS[n_array].ITEMS = [ENTRY (KINT 2048) (DIRECT (POBJECT n_fcc))]',
            'n_fcc = |S.OBJECTS|',
            '$constant_callable_record(S_after.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
            'pconstantclosure.DECL = pclassconstantdesc_y.ORIGIN',
            'pconstantclosure.SITE = porigin_site',
            'pconstantclosure.PREFIX = |S.DECLARATIONS|',
            '$constant_callable_record_valid(S_after, pconstantclosure)',
            '$trait_cache_event_at(S_after.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause)',
            'ptraitcachecause.CLASS = porigin_c',
            'ptraitcachecause.PREFIX = |S.DECLARATIONS|',
            'ptraitcachecause.USERPREFIX = |S.USERCONSTANTS|',
            'porigin_item = $constant_child(pclassconstantdesc_y.INITIALIZER, [PCFIELD 0, PCINDEX 0])',
            'porigin_key = $constant_child(porigin_item, [PCFIELD 0])',
            '$compiled_read(S_after, porigin_key) = eps',
            '$trait_cache_flow_context(S_after, porigin_key, porigin_p, ptraitcachecause.PREFIX) = ((pclassconstantdesc_y, ptraitcachecause))',
            '$trait_cache_source_key(S_after, porigin_key, porigin_p, ptraitcachecause.PREFIX) = (PINT 2048)',
            '$trait_cache_source_key(S_after, porigin_key, porigin_c, ptraitcachecause.PREFIX) = eps',
            '$trait_cache_source_key(S_after, porigin_key, porigin_p, 0) = eps',
            '$constant_callable_cache_valid(S_after, pclassconstantdesc_y, pdefaultcache_y.CLASS, ptraitcachecause.PREFIX)',
            '~$constant_callable_cache_valid(S_after, pclassconstantdesc_y, PVARRAY b_array ([(KINT 0, PVCLOSURE n_fcc porigin_site)]), ptraitcachecause.PREFIX)',
            '$heap_count(HARRAY n_array, $class_constant_roots(S_after.CLASSCONSTANTCACHE)) = 1',
            '$heap_count(HOBJECT n_fcc, $class_constant_roots(S_after.CLASSCONSTANTCACHE)) = 0',
            '$heap_owners($heap_graph(S_after), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_after), HOBJECT n_fcc) = 1',
            '$call_descriptors_valid(S_after)',
            '$declaration_history_valid(S_after)',
            '$class_constant_state_valid(S_after)',
            '$constant_callable_records_valid(S_after, S_after.CONSTANTCLOSURES)',
            '$heap_valid($heap_graph(S_after))',
            'S_done = $drive(S_after, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'S_done.ARRAYS[n_array].ITEMS = S_after.ARRAYS[n_array].ITEMS',
            '$lookup(S_done.ENV, $ptascii("a")) = (n_cell_a)',
            'S_done.STORE[n_cell_a] = DEFINED (PARRAY n_array)',
            '$class_at(S_done.CLASSES, porigin_c) = (pclassdesc_composed)',
            '$ppproperty_desc_at(pclassdesc_composed.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
            '$class_static_at(S_done.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x)',
            'pclassstatic_x.STATE = PROP_VALUE (DIRECT (PARRAY n_copy))',
            'n_copy =/= n_array',
            'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 2048) (DIRECT PNULL)]',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S_done), HARRAY n_copy) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_fcc) = 1',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
            '$call_descriptors_valid(S_done)',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$class_statics_valid(S_done)',
            '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
