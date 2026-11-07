#!/usr/bin/env python3
"""Literal function targets keep original sends through frame and FCC retirement."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import anonymous_static_string_callable_producer_magic_protocol as method
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_function_string_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_function_string_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-function-string-direct-return-old', 'magic-function-string-fcc-return-old')
UNPACK = 'magic-function-string-nullary-unpack-refused'
READY, BODY, SEND = method.READY, method.BODY, method.SEND
BOUNDARY = method.BOUNDARY
PREFIX = method.PREFIX


def at(front, state):
    return front.replace('S.', state + '.')


def seeker(label, front):
    return PREFIX[PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$functionstring246_' + label + '_')


def unpack(fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'expression_producer = NExprFuncCall expression_callback (SEQUENCE eps) metadata_producer_call',
        'expression_callback = NScalarString phpType33 metadata_literal',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_required_producer(S,porigin_producer,expression_producer) = (pfunction)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)', '$magic_method_argument_call(expression_producer)',
        '~$magic_method_argument_call(NExprFuncCall (NName (BYTES "cGF5bG9hZDI0Ng==") metadata_literal) (SEQUENCE eps) metadata_producer_call)',
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
    for label, stop in [('ready', READY), ('body', BODY), ('send', SEND)]:
        prefix += seeker(label, stop)
    producer = ('$magic_method_firstclass_producer({state},porigin_producer,expression_producer) = (pfunction)' if fcc else
                '$magic_method_required_producer({state},porigin_producer,expression_producer) = (pfunction)')
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
        checks += ['porigin_selection = porigin_producer', '$magic_method_argument_call(expression_producer)', '~$magic_method_firstclass_call(expression_producer)']
    checks += [
        'expression_callback = NScalarString (BYTES text_literal) metadata_literal', 'porigin_selection = PORIGIN n_unit pcpath_selection',
        '$origin_node(S.SOURCES,porigin_selection) = (NExprFuncCall expression_callback (SEQUENCE phpType7_site*) metadata_site)',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])) = (expression_callback)',
        '$compiled_read(S,PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])) = eps',
        'ptbytes_original = $base64(text_literal)', '~$dynamic_method_scan(ptbytes_original,false,false)',
        'ptbytes_original = 92 :: ptbytes_normalized', '$ppcall_literal_name(ptbytes_original) = ptbytes_normalized',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]', '$code_name(pcode.NAMES,pcpath_selection) = ((ptbytes_normalized,eps))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_selection) = ((z_call,b_call))',
        '$call_target(S,ptbytes_normalized,eps) = (pfunction)', 'porigin_function = pfunction.ORIGIN',
        '$magic_method_function_string_source(S,porigin_selection,expression_callback,phpType7_real*) = (pfunction)',
        producer.format(state='S'), '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '~$magic_method_context_call(expression_producer)', '~$magic_method_context_arguments(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_function_string_source(S[.SOURCES = eps],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_function_string_source(S[.CODE = [pcode[.NAMES = eps]]],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_function_string_source(S[.CALLABLES = eps],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_function_string_source(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_selection ptbytes_original eps]]]],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_function_string_source(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_selection ptbytes_normalized (ptbytes_normalized)]]]],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_function_string_source(S,porigin_selection,expression_callback,eps) = eps',
        '$magic_method_function_string_source(S,porigin_selection,expression_callback,[NVariadicPlaceholder metadata_literal]) = eps',
        '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        ('$magic_method_firstclass_producer(S,porigin_producer,NExprFuncCall expression_capture (SEQUENCE ([phpType7_second,phpType7_first])) metadata_producer) = eps' if fcc else
         '$magic_method_required_producer(S,porigin_producer,NExprFuncCall expression_callback (SEQUENCE ([phpType7_second,phpType7_first])) metadata_producer) = eps'),
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if fcc:
        checks += [
            'S_selected.TODO = (FIRSTCLASS_CONVERT porigin_selection z_init z_capture) :: ptask_selection_tail*',
            '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
            'n_wrapper = |S_selected.OBJECTS|', 'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [NAMEDCLOSURE porigin_function]',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
            'S_ready = $functionstring246_ready_seek(S_wrapped,2048)', 'pcalltarget = CLOSURE_TARGET n_wrapper',
        ]
    else:
        checks += ['S_ready = S_selected', 'pcalltarget = porigin_function']
    checks += [
        'S_ready.COMPLETION = BUDGET', at(READY, 'S_ready'), 'pcalltarget_ready = pcalltarget', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        '$functionstring246_ready_seek(S,2048) = S_ready', '$target_nodes(pcalltarget) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$target_function(S_ready,pcalltarget) = (pfunction)', '$target_receiver(S_ready,pcalltarget) = eps',
        '$target_lexical_class(S_ready,pcalltarget) = eps', '$target_called_class(S_ready,pcalltarget) = eps',
        'S_body_found = $functionstring246_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)', 'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        producer.format(state='S_body'),
        'S_send_found = $functionstring246_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_old', 'pmagicmethodcall_send = pmagicmethodcall', 'porigin_send = pmagicmethodcall.SITE', 'z_send = pmagicmethodcall.LINE',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$magic_method_copy_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;CAPTURE;")',
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
                 (Path(__file__), CATALOGUE, CONTROLS, Path(direct.__file__), Path(names.__file__), Path(method.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
