#!/usr/bin/env python3
"""Initial reference array CELL, actual SEND/COW and returned-child ownership."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_refarray_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-refarray-instance-cow'
RAW = 'S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin_site? z) :: ptask_capturetail*'
PRE = ('S.TODO = (STMT (NStmtExpression (NExprAssign (NExprArrayDimFetch (NExprVariable (BYTES text_alias_pre) metadata_alias_pre) (NScalarInt (INTEGER 0) metadata_key_pre) metadata_dim_pre) (NScalarInt (INTEGER 99) metadata_rhs_pre) metadata_assign_pre) metadata_stmt_pre)) :: ptask_pre_tail* '
       '-- if $base64(text_alias_pre) = $ptascii("alias") -- if S.CURRENT = (pcallcontext_pre)')
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'MAGIC_METHOD_TARGET pmagicmethodcall n_arguments pvalue*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_return_string])) metadata_return_echo)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)
for label, front in [('raw', RAW), ('pre', PRE), ('return', RETURN)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$refarray199_' + label + '_')
PREFIX += r'''
dec $refarray199_sent_one(ptask) : (pmagicmethodcall, nat)?
def $refarray199_sent_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 1 ([KNOWN (PARRAY n)]) porigin? z) = ((pmagicmethodcall,n))
def $refarray199_sent_one(ptask) = eps -- otherwise
dec $refarray199_sent(ptask*) : (pmagicmethodcall, nat)?
def $refarray199_sent(eps) = eps
def $refarray199_sent(ptask :: ptask_tail*) = ((pmagicmethodcall,n))
  -- if $refarray199_sent_one(ptask) = ((pmagicmethodcall,n))
def $refarray199_sent(ptask :: ptask_tail*) = $refarray199_sent(ptask_tail*)
  -- if $refarray199_sent_one(ptask) = eps
'''


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.FUNCTIONS = [pfunction_shift]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_raw_found = $refarray199_raw_seek(S_initial,2048)',
        'S_raw_found.COMPLETION = BUDGET', 'S_raw = S_raw_found[.COMPLETION = NORMAL]',
        RAW.replace('S.TODO', 'S_raw.TODO'),
        r'pmagicmethodcall.ARGUMENTS = phpType7* /\ |phpType7*| = 2',
        r'porigin_site? = (pmagicmethodcall.SITE) /\ z = pmagicmethodcall.LINE',
        'ptask_capturetail* = METHOD_RESULT :: pmagicmethodcall.TAIL',
        '$lookup(S_raw.ENV,$ptascii("values")) = (n_input_cell)',
        '$lookup(S_raw.ENV,$ptascii("alias")) = (n_input_cell)',
        'n_input_cell <- S_raw.REFCELLS',
        'S_raw.STORE[n_input_cell] = DEFINED (PARRAY n_old_array)',
        '$node_children(S_raw,HCELL n_input_cell) = [HARRAY n_old_array]',
        '$node_children(S_raw,HARRAY n_old_array) = [HOBJECT n_old]',
        'S_raw.ARRAYS[n_old_array] = $magic_method_array([PINT 7,POBJECT n_old],0)',
        '$heap_owners($heap_graph(S_raw),HCELL n_input_cell) = 2',
        '$heap_owners($heap_graph(S_raw),HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_old) = 1',
        '$magic_method_array_capture(S_raw,pmagicmethodcall.ARGUMENTS)',
        '$magic_method_capture(S_raw,pmagicmethodcall)',
        '~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0)',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        '~$magic_method_descriptor(S_raw,pmagicmethodcall[.ARGUMENTS = eps])',
        '~$magic_method_caller(S_raw,pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)])',
        '~$magic_method_flat_entries(S_raw,[ENTRY (KINT 0) (ALIAS n_input_cell)])',
        'S_pre_found = $refarray199_pre_seek(S_raw,2048)',
        'S_pre_found.COMPLETION = BUDGET', 'S_pre = S_pre_found[.COMPLETION = NORMAL]',
        PRE.replace('S.', 'S_pre.'),
        'pcallcontext_pre.FUNCTION = pfunction_shift.ORIGIN',
        'S_pre.FRAMES = [pframe_pre]',
        '$refarray199_sent(pframe_pre.TODO) = ((pmagicmethodcall,n_old_array))',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PARRAY n_old_array)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe_pre.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT,HARRAY n_old_array]',
        '$magic_method_descriptor(S_pre,pmagicmethodcall)',
        'pframe_pre.CONTEXT = pmagicmethodcall.CALLER',
        '$call_argument_origin(S_pre,(pmagicmethodcall.SITE),1) = pframe_pre.ORIGIN',
        '$lookup(S_pre.ENV,$ptascii("alias")) = (n_input_cell)',
        'S_pre.STORE[n_input_cell] = DEFINED (PARRAY n_old_array)',
        '$node_children(S_pre,HCELL n_input_cell) = [HARRAY n_old_array]',
        '$heap_owners($heap_graph(S_pre),HARRAY n_old_array) = 2',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_pre),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$call_descriptors_valid(S_pre)', '$heap_valid($heap_graph(S_pre))',
        'S_found = $factory182_seek(S_pre,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        '$lookup($global_table_view(S).ENV,$ptascii("values")) = (n_input_cell)',
        '$lookup($global_table_view(S).ENV,$ptascii("alias")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_current_array)',
        'n_old_array =/= n_current_array',
        '$node_children(S,HCELL n_input_cell) = [HARRAY n_current_array]',
        '$node_children(S,HARRAY n_current_array) = [HOBJECT n_new]',
        'S.ARRAYS[n_current_array] = $magic_method_array([PINT 99,POBJECT n_new],0)',
        'n_old =/= n_new',
        'pvalue* = [PARRAY n_old_array,PINT 9]',
        '$lookup(S.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S.ARRAYS[n_arguments] = $magic_method_array(pvalue*,0)',
        '$node_children(S,HARRAY n_arguments) = [HARRAY n_old_array]',
        'S.ARRAYS[n_old_array] = $magic_method_array([PINT 7,POBJECT n_old],0)',
        '$heap_owners($heap_graph(S),HCELL n_input_cell) = 2',
        '$heap_owners($heap_graph(S),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_current_array) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        'S.FRAMES = pframe :: pframe_tail*',
        '$magic_method_frame(S,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,pvalue*)',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_return_found = $refarray199_return_seek(S,4096)',
        'S_return_found.COMPLETION = BUDGET', 'S_return = S_return_found[.COMPLETION = NORMAL]',
        RETURN.replace('S.', 'S_return.'),
        'S_return.FRAMES = eps',
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_return.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$node_children(S_return,HOBJECT n_child) = [HARRAY n_old_array]',
        '$node_children(S_return,HCELL n_input_cell) = [HARRAY n_current_array]',
        '$heap_owners($heap_graph(S_return),HARRAY n_old_array) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_current_array) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_new) = 1',
        '~((HARRAY n_arguments) <- S_return.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;OWNER;")',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HCELL n_input_cell) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_old_array) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_current_array) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
