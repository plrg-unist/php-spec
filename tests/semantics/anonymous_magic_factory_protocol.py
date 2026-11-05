#!/usr/bin/env python3
"""Checked magic-source bounds and real borrowed-getter factory ownership."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_magic_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-get-anonymous-cleared-receiver'
FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'PROPERTY_GET_TARGET n_receiver porigin_getter')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $factory189_held(pstate) : bool
def $factory189_held(S) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata_echo)) :: ptask_tail*
  -- if $base64(text) = $ptascii("HELD;")
def $factory189_held(S) = false -- otherwise
dec $factory189_seek_held(pstate, nat) : pstate
def $factory189_seek_held(S, 0) = S
def $factory189_seek_held(S, n) = S -- if $(n > 0) /\ $factory189_held(S)
def $factory189_seek_held(S, n) = $factory189_seek_held($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$factory189_held(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $factory189_seek_held(S, n) = S -- otherwise
'''


def context(fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_owner,pclassdesc_child,pclassdesc_after]',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("__get")) = (pmethoddesc)',
        '$origin_node([P.FOLD.SOURCE],pmethoddesc.FUNCTION.ORIGIN) = (pcnode_method)',
        'pcnode_method = NStmtClassMethod (SEQUENCE eps) (INTEGER flags) (BOOLEAN b_ref) (NIdentifier (BYTES text) metadata_name) phpType16 ABSENT (SEQUENCE statement*) metadata',
        '~b_ref', '$anonymous_get_factory_parameters(phpType16)',
        '$anonymous_method_factory_node(pcnode_method)',
        '$anonymous_magic_factory(flags,b_ref,$base64(text),phpType16,ABSENT,statement*)',
        '~$anonymous_magic_factory(flags,true,$base64(text),phpType16,ABSENT,statement*)',
        '~$anonymous_magic_factory(flags,false,$ptascii("__destruct"),phpType16,ABSENT,statement*)',
        '~$anonymous_magic_factory(flags,false,$base64(text),phpType16,NIdentifier (BYTES "b2JqZWN0") metadata_name,statement*)',
    ]


def runtime(row, fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_owner,pclassdesc_child,pclassdesc_after]',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("__get")) = (pmethoddesc)',
        '~pmethoddesc.FUNCTION.SIGNATURE.BYREF',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'porigin_getter = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_owner.ORIGIN)',
        'pcallcontext.RECEIVER = (n_receiver)',
        'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_owner.ORIGIN',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_saved*',
        'ppropertyget.OBJECT = n_receiver',
        'ppropertyget.CLASS = pclassdesc_owner.ORIGIN',
        'ppropertyget.METHOD = porigin_getter',
        '$property_get_frame(S,pcallcontext,pframe)',
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_receiver_roots(pcallcontext) = eps',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        'S.ORIGIN = (porigin_new)',
        '$origin_child((porigin_new),[PCFIELD 0]) = (pclassdesc_child.ORIGIN)',
        '$anonymous_new_name(S,porigin_new) = (pclassdesc_child.NAME)',
        '$declaration_early(S.DECLARATIONS,pclassdesc_child.ORIGIN,PPCLASS)',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$class_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$anonymous_new_task_valid(S[.ORIGIN = (pclassdesc_owner.ORIGIN)],NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)',
        '~$property_get_frame(S,pcallcontext,pframe[.TODO = (PROPERTY_GET_RESULT ppropertyget[.CLASS = pclassdesc_child.ORIGIN]) :: ptask_saved*])',
        'S_held_found = $factory189_seek_held(S,4096)',
        'S_held_found.COMPLETION = BUDGET',
        'S_held = S_held_found[.COMPLETION = NORMAL]',
        '$factory189_held(S_held)',
        '$lookup(S_held.ENV,$ptascii("child")) = (n_child_cell)',
        'S_held.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_held.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '~((HOBJECT n_receiver) <- S_held.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_held),HOBJECT n_child) = 1',
        '$factory182_output(S_held.EVENTS) = $ptascii("GET;OWNER;")',
        '$call_descriptors_valid(S_held)', '$heap_valid($heap_graph(S_held))',
        'S_split = $drive_steps(S,3)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4099)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$declaration_history_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


def render(case, fixture, filename):
    checks = context(fixture, filename) if case['id'].endswith('-context') else runtime(ROWS[CASE], fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or [CASE + '-context', CASE]
    protocol.run({name: {'id': name, 'source': ROWS[CASE]['source']} for name in selected},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
