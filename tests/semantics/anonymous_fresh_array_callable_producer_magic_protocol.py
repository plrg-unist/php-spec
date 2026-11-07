#!/usr/bin/env python3
"""Fixed-name direct/FCC arrays retain generic source and copy authority."""
import argparse
import json
from pathlib import Path
import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_fresh_array_callable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = ('magic-fresh-array-callable-return-this', 'magic-fresh-array-firstclass-return-this')
BODY = direct.BODY.replace('INVOKE;', 'CAPTURE;')
SHIFT = direct.SHIFT
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = eps')
CONVERT = 'S.TODO = (ARRAY_CONVERT pcalltarget_capture parrayselection_capture) :: ptask_convert_tail* -- if S.CURRENT = eps'
READY = 'S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* -- if S.CURRENT = eps'


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    start = ('S.TODO = (' + ('FIRSTCLASS_CONVERT' if fcc else 'CALL_DYNAMIC') +
             ' porigin_selection z_init z_call) :: ptask_selection_tail* '
             '-- if S.RESULT = KNOWN (PARRAY n_callback) -- if S.CURRENT = eps')
    prefix = names.PREFIX.replace(names.FRONT, start)
    for label, front in [('ready', READY), ('convert', CONVERT), ('shift', SHIFT), ('body', BODY), ('send', SEND)]:
        prefix += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$fresharray242_' + label + '_')
    prefix += direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
    producer = ('$magic_method_firstclass_producer({state},porigin_producer,expression_producer) = (pmethoddesc.FUNCTION)' if fcc else
                '$magic_method_instance_producer({state},porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))')
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', start,
        '$newinvoke236_outer(ptask_selection_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = eps', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
    ]
    if fcc:
        checks += [
            'porigin_producer = PORIGIN n_unit pcpath_producer',
            'expression_producer = NExprFuncCall (NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture) (SEQUENCE phpType7_real*) metadata_producer',
            'porigin_selection = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
            '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
            '$magic_method_firstclass_call(expression_producer)', '~$magic_method_instance_call(expression_producer)',
        ]
    else:
        checks += [
            'expression_producer = NExprFuncCall expression_callback (SEQUENCE phpType7_real*) metadata_producer',
            'porigin_selection = porigin_producer', '$magic_method_instance_call(expression_producer)',
            '~$magic_method_firstclass_call(expression_producer)',
        ]
    checks += [
        'porigin_selection = PORIGIN n_unit pcpath_selection',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        'expression_new = NExprNew (NName (BYTES text_class) metadata_class) (SEQUENCE phpType7_ctor*) metadata_new',
        '~$ppscoped_keyword(NName (BYTES text_class) metadata_class)',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        'pcpath_new = pcpath_selection ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
        'porigin_new = PORIGIN n_unit pcpath_new', '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
        '$origin_child((porigin_selection),[PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1]) = (porigin_literal)',
        '$magic_method_literal_value(S,porigin_literal,expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        'S.CODE = [pcode]', '$code_name(pcode.NAMES,pcpath_new) = ((preqbytes,eps))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = eps', '~$ordinary_keyword_new_site(S,porigin_new)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_selection) = (z_init)', '$closure_source_class(S,porigin_selection) = eps',
        '$magic_method_new_class(S,porigin_new,expression_new) = ((preqbytes,porigin_allocated))',
        '$magic_method_fresh_receiver(S,porigin_new,expression_new) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild242")) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase242")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptlc(preqbytes)) = (porigin_allocated)',
        '$magic_method_fresh_array_source(S,porigin_selection,expression_callback,phpType7_real*) = ((porigin_allocated,pmethoddesc))',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', r'~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT', producer.format(state='S'),
        '~$magic_method_context_call(expression_producer)', '~$magic_method_context_arguments(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_fresh_array_source(S[.SOURCES = eps],porigin_selection,expression_callback,phpType7_real*) = eps',
        '$magic_method_fresh_array_source(S[.CODE = [pcode[.NAMES = eps]]],porigin_selection,expression_callback,phpType7_real*) = eps',
        '~$magic_method_copy_source(S[.CODE = [pcode[.NAMES = eps]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_selection)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_packet)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED (METHOD_TARGET n_packet porigin_method) porigin_allocated ($ptascii("capture"))',
        'S_zero = $drive_steps(S,0)', 'S_zero = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.OBJECTS = S.OBJECTS', 'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if fcc:
        checks += [
            '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
            '~$magic_method_copy_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
            'S_convert = $fresharray242_convert_seek(S_selected,2048)', 'S_convert.COMPLETION = BUDGET', at(CONVERT, 'S_convert'),
            'pcalltarget_capture = METHOD_TARGET n_packet porigin_method',
            'parrayselection_capture.SITE = porigin_selection', 'parrayselection_capture.REQUESTED = porigin_allocated',
            'parrayselection_capture.INIT = z_init', 'parrayselection_capture.LINE = z_call',
            'parrayselection_capture.NAME = $ptascii("capture")',
            '$array_convert_valid(S_convert,pcalltarget_capture,parrayselection_capture)',
            '~((HARRAY n_callback) <- S_convert.ALLOCATIONS)',
            'n_wrapper = |S.OBJECTS|', 'S_wrapped = $drive_steps(S_convert[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS[n_wrapper] = ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?',
            'S_wrapped.OBJECTS = S.OBJECTS ++ [ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?]',
            'pmethodcapture? = $method_capture_current(S_convert,porigin_selection)',
            'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)', 'S_wrapped.BASE = BASE_VALUE (KNOWN PNULL)',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_packet]',
            'S_ready = $fresharray242_ready_seek(S_wrapped,2048)', 'pcalltarget = CLOSURE_TARGET n_wrapper',
        ]
    else:
        checks += [
            'S_ready = $fresharray242_ready_seek(S_selected,2048)',
            'pcalltarget = ARRAY_METHOD_TARGET (METHOD_TARGET n_packet porigin_method) {SITE porigin_selection, INIT z_init, LINE z_call, REQUESTED porigin_allocated, NAME $ptascii("capture")}',
        ]
    checks += [
        'S_ready.COMPLETION = BUDGET', at(READY, 'S_ready'),
        'pcalltarget_ready = pcalltarget', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        'S_direct = $fresharray242_ready_seek(S,2048)', 'S_direct = S_ready',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '$target_instance(pcalltarget) = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$target_receiver(S_ready,pcalltarget) = (n_packet)',
        '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)',
        '$target_called_class(S_ready,pcalltarget) = (porigin_allocated)',
        '$call_selected_valid(S_ready,pcalltarget,(porigin_producer))',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_packet) = 1',
        'S_shift_found = $fresharray242_shift_seek(S_ready,2048)', 'S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', at(SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)', 'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        producer.format(state='S_shift'), '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        'S_body_found = $fresharray242_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget',
        'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        'pcallcontext_body.RECEIVER = (n_packet)',
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else '[HOBJECT n_packet]'),
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1', producer.format(state='S_body'),
        'S_send_found = $fresharray242_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall', 'porigin_send = pmagicmethodcall.SITE', 'z_send = pmagicmethodcall.LINE',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$magic_method_copy_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT n_packet)]) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;CAPTURE;")',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_packet)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$tasks_nodes(S_sent.TODO)) = 1',
        '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]
    if fcc:
        checks += ['~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)']
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or CASES)},
                 (Path(__file__), CATALOGUE, Path(direct.__file__), Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
