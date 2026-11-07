#!/usr/bin/env python3
"""Keyword callback arrays retain original scope and real receiver ownership."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_array_from_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
FACTORY = ('S.TODO = (API_CALLABLE_RESULT papiquery 0) :: ptask_factory_tail* '
           '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.CURRENT = (pcallcontext_producer) -- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
SHADOW = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_shadow_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_shadow)')
PREFIX = names.PREFIX.replace(names.FRONT, FACTORY)
for label, front in [('ready', READY), ('producer', PRODUCER), ('after', AFTER), ('shadow', SHADOW)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$kwarray239_' + label + '_')
PREFIX += r'''
dec $kwarray239_outer_one(ptask) : pmagicmethodcall?
def $kwarray239_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $kwarray239_outer_one(ptask) = eps -- otherwise
dec $kwarray239_outer(ptask*) : pmagicmethodcall?
def $kwarray239_outer(eps) = eps
def $kwarray239_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $kwarray239_outer_one(ptask) = (pmagicmethodcall)
def $kwarray239_outer(ptask :: ptask_tail*) = $kwarray239_outer(ptask_tail*) -- if $kwarray239_outer_one(ptask) = eps
dec $kwarray239_omit(pcodeexpr, pcpath, bool) : bool
def $kwarray239_omit(CODECALL_INIT pcpath z, pcpath, true) = true
def $kwarray239_omit(CODEEXPR pcpath z b_expr, pcpath, false) = true
def $kwarray239_omit(pcodeexpr, pcpath, b) = false -- otherwise
dec $kwarray239_cut(pcodeexpr*, pcpath, bool) : pcodeexpr*
def $kwarray239_cut(eps, pcpath, b) = eps
def $kwarray239_cut(pcodeexpr :: pcodeexpr_tail*, pcpath, b) = $kwarray239_cut(pcodeexpr_tail*, pcpath, b) -- if $kwarray239_omit(pcodeexpr, pcpath, b)
def $kwarray239_cut(pcodeexpr :: pcodeexpr_tail*, pcpath, b) = pcodeexpr :: $kwarray239_cut(pcodeexpr_tail*, pcpath, b) -- if ~$kwarray239_omit(pcodeexpr, pcpath, b)
'''


def at(front, state):
    return front.replace('S.', state + '.').replace('(S,', '(' + state + ',')


def source_parts():
    return [
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_method_from_callable_parts(S,porigin_producer,expression_producer) = ((porigin_callback,expression_callback,phpType7_real*))',
        'porigin_factory = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'porigin_callback = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 2,PCINDEX 0,PCFIELD 1])',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (porigin_new)',
        'porigin_new = PORIGIN n_unit pcpath_new',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 1,PCFIELD 1]) = (porigin_method)',
        '$magic_method_literal_value(S,porigin_method,expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope239")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild239")) = (porigin_called)',
        '$closure_source_class(S,porigin_factory) = (porigin_scope)',
    ]


def shadow(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $kwarray239_shadow_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHADOW, 'S.ORIGIN = (porigin_outer)',
        '$call_argument_origin(S,(porigin_outer),0) = (porigin_producer)',
    ] + source_parts() + [
        'pcallcontext_shadow.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_shadow.CALLED_CLASS = (porigin_called)',
        '$magic_method_keyword_new_class(S,S.CURRENT,porigin_new,expression_new) = (porigin_called)',
        '$magic_method_keyword_new_source(S,S.CURRENT,porigin_new,expression_new)',
        '$scope_method(S,porigin_called,$ptascii("capture"),true,(porigin_scope)) = (pmethoddesc_private)',
        'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
        '$effective_method(S,porigin_called,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_public)',
        'pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_private.FUNCTION.ORIGIN =/= pmethoddesc_public.FUNCTION.ORIGIN',
        '$magic_method_plain_instance_source(S,pmethoddesc_public,phpType7_real*)',
        '~$magic_method_plain_instance_source(S,pmethoddesc_private,phpType7_real*)',
        '$magic_method_context_call(expression_producer)',
        '~$magic_method_context_source(S,S.CURRENT,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_array_from_callable_producer(S,S.CURRENT,porigin_producer,expression_producer) = eps',
        'S_done = $drive_steps(S,128)',
        'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    row = ROWS[case['id']]
    if row.get('model_status') == 'unsupported':
        checks = shadow(fixture, filename)
    else:
        static = case['id'].endswith('self-static-early-selector')
        allocated = 'peerscope239' if static else 'peerbase239'
        expected = 'REQUEST-SELECTED' if static else 'REQUEST-OLD'
        checks = [
            'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
            r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
            'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
            'S = S_found[.COMPLETION = NORMAL]', FACTORY,
            '$kwarray239_outer(ptask_factory_tail*) = (pmagicmethodcall)',
            'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
            '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
        ] + source_parts() + [
            'pconfigcall.SITE = porigin_factory', '|phpType7_real*| = 2',
            'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new', '|phpType7_ctor*| = 1',
            '$class_named(S.CLASSNAMES,$ptascii("' + allocated + '")) = (porigin_allocated)',
            'porigin_allocated =/= porigin_called',
            'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
            'pcallcontext_caller.RECEIVER = (n_caller)',
            '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_new,expression_new) = (porigin_allocated)',
            '$magic_method_keyword_new_source(S,pmagicmethodcall.CALLER,porigin_new,expression_new)',
            '$scope_method(S,porigin_allocated,$ptascii("capture"),true,(porigin_scope)) = (pmethoddesc)',
            '$effective_method(S,porigin_called,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_wrong)',
            'pmethoddesc.FUNCTION.ORIGIN =/= pmethoddesc_wrong.FUNCTION.ORIGIN',
            '$magic_method_keyword_new_array_from_callable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
            '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            '$magic_method_from_callable_producer(S,porigin_producer,expression_producer) = eps',
            '$magic_method_keyword_new_invokable_from_callable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
            'S.CODE = [pcode]', '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
            '$code_expression(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = ((z_factory,false))',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = eps',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = (z_new)',
            '~$magic_method_context_source(S,eps,porigin_producer,expression_producer)',
            '~$magic_method_context_source(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer)',
        ]
        for path, init in [('pcpath_producer', 'true'), ('pcpath_new', 'true'), ('pcpath_producer ++ [PCFIELD 0]', 'false')]:
            checks.append('~$magic_method_context_source(S[.CODE = [pcode[.EXPRESSIONS = $kwarray239_cut(pcode.EXPRESSIONS,' + path + ',' + init + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)')
        checks += [
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]', 'papiquery.VALUE = PARRAY n_callback',
            'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
            'n_caller =/= n_selector',
            '$object_class_origin(S,n_selector) = (porigin_allocated)', 'papiquery.SCOPE = (porigin_scope)',
            '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)',
            '$heap_owners($heap_graph(S),HARRAY n_callback) = 1', '$heap_owners($heap_graph(S),HOBJECT n_selector) = 1',
            'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
            'n_wrapper = |S.OBJECTS|', 'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
            'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
            'pfrommethod.ARRAY', '~pfrommethod.INVOKE', 'pfrommethod.STATIC' if static else '~pfrommethod.STATIC',
            'pfrommethod.INPUT = POBJECT n_selector', 'pfrommethod.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
            'pfrommethod.CLASS.REQUESTED = porigin_allocated', 'pfrommethod.CLASS.CALLED = porigin_allocated',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = ' + ('eps' if static else '[HOBJECT n_selector]'),
            'S_ready_found = $kwarray239_ready_seek(S_wrapped,2047)', 'S_ready_found.COMPLETION = BUDGET',
            'S_direct = $kwarray239_ready_seek(S,2048)', 'S_direct = S_ready_found',
            'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(READY, 'S_ready'),
            'n_wrapper_ready = n_wrapper', 'pcallcontext_ready = pcallcontext_caller',
            'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
            '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = ' + ('0' if static else '1'),
            '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
            '$from_valid(S_ready,pfrommethod)', '$from_selected(S_ready,pfrommethod) = (pmethoddesc)',
            'S_producer_found = $kwarray239_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
            'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
            'n_wrapper_producer = n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)',
            'pcallcontext_producer.RECEIVER = ' + ('eps' if static else '(n_selector)'),
            'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)',
            '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
            '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
            'S_producer.STORE[n_saved] = DEFINED pvalue_request',
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("' + expected + '"))',
            '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)', 'S_producer.STORE[n_late] = DEFINED (PINT 99)',
            '~$magic_method_context_source(S_producer,S_producer.CURRENT,porigin_producer,expression_producer)',
            '$magic_method_context_source(S_producer,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            'S_after_found = $kwarray239_after_seek(S_producer,2048)', 'S_after_found.COMPLETION = BUDGET',
            'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
            '~((HOBJECT n_wrapper) <- S_after.ALLOCATIONS)', '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
            '$lookup(S_after.ENV,$ptascii("kept")) = (n_kept)',
            'S_after.STORE[n_kept] = DEFINED ' + ('pvalue_request' if static else '(POBJECT n_selector)'),
            '$heap_owners($heap_graph(S_after),HOBJECT n_selector) = ' + ('0' if static else '1'),
            '$magic_method_context_source(S_after,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            '~$magic_method_context_source(S_after,S_after.CURRENT,porigin_producer,expression_producer)',
            'S_done = $drive_steps(S_after,512)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
            '~((HOBJECT n_selector) <- S_done.ALLOCATIONS)', '$heap_valid($heap_graph(S_done))',
        ]
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=list(ROWS))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or ROWS)},
                 (Path(__file__), CATALOGUE, Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
