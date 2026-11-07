#!/usr/bin/env python3
"""This-array statics retain the original caller owner and old sent values."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_array_callable_producer_magic_independent_cases.json'
ROWS = {r['id']: r for r in json.loads(CATALOGUE.read_text())['cases']}
DEFAULTS = [name for name in ROWS if not name.endswith('instance-return-this')]
SHADOW = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_shadow_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_caller)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
HELPERS = r'''
dec $peerthis243_outer_one(ptask) : pmagicmethodcall?
def $peerthis243_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $peerthis243_outer_one(ptask) = eps -- otherwise
dec $peerthis243_outer(ptask*) : pmagicmethodcall?
def $peerthis243_outer(eps) = eps
def $peerthis243_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $peerthis243_outer_one(ptask) = (pmagicmethodcall)
def $peerthis243_outer(ptask :: ptask_tail*) = $peerthis243_outer(ptask_tail*) -- if $peerthis243_outer_one(ptask) = eps
dec $peerthis243_init_at(pcodeexpr, pcpath) : bool
def $peerthis243_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $peerthis243_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $peerthis243_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $peerthis243_without_init(eps, pcpath) = eps
def $peerthis243_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $peerthis243_without_init(pcodeexpr_tail*, pcpath) -- if $peerthis243_init_at(pcodeexpr, pcpath)
def $peerthis243_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $peerthis243_without_init(pcodeexpr_tail*, pcpath) -- if ~$peerthis243_init_at(pcodeexpr, pcpath)
dec $peerthis243_expression_at(pcodeexpr, pcpath) : bool
def $peerthis243_expression_at(CODEEXPR pcpath z b, pcpath) = true
def $peerthis243_expression_at(pcodeexpr, pcpath) = false -- otherwise
dec $peerthis243_without_expression(pcodeexpr*, pcpath) : pcodeexpr*
def $peerthis243_without_expression(eps, pcpath) = eps
def $peerthis243_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = $peerthis243_without_expression(pcodeexpr_tail*, pcpath) -- if $peerthis243_expression_at(pcodeexpr, pcpath)
def $peerthis243_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $peerthis243_without_expression(pcodeexpr_tail*, pcpath) -- if ~$peerthis243_expression_at(pcodeexpr, pcpath)
'''


def seeker(label, front):
    return names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$peerthis243_' + label + '_')


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = '-fcc-' in case['id']
    shadow = ROWS[case['id']].get('model_status') == 'unsupported'
    front = ('S.TODO = (' + ('FIRSTCLASS_CONVERT porigin_selection z_init z_convert' if fcc else 'CALL_DYNAMIC porigin_selection z_init z_call') +
             ') :: ptask_select_tail* -- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = (pcallcontext_caller)')
    ready = ('S.TODO = (CALL_ARGS ' + ('(CLOSURE_TARGET n_wrapper)' if fcc else '(ARRAY_METHOD_TARGET pcalltarget parrayselection)') +
             ' phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* -- if S.CURRENT = (pcallcontext_ready)')
    body = ('S.TODO = (RETURN_VALUE z_return) :: ptask_body_tail* -- if S.CURRENT = (pcallcontext_body) -- if pcallcontext_body.TARGET = ' +
            ('CLOSURE_TARGET n_wrapper' if fcc else 'ARRAY_METHOD_TARGET pcalltarget parrayselection'))
    convert = 'S.TODO = (ARRAY_CONVERT pcalltarget parrayselection) :: ptask_convert_tail*'
    prefix = names.PREFIX.replace(names.FRONT, SHADOW if shadow else front) + HELPERS
    for label, stop in [('ready', ready), ('convert', convert), ('body', body), ('after', AFTER)]:
        prefix += seeker(label, stop)
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', SHADOW if shadow else front]
    if shadow:
        checks += ['S.ORIGIN = (porigin_outer)', '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)']
    else:
        checks += ['$peerthis243_outer(ptask_select_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
                   'pmagicmethodcall.PRODUCERS = eps', '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)']
    checks += ['porigin_producer = PORIGIN n_unit pcpath_producer', '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
               'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture']
    site = 'pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'
    checks += ['porigin_site = PORIGIN n_unit (' + site + ')',
               'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_this (BOOLEAN false) (BOOLEAN false) metadata_this_item),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method_item)])) metadata_array',
               'expression_this = NExprVariable (BYTES text_this) metadata_this', '$direct_this(BYTES text_this)',
               'pcpath_this = (' + site + ') ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
               '$source_emission_this_fetch(S,n_unit,pcpath_this,expression_this)',
               '$class_named(S.CLASSNAMES,$ptascii("peerscope243")) = (porigin_scope)',
               '$class_named(S.CLASSNAMES,$ptascii("peerchild243")) = (porigin_class)',
               '$closure_source_class(S,porigin_site) = (porigin_scope)',
               'pcallcontext_caller.RECEIVER = (n_this)', '$object_class_origin(S,n_this) = (porigin_class)',
               'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
               '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]', '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)']
    if fcc:
        checks += ['$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_capture)', '$magic_method_firstclass_site(S,porigin_producer,expression_producer)']
    proof = '$magic_method_this_producer({state},(pcallcontext_caller),porigin_producer,expression_producer)'
    if shadow:
        checks += ['$scope_method(S,porigin_class,$ptascii("capture"),true,(porigin_scope)) = (pmethoddesc_private)',
                   'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
                   '$effective_method(S,porigin_class,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_public)',
                   'pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC', '$magic_method_plain_instance_source(S,pmethoddesc_public,phpType7_real*)',
                   proof.format(state='S') + ' = eps', '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
                   'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"', '$factory182_output(S_done.EVENTS) = eps']
    else:
        checks += ['porigin_selection = porigin_site', '|phpType7_real*| = 2',
                   '$method_class_selected(S,porigin_class,$ptascii("capture"),(porigin_scope)) = (pmethoddesc)',
                   'pmethoddesc.STATIC', proof.format(state='S') + ' = ((n_this,porigin_class,pmethoddesc))',
                   '$magic_method_context_call(expression_producer)', '$magic_method_argument_source(S,porigin_producer,1,expression_producer)',
                   '~$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
                   '$magic_method_this_producer(S,eps,porigin_producer,expression_producer) = eps',
                   '$magic_method_this_producer(S[.SOURCES = eps],(pcallcontext_caller),porigin_producer,expression_producer) = eps']
        for path in ['pcpath_this', 'pcpath_producer'] + (['pcpath_producer ++ [PCFIELD 0]'] if fcc else []):
            helper = '$peerthis243_without_expression' if path == 'pcpath_this' else '$peerthis243_without_init'
            state = 'S[.CODE = [pcode[.EXPRESSIONS = ' + helper + '(pcode.EXPRESSIONS,' + path + ')]]]'
            checks.append(proof.format(state=state) + ' = eps')
        checks += ['S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_this)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
                   'pcalltarget = STATIC_METHOD_TARGET porigin_class pmethoddesc.FUNCTION.ORIGIN',
                   '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED pcalltarget porigin_class ($ptascii("capture"))',
                   '$heap_owners($heap_graph(S),HOBJECT n_this) = 3', '$call_context_roots(S.CURRENT) = [HOBJECT n_this]',
                   'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]', 'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET']
        if fcc:
            checks += ['S_convert_found = $peerthis243_convert_seek(S_selected,2048)', 'S_convert_found.COMPLETION = BUDGET',
                       'S_convert = S_convert_found[.COMPLETION = NORMAL]', at(convert, 'S_convert'),
                       'parrayselection.SITE = porigin_site', 'parrayselection.INIT = z_capture', 'parrayselection.LINE = z_convert',
                       '$array_convert_valid(S_convert,pcalltarget,parrayselection)',
                       'n_wrapper = |S_convert.OBJECTS|', 'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
                       'pmethodcapture? = $method_capture_current(S_convert,porigin_site)',
                       'S_wrapped.OBJECTS[n_wrapper] = ARRAYMETHODCLOSURE pcalltarget parrayselection pmethodcapture?',
                       '$node_children(S_wrapped,HOBJECT n_wrapper) = eps']
        checks += ['S_ready_found = $peerthis243_ready_seek(' + ('S_wrapped' if fcc else 'S_selected') + ',2048)', 'S_ready_found.COMPLETION = BUDGET',
                   '$peerthis243_ready_seek(' + ('S_convert' if fcc else 'S') + ',2049) = S_ready_found',
                   'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(ready, 'S_ready'),
                   'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer', 'pcallcontext_ready = pcallcontext_caller',
                   '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)', '$heap_owners($heap_graph(S_ready),HOBJECT n_this) = 2',
                   '$target_receiver(S_ready,' + ('CLOSURE_TARGET n_wrapper' if fcc else 'ARRAY_METHOD_TARGET pcalltarget parrayselection') + ') = eps',
                   'S_body_found = $peerthis243_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
                   'S_body = S_body_found[.COMPLETION = NORMAL]', at(body, 'S_body'),
                   'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'), 'pcallcontext_body.RECEIVER = eps',
                   'pcallcontext_body.CALLED_CLASS = (porigin_class)',
                   '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1', '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 1',
                   '$lookup($global_table_view(S_body).ENV,$ptascii("runner")) = (n_runner)', 'S_body.STORE[n_runner] = DEFINED PNULL',
                   '$lookup($global_table_view(S_body).ENV,$ptascii("late")) = (n_late)', 'S_body.STORE[n_late] = DEFINED (PINT 99)',
                   '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED pvalue_old',
                   'pvalue_old = PSTRING_CARRIER (REQUEST_STRING n_old) ($ptascii("REQUEST-OLD"))',
                   'S_after_found = $peerthis243_after_seek(S_body,2048)', 'S_after_found.COMPLETION = BUDGET',
                   'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
                   '~((HOBJECT n_this) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
                   '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)', 'S_after.STORE[n_kept] = DEFINED pvalue_old',
                   '$lookup(S_after.ENV,$ptascii("late")) = (n_late_after)',
                   'S_after.STORE[n_late_after] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_end) ($ptascii("REQUEST-END")))',
                   proof.format(state='S_after') + ' = ((n_this,porigin_class,pmethoddesc))',
                   '$magic_method_context_values(S_after,(pcallcontext_caller),pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old],eps) = ([PBOOL false,pvalue_old])',
                   '$magic_method_context_values(S_after,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old],eps) = eps',
                   '$heap_valid($heap_graph(S_after))']
        if fcc:
            checks.append('~((HOBJECT n_wrapper) <- S_after.ALLOCATIONS)')
        else:
            checks += ['parrayselection.SITE = porigin_producer', 'parrayselection.INIT = z_outer', 'parrayselection.REQUESTED = porigin_class']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=DEFAULTS)
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or DEFAULTS)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
