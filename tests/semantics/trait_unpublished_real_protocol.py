#!/usr/bin/env python3
"""Reached unpublished REAL births retain scope and real cache ownership."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_data_unpublished_real_cases.json'
SEED = HERE / 'trait_public_object_initializer_review.watsup'
HELPERS = HERE / 'trait_unpublished_real.watsup'
protocol.MODULES = [*protocol.MODULES, SEED, HELPERS]
SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source']
STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

START = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    'S_constants = $trait_data_constants(S, pclassdesc_c, [pclassdesc_t], eps)',
    'S_constants.COMPLETION = NORMAL',
    '$class_at(S_constants.CLASSES, porigin_c) = (pclassdesc_constants)',
    '$class_constant_desc(pclassdesc_constants.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_c',
    'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
    '$ppproperty_desc_at(pclassdesc_constants.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
    'ppropertydesc_x.DEFAULT = PROP_DEFERRED porigin_root',
    'porigin_root = PORIGIN n_source pcpath_root',
    '$origin_node(S.SOURCES, porigin_root) = (expression_root)',
    '$review_trait_object_seed(S_constants, pclassdesc_constants, porigin_root) = (F_seed)',
    '$review_trait_real_start(F_seed, pcpath_root, pclassconstantdesc_y, $expression_line(expression_root)) = ((S_start, ptraitcachecause))',
    '$trait_real_pending(S_start, ptraitcachecause)',
    '$trait_real_active(S_start, ptraitcachecause)',
    '$class_constant_active(S_start)',
    'ptraitcachecause.TABLE = pclassdesc_constants.CONSTANTS',
    'ptraitcachecause.LOOKUPS = [porigin_root]',
    'ptraitcachecause.PREFIX = |S.DECLARATIONS|',
    '$task_nodes(TRAIT_OBJECT_COMPARISON ptraitcachecause) = eps',
    '$call_task_valid(S_start, TRAIT_OBJECT_COMPARISON ptraitcachecause)',
    'n_object = |S_start.OBJECTS|',
    'S_birth = $review_trait_real_birth(S_start, ptraitcachecause, n_object, 300)',
    'S_birth.COMPLETION = NORMAL',
    '$trait_real_active(S_birth, ptraitcachecause)',
    '$class_named(S_birth.CLASSNAMES, $ptascii("c")) = eps',
    'S_birth.RESULT = KNOWN (POBJECT n_object)',
    '$trait_real_birth_at(S_birth.CLASSCONSTANTHISTORY, n_object) = ((porigin_site, ptraitcachecause))',
    '$constant_callable_record(S_birth.CONSTANTCLOSURES, n_object) = (pconstantclosure)',
    'pconstantclosure.SITE = porigin_site',
    'pconstantclosure.DECL = pclassconstantdesc_y.ORIGIN',
    'pconstantclosure.PREFIX = ptraitcachecause.PREFIX',
    '$constant_callable_record_valid(S_birth, pconstantclosure)',
    '$closure_scope_at(S_birth.CLOSURESCOPES, n_object) = (pclosurescope)',
    'pclosurescope.LEXICAL = porigin_c',
    'pclosurescope.CALLED = porigin_c',
    'pclosurescope.RECEIVER = eps',
    '$closure_scope_row_valid(S_birth, pclosurescope)',
    '$heap_owners($heap_graph(S_birth), HOBJECT n_object) = 1',
    '$heap_count(HOBJECT n_object, $class_constant_roots(S_birth.CLASSCONSTANTCACHE)) = 0',
    '$default_cache_at(S_birth.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
]

CASES = {
    'real-birth-live-marker-and-completed-cache': {
        'source': SOURCE,
        'stage': STAGE,
        'checks': START + [
            '~$trait_real_authority(S_birth[.TODO = eps], ptraitcachecause)',
            '~$constant_callable_record_valid(S_birth[.TODO = eps], pconstantclosure)',
            '~$closure_scope_row_valid(S_birth[.TODO = eps], pclosurescope)',
            '~$trait_real_pending(S_birth[.TODO = S_birth.TODO ++ [TRAIT_OBJECT_COMPARISON ptraitcachecause]], ptraitcachecause)',
            'S_end = $review_trait_real_complete(S_birth, ptraitcachecause, 300)',
            '$trait_real_complete(S_end, ptraitcachecause)',
            '$trait_real_active(S_end, ptraitcachecause) = false',
            '$trait_real_authority(S_end, ptraitcachecause)',
            'S_end.TODO = [TRAIT_OBJECT_COMPARISON ptraitcachecause]',
            '$call_task_valid(S_end, TRAIT_OBJECT_COMPARISON ptraitcachecause)',
            '$constant_callable_record_valid(S_end, pconstantclosure)',
            '$default_cache_at(S_end.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache)',
            'pdefaultcache.VALUE = POBJECT n_object',
            '$heap_count(HOBJECT n_object, $class_constant_roots(S_end.CLASSCONSTANTCACHE)) = 1',
            '$trait_real_failure_memory(F_seed, S_end) = F_seed.MEMORY',
        ],
    },
    'real-birth-publication-and-independent-imports': {
        'source': SOURCE,
        'stage': STAGE,
        'checks': [
            'S_after = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
            'S_after.COMPLETION = NORMAL',
            '$class_named(S_after.CLASSNAMES, $ptascii("c")) = (porigin_c)',
            '$class_at(S_after.CLASSES, porigin_c) = (pclassdesc_bound)',
            '$class_constant_desc(pclassdesc_bound.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'pdefaultcache_y.VALUE = POBJECT n_y',
            '$constant_callable_record(S_after.CONSTANTCLOSURES, n_y) = (pconstantclosure_y)',
            '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_y) = ((pconstantclosure_y.SITE, ptraitcachecause_y))',
            '$trait_real_published(S_after, ptraitcachecause_y)',
            'pconstantclosure_y.PREFIX = |S.DECLARATIONS|',
            '$constant_callable_record_valid(S_after, pconstantclosure_y)',
            '$heap_owners($heap_graph(S_after), HOBJECT n_y) = 1',
            '$call_descriptors_valid(S_after)',
            '$class_constant_state_valid(S_after)',
            '$heap_valid($heap_graph(S_after))',
            'S_done = $drive(S_after, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            '$class_named(S_done.CLASSNAMES, $ptascii("e")) = (porigin_e)',
            '$class_at(S_done.CLASSES, porigin_e) = (pclassdesc_e)',
            '$class_constant_desc(pclassdesc_e.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_z)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_z)',
            'pdefaultcache_z.VALUE = POBJECT n_z',
            'n_z =/= n_y',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_z) = (pconstantclosure_z)',
            'pconstantclosure_z.SITE = pconstantclosure_y.SITE',
            'pconstantclosure_z.DECL =/= pconstantclosure_y.DECL',
            '$(pconstantclosure_z.PREFIX > pconstantclosure_y.PREFIX)',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_y) = (pclosurescope_y)',
            r'pclosurescope_y.LEXICAL = porigin_c /\ pclosurescope_y.CALLED = porigin_c',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_z) = (pclosurescope_z)',
            r'pclosurescope_z.LEXICAL = porigin_e /\ pclosurescope_z.CALLED = porigin_e',
            '$heap_count(HOBJECT n_y, $class_constant_roots(S_done.CLASSCONSTANTCACHE)) = 1',
            '$heap_count(HOBJECT n_z, $class_constant_roots(S_done.CLASSCONSTANTCACHE)) = 1',
            '$constant_callable_record_valid(S_done, pconstantclosure_y)',
            '$constant_callable_record_valid(S_done, pconstantclosure_z)',
            '$call_descriptors_valid(S_done)',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, SEED, HELPERS))
