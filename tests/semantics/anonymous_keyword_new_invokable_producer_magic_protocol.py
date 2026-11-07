#!/usr/bin/env python3
"""Keyword-New bare invocation keeps a real method receiver through return/SEND."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_invokable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-invokable-return-this'
DYNAMIC = ('S.TODO = (CALL_DYNAMIC porigin_producer z_init z_call) :: ptask_dynamic_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_packet) -- if S.CURRENT = (pcallcontext_caller)')
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_body) metadata_body])) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("INVOKE;") -- if S.CURRENT = (pcallcontext_body)')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* -- if S.RESULT = KNOWN (POBJECT n_return) '
          '-- if S.CURRENT = (pcallcontext_return) -- if pcallcontext_return.TARGET = METHOD_TARGET n_return porigin_return')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_send)')
PREFIX = names.PREFIX.replace(names.FRONT, DYNAMIC)
for label, front in [('shift', SHIFT), ('body', BODY), ('return', RETURN), ('send', SEND)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$newinvoke236_' + label + '_')
PREFIX += r'''
dec $newinvoke236_outer_one(ptask) : pmagicmethodcall?
def $newinvoke236_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $newinvoke236_outer_one(ptask) = eps -- otherwise
dec $newinvoke236_outer(ptask*) : pmagicmethodcall?
def $newinvoke236_outer(eps) = eps
def $newinvoke236_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $newinvoke236_outer_one(ptask) = (pmagicmethodcall)
def $newinvoke236_outer(ptask :: ptask_tail*) = $newinvoke236_outer(ptask_tail*) -- if $newinvoke236_outer_one(ptask) = eps
dec $newinvoke236_init_at(pcodeexpr, pcpath) : bool
def $newinvoke236_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $newinvoke236_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $newinvoke236_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $newinvoke236_without_init(eps, pcpath) = eps
def $newinvoke236_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $newinvoke236_without_init(pcodeexpr_tail*, pcpath) -- if $newinvoke236_init_at(pcodeexpr, pcpath)
def $newinvoke236_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $newinvoke236_without_init(pcodeexpr_tail*, pcpath) -- if ~$newinvoke236_init_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', DYNAMIC,
        '$newinvoke236_outer(ptask_dynamic_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase236")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope236")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild236")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_new (SEQUENCE phpType7_real*) metadata_producer',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_new)',
        '$magic_method_keyword_new_invokable_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_invokable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$effective_method(S,porigin_allocated,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc)',
        '$object_invoke_method(S,n_packet) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', r'~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '~$magic_method_plain_instance_source(S,pmethoddesc,phpType7_real*)',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '~$magic_producer_candidate(S,S.TODO,porigin_producer)',
        '$magic_method_keyword_new_invokable_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0])]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'pcalltarget = METHOD_TARGET n_packet porigin_method',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT pcalltarget (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_producer) z_call)) :: ptask_dynamic_tail*',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_selected.OBJECTS = S.OBJECTS', '$target_instance(pcalltarget) = eps',
        '$target_receiver(S_selected,pcalltarget) = (n_packet)',
        '$target_lexical_class(S_selected,pcalltarget) = (porigin_base)',
        '$target_called_class(S_selected,pcalltarget) = (porigin_allocated)',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_producer))',
        '$task_nodes(S_selected.TODO[0]) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_packet) = 1',
        'S_ready = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_ready.COMPLETION = BUDGET',
        'S_ready.TODO = (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_producer) z_call) :: ptask_dynamic_tail*',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_ready',
        '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_shift_found = $newinvoke236_shift_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', at(SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_invokable_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newinvoke236_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget',
        'pcallcontext_body.INSTANCE = eps', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$magic_method_keyword_new_invokable_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S_body,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_return_found = $newinvoke236_return_seek(S_body,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', at(RETURN, 'S_return'),
        'n_return = n_packet', 'porigin_return = porigin_method',
        '$heap_owners($heap_graph(S_return),HOBJECT n_packet) = 2',
        'S_send_found = $newinvoke236_send_seek(S_return,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
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
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;INVOKE;")',
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
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
