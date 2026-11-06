#!/usr/bin/env python3
"""Fresh invokable conversion binds the real receiver before IIFE arguments."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invokable_firstclass_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
CAPTURE = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init_capture z_capture) :: ptask_capture_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_this) -- if S.CURRENT = eps')
CONVERT = ('S.TODO = (METHOD_CONVERT (METHOD_TARGET n_this_convert porigin_method_convert) porigin_convert z_convert) :: ptask_convert_tail* '
           '-- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_send 0 eps) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_sent) -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, CAPTURE)
for label, front in [('ready', READY), ('producer', PRODUCER), ('send', SEND), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$invokefcc219_' + label + '_')
PREFIX += r'''
dec $invokefcc219_outer_one(ptask) : pmagicmethodcall?
def $invokefcc219_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $invokefcc219_outer_one(ptask) = eps -- otherwise
dec $invokefcc219_outer(ptask*) : pmagicmethodcall?
def $invokefcc219_outer(eps) = eps
def $invokefcc219_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $invokefcc219_outer_one(ptask) = (pmagicmethodcall)
def $invokefcc219_outer(ptask :: ptask_tail*) = $invokefcc219_outer(ptask_tail*) -- if $invokefcc219_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CAPTURE,
        '$invokefcc219_outer(ptask_capture_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = eps', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        'porigin_new = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_outer',
        'expression_capture = NExprFuncCall expression_new (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
        '|phpType7_real*| = 2', '$magic_method_firstclass_site(S,porigin_outer,expression_outer)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_init_capture)',
        '$magic_method_constructor_producer(S,porigin_new,expression_new) = ((porigin_called,pmethoddesc_constructor))',
        '$class_named(S.CLASSNAMES,$ptascii("peerproducerchild219")) = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("peerproducerbase219")) = (porigin_declaring)',
        'S.OBJECTS[n_this] = INSTANCE porigin_called',
        '$magic_method_firstclass_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$object_invoke_method(S,n_this) = (pmethoddesc)',
        'pmethoddesc.FUNCTION = pfunction', 'pmethoddesc.OWNER = porigin_declaring',
        'porigin_method = pfunction.ORIGIN',
        '$factory182_output(S.EVENTS) = $ptascii("CTOR;")',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_convert = S_one[.COMPLETION = NORMAL]', CONVERT.replace('S.', 'S_convert.'),
        'n_this_convert = n_this', 'porigin_method_convert = porigin_method', 'porigin_convert = porigin_capture',
        '$call_selected_valid(S_convert,METHOD_TARGET n_this porigin_method,(porigin_capture))',
        '$method_capture_current(S_convert,porigin_capture) = eps',
        'n_wrapper = |S_convert.OBJECTS|',
        'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_convert.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_called eps]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_declaring', 'pclosurescope.CALLED = porigin_called',
        'pclosurescope.RECEIVER = (n_this)', '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
        'S_ready_found = $invokefcc219_ready_seek(S_wrapped[.COMPLETION = NORMAL],128)',
        'S_ready_found.COMPLETION = BUDGET', 'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_outer',
        'S_producer_found = $invokefcc219_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_this', 'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = (n_this)',
        'pcallcontext_producer.LEXICAL_CLASS = (porigin_declaring)', 'pcallcontext_producer.CALLED_CLASS = (porigin_called)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;SHIFT;INVOKE:PeerProducerBase219:PeerProducerChild219;")',
        'S_send_found = $invokefcc219_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'n_sent = n_this', 'pmagicmethodcall_send = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 1',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this),KNOWN (PBOOL false)],eps) = ([POBJECT n_this,PBOOL false])',
        'S_handler_found = $invokefcc219_handler_seek(S_send,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [POBJECT n_this,PBOOL false]', 'n_arguments = n_named',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED (POBJECT n_this)',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (POBJECT n_this)),ENTRY (KSTRING $ptascii("later")) (DIRECT (PBOOL false))]',
        'S_after_found = $invokefcc219_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        'S_after.STORE[n_kept_cell] = DEFINED (POBJECT n_this)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 1',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_this) <- S_done.ALLOCATIONS)', '~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS)',
        '$magic_method_firstclass_producer(S_done,porigin_outer,expression_outer) = (pfunction)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
