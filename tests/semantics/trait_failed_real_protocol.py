#!/usr/bin/env python3
"""Genuine failed REAL birth, cache rollback and retired receipt guards."""
from pathlib import Path
import json

import closure_call_protocol as protocol
import trait_unpublished_real_protocol as birth

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_data_failed_real_cases.json'
HELPERS = HERE / 'trait_failed_real.watsup'
FAILURE = HERE / 'trait_unpublished_real_failure_review.watsup'
protocol.MODULES = [*protocol.MODULES, HELPERS, FAILURE]
ROWS = json.loads(CATALOGUE.read_text())['cases']

FINAL = [
    'S_after.COMPLETION = REQUESTFATAL ptbytes_kind ptbytes_message z_fatal',
    'ptbytes_kind = $ptascii("CompileError")',
    '$class_named(S_after.CLASSNAMES, $ptascii("c")) = eps',
    'S_after.CLASSES = S_seed.CLASSES',
    'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c $declaration_cause(S_seed)]',
    '$constant_callable_record(S_after.CONSTANTCLOSURES, n_object) = (pconstantclosure)',
    '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_object) = ((porigin_site, ptraitcachecause))',
    '$trait_real_receipt_source(S_after, pconstantclosure, ptraitcachecause) = (pclassconstantdesc_y)',
    '$class_constant_origin(S_after.CLASSES, pclassconstantdesc_y.ORIGIN) = eps',
    '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$trait_cache_event_at(S_after.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = eps',
    '~(HOBJECT n_object <- S_after.ALLOCATIONS)',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_object) = eps',
    '$trait_real_retired_receipt(S_after, pconstantclosure) = (pclassconstantdesc_y)',
    '$constant_callable_record_valid(S_after, pconstantclosure)',
    '~$constant_callable_value_valid(S_after, n_object, porigin_site)',
    '$class_constant_state_valid(S_after)',
    '$call_descriptors_valid(S_after)',
    '$declaration_history_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    'S_live = S_after[.ALLOCATIONS = S_after.ALLOCATIONS ++ [HOBJECT n_object]]',
    '$trait_real_retired_receipt(S_live, pconstantclosure) = eps',
    '~$constant_callable_record_valid(S_live, pconstantclosure)',
    '~$call_descriptors_valid(S_live)',
    '$trait_real_retired_receipt(S_after[.DECLARATIONS = S_seed.DECLARATIONS], pconstantclosure) = eps',
    '$trait_real_retired_receipt(S_after, pconstantclosure[.PREFIX = $(pconstantclosure.PREFIX + 1)]) = eps',
    '$trait_real_retired_receipt(S_after, pconstantclosure[.DECL = porigin_c]) = eps',
    '$trait_real_retired_receipt(S_after, pconstantclosure[.SITE = porigin_c]) = eps',
    '$trait_real_retired_receipt(S_after[.CLASSNAMES = S_after.CLASSNAMES ++ [($ptascii("c"), porigin_c)]], pconstantclosure) = eps',
    'S_without_birth = S_after[.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY]',
    '$trait_real_retired_receipt(S_without_birth, pconstantclosure) = eps',
    '~$constant_callable_record_valid(S_without_birth, pconstantclosure)',
]

CASES = {
    'throwing-real-birth-keeps-actual-error-and-retires-owner': {
        'source': ROWS[0]['source'],
        'stage': birth.STAGE,
        'checks': birth.START + [
            '$review_trait_real_failure(S_birth, ptraitcachecause, 300) = ((S_before, S_raw))',
            '$trait_cache_object_error_allowed(S_before, ptraitcachecause)',
            '~$trait_cache_object_error_allowed(S_before, ptraitcachecause[.ROOT = porigin_site])',
            'S_raw.COMPLETION = THROWN "DivisionByZeroError" ptbytes_error z_error',
            'F_error = $trait_cache_object_resume(F_seed, pcpath_root, pclassconstantdesc_y, $expression_line(expression_root), S_before, S_raw, ptraitcachecause)',
            'F_error.VALUE = eps',
            'F_error.MEMORY.COMPLETION = THROWN "DivisionByZeroError" ptbytes_error z_error',
            'S_seed = S[.TODO = ptask_tail*]',
            'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_c)',
            '$trait_cache_failed(S_seed, S_link)',
            '$trait_failed_cache_class(S_seed, S_link) = (porigin_c)',
            '$trait_failed_cache_ready(S_seed, S_link)',
            'S_link.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause]',
            'S_link.CLASSCONSTANTCACHE = S_seed.CLASSCONSTANTCACHE',
            'S_after = $trait_restore(S_seed, S_link)',
            'S_after.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY',
        ] + FINAL,
    },
    'completed-real-cache-failure-keeps-source-history-without-live-authority': {
        'source': ROWS[1]['source'],
        'stage': birth.STAGE,
        'checks': [
            'S_seed = S[.TODO = ptask_tail*]',
            'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_c)',
            'n_object = |S_seed.OBJECTS|',
            '$trait_real_birth_at(S_link.CLASSCONSTANTHISTORY, n_object) = ((porigin_site, ptraitcachecause))',
            '$trait_cache_cause_selected(S_link, ptraitcachecause) = (pclassconstantdesc_y)',
            'porigin_y = pclassconstantdesc_y.ORIGIN',
            'S_link.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause, CCTRAITCACHE porigin_y ptraitcachecause]',
            '$constant_callable_record(S_link.CONSTANTCLOSURES, n_object) = (pconstantclosure)',
            '$default_cache_at(S_link.CLASSCONSTANTCACHE, porigin_y) = (pdefaultcache)',
            'pdefaultcache.VALUE = POBJECT n_object',
            'pdefaultcache.CLASS = PVCLOSURE n_object porigin_site',
            'HOBJECT n_object <- S_link.ALLOCATIONS',
            '$closure_scope_at(S_link.CLOSURESCOPES, n_object) = (pclosurescope)',
            r'pclosurescope.LEXICAL = porigin_c /\ pclosurescope.CALLED = porigin_c',
            '~$trait_real_authority(S_link, ptraitcachecause)',
            '$trait_real_failed_bound(S_link, pclassconstantdesc_y, pdefaultcache.CLASS, ptraitcachecause)',
            '$trait_failed_cache_bound(S_link, pclassconstantdesc_y, pdefaultcache.CLASS, ptraitcachecause)',
            '~$trait_failed_cache_bound(S_link, pclassconstantdesc_y, PVSCALAR, ptraitcachecause)',
            '$trait_failed_cache_ready(S_seed, S_link)',
            'S_bad_class = S_link[.CLASSCONSTANTCACHE = S_seed.CLASSCONSTANTCACHE ++ [pdefaultcache[.CLASS = PVSCALAR]]]',
            '~$trait_failed_cache_ready(S_seed, S_bad_class)',
            'S_duplicate = S_link[.CLASSCONSTANTHISTORY = S_link.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause]]',
            '~$trait_failed_cache_ready(S_seed, S_duplicate)',
            'S_missing = S_link[.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY ++ [CCTRAITCACHE porigin_y ptraitcachecause]]',
            '~$trait_failed_cache_ready(S_seed, S_missing)',
            'S_restored = $trait_restore(S_seed, S_link)',
            '$iterator_notice_seeds(S_restored.TODO) =/= eps',
            '~$call_tasks_valid(S_restored, S_restored.TODO)',
            'PhpStep: S ~> S_after',
            'S_after.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause]',
            'S_after.COMPLETION = STATICBYTES ptbytes_message z_fatal',
        ] + FINAL[2:],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, birth.CATALOGUE,
                         birth.SEED, birth.HELPERS, HELPERS, FAILURE))
