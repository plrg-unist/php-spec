#!/usr/bin/env python3
"""Actual magic-call factory frame, snapshot array and returned payload owners."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_magic_argument_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-call-delayed-argument-child-return'
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'MAGIC_METHOD_TARGET pmagicmethodcall n_arguments pvalue*')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        'S.OBJECTS[pmagicmethodcall.OBJECT] = INSTANCE pclassdesc_called.ORIGIN',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PINT 99)',
        'pvalue* = [PINT 7,POBJECT n_payload]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S.ARRAYS[n_arguments] = $magic_method_array(pvalue*,0)',
        '(HARRAY n_arguments) <- S.ALLOCATIONS',
        '$node_children(S,HARRAY n_arguments) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
        'S.OBJECTS[n_payload] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_payload) = eps',
        '$magic_method_value(S,POBJECT n_payload)',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_method_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,pvalue*)',
        '$call_receiver_roots(pcallcontext) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.ORIGIN = (porigin_new)',
        '$origin_child((porigin_new),[PCFIELD 0]) = (pclassdesc_child.ORIGIN)',
        '$anonymous_new_name(S,porigin_new) = (pclassdesc_child.NAME)',
        '$factory182_output(S.EVENTS) = $ptascii("CLEAR;MAGIC;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$magic_method_frame(S,pcallcontext[.CALLED_CLASS = (pclassdesc_base.ORIGIN)],pframe,pframe_tail*,pmagicmethodcall,n_arguments,pvalue*)',
        '~$magic_method_frame(S,pcallcontext,pframe[.ORIGIN = (pclassdesc_child.ORIGIN)],pframe_tail*,pmagicmethodcall,n_arguments,pvalue*)',
        'S_split = $drive_steps(S,3)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,8195)', 'S_full = S_done',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
