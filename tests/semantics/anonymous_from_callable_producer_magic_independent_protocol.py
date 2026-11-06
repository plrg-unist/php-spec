#!/usr/bin/env python3
"""A normal factory selects a static USER target before real invocation arguments."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_from_callable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
QUERY = ('S.TODO = (API_CALLABLE_RESULT papiquery 1) :: ptask_query_tail* '
         '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
         '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN pvalue_returned -- if S.CURRENT = eps')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_magic) metadata_magic) :: expression_magic_tail*)) metadata_echo)) :: ptask_handler_tail* '
           '-- if $base64(text_magic) = $ptascii("MAGIC:") -- if S.CURRENT = (pcallcontext_handler) '
           '-- if pcallcontext_handler.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_handler n_arguments n_named pvalue_items*')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, QUERY)
for label, front in [('ready', READY), ('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$from222_' + label + '_')
PREFIX += r'''
dec $from222_outer_one(ptask) : pmagicmethodcall?
def $from222_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $from222_outer_one(ptask) = eps -- otherwise
dec $from222_outer(ptask*) : pmagicmethodcall?
def $from222_outer(eps) = eps
def $from222_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $from222_outer_one(ptask) = (pmagicmethodcall)
def $from222_outer(ptask :: ptask_tail*) = $from222_outer(ptask_tail*) -- if $from222_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', QUERY,
        '$from222_outer(ptask_query_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_factory = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])', 'pconfigcall.SITE = porigin_factory',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_factory (SEQUENCE phpType7_real*) metadata_outer',
        'expression_factory = NExprStaticCall phpType19_factory (NIdentifier (BYTES text_factory) metadata_method) (SEQUENCE ([(NArg ABSENT expression_literal (BOOLEAN false) (BOOLEAN false) metadata_arg)])) metadata_factory',
        '|phpType7_real*| = 2', '$ppscoped_named(phpType19_factory)',
        '$from_static_class(S,porigin_factory,phpType19_factory)',
        '$magic_method_from_callable_call(expression_outer)', '~$magic_method_firstclass_call(expression_outer)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_outer_init)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = ((z_factory,false))',
        '$call_argument_origin(S,(porigin_factory),0) = (porigin_literal)',
        '$magic_method_literal_value(S,porigin_literal,expression_literal) = (pvalue_literal)',
        'pvalue_literal = $string_literal_value(PSTRING ($ptascii("PeerProducerChild222::capture")))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_literal)]', 'papiquery.VALUE = pvalue_literal',
        '$api_query_valid(S,papiquery,1)', 'papiquery.CLASS.STRICT',
        'porigin_class = papiquery.CLASS.REQUESTED', 'papiquery.CLASS.CALLED = porigin_class',
        'papiquery.CLASS.RECEIVER = eps', 'papiquery.SCOPE = eps', 'papiquery.THIS = eps',
        '$magic_method_from_callable_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)',
        'pmethoddesc.FUNCTION = pfunction', 'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_class',
        '$api_method_result(S,papiquery,$ptascii("capture")) = HANDLERRESOLVED (API_METHOD_TARGET papiquery pfunction.ORIGIN ($ptascii("capture")) true)',
        '$factory182_output(S.EVENTS) = eps', 'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'pfrommethod.SITE = porigin_factory', 'pfrommethod.FACTORY = eps',
        'pfrommethod.FUNCTION = pfunction.ORIGIN', 'pfrommethod.CLASS = papiquery.CLASS',
        'pfrommethod.STATIC', '$from_receiver(pfrommethod) = eps',
        '$from_selected(S_wrapped,pfrommethod) = (pmethoddesc)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class', 'pclosurescope.RECEIVER = eps',
        'S_ready_found = $from222_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $from222_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        'S_producer_found = $from222_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)',
        'pcallcontext_producer.RECEIVER = eps', 'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_class)', '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_result_found = $from222_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_method_from_callable_producer(S_result,porigin_outer,expression_outer) = (pfunction)',
        'S_handler_found = $from222_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall', 'pvalue_items* = [PBOOL false,pvalue_string]', 'n_arguments = n_named',
        'S_handler.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT pvalue_string)]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)',
        'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        'S_after_found = $from222_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        'S_after.FRAMES = eps', '~((HARRAY n_arguments) <- S_after.ALLOCATIONS)',
        'S_done = $drive_steps(S_after,256)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '$magic_method_from_callable_producer(S_done,porigin_outer,expression_outer) = (pfunction)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
