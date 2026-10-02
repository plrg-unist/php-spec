#!/usr/bin/env python3
"""Source-derived public object invocation, capture and receiver ownership."""
from pathlib import Path
import json

import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/source_invoke_cases.json'
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())}
GUARDS = ['$call_descriptors_valid(S)', '$class_state_valid(S)',
          '$closure_state_valid(S)', '$heap_valid($heap_graph(S))']
LOOKUP = 'S.TODO = (CALL_DYNAMIC porigin_site z_init z_call) :: ptask_tail*'
FIRST = 'S.TODO = (FIRSTCLASS_CONVERT porigin_site z_init z_convert) :: ptask_tail*'
TARGET = 'METHOD_TARGET n_receiver porigin_method'
ARGS = f'CALL_ARGS ({TARGET}) phpType7* 0 eps (porigin_site) z'
SEND = f'CALL_SEND ({TARGET}) phpType7* 0 eps (porigin_site) z'
CONVERT = f'S.TODO = (METHOD_CONVERT ({TARGET}) porigin_site z) :: ptask_tail*'

CV_CHECKS = [
    'S.RESULT = VARIABLE $ptascii("o") z_operand',
    '$lookup(S.ENV, $ptascii("o")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
    '$dynamic_cv_name(S, porigin_site) = ($ptascii("o"))',
    '~$dynamic_this_site(S, porigin_site)',
    '$dynamic_operand_valid(S, porigin_site)', '$dynamic_result_valid(S)',
    '~$dynamic_operand_valid(S[.RESULT = KNOWN (POBJECT n_receiver)], porigin_site)',
    '~$dynamic_result_valid(S[.RESULT = KNOWN (POBJECT n_receiver)])',
    '~$dynamic_operand_valid(S[.RESULT = VARIABLE $ptascii("wrong") z_operand], porigin_site)',
    *GUARDS,
]
THIS_CHECKS = [
    '$dynamic_this_site(S, porigin_site)',
    'S.RESULT = KNOWN (POBJECT n_receiver)',
    '$this_receiver(S) = (n_receiver)',
    '$dynamic_operand_valid(S, porigin_site)', '$dynamic_result_valid(S)',
    '~$dynamic_operand_valid(S[.RESULT = VARIABLE $ptascii("this") 1], porigin_site)',
    'n_other = |S.OBJECTS|',
    'S_other = S[.OBJECTS = S.OBJECTS ++ [S.OBJECTS[n_receiver]]][.OBJECTPROPS = S.OBJECTPROPS ++ [{OBJECT n_other, SLOTS eps, MATERIALIZED false}]][.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_other]][.RESULT = KNOWN (POBJECT n_other)]',
    '$unpack_owned(S_other, S_other.RESULT)',
    '$heap_valid($heap_graph(S_other))',
    '~$dynamic_operand_valid(S_other, porigin_site)',
    '~$dynamic_result_valid(S_other)',
    *GUARDS,
]
CAPTURE_CHECKS = [
    '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
    'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
    'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
    '$method_capture_site(S, porigin_site, pmethoddesc)',
    '$call_task_valid(S, METHOD_CONVERT (' + TARGET + ') porigin_site z)',
    *GUARDS,
    'S_after = $drive_steps(S[.COMPLETION = NORMAL], 1)',
    'S_after.RESULT = KNOWN (POBJECT n_capture)',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_capture) = (pclosurescope)',
    'pclosurescope.LEXICAL = pmethoddesc.OWNER',
    'pclosurescope.CALLED = porigin_class',
    'pclosurescope.RECEIVER = (n_receiver)', 'pclosurescope.CREATION = eps',
    '$node_children(S_after, HOBJECT n_capture) = [HOBJECT n_receiver]',
    '$closure_scope_row_valid(S_after, pclosurescope)',
    '$call_descriptors_valid(S_after)', '$closure_state_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    '~$closure_scope_row_valid(S_after, pclosurescope[.RECEIVER = eps])',
    '~$closure_scope_row_valid(S_after, pclosurescope[.CREATION = ({FUNCTION porigin_method, CALLSITE porigin_site, RECEIVER true})])',
]

CASES = {
    'object-cv-before-resolution': {
        'source': SOURCES['public-basic'], 'stage': LOOKUP,
        'checks': [*CV_CHECKS, '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
                   '$typed_callable(S, POBJECT n_receiver) = (true)'],
    },
    'firstclass-cv-before-resolution': {
        'source': SOURCES['dual-role-firstclass-invoke'], 'stage': FIRST,
        'checks': [*CV_CHECKS, '$firstclass_evaluated(S, porigin_site)',
                   '$dynamic_fixed_name(S, porigin_site) = eps',
                   '$firstclass_task_valid(S, porigin_site, z_init, z_convert)'],
    },
    'firstclass-owned-new-callee': {
        'source': SOURCES['owned-new-object-firstclass'], 'stage': FIRST,
        'checks': [
            'S.RESULT = KNOWN (POBJECT n_receiver)',
            '$dynamic_cv_name(S, porigin_site) = eps',
            '~$dynamic_this_site(S, porigin_site)',
            '$unpack_owned(S, S.RESULT)', '$dynamic_operand_valid(S, porigin_site)',
            '$dynamic_result_valid(S)',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            '~$dynamic_operand_valid(S[.RESULT = VARIABLE $ptascii("wrong") 1], porigin_site)',
            *GUARDS,
        ],
    },
    'direct-this-before-object-lookup': {
        'source': SOURCES['direct-this-object-call'], 'stage': LOOKUP,
        'checks': THIS_CHECKS,
    },
    'rebound-this-before-firstclass-lookup': {
        'source': SOURCES['rebound-this-object-capture'], 'stage': FIRST,
        'checks': [
            *THIS_CHECKS,
            'S.CURRENT = (pcallcontext)', 'pcallcontext.INSTANCE = (n_producer)',
            'n_producer =/= n_receiver',
            '$unpack_owned(S, KNOWN (POBJECT n_producer))',
            '~$dynamic_operand_valid(S[.RESULT = KNOWN (POBJECT n_producer)], porigin_site)',
            '~$dynamic_result_valid(S[.RESULT = KNOWN (POBJECT n_producer)])',
        ],
    },
    'public-descriptor-and-selected-task': {
        'source': SOURCES['public-basic'], 'stage': f'S.TODO = ({ARGS}) :: ptask_tail*',
        'checks': [
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            'S.CLASSES = [pclassdesc]', 'pclassdesc.ORIGIN = porigin_class',
            'pclassdesc.METHODS = [pmethoddesc]',
            '$target_nodes(' + TARGET + ') = [HOBJECT n_receiver]',
            '$target_instance(' + TARGET + ') = eps',
            '$target_receiver(S, ' + TARGET + ') = (n_receiver)',
            '$call_task_valid(S, ' + ARGS + ')', *GUARDS,
            '$ppmethod_public_invoke(0, $ptascii("__INVOKE"))',
            '~$ppmethod_public_invoke(9, $ptascii("__invoke"))',
            '~$ppmethod_public_invoke(4, $ptascii("__invoke"))',
            '~$call_task_valid(S, CALL_ARGS (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 0 eps (porigin_site) z)',
            '~$call_selected_valid(S, ' + TARGET + ', (porigin_method))',
            '~$call_task_valid(S, CALL_ARGS (' + TARGET + ') phpType7* 0 eps (porigin_site) $(z + 100))',
            '$object_invoke_method(S[.CLASSNAMES = eps], n_receiver) = eps',
            '$object_invoke_method(S[.ALLOCATIONS = eps], n_receiver) = eps',
            '$object_invoke_method(S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.STATIC = true]]]]], n_receiver) = eps',
            '$object_invoke_method(S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.ABSTRACT = true]]]]], n_receiver) = eps',
            '$object_invoke_method(S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.VISIBILITY = PROPERTY_PRIVATE]]]]], n_receiver) = eps',
            '$typed_callable(S[.CLASSNAMES = eps], POBJECT n_receiver) = (false)',
        ],
    },
    'selected-receiver-survives-callee-replacement': {
        'source': SOURCES['callee-replaced-before-send'],
        'stage': f'S.TODO = ({SEND}) :: ptask_tail* -- if S.RESULT = KNOWN (PINT 3)',
        'checks': [
            'n_receiver = 0', '$lookup(S.ENV, $ptascii("o")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_replacement)',
            'n_replacement =/= n_receiver', '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '(HOBJECT n_replacement) <- S.ALLOCATIONS',
            '$task_nodes(' + SEND + ') = [HOBJECT n_receiver]',
            '$call_task_valid(S, ' + SEND + ')',
            '$call_selected_valid(S, ' + TARGET + ', (porigin_site))', *GUARDS,
            'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_replacement) <- S_done.ALLOCATIONS',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'inherited-owner-called-and-current-instance': {
        'source': SOURCES['inherited-owner-called-receiver'],
        'stage': f'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = {TARGET}',
        'checks': [
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            '$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("A")',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("B")',
            'pmethoddesc.OWNER =/= porigin_called',
            'pcallcontext.INSTANCE = eps', 'pcallcontext.RECEIVER = (n_receiver)',
            'pcallcontext.LEXICAL_CLASS = (pmethoddesc.OWNER)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            '$trace_context_class(S, pcallcontext) = ($ptascii("A"))',
            '$trace_context_type(S, pcallcontext) = ($ptascii("->"))',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_receiver]', *GUARDS,
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (n_receiver)])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.RECEIVER = eps])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_called)])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (pmethoddesc.OWNER)])])',
        ],
    },
    'inherited-capture-owner-scope': {
        'source': SOURCES['inherited-firstclass-clone-retirement'], 'stage': CONVERT,
        'checks': [
            *CAPTURE_CHECKS, 'pmethoddesc.OWNER =/= porigin_class',
            '$method_capture_current(S, porigin_site) = eps',
            'S_after.OBJECTS[n_capture] = METHODCLOSURE porigin_method porigin_site porigin_class eps',
            '$method_capture_in_scope(S_after, pmethoddesc, porigin_site, porigin_class, pclosurescope[.LEXICAL = porigin_class], eps, eps)',
            '~$closure_scope_row_valid(S_after, pclosurescope[.LEXICAL = porigin_class])',
            '~$closure_scope_row_valid(S_after, pclosurescope[.CALLED = pmethoddesc.OWNER])',
        ],
    },
    'object-capture-retains-callee-without-issuer-root': {
        'source': SOURCES['rebound-producer-object-capture'], 'stage': CONVERT,
        'checks': [
            'S.CURRENT = (pcallcontext)', 'pcallcontext.RECEIVER = (n_issuer)',
            'n_issuer =/= n_receiver', 'pcallcontext.INSTANCE = (n_producer)',
            '$method_capture_current(S, porigin_site) = (pmethodcapture)',
            'pmethodcapture.FUNCTION = pcallcontext.FUNCTION',
            'pmethodcapture.CALLSITE = pcallcontext.CALLSITE',
            *CAPTURE_CHECKS,
            'pmethodcapture.LEXICAL_CLASS =/= (porigin_class)',
            'S_after.OBJECTS[n_capture] = METHODCLOSURE porigin_method porigin_site porigin_class (pmethodcapture)',
            '$method_capture_certificate_valid(S, porigin_site, (pmethodcapture))',
            '~$method_capture_certificate_valid(S, porigin_site, (pmethodcapture[.FUNCTION = porigin_method]))',
            '~$method_capture_certificate_valid(S, porigin_site, (pmethodcapture[.CALLSITE = (porigin_site)]))',
            'S_done = $drive(S_after[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            '~((HOBJECT n_issuer) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_producer) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_receiver) <- S_done.ALLOCATIONS',
            '$node_children(S_done, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$closure_scope_row_valid(S_done, pclosurescope)',
            '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'bound-this-source-capture-producer': {
        'source': SOURCES['rebound-this-object-capture'], 'stage': CONVERT,
        'checks': [
            'S.CURRENT = (pcallcontext)', 'pcallcontext.RECEIVER = (n_receiver)',
            '$method_capture_current(S, porigin_site) = (pmethodcapture)',
            '$method_capture_producer_this_valid(S, porigin_site, pmethodcapture)',
            '$method_capture_certificate_valid(S, porigin_site, (pmethodcapture))',
            *CAPTURE_CHECKS,
            '$origin_node(S.SOURCES, porigin_site) = (NExprFuncCall expression_this phpType6 metadata)',
            '$method_capture_this(expression_this)',
            'S_after.OBJECTS[n_capture] = METHODCLOSURE porigin_method porigin_site porigin_class (pmethodcapture)',
        ],
    },
    'cloned-capture-and-last-receiver-retirement': {
        'source': SOURCES['firstclass-clone-typed-reference-retirement'],
        'stage': ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_capture) phpType7* 0 eps (porigin_call) z) :: ptask_tail* '
                  '-- if S.OBJECTS[n_capture] = METHODCLOSURE porigin_method porigin_site porigin_class pmethodcapture?'),
        'checks': [
            '$closure_scope_at(S.CLOSURESCOPES, n_capture) = (pclosurescope)',
            'pclosurescope.RECEIVER = (n_receiver)', 'pclosurescope.CREATION = eps',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$lookup(S.ENV, $ptascii("o")) = (n_o)', 'S.STORE[n_o] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("f")) = (n_f)', 'S.STORE[n_f] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("r")) = (n_ref)', 'S.STORE[n_ref] = DEFINED (PINT 1)',
            '$propref_at(S.PROPREFS, n_ref) = (ppropref)',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS', *GUARDS,
            'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '$propref_at(S_done.PROPREFS, n_ref) = eps',
            'S_done.STORE[n_ref] = DEFINED (PSTRING $ptascii("s"))',
            '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'saved-firstclass-during-producing-call': {
        # This extra finite source has no author native32 agreement claim.
        'source': ('<?php\nclass A{public function __invoke(){echo "I";}}\n'
                   '$o=new A;function maker(){global $o;return $o;}\n'
                   '$f=maker()(...);$o=null;$f();\n'),
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("maker") '
                  '-- if S.RESULT = VARIABLE $ptascii("o") z_operand '
                  '-- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = (ORIGIN_RETURN porigin_saved?) :: '
                  '(FIRSTCLASS_CONVERT porigin_site z_init z_convert) :: ptask_tail*'),
        'checks': [
            '$dynamic_result_valid(S)',
            'S_saved = S[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO]',
            '$call_tasks_valid(S_saved, pframe.TODO)',
            '$dynamic_cv_name(S, porigin_site) = eps',
            '~$unpack_owned(S, S.RESULT)',
            '~$dynamic_result_valid(S_saved)', *GUARDS,
            'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            '$lookup(S_done.ENV, $ptascii("o")) = (n_o)', 'S_done.STORE[n_o] = DEFINED PNULL',
            '$lookup(S_done.ENV, $ptascii("f")) = (n_f)',
            'S_done.STORE[n_f] = DEFINED (POBJECT n_capture)',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_capture) = (pclosurescope)',
            'pclosurescope.RECEIVER = (n_receiver)',
            '(HOBJECT n_receiver) <- S_done.ALLOCATIONS',
            '$closure_scope_row_valid(S_done, pclosurescope)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'fixed-firstclass-source-rejects-object-conversion': {
        # Extra finite source only; no author native32 agreement is claimed.
        'source': '<?php class A{public function __invoke(){}}function normal(){}$o=new A;normal();$f=normal(...);$f();',
        'stage': FIRST,
        'checks': [
            '$lookup(S.ENV, $ptascii("o")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
            '~$firstclass_evaluated(S, porigin_site)',
            '$dynamic_fixed_name(S, porigin_site) = ($ptascii("normal"))',
            '$firstclass_task_valid(S, porigin_site, z_init, z_convert)',
            '~$method_capture_site(S, porigin_site, pmethoddesc)',
            '~$call_selected_valid(S, ' + TARGET + ', (porigin_site))',
            '~$call_task_valid(S, METHOD_CONVERT (' + TARGET + ') porigin_site z_convert)',
            '~$method_capture_in_scope(S, pmethoddesc, porigin_site, porigin_class, {OBJECT n_receiver, LEXICAL pmethoddesc.OWNER, CALLED porigin_class, RECEIVER (n_receiver), CREATION eps}, eps, eps)',
            *GUARDS,
        ],
    },
    'ordinary-named-source-rejects-object-selection': {
        'source': '<?php class A{public function __invoke(){}}function normal(){}$o=new A;normal();$f=normal(...);$f();',
        'stage': 'S.TODO = (CALL_ARGS porigin_function phpType7* 0 eps (porigin_site) z) :: ptask_tail*',
        'checks': [
            '$lookup(S.ENV, $ptascii("o")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_receiver)',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
            '$call_selected_valid(S, porigin_function, (porigin_site))',
            '$call_task_valid(S, CALL_ARGS porigin_function phpType7* 0 eps (porigin_site) z)',
            '~$call_selected_valid(S, ' + TARGET + ', (porigin_site))',
            '~$call_task_valid(S, CALL_ARGS (' + TARGET + ') phpType7* 0 eps (porigin_site) z)',
            '~$method_capture_site(S, porigin_site, pmethoddesc)',
            *GUARDS,
        ],
    },
}

for name, source_id, stage, root_check in [
    ('normal-call-reference-retirement', 'selected-receiver-typed-reference-lifetime',
     f'S.TODO = ({SEND}) :: ptask_tail* -- if S.RESULT = KNOWN (PINT 0)',
     'HOBJECT n_receiver <- $tasks_nodes(S.TODO)'),
    ('argument-throw-reference-retirement', 'selected-receiver-argument-throw-lifetime',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("arg") -- if S.EVENTS = [OUTPUT ([69])]',
     'HOBJECT n_receiver <- $frames_roots(S.FRAMES)'),
    ('body-throw-reference-retirement', 'selected-receiver-body-throw-lifetime',
     f'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = {TARGET} -- if S.EVENTS = [OUTPUT ([69]), OUTPUT ([73])]',
     'HOBJECT n_receiver <- $call_context_roots(S.CURRENT)'),
]:
    CASES[name] = {
        'source': SOURCES[source_id], 'stage': stage,
        'checks': [
            'n_receiver = 0', '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS', root_check, *GUARDS,
            'S_done = $drive(S[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL',
            '$lookup(S_done.ENV, $ptascii("o")) = (n_o)', 'S_done.STORE[n_o] = DEFINED PNULL',
            '$lookup(S_done.ENV, $ptascii("r")) = (n_ref)',
            'S_done.STORE[n_ref] = DEFINED (PSTRING $ptascii("s"))',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$propref_at(S_done.PROPREFS, n_ref) = eps',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    }


def run(cases=None):
    protocol.run(CASES if cases is None else cases,
                 extra_inputs=(Path(__file__), CATALOGUE))


if __name__ == '__main__':
    run()
