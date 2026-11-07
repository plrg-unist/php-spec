#!/usr/bin/env python3
"""Literal This arrays preserve caller ownership and actual call authority."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_array_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_this_array_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-this-array-direct-return-this', 'magic-this-array-fcc-return-this')
UNPACK = 'magic-this-array-direct-unpack-refused'
READY = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_caller)')
CONVERT = 'S.TODO = (ARRAY_CONVERT pcalltarget_capture parrayselection_capture) :: ptask_convert_tail*'
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_caller)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = (pcallcontext_boundary)')
HELPERS = r'''
dec $thisarray243_expression_at(pcodeexpr, pcpath) : bool
def $thisarray243_expression_at(CODEEXPR pcpath z b, pcpath) = true
def $thisarray243_expression_at(pcodeexpr, pcpath) = false -- otherwise
dec $thisarray243_without_expression(pcodeexpr*, pcpath) : pcodeexpr*
def $thisarray243_without_expression(eps, pcpath) = eps
def $thisarray243_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = $thisarray243_without_expression(pcodeexpr_tail*, pcpath) -- if $thisarray243_expression_at(pcodeexpr, pcpath)
def $thisarray243_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $thisarray243_without_expression(pcodeexpr_tail*, pcpath) -- if ~$thisarray243_expression_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.')


def seeker(label, front):
    return names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisarray243_' + label + '_')


def unpack(fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_this_producer(S,S.CURRENT,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_this_call(expression_producer)', '$magic_method_instance_call(expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$ptascii("pack")) = (n_pack_cell)', 'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]
    return names.PREFIX.replace(names.FRONT, BOUNDARY), checks


def ownership(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    front = ('S.TODO = (' + ('FIRSTCLASS_CONVERT' if fcc else 'CALL_DYNAMIC') +
             ' porigin_selection z_init z_call) :: ptask_selection_tail* '
             '-- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = (pcallcontext_caller)')
    prefix = names.PREFIX.replace(names.FRONT, front) + HELPERS
    prefix += direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
    for label, stop in [('ready', READY), ('convert', CONVERT), ('body', BODY), ('send', SEND), ('after', AFTER)]:
        prefix += seeker(label, stop)
    proof = '$magic_method_this_producer({state},pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))'
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', front,
        '$newinvoke236_outer(ptask_selection_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        'pcallcontext_caller.RECEIVER = (n_this)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer', '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer',
        '|phpType7_real*| = 2',
    ]
    if fcc:
        checks += [
            'expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
            'porigin_selection = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
            '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
            '$magic_method_firstclass_call(expression_producer)',
            '$magic_method_this_array_callable_source(S,pmagicmethodcall.CALLER,porigin_selection,expression_callback,[NVariadicPlaceholder metadata_placeholder]) = eps',
        ]
    else:
        checks += ['porigin_selection = porigin_producer', '~$magic_method_firstclass_call(expression_producer)', '$magic_method_instance_call(expression_producer)']
    checks += [
        'porigin_selection = PORIGIN n_unit pcpath_selection',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_this (BOOLEAN false) (BOOLEAN false) metadata_this_item),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method_item)])) metadata_array',
        'expression_this = NExprVariable (BYTES text_this) metadata_this', '$direct_this(BYTES text_this)',
        'pcpath_this = pcpath_selection ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
        '$source_emission_this_fetch(S,n_unit,pcpath_this,expression_this)',
        '$magic_method_literal_value(S,PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1]),expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))', '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase243")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope243")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild243")) = (porigin_class)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        '$closure_source_class(S,porigin_selection) = (porigin_scope)',
        '$goto_source_owner($all_functions(S),n_unit,pcpath_selection) = (pfunction_caller)', 'pcallcontext_caller.FUNCTION = pfunction_caller.ORIGIN',
        '$magic_method_this_array_callable_source(S,pmagicmethodcall.CALLER,porigin_selection,expression_callback,phpType7_real*) = ((n_this,porigin_class,pmethoddesc))',
        proof.format(state='S'), 'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        '$magic_method_this_call(expression_producer)', '$magic_method_context_call(expression_producer)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_this_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.RECEIVER = eps]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.LEXICAL_CLASS = (porigin_base)]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.CALLED_CLASS = (porigin_scope)]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S[.CODE = [pcode[.EXPRESSIONS = $thisarray243_without_expression(pcode.EXPRESSIONS,pcpath_this)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_this_array_callable_source(S,pmagicmethodcall.CALLER,porigin_selection,expression_callback,eps) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("runner")) = (n_runner_cell)', 'S.STORE[n_runner_cell] = DEFINED PNULL',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_this)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$heap_owners($heap_graph(S),HOBJECT n_this) = 2', '$call_context_roots(S.CURRENT) = [HOBJECT n_this]',
        '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED (METHOD_TARGET n_this porigin_method) porigin_class ($ptascii("capture"))',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.OBJECTS = S.OBJECTS', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if fcc:
        checks += [
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
            '$magic_method_this_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
            'S_convert = $thisarray243_convert_seek(S_selected,2048)', 'S_convert.COMPLETION = BUDGET', at(CONVERT, 'S_convert'),
            'pcalltarget_capture = METHOD_TARGET n_this porigin_method', 'parrayselection_capture.SITE = porigin_selection',
            'parrayselection_capture.REQUESTED = porigin_class', 'parrayselection_capture.INIT = z_init',
            '$array_convert_valid(S_convert,pcalltarget_capture,parrayselection_capture)', '~((HARRAY n_callback) <- S_convert.ALLOCATIONS)',
            'n_wrapper = |S.OBJECTS|', 'S_wrapped = $drive_steps(S_convert[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
            'pmethodcapture? = $method_capture_current(S_convert,porigin_selection)',
            'S_wrapped.OBJECTS = S.OBJECTS ++ [ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?]',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
            'S_ready = $thisarray243_ready_seek(S_wrapped,2048)', 'pcalltarget = CLOSURE_TARGET n_wrapper',
        ]
    else:
        checks += [
            'S_ready = $thisarray243_ready_seek(S_selected,2048)',
            'pcalltarget = ARRAY_METHOD_TARGET (METHOD_TARGET n_this porigin_method) {SITE porigin_selection, INIT z_init, LINE z_call, REQUESTED porigin_class, NAME $ptascii("capture")}',
        ]
    checks += [
        'S_ready.COMPLETION = BUDGET', at(READY, 'S_ready'), 'pcalltarget_ready = pcalltarget',
        'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer', '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_this) = 2',
        'S_direct = $thisarray243_ready_seek(S,2048)', 'S_direct = S_ready',
        '$target_receiver(S_ready,pcalltarget) = (n_this)', '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)',
        '$target_called_class(S_ready,pcalltarget) = (porigin_class)',
        'S_body_found = $thisarray243_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.RECEIVER = (n_this)',
        'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else '[HOBJECT n_this]'),
        '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1', '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 2',
        proof.format(state='S_body'), '$magic_method_this_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        'S_send_found = $thisarray243_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'), 'n_send = n_this',
        'pmagicmethodcall_send = pmagicmethodcall', 'porigin_send = pmagicmethodcall.SITE', 'z_send = pmagicmethodcall.LINE',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 2',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this)],eps) = ([POBJECT n_this])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_this)],eps) = eps',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_this)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_this) = 2', '$heap_count(HOBJECT n_this,$tasks_nodes(S_sent.TODO)) = 1',
        '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        'S_after_found = $thisarray243_after_seek(S_sent[.COMPLETION = NORMAL],2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', at(AFTER, 'S_after'), 'S_after.FRAMES = eps',
        '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 1', '(HOBJECT n_this) <- S_after.ALLOCATIONS',
        proof.format(state='S_after'), '$magic_method_this_producer(S_after,S_after.CURRENT,porigin_producer,expression_producer) = eps',
        '$factory182_output(S_after.EVENTS) = $ptascii("SHIFT;CAPTURE;PacketBase243/PacketChild243;HANDLER;OWNER;")',
    ]
    if fcc:
        checks += ['~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)']
    return prefix, checks


def render(case, fixture, filename):
    prefix, checks = unpack(fixture, filename) if case['id'] == UNPACK else ownership(case, fixture, filename)
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=(*CASES, UNPACK))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or (*CASES, UNPACK))},
                 (Path(__file__), CATALOGUE, CONTROLS, Path(direct.__file__), Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
