#!/usr/bin/env python3
"""Keyword NEW allocation scope and its real constructor-to-SEND owners."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-pending-leaf'
CTOR = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_ctor) metadata_ctor])) metadata_echo)) :: ptask_ctor_tail* '
        '-- if $base64(text_ctor) = $ptascii("CTOR;") -- if S.CURRENT = (pcallcontext_ctor)')
RESULT = ('S.TODO = (CTOR_RESULT n_result) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (PINT 7) -- if S.CURRENT = (pcallcontext_result)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) phpType7_send* 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_send)')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, CTOR)
for label, front in [('result', RESULT), ('send', SEND), ('return', RETURN)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$new233_' + label + '_')
PREFIX += r'''
dec $new233_outer_one(ptask) : pmagicmethodcall?
def $new233_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $new233_outer_one(ptask) = eps -- otherwise
dec $new233_outer(ptask*) : pmagicmethodcall?
def $new233_outer(eps) = eps
def $new233_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $new233_outer_one(ptask) = (pmagicmethodcall)
def $new233_outer(ptask :: ptask_tail*) = $new233_outer(ptask_tail*) -- if $new233_outer_one(ptask) = eps
'''


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    clauses = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CTOR,
        'pcallcontext_ctor.TARGET = METHOD_TARGET n_packet porigin_ctor',
        'S.FRAMES = pframe_caller :: pframe_tail*',
        '$new233_outer(pframe_caller.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        'pframe_caller.CONTEXT = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase233")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope233")) = (porigin_allocated)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild233")) = (porigin_called)',
        'porigin_allocated =/= porigin_called',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_allocated)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_ctor.CALLED_CLASS = (porigin_allocated)',
        'pcallcontext_ctor.RECEIVER = (n_packet)',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprNew name_producer (SEQUENCE phpType7_inner*) metadata_producer',
        '$ordinary_keyword_new_site(S,porigin_producer)',
        '$magic_method_keyword_new_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_class(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = (porigin_allocated)',
        '$magic_method_keyword_new_source(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '~$magic_method_keyword_new_source(S,S.CURRENT,porigin_producer,expression_producer)',
        '~$magic_method_keyword_new_source(S,eps,porigin_producer,expression_producer)',
        '~$magic_method_keyword_new_source(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '~$magic_method_keyword_new_source(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_class(S,(pcallcontext_caller[.CALLED_CLASS = eps]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_class(S,(pcallcontext_caller[.FUNCTION = porigin_ctor]),porigin_producer,expression_producer) = eps',
        '$magic_method_constructor_source(S,porigin_allocated,phpType7_inner*) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_ctor',
        'pmethoddesc.OWNER = porigin_base',
        '$magic_method_constructor_producer(S,porigin_producer,expression_producer) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_replacement)',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
        'S.STORE[n_saved] = DEFINED (POBJECT n_old)', 'n_old =/= n_replacement',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 2',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CTOR_RESULT n_packet) = [HOBJECT n_packet]',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_result_found = $new233_result_seek(S,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', at(RESULT, 'S_result'),
        'n_result = n_packet', 'pcallcontext_result = pcallcontext_caller',
        '$ctor_result_valid(S_result,n_packet)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_packet) = 1',
        '~((HOBJECT n_old) <- S_result.ALLOCATIONS)',
        'S_instance = $drive_steps(S_result,1)', 'S_instance.COMPLETION = BUDGET',
        'S_instance.RESULT = KNOWN (POBJECT n_packet)', 'S_instance.TODO = ptask_result_tail*',
        '$heap_owners($heap_graph(S_instance),HOBJECT n_packet) = 1',
        'S_send_found = $new233_send_seek(S_instance[.COMPLETION = NORMAL],2047)',
        'S_send_found.COMPLETION = BUDGET',
        'S_direct = $new233_send_seek(S_result,2048)', 'S_direct = S_send_found',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_packet', 'pcallcontext_send = pcallcontext_caller',
        'pmagicmethodcall_send = pmagicmethodcall',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet),KNOWN PNULL],eps) = ([POBJECT n_packet,PNULL])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet),KNOWN PNULL],eps) = eps',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN PNULL],eps) = eps',
        '$magic_method_value(S_send,POBJECT n_replacement)',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_replacement),KNOWN PNULL],eps) = eps',
        '$magic_method_context_values(S_send[.CODE = eps],pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet),KNOWN PNULL],eps) = eps',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$new233_outer(S_send.TODO) = (pmagicmethodcall)',
        '$call_descriptors_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_root_found = $new233_return_seek(S_send,2048)', 'S_root_found.COMPLETION = BUDGET',
        'S_root = S_root_found[.COMPLETION = NORMAL]', at(RETURN, 'S_root'), 'S_root.FRAMES = eps',
        '$magic_method_keyword_new_class(S_root,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = (porigin_allocated)',
        '$magic_method_keyword_new_class(S_root,S_root.CURRENT,porigin_producer,expression_producer) = eps',
        '$heap_owners($heap_graph(S_root),HOBJECT n_packet) = 1',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_root.ALLOCATIONS)',
        'S_done = $drive_steps(S_root,2048)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.term(base64.b64decode(ROWS[CASE]['stdout_template_base64'])),
        '~((HOBJECT n_packet) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)',
        '$magic_method_context_values(S_done,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet),KNOWN PNULL],eps) = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
