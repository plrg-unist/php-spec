#!/usr/bin/env python3
"""A reached callback keeps the sole precomputed RHS until its opcode finishes."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_property_rhs_review_cases.json')
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'precomputed-array-rhs-installed-before-handler-exception-propagates')

CASES = {
    'abrupt-handler-completes-write-from-sole-owning-rhs': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
                  '(TRAIT_PROPERTY_STORE porigin_site eps (KNOWN (PARRAY n_rhs)) z) :: ptask_saved* '
                  '-- if perrorcall.RESUME = TRAIT_PROPERTY_PHASE ptraitproperty 1'),
        'checks': [
            '$call_current_valid(S)',
            '$call_frames_valid(S, S.FRAMES)',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$class_statics_valid(S)',
            '$heap_valid($heap_graph(S))',
            'perrorcall.TARGET = (pcallcontext.TARGET)',
            'ptraitproperty.MODE = PPW',
            'ptraitproperty.SITE = porigin_site',
            'ptraitproperty.LINE = z',
            'pframe.ORIGIN = (porigin_site)',
            'pframe.CONTEXT = eps',
            'S_emitter = $api_saved_frame_scope($constant_frame_scope(S, pframe, pframe_tail*), pframe, pframe_tail*)',
            '$error_call_valid(S_emitter, perrorcall)',
            '$call_task_valid(S_emitter, TRAIT_PROPERTY_STORE porigin_site eps (KNOWN (PARRAY n_rhs)) z)',
            '~$call_task_valid(S_emitter, TRAIT_PROPERTY_STORE (PORIGIN 999 eps) eps (KNOWN (PARRAY n_rhs)) z)',
            '~$call_task_valid(S_emitter, TRAIT_PROPERTY_STORE porigin_site (ADD) (KNOWN (PARRAY n_rhs)) z)',
            '~$call_task_valid(S_emitter, TRAIT_PROPERTY_STORE porigin_site eps (KNOWN (PARRAY 999)) z)',
            '~$call_task_valid(S_emitter, TRAIT_PROPERTY_STORE porigin_site eps (KNOWN (PARRAY n_rhs)) $(z + 10))',
            '~$error_call_valid(S_emitter, perrorcall[.RESUME = TRAIT_PROPERTY_PHASE (ptraitproperty[.ROOT = PORIGIN 999 eps]) 1])',
            '~$call_current_valid(S[.FRAMES = pframe[.TODO = ptask_saved*] :: pframe_tail*])',
            '$task_nodes(TRAIT_PROPERTY_PHASE ptraitproperty 1) = eps',
            '$task_nodes(TRAIT_PROPERTY_STORE porigin_site eps (KNOWN (PARRAY n_rhs)) z) = [HARRAY n_rhs]',
            '$heap_owners($heap_graph(S), HARRAY n_rhs) = 1',
            '$heap_owners($heap_graph(S[.FRAMES = pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*] :: pframe_tail*]), HARRAY n_rhs) = 0',
            'S.ARRAYS[n_rhs].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
            '$class_static_at(S.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic)',
            'pclassstatic.STATE = PROP_VALUE (DIRECT (PARRAY n_old))',
            'n_old =/= n_rhs',
            'S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
            'S_done = $drive(S, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$outputs(S_done.EVENTS) = $ptascii("PRE;H;CAUGHT;1")',
            '$class_static_at(S_done.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic_done)',
            'pclassstatic_done.STATE = PROP_VALUE (DIRECT (PARRAY n_rhs))',
            '$heap_owners($heap_graph(S_done), HARRAY n_rhs) = 1',
            '$lookup(S_done.ENV, $ptascii("e")) = (n_exception_cell)',
            'S_done.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            '$throwable_field(S_done, n_exception, "message") = PSTRING $ptascii("STOP")',
            '$throwable_field(S_done, n_exception, "previous") = PNULL',
            '$call_descriptors_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$class_statics_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 3000)',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
