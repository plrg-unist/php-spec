#!/usr/bin/env python3
"""Fatal reserved names remain distinct from lookup and source permissions."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/semantics'
sys.path.insert(0, str(HERE))
import closure_call_protocol as protocol

CATALOGUE = HERE / 'trait_failed_name_cases.json'
HELPERS = HERE / 'trait_failed_name.watsup'
protocol.MODULES = [*protocol.MODULES, HELPERS]
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}


def b(text):
    return '$ptascii(' + json.dumps(text) + ')'


def stage(name):
    return ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
            'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
            '-- if S.ORIGIN = (porigin_c) '
            '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
            '-- if pclassdesc_c.NAME = ' + b(name))


def admission(state):
    return [f'$call_descriptors_valid({state})',
            f'$declaration_history_valid({state})',
            f'$class_constant_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def fatal(name, row):
    return admission('S') + [
        f'$class_named(S.CLASSNAMES, {b(name.lower())}) = eps',
        f'$failed_class_reserved(S, {b(name)}) = eps',
        '~$failed_class_pending(S, pclassdesc_c)',
        'S_seed = S[.TODO = ptask_tail*]',
        'pdeclcause = $declaration_cause(S_seed)',
        'PhpStep: S ~> S_after',
        f'S_after.DECLARATIONS = S.DECLARATIONS ++ [{row} porigin_c pdeclcause]',
        'S_after.CLASSES = S.CLASSES',
        'S_after.CLASSNAMES = S.CLASSNAMES',
        '$failed_class_count(S_after.DECLARATIONS, porigin_c) = 1',
        f'$failed_class_reserved(S_after, {b(name.swapcase())}) = (pclassdesc_c)',
        f'$class_named(S_after.CLASSNAMES, {b(name.lower())}) = eps',
        '$runtime_class_report_valid(S_after)',
    ] + admission('S_after')


def reject(old_name, new_name):
    return [
        f'$review_failed_name_statement(S_after, {b(new_name)}, 500) = (S_late)',
        'S_late.ORIGIN = (porigin_new)',
        '$class_at(S_late.CLASSES, porigin_new) = (pclassdesc_new)',
        'porigin_new =/= porigin_c',
        '$failed_class_pending(S_late, pclassdesc_new)',
        f'$failed_class_reserved(S_late, {b(new_name)}) = (pclassdesc_c)',
        'S_late.DECLARATIONS = S_after.DECLARATIONS',
    ] + admission('S_late') + [
        'PhpStep: S_late ~> S_rejected',
        'S_rejected.COMPLETION = STATICBYTES ptbytes_new pclassdesc_new.LINE',
        f'ptbytes_new = {b("Cannot redeclare class " + old_name + " (previously declared in ")} ++ $call_sourcefile(S.FILES, porigin_c) ++ [58] ++ $ntunsigned(pclassdesc_c.LINE) ++ [41]',
        'S_rejected.CLASSNAMES = S_late.CLASSNAMES',
        'S_rejected.CLASSES = S_late.CLASSES',
        'S_rejected.DECLARATIONS = S_late.DECLARATIONS',
        'S_rejected.CLASSCONSTANTCACHE = S_late.CLASSCONSTANTCACHE',
        'S_rejected.CLASSCONSTANTHISTORY = S_late.CLASSCONSTANTHISTORY',
        'S_rejected.CONSTANTCLOSURES = S_late.CONSTANTCLOSURES',
        'S_rejected.CLOSURESCOPES = S_late.CLOSURESCOPES',
        'S_rejected.OBJECTS = S_late.OBJECTS',
        'S_rejected.EVENTS = S_late.EVENTS',
        '$failed_class_report_origin(S_rejected) = eps',
        '$runtime_class_report_valid(S_rejected)',
    ] + admission('S_rejected')


DEAD = [
    'n_c = |S.OBJECTS|',
    '$constant_callable_record(S_after.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_c) = ((pconstantclosure_c.SITE, ptraitcachecause_c))',
    'ptraitcachecause_c.CLASS = porigin_c',
    '$trait_real_retired_receipt(S_after, pconstantclosure_c) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_c',
    '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_c) = eps',
    '~(HOBJECT n_c <- S_after.ALLOCATIONS)',
    '~$constant_callable_value_valid(S_after, n_c, pconstantclosure_c.SITE)',
    '$heap_owners($heap_graph(S_after), HOBJECT n_c) = 0',
]

CASES = {
    'cacheless-source-history-and-before-trait-binding-priority': {
        'source': ROWS['binding-priority']['source'], 'stage': stage('C'),
        'checks': fatal('C', 'PDRTRAITFAIL') + [
            'S_after.COMPLETION = STATICBYTES ptbytes_first 6',
            '$failed_class_report_origin(S_after) = (porigin_c)',
            'S_after.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
            'S_after.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'S_missing = S_after[.DECLARATIONS = S.DECLARATIONS]',
            '$failed_class_reserved(S_missing, $ptascii("c")) = eps',
            '~$runtime_class_report_valid(S_missing)',
            '~$declaration_history_valid(S_missing)',
            'S_duplicate = S_after[.DECLARATIONS = S_after.DECLARATIONS ++ [PDRTRAITFAIL porigin_c pdeclcause]]',
            '$failed_class_reserved(S_duplicate, $ptascii("c")) = eps',
            '~$declaration_history_valid(S_duplicate)',
            'S_unit = S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITFAIL porigin_c pdeclcause[.UNIT = 999]]]',
            '~$declaration_history_valid(S_unit)',
            'S_calls = S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITFAIL porigin_c pdeclcause[.CALLS = [(porigin_c, eps, eps, eps)]]]]',
            '~$declaration_history_valid(S_calls)',
            '~$declaration_history_valid(S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause]])',
            '~$declaration_history_valid(S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRCLASSFATAL porigin_c pdeclcause]])',
            'S_published = S_after[.CLASSNAMES = S_after.CLASSNAMES ++ [($ptascii("c"), porigin_c)]]',
            '$failed_class_reserved(S_published, $ptascii("c")) = eps',
            '~$declaration_history_valid(S_published)',
            '$failed_class_reserved(S_after[.SOURCES = eps], $ptascii("c")) = eps',
        ] + reject('C', 'c') + [
            '$trait_needs_binding(S_late, pclassdesc_new)',
            '$trait_plan(S_late, pclassdesc_new).TRAITS =/= eps',
            'S_late.TODO = ptask_late :: ptask_late_tail*',
            '~$failed_class_cacheless(S_late[.TODO = ptask_late_tail*], S_rejected, pclassdesc_new)',
            'pdeclcause_new = $declaration_cause(S_late)',
            '~$declaration_history_valid(S_rejected[.DECLARATIONS = S_rejected.DECLARATIONS ++ [PDRTRAITFAIL porigin_new pdeclcause_new]])',
            'S_later_fatal = S_rejected[.DECLARATIONS = S_rejected.DECLARATIONS ++ [PDRCLASSFATAL porigin_new pdeclcause_new]]',
            '$failed_class_header(S_later_fatal, PDRCLASSFATAL porigin_new pdeclcause_new, $ptascii("c")) = eps',
            '$failed_class_reserved(S_later_fatal, $ptascii("c")) = (pclassdesc_c)',
            '~$declaration_history_valid(S_later_fatal)',
        ],
    },
    'typed-real-qualified-name-reservation-with-dead-receipt': {
        'source': ROWS['namespace-typed']['source'], 'stage': stage('Ns\\C'),
        'checks': fatal('Ns\\C', 'PDRTRAITCACHEFAIL') + [
            'S_after.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_first 6',
            f'$failed_class_reserved(S_after, {b("C")}) = eps',
            f'$failed_class_reserved(S_after, {b("Other\\C")}) = eps',
        ] + DEAD + [
            'S_wrong_row = S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITFAIL porigin_c pdeclcause]]',
            '~$declaration_history_valid(S_wrong_row)',
            '$trait_real_retired_receipt(S_wrong_row, pconstantclosure_c) = eps',
            '~$declaration_history_valid(S_after[.DECLARATIONS = S.DECLARATIONS ++ [PDRCLASSFATAL porigin_c pdeclcause]])',
        ] + reject('Ns\\C', 'Ns\\c') + [
            '$trait_real_retired_receipt(S_rejected, pconstantclosure_c) = (pclassconstantdesc_y)',
            '~$constant_callable_value_valid(S_rejected, n_c, pconstantclosure_c.SITE)',
            '$closure_scope_at(S_rejected.CLOSURESCOPES, n_c) = eps',
        ],
    },
    'same-basename-in-distinct-namespace-keeps-failed-scope-dead': {
        'source': ROWS['distinct-namespace']['source'], 'stage': stage('A\\C'),
        'checks': fatal('A\\C', 'PDRTRAITCACHEFAIL') + DEAD + [
            f'$failed_class_reserved(S_after, {b("B\\C")}) = eps',
            f'$failed_class_reserved(S_after, {b("C")}) = eps',
            f'$review_failed_name_statement(S_after, {b("B\\C")}, 500) = (S_b)',
            'S_b.ORIGIN = (porigin_b)',
            '$class_at(S_b.CLASSES, porigin_b) = (pclassdesc_b)',
            'porigin_b =/= porigin_c',
            '~$failed_class_pending(S_b, pclassdesc_b)',
            'S_b.CURRENT = (pcallcontext_b)',
            'pcallcontext_b.FUNCTION = porigin_function_b',
            '$function_at($all_functions(S_b), porigin_function_b) = (pfunction_b)',
            f'pfunction_b.NAME = {b("B\\fill")}',
        ] + admission('S_b') + [
            'PhpStep: S_b ~> S_b_after',
            'S_b_after.COMPLETION = NORMAL',
            f'$class_named(S_b_after.CLASSNAMES, {b("b\\c")}) = (porigin_b)',
            f'$class_named(S_b_after.CLASSNAMES, {b("a\\c")}) = eps',
            f'$failed_class_reserved(S_b_after, {b("a\\C")}) = (pclassdesc_c)',
            '$trait_real_retired_receipt(S_b_after, pconstantclosure_c) = (pclassconstantdesc_y)',
            '~(HOBJECT n_c <- S_b_after.ALLOCATIONS)',
            '$closure_scope_at(S_b_after.CLOSURESCOPES, n_c) = eps',
            '$failed_class_count(S_b_after.DECLARATIONS, porigin_b) = 0',
            'pdeclcause_b = $declaration_cause(S_b)',
            '~$declaration_history_valid(S_b_after[.DECLARATIONS = S_b.DECLARATIONS ++ [PDRTRAITFAIL porigin_b pdeclcause_b]])',
        ] + admission('S_b_after') + [
            'pdeclcause_b.UNIT = 0',
            '|pdeclcause_b.CALLS| = 2',
            'pdeclcause_b.CALLS[0] = (porigin_function_first, porigin_site_first?, porigin_lexical_first?, porigin_called_first?)',
            'pdeclcause_b.CALLS[1] = (porigin_callback, eps, eps, eps)',
            'S_b.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
            'S_b.SHUTDOWN.INDEX = 0',
            'S_b.SHUTDOWN.ENTRIES = [pshutdownentry]',
            '$target_function(S_b, pshutdownentry.TARGET) = (pfunction_callback)',
            'pfunction_callback.ORIGIN = porigin_callback',
            '$shutdown_entry_valid(S_b, pshutdownentry)',
            '$declaration_shutdown_callback(S_b, porigin_callback, S_b.SHUTDOWN.ENTRIES) = (pshutdownentry)',
            '$declaration_cause_valid(S_b, porigin_b, pdeclcause_b)',
            'S_missing_queue = S_b_after[.SHUTDOWN.ENTRIES = eps]',
            '$declaration_shutdown_callback(S_missing_queue, porigin_callback, S_missing_queue.SHUTDOWN.ENTRIES) = eps',
            '~$declaration_history_valid(S_missing_queue)',
            'S_pending_queue = S_b_after[.SHUTDOWN.PHASE = SHUTDOWN_PENDING]',
            '$declaration_shutdown_callback(S_pending_queue, porigin_callback, S_pending_queue.SHUTDOWN.ENTRIES) = eps',
            '~$declaration_history_valid(S_pending_queue)',
            'pshutdownentry_wrong = pshutdownentry[.TARGET = porigin_function_b]',
            'S_wrong_queue = S_b_after[.SHUTDOWN.ENTRIES = [pshutdownentry_wrong]]',
            '$declaration_shutdown_callback(S_wrong_queue, porigin_callback, S_wrong_queue.SHUTDOWN.ENTRIES) = eps',
            '~$declaration_history_valid(S_wrong_queue)',
            'S_future_queue = S_b_after[.SHUTDOWN.ENTRIES = [pshutdownentry_wrong, pshutdownentry]]',
            '$shutdown_entry_valid(S_future_queue, pshutdownentry)',
            '$declaration_shutdown_callback(S_future_queue, porigin_callback, S_future_queue.SHUTDOWN.ENTRIES) = eps',
            '~$declaration_history_valid(S_future_queue)',
            '$declaration_shutdown_callback(S_b, porigin_callback, [pshutdownentry_wrong]) = eps',
            '$declaration_shutdown_callback(S_b, porigin_function_b, S_b.SHUTDOWN.ENTRIES) = eps',
            'pdeclcause_lexical = pdeclcause_b[.CALLS = [(porigin_function_first, porigin_site_first?, porigin_lexical_first?, porigin_called_first?), (porigin_callback, eps, (porigin_c), eps)]]',
            '~$declaration_cause_valid(S_b, porigin_b, pdeclcause_lexical)',
            '~$declaration_history_valid(S_b_after[.DECLARATIONS = S_b.DECLARATIONS ++ [PDRCLASS porigin_b pdeclcause_lexical]])',
            'pdeclcause_called = pdeclcause_b[.CALLS = [(porigin_function_first, porigin_site_first?, porigin_lexical_first?, porigin_called_first?), (porigin_callback, eps, eps, (porigin_b))]]',
            '~$declaration_cause_valid(S_b, porigin_b, pdeclcause_called)',
            '~$declaration_history_valid(S_b_after[.DECLARATIONS = S_b.DECLARATIONS ++ [PDRCLASS porigin_b pdeclcause_called]])',
            'pdeclcause_site = pdeclcause_b[.CALLS = [(porigin_function_first, porigin_site_first?, porigin_lexical_first?, porigin_called_first?), (porigin_callback, (pshutdownentry.CALL.SITE), eps, eps)]]',
            '~$declaration_cause_valid(S_b, porigin_b, pdeclcause_site)',
            '~$declaration_history_valid(S_b_after[.DECLARATIONS = S_b.DECLARATIONS ++ [PDRCLASS porigin_b pdeclcause_site]])',
            'PhpStep: S_b_after ~> S_b_next',
            'S_b_next.COMPLETION = NORMAL',
        ] + admission('S_b_next') + [
            'S_done = $drive_steps(S_b_next, 500)',
            'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S_done.SHUTDOWN.INDEX = 1',
            'S_done.COMPLETION = S_done.SHUTDOWN.COMPLETION',
            '$trait_real_retired_receipt(S_done, pconstantclosure_c) = (pclassconstantdesc_y)',
            f'$class_named(S_done.CLASSNAMES, {b("b\\c")}) = (porigin_b)',
            f'$class_named(S_done.CLASSNAMES, {b("a\\c")}) = eps',
            '~(HOBJECT n_c <- S_done.ALLOCATIONS)',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_c) = eps',
        ] + admission('S_done'),
    },
    'returning-link-error-releases-name-before-later-casefold-publication': {
        'source': ROWS['catchable-link-cleanup']['source'], 'stage': stage('C'),
        'checks': admission('S') + [
            'S.CURRENT = (pcallcontext_first)',
            '$trait_plan(S, pclassdesc_c).TRAITS = eps',
            'S_seed = S[.TODO = ptask_tail*]',
            'PhpStep: S ~> S_error',
            'S_error.COMPLETION = THROWN "Error" $ptascii("Class \\\"MissingParent\\\" not found") 2',
            'S_error.DECLARATIONS = S.DECLARATIONS',
            'S_error.CLASSNAMES = S.CLASSNAMES',
            '$failed_class_count(S_error.DECLARATIONS, porigin_c) = 0',
            '$failed_class_reserved(S_error, $ptascii("C")) = eps',
            '~$failed_class_cacheless(S_seed, S_error, pclassdesc_c)',
            '$review_failed_name_statement(S_error, $ptascii("c"), 500) = (S_late)',
            'S_late.ORIGIN = (porigin_new)',
            '$class_at(S_late.CLASSES, porigin_new) = (pclassdesc_new)',
            'porigin_new =/= porigin_c',
            '$class_named(S_late.CLASSNAMES, $ptascii("c")) = eps',
            '$failed_class_reserved(S_late, $ptascii("C")) = eps',
            '~$failed_class_pending(S_late, pclassdesc_new)',
        ] + admission('S_late') + [
            'PhpStep: S_late ~> S_after',
            'S_after.COMPLETION = NORMAL',
            '$class_named(S_after.CLASSNAMES, $ptascii("c")) = (porigin_new)',
            '$failed_class_count(S_after.DECLARATIONS, porigin_c) = 0',
            '$failed_class_count(S_after.DECLARATIONS, porigin_new) = 0',
            '$failed_class_reserved(S_after, $ptascii("C")) = eps',
        ] + admission('S_after'),
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, HELPERS))
