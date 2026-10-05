#!/usr/bin/env python3
"""A reached failed trait link retains a public FCC and retires temporary owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
HARD = HERE / 'trait_data_failed_object_cache_review_cases.json'
ERROR = HERE / 'trait_data_failed_object_error_review_cases.json'
HARD_SOURCE = json.loads(HARD.read_text())['cases'][0]['source']
ERROR_SOURCE = json.loads(ERROR.read_text())['cases'][0]['source']

STAGE = ('S.TODO = (STMT (NStmtTrait phpType14 phpType3 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_u) '
         '-- if $class_at(S.CLASSES, porigin_u) = (pclassdesc_u) '
         '-- if pclassdesc_u.NAME = $ptascii("U")')

BEFORE = [
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("u")) = eps',
    'pclassdesc_u.KIND = "trait"',
    '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
    '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
    '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_p',
    '~pclassconstantdesc_y.FOLDED',
    '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$trait_cache_object_source(S, pclassconstantdesc_y)',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
    'pdeclcause = $declaration_cause(S)',
    'ptraitplan = $trait_plan(S, pclassdesc_u)',
    'ptraitfetch = $trait_fetch(S, ptraitplan.TRAITS, eps)',
    'ptraitfetch = TRAITFETCHED pclassdesc_traits*',
    '|pclassdesc_traits*| = 1',
    'S_link = $trait_fetched(S, pclassdesc_u, ptraitplan, ptraitfetch)',
]

PAIR = [
    '$trait_failed_cache_ready(S, S_link)',
    '$trait_failed_cache_class(S, S_link) = (porigin_u)',
    '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
    'S_link.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_y]',
    'pdefaultcache_y.VALUE = POBJECT n_y',
    'pdefaultcache_y.CLASS = PVCLOSURE n_y porigin_site_y',
    'n_y = |S.OBJECTS|',
    '$method_named(pclassdesc_p.METHODS, $ptascii("reveal")) = (pmethoddesc_reveal)',
    'S_link.OBJECTS[n_y] = CONSTANTCLOSURE porigin_site_y (METHODCLOSURE pmethoddesc_reveal.FUNCTION.ORIGIN porigin_site_y porigin_p eps)',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_y) = (pconstantclosure_y)',
    'S_link.CONSTANTCLOSURES = S.CONSTANTCLOSURES ++ [pconstantclosure_y]',
    'pconstantclosure_y.DECL = pclassconstantdesc_y.ORIGIN',
    'pconstantclosure_y.SITE = porigin_site_y',
    'pconstantclosure_y.PREFIX = |S.DECLARATIONS|',
    '$constant_callable_record_valid(S_link, pconstantclosure_y)',
    '$closure_scope_at(S_link.CLOSURESCOPES, n_y) = (pclosurescope_y)',
    'pclosurescope_y.LEXICAL = porigin_p',
    'pclosurescope_y.CALLED = porigin_p',
    'pclosurescope_y.RECEIVER = eps',
    'pclosurescope_y.CREATION = eps',
    'S_link.CLOSURESCOPES = S.CLOSURESCOPES ++ [pclosurescope_y]',
    '$trait_cache_event_at(S_link.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
    'S_link.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [(CCTRAITCACHE pclassconstantdesc_y.ORIGIN ptraitcachecause_y)]',
    'ptraitcachecause_y.CLASS = porigin_u',
    'ptraitcachecause_y.TABLE = eps',
    'ptraitcachecause_y.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause_y.USERPREFIX = |S.USERCONSTANTS|',
    'ptraitcachecause_y.LOOKUPS = [ptraitcachecause_y.ROOT]',
    '$trait_cache_cause_selected(S_link, ptraitcachecause_y) = (pclassconstantdesc_y)',
    '$trait_cache_bound_value(S_link, pclassconstantdesc_y, pdefaultcache_y.CLASS, ptraitcachecause_y.PREFIX)',
    '$heap_count(HOBJECT n_y, $class_constant_roots(S_link.CLASSCONSTANTCACHE)) = 1',
    '$heap_owners($heap_graph(S_link), HOBJECT n_y) = 1',
    'S_link.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_y]',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE])',
    '~$trait_failed_cache_ready(S, S_link[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY])',
]

RESTORED = [
    'S_failed = $activate_class(S[.TODO = ptask_tail*], pclassdesc_u)',
    'S_failed.COMPLETION = S_link.COMPLETION',
    'S_failed.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_u pdeclcause]',
    'S_failed.CLASSES = S.CLASSES',
    'S_failed.CLASSNAMES = S.CLASSNAMES',
    'S_failed.CURRENT = S.CURRENT',
    'S_failed.FRAMES = S.FRAMES',
    'S_failed.ERRORHANDLER = S.ERRORHANDLER',
    '$class_named(S_failed.CLASSNAMES, $ptascii("u")) = eps',
    '$trait_failed_cache_index(S_failed.DECLARATIONS, porigin_u, 0) = (ptraitcachecause_y.PREFIX)',
    'S_failed.CLASSCONSTANTCACHE = S_link.CLASSCONSTANTCACHE',
    'S_failed.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY',
    'S_failed.OBJECTS[n_y] = S_link.OBJECTS[n_y]',
    'S_failed.CONSTANTCLOSURES = S_link.CONSTANTCLOSURES',
    'S_failed.CLOSURESCOPES = S_link.CLOSURESCOPES',
    'S_failed.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_y]',
    '$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
    '$constant_callable_cache_valid(S_failed, pclassconstantdesc_y, pdefaultcache_y.CLASS, ptraitcachecause_y.PREFIX)',
    '$constant_callable_record_valid(S_failed, pconstantclosure_y)',
    '$heap_owners($heap_graph(S_failed), HOBJECT n_y) = 1',
    '$declaration_history_valid(S_failed)',
    '$call_descriptors_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$constant_callable_records_valid(S_failed, S_failed.CONSTANTCLOSURES)',
    '$heap_valid($heap_graph(S_failed))',
    '~$class_constant_state_valid(S_failed[.DECLARATIONS = S.DECLARATIONS])',
    '~$constant_callable_record_valid(S_failed, pconstantclosure_y[.DECL = porigin_u])',
    '~$constant_callable_record_valid(S_failed, pconstantclosure_y[.PREFIX = 0])',
    '~$constant_callable_records_valid(S_failed[.CONSTANTCLOSURES = S.CONSTANTCLOSURES], S.CONSTANTCLOSURES)',
    '~$constant_callable_record_valid(S_failed[.CLOSURESCOPES = S.CLOSURESCOPES ++ [pclosurescope_y[.LEXICAL = porigin_u]]], pconstantclosure_y)',
    '~$trait_cache_cause_valid(S_failed, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = [pclassconstantdesc_y.INITIALIZER]])',
]

FINISH = [
    'S_done = $drive(S_failed, 3000)',
    'S_done.COMPLETION = REQUESTFATAL ptbytes_fatal_class preqbytes_fatal pclassdesc_u.LINE',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$class_named(S_done.CLASSNAMES, $ptascii("u")) = eps',
    '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
    'S_done.OBJECTS[n_y] = S_failed.OBJECTS[n_y]',
    '$constant_callable_record(S_done.CONSTANTCLOSURES, n_y) = (pconstantclosure_y)',
    '$heap_owners($heap_graph(S_done), HOBJECT n_y) = 1',
    '$declaration_history_valid(S_done)',
    '$call_descriptors_valid(S_done)',
    '$class_constant_state_valid(S_done)',
    '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
    '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'hard-trait-conflict-retains-public-private-fcc-and-no-temporary-array': {
        'source': HARD_SOURCE,
        'stage': STAGE,
        'checks': BEFORE + [
            'S_link.COMPLETION = STATICBYTES preqbytes_fatal pclassdesc_u.LINE',
        ] + PAIR + RESTORED + FINISH,
    },
    'trait-operand-error-retains-public-private-fcc-and-retires-throwable': {
        'source': ERROR_SOURCE,
        'stage': STAGE,
        'checks': BEFORE + [
            'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") preqbytes_fatal pclassdesc_u.LINE',
            'S_link.TRACE = eps',
            'S_link.ERRORFATALTRACE = eps',
        ] + PAIR + [
            'n_error = $(n_y + 1)',
            'S_link.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Error"',
            '~((HOBJECT n_error) <- S_link.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_link), HOBJECT n_error) = 0',
        ] + RESTORED + [
            'S_failed.TRACE = eps',
            'S_failed.ERRORFATALTRACE = eps',
            '~((HOBJECT n_error) <- S_failed.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_failed), HOBJECT n_error) = 0',
        ] + FINISH + [
            '~((HOBJECT n_error) <- S_done.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), HARD, ERROR))
