#!/usr/bin/env python3
"""A reference-CV SEND owns the copied object, never the caller's wrapper."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_refcell_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-refcell-instance-rebound'
RAW = 'S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin_site? z) :: ptask_capturetail*'
LATER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_later_tail* '
         '-- if $base64(text_marker) = $ptascii("CLEAR;") -- if S.CURRENT = (pcallcontext_later)')
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'MAGIC_METHOD_TARGET pmagicmethodcall n_arguments pvalue*')
HELD = ('S.TODO = (STMT (NStmtEcho (SEQUENCE expression_held*) metadata_held_echo)) :: ptask_held_tail* '
        '-- if expression_held* = (NScalarString (BYTES text_held) metadata_held) :: expression_held_tail* '
        '-- if $base64(text_held) = $ptascii("HELD:")')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)
for label, front in [('raw', RAW), ('later', LATER), ('held', HELD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$refcell198_' + label + '_')
PREFIX += r'''
dec $refcell198_sent_one(ptask) : (pmagicmethodcall, poperand*)?
def $refcell198_sent_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 1 poperand* porigin? z) = ((pmagicmethodcall,poperand*))
def $refcell198_sent_one(ptask) = eps -- otherwise
dec $refcell198_sent(ptask*) : (pmagicmethodcall, poperand*)?
def $refcell198_sent(eps) = eps
def $refcell198_sent(ptask :: ptask_tail*) = ((pmagicmethodcall,poperand*))
  -- if $refcell198_sent_one(ptask) = ((pmagicmethodcall,poperand*))
def $refcell198_sent(ptask :: ptask_tail*) = $refcell198_sent(ptask_tail*)
  -- if $refcell198_sent_one(ptask) = eps
'''


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.FUNCTIONS = [pfunction_later]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_raw_found = $refcell198_raw_seek(S_initial,2048)',
        'S_raw_found.COMPLETION = BUDGET', 'S_raw = S_raw_found[.COMPLETION = NORMAL]',
        RAW.replace('S.TODO', 'S_raw.TODO'),
        r'pmagicmethodcall.ARGUMENTS = phpType7* /\ |phpType7*| = 2',
        r'porigin_site? = (pmagicmethodcall.SITE) /\ z = pmagicmethodcall.LINE',
        'ptask_capturetail* = METHOD_RESULT :: pmagicmethodcall.TAIL',
        '$lookup(S_raw.ENV,$ptascii("argument")) = (n_input_cell)',
        '$lookup(S_raw.ENV,$ptascii("alias")) = (n_input_cell)',
        'n_input_cell <- S_raw.REFCELLS',
        'S_raw.STORE[n_input_cell] = DEFINED (POBJECT n_payload)',
        '$node_children(S_raw,HCELL n_input_cell) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S_raw),HCELL n_input_cell) = 2',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_payload) = 1',
        '$magic_method_cv_capture(S_raw,n_input_cell)',
        '$magic_method_capture(S_raw,pmagicmethodcall)',
        '~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0)',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        '~$magic_method_cv_capture(S_raw[.STORE = $set_cell(S_raw.STORE,n_input_cell,DEFINED (PINT 7))],n_input_cell)',
        '~$magic_method_cv_capture(S_raw[.STORE = $set_cell(S_raw.STORE,n_input_cell,DEFINED (PSTRING $ptascii("text")))],n_input_cell)',
        '~$magic_method_cv_capture(S_raw[.STORE = $set_cell(S_raw.STORE,n_input_cell,DEFINED (PARRAY 0))],n_input_cell)',
        '~$magic_method_caller(S_raw,pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)])',
        '~$magic_method_descriptor(S_raw,pmagicmethodcall[.CLASS = pclassdesc_base.ORIGIN])',
        '~$magic_method_descriptor(S_raw,pmagicmethodcall[.ARGUMENTS = eps])',
        'S_later_found = $refcell198_later_seek(S_raw,2048)',
        'S_later_found.COMPLETION = BUDGET', 'S_later = S_later_found[.COMPLETION = NORMAL]',
        LATER.replace('S.', 'S_later.'),
        'pcallcontext_later.FUNCTION = pfunction_later.ORIGIN',
        'S_later.FRAMES = [pframe_later]',
        '$refcell198_sent(pframe_later.TODO) = ((pmagicmethodcall,[KNOWN (POBJECT n_payload)]))',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_payload)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe_later.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT,HOBJECT n_payload]',
        '$magic_method_descriptor(S_later,pmagicmethodcall)',
        'pframe_later.CONTEXT = pmagicmethodcall.CALLER',
        '$call_argument_origin(S_later,(pmagicmethodcall.SITE),1) = pframe_later.ORIGIN',
        '$lookup($global_table_view(S_later).ENV,$ptascii("argument")) = (n_input_cell)',
        '$lookup($global_table_view(S_later).ENV,$ptascii("alias")) = (n_input_cell)',
        'S_later.STORE[n_input_cell] = DEFINED (POBJECT n_replacement)',
        'n_payload =/= n_replacement',
        '$node_children(S_later,HCELL n_input_cell) = [HOBJECT n_replacement]',
        '$heap_owners($heap_graph(S_later),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S_later),HOBJECT n_replacement) = 1',
        '$heap_owners($heap_graph(S_later),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$call_descriptors_valid(S_later)', '$heap_valid($heap_graph(S_later))',
        'S_found = $factory182_seek(S_later,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_input_cell)',
        '$lookup($global_table_view(S).ENV,$ptascii("alias")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (POBJECT n_replacement)',
        '$heap_owners($heap_graph(S),HCELL n_input_cell) = 2',
        '$node_children(S,HCELL n_input_cell) = [HOBJECT n_replacement]',
        'pvalue* = [POBJECT n_payload,PINT 9]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S.ARRAYS[n_arguments] = $magic_method_array(pvalue*,0)',
        '$node_children(S,HARRAY n_arguments) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_replacement) = 1',
        '$call_receiver_roots(pcallcontext) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_method_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,pvalue*)',
        '$factory182_output(S.EVENTS) = $ptascii("CLEAR;MAGIC;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_held_found = $refcell198_held_seek(S,4096)',
        'S_held_found.COMPLETION = BUDGET', 'S_held = S_held_found[.COMPLETION = NORMAL]',
        HELD.replace('S.TODO', 'S_held.TODO'),
        '$lookup(S_held.ENV,$ptascii("argument")) = eps',
        '$lookup(S_held.ENV,$ptascii("alias")) = eps',
        '~((HCELL n_input_cell) <- S_held.ALLOCATIONS)',
        '~((HOBJECT n_replacement) <- S_held.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_held.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_held.ALLOCATIONS)',
        '$lookup(S_held.ENV,$ptascii("child")) = (n_child_cell)',
        'S_held.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_held.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$node_children(S_held,HOBJECT n_child) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S_held),HOBJECT n_payload) = 1',
        '$factory182_output(S_held.EVENTS) = $ptascii("CLEAR;MAGIC;CHILD;OWNER;RETURN;ALIAS:new;ARG(new);")',
        '$call_descriptors_valid(S_held)', '$heap_valid($heap_graph(S_held))',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
