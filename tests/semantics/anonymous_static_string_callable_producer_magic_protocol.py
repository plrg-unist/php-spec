#!/usr/bin/env python3
"""Literal method names retain emitted call authority and real returned leaves."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_string_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_static_string_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-static-string-direct-return-old', 'magic-static-string-fcc-return-old')
UNPACK = 'magic-static-string-direct-unpack-refused'
READY = 'S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* -- if S.CURRENT = eps'
CONVERT = 'S.TODO = (STRING_CONVERT pcalltarget_capture pstringselection_capture) :: ptask_convert_tail* -- if S.CURRENT = eps'
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(
    'def $factory182_seek(S, n) = $factory182_seek(',
    'def $factory182_seek(S, n) = S -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO = eps\n'
    'def $factory182_seek(S, n) = $factory182_seek(').replace(
    '  -- if $(n > 0) /\\ ~$factory182_front(S)\n',
    '  -- if $(n > 0) /\\ ~$factory182_front(S) /\\ S.TODO =/= eps\n')


def at(front, state):
    return front.replace('S.', state + '.')


def seeker(label, front):
    return PREFIX[PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$staticstring245_' + label + '_')


def unpack(fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        BOUNDARY, 'S.ORIGIN = (porigin_site)', 'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_static_producer(S,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)', '$magic_method_static_call(expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps', '$lookup(S.ENV,$ptascii("pack")) = (n_pack)',
        'S.STORE[n_pack] = DEFINED (PARRAY n_pack_array)',
        'S.ARRAYS[n_pack_array] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]
    return PREFIX.replace(names.FRONT, BOUNDARY), checks


def ownership(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    front = ('S.TODO = (EVAL (NExprFuncCall (NScalarString (BYTES text_literal) metadata_literal) (SEQUENCE phpType7_site*) metadata_site)) :: ptask_selection_tail* '
             '-- if S.CURRENT = eps -- if $ppfirstclass(phpType7_site*) = ' + ('true' if fcc else 'false'))
    prefix = PREFIX.replace(names.FRONT, front) + direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
    for label, stop in [('ready', READY), ('convert', CONVERT), ('body', BODY), ('send', SEND)]:
        prefix += seeker(label, stop)
    producer = ('$magic_method_firstclass_producer({state},porigin_producer,expression_producer) = (pmethoddesc.FUNCTION)' if fcc else
                '$magic_method_static_producer({state},porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))')
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', front,
        '$newinvoke236_outer(ptask_selection_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = eps', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer', '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall ' + ('expression_capture' if fcc else 'expression_callback') + ' (SEQUENCE phpType7_real*) metadata_producer',
        'phpType7_real* = [phpType7_first,phpType7_second]', 'phpType7_first =/= phpType7_second',
    ]
    if fcc:
        checks += [
            'expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
            'porigin_selection = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])', '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
            '$magic_method_firstclass_call(expression_producer)',
        ]
    else:
        checks += ['porigin_selection = porigin_producer', '$magic_method_static_call(expression_producer)', '~$magic_method_firstclass_call(expression_producer)']
    checks += [
        'expression_callback = NScalarString (BYTES text_literal) metadata_literal', 'porigin_selection = PORIGIN n_unit pcpath_selection',
        '$origin_node(S.SOURCES,porigin_selection) = (NExprFuncCall expression_callback (SEQUENCE phpType7_site*) metadata_site)',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])) = (expression_callback)',
        '$compiled_read(S,PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])) = eps',
        'ptbytes_original = $base64(text_literal)', '$method_string_parts(ptbytes_original) = ((ptbytes_class,ptbytes_method))',
        'ptbytes_original = 92 :: ptbytes_normalized', '$ppcall_literal_name(ptbytes_original) = ptbytes_normalized',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]', '$code_name(pcode.NAMES,pcpath_selection) = ((ptbytes_normalized,eps))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_selection) = ((z_call,b_call))',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase245")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild245")) = (porigin_class)',
        '$magic_method_static_string_source(S,porigin_selection,expression_callback,phpType7_real*) = ((porigin_class,pmethoddesc))',
        producer.format(state='S'), 'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base', 'pmethoddesc.STATIC',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '~$magic_method_context_call(expression_producer)', '~$magic_method_context_arguments(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_static_string_source(S[.SOURCES = eps],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_static_string_source(S[.CODE = [pcode[.NAMES = eps]]],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_static_string_source(S,porigin_selection,expression_callback,eps) = eps',
        '$magic_method_static_string_source(S,porigin_selection,expression_callback,[NVariadicPlaceholder metadata_literal]) = eps',
        '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        ('$magic_method_firstclass_producer(S,porigin_producer,NExprFuncCall expression_capture (SEQUENCE ([phpType7_second,phpType7_first])) metadata_producer) = eps' if fcc else
         '$magic_method_static_producer(S,porigin_producer,NExprFuncCall expression_callback (SEQUENCE ([phpType7_second,phpType7_first])) metadata_producer) = eps'),
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if fcc:
        checks += [
            'S_selected.TODO = (FIRSTCLASS_CONVERT porigin_selection z_init z_capture) :: ptask_selection_tail*',
            '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
            'S_convert_found = $staticstring245_convert_seek(S_selected,2048)', 'S_convert_found.COMPLETION = BUDGET',
            'S_convert = S_convert_found[.COMPLETION = NORMAL]', at(CONVERT, 'S_convert'),
            'pcalltarget_capture = STATIC_METHOD_TARGET porigin_class porigin_method', 'pstringselection_capture.SITE = porigin_selection',
            'pstringselection_capture.REQUESTED = porigin_class', 'pstringselection_capture.INIT = z_init', 'pstringselection_capture.ORIGINAL = ptbytes_original',
            'n_wrapper = |S_convert.OBJECTS|', 'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS = S_convert.OBJECTS ++ [STRINGMETHODCLOSURE pcalltarget_capture pstringselection_capture]',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
            'S_ready = $staticstring245_ready_seek(S_wrapped,2048)', 'pcalltarget = CLOSURE_TARGET n_wrapper',
        ]
    else:
        checks += [
            'S_ready = $staticstring245_ready_seek(S_selected,2048)',
            'pcalltarget = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) {SITE porigin_selection, INIT z_init, LINE z_call, REQUESTED porigin_class, ORIGINAL ptbytes_original}',
        ]
    checks += [
        'S_ready.COMPLETION = BUDGET', at(READY, 'S_ready'), 'pcalltarget_ready = pcalltarget', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        '$staticstring245_ready_seek(S,2048) = S_ready', '$target_nodes(pcalltarget) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$target_receiver(S_ready,pcalltarget) = eps', '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)', '$target_called_class(S_ready,pcalltarget) = (porigin_class)',
        'S_body_found = $staticstring245_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET', 'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)', 'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        producer.format(state='S_body'),
        'S_send_found = $staticstring245_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET', 'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_old', 'pmagicmethodcall_send = pmagicmethodcall', 'porigin_send = pmagicmethodcall.SITE', 'z_send = pmagicmethodcall.LINE',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$magic_method_copy_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;CAPTURE;PacketBase245/PacketChild245;")',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
        '$heap_count(HOBJECT n_old,$tasks_nodes(S_sent.TODO)) = 1', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
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
