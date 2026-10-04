#!/usr/bin/env python3
"""Reached collision failures preserve source authority and drop temporary owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
FUNCTIONS = HERE / 'trait_data_collision_error_function_review_cases.json'
OPERATIONS = HERE / 'trait_data_collision_error_review_cases.json'
SOURCES = {row['id']: row['source']
           for path in (FUNCTIONS, OPERATIONS)
           for row in json.loads(path.read_text())['cases']}

STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

BINDINGS = [
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    '$ppproperty_desc_at(pclassdesc_c.PROPERTIES, $ptascii("x")) = (ppropertydesc_c)',
    '$ppproperty_desc_at(pclassdesc_t.PROPERTIES, $ptascii("x")) = (ppropertydesc_t)',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
]

RECORD_AUTHORITY = [
    'F_error.RECORD = (pfrecorder)',
    'pfrecorder.CLASS = porigin_c',
    'pfrecorder.ROOT = porigin_root',
    'porigin_root = PORIGIN n_source pcpath_root',
    '$trait_recording(F_error, pcpath_root)',
    '$trait_fold_owner(F_error) = (porigin_c)',
    'F_error.EXTERNAL = (S)',
    'F_error.MEMORY.ERRORHANDLER.CALLBACK = eps',
    '~$trait_recording(F_error[.RECORD = eps], pcpath_root)',
    '~$trait_recording(F_error[.EXTERNAL = eps], pcpath_root)',
    '~$trait_recording(F_error[.RECORD = (pfrecorder[.CLASS = porigin_t])], pcpath_root)',
    '~$trait_recording(F_error[.RECORD = (pfrecorder[.ROOT = porigin_c])], pcpath_root)',
    '~$trait_recording(F_error[.EXTERNAL = (S[.SOURCES = eps])], pcpath_root)',
    '~$trait_recording(F_error[.CLASSCONTEXT = eps], pcpath_root)',
    '~$trait_recording(F_error[.MEMORY = F_error.MEMORY[.CONSTCONTEXT = eps]], pcpath_root)',
    '~$trait_recording(F_error, eps)',
    '$trait_fold_error(F_error) = (ptraitdataerror)',
    'F_error.VALUE = eps',
    'ptraitdataerror.OWNER = porigin_c',
    'F_error.MEMORY.COMPLETION = THROWN ptraitdataerror.KIND ptraitdataerror.MESSAGE ptraitdataerror.LINE',
    'F_error.MEMORY.ERRORORIGIN = (porigin_c)',
    'F_retraced = $trait_collision_raise(F_error, pcpath_root, F_error.MEMORY[.TRACE = eps], ptraitdataerror.KIND, ptraitdataerror.MESSAGE, ptraitdataerror.LINE)',
    'F_retraced.MEMORY.TRACE = ptraitdataerror.TRACE',
]

TERMINAL = [
    'S_failed = $activate_class_body(S, pclassdesc_c)',
    'S_failed.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_fatal pclassdesc_c.LINE',
    'ptbytes_fatal_rendered = $ptascii("Fatal error: ") ++ ptbytes_fatal ++ $ptascii(" in ") ++ $call_sourcefile(S.FILES, porigin_c) ++ $ptascii(" on line ") ++ $decimal_integer(pclassdesc_c.LINE) ++ [10]',
    'S_failed.CLASSES = S.CLASSES',
    'S_failed.CLASSNAMES = S.CLASSNAMES',
    'S_failed.DECLARATIONS = S.DECLARATIONS',
    'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    'S_failed.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
    'S_failed.ERRORHANDLER = S.ERRORHANDLER',
    'S_failed.CURRENT = S.CURRENT',
    'S_failed.FRAMES = S.FRAMES',
    'S_failed.TRACE = eps',
    'S_failed.ERRORFATALTRACE = eps',
    'S_failed.RESULT = S.RESULT',
    '$iterator_notice_seeds(S_failed.TODO) = eps',
    'S_failed.ALLOCATIONS = S.ALLOCATIONS',
    'S_failed.OBJECTPROPS = S.OBJECTPROPS',
    'n_error = |S.OBJECTS|',
    'S_failed.OBJECTS[n_error] = THROWABLE pthrowable_error',
    '~((HOBJECT n_error) <- S_failed.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_failed), HOBJECT n_error) = 0',
    '$heap_valid($heap_graph(S_failed))',
    '$declaration_history_valid(S_failed)',
]

CASES = {
    'bare-first-error-keeps-real-function-trace-and-skips-incoming-warning': {
        'source': SOURCES['bare-property-error-keeps-real-function-trace-without-fake-expression-frame'],
        'stage': STAGE,
        'checks': BINDINGS + [
            'S.CURRENT = (pcallcontext)',
            '$call_current_valid(S)',
            'ppropertydesc_c.DEFAULT = PROP_DEFERRED porigin_root',
            '$trait_member_fold(S, pclassdesc_c, porigin_root) = (F_error)',
        ] + RECORD_AUTHORITY + [
            'ptraitdataerror.KIND = "Error"',
            'ptraitdataerror.MESSAGE = $ptascii("Undefined constant ") ++ [34] ++ $ptascii("DOES_NOT_EXIST") ++ [34]',
            'ptraitdataerror.LINE = 6',
            'ptraitdataerror.TRACE = [ptraceframe_build]',
            'ptraceframe_build.FUNCTION = $ptascii("build")',
            'ptraceframe_build.LINE = 9',
            'ptraceframe_build.CLASS = eps',
            'F_error.RECORDED = eps',
            'ptraitdatacomparison = $trait_data_compare_left(S, pclassdesc_c, ppropertydesc_c, ppropertydesc_t, TRAITVALUEERROR F_error.MEMORY ptraitdataerror eps)',
            'ptraitdatacomparison.CHECK = TRAITDATAERROR ptraitdataerror',
            'ptraitdatacomparison.NOTICES = eps',
            'ptraitdatacomparison.MEMORY = (F_error.MEMORY)',
        ] + TERMINAL + [
            '$(|S_failed.EVENTS| = |S.EVENTS| + 2)',
            'S_failed.EVENTS[0:|S.EVENTS|] = S.EVENTS',
            'S_failed.EVENTS[|S.EVENTS|:2] = [DIAGNOSTIC_SOURCE n_source "Warning" ptbytes_error 6, STDERR ptbytes_fatal_rendered]',
            'pthrowable_error.KIND = "Error"',
        ],
    },
    'failed-array-key-default-flush-discards-error-and-scratch-array-owners': {
        'source': SOURCES['collision-array-key-error-retains-earlier-value-warning'],
        'stage': STAGE,
        'checks': BINDINGS + [
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            'ppropertydesc_t.DEFAULT = PROP_DEFERRED porigin_root',
            '$trait_member_fold(S, pclassdesc_c, porigin_root) = (F_error)',
        ] + RECORD_AUTHORITY + [
            'ptraitdataerror.KIND = "TypeError"',
            'ptraitdataerror.MESSAGE = $ptascii("Cannot access offset of type array on array")',
            'ptraitdataerror.LINE = 3',
            'ptraitdataerror.TRACE = [ptraceframe_expression]',
            'ptraceframe_expression.FUNCTION = $ptascii("[constant expression]")',
            'ptraceframe_expression.LINE = 5',
            'ptraceframe_expression.CLASS = eps',
            'F_error.RECORDED = [pfdiagnostic]',
            'pfdiagnostic.OWNER = porigin_c',
            'pfdiagnostic.LEVEL = 8192',
            'pfdiagnostic.LINE = 3',
            'pfdiagnostic.MESSAGE = $deprecated_constant_message()',
        ] + TERMINAL + [
            '$(|S_failed.EVENTS| = |S.EVENTS| + 3)',
            'S_failed.EVENTS[0:|S.EVENTS|] = S.EVENTS',
            'S_failed.EVENTS[|S.EVENTS|:3] = [DIAGNOSTIC_SOURCE n_source "Deprecated" $deprecated_constant_message() 3, DIAGNOSTIC_SOURCE n_source "Warning" ptbytes_error 3, STDERR ptbytes_fatal_rendered]',
            'pthrowable_error.KIND = "TypeError"',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), FUNCTIONS, OPERATIONS))
