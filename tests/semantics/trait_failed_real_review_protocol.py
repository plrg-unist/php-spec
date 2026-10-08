#!/usr/bin/env python3
"""Actual failed REAL births authenticate only retired source receipts."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/semantics'
sys.path.insert(0, str(HERE))
import closure_call_protocol as protocol

CATALOGUE = HERE / 'trait_data_failed_real_review_cases.json'
HELPERS = HERE / 'trait_failed_real.watsup'
protocol.MODULES = [*protocol.MODULES, HELPERS]
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())['cases']}
STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) -- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

BEFORE = [
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    'S_seed = S[.TODO = ptask_tail*]',
    'pdeclcause = $declaration_cause(S_seed)',
    'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_c)',
    '$trait_failed_cache_ready(S_seed, S_link)',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_birth_at(S_link.CLASSCONSTANTHISTORY, n_c) = ((pconstantclosure_c.SITE, ptraitcachecause_c))',
    '$trait_cache_cause_selected(S_link, ptraitcachecause_c) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_c',
    'pconstantclosure_c.DECL = pclassconstantdesc_y.ORIGIN',
    'pconstantclosure_c.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause_c.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause_c.USERPREFIX = |S.USERCONSTANTS|',
]

RETIRED = [
    'PhpStep: S ~> S_failed',
    'S_failed.COMPLETION = S_link.COMPLETION',
    'S_failed.CLASSES = S.CLASSES',
    'S_failed.CLASSNAMES = S.CLASSNAMES',
    'S_failed.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause]',
    'S_failed.TRACE = eps',
    'S_failed.ERRORFATALTRACE = eps',
    '$default_cache_at(S_failed.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$trait_cache_event_at(S_failed.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = eps',
    '$constant_callable_record(S_failed.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_birth_at(S_failed.CLASSCONSTANTHISTORY, n_c) = ((pconstantclosure_c.SITE, ptraitcachecause_c))',
    '~((HOBJECT n_c) <- S_failed.ALLOCATIONS)',
    '$closure_scope_at(S_failed.CLOSURESCOPES, n_c) = eps',
    '$heap_owners($heap_graph(S_failed), HOBJECT n_c) = 0',
    '$trait_real_retired_receipt(S_failed, pconstantclosure_c) = (pclassconstantdesc_y)',
    '$constant_callable_record_valid(S_failed, pconstantclosure_c)',
    '$call_descriptors_valid(S_failed)',
    '$declaration_history_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$constant_callable_records_valid(S_failed, S_failed.CONSTANTCLOSURES)',
    '$heap_valid($heap_graph(S_failed))',
]

PUBLIC = [
    '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
    '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
    '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Z")) = (pclassconstantdesc_z)',
    '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = eps',
    '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_p)',
    'pdefaultcache_p.VALUE = POBJECT n_p',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_p) = (pconstantclosure_p)',
    '$default_cache_at(S_failed.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_p)',
    '$constant_callable_record(S_failed.CONSTANTCLOSURES, n_p) = (pconstantclosure_p)',
    '$constant_callable_record_valid(S_failed, pconstantclosure_p)',
    '$heap_owners($heap_graph(S_failed), HOBJECT n_p) = 1',
]

CASES = {
    'retired-real-receipt-rejects-live-source-prefix-and-failed-history-forgeries': {
        'source': SOURCES['typed-real-birth'], 'stage': STAGE,
        'checks': ['n_c = |S.OBJECTS|'] + BEFORE + RETIRED + [
            'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_fatal 5',
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_failed.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_c pconstantclosure_c.SITE ptraitcachecause_c]',
            'S_revived = S_failed[.ALLOCATIONS = S_failed.ALLOCATIONS ++ [HOBJECT n_c]][.CLOSURESCOPES = S_failed.CLOSURESCOPES ++ [{OBJECT n_c, LEXICAL porigin_c, CALLED porigin_c, RECEIVER eps, CREATION eps}]]',
            '$trait_real_retired_receipt(S_revived, pconstantclosure_c) = eps',
            '~$constant_callable_record_valid(S_revived, pconstantclosure_c)',
            '~$class_constant_state_valid(S_revived)',
            '$trait_real_retired_receipt(S_failed[.DECLARATIONS = S.DECLARATIONS], pconstantclosure_c) = eps',
            '$trait_real_retired_receipt(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRCLASS porigin_c pdeclcause]], pconstantclosure_c) = eps',
            '$trait_real_retired_receipt(S_failed[.CLASSNAMES = S_failed.CLASSNAMES ++ [($ptascii("c"), porigin_c)]], pconstantclosure_c) = eps',
            '$trait_real_retired_receipt(S_failed, pconstantclosure_c[.PREFIX = $nabs($(pconstantclosure_c.PREFIX + 1))]) = eps',
            '$trait_real_retired_receipt(S_failed, pconstantclosure_c[.DECL = pconstantclosure_c.SITE]) = eps',
            '$trait_real_retired_receipt(S_failed, pconstantclosure_c[.SITE = porigin_c]) = eps',
            '$trait_real_retired_receipt(S_failed[.SOURCES = eps], pconstantclosure_c) = eps',
            'S_missing = S_failed[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY]',
            '$trait_real_retired_receipt(S_missing, pconstantclosure_c) = eps',
            '~$call_descriptors_valid(S_missing)',
            'S_table = S_failed[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_c pconstantclosure_c.SITE ptraitcachecause_c[.TABLE = eps]]]',
            '$trait_real_retired_receipt(S_table, pconstantclosure_c) = eps',
            'S_lookup = S_failed[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_c pconstantclosure_c.SITE ptraitcachecause_c[.LOOKUPS = eps]]]',
            '$trait_real_retired_receipt(S_lookup, pconstantclosure_c) = eps',
            'S_root = S_failed[.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_c pconstantclosure_c.SITE ptraitcachecause_c[.ROOT = pconstantclosure_c.SITE]]]',
            '$trait_real_retired_receipt(S_root, pconstantclosure_c) = eps',
            'S_duplicate = S_failed[.CLASSCONSTANTHISTORY = S_failed.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_c pconstantclosure_c.SITE ptraitcachecause_c]]',
            '~$class_constant_state_valid(S_duplicate)',
            '~$declaration_history_valid(S_failed[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause[.UNIT = $nabs($(pdeclcause.UNIT + 1))]]])',
        ],
    },
    'throwing-real-birth-retains-prior-public-cache-and-outside-handler-graph': {
        'source': SOURCES['throw-published-cache'], 'stage': STAGE,
        'checks': ['n_p = |S.OBJECTS|', 'n_c = $nabs($(n_p + 1))'] + BEFORE + RETIRED + PUBLIC + [
            'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_fatal 10',
            'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_p]',
            'S.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            'S_failed.ERRORHANDLER = S.ERRORHANDLER',
            'S.OBJECTS[n_handler] = REALCLOSURE porigin_handler ([DIRECT (POBJECT n_box)]) pstaticcell*',
            '(HOBJECT n_handler) <- S_failed.ALLOCATIONS',
            '(HOBJECT n_box) <- S_failed.ALLOCATIONS',
            '$heap_owners($heap_graph(S_failed), HOBJECT n_handler) = 1',
            '$heap_owners($heap_graph(S_failed), HOBJECT n_box) = 1',
            'S_done = $drive(S_failed, 3000)',
            'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S_done.COMPLETION = S_failed.COMPLETION',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_p)',
            '$constant_callable_record_valid(S_done, pconstantclosure_c)',
            '$call_descriptors_valid(S_done)',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'failed-real-cache-keeps-retired-c-distinct-from-later-published-e-birth': {
        'source': SOURCES['late-published-cache'], 'stage': STAGE,
        'checks': ['n_p = |S.OBJECTS|', 'n_c = $nabs($(n_p + 1))'] + BEFORE + RETIRED + PUBLIC + [
            'S_link.COMPLETION = STATICBYTES ptbytes_fatal 7',
            '$default_cache_at(S_link.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_c)',
            'pdefaultcache_c.VALUE = PARRAY n_array_c',
            '(HARRAY n_array_c) <- S_link.ALLOCATIONS',
            '~((HARRAY n_array_c) <- S_failed.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_failed), HARRAY n_array_c) = 0',
            '$trait_real_failed_bound(S_link, pclassconstantdesc_y, pdefaultcache_c.CLASS, ptraitcachecause_c)',
            'S_scalar = S_link[.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_p, pdefaultcache_c[.VALUE = PINT 17]]]',
            '~$trait_real_failed_bound(S_scalar, pclassconstantdesc_y, pdefaultcache_c.CLASS, ptraitcachecause_c)',
            '~$trait_failed_cache_ready(S_seed, S_scalar)',
            'S_done = $drive(S_failed, 3000)',
            'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S_done.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_fatal 7',
            '$class_named(S_done.CLASSNAMES, $ptascii("e")) = (porigin_e)',
            '$class_at(S_done.CLASSES, porigin_e) = (pclassdesc_e)',
            '$class_constant_desc(pclassdesc_e.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_e_y)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_e_y.ORIGIN) = (pdefaultcache_e)',
            'pdefaultcache_e.VALUE = PARRAY n_array_e',
            'n_array_e =/= n_array_c',
            'S_done.ARRAYS[n_array_e].ITEMS = (ENTRY (KINT 0) (DIRECT (POBJECT n_e))) :: pentry_e_tail*',
            'n_e =/= n_c',
            'n_e =/= n_p',
            '$constant_callable_record(S_done.CONSTANTCLOSURES, n_e) = (pconstantclosure_e)',
            'pconstantclosure_e.SITE = pconstantclosure_c.SITE',
            'pconstantclosure_e.PREFIX = |S_done.DECLARATIONS|',
            '$(pconstantclosure_c.PREFIX < pconstantclosure_e.PREFIX)',
            '$trait_real_birth_at(S_done.CLASSCONSTANTHISTORY, n_e) = eps',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_e) = (pclosurescope_e)',
            'pclosurescope_e.LEXICAL = porigin_e',
            'pclosurescope_e.CALLED = porigin_e',
            r'pclosurescope_e.RECEIVER = eps /\ pclosurescope_e.CREATION = eps',
            '$constant_callable_record_valid(S_done, pconstantclosure_e)',
            '$trait_real_retired_receipt(S_done, pconstantclosure_c) = (pclassconstantdesc_y)',
            '~((HOBJECT n_c) <- S_done.ALLOCATIONS)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_z.ORIGIN) = (pdefaultcache_p)',
            '$call_descriptors_valid(S_done)',
            '$declaration_history_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {key: value for key, value in CASES.items() if args.match in key}
    assert selected
    protocol.run(selected, (Path(__file__).resolve(), CATALOGUE, HELPERS))
