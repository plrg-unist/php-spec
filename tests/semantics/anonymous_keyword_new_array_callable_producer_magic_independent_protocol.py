#!/usr/bin/env python3
"""Direct keyword callback arrays select a target without a Closure wrapper."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_array_callable_producer_magic_independent_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
SELECT = ('S.TODO = (CALL_DYNAMIC porigin_dynamic z_init z_call) :: ptask_select_tail* '
          '-- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (ARRAY_METHOD_TARGET pcalltarget_ready parrayselection_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_return) :: ptask_producer_tail* '
            '-- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = ARRAY_METHOD_TARGET pcalltarget_producer parrayselection_producer')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
SHADOW = ('S.TODO = (EVAL (NExprMethodCall expression_owner (NIdentifier (BYTES text_missing) metadata_missing) (SEQUENCE phpType7_outer*) metadata_outer)) :: ptask_shadow_tail* '
          '-- if $base64(text_missing) = $ptascii("MiSsInG") -- if S.CURRENT = (pcallcontext_shadow)')
PREFIX = names.PREFIX.replace(names.FRONT, SELECT)
for label, front in [('ready', READY), ('producer', PRODUCER), ('after', AFTER), ('shadow', SHADOW)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$rawarray240_' + label + '_')
PREFIX += r'''
dec $rawarray240_outer_one(ptask) : pmagicmethodcall?
def $rawarray240_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $rawarray240_outer_one(ptask) = eps -- otherwise
dec $rawarray240_outer(ptask*) : pmagicmethodcall?
def $rawarray240_outer(eps) = eps
def $rawarray240_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $rawarray240_outer_one(ptask) = (pmagicmethodcall)
def $rawarray240_outer(ptask :: ptask_tail*) = $rawarray240_outer(ptask_tail*) -- if $rawarray240_outer_one(ptask) = eps
dec $rawarray240_init_at(pcodeexpr, pcpath) : bool
def $rawarray240_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $rawarray240_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $rawarray240_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $rawarray240_without_init(eps, pcpath) = eps
def $rawarray240_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $rawarray240_without_init(pcodeexpr_tail*, pcpath) -- if $rawarray240_init_at(pcodeexpr, pcpath)
def $rawarray240_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $rawarray240_without_init(pcodeexpr_tail*, pcpath) -- if ~$rawarray240_init_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.').replace('(S,', '(' + state + ',')


def source_parts():
    return [
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_callback (SEQUENCE phpType7_real*) metadata_producer',
        'porigin_callback = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (porigin_new)',
        'porigin_new = PORIGIN n_unit pcpath_new',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 1,PCFIELD 1]) = (porigin_method)',
        '$magic_method_literal_value(S,porigin_method,expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$class_named(S.CLASSNAMES,$ptascii("peerscope240")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("peerchild240")) = (porigin_called)',
        '$closure_source_class(S,porigin_producer) = (porigin_scope)',
    ]


def shadow(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $rawarray240_shadow_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
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
        '$magic_method_keyword_new_array_call(expression_producer)',
        '~$magic_method_context_source(S,S.CURRENT,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_array_producer(S,S.CURRENT,porigin_producer,expression_producer) = eps',
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
        allocated = 'peerscope240' if static else 'peerbase240'
        expected = 'REQUEST-SELECTED' if static else 'REQUEST-OLD'
        target = ('STATIC_METHOD_TARGET porigin_allocated pmethoddesc.FUNCTION.ORIGIN' if static else
                  'METHOD_TARGET n_selector pmethoddesc.FUNCTION.ORIGIN')
        checks = [
            'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
            r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
            'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
            'S = S_found[.COMPLETION = NORMAL]', SELECT,
            '$rawarray240_outer(ptask_select_tail*) = (pmagicmethodcall)',
            'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
            '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_producer)',
        ] + source_parts() + [
            'porigin_dynamic = porigin_producer', '|phpType7_real*| = 2',
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
            '$magic_method_keyword_new_array_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
            '$magic_method_fresh_method_source(S,porigin_allocated,porigin_producer,$ptascii("capture"),phpType7_real*) = (pmethoddesc)',
            '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            '$magic_method_from_callable_parts(S,porigin_producer,expression_producer) = eps',
            '$magic_method_keyword_new_array_from_callable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
            'S.CODE = [pcode]', '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init)',
            '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = (z_new)',
            '~$magic_method_context_source(S,eps,porigin_producer,expression_producer)',
            '~$magic_method_context_source(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer)',
        ]
        for path in ['pcpath_producer', 'pcpath_new']:
            checks.append('~$magic_method_context_source(S[.CODE = [pcode[.EXPRESSIONS = $rawarray240_without_init(pcode.EXPRESSIONS,' + path + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer)')
        checks += [
            'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
            'n_caller =/= n_selector', '$object_class_origin(S,n_selector) = (porigin_allocated)',
            '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED pcalltarget porigin_allocated ($ptascii("capture"))',
            'pcalltarget = ' + target,
            '$heap_owners($heap_graph(S),HARRAY n_callback) = 1', '$heap_owners($heap_graph(S),HOBJECT n_selector) = 1',
            'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
            'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
            'S_selected.OBJECTS = S.OBJECTS', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_ready_found = $rawarray240_ready_seek(S_selected,2047)', 'S_ready_found.COMPLETION = BUDGET',
            'S_direct = $rawarray240_ready_seek(S,2048)', 'S_direct = S_ready_found',
            'S_ready = S_ready_found[.COMPLETION = NORMAL]', at(READY, 'S_ready'),
            'pcalltarget_ready = pcalltarget', 'pcallcontext_ready = pcallcontext_caller',
            'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
            'parrayselection_ready.SITE = porigin_producer', 'parrayselection_ready.REQUESTED = porigin_allocated',
            'parrayselection_ready.INIT = z_init', 'parrayselection_ready.NAME = $ptascii("capture")',
            '$call_selected_valid(S_ready,ARRAY_METHOD_TARGET pcalltarget_ready parrayselection_ready,(porigin_producer))',
            '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = ' + ('0' if static else '1'),
            '$target_nodes(ARRAY_METHOD_TARGET pcalltarget_ready parrayselection_ready) = ' + ('eps' if static else '[HOBJECT n_selector]'),
            'S_producer_found = $rawarray240_producer_seek(S_ready,2048)', 'S_producer_found.COMPLETION = BUDGET',
            'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
            'pcalltarget_producer = pcalltarget', 'parrayselection_producer = parrayselection_ready',
            'pcallcontext_producer.INSTANCE = eps',
            'pcallcontext_producer.RECEIVER = ' + ('eps' if static else '(n_selector)'),
            'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_producer.CALLED_CLASS = (porigin_allocated)',
            '$call_context_roots(S_producer.CURRENT) = ' + ('eps' if static else '[HOBJECT n_selector]'),
            '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
            'S_producer.STORE[n_saved] = DEFINED pvalue_request',
            'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("' + expected + '"))',
            '$lookup($global_table_view(S_producer).ENV,$ptascii("late")) = (n_late)', 'S_producer.STORE[n_late] = DEFINED (PINT 99)',
            '~$magic_method_context_source(S_producer,S_producer.CURRENT,porigin_producer,expression_producer)',
            '$magic_method_context_source(S_producer,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
            'S_after_found = $rawarray240_after_seek(S_producer,2048)', 'S_after_found.COMPLETION = BUDGET',
            'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'),
            '~((HOBJECT n_caller) <- S_after.ALLOCATIONS)',
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
