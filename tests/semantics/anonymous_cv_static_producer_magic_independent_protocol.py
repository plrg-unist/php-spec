#!/usr/bin/env python3
"""An actual plain-CV read stamps a static target before the CV can retire."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_static_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_capture* false b_base z_capture) :: ptask_read_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if $ppfirstclass(phpType7_capture*) '
        '-- if S.RESULT = VARIABLE ($ptascii("producer")) z_cv -- if S.CURRENT = eps')
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
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('handler', HANDLER), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvstatic232_' + label + '_')
PREFIX += r'''
dec $cvstatic232_outer_one(ptask) : pmagicmethodcall?
def $cvstatic232_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cvstatic232_outer_one(ptask) = eps -- otherwise
dec $cvstatic232_outer(ptask*) : pmagicmethodcall?
def $cvstatic232_outer(eps) = eps
def $cvstatic232_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvstatic232_outer_one(ptask) = (pmagicmethodcall)
def $cvstatic232_outer(ptask :: ptask_tail*) = $cvstatic232_outer(ptask_tail*) -- if $cvstatic232_outer_one(ptask) = eps
dec $cvstatic232_bad_one(ptask) : ptask
def $cvstatic232_bad_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 eps
def $cvstatic232_bad_one(ptask) = ptask -- otherwise
dec $cvstatic232_bad(ptask*) : ptask*
def $cvstatic232_bad(eps) = eps
def $cvstatic232_bad(ptask :: ptask_tail*) = $cvstatic232_bad_one(ptask) :: $cvstatic232_bad(ptask_tail*)
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        'S_read.ORIGIN = (porigin_capture)', '$cvstatic232_outer(S_read.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall.SITE),1) = (porigin_outer)',
        '$origin_child((porigin_outer),[PCFIELD 0]) = (porigin_capture)',
        '$origin_node(S_read.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_invoke',
        'expression_capture = NExprMethodCall expression_cv (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_capture*) metadata_capture',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv',
        'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]', '|phpType7_real*| = 2',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)', 'z_capture = $runtime_line(S_read,eps,expression_capture)',
        'porigin_outer = PORIGIN n_unit pcpath_outer', '$code_at(S_read.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_init_capture)',
        '$magic_producer_cv_parts(S_read,porigin_outer,expression_outer) = ((porigin_capture,VARIABLE ($ptascii("producer")) z_cv,$ptascii("capture"),phpType7_capture*,phpType7_real*))',
        '$magic_producer_argument_site(S_read,porigin_capture) = (porigin_outer)',
        '$lookup(S_read.ENV,$ptascii("producer")) = (n_producer_cell)',
        '~(n_producer_cell <- S_read.REFCELLS)',
        'S_read.STORE[n_producer_cell] = DEFINED (POBJECT n_selector)',
        '$magic_producer_cell(S_read,$ptascii("producer")) = (n_selector)',
        '$object_class_origin(S_read,n_selector) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_outer,porigin_class) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_class',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("capture"),phpType7_capture*,z_capture)',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;FIRST;")',
        'S_bad = S_read[.TODO = $cvstatic232_bad(S_read.TODO)]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_outer)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_outer) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$ptascii("capture"),phpType7_capture*,z_capture)',
        'S_bad_selected = $method_selected_metadata(S_bad,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN,(porigin_capture))',
        'S_bad_selected.COMPLETION = UNSUPPORTED "magic method producer selection fact"',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT (STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) (METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) porigin_capture z_capture)) :: ptask_selected_tail*',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        '$cvstatic232_outer(ptask_selected_tail*) = (pmagicmethodcall_selected)',
        'pmagicproducerfact_selected = {SITE porigin_outer,CLASS porigin_class,METHOD pfunction.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_selected]]',
        '$magic_producer_fact_at(pmagicmethodcall_selected.PRODUCERS,porigin_capture) = eps',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_selector) = 1',
        'S_convert = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_convert.COMPLETION = BUDGET',
        'S_convert.TODO = (METHOD_CONVERT (STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) porigin_capture z_capture) :: ptask_selected_tail*',
        'n_wrapper = |S_convert.OBJECTS|',
        'S_wrapped = $drive_steps(S_convert[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S_read,3)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_convert.OBJECTS ++ [METHODCLOSURE pfunction.ORIGIN porigin_capture porigin_class eps]',
        'S_wrapped.TODO = ptask_selected_tail*',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = eps', '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_selector) = 1',
        'S_producer_found = $cvstatic232_producer_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_wrapper_producer = n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)', 'pcallcontext_producer.RECEIVER = eps',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '~((HOBJECT n_selector) <- S_producer.ALLOCATIONS)', '$heap_owners($heap_graph(S_producer),HOBJECT n_selector) = 0',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("producer")) = eps',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late_cell)', 'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))', 'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$magic_producer_facts_valid(S_producer,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        'S_result_found = $cvstatic232_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pvalue_returned = pvalue_string', 'pmagicmethodcall_result = pmagicmethodcall_selected',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_string],[pmagicproducerfact_selected]) = ([PBOOL false,pvalue_string])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_string],eps) = eps',
        'S_handler_found = $cvstatic232_handler_seek(S_result,2048)', 'S_handler_found.COMPLETION = BUDGET',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', HANDLER.replace('S.', 'S_handler.'),
        'pmagicmethodcall_handler = pmagicmethodcall_selected', 'pvalue_items* = [PBOOL false,pvalue_string]',
        '$lookup($global_table_view(S_handler).ENV,$ptascii("kept")) = (n_kept_cell)', 'S_handler.STORE[n_kept_cell] = DEFINED pvalue_string',
        'S_after_found = $cvstatic232_after_seek(S_handler,2048)', 'S_after_found.COMPLETION = BUDGET',
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
