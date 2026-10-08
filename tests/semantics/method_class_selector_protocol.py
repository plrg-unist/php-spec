#!/usr/bin/env python3
"""Source-derived static selector lifetime and captured-target checks."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('method_class_selector_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())}
GUARDS = ['$call_descriptors_valid(S)', '$class_state_valid(S)',
          '$heap_valid($heap_graph(S))']
DIRECT_TARGET = 'STATIC_METHOD_TARGET porigin_class porigin_method'
DIRECT_ARGS = f'CALL_ARGS ({DIRECT_TARGET}) phpType7* 0 eps (porigin_site) z'
DIRECT_SEND = f'CALL_SEND ({DIRECT_TARGET}) phpType7* 0 eps (porigin_site) z'
DIRECT_BODY = ('S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = '
               + DIRECT_TARGET)

CASES = {
    'static-direct-before-argument': {
        'source': SOURCES['direct-static-argument-lifetime'],
        'stage': f'S.TODO = ({DIRECT_ARGS}) :: ptask_tail*',
        'checks': [
            '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_selector)',
            '(HOBJECT n_selector) <- S.ALLOCATIONS',
            '$target_nodes(' + DIRECT_TARGET + ') = eps',
            '$target_receiver(S, ' + DIRECT_TARGET + ') = eps',
            '$target_function(S, ' + DIRECT_TARGET + ') = (pfunction)',
            '$target_function(S, METHOD_TARGET n_selector porigin_method) = (pfunction)',
            '$call_task_valid(S, ' + DIRECT_ARGS + ')',
            *GUARDS,
            '~$call_selected_valid(S, METHOD_TARGET n_selector porigin_method, (porigin_site))',
            '~$call_task_valid(S, CALL_ARGS (METHOD_TARGET n_selector porigin_method) phpType7* 0 eps (porigin_site) z)',
            '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n_selector porigin_method) phpType7* 0 eps (porigin_site) z) :: ptask_tail*])',
            '~$call_task_valid(S, CALL_ARGS (' + DIRECT_TARGET + ') phpType7* 0 eps (porigin_site) $(z + 100))',
            '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (' + DIRECT_TARGET + ') phpType7* 0 eps (porigin_site) $(z + 100)) :: ptask_tail*])',
            '~$call_selected_valid(S, ' + DIRECT_TARGET + ', (porigin_class))',
        ],
    },
    'static-direct-after-argument': {
        'source': SOURCES['direct-static-argument-lifetime'],
        'stage': f'S.TODO = ({DIRECT_SEND}) :: ptask_tail* -- if S.RESULT = KNOWN (PINT 0)',
        'checks': [
            'S.OBJECTS[0] = INSTANCE porigin_class',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("r")) = (n_refcell)',
            'S.STORE[n_refcell] = DEFINED (PSTRING $ptascii("s"))',
            '$propref_at(S.PROPREFS, n_refcell) = eps',
            '$target_nodes(' + DIRECT_TARGET + ') = eps',
            '$target_function(S, ' + DIRECT_TARGET + ') = (pfunction)',
            '$call_task_valid(S, ' + DIRECT_SEND + ')',
            *GUARDS,
            '~$call_task_valid(S, CALL_SEND (' + DIRECT_TARGET + ') phpType7* 0 eps (porigin_class) z)',
            '~$call_descriptors_valid(S[.TODO = (CALL_SEND (' + DIRECT_TARGET + ') phpType7* 0 eps (porigin_class) z) :: ptask_tail*])',
        ],
    },
    'static-direct-body-after-retirement': {
        'source': SOURCES['direct-static-argument-lifetime'],
        'stage': DIRECT_BODY,
        'checks': [
            'S.OBJECTS[0] = INSTANCE porigin_class',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            'pcallcontext.INSTANCE = eps', 'pcallcontext.RECEIVER = eps',
            'pcallcontext.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext.CALLED_CLASS = (porigin_class)',
            'S.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("r")) = (n_refcell)',
            'S.STORE[n_refcell] = DEFINED (PSTRING $ptascii("s"))',
            '$propref_at(S.PROPREFS, n_refcell) = eps',
            '$trace_context_type(S, pcallcontext) = ($ptascii("::"))',
            '$trace_context_class(S, pcallcontext) = ($ptascii("A"))',
            '$target_function(S, ' + DIRECT_TARGET + ') = (pfunction)',
            *GUARDS,
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.TARGET = METHOD_TARGET 0 porigin_method])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.RECEIVER = (0)])])',
        ],
    },
    'static-scoped-before-name': {
        'source': SOURCES['scoped-static-name-detach'],
        'stage': ('S.TODO = (AT porigin_name (EVAL expression_name)) :: '
                  '(SCOPED_NAME phpType19 poperand phpType7* z) :: ptask_tail*'),
        'checks': [
            'poperand = KNOWN (PSTRING $ptascii("A"))',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_selector)',
            '(HOBJECT n_selector) <- S.ALLOCATIONS',
            '$task_nodes(SCOPED_NAME phpType19 poperand phpType7* z) = eps',
            '$call_task_valid(S, SCOPED_NAME phpType19 poperand phpType7* z)',
            *GUARDS,
            '~$call_task_valid(S, SCOPED_NAME phpType19 (KNOWN (POBJECT n_selector)) phpType7* z)',
            '~$call_descriptors_valid(S[.TODO = (AT porigin_name (EVAL expression_name)) :: (SCOPED_NAME phpType19 (KNOWN (POBJECT n_selector)) phpType7* z) :: ptask_tail*])',
            '~$call_task_valid(S, SCOPED_NAME phpType19 poperand phpType7* $(z + 100))',
        ],
    },
    'static-scoped-after-name-retirement': {
        'source': SOURCES['scoped-static-name-detach'],
        'stage': ('S.TODO = (SCOPED_NAME phpType19 poperand phpType7* z) :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (PSTRING $ptascii("f"))'),
        'checks': [
            'poperand = KNOWN (PSTRING $ptascii("A"))',
            'S.OBJECTS[0] = INSTANCE porigin_class',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            '$lookup(S.ENV, $ptascii("r")) = (n_refcell)',
            'S.STORE[n_refcell] = DEFINED (PSTRING $ptascii("s"))',
            '$propref_at(S.PROPREFS, n_refcell) = eps',
            '$call_task_valid(S, SCOPED_NAME phpType19 poperand phpType7* z)',
            *GUARDS,
            'S_after = $drive_steps(S[.COMPLETION = NORMAL], 1)',
            'S_after.TODO = (CALL_ARGS (SCOPED_TARGET porigin_class porigin_method porigin_class eps poperand) phpType7* 0 eps (porigin_site) z) :: METHOD_RESULT :: ptask_tail*',
            '$target_nodes(SCOPED_TARGET porigin_class porigin_method porigin_class eps poperand) = eps',
            '$target_function(S_after, SCOPED_TARGET porigin_class porigin_method porigin_class eps poperand) = (pfunction)',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            '~$call_selected_valid(S_after, SCOPED_TARGET porigin_class porigin_method porigin_class eps (KNOWN (POBJECT 0)), (porigin_site))',
        ],
    },
    'scoped-instance-keeps-receiver': {
        'source': SOURCES['scoped-instance-receiver-lifetime'],
        'stage': ('S.TODO = (CALL_SEND (SCOPED_TARGET porigin_class porigin_method '
                  'porigin_class (n_receiver) poperand) phpType7* 0 eps '
                  '(porigin_site) z) :: ptask_tail* -- if S.RESULT = KNOWN (PINT 0)'),
        'checks': [
            'poperand = KNOWN (PSTRING $ptascii("A"))',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '(HOBJECT n_receiver) <- $target_nodes(SCOPED_TARGET porigin_class porigin_method porigin_class (n_receiver) poperand)',
            'S.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("r")) = (n_refcell)',
            'S.STORE[n_refcell] = DEFINED (PINT 1)',
            '$propref_at(S.PROPREFS, n_refcell) = (ppropref)',
            *GUARDS,
            '~$call_selected_valid(S, SCOPED_TARGET porigin_class porigin_method porigin_class eps poperand, (porigin_site))',
            '~$call_selected_valid(S, STATIC_METHOD_TARGET porigin_class porigin_method, (porigin_site))',
        ],
    },
    'static-fetched-name-keeps-original-value': {
        'source': SOURCES['direct-static-name-before-selection'],
        'stage': DIRECT_BODY,
        'checks': [
            'S.OBJECTS[0] = INSTANCE porigin_class',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            'S.GLOBALTABLE = (psymboltable)',
            '$lookup(psymboltable.ENV, $ptascii("r")) = (n_refcell)',
            'S.STORE[n_refcell] = DEFINED (PINT 1)',
            '$propref_at(S.PROPREFS, n_refcell) = eps',
            'pcallcontext.RECEIVER = eps',
            *GUARDS,
        ],
    },
    'static-lexical-private-owner-and-called-class': {
        'source': SOURCES['direct-static-lexical-private-parent'],
        'stage': DIRECT_BODY,
        'checks': [
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("C")',
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            '$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("P")',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
            'pcallcontext.CALLED_CLASS = (porigin_class)',
            'pcallcontext.RECEIVER = eps',
            '$trace_context_class(S, pcallcontext) = ($ptascii("P"))',
            '$trace_context_type(S, pcallcontext) = ($ptascii("::"))',
            '$effective_method(S, porigin_class, $ptascii("f"), |S.CLASSES|) = (pmethoddesc_child)',
            '$target_function(S, STATIC_METHOD_TARGET porigin_class pmethoddesc_child.FUNCTION.ORIGIN) = (pfunction_child)',
            '~$call_selected_valid(S, STATIC_METHOD_TARGET porigin_class pmethoddesc_child.FUNCTION.ORIGIN, pcallcontext.CALLSITE)',
            *GUARDS,
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_class)])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (pmethoddesc.OWNER)])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.TARGET = STATIC_METHOD_TARGET pmethoddesc.OWNER porigin_method])])',
        ],
    },
    'static-first-class-conversion': {
        'source': SOURCES['direct-static-first-class'],
        'stage': ('S.TODO = (METHOD_CONVERT (' + DIRECT_TARGET
                  + ') porigin_site z) :: ptask_tail*'),
        'checks': [
            '$target_nodes(' + DIRECT_TARGET + ') = eps',
            '$method_capture_requested(S, ' + DIRECT_TARGET + ') = (porigin_class)',
            '$call_task_valid(S, METHOD_CONVERT (' + DIRECT_TARGET + ') porigin_site z)',
            *GUARDS,
            '~$call_task_valid(S, METHOD_CONVERT (METHOD_TARGET 0 porigin_method) porigin_site z)',
            '~$call_task_valid(S, METHOD_CONVERT (' + DIRECT_TARGET + ') porigin_site $(z + 100))',
            'S_after = $drive_steps(S[.COMPLETION = NORMAL], 1)',
            'S_after.RESULT = KNOWN (POBJECT n_closure)',
            'S_after.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_class eps',
            '$closure_scope_at(S_after.CLOSURESCOPES, n_closure) = (pclosurescope)',
            'pclosurescope.RECEIVER = eps',
            'pclosurescope.CALLED = porigin_class',
            '$node_children(S_after, HOBJECT n_closure) = eps',
            '$call_descriptors_valid(S_after)', '$closure_state_valid(S_after)',
            '$heap_valid($heap_graph(S_after))',
        ],
    },
    'static-private-first-class-conversion': {
        'source': SOURCES['direct-static-private-first-class'],
        'stage': ('S.TODO = (METHOD_CONVERT (' + DIRECT_TARGET
                  + ') porigin_site z) :: ptask_tail*'),
        'checks': [
            '$call_task_valid(S, METHOD_CONVERT (' + DIRECT_TARGET + ') porigin_site z)',
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("C")',
            *GUARDS,
            'S_after = $drive_steps(S[.COMPLETION = NORMAL], 1)',
            'S_after.RESULT = KNOWN (POBJECT n_closure)',
            'S_after.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_class eps',
            '$closure_scope_at(S_after.CLOSURESCOPES, n_closure) = (pclosurescope)',
            'pclosurescope.LEXICAL = pmethoddesc.OWNER',
            'pclosurescope.CALLED = porigin_class',
            'pclosurescope.RECEIVER = eps',
            '$closure_source_class(S_after, porigin_site) = (pmethoddesc.OWNER)',
            '$effective_method(S_after, porigin_class, pmethoddesc.NAME, |S_after.CLASSES|) = (pmethoddesc_child)',
            'pmethoddesc_child.FUNCTION.ORIGIN =/= porigin_method',
            '$method_class_selected(S_after, porigin_class, pmethoddesc.NAME, (pmethoddesc.OWNER)) = (pmethoddesc)',
            '$method_capture_live(S_after, pmethoddesc, porigin_site, porigin_class, pclosurescope)',
            '$closure_scope_row_valid(S_after, pclosurescope)',
            '$closure_state_valid(S_after)',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            '~$method_capture_live(S_after, pmethoddesc_child, porigin_site, porigin_class, pclosurescope[.LEXICAL = porigin_class])',
            '~$closure_scope_row_valid(S_after, pclosurescope[.LEXICAL = porigin_class])',
        ],
    },
    'static-live-selector-rejects-context-instance': {
        'source': SOURCES['direct-static-body-trace'],
        'stage': DIRECT_BODY,
        'checks': [
            '(HOBJECT 0) <- S.ALLOCATIONS',
            'S.OBJECTS[0] = INSTANCE porigin_class',
            'pcallcontext.INSTANCE = eps',
            '$target_instance(pcallcontext.TARGET) = eps',
            *GUARDS,
            '$trace_context_class(S, pcallcontext) = ($ptascii("A"))',
            'pcallcontext_bad = pcallcontext[.INSTANCE = (0)]',
            'S_bad = S[.CURRENT = (pcallcontext_bad)]',
            '~$call_context_valid(S_bad, pcallcontext_bad, S_bad.CVS)',
            '~$call_descriptors_valid(S_bad)',
            '$heap_valid($heap_graph(S_bad))',
        ],
    },
    'captured-method-saved-instance': {
        'source': SOURCES['method-wrapper-instance-coexistence'],
        'stage': ('S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.CONTEXT = (pcallcontext_saved) '
                  '-- if pcallcontext_saved.TARGET = CLOSURE_TARGET n_closure '
                  '-- if S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_class eps'),
        'checks': [
            'pcallcontext.INSTANCE = eps',
            'pcallcontext_saved.INSTANCE = (n_closure)',
            '$target_instance(pcallcontext_saved.TARGET) = (n_closure)',
            '$closure_scope_at(S.CLOSURESCOPES, n_closure) = (pclosurescope)',
            'pclosurescope.RECEIVER = eps',
            '$class_at(S.CLASSES, pclosurescope.LEXICAL) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("P")',
            '$class_at(S.CLASSES, pclosurescope.CALLED) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("C")',
            '$call_current_valid(S)', '$call_saved_context_valid(S, pframe)',
            '$closure_state_valid(S)', *GUARDS,
            'pframe_bad = pframe[.CONTEXT = (pcallcontext_saved[.INSTANCE = eps])]',
            'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
            '~$call_saved_context_valid(S_bad, pframe_bad)',
            '~$call_descriptors_valid(S_bad)',
            '$heap_valid($heap_graph(S_bad))',
        ],
    },
    'closure-call-current-instance': {
        'source': SOURCES['method-wrapper-instance-coexistence'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver'),
        'checks': [
            'pcallcontext.INSTANCE = (n_source)',
            '$target_instance(pcallcontext.TARGET) = (n_source)',
            '(HOBJECT n_source) <- S.ALLOCATIONS',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            'S.OBJECTS[n_source] = REALCLOSURE porigin pitem* pstaticcell*',
            '$call_current_valid(S)', '$closure_state_valid(S)', *GUARDS,
            'pcallcontext_bad = pcallcontext[.INSTANCE = eps]',
            'S_bad = S[.CURRENT = (pcallcontext_bad)]',
            '~$call_context_valid(S_bad, pcallcontext_bad, S_bad.CVS)',
            '~$call_descriptors_valid(S_bad)',
            '$heap_valid($heap_graph(S_bad))',
        ],
    },
    'closure-call-saved-instance': {
        'source': SOURCES['method-wrapper-instance-coexistence'],
        'stage': ('S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.CONTEXT = (pcallcontext_saved) '
                  '-- if pcallcontext_saved.TARGET = CLOSURE_CALL_TARGET n_source n_receiver'),
        'checks': [
            'pcallcontext.INSTANCE = eps',
            'pcallcontext_saved.INSTANCE = (n_source)',
            '$target_instance(pcallcontext_saved.TARGET) = (n_source)',
            'pcallcontext_saved.WRAPPER = (pnamedargs)',
            'pnamedargs = {SLOTS eps, NAMED eps}',
            '$call_current_valid(S)', '$call_saved_context_valid(S, pframe)',
            '$wrapper_context_valid(S, pcallcontext_saved)',
            '$closure_state_valid(S)', *GUARDS,
            'pframe_bad = pframe[.CONTEXT = (pcallcontext_saved[.INSTANCE = eps])]',
            'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
            '~$call_saved_context_valid(S_bad, pframe_bad)',
            '~$call_descriptors_valid(S_bad)',
            '$heap_valid($heap_graph(S_bad))',
        ],
    },
}

PUBLISHED_ABSTRACT_CALL_STAGE = ('S.TODO = (SCOPED_CLASS (NName (BYTES text_class) metadata_class) (NIdentifier (BYTES '
 'text_method) metadata_method) phpType7* z) :: ptask_tail* -- if $ptlc($base64(text_class)) = '
 '$ptascii("a") -- if $ptlc($base64(text_method)) = $ptascii("n") -- if S.ORIGIN = (porigin_site) '
 '-- if S.CURRENT = eps -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a) -- if '
 '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)')
# The final five clauses are helper-only flag probes, without reached-state claims.
PUBLISHED_ABSTRACT_CALL = ['$scoped_class_task(S, NName (BYTES text_class) metadata_class, NIdentifier (BYTES text_method) '
 'metadata_method, phpType7*, z)',
 '$call_task_valid(S, SCOPED_CLASS (NName (BYTES text_class) metadata_class) (NIdentifier (BYTES '
 'text_method) metadata_method) phpType7* z)',
 'pclassdesc_a.NAME = $ptascii("A") /\\ pclassdesc_a.KIND = "class" /\\ pclassdesc_a.ABSTRACT',
 '$scoped_source_name(S, NName (BYTES text_class) metadata_class) = (pclassdesc_a.NAME)',
 '$method_named(pclassdesc_a.METHODS, $ptascii("n")) = (pmethoddesc_n)',
 'pmethoddesc_n.OWNER = porigin_a /\\ pmethoddesc_n.ABSTRACT /\\ pmethoddesc_n.STATIC /\\ '
 'pmethoddesc_n.VISIBILITY = PROPERTY_PUBLIC',
 '$method_accessible(S, pmethoddesc_n, eps)',
 'phpType7* = (NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument) '
 ':: phpType7_tail*',
 'phpType7_tail* = eps',
 '$origin_node(S.SOURCES, porigin_site) = (NExprStaticCall (NName (BYTES text_class) '
 'metadata_class) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7*) '
 'metadata_call)',
 '$call_current_valid(S)',
 'PhpStep: S ~> S_rejected',
 'S_rejected.COMPLETION = THROWN "Error" $ptascii("Cannot call abstract method A::n()") z',
 'S_rejected.TODO = eps /\\ S_rejected.CURRENT = S.CURRENT',
 'S_rejected.OBJECTS = S.OBJECTS /\\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\\ S_rejected.EVENTS '
 '= S.EVENTS',
 '$class_constant_state_valid(S_rejected)',
 '$call_descriptors_valid(S_rejected)',
 '$declaration_history_valid(S_rejected)',
 '$heap_valid($heap_graph(S_rejected))',
 'S_denied = $scoped_select_found(S, NName (BYTES text_class) metadata_class, porigin_a, '
 'pmethoddesc_n[.VISIBILITY = PROPERTY_PROTECTED], KNOWN (PSTRING pclassdesc_a.NAME), '
 '$ptascii("n"), phpType7*, z)',
 'S_denied.COMPLETION = THROWN "Error" $ptascii("Call to protected method A::n() from global '
 'scope") z /\\ S_denied.TODO = eps',
 'S_nonstatic = $scoped_select_found(S, NName (BYTES text_class) metadata_class, porigin_a, '
 'pmethoddesc_n[.STATIC = false], KNOWN (PSTRING pclassdesc_a.NAME), $ptascii("n"), phpType7*, z)',
 'S_nonstatic.COMPLETION = THROWN "Error" $ptascii("Cannot call abstract method A::n()") z /\\ '
 'S_nonstatic.TODO = eps',
 '$scoped_select_found(S, NName (BYTES text_class) metadata_class, porigin_a, '
 'pmethoddesc_n[.ABSTRACT = false], KNOWN (PSTRING pclassdesc_a.NAME), $ptascii("n"), phpType7*, '
 'z) = $scoped_select_found_base(S, NName (BYTES text_class) metadata_class, porigin_a, '
 'pmethoddesc_n[.ABSTRACT = false], KNOWN (PSTRING pclassdesc_a.NAME), $ptascii("n"), phpType7*, '
 'z)']
CASES['published-abstract-static-call-before-arguments'] = {
    'source': SOURCES['published-abstract-static-call-before-arguments'],
    'stage': PUBLISHED_ABSTRACT_CALL_STAGE,
    'checks': PUBLISHED_ABSTRACT_CALL,
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE))
