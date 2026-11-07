#!/usr/bin/env python3
"""A fresh static selector retires before real callable arguments are captured."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_fresh_static_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
PREP = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_capture* false b_base z_capture) :: ptask_prep_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if S.CURRENT = eps '
        '-- if $method_capture(S,b_base,z_capture) = (S_capture,KNOWN (POBJECT n_selector))')
CONVERT = ('S.TODO = (METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class_convert porigin_method_convert) porigin_capture z_convert) :: ptask_convert_tail* '
           '-- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_outer_ready) z_outer) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_magic) metadata_magic])) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC;") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, PREP)
for label, front in [('convert', CONVERT), ('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$freshstatic231_' + label + '_')
PREFIX += r'''
dec $freshstatic231_outer_one(ptask) : pmagicmethodcall?
def $freshstatic231_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $freshstatic231_outer_one(ptask) = eps -- otherwise
dec $freshstatic231_outer(ptask*) : pmagicmethodcall?
def $freshstatic231_outer(eps) = eps
def $freshstatic231_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $freshstatic231_outer_one(ptask) = (pmagicmethodcall)
def $freshstatic231_outer(ptask :: ptask_tail*) = $freshstatic231_outer(ptask_tail*) -- if $freshstatic231_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PREP,
        '$freshstatic231_outer(ptask_prep_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])', 'S.ORIGIN = (porigin_capture)',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_outer',
        'expression_capture = NExprMethodCall expression_receiver (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_capture*) metadata_capture',
        'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]', '|phpType7_real*| = 2',
        '$magic_method_firstclass_site(S,porigin_outer,expression_outer)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_init_capture)',
        '$magic_method_fresh_receiver(S,PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 0]),expression_receiver) = (porigin_class)',
        '$magic_method_firstclass_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$class_method_origin(S.CLASSES,pfunction.ORIGIN) = (pmethoddesc)', 'pmethoddesc.STATIC',
        'pmethoddesc.OWNER =/= porigin_class', '~$magic_method_plain_instance_source(S,pmethoddesc,phpType7_real*)',
        'S.OBJECTS[n_selector] = INSTANCE porigin_class', '(HOBJECT n_selector) <- S.ALLOCATIONS',
        '$factory182_output(S.EVENTS) = $ptascii("CTOR;")',
        '$lookup($global_table_view(S).ENV,$ptascii("late")) = (n_late_cell)',
        'S.STORE[n_late_cell] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD")))',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_convert_found = $freshstatic231_convert_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_convert_found.COMPLETION = BUDGET',
        'S_direct = $freshstatic231_convert_seek(S,2048)', 'S_direct = S_convert_found',
        'S_convert = S_convert_found[.COMPLETION = NORMAL]', CONVERT.replace('S.', 'S_convert.'),
        'porigin_class_convert = porigin_class', 'porigin_method_convert = pfunction.ORIGIN',
        '~((HOBJECT n_selector) <- S_convert.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_convert),HOBJECT n_selector) = 0',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_receiver(S_convert,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$call_task_valid(S_convert,METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) porigin_capture z_convert)',
        '$factory182_output(S_convert.EVENTS) = $ptascii("CTOR;SELECTOR-END;")',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("REQUEST-SELECTED"))',
        'S_convert.STORE[n_late_cell] = DEFINED pvalue_string',
        '$magic_method_firstclass_producer(S_convert,porigin_outer,expression_outer) = (pfunction)',
        'n_wrapper = |S_convert.OBJECTS|',
        'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS = S_convert.OBJECTS ++ [METHODCLOSURE pfunction.ORIGIN porigin_capture porigin_class eps]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = eps', '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        'S_ready_found = $freshstatic231_ready_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_ready_found.COMPLETION = BUDGET',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_outer_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 0',
        '$factory182_output(S_ready.EVENTS) = $ptascii("CTOR;SELECTOR-END;")',
        'S_producer_found = $freshstatic231_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string', 'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_selector) = 0',
        'S_result_found = $freshstatic231_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_method_firstclass_producer(S_result,porigin_outer,expression_outer) = (pfunction)',
        'S_handler_found = $freshstatic231_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        'S_after_found = $freshstatic231_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
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
