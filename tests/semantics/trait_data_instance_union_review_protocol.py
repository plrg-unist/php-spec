#!/usr/bin/env python3
"""Imported instance templates keep their full declaration and source scope."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_instance_union_review_cases.json')
SOURCES = {row['id']: row['source']
           for row in json.loads(CATALOGUE.read_text())['cases']}

STAGE = ('S.TODO = (EVAL (NScalarMagicConstClass metadata)) :: ptask_tail* '
         '-- if S.CONSTCONTEXT = (pconstantcontext) '
         '-- if pconstantcontext.ORIGIN = '
         'TRAIT_MEMBER_ORIGIN porigin_owner porigin_source '
         '-- if $instance_default_context_at(S.TODO) = (porigin_requested)')

SCOPE_CHECKS = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$instance_default_state_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_owner)',
    '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_c)',
    'pclassdesc_c.PROPERTIES = [ppropertydesc_c]',
    'ppropertydesc_c.ORIGIN = pconstantcontext.ORIGIN',
    'ppropertydesc_c.DEFAULT = PROP_DEFERRED porigin_initializer',
    '$origin_source(pconstantcontext.ORIGIN) = porigin_source',
    '$constant_expression_root(S, pconstantcontext.ORIGIN) '
    '= (porigin_initializer)',
    '$property_default_active_desc(S, pconstantcontext.ORIGIN) '
    '= (ppropertydesc_c)',
    '$static_default_context_at(S.TODO) = (pstaticdefaultcontext)',
    'pstaticdefaultcontext.DECL = pconstantcontext.ORIGIN',
    'pstaticdefaultcontext.ROOT = porigin_requested',
    '$instance_default_pending(S, porigin_requested, pconstantcontext.ORIGIN)',
    '$static_default_scope(S) = (porigin_owner)',
    '$static_default_context_valid(S, pconstantcontext)',
    '$instance_default_site_valid(S, porigin_requested, '
    'pstaticdefaultcontext, S.TODO)',
    'S.ORIGIN = (porigin_site)',
    '$constant_expression_below(S, pconstantcontext.ORIGIN, porigin_site)',
    '$trait_initializer_scope(S) = (porigin_owner)',
    '$compiled_read(S, porigin_site) = eps',
    '$trait_initializer_scope(S[.CONSTCONTEXT = eps]) = eps',
    '$trait_initializer_scope(S[.CONSTCONTEXT = '
    '(pconstantcontext[.ORIGIN = porigin_source])]) = eps',
    '$trait_initializer_scope(S[.CONSTCONTEXT = '
    '(pconstantcontext[.ORIGIN = TRAIT_MEMBER_ORIGIN '
    '(PORIGIN 999 eps) porigin_source])]) = eps',
    '$trait_initializer_scope(S[.TODO = eps]) = eps',
    '$trait_initializer_scope(S[.ORIGIN = (PORIGIN 999 eps)]) = eps',
    '$trait_initializer_scope(S[.INSTANCEDEFAULTS = eps]) = eps',
    '~$instance_default_site_valid(S, porigin_requested, '
    'pstaticdefaultcontext[.DECL = porigin_source], S.TODO)',
    '~$instance_default_site_valid(S, porigin_requested, '
    'pstaticdefaultcontext[.ROOT = PORIGIN 999 eps], S.TODO)',
    '~$instance_default_site_valid(S, porigin_requested, '
    'pstaticdefaultcontext[.LINE = $(pstaticdefaultcontext.LINE + 100)], S.TODO)',
    '~$instance_default_site_valid(S[.INSTANCEDEFAULTS = eps], '
    'porigin_requested, pstaticdefaultcontext, S.TODO)',
    'PhpStep: S ~> S_class',
    'S_class.RESULT = KNOWN (PSTRING $ptascii("C"))',
    'S_done = $drive(S_class, 2500)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$instance_default_state_valid(S_done)',
    '$class_constant_state_valid(S_done)',
    '$property_state_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2500)',
]

CASES = {
    'inherited-template-keeps-importing-scope-and-array-owners': {
        'source': SOURCES['imported-array-using-scope-inherited-and-cow'],
        'stage': STAGE + ' -- if $class_named(S.CLASSNAMES, $ptascii("d")) '
                         '= (porigin_requested)',
        'checks': SCOPE_CHECKS + [
            'S.CURRENT = eps',
            'porigin_requested =/= porigin_owner',
            '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_e)',
            '$class_at(S.CLASSES, porigin_requested) = (pclassdesc_d)',
            'pclassdesc_d.PROPERTIES = eps',
            '$property_layout(S, porigin_requested, |S.CLASSES|) '
            '= [ppropertydesc_c]',
            '$trait_initializer_scope(S[.CONSTCONTEXT = '
            '(pconstantcontext[.ORIGIN = TRAIT_MEMBER_ORIGIN '
            'porigin_e porigin_source])]) = eps',
            '~$instance_default_site_valid(S, porigin_owner, '
            'pstaticdefaultcontext, S.TODO)',
            '$class_at(S_done.CLASSES, porigin_e) = (pclassdesc_e)',
            'pclassdesc_e.PROPERTIES = [ppropertydesc_e]',
            'ppropertydesc_e.ORIGIN = porigin_decl_e',
            'porigin_decl_e = TRAIT_MEMBER_ORIGIN porigin_e porigin_source',
            'porigin_decl_e =/= pconstantcontext.ORIGIN',
            '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_owner, '
            'pconstantcontext.ORIGIN) = (pinstancetemplate_c)',
            '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_requested, '
            'pconstantcontext.ORIGIN) = (pinstancetemplate_d)',
            '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_e, '
            'porigin_decl_e) = (pinstancetemplate_e)',
            'pinstancetemplate_c.STATE = INSTANCE_VALUE (PARRAY n_c) pvalueclass_c',
            'pinstancetemplate_d.STATE = INSTANCE_VALUE (PARRAY n_d) pvalueclass_d',
            'pinstancetemplate_e.STATE = INSTANCE_VALUE (PARRAY n_e) pvalueclass_e',
            'n_c =/= n_d',
            'n_c =/= n_e',
            'n_d =/= n_e',
            '$lookup(S_done.ENV, $ptascii("c")) = (n_cell_c)',
            'S_done.STORE[n_cell_c] = DEFINED (POBJECT n_object_c)',
            '$objectprops_at(S_done.OBJECTPROPS, n_object_c) = ([ppropertyslot])',
            'ppropertyslot.DECL = (pconstantcontext.ORIGIN)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_mutated))',
            'n_mutated =/= n_c',
            '(HARRAY n_c) <- $instance_default_roots(S_done.INSTANCEDEFAULTS)',
            '(HARRAY n_d) <- $instance_default_roots(S_done.INSTANCEDEFAULTS)',
            '(HARRAY n_e) <- $instance_default_roots(S_done.INSTANCEDEFAULTS)',
            'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps]'
            '[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
            '~((HARRAY n_mutated) <- S_dead.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_dead), HARRAY n_c) = 1',
            '$heap_owners($heap_graph(S_dead), HARRAY n_d) = 1',
            '$heap_owners($heap_graph(S_dead), HARRAY n_e) = 1',
            '$instance_default_state_valid(S_dead)',
            '$heap_valid($heap_graph(S_dead))',
        ],
    },
    'initializer-scope-keeps-authentic-live-caller': {
        'source': SOURCES['imported-array-initializer-overrides-live-caller-scope'],
        'stage': STAGE + ' -- if S.CURRENT = (pcallcontext)',
        'checks': SCOPE_CHECKS + [
            'porigin_requested = porigin_owner',
            '$class_named(S.CLASSNAMES, $ptascii("q")) = (porigin_q)',
            'pcallcontext.LEXICAL_CLASS = (porigin_q)',
            'pcallcontext.CALLED_CLASS = (porigin_q)',
            '$call_current_valid(S)',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_owner)])])',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = pconstantcontext.ORIGIN])])',
            'S_class.CURRENT = S.CURRENT',
            'S_class.CVS = S.CVS',
            '$call_current_valid(S_class)',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
