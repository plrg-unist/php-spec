#!/usr/bin/env python3
"""A method-string CV saves requested class and method before argument effects."""
import argparse
import json
from pathlib import Path

import anonymous_function_cv_callable_producer_magic_protocol as function
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_string_cv_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_method_string_cv_callable_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS) for row in json.loads(path.read_text())['cases']}
CASES = ('magic-method-string-cv-direct-return-old', 'magic-method-string-cv-fcc-return-old')
UNPACK = 'magic-method-string-cv-nullary-unpack-refused'
literal, direct, names = function.literal, function.direct, function.names
BODY = literal.BODY.replace('$ptascii("CAPTURE;")', '$ptascii("CAPTURE:")')


def seeker(label, front):
    return literal.PREFIX[literal.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$methodstringcv248_' + label + '_')


def ownership(case, fixture, filename):
    fcc = ROWS[case['id']]['producer_mode'] == 'fcc'
    front = ('S.TODO = (' + ('FIRSTCLASS_CONVERT porigin_capture z_init z_capture' if fcc else 'CALL_DYNAMIC porigin_capture z_init z_call')
             + ') :: ptask_read_tail* -- if S.CURRENT = eps -- if S.RESULT = VARIABLE ($ptascii("producer")) z_cv -- if S.ORIGIN = (porigin_capture)')
    prefix = literal.PREFIX.replace(names.FRONT, front) + direct.PREFIX[direct.PREFIX.index('dec $newinvoke236_outer_one'):]
    for label, stop in [('ready', literal.READY), ('body', BODY), ('send', literal.SEND)]:
        prefix += seeker(label, stop)
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', front,
        '$newinvoke236_outer(S.TODO) = (pmagicmethodcall_initial)', 'pmagicmethodcall_initial.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall_initial.SITE),0) = (porigin_producer)',
        'porigin_producer = PORIGIN n_unit pcpath_producer', '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_producer_cv_parts(S,porigin_producer,expression_producer) = ((porigin_capture,S.RESULT,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
        '|phpType7_real*| = 2', 'porigin_capture = PORIGIN n_unit pcpath_capture',
        '$origin_node(S.SOURCES,porigin_capture) = (NExprFuncCall expression_cv (SEQUENCE phpType7_capture*) metadata_capture)',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv', '$base64(text_cv) = $ptascii("producer")',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]', '$code_name(pcode.NAMES,pcpath_capture) = eps',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_capture) = (z_init)',
        '$source_emission_cv(S,n_unit,pcpath_capture ++ [PCFIELD 0],expression_cv)',
        '$lookup(S.ENV,$ptascii("producer")) = (n_callee)', 'S.STORE[n_callee] = DEFINED pvalue_name',
        '$magic_producer_string_bytes(S,$ptascii("producer")) = (ptbytes_callback)', '$string_bytes(pvalue_name) = (ptbytes_callback)',
        '$method_string_parts(ptbytes_callback) = ((ptbytes_class,ptbytes_method))',
        '$class_named(S.CLASSNAMES,$ptlc($typed_callable_name(ptbytes_class))) = (porigin_class)',
        '$class_at(S.CLASSES,porigin_class) = (pclassdesc)', 'pclassdesc.NAME = $ptascii("ProducerChild248")',
        '$effective_method(S,porigin_class,ptbytes_method,|S.CLASSES|) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'porigin_owner = pmethoddesc.OWNER', 'porigin_owner =/= porigin_class',
        '$class_at(S.CLASSES,porigin_owner) = (pclassdesc_owner)', 'pclassdesc_owner.NAME = $ptascii("ProducerBase248")',
        '$magic_producer_cell(S,$ptascii("producer")) = eps', '$magic_producer_function_cell(S,$ptascii("producer")) = eps',
        '$magic_producer_selected_source(S,porigin_producer,porigin_class) = eps',
        '$magic_producer_static_string_source(S,porigin_producer,porigin_class,porigin_method)',
        '$magic_producer_static_string_read(S,porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_class,METHOD porigin_method}',
        '$magic_producer_fact_source(S,pmagicproducerfact)', '~$magic_producer_fact_source(S,pmagicproducerfact[.CLASS = eps])',
        '$class_named(S.CLASSNAMES,$ptascii("wrong248")) = (porigin_wrong)',
        '$effective_method(S,porigin_wrong,$ptascii("capture"),|S.CLASSES|) = (pmethoddesc_wrong)',
        '~$magic_producer_fact_source(S,pmagicproducerfact[.CLASS = (porigin_wrong)])',
        '~$magic_producer_fact_source(S,pmagicproducerfact[.METHOD = pmethoddesc_wrong.FUNCTION.ORIGIN])',
        '~$magic_producer_static_string_source(S[.CLASSNAMES = eps],porigin_producer,porigin_class,porigin_method)',
        '~$magic_producer_static_string_source(S[.SOURCES = eps],porigin_producer,porigin_class,porigin_method)',
        '~$magic_producer_static_string_read(S[.ENV = eps],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_static_string_read(S[.STORE[n_callee] = DEFINED PNULL],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_static_string_read(S[.LITERALREFDEBTS = [n_callee]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_static_string_read(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_capture ptbytes_callback eps]]]],porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_capture*)',
        '~$magic_producer_static_string_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_capture)]]],porigin_producer,porigin_class,porigin_method)',
        '$drive_steps(S,0) = S[.COMPLETION = BUDGET]', 'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        '$newinvoke236_outer(S_selected.TODO) = (pmagicmethodcall)', 'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact])',
        '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact,pmagicproducerfact])',
        '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact],0)',
        '$task_nodes(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE) = $task_nodes(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial) eps 0 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE)',
        '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
    ]
    if fcc:
        checks += [
            'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]', 'n_callee <- S.REFCELLS',
            'pvalue_name = PSTRING_CARRIER (REQUEST_STRING n_name) ptbytes_callback',
            'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
            'S_selected.TODO = (STRING_CONVERT pcalltarget_static pstringselection) :: ptask_selected_tail*',
            'pcalltarget_static = STATIC_METHOD_TARGET porigin_class porigin_method',
            'pstringselection.SITE = porigin_capture', 'pstringselection.ORIGINAL = ptbytes_callback',
            '$string_site_valid(S_selected,pstringselection,true)',
            'n_wrapper = |S_selected.OBJECTS|', 'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
            'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [STRINGMETHODCLOSURE pcalltarget_static pstringselection]',
            '$node_children(S_wrapped,HOBJECT n_wrapper) = eps', 'pcalltarget = CLOSURE_TARGET n_wrapper',
            '~$magic_producer_static_string_source(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],porigin_producer,porigin_class,porigin_method)',
        ]
    else:
        checks += ['phpType7_capture* = phpType7_real*', '~(n_callee <- S.REFCELLS)', 'porigin_capture = porigin_producer', 'S_wrapped = S_selected']
    checks += [
        'S_ready = $methodstringcv248_ready_seek(S_wrapped,2048)', 'S_ready.COMPLETION = BUDGET', literal.at(literal.READY, 'S_ready'),
        'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
    ]
    if fcc:
        checks += ['pcalltarget_ready = pcalltarget']
    else:
        checks += ['pcalltarget = pcalltarget_ready', 'pcalltarget = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) pstringselection',
                   'pstringselection.ORIGINAL = ptbytes_callback', 'pstringselection.SITE = porigin_producer', '$string_site_valid(S_ready,pstringselection,false)']
    checks += [
        '$target_function(S_ready,pcalltarget) = (pmethoddesc.FUNCTION)', '$target_receiver(S_ready,pcalltarget) = eps',
        '$target_lexical_class(S_ready,pcalltarget) = (porigin_owner)', '$target_called_class(S_ready,pcalltarget) = (porigin_class)',
        '$target_nodes(pcalltarget) = ' + ('[HOBJECT n_wrapper]' if fcc else 'eps'),
        'S_body_found = $methodstringcv248_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', literal.at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget', 'pcallcontext_body.FUNCTION = porigin_method', 'pcallcontext_body.RECEIVER = eps',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_body.CALLED_CLASS = (porigin_class)',
        'pcallcontext_body.INSTANCE = ' + ('(n_wrapper)' if fcc else 'eps'),
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved)', 'S_body.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument)', 'S_body.STORE[n_argument] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        '$magic_producer_fact_source(S_body,pmagicproducerfact)',
        'S_send_found = $methodstringcv248_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', literal.at(literal.SEND, 'S_send'),
        'pmagicmethodcall_send = pmagicmethodcall', 'n_send = n_old',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;CAPTURE:ProducerBase248/ProducerChild248;")',
        '$magic_producer_fact_source(S_send,pmagicproducerfact)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],[pmagicproducerfact]) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1', 'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1', '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]
    if fcc:
        checks += ['$lookup(S_send.ENV,$ptascii("producer")) = eps', '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)']
    return prefix, checks


def render(case, fixture, filename):
    prefix, checks = function.unpack(fixture, filename) if case['id'] == UNPACK else ownership(case, fixture, filename)
    return prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in checks), len(checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=(*CASES, UNPACK))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in (args.case or (*CASES, UNPACK))},
                 (Path(__file__), CATALOGUE, CONTROLS, Path(function.__file__), Path(literal.__file__), Path(literal.method.__file__), Path(direct.__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
