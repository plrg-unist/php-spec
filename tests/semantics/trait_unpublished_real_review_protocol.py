#!/usr/bin/env python3
"""Independent authentic birth receipt, source transfer and durable clone checks."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/semantics'
sys.path.insert(0, str(HERE))
import closure_call_protocol as protocol
import trait_unpublished_real_protocol as author

FAILURE = HERE / 'trait_unpublished_real_failure_review.watsup'
protocol.MODULES = [*protocol.MODULES, FAILURE]

CATALOGUE = HERE / 'trait_data_unpublished_real_review_cases.json'
SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source']
FAILED_INITIALIZER = ('<?php\ntrait T{public const Y=[static function(){echo "X;";},E_STRICT,1/0][0];public static $x=self::Y;}\n'
                      'echo "PRE;";\nclass C{use T;public static $x=self::Y;}\necho "POST;";\n')

CASES = {
    'real-birth-receipt-rejects-marker-source-table-and-lookup-forgeries': {
        'source': author.SOURCE,
        'stage': author.STAGE,
        'checks': author.START + [
            'S_birth.CLASSCONSTANTHISTORY = S_start.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause]',
            '$trait_real_cause(S_birth, ptraitcachecause) = (pclassconstantdesc_y)',
            '$trait_real_birth_owner(S_birth, pconstantclosure) = (porigin_c)',
            '$constant_callable_owner_valid(S_birth, pconstantclosure, porigin_c)',
            '$class_constant_callable_receipt_owner(S_birth, pconstantclosure) = (porigin_c)',
            '$trait_real_cause(S_birth, ptraitcachecause[.ROOT = pclassconstantdesc_y.INITIALIZER]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.TABLE = eps]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.TABLE = [pclassconstantdesc_y[.OWNER = porigin_t]]]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.TABLE = [pclassconstantdesc_y[.NAME = $ptascii("Z")]]]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.LOOKUPS = eps]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.LOOKUPS = [porigin_site]]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.LOOKUPS = [porigin_root, porigin_root]]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.PREFIX = $(ptraitcachecause.PREFIX + 1)]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.USERPREFIX = $(ptraitcachecause.USERPREFIX + 1)]) = eps',
            '$trait_real_cause(S_birth, ptraitcachecause[.CLASS = porigin_t]) = eps',
            '~$constant_callable_record_valid(S_birth, pconstantclosure[.PREFIX = $(pconstantclosure.PREFIX + 1)])',
            '~$constant_callable_record_valid(S_birth, pconstantclosure[.DECL = porigin_y_source])',
            '~$constant_callable_record_valid(S_birth, pconstantclosure[.SITE = porigin_root])',
            '~$constant_callable_owner_valid(S_birth, pconstantclosure, porigin_t)',
            'S_missing = S_birth[.CLASSCONSTANTHISTORY = S_start.CLASSCONSTANTHISTORY]',
            '$trait_real_birth_owner(S_missing, pconstantclosure) = eps',
            '~$constant_callable_owner_valid(S_missing, pconstantclosure, porigin_c)',
            '~$closure_scope_row_valid(S_missing, pclosurescope)',
            'S_early = S_birth[.CLASSNAMES = S_birth.CLASSNAMES ++ [($ptascii("c"), porigin_c)]]',
            '~$trait_real_active(S_early, ptraitcachecause)',
            '~$trait_real_published(S_early, ptraitcachecause)',
            '~$constant_callable_record_valid(S_early, pconstantclosure)',
            '~$call_task_valid(S_birth, TRAIT_OBJECT_COMPARISON ptraitcachecause[.ROOT = porigin_site])',
            '~$trait_real_pending(S_birth[.TODO = S_birth.TODO ++ [TRAIT_OBJECT_COMPARISON ptraitcachecause]], ptraitcachecause)',
            '$trait_real_stamp(S_birth, n_object, porigin_site, pconstantclosure.DECL, pconstantclosure.PREFIX) = S_birth',
            '$class_constant_history_fold(S_birth[.CLASSCONSTANTHISTORY = S_birth.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause]], S_birth.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_object porigin_site ptraitcachecause], eps, eps, 0) = CCBAD',
            '$task_nodes(TRAIT_OBJECT_COMPARISON ptraitcachecause) = eps',
        ],
    },
    'real-birth-durable-receipt-rejects-postpublication-prefix-bypass': {
        'source': author.SOURCE,
        'stage': author.STAGE,
        'checks': [
            'S_after = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
            'S_after.COMPLETION = NORMAL',
            '$class_at(S_after.CLASSES, porigin_c) = (pclassdesc_bound)',
            '$class_constant_desc(pclassdesc_bound.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'pdefaultcache_y.VALUE = POBJECT n_y',
            '$constant_callable_record(S_after.CONSTANTCLOSURES, n_y) = (pconstantclosure_y)',
            '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_y) = ((pconstantclosure_y.SITE, ptraitcachecause_y))',
            'pconstantclosure_y.PREFIX = |S.DECLARATIONS|',
            '$trait_real_published(S_after, ptraitcachecause_y)',
            '$constant_callable_owner_valid(S_after, pconstantclosure_y, porigin_c)',
            '$class_constant_callable_receipt_owner(S_after, pconstantclosure_y) = (porigin_c)',
            '$constant_callable_record_valid(S_after, pconstantclosure_y)',
            '$constant_callable_published(S_after.DECLARATIONS[0:|S_after.DECLARATIONS|], porigin_c)',
            '~$constant_callable_owner_valid(S_after, pconstantclosure_y[.PREFIX = |S_after.DECLARATIONS|], porigin_c)',
            '~$constant_callable_record_valid(S_after, pconstantclosure_y[.PREFIX = |S_after.DECLARATIONS|])',
            '$class_constant_callable_receipt_owner(S_after, pconstantclosure_y[.PREFIX = |S_after.DECLARATIONS|]) = eps',
            'S_future = S_after[.CONSTANTCLOSURES = S.CONSTANTCLOSURES ++ [pconstantclosure_y[.PREFIX = |S_after.DECLARATIONS|]]]',
            '~$constant_callable_records_valid(S_future, S_future.CONSTANTCLOSURES)',
            '~$class_constant_state_valid(S_future)',
            '$trait_real_cause(S_after, ptraitcachecause_y[.PREFIX = |S_after.DECLARATIONS|]) = eps',
            'S_duplicate = S_after[.CLASSCONSTANTHISTORY = S_after.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_y pconstantclosure_y.SITE ptraitcachecause_y]]',
            '~$class_constant_state_valid(S_duplicate)',
            '~$trait_real_published(S_after[.CLASSNAMES = S.CLASSNAMES], ptraitcachecause_y)',
            '~$constant_callable_record_valid(S_after[.CLASSNAMES = S.CLASSNAMES], pconstantclosure_y)',
            '$call_descriptors_valid(S_after)',
            '$declaration_history_valid(S_after)',
            '$class_constant_state_valid(S_after)',
            '$heap_valid($heap_graph(S_after))',
        ],
    },
    'nested-real-caches-and-clone-retain-source-after-property-retirement': {
        'source': SOURCE,
        'stage': ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin_c) -- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
                  '-- if pclassdesc_c.NAME = $ptascii("N") ++ [92] ++ $ptascii("C")'),
        'checks': [
            'S_after = $activate_class(S[.TODO = ptask_tail*], pclassdesc_c)',
            'S_after.COMPLETION = NORMAL',
            'S_done = $drive(S_after, 3000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            '$class_named(S_done.CLASSNAMES, $ptascii("n") ++ [92] ++ $ptascii("e")) = (porigin_e)',
            '$class_at(S_done.CLASSES, porigin_c) = (pclassdesc_c_bound)',
            '$class_at(S_done.CLASSES, porigin_e) = (pclassdesc_e_bound)',
            '$class_constant_desc(pclassdesc_c_bound.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_c_y)',
            '$class_constant_desc(pclassdesc_e_bound.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_e_y)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_c_y.ORIGIN) = (pdefaultcache_c)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_e_y.ORIGIN) = (pdefaultcache_e)',
            'pdefaultcache_c.VALUE = PARRAY n_array_c',
            'pdefaultcache_e.VALUE = PARRAY n_array_e',
            'n_array_c =/= n_array_e',
            'S_done.ARRAYS[n_array_c].ITEMS = (ENTRY (KINT 0) (DIRECT (POBJECT n_c))) :: pentry_c_tail*',
            'S_done.ARRAYS[n_array_e].ITEMS = (ENTRY (KINT 0) (DIRECT (POBJECT n_e))) :: pentry_e_tail*',
            'pentry_c_tail* = [ENTRY (KINT 1) (DIRECT (PINT 2048))]',
            'pentry_e_tail* = [ENTRY (KINT 1) (DIRECT (PINT 2048))]',
            'n_c =/= n_e',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_e) = (pconstantclosure_e)',
            'pconstantclosure_c.SITE = pconstantclosure_e.SITE',
            'pconstantclosure_c.DECL =/= pconstantclosure_e.DECL',
            '$constant_callable_record_valid(S_done, pconstantclosure_c)',
            '$constant_callable_record_valid(S_done, pconstantclosure_e)',
            '$lookup(S_done.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_done.STORE[n_copy_cell] = DEFINED (POBJECT n_copy)',
            r'n_copy =/= n_c /\ n_copy =/= n_e',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_copy) = eps',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_copy) = (pclosurescope_copy)',
            r'pclosurescope_copy.LEXICAL = porigin_c /\ pclosurescope_copy.CALLED = porigin_c',
            '$closure_scope_row_valid(S_done, pclosurescope_copy)',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_e) = (pclosurescope_e)',
            r'pclosurescope_e.LEXICAL = porigin_e /\ pclosurescope_e.CALLED = porigin_e',
            '~$closure_scope_row_valid(S_done, pclosurescope_copy[.LEXICAL = porigin_e])',
            '~$closure_scope_row_valid(S_done, pclosurescope_copy[.CALLED = porigin_e])',
            '$call_descriptors_valid(S_done)',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'real-birth-division-error-stops-in-authentic-unpublished-marker': {
        'source': FAILED_INITIALIZER,
        'stage': author.STAGE,
        'checks': author.START + [
            '$review_trait_real_failure(S_birth, ptraitcachecause, 300) = ((S_before, S_raw))',
            '$class_constant_active(S_before)',
            '$trait_real_active(S_before, ptraitcachecause)',
            '$trait_real_birth_at(S_before.CLASSCONSTANTHISTORY, n_object) = ((porigin_site, ptraitcachecause))',
            '$trait_cache_object_scalar_error(S_raw.COMPLETION)',
            'S_raw.COMPLETION = THROWN "DivisionByZeroError" ptbytes_message z_error',
            '$trait_real_markers(S_before.TODO) = [ptraitcachecause]',
            'F_error = $trait_cache_object_resume(F_seed, pcpath_root, pclassconstantdesc_y, $expression_line(expression_root), S_before, S_raw, ptraitcachecause)',
            'F_error.VALUE = eps',
            'F_error.MEMORY.COMPLETION = UNSUPPORTED "unpublished trait callable initializer exception"',
            'F_error.MEMORY.OBJECTS = F_seed.MEMORY.OBJECTS',
            'F_error.MEMORY.ALLOCATIONS = F_seed.MEMORY.ALLOCATIONS',
            'F_error.MEMORY.CLASSCONSTANTHISTORY = F_seed.MEMORY.CLASSCONSTANTHISTORY',
            '$trait_real_birth_at(F_error.MEMORY.CLASSCONSTANTHISTORY, n_object) = eps',
            '$default_cache_at(F_error.MEMORY.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            '$trait_member_fold(S_constants, pclassdesc_constants, porigin_root) = (F_full)',
            'F_full.VALUE = eps',
            'F_full.MEMORY.COMPLETION = UNSUPPORTED "unpublished trait callable initializer exception"',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {key: value for key, value in CASES.items() if args.match in key}
    assert selected
    protocol.run(selected, (Path(__file__).resolve(), CATALOGUE, author.CATALOGUE, author.SEED, author.HELPERS, FAILURE))
