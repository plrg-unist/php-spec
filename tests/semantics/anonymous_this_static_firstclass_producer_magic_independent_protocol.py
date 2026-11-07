#!/usr/bin/env python3
"""A static This callable owns its wrapper while the saved caller owns This."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_static_firstclass_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
CONVERT = ('S.TODO = (METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class_convert porigin_method) porigin_capture z_capture) :: ptask_convert_tail* '
           '-- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_outer_ready) z_outer) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = (pcallcontext_result)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, CONVERT)
for label, front in [('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisstatic230_' + label + '_')
PREFIX += r'''
dec $thisstatic230_outer_one(ptask) : pmagicmethodcall?
def $thisstatic230_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $thisstatic230_outer_one(ptask) = eps -- otherwise
dec $thisstatic230_outer(ptask*) : pmagicmethodcall?
def $thisstatic230_outer(eps) = eps
def $thisstatic230_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisstatic230_outer_one(ptask) = (pmagicmethodcall)
def $thisstatic230_outer(ptask :: ptask_tail*) = $thisstatic230_outer(ptask_tail*) -- if $thisstatic230_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CONVERT,
        '$thisstatic230_outer(ptask_convert_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_outer',
        'expression_capture = NExprMethodCall expression_this (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
        'expression_this = NExprVariable (BYTES text_this) metadata_this',
        '$direct_this(BYTES text_this)', '$base64(text_method) = $ptascii("capture")',
        '|phpType7_real*| = 2',
        '$magic_method_firstclass_site(S,porigin_outer,expression_outer)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_init_capture)',
        'pcallcontext_caller.RECEIVER = (n_this)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        '$object_class_origin(S,n_this) = (porigin_class)', 'porigin_class_convert = porigin_class',
        '$method_receiver_operand_valid(S,expression_this,KNOWN (POBJECT n_this))',
        '$magic_method_this_producer(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_source(S,pmagicmethodcall.CALLER,porigin_capture,$ptascii("capture"),phpType7_real*) = eps',
        'pfunction = pmethoddesc.FUNCTION', 'porigin_method = pfunction.ORIGIN', 'pmethoddesc.STATIC',
        'pmethoddesc.OWNER =/= porigin_class',
        '$call_task_valid(S,METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class porigin_method) porigin_capture z_capture)',
        '$method_capture_current(S,porigin_capture) = eps',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class porigin_method) = eps',
        '$target_receiver(S,STATIC_METHOD_TARGET porigin_class porigin_method) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_this) = 2',
        'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_class eps]',
        'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = eps', '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_this) = 2',
        'S_ready_found = $thisstatic230_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)',
        'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $thisstatic230_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'pcallcontext_ready = pcallcontext_caller',
        'porigin_outer_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '$target_receiver(S_ready,CLOSURE_TARGET n_wrapper) = eps',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        '$factory182_output(S_ready.EVENTS) = eps',
        'S_producer_found = $thisstatic230_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
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
        'S_result_found = $thisstatic230_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        'pcallcontext_result = pcallcontext_caller',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_this) = 1',
        'S_handler_found = $thisstatic230_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        '$magic_method_this_producer(S_handler,S_handler.CURRENT,porigin_outer,expression_outer) = eps',
        'S_after_found = $thisstatic230_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HOBJECT n_this) <- S_after.ALLOCATIONS)',
        '$magic_method_this_producer(S_after,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '$closure_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
