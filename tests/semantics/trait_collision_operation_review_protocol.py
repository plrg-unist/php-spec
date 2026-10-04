#!/usr/bin/env python3
"""A genuine recorded key warning keeps live settings and real array owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_recorded_operation_cases.json')
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'recorded-float-key-deprecation-ignores-live-display-and-mask')
CASES = {
    'recorded-key-warning-is-independent-of-display-and-keeps-pool-static-owners': {
        'source': SOURCE,
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': [
            'S.CURRENT = eps',
            'S.REPORTING = 0',
            'S.DISPLAYINI = ($ptascii("0"))',
            'S.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$class_statics_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            '$ppproperty_desc_at(pclassdesc_c.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
            'ppropertydesc_x.DEFAULT = PROP_STORED porigin_default',
            '$pool_value(S.POOLS, porigin_default) = (PARRAY n_array)',
            '$class_static_at(S.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x)',
            'pclassstatic_x.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 1',
            '$heap_count(HARRAY n_array, $class_static_roots(S.CLASSSTATICS)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            '$task_nodes(DECL_NOTICES pdeclnoticebatch) = eps',
            'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_name), (TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_key)]',
            'pfdiagnostic_name.LEVEL = 8192',
            'pfdiagnostic_key.LEVEL = 8192',
            'pfdiagnostic_name.SITE =/= pfdiagnostic_key.SITE',
            '$call_task_valid(S, DECL_NOTICES pdeclnoticebatch)',
            '$call_task_valid(S[.REPORTING = 32767][.DISPLAYINI = ($ptascii("stderr"))][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.SOURCES = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.CODE = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [pdeclnoticebatch.NOTICES[0], (TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_key[.SITE = pfdiagnostic_name.SITE]))]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [pdeclnoticebatch.NOTICES[0], (TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_key[.LEVEL = 2]))]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [pdeclnoticebatch.NOTICES[0], (TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_key[.MESSAGE = $ptascii("forged")]))]]))',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$call_descriptors_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$class_statics_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            '$class_static_at(S_done.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x)',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 2',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
