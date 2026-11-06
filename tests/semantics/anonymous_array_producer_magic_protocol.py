#!/usr/bin/env python3
"""A named maker return transfers its flat array to the pending magic send."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_array_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-array-producer-instance-transient'
FRONT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_tail* '
         '-- if $base64(text_marker) = $ptascii("SHIFT;") '
         '-- if S.CURRENT = (pcallcontext)')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $producer197_send_one(ptask) : (pmagicmethodcall, nat)?
def $producer197_send_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PARRAY n)]) porigin? z) = ((pmagicmethodcall,n))
def $producer197_send_one(ptask) = eps -- otherwise
dec $producer197_send(ptask*) : (pmagicmethodcall, nat)?
def $producer197_send(eps) = eps
def $producer197_send(ptask :: ptask_tail*) = ((pmagicmethodcall,n))
  -- if $producer197_send_one(ptask) = ((pmagicmethodcall,n))
def $producer197_send(ptask :: ptask_tail*) = $producer197_send(ptask_tail*)
  -- if $producer197_send_one(ptask) = eps
'''


RETURN_FRONT = ('S.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_return)) porigin_return?) :: ptask_return_tail* '
                '-- if S.CURRENT = (pcallcontext_return) '
                '-- if $target_function(S,pcallcontext_return.TARGET) = (pfunction_return) '
                '-- if pfunction_return.NAME = $ptascii("make197")')
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, RETURN_FRONT).replace('$factory182_', '$producer197_')
PREFIX += r"""
dec $producer197_target_one(ptask) : pmagicmethodcall?
def $producer197_target_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* n poperand* porigin? z) = (pmagicmethodcall)
def $producer197_target_one(ptask) = eps -- otherwise
dec $producer197_target(ptask*) : pmagicmethodcall?
def $producer197_target(eps) = eps
def $producer197_target(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $producer197_target_one(ptask) = (pmagicmethodcall)
def $producer197_target(ptask :: ptask_tail*) = $producer197_target(ptask_tail*)
  -- if $producer197_target_one(ptask) = eps
"""


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_payload,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        '$ppmethod_call_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'P.FUNCTIONS = [pfunction_make,pfunction_shift]',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_return_found = $producer197_seek(S_initial,4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN_FRONT.replace('S.', 'S_return.').replace('(S,','(S_return,'),
        'pfunction_return = pfunction_make',
        'pcallcontext_return.ARGC = 0', 'pcallcontext_return.RECEIVER = eps',
        '$call_context_roots(S_return.CURRENT) = eps',
        '$lookup(S_return.ENV,$ptascii("local")) = (n_local_cell)',
        'S_return.STORE[n_local_cell] = DEFINED (PARRAY n_return)',
        '$node_children(S_return,HCELL n_local_cell) = [HARRAY n_return]',
        '$node_children(S_return,HARRAY n_return) = [HOBJECT n_return_old]',
        'S_return.ARRAYS[n_return] = $magic_method_array([PINT 7,POBJECT n_return_old],0)',
        '$heap_owners($heap_graph(S_return),HARRAY n_return) = 2',
        '$heap_owners($heap_graph(S_return),HOBJECT n_return_old) = 1',
        'S_return.FRAMES = [pframe_return]',
        '$producer197_target(pframe_return.TODO) = (pmagicmethodcall_return)',
        '$heap_owners($heap_graph(S_return),HOBJECT pmagicmethodcall_return.OBJECT) = 2',
        '$factory182_output(S_return.EVENTS) = $ptascii("MAKER;")',
        '$call_current_valid(S_return)', '$call_descriptors_valid(S_return)',
        '$gc_state_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_found = $factory182_seek(S_return,4096)',
        'S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'n_array = n_return', 'n_old = n_return_old', 'pmagicmethodcall = pmagicmethodcall_return',
        'pcallcontext.FUNCTION = pfunction_shift.ORIGIN',
        'pcallcontext.TARGET = pfunction_shift.ORIGIN',
        'pcallcontext.ARGC = 0', 'pcallcontext.RECEIVER = eps',
        '$call_context_roots(S.CURRENT) = eps',
        'S.FRAMES = pframe :: pframe_tail*',
        '$producer197_send(pframe.TODO) = ((pmagicmethodcall,n_array))',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PARRAY n_array)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.CLASS = pclassdesc_called.ORIGIN',
        'pmagicmethodcall.ARGUMENTS = [phpType7_maker,phpType7_later]',
        'phpType7_maker = NArg phpType3_name (NExprFuncCall (NName (BYTES text_maker) metadata_maker) (SEQUENCE eps) metadata_call) (BOOLEAN false) (BOOLEAN false) metadata_arg',
        '$magic_method_array_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS) = (pfunction_make)',
        '~pfunction_make.SIGNATURE.BYREF', 'pfunction_make.SIGNATURE.PARAMETERS = eps',
        'pfunction_make.DEFAULTS = eps', '~$function_generator(S,pfunction_make)',
        '$lookup(S.ENV,$ptascii("local")) = eps',
        '$magic_method_array_cv(pmagicmethodcall.ARGUMENTS) = eps',
        '$magic_method_flat_array(S,n_array)',
        '$node_children(S,HARRAY n_array) = [HOBJECT n_old]',
        'S.ARRAYS[n_array] = $magic_method_array([PINT 7,POBJECT n_old],0)',
        'S.OBJECTS[n_old] = INSTANCE pclassdesc_payload.ORIGIN',
        '$node_children(S,HOBJECT n_old) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_array) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT,HARRAY n_array]',
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
        '$factory182_output(S.EVENTS) = $ptascii("MAKER;")',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PARRAY n_array),KNOWN (PINT 9)]) = ([PARRAY n_array,PINT 9])',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,[phpType7_later,phpType7_maker],[KNOWN (PARRAY n_array),KNOWN (PINT 9)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9),KNOWN (PARRAY n_array)]) = eps',
        '$magic_method_call_values(S,pmagicmethodcall.ARGUMENTS,[KNOWN (PARRAY n_array),KNOWN (PINT 9)]) = eps',
        'S_split = $drive_steps(S,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4098)', 'S_full = S_done',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
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
