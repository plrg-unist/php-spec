#!/usr/bin/env python3
"""A fresh static selector retires before any real argument is captured."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_fresh_static_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-fresh-static-direct-selector-before-arguments'
PREP = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_real* false b_base z_prep) :: ptask_prep_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if S.CURRENT = eps '
        '-- if $method_capture(S,b_base,z_prep) = (S_capture,KNOWN (POBJECT n_selector))')
READY = ('S.TODO = (CALL_ARGS (STATIC_METHOD_TARGET porigin_class_ready porigin_method_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE:") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_new) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, PREP)
for label, front in [('ready', READY), ('body', BODY), ('send', SEND)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$freshstatic231_' + label + '_')
PREFIX += r'''
dec $freshstatic231_outer_one(ptask) : pmagicmethodcall?
def $freshstatic231_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $freshstatic231_outer_one(ptask) = eps -- otherwise
dec $freshstatic231_outer(ptask*) : pmagicmethodcall?
def $freshstatic231_outer(eps) = eps
def $freshstatic231_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $freshstatic231_outer_one(ptask) = (pmagicmethodcall)
def $freshstatic231_outer(ptask :: ptask_tail*) = $freshstatic231_outer(ptask_tail*) -- if $freshstatic231_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PREP,
        '$freshstatic231_outer(ptask_prep_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)', 'S.ORIGIN = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprMethodCall expression_receiver (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_real*) metadata',
        '|phpType7_real*| = 2',
        '$magic_method_fresh_receiver(S,PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0]),expression_receiver) = (porigin_class)',
        '$magic_method_instance_producer(S,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_class',
        '~$magic_method_plain_instance_source(S,pmethoddesc,phpType7_real*)',
        'S.OBJECTS[n_selector] = INSTANCE porigin_class', '(HOBJECT n_selector) <- S.ALLOCATIONS',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)', 'S.STORE[n_argument_cell] = DEFINED (POBJECT n_old)',
        '$factory182_output(S.EVENTS) = eps',
        'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_ready_found = $freshstatic231_ready_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $freshstatic231_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'porigin_class_ready = porigin_class', 'porigin_method_ready = pfunction.ORIGIN',
        'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
        '~((HOBJECT n_selector) <- S_ready.ALLOCATIONS)', '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 0',
        '$object_class_origin(S_ready,n_selector) = (porigin_class)',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_instance(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_receiver(S_ready,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_function(S_ready,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = (pfunction)',
        '$method_call_selected(S_ready,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN,(porigin_producer))',
        'S_ready.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '~((HOBJECT n_old) <- S_ready.ALLOCATIONS)',
        '$factory182_output(S_ready.EVENTS) = $ptascii("OLD;SELECTOR-END;")',
        '$magic_method_instance_producer(S_ready,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        'S_body_found = $freshstatic231_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN',
        'pcallcontext_body.INSTANCE = eps', 'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_body.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_body.CURRENT) = eps', '$heap_owners($heap_graph(S_body),HOBJECT n_selector) = 0',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_new)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_later)', 'n_later =/= n_new',
        '$call_current_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        'S_send_found = $freshstatic231_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'), 'pmagicmethodcall_send = pmagicmethodcall',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_new)],eps) = ([POBJECT n_new])',
        '$magic_method_instance_producer(S_send,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        '$factory182_output(S_send.EVENTS) = $ptascii("OLD;SELECTOR-END;SHIFT;CAPTURE:SelectorBase231:SelectorChild231;")',
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
