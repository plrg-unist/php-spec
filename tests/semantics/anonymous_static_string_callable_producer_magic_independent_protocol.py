#!/usr/bin/env python3
"""SL checks for literal method-string selection, snapshots and static roots."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_string_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
DEFAULTS = [name for name in ROWS if 'inherited-old' in name or '-direct-peer-' in name]
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_boundary_tail* '
            '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_caller)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
HELPERS = r'''
dec $peerstring245_outer_one(ptask) : pmagicmethodcall?
def $peerstring245_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $peerstring245_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $peerstring245_outer_one(ptask) = eps -- otherwise
dec $peerstring245_outer(ptask*) : pmagicmethodcall?
def $peerstring245_outer(eps) = eps
def $peerstring245_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $peerstring245_outer_one(ptask) = (pmagicmethodcall)
def $peerstring245_outer(ptask :: ptask_tail*) = $peerstring245_outer(ptask_tail*) -- if $peerstring245_outer_one(ptask) = eps
dec $peerstring245_init_at(pcodeexpr, pcpath) : bool
def $peerstring245_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $peerstring245_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $peerstring245_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $peerstring245_without_init(eps, pcpath) = eps
def $peerstring245_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $peerstring245_without_init(pcodeexpr_tail*, pcpath) -- if $peerstring245_init_at(pcodeexpr, pcpath)
def $peerstring245_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $peerstring245_without_init(pcodeexpr_tail*, pcpath) -- if ~$peerstring245_init_at(pcodeexpr, pcpath)
'''
PREFIX = names.PREFIX.replace(
    'def $factory182_seek(S, n) = $factory182_seek(',
    'def $factory182_seek(S, n) = S -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO = eps\n'
    'def $factory182_seek(S, n) = $factory182_seek(').replace(
    '  -- if $(n > 0) /\\ ~$factory182_front(S)\n',
    '  -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO =/= eps\n')


def seeker(label, front):
    return PREFIX[PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$peerstring245_' + label + '_')


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = '-fcc-' in case['id']
    private = 'private-scope' in case['id']
    inherited = 'inherited-old' in case['id']
    index = 1 if inherited else 0
    front = ('S.TODO = (FIRSTCLASS_CONVERT porigin_selection z_init z_call) :: ptask_selection_tail* ' if fcc else
             'S.TODO = (EVAL (NExprFuncCall (NScalarString (BYTES text_selected) metadata_selected) (SEQUENCE phpType7_selected*) metadata_selection)) :: ptask_selection_tail* ')
    front += '-- if S.CURRENT = (pcallcontext_caller)'
    ready = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
             '-- if S.CURRENT = (pcallcontext_ready)')
    body = ('S.TODO = (RETURN_VALUE z_return) :: ptask_body_tail* -- if S.RESULT = VARIABLE ($ptascii("saved")) z_saved '
            '-- if S.CURRENT = (pcallcontext_body)')
    convert = 'S.TODO = (STRING_CONVERT pcalltarget_capture pstringselection_capture) :: ptask_convert_tail*'
    prefix = PREFIX.replace(names.FRONT, BOUNDARY if private else front) + HELPERS
    for label, stop in [('ready', ready), ('body', body), ('after', AFTER), ('convert', convert)]:
        prefix += seeker(label, stop)
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', BOUNDARY if private else front]
    if private:
        checks += ['S.ORIGIN = (porigin_outer)', '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)']
    else:
        checks += ['$peerstring245_outer(ptask_selection_tail*) = (pmagicmethodcall)',
                   'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
                   '$call_argument_origin(S,(pmagicmethodcall.SITE),' + str(index) + ') = (porigin_producer)']
    checks += ['porigin_producer = PORIGIN n_unit pcpath_producer',
               '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
               'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture']
    selection_path = 'pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'
    checks += ['pcpath_selection = ' + selection_path, 'porigin_selection = PORIGIN n_unit pcpath_selection',
               'porigin_callback = PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])',
               'expression_callback = NScalarString (BYTES text_callback) metadata_callback',
               '$origin_node(S.SOURCES,porigin_callback) = (expression_callback)',
               '$ppcall_literal(expression_callback) = ($base64(text_callback))',
               '$compiled_read(S,porigin_callback) = eps', '$compiled_effects(S,porigin_callback) = eps',
               '$value_nodes(PSTRING ($base64(text_callback))) = eps',
               '$class_named(S.CLASSNAMES,$ptascii("peerscope245")) = (porigin_scope)',
               '$class_named(S.CLASSNAMES,$ptascii("peerchild245")) = (porigin_child)',
               'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_child)',
               'pcallcontext_caller.RECEIVER = (n_this)', '$object_class_origin(S,n_this) = (porigin_child)']
    proof = ('$magic_method_firstclass_producer({state},porigin_producer,expression_producer)' if fcc else
             '$magic_method_static_producer({state},porigin_producer,expression_producer)')
    helper = '$magic_method_static_string_source({state},porigin_selection,expression_callback,phpType7_real*)'
    if private:
        checks += ['$effective_method(S,porigin_scope,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc)',
                   'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
                   helper.format(state='S') + ' = eps', proof.format(state='S') + ' = eps',
                   '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
                   'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
                   '$factory182_output(S_done.EVENTS) = eps']
    else:
        value = '(pmethoddesc.FUNCTION)' if fcc else '((porigin_requested,pmethoddesc))'
        checks += [helper.format(state='S') + ' = ((porigin_requested,pmethoddesc))',
                   proof.format(state='S') + ' = ' + value,
                   'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', 'pmethoddesc.STATIC',
                   '$magic_method_argument_source(S,porigin_producer,' + str(index) + ',expression_producer)',
                   '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,' + str(index) + ')',
                   '~$magic_method_context_call(expression_producer)',
                   '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
                   '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
                   '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
                   '$code_name(pcode.NAMES,pcpath_selection) = (($ppcall_literal_name($base64(text_callback)),eps))',
                   helper.format(state='S[.CURRENT = eps][.POOLS = eps]') + ' = ((porigin_requested,pmethoddesc))',
                   helper.format(state='S[.SOURCES = eps]') + ' = eps',
                   helper.format(state='S[.CODE = eps]') + ' = eps',
                   '$magic_method_static_string_source(S,porigin_selection,expression_callback,eps) = eps',
                   '$magic_method_static_string_source(S,porigin_selection,expression_callback,[NVariadicPlaceholder metadata_producer]) = eps',
                   '$magic_method_static_string_source(S,porigin_callback,expression_callback,phpType7_real*) = eps',
                   helper.format(state='S[.CODE = [pcode[.NAMES = (CODENAME pcpath_selection ($ptascii("Wrong::capture")) eps) :: pcode.NAMES]]]') + ' = eps',
                   helper.format(state='S[.CODE = [pcode[.NAMES = (CODENAME pcpath_selection ($ppcall_literal_name($base64(text_callback))) ($ptascii("fallback"))) :: pcode.NAMES]]]') + ' = eps',
                   proof.format(state='S[.CODE = [pcode[.EXPRESSIONS = $peerstring245_without_init(pcode.EXPRESSIONS,pcpath_producer)]]]') + ' = eps',
                   '$heap_owners($heap_graph(S),HOBJECT n_this) = 2']
        if fcc:
            checks += ['$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
                       proof.format(state='S[.CODE = [pcode[.EXPRESSIONS = $peerstring245_without_init(pcode.EXPRESSIONS,pcpath_selection)]]]') + ' = eps']
        else:
            checks += ['$magic_method_static_call(expression_producer)', 'S.ORIGIN = (porigin_selection)']
        if not inherited:
            checks += ['porigin_requested = porigin_child', 'pmethoddesc.OWNER = porigin_child',
                       '$scope_method(S,porigin_child,$ptascii("capture"),true,(porigin_scope)) = (pmethoddesc_private)',
                       'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE', 'pmethoddesc_private.OWNER = porigin_scope']
        else:
            checks += ['porigin_requested = porigin_scope', '$class_named(S.CLASSNAMES,$ptascii("peerbase245")) = (porigin_base)',
                       'pmethoddesc.OWNER = porigin_base', '|phpType7_real*| = 2',
                       '$effective_method(S,porigin_child,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_wrong)',
                       'pmethoddesc_wrong.FUNCTION.ORIGIN =/= pmethoddesc.FUNCTION.ORIGIN',
                       'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
                       'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET']
            if not fcc:
                checks += ['$magic_method_static_producer(S,porigin_producer,NExprFuncCall expression_callback (SEQUENCE ([phpType7_real*[1],phpType7_real*[0]])) metadata_producer) = eps']
            if fcc:
                checks += ['S_convert_found = $peerstring245_convert_seek(S_selected,2048)', 'S_convert_found.COMPLETION = BUDGET',
                           'S_convert = S_convert_found[.COMPLETION = NORMAL]', at(convert, 'S_convert'),
                           'pcalltarget_capture = STATIC_METHOD_TARGET porigin_requested pmethoddesc.FUNCTION.ORIGIN',
                           'pstringselection_capture.ORIGINAL = $base64(text_callback)',
                           '$string_convert_valid(S_convert,pcalltarget_capture,pstringselection_capture)',
                           'n_wrapper = |S_convert.OBJECTS|', 'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
                           'S_wrapped.OBJECTS[n_wrapper] = STRINGMETHODCLOSURE pcalltarget_capture pstringselection_capture',
                           '$node_children(S_wrapped,HOBJECT n_wrapper) = eps']
            checks += ['S_ready_found = $peerstring245_ready_seek(S_selected,2048)', 'S_ready_found.COMPLETION = BUDGET',
                       '$peerstring245_ready_seek(S,2049) = S_ready_found',
                       'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(ready, 'S_ready'),
                       'pcallcontext_ready = pcallcontext_caller', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
                       '$target_receiver(S_ready,pcalltarget_ready) = eps',
                       '$target_lexical_class(S_ready,pcalltarget_ready) = (porigin_base)',
                       '$target_called_class(S_ready,pcalltarget_ready) = (porigin_requested)',
                       'S_body_found = $peerstring245_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
                       'S_body = S_body_found[.COMPLETION = NORMAL]', at(body, 'S_body'),
                       'pcallcontext_body.TARGET = pcalltarget_ready', 'pcallcontext_body.RECEIVER = eps',
                       'pcallcontext_body.LEXICAL_CLASS = (porigin_base)', 'pcallcontext_body.CALLED_CLASS = (porigin_requested)',
                       '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1',
                       '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 1',
                       '$lookup($global_table_view(S_body).ENV,$ptascii("runner")) = (n_runner)', 'S_body.STORE[n_runner] = DEFINED PNULL',
                       '$lookup($global_table_view(S_body).ENV,$ptascii("late")) = (n_late)', 'S_body.STORE[n_late] = DEFINED (PINT 99)',
                       '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED pvalue_old',
                       'pvalue_old = PSTRING_CARRIER (REQUEST_STRING n_old) ($ptascii("REQUEST-OLD"))',
                       '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
                       'S_after_found = $peerstring245_after_seek(S_body,2048)', 'S_after_found.COMPLETION = BUDGET',
                       'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
                       '~((HOBJECT n_this) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
                       '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)', 'S_after.STORE[n_kept] = DEFINED pvalue_old',
                       '$lookup(S_after.ENV,$ptascii("late")) = (n_late_after)',
                       'S_after.STORE[n_late_after] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_end) ($ptascii("REQUEST-END")))',
                       proof.format(state='S_after') + ' = ' + value,
                       '$magic_method_collected_values(S_after,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN pvalue_old]) = ([PBOOL false,pvalue_old])',
                       '$heap_valid($heap_graph(S_after))']
            if fcc:
                checks += ['pcalltarget_ready = CLOSURE_TARGET n_wrapper', '~((HOBJECT n_wrapper) <- S_after.ALLOCATIONS)']
            else:
                checks += ['pcalltarget_ready = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_requested pmethoddesc.FUNCTION.ORIGIN) pstringselection_ready',
                           'pstringselection_ready.ORIGINAL = $base64(text_callback)', '$target_nodes(pcalltarget_ready) = eps']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=DEFAULTS)
    args = parser.parse_args()
    chosen = args.case or DEFAULTS
    protocol.run({name: ROWS[name] for name in chosen},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
