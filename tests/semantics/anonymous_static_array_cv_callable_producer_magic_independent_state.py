#!/usr/bin/env python3
"""Runtime callback arrays retire after selection, before real arguments finish."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_function_cv_callable_producer_magic_independent_state as previous
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_array_cv_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
HELPERS = r'''
dec $arraycv249_outer_one(ptask) : pmagicmethodcall?
def $arraycv249_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $arraycv249_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $arraycv249_outer_one(ptask) = eps -- otherwise
dec $arraycv249_outer(ptask*) : pmagicmethodcall?
def $arraycv249_outer(eps) = eps
def $arraycv249_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $arraycv249_outer_one(ptask) = (pmagicmethodcall)
def $arraycv249_outer(ptask :: ptask_tail*) = $arraycv249_outer(ptask_tail*) -- if $arraycv249_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    fcc = case['producer_mode'] == 'fcc'
    index = 1 if fcc else 0
    read = ('S.TODO = (' + ('FIRSTCLASS_CONVERT porigin_selection z_init z_convert' if fcc else
                           'CALL_DYNAMIC porigin_selection z_init z_call') + ') :: ptask_read_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("callee")) z_cv -- if S.CURRENT = eps')
    ready = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
             '-- if S.CURRENT = eps')
    body = ('S.TODO = (RETURN_VALUE z_return) :: ptask_body_tail* -- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved '
            '-- if S.CURRENT = (pcallcontext_body)')
    result = ('S.TODO = (' + ('MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])' if fcc else
                             'CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_result) eps 0 eps (porigin_result) z_result')
              + ') :: ptask_result_tail* -- if S.RESULT = KNOWN pvalue_result -- if S.CURRENT = eps')
    after = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_return])) metadata_echo)) :: ptask_after_tail* '
             '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
    prefix = (previous.OUTPUT + HELPERS + previous.HELPERS[previous.HELPERS.index('dec $cvfunction247_code_at'):]
              + ''.join(previous.seeker(label, front) for label, front in
                        [('read', read), ('ready', ready), ('body', body), ('result', result), ('after', after)]))
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $cvfunction247_read_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', read, 'S.ORIGIN = (porigin_selection)',
              '$arraycv249_outer(ptask_read_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = eps', 'pmagicmethodcall.PRODUCERS = eps',
              '$call_argument_origin(S,(pmagicmethodcall.SITE),' + str(index) + ') = (porigin_producer)',
              'porigin_producer = PORIGIN n_unit pcpath_producer',
              '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
              'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer',
              '|phpType7_real*| = 2', 'expression_callback = NExprVariable (BYTES text_callback) metadata_callback',
              '$base64(text_callback) = $ptascii("callee")', 'porigin_selection = PORIGIN n_unit pcpath_selection',
              'pcpath_selection = ' + ('pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'),
              'porigin_callback = PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])',
              '$source_emission_cv(S,n_unit,pcpath_selection ++ [PCFIELD 0],expression_callback)',
              '$compiled_read(S,porigin_callback) = eps', '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
              '$code_expression(pcode.EXPRESSIONS,pcpath_selection ++ [PCFIELD 0]) = ((z_cv,false))',
              '$code_name(pcode.NAMES,pcpath_selection) = eps', '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
                   'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]', '$firstclass_task_valid(S,porigin_selection,z_init,z_convert)']
    else:
        checks += ['phpType7_capture* = phpType7_real*', '$dynamic_task_valid(S,porigin_selection,z_init,z_call)']
    checks += ['$magic_producer_cv_parts(S,porigin_producer,expression_producer) = ((porigin_selection,S.RESULT,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
               '$lookup(S.ENV,$ptascii("callee")) = (n_callee)', 'S.STORE[n_callee] = DEFINED (PARRAY n_callback)',
               'S.ARRAYS[n_callback] = parray_callback',
               'parray_callback.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_class),ENTRY (KINT 1) (DIRECT pvalue_method)]',
               'pvalue_class = PSTRING_CARRIER (REQUEST_STRING n_name) ($ptascii("ReviewChild249"))',
               '$string_bytes(pvalue_method) = ($ptascii("capture"))', '$string_carrier_valid(S,pvalue_class)',
               '(HARRAY n_callback) <- S.ALLOCATIONS', '~((HARRAY n_callback) <- $pools_nodes(S.POOLS))',
               '$node_children(S,HARRAY n_callback) = eps', '$heap_owners($heap_graph(S),HARRAY n_callback) = 1',
               '$magic_producer_array_cell(S,$ptascii("callee")) = (n_callback)',
               '$magic_producer_static_array_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
               '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
               '$magic_producer_array_cell(S[.ENV = eps],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.STORE[n_callee] = UNDEFINED],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.STORE[n_callee] = DEFINED PNULL],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.LITERALREFDEBTS = [n_callee]],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.STRINGDATA = eps],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS,HARRAY n_callback)],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.ARRAYS[n_callback] = parray_callback[.ITEMS = eps]],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.ARRAYS[n_callback] = parray_callback[.ITEMS = [ENTRY (KINT 0) (ALIAS n_callee),ENTRY (KINT 1) (DIRECT pvalue_method)]]],$ptascii("callee")) = eps',
               '$magic_producer_array_cell(S[.ARRAYS[n_callback] = parray_callback[.ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("ReviewChild249")))),ENTRY (KINT 1) (DIRECT pvalue_method)]]],$ptascii("callee")) = eps',
               '~$magic_producer_static_array_read(S[.ARRAYS[n_callback] = parray_callback[.ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ($ptascii("self")))),ENTRY (KINT 1) (DIRECT pvalue_method)]]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
               '$class_named(S.CLASSNAMES,$ptascii("reviewchild249")) = (porigin_requested)',
               '$effective_method(S,porigin_requested,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc)',
               'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.OWNER =/= porigin_requested',
               r'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC /\ pmethoddesc.STATIC',
               '$magic_method_plain_static_source(S,pmethoddesc,phpType7_real*)',
               'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_requested,METHOD pfunction.ORIGIN}',
               '$magic_producer_fact_source(S,pmagicproducerfact)',
               '$class_named(S.CLASSNAMES,$ptascii("wrong249")) = (porigin_wrong)',
               '$effective_method(S,porigin_wrong,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_wrong)',
               '~$magic_producer_fact_source(S,pmagicproducerfact[.CLASS = (porigin_wrong)])',
               '~$magic_producer_fact_source(S,pmagicproducerfact[.METHOD = pmethoddesc_wrong.FUNCTION.ORIGIN])',
               '~$magic_producer_fact_source(S,pmagicproducerfact[.CLASS = eps])',
               '~$magic_producer_fact_source(S[.CLASSES = eps],pmagicproducerfact)',
               '~$magic_producer_fact_source(S[.SOURCES = eps],pmagicproducerfact)',
               '~$magic_producer_fact_source(S[.CODE = [pcode[.EXPRESSIONS = $cvfunction247_without_code(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicproducerfact)',
               '~$magic_producer_fact_source(S[.CODE = [pcode[.EXPRESSIONS = $cvfunction247_without_code(pcode.EXPRESSIONS,pcpath_selection ++ [PCFIELD 0])]]],pmagicproducerfact)',
               '$drive_steps(S,0) = S[.COMPLETION = BUDGET]', 'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
               '$arraycv249_outer(S_selected.TODO) = (pmagicmethodcall_selected)',
               'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact]]',
               'S_selected.ARRAYS = S.ARRAYS', 'S_selected.STORE = S.STORE', 'S_selected.ALLOCATIONS = S.ALLOCATIONS',
               '$heap_owners($heap_graph(S_selected),HARRAY n_callback) = 1',
               '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
               '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact])',
               '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact,pmagicproducerfact])',
               '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact],' + str(index) + ')',
               '$task_nodes(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_selected) eps 0 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE) = $task_nodes(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE)',
               'S_ready_found = $cvfunction247_ready_seek(S_selected,2048)', 'S_ready_found.COMPLETION = BUDGET',
               'S_ready = S_ready_found[.COMPLETION = NORMAL]', previous.at(ready, 'S_ready'),
               'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
               '$target_function(S_ready,pcalltarget_ready) = (pfunction)', '$target_receiver(S_ready,pcalltarget_ready) = eps',
               '$target_lexical_class(S_ready,pcalltarget_ready) = (pmethoddesc.OWNER)', '$target_called_class(S_ready,pcalltarget_ready) = (porigin_requested)',
               'pcalltarget_static = STATIC_METHOD_TARGET porigin_requested pfunction.ORIGIN']
    if fcc:
        checks += ['$lookup(S.ENV,$ptascii("alias")) = (n_callee)', 'n_callee <- S.REFCELLS',
                   'n_wrapper = |S.OBJECTS|', 'pcalltarget_ready = CLOSURE_TARGET n_wrapper',
                   'S_ready.OBJECTS[n_wrapper] = ARRAYMETHODCLOSURE pcalltarget_static parrayselection eps',
                   '$node_children(S_ready,HOBJECT n_wrapper) = eps',
                   '$target_nodes(pcalltarget_ready) = [HOBJECT n_wrapper]']
    else:
        checks += ['~(n_callee <- S.REFCELLS)', 'pcalltarget_ready = ARRAY_METHOD_TARGET pcalltarget_static parrayselection',
                   '$target_nodes(pcalltarget_ready) = eps']
    checks += ['parrayselection.REQUESTED = porigin_requested', 'parrayselection.NAME = $ptascii("capture")', 'parrayselection.SITE = porigin_selection',
               '$array_target_identity(S_ready,pcalltarget_static,parrayselection)',
               '$array_site_valid(S_ready,parrayselection,' + ('true' if fcc else 'false') + ')',
               '~$array_target_identity(S_ready,pcalltarget_static,parrayselection[.NAME = $ptascii("wrong")])',
               '~$array_target_identity(S_ready,pcalltarget_static,parrayselection[.REQUESTED = porigin_wrong])',
               '~$array_site_valid(S_ready,parrayselection[.INIT = $(z_init + 100)],' + ('true' if fcc else 'false') + ')',
               'S_identity = S_ready[.TODO = eps]',
               '$method_selected_metadata(S_identity,ARRAY_METHOD_TARGET pcalltarget_static parrayselection,(porigin_selection)) = S_identity']
    if fcc:
        checks += ['S_capture_identity = $function_cache_fcc(S_identity,pcalltarget_static,porigin_selection)[.TODO = (ARRAY_CONVERT ($scope_target_site(S_identity,pcalltarget_static,porigin_selection,true)) parrayselection) :: S_identity.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$array_capture_result(S_identity,ARRAYRESOLVED pcalltarget_static porigin_requested ($ptascii("capture")),porigin_selection,z_init,parrayselection.LINE) = S_capture_identity']
    else:
        checks += ['S_dynamic_identity = S_identity[.TODO = $method_args_task(ARRAY_METHOD_TARGET ($scope_target_site(S_identity,pcalltarget_static,porigin_selection,false)) parrayselection,$dynamic_arguments(S_identity,porigin_selection),(porigin_selection),parrayselection.LINE) :: S_identity.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$array_dynamic_result(S_identity,ARRAYRESOLVED pcalltarget_static porigin_requested ($ptascii("capture")),porigin_selection,z_init,parrayselection.LINE) = S_dynamic_identity']
    checks += [
               'S_body_found = $cvfunction247_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
               'S_body = S_body_found[.COMPLETION = NORMAL]', previous.at(body, 'S_body'),
               'pcallcontext_body.TARGET = pcalltarget_ready', 'pcallcontext_body.FUNCTION = pfunction.ORIGIN',
               'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_body.CALLED_CLASS = (porigin_requested)',
               'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
               '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
               '$lookup($global_table_view(S_body).ENV,$ptascii("callee")) = eps',
               '~((HCELL n_callee) <- S_body.ALLOCATIONS)', '~((HARRAY n_callback) <- S_body.ALLOCATIONS)',
               '$heap_owners($heap_graph(S_body),HARRAY n_callback) = 0', '$magic_producer_fact_source(S_body,pmagicproducerfact)',
               '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
               '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)',
               'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
               'S_result_found = $cvfunction247_result_seek(S_body,2048)', 'S_result_found.COMPLETION = BUDGET',
               'S_result = S_result_found[.COMPLETION = NORMAL]', previous.at(result, 'S_result'),
               'pmagicmethodcall_result = pmagicmethodcall_selected', 'pvalue_result = POBJECT n_old',
               '~((HCELL n_saved) <- S_result.ALLOCATIONS)',
               '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,' + ('[KNOWN (PBOOL false),KNOWN pvalue_result]' if fcc else '[KNOWN pvalue_result]') + ',[pmagicproducerfact]) = (' + ('[PBOOL false,pvalue_result]' if fcc else '[pvalue_result]') + ')',
               'S_after_found = $cvfunction247_after_seek(S_result,2048)', 'S_after_found.COMPLETION = BUDGET',
               'S_after = S_after_found[.COMPLETION = NORMAL]', previous.at(after, 'S_after'),
               '~((HOBJECT pmagicmethodcall.OBJECT) <- S_after.ALLOCATIONS)',
               '$lookup(S_after.ENV,$ptascii("child")) = (n_child_cell)', 'S_after.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
               '$objectprops_at(S_after.OBJECTPROPS,n_child) = (ppropertyslot_child*)',
               '$property_slot_at(ppropertyslot_child*,$ptascii("saved")) = (ppropertyslot_saved)',
               'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
               'S_after.ARRAYS[n_arguments].ITEMS = ' + ('[ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("last")) (DIRECT (POBJECT n_old))]' if fcc else '[ENTRY (KINT 0) (DIRECT (POBJECT n_old))]'),
               '$heap_valid($heap_graph(S_after))']
    if fcc:
        checks += ['$lookup($global_table_view(S_body).ENV,$ptascii("alias")) = eps', '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)']
    checks += ['S_done = $drive_steps(S_after,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
               '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(case['stdout_template_base64']), filename),
               '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
               '$magic_producer_fact_source(S_done,pmagicproducerfact)',
               'S_one = $drive_steps(S_after,1)', '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=ROWS)
    args = parser.parse_args()
    protocol.run({name: ROWS[name] for name in (args.case or ROWS)},
                 (Path(__file__), CATALOGUE, Path(previous.__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
