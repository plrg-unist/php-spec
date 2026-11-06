#!/usr/bin/env python3
"""Saved caller scopes for real keyword-static targets and collection."""
import argparse
import base64
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_static_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_keyword_static_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-keyword-static-pending-leaf'
UNPACK = 'magic-keyword-static-unpack-refused'
SELECT = ('S.TODO = (FUNCTION_CACHE_INIT (SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) '
          '(CALL_ARGS (SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) phpType7_inner* 0 eps (porigin_producer) z_call)) :: ptask_select_tail* '
          '-- if S.CURRENT = (pcallcontext_caller)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = (pcallcontext_send)')
HANDLER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_handler) metadata_string_handler])) metadata_echo_handler)) :: ptask_handler_tail* '
           '-- if $base64(text_handler) = $ptascii("HANDLER;") -- if S.CURRENT = (pcallcontext_handler)')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = (pcallcontext_boundary)')
PREFIX = names.PREFIX.replace(names.FRONT, SELECT)
for label, front in [('send', SEND), ('handler', HANDLER), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$keyword214_' + label + '_')
PREFIX += r'''
dec $keyword214_outer_one(ptask) : pmagicmethodcall?
def $keyword214_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $keyword214_outer_one(ptask) = eps -- otherwise
dec $keyword214_outer(ptask*) : pmagicmethodcall?
def $keyword214_outer(eps) = eps
def $keyword214_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $keyword214_outer_one(ptask) = (pmagicmethodcall)
def $keyword214_outer(ptask :: ptask_tail*) = $keyword214_outer(ptask_tail*) -- if $keyword214_outer_one(ptask) = eps
'''


def at(front, state):
    return front.replace('S.', state + '.')


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SELECT,
        '$class_named(S.CLASSNAMES,$ptascii("producerscope214")) = (porigin_requested)',
        '$class_named(S.CLASSNAMES,$ptascii("producerchild214")) = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("producerbase214")) = (porigin_declaring)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_requested)', 'pcallcontext_caller.CALLED_CLASS = (porigin_called)',
        '$keyword214_outer(S.TODO) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        'pmagicmethodcall.PRODUCERS = eps', '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_method_keyword_static_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_declaring', 'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$target_nodes(SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) = eps',
        '$target_receiver(S,SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) = eps',
        '$target_instance(SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) = eps',
        '$magic_method_keyword_static_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_static_producer(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_static_producer(S,(pcallcontext_caller[.CALLED_CLASS = eps]),porigin_producer,expression_producer) = eps',
        'S_send_found = $keyword214_send_seek(S,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
        '$magic_method_value(S_send,POBJECT n_old)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_sent_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
        'pdestructionrelease.CALLER = pmagicmethodcall.CALLER',
        'S_handler_found = $keyword214_handler_seek(S_sent[.COMPLETION = NORMAL],2047)', 'S_handler_found.COMPLETION = BUDGET',
        'S_direct = $keyword214_handler_seek(S_send,2048)', 'S_direct = S_handler_found',
        'S_handler = S_handler_found[.COMPLETION = NORMAL]', at(HANDLER, 'S_handler'),
        'pcallcontext_handler.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_table ([POBJECT n_old])',
        'S_handler.ARRAYS[n_table] = $magic_method_array([POBJECT n_old],0)',
        'pcallcontext_handler.LEXICAL_CLASS =/= pcallcontext_caller.LEXICAL_CLASS',
        '$magic_method_keyword_static_producer(S_handler,S_handler.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_static_producer(S_handler,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_context_values(S_handler,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_context_values(S_handler,S_handler.CURRENT,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_descriptor(S_handler,pmagicmethodcall)', '$call_descriptors_valid(S_handler)',
        'S_root_found = $keyword214_return_seek(S_handler,2048)', 'S_root_found.COMPLETION = BUDGET',
        'S_root = S_root_found[.COMPLETION = NORMAL]', at(RETURN, 'S_root'), 'S_root.FRAMES = eps',
        '$magic_method_keyword_static_producer(S_root,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_keyword_static_producer(S_root,S_root.CURRENT,porigin_producer,expression_producer) = eps',
        '(HARRAY n_table) <- S_root.ALLOCATIONS', '(HOBJECT n_old) <- S_root.ALLOCATIONS',
        '$heap_owners($heap_graph(S_root),HOBJECT n_old) = 1',
        'S_done = $drive_steps(S_root,2048)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.term(base64.b64decode(ROWS[CASE]['stdout_template_base64'])),
        '~((HARRAY n_table) <- S_done.ALLOCATIONS)', '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $keyword214_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_keyword_static_producer(S,S.CURRENT,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$base64(text_pack)) = (n_pack_cell)', 'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,2048)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    clauses = unpack_boundary(fixture, filename) if case['source'] == ROWS[UNPACK]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
