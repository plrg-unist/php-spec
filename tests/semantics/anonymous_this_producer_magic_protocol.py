#!/usr/bin/env python3
"""Caller-held This survives a producer edge and later retires independently."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_this_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-this-direct-pending-leaf'
UNPACK = 'magic-this-unpack-refused'
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_string_body) :: expression_echo_tail*)) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = (pcallcontext_send)')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = (pcallcontext_boundary)')
PREFIX = names.PREFIX.replace(names.FRONT, BODY)
for label, front in [('send', SEND), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$this216_' + label + '_')
PREFIX += r'''
dec $this216_outer_one(ptask) : pmagicmethodcall?
def $this216_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $this216_outer_one(ptask) = eps -- otherwise
dec $this216_outer(ptask*) : pmagicmethodcall?
def $this216_outer(eps) = eps
def $this216_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $this216_outer_one(ptask) = (pmagicmethodcall)
def $this216_outer(ptask :: ptask_tail*) = $this216_outer(ptask_tail*) -- if $this216_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BODY,
        'pcallcontext_body.TARGET = METHOD_TARGET n_this porigin_method',
        'pcallcontext_body.RECEIVER = (n_this)', 'pcallcontext_body.INSTANCE = eps',
        'pcallcontext_body.CALLSITE = (porigin_producer)',
        'S.FRAMES = pframe_caller :: pframe_tail*', 'pframe_caller.CONTEXT = (pcallcontext_caller)',
        'pcallcontext_caller.RECEIVER = (n_this)',
        '$this216_outer(pframe_caller.TODO) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_method_this_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_this]', '$heap_owners($heap_graph(S),HOBJECT n_this) = 2',
        '$lookup($global_table_view(S).ENV,$ptascii("runner")) = (n_runner_cell)', 'S.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved_cell)', 'S.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;")',
        '$magic_method_this_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S,(pcallcontext_caller[.RECEIVER = eps]),porigin_producer,expression_producer) = eps',
        '$magic_method_this_producer(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_send_found = $this216_send_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_send_found.COMPLETION = BUDGET',
        'S_direct = $this216_send_seek(S,2048)', 'S_direct = S_send_found',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
        '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 1', '(HOBJECT n_this) <- S_send.ALLOCATIONS',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        'S_root_found = $this216_return_seek(S_send,2048)', 'S_root_found.COMPLETION = BUDGET',
        'S_root = S_root_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_root.'), 'S_root.FRAMES = eps',
        '~((HOBJECT n_this) <- S_root.ALLOCATIONS)', '(HOBJECT n_old) <- S_root.ALLOCATIONS',
        '$object_class_origin(S_root,n_this) = (porigin_class)',
        '$magic_method_this_producer(S_root,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_producer(S_root,S_root.CURRENT,porigin_producer,expression_producer) = eps',
        '$factory182_output(S_root.EVENTS) = $ptascii("SHIFT;PRODUCER;ProducerBase216/ProducerChild216;NEW;HANDLER;OWNER;THIS-END;")',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $this216_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_this_producer(S,S.CURRENT,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
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
    checks = unpack_boundary(fixture, filename) if case['source'] == ROWS[UNPACK]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks), len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
