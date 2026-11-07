#!/usr/bin/env python3
"""Static class-string arrays retain pool ownership and real returned leaves."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_array_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_static_array_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-static-array-direct-return-old', 'magic-static-array-fcc-return-old')
UNPACK = 'magic-static-array-direct-unpack-refused'
READY = 'S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* -- if S.CURRENT = eps'
CONVERT = 'S.TODO = (ARRAY_CONVERT pcalltarget_capture parrayselection_capture) :: ptask_convert_tail* -- if S.CURRENT = eps'
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
HELPERS = r'''
dec $staticarray244_expression_at(pcodeexpr, pcpath) : bool
def $staticarray244_expression_at(CODEEXPR pcpath z b, pcpath) = true
def $staticarray244_expression_at(pcodeexpr, pcpath) = false -- otherwise
dec $staticarray244_without_expression(pcodeexpr*, pcpath) : pcodeexpr*
def $staticarray244_without_expression(eps, pcpath) = eps
def $staticarray244_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = $staticarray244_without_expression(pcodeexpr_tail*, pcpath) -- if $staticarray244_expression_at(pcodeexpr, pcpath)
def $staticarray244_without_expression(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $staticarray244_without_expression(pcodeexpr_tail*, pcpath) -- if ~$staticarray244_expression_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.')


def seeker(label, front):
    return names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$staticarray244_' + label + '_')


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
    return names.PREFIX.replace(names.FRONT, BOUNDARY), checks


def ownership(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    front = ('S.TODO = (' + ('FIRSTCLASS_CONVERT' if fcc else 'CALL_DYNAMIC') +
             ' porigin_selection z_init z_call) :: ptask_selection_tail* -- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = eps')
    prefix = names.PREFIX.replace(names.FRONT, front) + HELPERS
    prefix += direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
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
        '|phpType7_real*| = 2',
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
        'porigin_selection = PORIGIN n_unit pcpath_selection', 'porigin_callback = PORIGIN n_unit (pcpath_selection ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_callback) = (expression_callback)',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_class (BOOLEAN false) (BOOLEAN false) metadata_class_item),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method_item)])) metadata_array',
        'expression_class = NScalarString (BYTES text_class) metadata_class', 'expression_method = NScalarString (BYTES text_method) metadata_method',
        'pcpath_class = pcpath_selection ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
        'pcpath_method = pcpath_selection ++ [PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1]',
        '$compiled_read(S,porigin_callback) = (PARRAY n_callback)', '$compiled_effects(S,porigin_callback) = eps',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_class),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$string_bytes(pvalue_class) = ($base64(text_class))', '$string_bytes(pvalue_method) = ($base64(text_method))',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]', '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase244")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild244")) = (porigin_class)',
        '$magic_method_static_array_source(S,porigin_callback,expression_callback,phpType7_real*) = ((porigin_class,pmethoddesc))',
        producer.format(state='S'), 'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base', 'pmethoddesc.STATIC',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '~$magic_method_context_call(expression_producer)', '~$magic_method_context_arguments(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_static_array_source(S[.SOURCES = eps],porigin_callback,expression_callback,phpType7_real*) = eps',
        '$magic_method_static_array_source(S[.POOLS = eps],porigin_callback,expression_callback,phpType7_real*) = eps',
        '$magic_method_static_array_source(S,porigin_callback,expression_callback,eps) = eps',
        'S_no_literals = S[.CODE = [pcode[.EXPRESSIONS = $staticarray244_without_expression($staticarray244_without_expression(pcode.EXPRESSIONS,pcpath_class),pcpath_method)]]]',
        '$compiled_read(S_no_literals,PORIGIN n_unit pcpath_class) = eps', '$compiled_read(S_no_literals,PORIGIN n_unit pcpath_method) = eps',
        '$magic_method_static_array_source(S_no_literals,porigin_callback,expression_callback,phpType7_real*) = ((porigin_class,pmethoddesc))',
        '$magic_method_static_array_source(S[.ARRAYS = S.ARRAYS[n_callback = S.ARRAYS[n_callback][.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_method),ENTRY (KINT 1) (DIRECT pvalue_method)]]]],porigin_callback,expression_callback,phpType7_real*) = eps',
        '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '(HARRAY n_callback) <- $pools_nodes(S.POOLS)', '$heap_owners($heap_graph(S),HARRAY n_callback) = 2',
        '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED (STATIC_METHOD_TARGET porigin_class porigin_method) porigin_class ($ptascii("capture"))',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if fcc:
        checks += [
            '$magic_method_static_array_source(S,porigin_callback,expression_callback,[NVariadicPlaceholder metadata_placeholder]) = eps',
            '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
            'S_convert = $staticarray244_convert_seek(S_selected,2048)', 'S_convert.COMPLETION = BUDGET', at(CONVERT, 'S_convert'),
            'pcalltarget_capture = STATIC_METHOD_TARGET porigin_class porigin_method', 'parrayselection_capture.SITE = porigin_selection',
            'parrayselection_capture.REQUESTED = porigin_class', 'parrayselection_capture.INIT = z_init',
            'pmethodcapture? = $method_capture_current(S_convert,porigin_selection)', 'n_wrapper = |S.OBJECTS|',
            'S_wrapped = $drive_steps(S_convert[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS = S.OBJECTS ++ [ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?]',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
            'S_ready = $staticarray244_ready_seek(S_wrapped,2048)', 'pcalltarget = CLOSURE_TARGET n_wrapper',
        ]
    else:
        checks += [
            'S_ready = $staticarray244_ready_seek(S_selected,2048)',
            'pcalltarget = ARRAY_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) {SITE porigin_selection, INIT z_init, LINE z_call, REQUESTED porigin_class, NAME $ptascii("capture")}',
        ]
    checks += [
        'S_ready.COMPLETION = BUDGET', at(READY, 'S_ready'), 'pcalltarget_ready = pcalltarget', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        '$staticarray244_ready_seek(S,2048) = S_ready', '(HARRAY n_callback) <- S_ready.ALLOCATIONS', '$heap_owners($heap_graph(S_ready),HARRAY n_callback) = 1',
        '$target_receiver(S_ready,pcalltarget) = eps', '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)', '$target_called_class(S_ready,pcalltarget) = (porigin_class)',
        'S_body_found = $staticarray244_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET', 'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.RECEIVER = eps', 'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)', 'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        '$heap_owners($heap_graph(S_body),HARRAY n_callback) = 1', producer.format(state='S_body'),
        'S_send_found = $staticarray244_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET', 'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_old', 'pmagicmethodcall_send = pmagicmethodcall', 'porigin_send = pmagicmethodcall.SITE', 'z_send = pmagicmethodcall.LINE',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_send),HARRAY n_callback) = 1',
        '$magic_method_copy_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;CAPTURE;PacketBase244/PacketChild244;")',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
        '$heap_count(HOBJECT n_old,$tasks_nodes(S_sent.TODO)) = 1', '$heap_owners($heap_graph(S_sent),HARRAY n_callback) = 1',
        '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
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
