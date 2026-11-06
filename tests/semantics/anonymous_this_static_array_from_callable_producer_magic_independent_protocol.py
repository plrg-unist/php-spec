#!/usr/bin/env python3
"""A receiver-free static wrapper preserves immutable caller This selection."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_static_array_from_callable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
FACTORY = ('S.TODO = (API_CALLABLE_RESULT papiquery 0) :: ptask_factory_tail* '
           '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_caller)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = (pcallcontext_caller)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, FACTORY)
for label, front in [('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisstaticarray228_' + label + '_')
PREFIX += r'''
dec $thisstaticarray228_outer_one(ptask) : pmagicmethodcall?
def $thisstaticarray228_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $thisstaticarray228_outer_one(ptask) = eps -- otherwise
dec $thisstaticarray228_outer(ptask*) : pmagicmethodcall?
def $thisstaticarray228_outer(eps) = eps
def $thisstaticarray228_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisstaticarray228_outer_one(ptask) = (pmagicmethodcall)
def $thisstaticarray228_outer(ptask :: ptask_tail*) = $thisstaticarray228_outer(ptask_tail*) -- if $thisstaticarray228_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$thisstaticarray228_outer(ptask_factory_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pcallcontext_caller.INSTANCE = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'pconfigcall.SITE = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_method_from_callable_parts(S,porigin_outer,expression_outer) = ((porigin_callback,expression_callback,phpType7_real*))',
        'porigin_callback = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 2,PCINDEX 0,PCFIELD 1])',
        '|phpType7_real*| = 2',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_receiver (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (porigin_receiver)',
        'expression_receiver = NExprVariable (BYTES text_this) metadata_this', '$direct_this(BYTES text_this)',
        'porigin_receiver = PORIGIN n_unit pcpath_receiver',
        '$source_emission_this_fetch(S,n_unit,pcpath_receiver,expression_receiver)',
        '$compiled_read(S,porigin_callback) = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]', 'papiquery.VALUE = PARRAY n_callback',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_this)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        'papiquery.INPUT = POBJECT n_this', '$object_class_origin(S,n_this) = (porigin_class)',
        'papiquery.CLASS.REQUESTED = porigin_class', 'papiquery.CLASS.CALLED = porigin_class',
        '~papiquery.CLASS.STRICT', 'papiquery.CLASS.RECEIVER = (n_this)', 'papiquery.SCOPE = pcallcontext_caller.LEXICAL_CLASS',
        'pcallcontext_caller.RECEIVER = (n_this)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_this]',
        '$api_query_valid(S,papiquery,0)',
        '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        '$magic_method_this_array_from_callable_producer(S,(pcallcontext_caller),porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        'pmethoddesc.OWNER =/= porigin_class', 'pmethoddesc.STATIC',
        '$magic_method_this_source(S,(pcallcontext_caller),pconfigcall.SITE,$ptascii("capture"),phpType7_real*) = eps',
        '$api_method_result(S,papiquery,$ptascii("capture")) = HANDLERRESOLVED (API_METHOD_TARGET papiquery pfunction.ORIGIN ($ptascii("capture")) false)',
        '$heap_owners($heap_graph(S),HARRAY n_callback) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_this) = 3',
        'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'pfrommethod.INPUT = POBJECT n_this', 'pfrommethod.FUNCTION = pfunction.ORIGIN',
        '~pfrommethod.INVOKE', 'pfrommethod.ARRAY', 'pfrommethod.STATIC',
        'pfrommethod.CLASS = papiquery.CLASS',
        '$from_receiver(pfrommethod) = eps', '$from_selected(S_wrapped,pfrommethod) = (pmethoddesc)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = eps',
        'S_ready_found = $thisstaticarray228_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $thisstaticarray228_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_this) = 2',
        'S_producer_found = $thisstaticarray228_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = eps',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_this) = 1',
        '$heap_count(HOBJECT n_this,$frames_roots(S_producer.FRAMES)) = 1',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner_cell)',
        'S_producer.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_result_found = $thisstaticarray228_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_this) = 1',
        'S_handler_found = $thisstaticarray228_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        '$magic_method_this_array_from_callable_producer(S_handler,S_handler.CURRENT,porigin_outer,expression_outer) = eps',
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        'S_after_found = $thisstaticarray228_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps',
        '~((HOBJECT n_this) <- S_after.ALLOCATIONS)',
        '$from_selected(S_after,pfrommethod) = (pmethoddesc)', '$from_valid(S_after,pfrommethod)',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_this) <- S_done.ALLOCATIONS)',
        '$magic_method_this_array_from_callable_producer(S_done,(pcallcontext_caller),porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
