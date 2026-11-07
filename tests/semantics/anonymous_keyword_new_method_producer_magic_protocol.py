#!/usr/bin/env python3
"""A fresh keyword receiver transfers real This through method return and SEND."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_method_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-method-return-this'
PREP = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_method* false false z_method) :: ptask_prep_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if S.RESULT = KNOWN (POBJECT n_packet) '
        '-- if S.ORIGIN = (porigin_producer) -- if S.CURRENT = (pcallcontext_caller)')
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_body) metadata_body])) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("METHOD;") -- if S.CURRENT = (pcallcontext_body)')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* -- if S.RESULT = KNOWN (POBJECT n_return) '
          '-- if S.CURRENT = (pcallcontext_return) -- if pcallcontext_return.TARGET = METHOD_TARGET n_return porigin_return')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_send)')
SENT = ('S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_sent) eps 1 ([KNOWN (POBJECT n_sent)]) (porigin_sent) z_sent) :: ptask_sent_tail* '
        '-- if S.CURRENT = (pcallcontext_sent)')
PREFIX = names.PREFIX.replace(names.FRONT, PREP)
for label, front in [('shift', SHIFT), ('body', BODY), ('return', RETURN), ('send', SEND), ('sent', SENT)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$newmethod234_' + label + '_')
PREFIX += r'''
dec $newmethod234_outer_one(ptask) : pmagicmethodcall?
def $newmethod234_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $newmethod234_outer_one(ptask) = eps -- otherwise
dec $newmethod234_outer(ptask*) : pmagicmethodcall?
def $newmethod234_outer(eps) = eps
def $newmethod234_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $newmethod234_outer_one(ptask) = (pmagicmethodcall)
def $newmethod234_outer(ptask :: ptask_tail*) = $newmethod234_outer(ptask_tail*) -- if $newmethod234_outer_one(ptask) = eps
'''


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PREP,
        '$newmethod234_outer(ptask_prep_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase234")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope234")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild234")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprMethodCall expression_receiver (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_method*) metadata_producer',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_receiver = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        '$ordinary_keyword_new_site(S,porigin_receiver)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_producer) = ((z_source,false))',
        'z_source = $source_line(metadata_producer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = eps',
        '$magic_method_keyword_new_method_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_method_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_base', '~pmethoddesc.STATIC',
        '$magic_method_instance_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '~$magic_producer_candidate(S,S.TODO,porigin_producer)',
        '$method_receiver_value_allowed(S,S.RESULT,$ptascii("capture"),phpType7_method*,z_method)',
        '$method_selected_metadata(S,METHOD_TARGET n_packet pmethoddesc.FUNCTION.ORIGIN,(porigin_producer)) = S',
        '$target_nodes(METHOD_TARGET n_packet pmethoddesc.FUNCTION.ORIGIN) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 1',
        '$magic_method_keyword_new_method_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S,(pcallcontext_caller[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]),porigin_producer,expression_producer) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = KNOWN PNULL', '$heap_owners($heap_graph(S_one),HOBJECT n_packet) = 1',
        'S_shift_found = $newmethod234_shift_seek(S_one[.COMPLETION = NORMAL],2047)',
        'S_shift_found.COMPLETION = BUDGET',
        'S_direct = $newmethod234_shift_seek(S,2048)', 'S_direct = S_shift_found',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', at(SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_method_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newmethod234_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = METHOD_TARGET n_packet pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_body.RECEIVER = (n_packet)', 'pcallcontext_body.INSTANCE = eps',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$magic_method_keyword_new_method_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S_body,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_return_found = $newmethod234_return_seek(S_body,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', at(RETURN, 'S_return'),
        'n_return = n_packet', 'porigin_return = pmethoddesc.FUNCTION.ORIGIN',
        '$heap_owners($heap_graph(S_return),HOBJECT n_packet) = 2',
        'S_send_found = $newmethod234_send_seek(S_return,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller',
        'S_send.BASE = BASE_VALUE (KNOWN (POBJECT n_packet))',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 2',
        '$heap_count(HOBJECT n_packet,$operand_nodes(S_send.RESULT)) = 1',
        '$heap_count(HOBJECT n_packet,$machine_base_roots(S_send)) = 1',
        '$heap_count(HOBJECT n_packet,$call_context_roots(S_send.CURRENT)) = 0',
        '$heap_count(HOBJECT n_packet,$frames_roots(S_send.FRAMES)) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = eps',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7)],eps) = ([PINT 7])',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PARRAY 0)],eps) = eps',
        '$call_descriptors_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_transfer = $drive_steps(S_send,1)', 'S_transfer.COMPLETION = BUDGET',
        'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_transfer_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_packet)]',
        'pdestructionrelease.CALLER = pmagicmethodcall.CALLER',
        'ptask_transfer_tail* = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_packet)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_transfer_sent_tail*',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_transfer.RESULT = KNOWN PNULL', 'S_transfer.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_transfer),HOBJECT n_packet) = 2',
        '$heap_count(HOBJECT n_packet,$tasks_nodes(S_transfer.TODO)) = 2',
        'S_sent_found = $newmethod234_sent_seek(S_transfer[.COMPLETION = NORMAL],2047)',
        'S_sent_found.COMPLETION = BUDGET',
        'S_sent_direct = $newmethod234_sent_seek(S_send,2048)', 'S_sent_direct = S_sent_found',
        'S_sent = S_sent_found[.COMPLETION = NORMAL]', at(SENT, 'S_sent'),
        'n_sent = n_packet', 'pmagicmethodcall_sent = pmagicmethodcall',
        'pcallcontext_sent = pcallcontext_caller',
        'porigin_sent = pmagicmethodcall.SITE', 'z_sent = pmagicmethodcall.LINE',
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
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
