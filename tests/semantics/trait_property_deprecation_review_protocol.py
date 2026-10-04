#!/usr/bin/env python3
"""Reached trait-property callbacks retain address, scope and storage owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_property_deprecation_review_cases.json')
DEFAULTS = Path(__file__).with_name('trait_data_static_default_review_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())['cases']}
RAW = {row['id']: row['source'] for row in json.loads(DEFAULTS.read_text())['cases']}

VALID = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$class_statics_valid(S)',
    '$proprefs_valid(S)',
    '$heap_valid($heap_graph(S))',
]
RECEIPT = [
    'S.ORIGIN = (ptraitproperty.SITE)',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (ptraitproperty.ROOT)',
    '$class_static_select(S, ptraitproperty.ROOT, ptraitproperty.NAME) = (ppropertydesc)',
    'ppropertydesc.ORIGIN = ptraitproperty.DECL',
    'ptraitproperty.NAME = $ptascii("x")',
    '$origin_source(ptraitproperty.DECL) = ptraitproperty.DECL',
    '$trait_property_source(S, ptraitproperty.SITE, ptraitproperty.ROOT, ptraitproperty.NAME, ptraitproperty.LINE)',
    '$task_nodes(TRAIT_PROPERTY_PHASE ptraitproperty 1) = eps',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE ptraitproperty 2)',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.SITE = PORIGIN 999 eps]) n_phase)',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.ROOT = PORIGIN 999 eps]) n_phase)',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.DECL = TRAIT_MEMBER_ORIGIN (PORIGIN 999 eps) ptraitproperty.DECL]) n_phase)',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.NAME = $ptascii("other")]) n_phase)',
    '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.LINE = $(ptraitproperty.LINE + 10)]) n_phase)',
    '~$call_task_valid(S[.SOURCES = eps], TRAIT_PROPERTY_PHASE ptraitproperty n_phase)',
    '~$call_task_valid(S[.CODE = eps], TRAIT_PROPERTY_PHASE ptraitproperty n_phase)',
    '~$call_task_valid(S[.CLASSNAMES = eps], TRAIT_PROPERTY_PHASE ptraitproperty n_phase)',
]
DONE = [
    'S_done = $drive(S, 3000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$call_descriptors_valid(S_done)',
    '$class_constant_state_valid(S_done)',
    '$class_statics_valid(S_done)',
    '$proprefs_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 3000)',
]

CASES = {
    'selected-address-survives-class-and-name-cv-rebinding': {
        'source': SOURCES['selected-trait-root-and-name-survive-handler-rebinding'],
        'stage': 'S.TODO = (TRAIT_PROPERTY_PHASE ptraitproperty 0) :: ptask_tail*',
        'checks': VALID + ['n_phase = 0'] + RECEIPT + [
            'S.CURRENT = eps',
            'S.BASE = BASE_CLASS_STATIC ptraitproperty.ROOT ptraitproperty.NAME',
            '$call_task_valid(S, TRAIT_PROPERTY_PHASE ptraitproperty 0)',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_c)',
            '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.ROOT = porigin_c]) 0)',
            '~$call_task_valid(S, TRAIT_PROPERTY_PHASE (ptraitproperty[.DECL = TRAIT_MEMBER_ORIGIN porigin_c ptraitproperty.DECL]) 0)',
            'PhpStep: S ~> S_warning',
            'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = TRAIT_PROPERTY_PHASE ptraitproperty 1',
            'perrorcall.SITE = ptraitproperty.SITE',
            'perrorcall.LEVEL = 8192',
            '$call_task_valid(S_warning, ERROR_HANDLER_INVOKE perrorcall)',
            '~$call_task_valid(S_warning, ERROR_HANDLER_INVOKE (perrorcall[.LEVEL = 2]))',
            '~$call_task_valid(S_warning, ERROR_HANDLER_INVOKE (perrorcall[.MESSAGE = eps]))',
        ] + DONE + [
            '$outputs(S_done.EVENTS) = $ptascii("H8192;9:C:other:1")',
            '$class_static_at(S_done.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic_done)',
            'pclassstatic_done.STATE = PROP_VALUE (DIRECT (PINT 9))',
        ],
    },
    'real-handler-keeps-authenticated-emitter-and-late-compound-rhs': {
        'source': SOURCES['compound-rereads-live-trait-cell-and-late-rhs-cv'],
        'stage': ('S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emitter* '
                  '-- if perrorcall.RESUME = TRAIT_PROPERTY_PHASE ptraitproperty 1'),
        'checks': VALID + [
            '$call_current_valid(S)',
            '$call_frames_valid(S, S.FRAMES)',
            '$error_context_valid(S, pcallcontext)',
            'pcallcontext.ARGC = 4',
            'S.ERRORHANDLER.CALLBACK = eps',
            'pframe.ORIGIN = (ptraitproperty.SITE)',
            'pframe.CONTEXT = eps',
            'perrorcall.TARGET = (pcallcontext.TARGET)',
            'S_emitter = $api_saved_frame_scope($constant_frame_scope(S, pframe, pframe_tail*), pframe, pframe_tail*)',
            '$error_call_valid(S_emitter, perrorcall)',
            '$call_task_valid(S_emitter, ERROR_HANDLER_RESULT perrorcall)',
            '~$error_call_valid(S_emitter, perrorcall[.SITE = PORIGIN 999 eps])',
            '~$error_call_valid(S_emitter, perrorcall[.LINE = $(perrorcall.LINE + 10)])',
            '~$error_call_valid(S_emitter, perrorcall[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE])',
            '~$error_call_valid(S_emitter, perrorcall[.RESUME = TRAIT_PROPERTY_PHASE (ptraitproperty[.DECL = TRAIT_MEMBER_ORIGIN (PORIGIN 999 eps) ptraitproperty.DECL]) 1])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.ARGC = 0])])',
            '~$call_current_valid(S[.FRAMES = pframe[.ORIGIN = (PORIGIN 999 eps)] :: pframe_tail*])',
            '~$call_current_valid(S[.FRAMES = pframe[.TODO = ptask_emitter*] :: pframe_tail*])',
        ] + DONE + [
            '$outputs(S_done.EVENTS) = $ptascii("H;12")',
            '$class_static_at(S_done.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic_done)',
            'pclassstatic_done.STATE = PROP_VALUE (DIRECT (PINT 12))',
            '$lookup(S_done.ENV, $ptascii("v")) = (n_rhs)',
            'S_done.STORE[n_rhs] = DEFINED (PINT 3)',
        ],
    },
    'posthandler-reference-send-retains-sole-typed-property-owner': {
        'source': SOURCES['by-reference-send-preserves-cell-after-handler-retirement'],
        'stage': ('S.CURRENT = eps -- if S.TODO = '
                  '(TRAIT_PROPERTY_PHASE ptraitproperty 1) :: ptask_tail*'),
        'checks': VALID + ['n_phase = 1'] + RECEIPT + [
            '$call_task_valid(S, TRAIT_PROPERTY_PHASE ptraitproperty 1)',
            'S.PROPREFS = eps',
            '$class_static_at(S.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic)',
            'pclassstatic.STATE = PROP_VALUE (DIRECT (PINT 4))',
            'PhpStep: S ~> S_resumed',
            'S_resumed.TODO = ptask_tail*',
            'S_resumed.BASE = BASE_CLASS_STATIC ptraitproperty.ROOT ptraitproperty.NAME',
        ] + DONE + [
            '$outputs(S_done.EVENTS) = $ptascii("H;F4;7")',
            'S_done.PROPREFS = [ppropref]',
            'ppropref.SOURCES = [CLASS_PROP_SOURCE ptraitproperty.DECL]',
            '$class_static_at(S_done.CLASSSTATICS, ptraitproperty.DECL) = (pclassstatic_done)',
            'pclassstatic_done.STATE = PROP_VALUE (ALIAS ppropref.CELL)',
            'S_done.STORE[ppropref.CELL] = DEFINED (PINT 7)',
            '$propref_source_valid(S_done, ppropref.CELL, CLASS_PROP_SOURCE ptraitproperty.DECL)',
            '~$propref_source_valid(S_done, ppropref.CELL, CLASS_PROP_SOURCE (TRAIT_MEMBER_ORIGIN ptraitproperty.ROOT ptraitproperty.DECL))',
            '~$class_statics_valid(S_done[.PROPREFS = eps])',
        ],
    },
    'raw-trait-initializer-keeps-live-caller-and-real-binder-scope': {
        'source': RAW['direct-trait-array-default-keeps-raw-trait-scope-under-live-caller'],
        'stage': ('S.TODO = (EVAL (NScalarMagicConstClass metadata)) :: ptask_tail* '
                  '-- if S.CONSTCONTEXT = (pconstantcontext) '
                  '-- if pconstantcontext.ORIGIN = PORIGIN n pcpath '
                  '-- if S.CURRENT = (pcallcontext)'),
        'checks': VALID + [
            '$call_current_valid(S)',
            '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
            '$class_named(S.CLASSNAMES, $ptascii("q")) = (porigin_q)',
            'pcallcontext.LEXICAL_CLASS = (porigin_q)',
            'pcallcontext.CALLED_CLASS = (porigin_q)',
            '$static_default_context_at(S.TODO) = (pstaticdefaultcontext)',
            'pstaticdefaultcontext.DECL = pconstantcontext.ORIGIN',
            'pstaticdefaultcontext.ROOT = porigin_t',
            '$property_declaring_class(S.CLASSES, pconstantcontext.ORIGIN) = (porigin_t)',
            '$static_default_scope(S) = (porigin_t)',
            '$static_default_context_valid(S, pconstantcontext)',
            'S.ORIGIN = (porigin_site)',
            '$constant_expression_below(S, pconstantcontext.ORIGIN, porigin_site)',
            '$trait_initializer_scope(S) = (porigin_t)',
            '$trait_initializer_scope(S[.CONSTCONTEXT = eps]) = eps',
            '$trait_initializer_scope(S[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_q pconstantcontext.ORIGIN])]) = eps',
            '$trait_initializer_scope(S[.TODO = eps]) = eps',
            '$trait_initializer_scope(S[.ORIGIN = (PORIGIN 999 eps)]) = eps',
            '$trait_initializer_scope(S[.SOURCES = eps]) = eps',
            '~$static_default_context_valid(S[.CLASSSTATICS = eps], pconstantcontext)',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_t)])])',
            'PhpStep: S ~> S_class',
            'S_class.RESULT = KNOWN (PSTRING $ptascii("T"))',
            'S_class.CURRENT = S.CURRENT',
            'S_class.CVS = S.CVS',
            '$call_current_valid(S_class)',
        ] + DONE + [
            '$outputs(S_done.EVENTS) = $ptascii("H8192;T:H8192;T")',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, DEFAULTS))
