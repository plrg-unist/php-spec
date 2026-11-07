#!/usr/bin/env python3
"""Fixed-name callback arrays retain physical scope and real call authority."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_fresh_array_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
DEFAULTS = [
    'magic-fixed-new-array-direct-peer-self-static-early-selector',
    'magic-fixed-new-array-fcc-peer-parent-instance-return-this',
    'magic-fixed-new-array-direct-peer-static-private-shadow-bound-control',
    'magic-fixed-new-array-fcc-peer-static-private-shadow-bound-control',
]
SHADOW = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_shadow_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_caller)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
HELPERS = r'''
dec $fresharray242_outer_one(ptask) : pmagicmethodcall?
def $fresharray242_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $fresharray242_outer_one(ptask) = eps -- otherwise
dec $fresharray242_outer(ptask*) : pmagicmethodcall?
def $fresharray242_outer(eps) = eps
def $fresharray242_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $fresharray242_outer_one(ptask) = (pmagicmethodcall)
def $fresharray242_outer(ptask :: ptask_tail*) = $fresharray242_outer(ptask_tail*) -- if $fresharray242_outer_one(ptask) = eps
dec $fresharray242_init_at(pcodeexpr, pcpath) : bool
def $fresharray242_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $fresharray242_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $fresharray242_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $fresharray242_without_init(eps, pcpath) = eps
def $fresharray242_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $fresharray242_without_init(pcodeexpr_tail*, pcpath) -- if $fresharray242_init_at(pcodeexpr, pcpath)
def $fresharray242_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $fresharray242_without_init(pcodeexpr_tail*, pcpath) -- if ~$fresharray242_init_at(pcodeexpr, pcpath)
'''


def seeker(label, front):
    return names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$fresharray242_' + label + '_')


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = '-fcc-' in case['id']
    shadow = ROWS[case['id']].get('model_status') == 'unsupported'
    static = case['id'].endswith('self-static-early-selector')
    select = (('FIRSTCLASS_CONVERT porigin_selection z_init z_convert' if fcc else 'CALL_DYNAMIC porigin_selection z_init z_call'))
    front = ('S.TODO = (' + select + ') :: ptask_select_tail* -- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = (pcallcontext_caller)')
    ready = ('S.TODO = (CALL_ARGS ' + ('(CLOSURE_TARGET n_wrapper)' if fcc else '(ARRAY_METHOD_TARGET pcalltarget parrayselection)') +
             ' phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* -- if S.CURRENT = (pcallcontext_ready)')
    producer = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* -- if S.CURRENT = (pcallcontext_producer) -- if pcallcontext_producer.TARGET = ' +
                ('CLOSURE_TARGET n_wrapper' if fcc else 'ARRAY_METHOD_TARGET pcalltarget parrayselection'))
    convert = 'S.TODO = (ARRAY_CONVERT pcalltarget parrayselection) :: ptask_convert_tail*'
    prefix = names.PREFIX.replace(names.FRONT, SHADOW if shadow else front) + HELPERS
    for label, stop in [('ready', ready), ('producer', producer), ('after', AFTER), ('convert', convert)]:
        prefix += seeker(label, stop)
    checks = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
              r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
              'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', SHADOW if shadow else front]
    if shadow:
        checks += ['S.ORIGIN = (porigin_outer)', '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)']
    else:
        checks += ['$fresharray242_outer(ptask_select_tail*) = (pmagicmethodcall)',
                   'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
                   '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)']
    checks += ['porigin_producer = PORIGIN n_unit pcpath_producer',
               '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
               'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer']
    if fcc:
        checks += ['expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture']
    site = 'pcpath_producer ++ [PCFIELD 0]' if fcc else 'pcpath_producer'
    checks += ['porigin_site = PORIGIN n_unit (' + site + ')',
               'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
               'expression_new = NExprNew (NName (BYTES text_new) metadata_name_new) (SEQUENCE phpType7_ctor*) metadata_new',
               '~$ppscoped_keyword(NName (BYTES text_new) metadata_name_new)',
               'pcpath_new = (' + site + ') ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
               'porigin_new = PORIGIN n_unit pcpath_new', '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
               '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
               '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = eps', '~$ordinary_keyword_new_site(S,porigin_new)',
               '$code_name(pcode.NAMES,pcpath_new) = ((preqbytes_new,eps))',
               '$class_named(S.CLASSNAMES,$ptlc(preqbytes_new)) = (porigin_allocated)',
               '$magic_method_fresh_receiver(S,porigin_new,expression_new) = (porigin_allocated)',
               '$class_named(S.CLASSNAMES,$ptascii("peerscope242")) = (porigin_scope)',
               '$class_named(S.CLASSNAMES,$ptascii("peerchild242")) = (porigin_called)',
               '$closure_source_class(S,porigin_site) = (porigin_scope)',
               'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
               '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)']
    if fcc:
        checks += ['$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_capture)',
                   '$magic_method_firstclass_site(S,porigin_producer,expression_producer)']
    selected = ('$magic_method_firstclass_producer(S,porigin_producer,expression_producer)' if fcc else
                '$magic_method_instance_producer(S,porigin_producer,expression_producer)')
    if shadow:
        checks += ['$scope_method(S,porigin_allocated,$ptascii("capture"),true,(porigin_scope)) = (pmethoddesc_private)',
                   'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
                   '$effective_method(S,porigin_allocated,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_public)',
                   'pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC',
                   '$magic_method_plain_instance_source(S,pmethoddesc_public,phpType7_real*)',
                   '~$magic_method_plain_instance_source(S,pmethoddesc_private,phpType7_real*)',
                   selected + ' = eps', '$magic_method_fresh_array_source(S,porigin_site,expression_callback,phpType7_real*) = eps',
                   '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
                   'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
                   '$factory182_output(S_done.EVENTS) = eps']
    else:
        checks += ['porigin_selection = porigin_site', '|phpType7_real*| = 2', '|phpType7_ctor*| = 1',
                   'porigin_allocated =/= porigin_called',
                   '$method_class_selected(S,porigin_allocated,$ptascii("capture"),(porigin_scope)) = (pmethoddesc)',
                   selected + ' = ' + ('(pmethoddesc.FUNCTION)' if fcc else '((porigin_allocated,pmethoddesc))'),
                   '$magic_method_fresh_array_source(S,porigin_site,expression_callback,phpType7_real*) = ((porigin_allocated,pmethoddesc))',
                   '$magic_method_argument_source(S,porigin_producer,1,expression_producer)',
                   '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
                   '~$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,2)',
                   '$magic_method_fresh_array_source(S[.SOURCES = eps],porigin_site,expression_callback,phpType7_real*) = eps',
                   '$magic_method_fresh_array_source(S[.CODE = [pcode[.NAMES = eps]]],porigin_site,expression_callback,phpType7_real*) = eps',
                   '$magic_method_fresh_array_source(S,porigin_site,expression_callback,eps) = eps']
        for path in ['pcpath_producer'] + (['pcpath_producer ++ [PCFIELD 0]'] if fcc else []):
            state = 'S[.CODE = [pcode[.EXPRESSIONS = $fresharray242_without_init(pcode.EXPRESSIONS,' + path + ')]]]'
            checks.append(selected.replace('(S,', '(' + state + ',') + ' = eps')
            checks.append('~$magic_method_copy_source(' + state + ',pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)')
        checks += ['S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
                   'pcalltarget = ' + ('STATIC_METHOD_TARGET porigin_allocated pmethoddesc.FUNCTION.ORIGIN' if static else 'METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN'),
                   '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED pcalltarget porigin_allocated ($ptascii("capture"))',
                   '$heap_owners($heap_graph(S),HARRAY n_callback) = 1', '$heap_owners($heap_graph(S),HOBJECT n_selector) = 1',
                   'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
                   'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET']
        if fcc:
            checks += ['S_convert_found = $fresharray242_convert_seek(S_selected,2048)', 'S_convert_found.COMPLETION = BUDGET',
                       'S_convert = S_convert_found[.COMPLETION = NORMAL]', at(convert, 'S_convert'),
                       'parrayselection.SITE = porigin_site', 'parrayselection.REQUESTED = porigin_allocated',
                       'parrayselection.INIT = z_capture', 'parrayselection.LINE = z_convert',
                       '$array_convert_valid(S_convert,pcalltarget,parrayselection)',
                       'n_wrapper = |S_convert.OBJECTS|', 'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
                       'S_wrapped.OBJECTS[n_wrapper] = ARRAYMETHODCLOSURE pcalltarget parrayselection pmethodcapture?',
                       '$node_children(S_wrapped,HOBJECT n_wrapper) = ' + ('eps' if static else '[HOBJECT n_selector]')]
        start = 'S_wrapped' if fcc else 'S_selected'
        checks += ['S_ready_found = $fresharray242_ready_seek(' + start + ',2048)', 'S_ready_found.COMPLETION = BUDGET',
                   '$fresharray242_ready_seek(' + ('S_convert' if fcc else 'S') + ',2049) = S_ready_found',
                   'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(ready, 'S_ready'),
                   'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer', 'pcallcontext_ready = pcallcontext_caller',
                   '$call_selected_valid(S_ready,' + ('CLOSURE_TARGET n_wrapper' if fcc else 'ARRAY_METHOD_TARGET pcalltarget parrayselection') + ',(porigin_producer))',
                   '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
                   '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = ' + ('0' if static else '1'),
                   'S_producer_found = $fresharray242_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
                   'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(producer, 'S_producer'),
                   'pcallcontext_producer.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
                   'pcallcontext_producer.RECEIVER = ' + ('eps' if static else '(n_selector)'),
                   'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)',
                   '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
                   'S_producer.STORE[n_saved] = DEFINED pvalue_request',
                   'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("' + ('REQUEST-SELECTED' if static else 'REQUEST-OLD') + '"))',
                   '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)', 'S_producer.STORE[n_late] = DEFINED (PINT 99)',
                   'S_after_found = $fresharray242_after_seek(S_producer,2048)', 'S_after_found.COMPLETION = BUDGET',
                   'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
                   'pcallcontext_caller.RECEIVER = (n_caller)', '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
                   '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)',
                   'pvalue_kept = ' + ('pvalue_request' if static else 'POBJECT n_selector'), 'S_after.STORE[n_kept] = DEFINED pvalue_kept',
                   '$magic_method_copy_values(S_after,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (PBOOL false),KNOWN pvalue_kept]) = ([PBOOL false,pvalue_kept])',
                   '$heap_owners($heap_graph(S_after),HOBJECT n_selector) = ' + ('0' if static else '1'), '$heap_valid($heap_graph(S_after))']
        if fcc:
            checks.append('~((HOBJECT n_wrapper) <- S_after.ALLOCATIONS)')
        else:
            checks += ['parrayselection.SITE = porigin_producer', 'parrayselection.INIT = z_outer',
                       'parrayselection.REQUESTED = porigin_allocated', 'parrayselection.NAME = $ptascii("capture")']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=list(ROWS))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or DEFAULTS)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
