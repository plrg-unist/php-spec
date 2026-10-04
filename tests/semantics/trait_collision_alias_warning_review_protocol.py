#!/usr/bin/env python3
"""A real private-final alias warning stays ahead of data-handler delivery."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_alias_warning_success_review_cases.json')
SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source']
CASES = {
    'concrete-private-final-warning-and-data-notice-have-authentic-phase-order': {
        'source': SOURCE,
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': [
            'S.CURRENT = eps',
            'S.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            '$method_named(pclassdesc_c.METHODS, $ptascii("g")) = (pmethoddesc_g)',
            'pmethoddesc_g.OWNER = porigin_c',
            'pmethoddesc_g.VISIBILITY = PROPERTY_PRIVATE',
            'pmethoddesc_g.FINAL',
            'pmethoddesc_g.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_c porigin_method_source ($ptascii("g"))',
            'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_alias), (TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_data)]',
            'pfdiagnostic_alias.LEVEL = 128',
            'pfdiagnostic_alias.SITE = porigin_c',
            'pfdiagnostic_alias.LINE = 5',
            'pfdiagnostic_data.LEVEL = 8192',
            'pfdiagnostic_data.SITE =/= porigin_c',
            'pfdiagnostic_data.LINE = 5',
            '~$error_handler_eligible(S, 128)',
            '$error_handler_eligible(S, 8192)',
            '$task_nodes(DECL_NOTICES pdeclnoticebatch) = eps',
            '$call_task_valid(S, DECL_NOTICES pdeclnoticebatch)',
            '$call_task_valid(S[.REPORTING = 0], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.SOURCES = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.CODE = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [pdeclnoticebatch.NOTICES[1], pdeclnoticebatch.NOTICES[0]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_alias[.LEVEL = 2])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_alias[.SITE = porigin_method_source])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_alias[.LINE = 6])), pdeclnoticebatch.NOTICES[1]]]))',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$call_descriptors_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
