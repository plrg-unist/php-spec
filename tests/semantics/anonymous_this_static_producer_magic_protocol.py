#!/usr/bin/env python3
"""Direct static selection owns no receiver while the original caller owns This."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_static_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-this-static-direct-caller-retained'
READY = ('S.TODO = (CALL_ARGS (STATIC_METHOD_TARGET porigin_class_ready porigin_method_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_caller)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE:") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = (pcallcontext_caller)')
AFTER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_after) metadata_after])) metadata_echo_after)) :: ptask_after_tail* '
         '-- if $base64(text_after) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READY)
for label, front in [('body', BODY), ('send', SEND), ('after', AFTER)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisstatic229_' + label + '_')
PREFIX += r'''
dec $thisstatic229_outer_one(ptask) : pmagicmethodcall?
def $thisstatic229_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $thisstatic229_outer_one(ptask) = eps -- otherwise
dec $thisstatic229_outer(ptask*) : pmagicmethodcall?
def $thisstatic229_outer(eps) = eps
def $thisstatic229_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisstatic229_outer_one(ptask) = (pmagicmethodcall)
def $thisstatic229_outer(ptask :: ptask_tail*) = $thisstatic229_outer(ptask_tail*) -- if $thisstatic229_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READY,
        '$thisstatic229_outer(ptask_ready_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_ready)',
        '$origin_node(S.SOURCES,porigin_ready) = (expression_producer)',
        'expression_producer = NExprMethodCall (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_name) metadata_name) (SEQUENCE phpType7_ready*) metadata',
        '$direct_this(BYTES text_this)', '$base64(text_name) = $ptascii("capture")', '|phpType7_ready*| = 2',
        'pcallcontext_caller.RECEIVER = (n_this)', 'pcallcontext_caller.CALLED_CLASS = (porigin_class)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)', '$object_class_origin(S,n_this) = (porigin_class)',
        '$magic_method_this_producer(S,pmagicmethodcall.CALLER,porigin_ready,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_source(S,pmagicmethodcall.CALLER,porigin_ready,$ptascii("capture"),phpType7_ready*) = eps',
        '$magic_method_this_array_source(S,pmagicmethodcall.CALLER,porigin_ready,$ptascii("capture"),phpType7_ready*) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_producer(S,eps,porigin_ready,expression_producer) = eps',
        'porigin_class_ready = porigin_class', 'porigin_method_ready = pmethoddesc.FUNCTION.ORIGIN',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.STATIC',
        'pmethoddesc.OWNER =/= porigin_scope', 'pmethoddesc.OWNER =/= porigin_class', 'porigin_scope =/= porigin_class',
        '$closure_source_class(S,porigin_ready) = (porigin_scope)',
        '$target_function(S,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = (pfunction)',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_instance(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_receiver(S,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("runner")) = (n_runner_cell)', 'S.STORE[n_runner_cell] = DEFINED PNULL',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_this]', '$heap_owners($heap_graph(S),HOBJECT n_this) = 1',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)', 'S.STORE[n_argument_cell] = DEFINED (POBJECT n_old)',
        '$factory182_output(S.EVENTS) = $ptascii("FIRST;")',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_body_found = $thisstatic229_body_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_body_found.COMPLETION = BUDGET',
        'S_direct = $thisstatic229_body_seek(S,2048)', 'S_direct = S_body_found',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN',
        'pcallcontext_body.INSTANCE = eps', 'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_body.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_body.CURRENT) = eps',
        '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1', '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 1',
        '$call_current_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_send_found = $thisstatic229_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'), 'pmagicmethodcall_send = pmagicmethodcall',
        '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 1',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("FIRST;SHIFT;CAPTURE:CallerBase229:CallerChild229;")',
        'S_after_found = $thisstatic229_after_seek(S_send,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        '~((HOBJECT n_this) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
        '$object_class_origin(S_after,n_this) = (porigin_class)',
        '$magic_method_this_producer(S_after,pmagicmethodcall.CALLER,porigin_ready,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_producer(S_after,eps,porigin_ready,expression_producer) = eps',
    ]


def render(case, fixture, filename):
    checks = ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROWS[CASE]['source']}},
                 extra_inputs=(CATALOGUE, Path(__file__), Path(names.__file__), ROOT / 'tests/semantics/profile.json'),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())
