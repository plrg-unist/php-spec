#!/usr/bin/env python3
"""A fresh selector retires before a static wrapper evaluates its real arguments."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_fresh_static_array_from_callable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
FACTORY = ('S.TODO = (API_CALLABLE_RESULT papiquery 0) :: ptask_factory_tail* '
           '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
PREFIX = names.PREFIX.replace(names.FRONT, FACTORY)
for label, front in [('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$freshstaticarray227_' + label + '_')
PREFIX += r'''
dec $freshstaticarray227_outer_one(ptask) : pmagicmethodcall?
def $freshstaticarray227_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $freshstaticarray227_outer_one(ptask) = eps -- otherwise
dec $freshstaticarray227_outer(ptask*) : pmagicmethodcall?
def $freshstaticarray227_outer(eps) = eps
def $freshstaticarray227_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $freshstaticarray227_outer_one(ptask) = (pmagicmethodcall)
def $freshstaticarray227_outer(ptask :: ptask_tail*) = $freshstaticarray227_outer(ptask_tail*) -- if $freshstaticarray227_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$freshstaticarray227_outer(ptask_factory_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'pconfigcall.SITE = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_method_from_callable_parts(S,porigin_outer,expression_outer) = ((porigin_callback,expression_callback,phpType7_real*))',
        'porigin_callback = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 2,PCINDEX 0,PCFIELD 1])',
        '|phpType7_real*| = 2',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_receiver (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (porigin_receiver)',
        '$magic_method_fresh_receiver(S,porigin_receiver,expression_receiver) = (porigin_class)',
        '$magic_method_constructor_producer(S,porigin_receiver,expression_receiver) = ((porigin_class,pmethoddesc_ctor))',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 1,PCFIELD 1]) = (porigin_method)',
        '$magic_method_literal_value(S,porigin_method,expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]', 'papiquery.VALUE = PARRAY n_callback',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$object_class_origin(S,n_selector) = (porigin_class)',
        'papiquery.INPUT = POBJECT n_selector', 'papiquery.CLASS.REQUESTED = porigin_class',
        'papiquery.CLASS.CALLED = porigin_class', '~papiquery.CLASS.STRICT',
        'papiquery.CLASS.RECEIVER = (n_selector)', 'papiquery.SCOPE = eps', 'papiquery.THIS = eps',
        '$api_query_valid(S,papiquery,0)',
        '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_class',
        '$magic_method_from_callable_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$api_method_result(S,papiquery,$ptascii("capture")) = HANDLERRESOLVED (API_METHOD_TARGET papiquery pfunction.ORIGIN ($ptascii("capture")) true)',
        '$heap_owners($heap_graph(S),HARRAY n_callback) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_selector) = 1',
        '$node_children(S,HARRAY n_callback) = [HOBJECT n_selector]', '$factory182_output(S.EVENTS) = $ptascii("CTOR;")',
        'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'pfrommethod.SITE = pconfigcall.SITE', 'pfrommethod.FACTORY = eps',
        'pfrommethod.INPUT = POBJECT n_selector', 'pfrommethod.FUNCTION = pfunction.ORIGIN',
        '~pfrommethod.INVOKE', 'pfrommethod.ARRAY', 'pfrommethod.STATIC',
        'pfrommethod.CLASS = papiquery.CLASS', '$from_receiver(pfrommethod) = eps',
        '$from_selected(S_wrapped,pfrommethod) = (pmethoddesc)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = eps',
        'S_ready_found = $freshstaticarray227_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $freshstaticarray227_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '~((HOBJECT n_selector) <- S_ready.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 0',
        '$object_class_origin(S_ready,n_selector) = (porigin_class)',
        '$from_selected(S_ready,pfrommethod) = (pmethoddesc)', '$from_valid(S_ready,pfrommethod)',
        '$factory182_output(S_ready.EVENTS) = $ptascii("CTOR;SELECTOR-END;")',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        'S_producer_found = $freshstaticarray227_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)',
        'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_result_found = $freshstaticarray227_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_method_from_callable_producer(S_result,porigin_outer,expression_outer) = (pfunction)',
        'S_handler_found = $freshstaticarray227_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]', 'n_arguments = n_named',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        'S_done = $drive_steps(S_handler,512)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_selector) <- S_done.ALLOCATIONS)',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '$magic_method_from_callable_producer(S_done,porigin_outer,expression_outer) = (pfunction)',
        '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
