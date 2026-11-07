#!/usr/bin/env python3
"""Function CV lookup precedes arguments; its borrowed fact outlives the caller."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_function_cv_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases'] if 'builtin-bound' not in row['id']}
OUTPUT = names.PREFIX[:names.PREFIX.index('dec $factory182_front')]
HELPERS = r'''
dec $cvfunction247_outer_one(ptask) : pmagicmethodcall?
def $cvfunction247_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cvfunction247_outer_one(ptask) = eps -- otherwise
dec $cvfunction247_outer(ptask*) : pmagicmethodcall?
def $cvfunction247_outer(eps) = eps
def $cvfunction247_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvfunction247_outer_one(ptask) = (pmagicmethodcall)
def $cvfunction247_outer(ptask :: ptask_tail*) = $cvfunction247_outer(ptask_tail*) -- if $cvfunction247_outer_one(ptask) = eps
dec $cvfunction247_code_at(pcodeexpr, pcpath) : bool
def $cvfunction247_code_at(CODEEXPR pcpath z b, pcpath) = true
def $cvfunction247_code_at(CODECALL_INIT pcpath z, pcpath) = true
def $cvfunction247_code_at(pcodeexpr, pcpath) = false -- otherwise
dec $cvfunction247_without_code(pcodeexpr*, pcpath) : pcodeexpr*
def $cvfunction247_without_code(eps, pcpath) = eps
def $cvfunction247_without_code(pcodeexpr :: pcodeexpr_tail*, pcpath) = $cvfunction247_without_code(pcodeexpr_tail*, pcpath) -- if $cvfunction247_code_at(pcodeexpr, pcpath)
def $cvfunction247_without_code(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $cvfunction247_without_code(pcodeexpr_tail*, pcpath) -- if ~$cvfunction247_code_at(pcodeexpr, pcpath)
'''


def seeker(label, front):
    stem = '$cvfunction247_' + label
    return ('\ndec ' + stem + '_front(pstate) : bool\n'
            'def ' + stem + '_front(S) = true -- if ' + front + '\n'
            'def ' + stem + '_front(S) = false -- otherwise\n'
            'dec ' + stem + '_seek(pstate, nat) : pstate\n'
            'def ' + stem + '_seek(S, 0) = S\n'
            'def ' + stem + '_seek(S, n) = S -- if $(n > 0) /\\ ' + stem + '_front(S)\n'
            'def ' + stem + '_seek(S, n) = ' + stem + '_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))\n'
            '  -- if $(n > 0) /\\ ~' + stem + '_front(S) /\\ S.TODO =/= eps\n'
            '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def ' + stem + '_seek(S, n) = S -- if $(n > 0) /\\ ~' + stem + '_front(S) /\\ S.TODO = eps\n'
            'def ' + stem + '_seek(S, n) = S -- if $(n > 0) /\\ ~' + stem + '_front(S) /\\ S.TODO =/= eps\n'
            '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n')


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = '-fcc-' in case['id']
    read = ('S.TODO = (' + ('FIRSTCLASS_CONVERT porigin_selection z_init z_convert' if fcc else
                           'CALL_DYNAMIC porigin_selection z_init z_call') + ') :: ptask_read_tail* '
            '-- if S.RESULT = VARIABLE ($ptascii("callee")) z_cv -- if S.CURRENT = (pcallcontext_caller)')
    ready = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
             '-- if S.CURRENT = (pcallcontext_ready)')
    body = ('S.TODO = (RETURN_VALUE z_return) :: ptask_body_tail* -- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved '
            '-- if S.CURRENT = (pcallcontext_body)')
    result = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
              '-- if S.RESULT = KNOWN pvalue_result -- if S.CURRENT = (pcallcontext_result)')
    after = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_return])) metadata_echo)) :: ptask_after_tail* '
             '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
    prefix = OUTPUT + HELPERS + ''.join(seeker(label, front) for label, front in
                                         [('read', read), ('ready', ready), ('body', body), ('result', result), ('after', after)])
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $cvfunction247_read_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', read, 'S.ORIGIN = (porigin_selection)',
              '$cvfunction247_outer(ptask_read_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
              'pmagicmethodcall.CALLER = (pcallcontext_caller)',
              '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
              'porigin_producer = PORIGIN n_unit pcpath_producer',
              '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
              'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer',
              '|phpType7_real*| = 2']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
                   'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]',
                   '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
                   '$firstclass_task_valid(S,porigin_selection,z_init,z_convert)']
    else:
        checks += ['phpType7_capture* = phpType7_real*', '$dynamic_task_valid(S,porigin_selection,z_init,z_call)']
    checks += ['porigin_selection = PORIGIN n_unit pcpath_selection',
               'pcpath_selection = ' + ('pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'),
               'porigin_callback = PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])',
               'expression_callback = NExprVariable (BYTES text_callback) metadata_callback',
               '$base64(text_callback) = $ptascii("callee")',
               '$origin_node(S.SOURCES,porigin_callback) = (expression_callback)',
               '$source_emission_cv(S,n_unit,pcpath_selection ++ [PCFIELD 0],expression_callback)',
               '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
               '$code_expression(pcode.EXPRESSIONS,pcpath_selection ++ [PCFIELD 0]) = ((z_cv,false))',
               '$code_name(pcode.NAMES,pcpath_selection) = eps', '$dynamic_fixed_name(S,porigin_selection) = eps',
               '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)',
               '$magic_producer_cv_parts(S,porigin_producer,expression_producer) = ((porigin_selection,S.RESULT,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
               '$magic_producer_argument_site(S,porigin_selection) = (porigin_producer)',
               '$magic_producer_pending(S,S.TODO,porigin_producer) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
               '$lookup(S.ENV,$ptascii("callee")) = (n_callee)', 'S.STORE[n_callee] = DEFINED pvalue_name',
               '$string_bytes(pvalue_name) = (ptbytes_name)', '$string_carrier_valid(S,pvalue_name)',
               '$call_target(S,$dynamic_lookup_name(ptbytes_name),eps) = (pfunction)',
               '$magic_producer_function_cell(S,$ptascii("callee")) = (pfunction)',
               '$magic_producer_function_source(S,porigin_producer,pfunction.ORIGIN)',
               '$magic_producer_function_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
               '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
               '~$magic_producer_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
               '$call_target(S,$ptascii("caller247\\\\saved247"),eps) = (pfunction_decoy)',
               'pfunction.ORIGIN =/= pfunction_decoy.ORIGIN',
               '$ptlc(pfunction.NAME) = $ptascii(' + json.dumps('payload247\\saved247' if fcc else 'saved247') + ')',
               'pfunction.SIGNATURE.RETURNS = eps',
               '$magic_method_copy_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1,[KNOWN (PINT 9)]) = eps',
               '$magic_producer_function_cell(S[.ENV = eps],$ptascii("callee")) = eps',
               '$magic_producer_function_cell(S[.STORE[n_callee] = UNDEFINED],$ptascii("callee")) = eps',
               '$magic_producer_function_cell(S[.STORE[n_callee] = DEFINED PNULL],$ptascii("callee")) = eps',
               '$magic_producer_function_cell(S[.STORE[n_callee] = DEFINED (PSTRING ptbytes_name)],$ptascii("callee")) = eps',
               '~$magic_producer_function_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),eps)',
               '~$magic_producer_function_source(S[.CALLABLES = eps],porigin_producer,pfunction.ORIGIN)',
               '~$magic_producer_function_source(S,porigin_callback,pfunction.ORIGIN)',
               '~$magic_producer_function_source(S[.CODE = [pcode[.NAMES = (CODENAME pcpath_selection ($ptascii("saved247")) eps) :: pcode.NAMES]]],porigin_producer,pfunction.ORIGIN)',
               '~$magic_producer_function_source(S[.CODE = [pcode[.EXPRESSIONS = $cvfunction247_without_code(pcode.EXPRESSIONS,pcpath_selection)]]],porigin_producer,pfunction.ORIGIN)',
               '~$magic_producer_function_source(S[.CODE = [pcode[.EXPRESSIONS = $cvfunction247_without_code(pcode.EXPRESSIONS,pcpath_selection ++ [PCFIELD 0])]]],porigin_producer,pfunction.ORIGIN)',
               'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
               'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
               '$cvfunction247_outer(S_selected.TODO) = (pmagicmethodcall_selected)',
               'pmagicproducerfact_selected = {SITE porigin_producer,CLASS eps,METHOD pfunction.ORIGIN}',
               'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_selected]]',
               '$magic_producer_fact_source(S_selected,pmagicproducerfact_selected)',
               '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
               '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected,pmagicproducerfact_selected])',
               '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],1)',
               '$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],2)',
               '~$magic_producer_fact_source(S_selected,pmagicproducerfact_selected[.CLASS = (pmagicmethodcall.CLASS)])',
               '~$magic_producer_fact_source(S_selected,pmagicproducerfact_selected[.METHOD = pcallcontext_caller.FUNCTION])',
               '$task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall_selected 1 ([KNOWN (PBOOL false)])) = $task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)]))']
    if fcc:
        checks += ['$lookup($global_table_view(S).ENV,$ptascii("alias")) = (n_callee)',
                   'n_callee <- S.REFCELLS', 'n_wrapper = |S.OBJECTS|',
                   'S_selected.OBJECTS[n_wrapper] = NAMEDCLOSURE pfunction.ORIGIN',
                   '$node_children(S_selected,HOBJECT n_wrapper) = eps',
                   '$closure_scope_at(S_selected.CLOSURESCOPES,n_wrapper) = eps']
    else:
        checks += ['|S_selected.OBJECTS| = |S.OBJECTS|']
    checks += ['S_ready_found = $cvfunction247_ready_seek(S_selected,2048)', 'S_ready_found.COMPLETION = BUDGET',
               'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(ready, 'S_ready'),
               'pcallcontext_ready = pcallcontext_caller', 'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
               '$target_function(S_ready,pcalltarget_ready) = (pfunction)', '$target_receiver(S_ready,pcalltarget_ready) = eps',
               '$target_lexical_class(S_ready,pcalltarget_ready) = eps', '$target_called_class(S_ready,pcalltarget_ready) = eps',
               'S_body_found = $cvfunction247_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
               'S_body = S_body_found[.COMPLETION = NORMAL]', at(body, 'S_body'),
               'pcallcontext_body.FUNCTION = pfunction.ORIGIN', 'pcallcontext_body.TARGET = pcalltarget_ready',
               'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.LEXICAL_CLASS = eps', 'pcallcontext_body.CALLED_CLASS = eps',
               '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)',
               'S_body.STORE[n_saved] = DEFINED pvalue_old',
               'pvalue_old = PSTRING_CARRIER (REQUEST_STRING n_old) ($ptascii("REQUEST-OLD"))',
               '$lookup($global_table_view(S_body).ENV,$ptascii("late")) = (n_late)',
               'S_body.STORE[n_late] = DEFINED (PINT 99)',
               'S_result_found = $cvfunction247_result_seek(S_body,2048)', 'S_result_found.COMPLETION = BUDGET',
               'S_result = S_result_found[.COMPLETION = NORMAL]', at(result, 'S_result'),
               'pcallcontext_result = pcallcontext_caller', 'pmagicmethodcall_result = pmagicmethodcall_selected',
               'pvalue_result = pvalue_old', '~((HCELL n_saved) <- S_result.ALLOCATIONS)',
               '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old],[pmagicproducerfact_selected]) = ([PBOOL false,pvalue_old])',
               '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old],eps) = eps',
               'S_after_found = $cvfunction247_after_seek(S_result,2048)', 'S_after_found.COMPLETION = BUDGET',
               'S_after = S_after_found[.COMPLETION = NORMAL]', at(after, 'S_after'),
               'pcallcontext_caller.RECEIVER = (n_this)', '~((HOBJECT n_this) <- S_after.ALLOCATIONS)',
               '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
               '$lookup(S_after.ENV,$ptascii("child")) = (n_child_cell)', 'S_after.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
               '$objectprops_at(S_after.OBJECTPROPS,n_child) = (ppropertyslot_child*)',
               '$property_slot_at(ppropertyslot_child*,$ptascii("saved")) = (ppropertyslot_saved)',
               'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
               'S_after.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT pvalue_old)]',
               '$magic_producer_fact_source(S_after,pmagicproducerfact_selected)',
               '$string_carrier_valid(S_after,pvalue_old)', '$heap_valid($heap_graph(S_after))']
    if fcc:
        checks += ['pcalltarget_ready = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
                   '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
                   '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
                   '$lookup($global_table_view(S_body).ENV,$ptascii("callee")) = eps',
                   '$lookup($global_table_view(S_body).ENV,$ptascii("alias")) = (n_callee)',
                   'S_body.STORE[n_callee] = DEFINED pvalue_name',
                   '$lookup(S_after.ENV,$ptascii("callee")) = eps']
    else:
        checks += ['pcalltarget_ready = pfunction.ORIGIN', 'pcallcontext_body.INSTANCE = eps',
                   '$call_context_roots(S_body.CURRENT) = eps', '$target_nodes(pcalltarget_ready) = eps',
                   '$lookup($global_table_view(S_body).ENV,$ptascii("callee")) = (n_callee)',
                   'S_body.STORE[n_callee] = DEFINED pvalue_retarget',
                   '$string_bytes(pvalue_retarget) = ($ptascii("Caller247\\\\wrong247"))',
                   '$call_target(S_body,$dynamic_lookup_name($ptascii("Caller247\\\\wrong247")),eps) = (pfunction_retarget)',
                   'pfunction_retarget.ORIGIN =/= pfunction.ORIGIN']
    checks += ['S_done = $drive_steps(S_after,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
               '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(case['stdout_template_base64']), filename),
               '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
               '$magic_producer_fact_source(S_done,pmagicproducerfact_selected)',
               'S_one = $drive_steps(S_after,1)', 'S_one.COMPLETION = BUDGET',
               '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=ROWS)
    args = parser.parse_args()
    protocol.run({name: ROWS[name] for name in (args.case or ROWS)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
