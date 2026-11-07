#!/usr/bin/env python3
"""SL checks for literal function names, ordinary targets and caller retirement."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_function_string_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
DEFAULTS = [name for name in ROWS if '-direct-peer-global-' in name or '-fcc-peer-qualified-' in name]
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(
    'def $factory182_seek(S, n) = $factory182_seek(',
    'def $factory182_seek(S, n) = S -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO = eps\n'
    'def $factory182_seek(S, n) = $factory182_seek(').replace(
    '  -- if $(n > 0) /\\ ~$factory182_front(S)\n',
    '  -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO =/= eps\n')
HELPERS = r'''
dec $peerfunction246_outer(ptask*) : pmagicmethodcall?
def $peerfunction246_outer(eps) = eps
def $peerfunction246_outer((MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) :: ptask_tail*) = (pmagicmethodcall)
def $peerfunction246_outer(ptask :: ptask_tail*) = $peerfunction246_outer(ptask_tail*) -- otherwise
dec $peerfunction246_init_at(pcodeexpr, pcpath) : bool
def $peerfunction246_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $peerfunction246_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $peerfunction246_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $peerfunction246_without_init(eps, pcpath) = eps
def $peerfunction246_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $peerfunction246_without_init(pcodeexpr_tail*, pcpath) -- if $peerfunction246_init_at(pcodeexpr, pcpath)
def $peerfunction246_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $peerfunction246_without_init(pcodeexpr_tail*, pcpath) -- if ~$peerfunction246_init_at(pcodeexpr, pcpath)
'''


def seeker(label, front):
    return PREFIX[PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$peerfunction246_' + label + '_')


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = '-fcc-' in case['id']
    front = ('S.TODO = (FIRSTCLASS_CONVERT porigin_selection z_init z_call) :: ptask_selection_tail* ' if fcc else
             'S.TODO = (EVAL (NExprFuncCall (NScalarString (BYTES text_selected) metadata_selected) (SEQUENCE phpType7_selected*) metadata_selection)) :: ptask_selection_tail* ')
    front += '-- if S.CURRENT = (pcallcontext_caller)'
    ready = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
             '-- if S.CURRENT = (pcallcontext_ready)')
    body = ('S.TODO = (RETURN_VALUE z_return) :: ptask_body_tail* -- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved '
            '-- if S.CURRENT = (pcallcontext_body)')
    prefix = PREFIX.replace(names.FRONT, front) + HELPERS
    for label, stop in [('ready', ready), ('body', body), ('after', AFTER)]:
        prefix += seeker(label, stop)
    proof = ('$magic_method_firstclass_producer({state},porigin_producer,expression_producer)' if fcc else
             '$magic_method_required_producer({state},porigin_producer,expression_producer)')
    helper = '$magic_method_function_string_source({state},porigin_selection,expression_callback,phpType7_real*)'
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', front,
              '$peerfunction246_outer(ptask_selection_tail*) = (pmagicmethodcall)',
              'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
              '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
              'porigin_producer = PORIGIN n_unit pcpath_producer',
              '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
              'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture']
    checks += ['pcpath_selection = ' + ('pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'),
               'porigin_selection = PORIGIN n_unit pcpath_selection',
               'porigin_callback = PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])',
               'expression_callback = NScalarString (BYTES text_callback) metadata_callback',
               '$origin_node(S.SOURCES,porigin_callback) = (expression_callback)',
               '$ppcall_literal(expression_callback) = ($base64(text_callback))',
               '$compiled_read(S,porigin_callback) = eps', '$compiled_effects(S,porigin_callback) = eps',
               '$value_nodes(PSTRING ($base64(text_callback))) = eps',
               '$class_named(S.CLASSNAMES,$ptascii("caller246\\\\peerscope246")) = (porigin_scope)',
               '$class_named(S.CLASSNAMES,$ptascii("caller246\\\\peerchild246")) = (porigin_child)',
               'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_child)',
               'pcallcontext_caller.RECEIVER = (n_this)', '$object_class_origin(S,n_this) = (porigin_child)',
               helper.format(state='S') + ' = (pfunction)', proof.format(state='S') + ' = (pfunction)',
               '$call_target(S,$ppcall_literal_name($base64(text_callback)),eps) = (pfunction)',
               '$call_target(S,$ptascii("caller246\\\\peercapture246"),eps) = (pfunction_decoy)',
               'pfunction_decoy.ORIGIN =/= pfunction.ORIGIN',
               '$ptlc(pfunction.NAME) = $ptascii(' + json.dumps('payload246\\peercapture246' if fcc else 'peercapture246') + ')',
               '|phpType7_real*| = 2', 'pfunction.SIGNATURE.RETURNS = eps',
               '$magic_method_argument_source(S,porigin_producer,1,expression_producer)',
               '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
               '~$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS ++ [pmagicmethodcall.ARGUMENTS[1]],2)',
               '$magic_method_copy_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS ++ [pmagicmethodcall.ARGUMENTS[1]],2,[KNOWN (PINT 6)]) = eps',
               '~$magic_method_context_call(expression_producer)',
               '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
               '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
               '$code_name(pcode.NAMES,pcpath_selection) = (($ppcall_literal_name($base64(text_callback)),eps))',
               '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
               helper.format(state='S[.CURRENT = eps][.POOLS = eps]') + ' = (pfunction)',
               helper.format(state='S[.SOURCES = eps]') + ' = eps',
               helper.format(state='S[.CODE = eps]') + ' = eps',
               helper.format(state='S[.CALLABLES = eps]') + ' = eps',
               '$magic_method_function_string_source(S,porigin_selection,expression_callback,eps) = eps',
               '$magic_method_function_string_source(S,porigin_selection,expression_callback,[NVariadicPlaceholder metadata_producer]) = eps',
               '$magic_method_function_string_source(S,porigin_callback,expression_callback,phpType7_real*) = eps',
               helper.format(state='S[.CODE = [pcode[.NAMES = (CODENAME pcpath_selection ($ptascii("Caller246\\\\peerCapture246")) eps) :: pcode.NAMES]]]') + ' = eps',
               helper.format(state='S[.CODE = [pcode[.NAMES = (CODENAME pcpath_selection ($ppcall_literal_name($base64(text_callback))) ($ptascii("fallback"))) :: pcode.NAMES]]]') + ' = eps',
               proof.format(state='S[.CODE = [pcode[.EXPRESSIONS = $peerfunction246_without_init(pcode.EXPRESSIONS,pcpath_producer)]]]') + ' = eps',
               '$heap_owners($heap_graph(S),HOBJECT n_this) = 2',
               'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]']
    if fcc:
        checks += ['$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
                   proof.format(state='S[.CODE = [pcode[.EXPRESSIONS = $peerfunction246_without_init(pcode.EXPRESSIONS,pcpath_selection)]]]') + ' = eps',
                   'n_wrapper = |S.OBJECTS|', 'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
                   'S_selected.OBJECTS[n_wrapper] = NAMEDCLOSURE pfunction.ORIGIN',
                   '$node_children(S_selected,HOBJECT n_wrapper) = eps',
                   '$closure_scope_at(S_selected.CLOSURESCOPES,n_wrapper) = eps']
    else:
        checks += ['$magic_method_argument_call(expression_producer)', 'S.ORIGIN = (porigin_selection)',
                   '$magic_method_required_producer(S,porigin_producer,NExprFuncCall expression_callback (SEQUENCE ([phpType7_real*[1],phpType7_real*[0]])) metadata_producer) = eps',
                   'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
                   '|S_selected.OBJECTS| = |S.OBJECTS|']
    checks += ['S_ready_found = $peerfunction246_ready_seek(S_selected,2048)', 'S_ready_found.COMPLETION = BUDGET',
               'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(ready, 'S_ready'),
               'pcallcontext_ready = pcallcontext_caller', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
               '$target_function(S_ready,pcalltarget_ready) = (pfunction)',
               '$target_receiver(S_ready,pcalltarget_ready) = eps',
               '$target_lexical_class(S_ready,pcalltarget_ready) = eps', '$target_called_class(S_ready,pcalltarget_ready) = eps',
               'S_body_found = $peerfunction246_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
               'S_body = S_body_found[.COMPLETION = NORMAL]', at(body, 'S_body'),
               'pcallcontext_body.TARGET = pcalltarget_ready', 'pcallcontext_body.FUNCTION = pfunction.ORIGIN',
               'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.LEXICAL_CLASS = eps', 'pcallcontext_body.CALLED_CLASS = eps',
               '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1',
               '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 1',
               '$lookup($global_table_view(S_body).ENV,$ptascii("runner")) = (n_runner)', 'S_body.STORE[n_runner] = DEFINED PNULL',
               '$lookup($global_table_view(S_body).ENV,$ptascii("late")) = (n_late)', 'S_body.STORE[n_late] = DEFINED (PINT 99)',
               '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED pvalue_old',
               'pvalue_old = PSTRING_CARRIER (REQUEST_STRING n_old) ($ptascii("REQUEST-OLD"))',
               '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
               'S_after_found = $peerfunction246_after_seek(S_body,2048)', 'S_after_found.COMPLETION = BUDGET',
               'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
               '~((HOBJECT n_this) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
               '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)', 'S_after.STORE[n_kept] = DEFINED pvalue_old',
               '$lookup(S_after.ENV,$ptascii("late")) = (n_late_after)',
               'S_after.STORE[n_late_after] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_end) ($ptascii("REQUEST-END")))',
               proof.format(state='S_after') + ' = (pfunction)',
               '$magic_method_collected_values(S_after,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old]) = ([PBOOL false,pvalue_old])',
               '$string_carrier_valid(S_after,pvalue_old)', '$heap_valid($heap_graph(S_after))']
    if fcc:
        checks += ['pcalltarget_ready = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
                   '~((HOBJECT n_wrapper) <- S_after.ALLOCATIONS)']
    else:
        checks += ['pcalltarget_ready = pfunction.ORIGIN', 'pcallcontext_body.INSTANCE = eps', '$target_nodes(pcalltarget_ready) = eps']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=DEFAULTS)
    args = parser.parse_args()
    chosen = args.case or DEFAULTS
    protocol.run({name: ROWS[name] for name in chosen},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
