#!/usr/bin/env python3
"""Genuine fatal name reservation, dead receipts and binding precedence."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_failed_name_cases.json'
HELPERS = HERE / 'trait_failed_name.watsup'
protocol.MODULES = [*protocol.MODULES, HELPERS]
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

BEFORE = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$failed_class_reserved(S, $ptascii("C")) = eps',
    '~$failed_class_pending(S, pclassdesc_c)',
    'S_seed = S[.TODO = ptask_tail*]',
    'pdeclcause = $declaration_cause(S_seed)',
    'PhpStep: S ~> S_after',
    'S_after.COMPLETION = STATICBYTES ptbytes_first z_first',
    'z_first = pclassdesc_c.LINE',
    'S_after.CLASSES = S.CLASSES',
    'S_after.CLASSNAMES = S.CLASSNAMES',
    '$failed_class_count(S_after.DECLARATIONS, porigin_c) = 1',
    '$failed_class_reserved(S_after, $ptascii("c")) = (pclassdesc_c)',
    '$failed_class_reserved(S_after, $ptascii("C")) = (pclassdesc_c)',
    r'$failed_class_reserved(S_after, $ptascii("N\\C")) = eps',
    '$failed_class_report_origin(S_after) = (porigin_c)',
    '$runtime_class_report_valid(S_after)',
    '$call_descriptors_valid(S_after)',
    '$declaration_history_valid(S_after)',
    '$class_constant_state_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
]

REDECLARE = [
    '$review_failed_name_statement(S_after, $ptascii("c"), 400) = (S_redeclare)',
    '$call_descriptors_valid(S_redeclare)',
    '$declaration_history_valid(S_redeclare)',
    '$class_constant_state_valid(S_redeclare)',
    '$heap_valid($heap_graph(S_redeclare))',
    'S_redeclare.ORIGIN = (porigin_new)',
    '$class_at(S_redeclare.CLASSES, porigin_new) = (pclassdesc_new)',
    'pclassdesc_new.ORIGIN =/= porigin_c',
    '$failed_class_pending(S_redeclare, pclassdesc_new)',
    '$class_named(S_redeclare.CLASSNAMES, $ptascii("c")) = eps',
    '$failed_class_reserved(S_redeclare, $ptascii("c")) = (pclassdesc_c)',
    'S_redeclare.DECLARATIONS = S_after.DECLARATIONS',
    'PhpStep: S_redeclare ~> S_rejected',
    'S_rejected.COMPLETION = STATICBYTES ptbytes_message z_new',
    'z_new = pclassdesc_new.LINE',
    'ptbytes_message = $ptascii("Cannot redeclare class C (previously declared in ") ++ $call_sourcefile(S_rejected.FILES, porigin_c) ++ [58] ++ $ntunsigned(pclassdesc_c.LINE) ++ [41]',
    'S_rejected.CLASSES = S_redeclare.CLASSES',
    'S_rejected.CLASSNAMES = S_redeclare.CLASSNAMES',
    'S_rejected.DECLARATIONS = S_redeclare.DECLARATIONS',
    'S_rejected.CLASSCONSTANTCACHE = S_redeclare.CLASSCONSTANTCACHE',
    'S_rejected.CLASSCONSTANTHISTORY = S_redeclare.CLASSCONSTANTHISTORY',
    'S_rejected.CONSTANTCLOSURES = S_redeclare.CONSTANTCLOSURES',
    'S_rejected.OBJECTS = S_redeclare.OBJECTS',
    'S_rejected.CLOSURESCOPES = S_redeclare.CLOSURESCOPES',
    'S_rejected.ALLOCATIONS = S_redeclare.ALLOCATIONS',
    'S_rejected.TRACE = $eval_exception_trace(S_redeclare)',
    'S_rejected.ERRORORIGIN = eps',
    '$failed_class_report_origin(S_rejected) = eps',
    '$call_descriptors_valid(S_rejected)',
    '$declaration_history_valid(S_rejected)',
    '$class_constant_state_valid(S_rejected)',
    '$heap_valid($heap_graph(S_rejected))',
    'S_shown = $shutdown_freeze(S_rejected[.REPORTING = 64])',
    'S_shown.COMPLETION = REQUESTFATAL ptbytes_kind ptbytes_message z_new',
    'ptbytes_kind = $ptascii("CompileError")',
    r'$(|S_shown.EVENTS| > |S_rejected.EVENTS|)',
    'S_hidden = $shutdown_freeze(S_rejected[.REPORTING = 1])',
    'S_hidden.EVENTS = S_rejected.EVENTS',
]

CASES = {
    'cacheless-fatal-reserves-before-parent-autoload': {
        'source': ROWS['autoload-priority']['source'],
        'stage': STAGE,
        'checks': BEFORE + [
            'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITFAIL porigin_c $declaration_cause(S_seed)]',
            'S_after.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY',
            'S_after.CLASSCONSTANTCACHE = S_seed.CLASSCONSTANTCACHE',
            'S_after.CONSTANTCLOSURES = S_seed.CONSTANTCLOSURES',
            'S_absent = S_after[.DECLARATIONS = S_seed.DECLARATIONS]',
            '$failed_class_reserved(S_absent, $ptascii("c")) = eps',
            '~$runtime_class_report_valid(S_absent)',
            '~$declaration_history_valid(S_absent)',
            'S_duplicate = S_after[.DECLARATIONS = S_after.DECLARATIONS ++ [PDRTRAITFAIL porigin_c $declaration_cause(S_seed)]]',
            '$failed_class_reserved(S_duplicate, $ptascii("c")) = eps',
            '~$declaration_history_valid(S_duplicate)',
            'S_bad_cause = S_after[.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITFAIL porigin_c pdeclcause[.UNIT = 20]]]',
            '~$declaration_history_valid(S_bad_cause)',
        ] + REDECLARE + [
            'pclassdesc_new.PARENT = ($ptascii("MissingParent"))',
            '$autoload_pending(S_redeclare, $ptascii("MissingParent"))',
            '~$autoload_parent_pending(S_redeclare, pclassdesc_new)',
            'S_rejected.EVENTS = S_redeclare.EVENTS',
            'S_rejected.AUTOLOAD = S_redeclare.AUTOLOAD',
        ],
    },
    'failed-real-receipt-reserves-name-without-live-class': {
        'source': ROWS['casefold-hard']['source'],
        'stage': STAGE,
        'checks': BEFORE + [
            'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c $declaration_cause(S_seed)]',
            'n_object = |S_seed.OBJECTS|',
            '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_object) = ((porigin_site, ptraitcachecause))',
            '$constant_callable_record(S_after.CONSTANTCLOSURES, n_object) = (pconstantclosure)',
            '$trait_real_retired_receipt(S_after, pconstantclosure) = (pclassconstantdesc_y)',
            '~(HOBJECT n_object <- S_after.ALLOCATIONS)',
            '$closure_scope_at(S_after.CLOSURESCOPES, n_object) = eps',
            '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
            '~$constant_callable_value_valid(S_after, n_object, porigin_site)',
        ] + REDECLARE + [
            '$trait_real_retired_receipt(S_redeclare, pconstantclosure) = (pclassconstantdesc_y)',
            '$trait_real_retired_receipt(S_rejected, pconstantclosure) = (pclassconstantdesc_y)',
            '~(HOBJECT n_object <- S_rejected.ALLOCATIONS)',
            '$closure_scope_at(S_rejected.CLOSURESCOPES, n_object) = eps',
            '~$constant_callable_value_valid(S_rejected, n_object, porigin_site)',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, HELPERS))
