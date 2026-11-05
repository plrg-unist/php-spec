#!/usr/bin/env python3
"""Actual setter factory receiver and nonowning post-destruction RHS delivery."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_property_magic_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'property-set-factory-rhs-delivery'
NEW_FRONT = names.FRONT.replace('CLOSURE_TARGET n_closure', 'PROPERTY_MAGIC_SET_TARGET ppropertymagicset')
DELIVERY_FRONT = ('S.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail* '
                  '-- if S.CURRENT = eps')


def setup(fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__set")) = (pmethoddesc)',
        '$ppmethod_set_signature(pmethoddesc.FUNCTION.SIGNATURE)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
    ]


def new(fixture, filename):
    return setup(fixture, filename) + [
        NEW_FRONT,
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'ppropertymagicset.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (ppropertymagicset.OBJECT)',
        'S.OBJECTS[ppropertymagicset.OBJECT] = INSTANCE pclassdesc_called.ORIGIN',
        'ppropertymagicset.INPUT = 7',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$lookup($global_table_view(S).ENV,$ptascii("input")) = (n_input_cell)',
        'ppropertymagicset.CELL = (n_input_cell)',
        'n_input_cell <- S.REFCELLS',
        'S.STORE[n_input_cell] = DEFINED (PINT 9)',
        '$property_magic_set_rhs(S,ppropertymagicset) = (9)',
        '$lookup(S.ENV,$ptascii("incoming")) = (n_incoming_cell)',
        'S.STORE[n_incoming_cell] = DEFINED (PINT 7)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_saved*',
        '$property_magic_set_frame(S,pcallcontext,pframe,pframe_tail*,ppropertymagicset)',
        '$target_nodes(pcallcontext.TARGET) = eps', '$call_receiver_roots(pcallcontext) = eps',
        '$task_nodes(PROPERTY_MAGIC_SET_RESULT ppropertymagicset) = [HOBJECT ppropertymagicset.OBJECT]',
        '$heap_owners($heap_graph(S),HOBJECT ppropertymagicset.OBJECT) = 1',
        'S.ORIGIN = (porigin_new)',
        '$origin_child((porigin_new),[PCFIELD 0]) = (pclassdesc_child.ORIGIN)',
        '$anonymous_new_name(S,porigin_new) = (pclassdesc_child.NAME)',
        '$call_current_valid(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$property_magic_set_context(S,pcallcontext[.CALLED_CLASS = (pclassdesc_base.ORIGIN)])',
        '~$property_magic_set_frame(S,pcallcontext,pframe[.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset[.INPUT = 9]) :: ptask_saved*],pframe_tail*,ppropertymagicset)',
        'S_split = $drive_steps(S,3)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        'S_full = $drive_steps(S,4099)', 'S_full = S_done',
        '~((HOBJECT ppropertymagicset.OBJECT) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def delivery(fixture, filename):
    return setup(fixture, filename) + [
        DELIVERY_FRONT,
        'ppropertymagicset.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'ppropertymagicset.INPUT = 7',
        '~((HOBJECT ppropertymagicset.OBJECT) <- S.ALLOCATIONS)',
        '$task_nodes(PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) = eps',
        '$property_magic_set_delivery_valid(S,ppropertymagicset)',
        '$call_task_valid(S,PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'ppropertymagicset.CELL = (n_input_cell)',
        'n_input_cell <- S.REFCELLS',
        'S.STORE[n_input_cell] = DEFINED (PINT 11)',
        '$property_magic_set_rhs(S,ppropertymagicset) = (11)',
        '$lookup(S.ENV,$ptascii("held")) = (n_held_cell)',
        'S.STORE[n_held_cell] = DEFINED (POBJECT n_child)',
        'S.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$heap_owners($heap_graph(S),HOBJECT n_child) = 1',
        '$factory182_output(S.EVENTS) = $ptascii("SET;OWNER;")',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$property_magic_set_delivery_valid(S[.ORIGIN = (pclassdesc_child.ORIGIN)],ppropertymagicset)',
        'S_done = $drive_steps(S,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$lookup(S_done.ENV,$ptascii("assigned")) = (n_assigned_cell)',
        'S_done.STORE[n_assigned_cell] = DEFINED (PINT 11)',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT ppropertymagicset.OBJECT) <- S_done.ALLOCATIONS)',
        '$class_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def render(case, fixture, filename):
    is_new = case['id'].endswith('-new')
    checks = new(fixture, filename) if is_new else delivery(fixture, filename)
    prefix = names.PREFIX.replace(names.FRONT, NEW_FRONT if is_new else DELIVERY_FRONT)
    return (prefix + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or [CASE + '-new', CASE + '-delivery']
    protocol.run({name: {'id': name, 'source': ROWS[CASE]['source']} for name in selected},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
