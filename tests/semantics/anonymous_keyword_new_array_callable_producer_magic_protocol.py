#!/usr/bin/env python3
"""Direct keyword-New callable arrays retain selected receivers through bare SEND."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_array_callable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-array-callable-return-this'
DYNAMIC = direct.DYNAMIC.replace('POBJECT n_packet', 'PARRAY n_callback')
BODY = direct.BODY.replace('INVOKE;', 'CAPTURE;')
READY = ('S.TODO = (CALL_ARGS pcalltarget_ready phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PREFIX = direct.PREFIX.replace(direct.DYNAMIC, DYNAMIC).replace('INVOKE;', 'CAPTURE;')
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, READY).replace('$factory182_', '$array240_ready_')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', DYNAMIC,
        '$newinvoke236_outer(ptask_dynamic_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_packet)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase240")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope240")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild240")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_callback (SEQUENCE phpType7_real*) metadata_producer',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        'expression_method = NScalarString phpType33 metadata_literal',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'pcpath_new = pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
        'porigin_new = PORIGIN n_unit pcpath_new',
        '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1])) = (expression_method)',
        '$magic_method_literal_value(S,PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1]),expression_method) = (pvalue_method)',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = (z_new)',
        '$magic_method_keyword_new_array_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_array_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$method_class_selected(S,porigin_allocated,$ptascii("capture"),(porigin_scope)) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', r'~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '$magic_method_fresh_method_source(S,porigin_allocated,porigin_producer,$ptascii("capture"),phpType7_real*) = (pmethoddesc)',
        '$magic_method_keyword_new_array_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S,pmagicmethodcall.CALLER,porigin_new,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_new)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '$array_resolve(S,n_callback,ARRAY_DISPATCH) = ARRAYRESOLVED (METHOD_TARGET n_packet porigin_method) porigin_allocated $ptascii("capture")',
        'pcalltarget = ARRAY_METHOD_TARGET (METHOD_TARGET n_packet porigin_method) {SITE porigin_producer, INIT z_init, LINE z_call, REQUESTED porigin_allocated, NAME $ptascii("capture")}',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_selected.OBJECTS = S.OBJECTS',
        'S_ready = $array240_ready_seek(S_selected,2048)', 'S_ready.COMPLETION = BUDGET',
        direct.at(READY, 'S_ready'), 'pcalltarget_ready = pcalltarget',
        'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        'z_ready = z_call', 'pcallcontext_ready = pcallcontext_caller',
        'S_direct = $array240_ready_seek(S,2048)', 'S_direct = S_ready',
        'S_ready.OBJECTS = S.OBJECTS',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '$target_instance(pcalltarget) = eps',
        '$target_receiver(S_ready,pcalltarget) = (n_packet)',
        '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)',
        '$target_called_class(S_ready,pcalltarget) = (porigin_allocated)',
        '$target_function(S_ready,pcalltarget) = (pmethoddesc.FUNCTION)',
        '$call_selected_valid(S_ready,pcalltarget,(porigin_producer))',
        '$task_nodes(S_ready.TODO[0]) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_packet) = 1',
        '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_shift_found = $newinvoke236_shift_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', direct.at(direct.SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_array_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newinvoke236_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', direct.at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget',
        'pcallcontext_body.INSTANCE = eps', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$magic_method_keyword_new_array_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_producer(S_body,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_send_found = $newinvoke236_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', direct.at(direct.SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller', 'porigin_send = pmagicmethodcall.SITE',
        'z_send = pmagicmethodcall.LINE', 'S_send.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$operand_nodes(S_send.RESULT)) = 1',
        '$heap_count(HOBJECT n_packet,$machine_base_roots(S_send)) = 0',
        '$heap_count(HOBJECT n_packet,$call_context_roots(S_send.CURRENT)) = 0',
        '$heap_count(HOBJECT n_packet,$frames_roots(S_send.FRAMES)) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;CAPTURE;")',
        '$call_descriptors_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_packet)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$tasks_nodes(S_sent.TODO)) = 1',
        '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__), Path(direct.__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
