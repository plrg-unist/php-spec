#!/usr/bin/env python3
"""Source-reached trait collision queues and authentic borrowed callback frames."""
from pathlib import Path
import json

import closure_call_protocol as protocol

DELIVERY = Path(__file__).with_name('trait_data_delivery_review_cases.json')
SCOPE = Path(__file__).with_name('trait_data_recording_scope_review_cases.json')
SOURCES = {row['id']: row['source'] for path in (DELIVERY, SCOPE)
           for row in json.loads(path.read_text())['cases']}
VALID = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$class_statics_valid(S)',
    '$heap_valid($heap_graph(S))',
]
DONE = [
    'S_done = $drive(S, 2000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$call_descriptors_valid(S_done)',
    '$declaration_history_valid(S_done)',
    '$class_constant_state_valid(S_done)',
    '$class_statics_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
]
CASES = {
    'published-collision-queue-requires-exact-member-effects-and-prefix': {
        'source': SOURCES['constant-then-property-recorded-warnings-see-replaced-handler'],
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': VALID + [
            'S.CURRENT = eps',
            'S.COMPLETION = NORMAL',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            'pdeclnoticebatch.SITE = porigin_c',
            'pdeclnoticebatch.LINE = pclassdesc_c.LINE',
            'pdeclnoticebatch.KIND = NOTICE_RUNTIME',
            'pdeclnoticebatch.CLASSES = [(porigin_c, n_prefix)]',
            'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_constant), (TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_property)]',
            'pfdiagnostic_constant.LEVEL = 8192',
            'pfdiagnostic_property.LEVEL = 8192',
            'pfdiagnostic_constant.SITE =/= pfdiagnostic_property.SITE',
            'pfdiagnostic_constant.LINE = pclassdesc_c.LINE',
            'pfdiagnostic_property.LINE = pclassdesc_c.LINE',
            '$trait_notice_plan(S, porigin_c, n_prefix, n_user) = (pdeclnoticebatch.NOTICES)',
            '$call_task_valid(S, DECL_NOTICES pdeclnoticebatch)',
            '$task_nodes(DECL_NOTICES pdeclnoticebatch) = eps',
            '$trait_notice_plan(S, porigin_c, |S.DECLARATIONS|, n_user) = eps',
            '$trait_notice_plan(S, porigin_c, n_prefix, $(|S.USERCONSTANTS| + 1)) = eps',
            '~$call_task_valid(S[.SOURCES = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.CODE = eps], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S[.DECLARATIONS = S.DECLARATIONS[0:n_prefix]], DECL_NOTICES pdeclnoticebatch)',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.SITE = pfdiagnostic_constant.SITE]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.INDEX = 3]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_property), (TRAIT_DATA_NOTICE porigin_c n_prefix n_user pfdiagnostic_constant)]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_constant[.MESSAGE = $ptascii("forged")])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_constant[.SITE = porigin_c])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_constant[.LEVEL = 2])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c n_prefix n_user (pfdiagnostic_constant[.LINE = $(pfdiagnostic_constant.LINE + 1)])), pdeclnoticebatch.NOTICES[1]]]))',
            '~$call_descriptors_valid(S[.TODO = (DECL_NOTICES pdeclnoticebatch) :: (DECL_NOTICES pdeclnoticebatch) :: ptask_tail*])',
        ] + DONE,
    },
    'recorded-collision-callback-keeps-real-Q-R-capture-and-emitter': {
        'source': SOURCES['recorded-collision-handler-keeps-real-lexical-and-called-maker-scope'],
        'stage': ('S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emitter* '
                  '-- if perrorcall.RESUME = DECL_NOTICE_RESUME pdeclnoticebatch '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': VALID + [
            '$call_current_valid(S)',
            '$call_frames_valid(S, S.FRAMES)',
            '$error_context_valid(S, pcallcontext)',
            'pcallcontext.ARGC = 4',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("Q"))) = (porigin_q)',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("R"))) = (porigin_r)',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            'pcallcontext.LEXICAL_CLASS = (porigin_q)',
            'pcallcontext.CALLED_CLASS = (porigin_r)',
            'pframe.CONTEXT = (pcallcontext_emitter)',
            'pcallcontext_emitter.NAME = $ptascii("linkClass")',
            'pcallcontext_emitter.LEXICAL_CLASS = eps',
            'pcallcontext_emitter.CALLED_CLASS = eps',
            'pdeclnoticebatch.SITE = porigin_c',
            'pdeclnoticebatch.INDEX = 1',
            'perrorcall.SITE = porigin_c',
            'perrorcall.LEVEL = 8192',
            'pframe.ORIGIN = (porigin_c)',
            'S_emitter = $api_saved_frame_scope($constant_frame_scope(S, pframe, pframe_tail*), pframe, pframe_tail*)',
            '$error_call_valid(S_emitter, perrorcall)',
            '$call_task_valid(S_emitter, ERROR_HANDLER_RESULT perrorcall)',
            '~$error_call_valid(S_emitter, perrorcall[.SITE = porigin_q])',
            '~$error_call_valid(S_emitter, perrorcall[.LEVEL = 2])',
            '~$error_call_valid(S_emitter, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
            '~$error_call_valid(S_emitter, perrorcall[.RESUME = DECL_NOTICE_RESUME (pdeclnoticebatch[.INDEX = 0])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_c)])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_c)])])',
            '~$call_current_valid(S[.FRAMES = pframe[.ORIGIN = (porigin_q)] :: pframe_tail*])',
            '~$call_current_valid(S[.FRAMES = pframe[.TODO = ptask_emitter*] :: pframe_tail*])',
        ] + DONE,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), DELIVERY, SCOPE))
