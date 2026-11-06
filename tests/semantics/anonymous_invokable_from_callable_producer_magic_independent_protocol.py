#!/usr/bin/env python3
"""A fresh callback owner transfers into a normal factory's receiver edge."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invokable_from_callable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
FACTORY = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_factory_tail* '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE '
           '-- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_this))] -- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, FACTORY)
for label, front in [('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$invfrom223_' + label + '_')
PREFIX += r'''
dec $invfrom223_outer_one(ptask) : pmagicmethodcall?
def $invfrom223_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $invfrom223_outer_one(ptask) = eps -- otherwise
dec $invfrom223_outer(ptask*) : pmagicmethodcall?
def $invfrom223_outer(eps) = eps
def $invfrom223_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $invfrom223_outer_one(ptask) = (pmagicmethodcall)
def $invfrom223_outer(ptask :: ptask_tail*) = $invfrom223_outer(ptask_tail*) -- if $invfrom223_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$invfrom223_outer(ptask_factory_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'pconfigcall.SITE = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_method_from_callable_parts(S,porigin_outer,expression_outer) = ((porigin_callback,expression_callback,phpType7_real*))',
        'porigin_callback = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 2,PCINDEX 0,PCFIELD 1])',
        '|phpType7_real*| = 2',
        '$magic_method_fresh_receiver(S,porigin_callback,expression_callback) = (porigin_class)',
        '$magic_method_constructor_producer(S,porigin_callback,expression_callback) = ((porigin_class,pmethoddesc_ctor))',
        '$object_class_origin(S,n_this) = (porigin_class)',
        '$object_invoke_method(S,n_this) = (pmethoddesc)', 'pfunction = pmethoddesc.FUNCTION',
        '$magic_method_from_callable_producer(S,porigin_outer,expression_outer) = (pfunction)',
        'pmethoddesc.OWNER =/= porigin_class', '$from_identity(S,POBJECT n_this) = eps',
        '$config_invoke_valid(S,pconfigcall)', '$heap_owners($heap_graph(S),HOBJECT n_this) = 1',
        '$factory182_output(S.EVENTS) = $ptascii("CTOR;")', 'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'pfrommethod.SITE = pconfigcall.SITE', 'pfrommethod.FACTORY = eps',
        'pfrommethod.INPUT = POBJECT n_this', 'pfrommethod.FUNCTION = pfunction.ORIGIN',
        'pfrommethod.INVOKE', '~pfrommethod.STATIC',
        'pfrommethod.CLASS.REQUESTED = porigin_class', 'pfrommethod.CLASS.CALLED = porigin_class',
        '$from_receiver(pfrommethod) = (n_this)', '$from_selected(S_wrapped,pfrommethod) = (pmethoddesc)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = (n_this)',
        'S_ready_found = $invfrom223_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $invfrom223_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_this) = 1',
        'S_producer_found = $invfrom223_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper', 'n_returned = n_this',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = (n_this)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_this) = 2',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_result_found = $invfrom223_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_this', 'pmagicmethodcall_result = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_this) = 1',
        'S_handler_found = $invfrom223_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,POBJECT n_this]', 'n_arguments = n_named',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_this))]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED (POBJECT n_this)',
        'S_after_found = $invfrom223_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 1',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_this) <- S_done.ALLOCATIONS)',
        '$magic_method_from_callable_producer(S_done,porigin_outer,expression_outer) = (pfunction)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
