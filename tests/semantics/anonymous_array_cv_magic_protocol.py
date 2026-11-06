#!/usr/bin/env python3
"""First array CV snapshot, generic COW, captured storage and payload ownership."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_array_cv_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-array-cv-instance-cow-snapshot'
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'MAGIC_METHOD_TARGET pmagicmethodcall n_arguments pvalue*')
RAW = ('S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin_site? z) :: ptask_capturetail*')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $array195_raw_front(pstate) : bool
def $array195_raw_front(S) = true -- if RAW
def $array195_raw_front(S) = false -- otherwise
dec $array195_raw_seek(pstate, nat) : pstate
def $array195_raw_seek(S, 0) = S
def $array195_raw_seek(S, n) = S -- if $(n > 0) /\ $array195_raw_front(S)
def $array195_raw_seek(S, n) = $array195_raw_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$array195_raw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $array195_raw_seek(S, n) = S -- otherwise
'''.replace('RAW', RAW)


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
        'S_raw_found = $array195_raw_seek(S_initial,2048)',
        'S_raw_found.COMPLETION = BUDGET', 'S_raw = S_raw_found[.COMPLETION = NORMAL]',
        RAW.replace('S.TODO','S_raw.TODO'),
        r'pmagicmethodcall.ARGUMENTS = phpType7* /\ |phpType7*| = 2',
        r'porigin_site? = (pmagicmethodcall.SITE) /\ z = pmagicmethodcall.LINE',
        'ptask_capturetail* = METHOD_RESULT :: pmagicmethodcall.TAIL',
        '$lookup(S_raw.ENV,$ptascii("values")) = (n_input_cell)',
        'S_raw.STORE[n_input_cell] = DEFINED (PARRAY n_snapshot)',
        '~(n_input_cell <- S_raw.REFCELLS)',
        '$magic_method_capture(S_raw,pmagicmethodcall)',
        '$magic_method_array_capture(S_raw,pmagicmethodcall.ARGUMENTS)',
        '$magic_method_flat_array(S_raw,n_snapshot)',
        '$node_children(S_raw,HARRAY n_snapshot) = [HOBJECT n_payload]',
        'S_raw.ARRAYS[n_snapshot] = $magic_method_array([PINT 7,POBJECT n_payload],0)',
        '$heap_owners($heap_graph(S_raw),HARRAY n_snapshot) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_payload) = 1',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        'S_found = $factory182_seek(S_raw,4096)',
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
        '$lookup($global_table_view(S).ENV,$ptascii("values")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_root)',
        'n_input_cell <- S.REFCELLS',
        'n_snapshot =/= n_root',
        '$node_children(S,HARRAY n_root) = [HOBJECT n_replacement]',
        'S.ARRAYS[n_root] = $magic_method_array([PINT 99,POBJECT n_replacement],0)',
        '$heap_owners($heap_graph(S),HARRAY n_root) = 1',
        'n_payload =/= n_replacement',
        'S.OBJECTS[n_replacement] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_replacement) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_replacement) = 1',
        'pvalue* = [PARRAY n_snapshot,PINT 9]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S.ARRAYS[n_arguments] = $magic_method_array(pvalue*,0)',
        '(HARRAY n_arguments) <- S.ALLOCATIONS',
        '$node_children(S,HARRAY n_arguments) = [HARRAY n_snapshot]',
        'S.ARRAYS[n_snapshot] = $magic_method_array([PINT 7,POBJECT n_payload],0)',
        '$node_children(S,HARRAY n_snapshot) = [HOBJECT n_payload]',
        '$heap_owners($heap_graph(S),HARRAY n_snapshot) = 1',
        '$magic_method_call_values(S,pmagicmethodcall.ARGUMENTS,(KNOWN pvalue)*) = (pvalue*)',
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
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_later]',
        'phpType7_later = NArg phpType3_later expression_later (BOOLEAN false) (BOOLEAN false) metadata_later',
        'phpType7_unpack = NArg phpType3_later expression_later (BOOLEAN false) (BOOLEAN true) metadata_later',
        '$magic_method_call_values(S,[phpType7_later,phpType7_first],(KNOWN pvalue)*) = eps',
        '$magic_method_call_values(S,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9),KNOWN (PARRAY n_snapshot)]) = eps',
        '$magic_method_array_cv([phpType7_first,phpType7_unpack]) = eps',
        '~$magic_method_flat_array(S,n_arguments)',
        '~$magic_method_array_capture(S_raw[.REFCELLS = S_raw.REFCELLS ++ [n_input_cell]],pmagicmethodcall.ARGUMENTS)',
        '~$magic_method_flat_entries(S,[ENTRY (KINT 0) (ALIAS n_input_cell)])',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_snapshot) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_root) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
