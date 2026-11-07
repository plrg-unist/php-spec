#!/usr/bin/env python3
"""Static CV selection stamps nonowning history before reference-cell mutation."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_static_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-cv-static-ref-selector-rebound'
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_real* false false z_read) :: ptask_read_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("reference")) z_cv -- if S.ORIGIN = (porigin_producer) -- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (STATIC_METHOD_TARGET porigin_class_ready porigin_method_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("CAPTURE:") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('ready', READY), ('body', BODY), ('send', SEND)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvstatic232_' + label + '_')
PREFIX += r'''
dec $cvstatic232_outer_one(ptask) : pmagicmethodcall?
def $cvstatic232_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $cvstatic232_outer_one(ptask) = eps -- otherwise
dec $cvstatic232_outer(ptask*) : pmagicmethodcall?
def $cvstatic232_outer(eps) = eps
def $cvstatic232_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvstatic232_outer_one(ptask) = (pmagicmethodcall)
def $cvstatic232_outer(ptask :: ptask_tail*) = $cvstatic232_outer(ptask_tail*) -- if $cvstatic232_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        '$cvstatic232_outer(ptask_read_tail*) = (pmagicmethodcall_initial)', 'pmagicmethodcall_initial.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall_initial.SITE),0) = (porigin_producer)',
        '$origin_node(S_read.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprMethodCall (NExprVariable (BYTES text_cv) metadata_cv) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_real*) metadata',
        '$base64(text_cv) = $ptascii("reference")', '$base64(text_method) = $ptascii("capture")', '|phpType7_real*| = 2',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)', 'z_read = $runtime_line(S_read,eps,expression_producer)',
        '$lookup(S_read.ENV,$ptascii("reference")) = (n_receiver_cell)',
        '$lookup(S_read.ENV,$ptascii("selector")) = (n_receiver_cell)', 'n_receiver_cell <- S_read.REFCELLS',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_selector)',
        '$magic_producer_cell(S_read,$ptascii("reference")) = (n_selector)',
        '$object_class_origin(S_read,n_selector) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_producer,porigin_class) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION', 'pmethoddesc.STATIC', 'pmethoddesc.OWNER =/= porigin_class',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("capture"),phpType7_real*,z_read)',
        '$method_selected_metadata(S_read,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN,eps) = S_read',
        'S_bad = S_read[.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_real* false false z_read) :: METHOD_RESULT :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial) eps 1 eps (pmagicmethodcall_initial.SITE) pmagicmethodcall_initial.LINE) :: METHOD_RESULT :: pmagicmethodcall_initial.TAIL]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_producer)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_producer) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$ptascii("capture"),phpType7_real*,z_read)',
        'S_bad_selected = $method_selected_metadata(S_bad,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN,(porigin_producer))',
        'S_bad_selected.COMPLETION = UNSUPPORTED "magic method producer selection fact"', 'S_bad_selected.TODO = S_bad.TODO',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        '$cvstatic232_outer(S_selected.TODO) = (pmagicmethodcall)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_class,METHOD pfunction.ORIGIN}',
        'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact])',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_selector) = 1',
        'S_ready_found = $cvstatic232_ready_seek(S_selected[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $cvstatic232_ready_seek(S_read,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'porigin_class_ready = porigin_class', 'porigin_method_ready = pfunction.ORIGIN',
        'porigin_ready = porigin_producer', 'phpType7_ready* = phpType7_real*',
        '$cvstatic232_outer(ptask_ready_tail*) = (pmagicmethodcall)',
        '$target_nodes(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_instance(STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$target_receiver(S_ready,STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN) = eps',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_selector) = 1',
        '$factory182_output(S_ready.EVENTS) = eps',
        'S_body_found = $cvstatic232_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = STATIC_METHOD_TARGET porigin_class pfunction.ORIGIN',
        'pcallcontext_body.INSTANCE = eps', 'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (pmethoddesc.OWNER)', 'pcallcontext_body.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_body.CURRENT) = eps',
        '~((HOBJECT n_selector) <- S_body.ALLOCATIONS)', '$heap_owners($heap_graph(S_body),HOBJECT n_selector) = 0',
        'S_body.STORE[n_receiver_cell] = DEFINED (POBJECT n_replacement)', 'n_replacement =/= n_selector',
        '$object_class_origin(S_body,n_replacement) = (porigin_replacement)',
        '$magic_producer_selected_source(S_body,porigin_producer,porigin_replacement) = eps',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)', '$heap_valid($heap_graph(S_body))',
        'S_send_found = $cvstatic232_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'), 'pmagicmethodcall_send = pmagicmethodcall',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],[pmagicproducerfact]) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("SELECTOR-END;SHIFT;CAPTURE:SelectorBase232:SelectorChild232;")',
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
