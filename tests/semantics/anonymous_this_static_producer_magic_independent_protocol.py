#!/usr/bin/env python3
"""A direct static This target borrows selection while the saved caller owns This."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_static_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READY = ('S.TODO = (CALL_ARGS (STATIC_METHOD_TARGET porigin_class_ready porigin_function_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_caller)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = STATIC_METHOD_TARGET porigin_class_producer porigin_function_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = (pcallcontext_caller)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READY)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisstatic229_' + label + '_')
PREFIX += r'''
dec $thisstatic229_outer_one(ptask) : pmagicmethodcall?
def $thisstatic229_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $thisstatic229_outer_one(ptask) = eps -- otherwise
dec $thisstatic229_outer(ptask*) : pmagicmethodcall?
def $thisstatic229_outer(eps) = eps
def $thisstatic229_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisstatic229_outer_one(ptask) = (pmagicmethodcall)
def $thisstatic229_outer(ptask :: ptask_tail*) = $thisstatic229_outer(ptask_tail*) -- if $thisstatic229_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READY,
        '$thisstatic229_outer(ptask_ready_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_ready)',
        '$origin_node(S.SOURCES,porigin_ready) = (expression_producer)',
        'expression_producer = NExprMethodCall expression_this (NIdentifier (BYTES text_name) metadata_name) (SEQUENCE phpType7_real*) metadata',
        'expression_this = NExprVariable (BYTES text_this) metadata_this',
        '$direct_this(BYTES text_this)', '$base64(text_name) = $ptascii("capture")',
        'phpType7_ready* = phpType7_real*', '|phpType7_real*| = 2',
        'pcallcontext_caller.RECEIVER = (n_this)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        '$object_class_origin(S,n_this) = (porigin_class)', 'porigin_class_ready = porigin_class',
        '$method_receiver_operand_valid(S,expression_this,KNOWN (POBJECT n_this))',
        '$magic_method_this_producer(S,pmagicmethodcall.CALLER,porigin_ready,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_source(S,pmagicmethodcall.CALLER,porigin_ready,$ptascii("capture"),phpType7_real*) = eps',
        'pfunction = pmethoddesc.FUNCTION', 'porigin_function_ready = pfunction.ORIGIN', 'pmethoddesc.STATIC',
        'pmethoddesc.OWNER =/= porigin_class',
        '$method_call_selected(S,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN,(porigin_ready))',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_receiver(S,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_instance(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_this]',
        '$heap_owners($heap_graph(S),HOBJECT n_this) = 2',
        '$factory182_output(S.EVENTS) = eps',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_producer_found = $thisstatic229_producer_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_producer_found.COMPLETION = BUDGET',
        'S_direct = $thisstatic229_producer_seek(S,2048)', 'S_direct = S_producer_found',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'porigin_class_producer = porigin_class', 'porigin_function_producer = pfunction.ORIGIN',
        'pcallcontext_producer.INSTANCE = eps', 'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = eps',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_this) = 1',
        '$heap_count(HOBJECT n_this,$frames_roots(S_producer.FRAMES)) = 1',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("runner")) = (n_runner_cell)',
        'S_producer.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_result_found = $thisstatic229_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        '$heap_owners($heap_graph(S_result),HOBJECT n_this) = 1',
        'S_handler_found = $thisstatic229_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        '$magic_method_this_producer(S_handler,S_handler.CURRENT,porigin_ready,expression_producer) = eps',
        'S_after_found = $thisstatic229_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HOBJECT n_this) <- S_after.ALLOCATIONS)',
        '$magic_method_this_producer(S_after,pmagicmethodcall.CALLER,porigin_ready,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
