#!/usr/bin/env python3
"""A first literal array is owned by the pending send while later code runs."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_array_literal_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-array-literal-instance-transient'
FRONT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_tail* '
         '-- if $base64(text_marker) = $ptascii("SHIFT;") '
         '-- if S.CURRENT = (pcallcontext)')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $literal196_send_one(ptask) : (pmagicmethodcall, nat)?
def $literal196_send_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PARRAY n)]) porigin? z) = ((pmagicmethodcall,n))
def $literal196_send_one(ptask) = eps -- otherwise
dec $literal196_send(ptask*) : (pmagicmethodcall, nat)?
def $literal196_send(eps) = eps
def $literal196_send(ptask :: ptask_tail*) = ((pmagicmethodcall,n))
  -- if $literal196_send_one(ptask) = ((pmagicmethodcall,n))
def $literal196_send(ptask :: ptask_tail*) = $literal196_send(ptask_tail*)
  -- if $literal196_send_one(ptask) = eps
'''


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'P.FUNCTIONS = [pfunction_shift]',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pfunction_shift.ORIGIN',
        'pcallcontext.TARGET = pfunction_shift.ORIGIN',
        'pcallcontext.ARGC = 0', 'pcallcontext.RECEIVER = eps',
        '$call_context_roots(S.CURRENT) = eps',
        'S.FRAMES = pframe :: pframe_tail*',
        '$literal196_send(pframe.TODO) = ((pmagicmethodcall,n_literal))',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PARRAY n_literal)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.CLASS = pclassdesc_called.ORIGIN',
        'pmagicmethodcall.ARGUMENTS = [phpType7_literal,phpType7_later]',
        'phpType7_literal = NArg phpType3_name (NExprArray (SEQUENCE phpType13*) metadata_array) (BOOLEAN false) (BOOLEAN false) metadata_literal',
        '$magic_method_array_source(pmagicmethodcall.ARGUMENTS)',
        '$magic_method_array_cv(pmagicmethodcall.ARGUMENTS) = eps',
        '$magic_method_literal_entries(phpType13*)',
        '$magic_method_flat_array(S,n_literal)',
        '$node_children(S,HARRAY n_literal) = [HOBJECT n_old]',
        'S.ARRAYS[n_literal] = $magic_method_array([PINT 7,POBJECT n_old],0)',
        'S.OBJECTS[n_old] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_old) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_literal) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT,HARRAY n_literal]',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.OBJECTS[pmagicmethodcall.OBJECT] = INSTANCE pclassdesc_called.ORIGIN',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S).ENV,$ptascii("replacement")) = (n_new_cell)',
        'S.STORE[n_new_cell] = DEFINED (POBJECT n_new)',
        'n_old =/= n_new',
        'S.OBJECTS[n_new] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_new) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_new) = 1',
        '$factory182_output(S.EVENTS) = eps',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        '$magic_method_call_values(S,pmagicmethodcall.ARGUMENTS,[KNOWN (PARRAY n_literal),KNOWN (PINT 9)]) = ([PARRAY n_literal,PINT 9])',
        '$magic_method_call_values(S,[phpType7_later,phpType7_literal],[KNOWN (PARRAY n_literal),KNOWN (PINT 9)]) = eps',
        '$magic_method_call_values(S,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9),KNOWN (PARRAY n_literal)]) = eps',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HARRAY n_literal) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
