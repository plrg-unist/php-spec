#!/usr/bin/env python3
"""Function CV acquisition survives callee rebinding and FCC retirement."""
import argparse
import json
from pathlib import Path

import anonymous_function_string_callable_producer_magic_protocol as literal
import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_function_cv_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_function_cv_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-function-cv-direct-return-old', 'magic-function-cv-fcc-return-old')
UNPACK = 'magic-function-cv-nullary-unpack-refused'


def seeker(label, front):
    return literal.PREFIX[literal.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$functioncv247_' + label + '_')


def ownership(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    front = ('S.TODO = (' + ('FIRSTCLASS_CONVERT porigin_capture z_init z_capture' if fcc else 'CALL_DYNAMIC porigin_capture z_init z_call')
             + ') :: ptask_read_tail* -- if S.CURRENT = eps -- if S.RESULT = VARIABLE ($ptascii("producer")) z_cv -- if S.ORIGIN = (porigin_capture)')
    prefix = literal.PREFIX.replace(names.FRONT, front) + direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
    for label, stop in [('ready', literal.READY), ('body', literal.BODY), ('send', literal.SEND)]:
        prefix += seeker(label, stop)
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', front,
        '$newinvoke236_outer(S.TODO) = (pmagicmethodcall_initial)', 'pmagicmethodcall_initial.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall_initial.SITE),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer', '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_producer_cv_parts(S,porigin_producer,expression_producer) = ((porigin_capture,S.RESULT,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
        'phpType7_real* = [phpType7_first,phpType7_second]', 'phpType7_first =/= phpType7_second',
        'porigin_capture = PORIGIN n_unit pcpath_capture',
        '$origin_node(S.SOURCES,porigin_capture) = (NExprFuncCall expression_cv (SEQUENCE phpType7_capture*) metadata_capture)',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv', '$base64(text_cv) = $ptascii("producer")',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_name(pcode.NAMES,pcpath_capture) = eps', '$code_call_init(pcode.EXPRESSIONS,pcpath_capture) = (z_init)',
        '$source_emission_cv(S,n_unit,pcpath_capture ++ [PCFIELD 0],expression_cv)',
        '$compiled_read(S,PORIGIN n_unit (pcpath_capture ++ [PCFIELD 0])) = eps',
        '$lookup(S.ENV,$ptascii("producer")) = (n_callee_cell)', 'S.STORE[n_callee_cell] = DEFINED pvalue_name',
        '$string_bytes(pvalue_name) = (ptbytes_original)', 'ptbytes_original = 92 :: ptbytes_lookup',
        '$magic_producer_cell(S,$ptascii("producer")) = eps', '$magic_producer_function_cell(S,$ptascii("producer")) = (pfunction)',
        '$call_target(S,$dynamic_lookup_name(ptbytes_original),eps) = (pfunction)', 'porigin_function = pfunction.ORIGIN',
        '$magic_producer_function_source(S,porigin_producer,porigin_function)',
        '$magic_producer_function_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS eps,METHOD porigin_function}',
        '$magic_producer_fact_source(S,pmagicproducerfact)',
        '~$magic_producer_fact_source(S,pmagicproducerfact[.CLASS = (porigin_function)])',
        '~$magic_producer_fact_source(S,pmagicproducerfact[.METHOD = pmagicmethodcall_initial.METHOD])',
        '~$magic_producer_fact_source(S[.SOURCES = eps],pmagicproducerfact)',
        '~$magic_producer_fact_source(S[.CALLABLES = eps],pmagicproducerfact)',
        '~$magic_producer_fact_source(S[.FUNCTIONS = [pfunction[.SIGNATURE.BYREF = true]]],pmagicproducerfact)',
        '~$magic_producer_fact_source(S[.FUNCTIONS = [pfunction[.SIGNATURE.PARAMETERS = eps]]],pmagicproducerfact)',
        '~$magic_producer_function_read(S[.STORE[n_callee_cell] = DEFINED PNULL],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_function_read(S[.ENV = eps],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_function_read(S[.LITERALREFDEBTS = [n_callee_cell]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_function_read(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_capture)]]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_function_read(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_capture ptbytes_lookup eps]]]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        '$newinvoke236_outer(S_selected.TODO) = (pmagicmethodcall)', 'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact])',
        '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact,pmagicproducerfact])',
        '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact],0)',
        '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
    ]
    if fcc:
        checks += [
            'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]', 'n_callee_cell <- S.REFCELLS',
            'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
            'n_wrapper = |S.OBJECTS|', 'S_selected.OBJECTS = S.OBJECTS ++ [NAMEDCLOSURE porigin_function]',
            '$node_children(S_selected,HOBJECT n_wrapper) = eps', 'pcalltarget = CLOSURE_TARGET n_wrapper',
            '~$magic_producer_function_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],porigin_producer,porigin_function)',
        ]
    else:
        checks += ['phpType7_capture* = phpType7_real*', '~(n_callee_cell <- S.REFCELLS)', 'porigin_capture = porigin_producer', 'pcalltarget = porigin_function']
    checks += [
        'S_ready = $functioncv247_ready_seek(S_selected,2048)', 'S_ready.COMPLETION = BUDGET', literal.at(literal.READY, 'S_ready'),
        'pcalltarget_ready = pcalltarget', 'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        '$target_receiver(S_ready,pcalltarget) = eps', '$target_lexical_class(S_ready,pcalltarget) = eps', '$target_called_class(S_ready,pcalltarget) = eps',
        'S_body_found = $functioncv247_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', literal.at(literal.BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$call_context_roots(S_body.CURRENT) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)', 'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        '$magic_producer_fact_source(S_body,pmagicproducerfact)',
        'S_send_found = $functioncv247_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', literal.at(literal.SEND, 'S_send'),
        'pmagicmethodcall_send = pmagicmethodcall', 'n_send = n_old', '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;CAPTURE;")',
        '$magic_producer_fact_source(S_send,pmagicproducerfact)', '$magic_producer_function_cell(S_send,$ptascii("producer")) =/= (pfunction)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],[pmagicproducerfact]) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)', '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
        'S_sent.RESULT = KNOWN PNULL', '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
        '$heap_count(HOBJECT n_old,$tasks_nodes(S_sent.TODO)) = 1', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]
    if fcc:
        checks += ['$lookup(S_send.ENV,$ptascii("producer")) = eps', '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)']
    return prefix, checks


def unpack(fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', literal.BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)', '$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)', '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,128)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]
    return literal.PREFIX.replace(names.FRONT, literal.BOUNDARY), checks


def render(case, fixture, filename):
    prefix, checks = unpack(fixture, filename) if case['id'] == UNPACK else ownership(case, fixture, filename)
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=(*CASES, UNPACK))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or (*CASES, UNPACK))},
                 (Path(__file__), CATALOGUE, CONTROLS, Path(literal.__file__), Path(literal.method.__file__), Path(direct.__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
