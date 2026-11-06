#!/usr/bin/env python3
"""A static This-array factory drops its array edge while its caller owns This."""
import argparse
import json
from pathlib import Path
import anonymous_this_array_from_callable_producer_magic_protocol as previous

protocol = previous.protocol
ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_static_array_from_callable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-this-static-array-caller-retained'
FACTORY, READY, BODY, SEND, AFTER = previous.FACTORY, previous.READY, previous.BODY, previous.SEND, previous.AFTER
PREFIX = previous.PREFIX.replace('$thisarray226_', '$thisstaticarray228_')


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$thisstaticarray228_outer(ptask_factory_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)', 'porigin_outer = PORIGIN n_unit pcpath_outer',
        'pconfigcall.SITE = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_method_from_callable_parts(S,porigin_outer,expression_outer) = ((porigin_callback,expression_callback,phpType7_real*))', '|phpType7_real*| = 2',
        '$compiled_read(S,porigin_callback) = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]', 'papiquery.VALUE = PARRAY n_callback',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_this)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        'papiquery.INPUT = POBJECT n_this', '~papiquery.CLASS.STRICT', 'papiquery.CLASS.REQUESTED = porigin_class',
        'papiquery.CLASS.RECEIVER = (n_this)', 'pcallcontext_caller.RECEIVER = (n_this)',
        'papiquery.SCOPE = pcallcontext_caller.LEXICAL_CLASS',
        '$api_query_valid(S,papiquery,0)',
        '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)', 'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER =/= porigin_class', 'pcallcontext_caller.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        '$magic_method_this_array_from_callable_producer(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_from_callable_producer(S,porigin_outer,expression_outer) = eps',
        '$magic_method_this_source(S,pmagicmethodcall.CALLER,pconfigcall.SITE,$ptascii("capture"),phpType7_real*) = eps',
        '$magic_method_this_array_source(S,pmagicmethodcall.CALLER,pconfigcall.SITE,$ptascii("capture"),phpType7_real*) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_array_source(S,eps,pconfigcall.SITE,$ptascii("capture"),phpType7_real*) = eps',
        '$magic_method_context_call(expression_outer)',
        '$magic_method_context_source(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer)',
        '~$magic_method_context_source(S,eps,porigin_outer,expression_outer)',
        '$lookup($global_table_view(S).ENV,$ptascii("runner")) = (n_runner_cell)', 'S.STORE[n_runner_cell] = DEFINED PNULL',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_this]',
        '$heap_owners($heap_graph(S),HARRAY n_callback) = 1', '$heap_owners($heap_graph(S),HOBJECT n_this) = 2',
        'n_wrapper = |S.OBJECTS|', 'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'pfrommethod.ARRAY', 'pfrommethod.STATIC', '~pfrommethod.INVOKE', 'pfrommethod.FUNCTION = pfunction.ORIGIN',
        'pfrommethod.INPUT = POBJECT n_this', 'pfrommethod.CLASS.RECEIVER = (n_this)',
        '$from_receiver(pfrommethod) = eps', '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        'S_ready_found = $thisstaticarray228_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $thisstaticarray228_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)', '$heap_owners($heap_graph(S_ready),HOBJECT n_this) = 1',
        '$from_selected(S_ready,pfrommethod) = (pmethoddesc)', '$from_valid(S_ready,pfrommethod)',
        '$factory182_output(S_ready.EVENTS) = $ptascii("FIRST;")',
        'S_body_found = $thisstaticarray228_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
        'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_body.CALLED_CLASS = (porigin_class)', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_count(HOBJECT n_this,$frames_roots(S_body.FRAMES)) = 1', '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 1',
        '$call_current_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)', 'n_old =/= n_this',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_send_found = $thisstaticarray228_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'), 'pmagicmethodcall_send = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 1',
        '$magic_method_this_array_from_callable_producer(S_send,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("FIRST;SHIFT;CAPTURE:CallerBase228:CallerChild228;")',
        'S_after_found = $thisstaticarray228_after_seek(S_send,2048)', 'S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', AFTER.replace('S.', 'S_after.'),
        '~((HOBJECT n_this) <- S_after.ALLOCATIONS)', '$heap_owners($heap_graph(S_after),HOBJECT n_this) = 0',
        '$object_class_origin(S_after,n_this) = (porigin_class)', '$from_selected(S_after,pfrommethod) = (pmethoddesc)',
        '$from_valid(S_after,pfrommethod)',
        '$magic_method_this_array_from_callable_producer(S_after,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
    ]


def render(case, fixture, filename):
    checks = ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROWS[CASE]['source']}},
                 extra_inputs=(CATALOGUE, Path(__file__), Path(previous.__file__),
                               Path(previous.names.__file__), ROOT / 'tests/semantics/profile.json'),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())
