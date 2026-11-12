#!/usr/bin/env python3
"""Reached undeclared unset selection, recursion and local-destruction guards."""
import argparse
import json
from pathlib import Path

import closure_call_protocol as protocol
import public_unset_protocol as public

CATALOGUE = Path(__file__).with_name('anonymous_missing_unset_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'selection': 'anonymous-missing-unset-public-slot-bypass',
    'active': 'anonymous-missing-unset-active-recursion',
    'local': 'anonymous-missing-unset-local-destruction',
}
PREFIX = public.PREFIX + r'''
dec $amu_inner(pstate) : bool
def $amu_inner(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ($ptascii("missing")))) z_receiver
def $amu_inner(S) = false -- otherwise
dec $amu_seek_inner(pstate,nat) : pstate
def $amu_seek_inner(S,n) = S -- if $amu_inner(S)
def $amu_seek_inner(S,0) = S -- if ~$amu_inner(S)
def $amu_seek_inner(S,n) = $amu_seek_inner($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$amu_inner(S)
  -- if S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amu_seek_inner(S,n) = S -- otherwise
'''


def seek(target, source, stage):
    return [
        target + '_raw = $pu_seek(' + source + ',' + stage + ',2048)',
        target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
        target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
        '$pu_stage(' + target + ',' + stage + ')',
    ]


def inner(source):
    return [
        'S_inner_raw = $amu_seek_inner(' + source + ',2048)',
        'S_inner_raw.COMPLETION = NORMAL \\/ S_inner_raw.COMPLETION = BUDGET',
        'S_inner = S_inner_raw[.COMPLETION = NORMAL]',
        '$amu_inner(S_inner)',
        'S_inner.TODO = UNSET_ARRAY :: ptask_inner_tail*',
        'S_inner.ORIGIN = (porigin_inner)',
        'porigin_inner =/= ppropertyunset.SITE',
        '$property_unset_absent_candidate(S_inner) = ((S_inner_target,ppropertyunset_inner))',
        'ppropertyunset_inner.PROPERTY = eps',
        'ppropertyunset_inner.OBJECT = n_receiver /\\ ppropertyunset_inner.METHOD = ppropertyunset.METHOD',
        'ppropertyunset_inner.SITE = porigin_inner',
        '$property_unset_capture(S_inner,ppropertyunset_inner)',
        '$property_unset_guard(S_inner,S_inner.CURRENT,S_inner.FRAMES,n_receiver,ppropertyunset.NAME)',
        '$property_unset_plan(S_inner) = eps /\\ $property_unset_pending(S_inner)',
        '$property_unset_absent_guarded_plan(S_inner) = (S_inner_target)',
        '$property_unset_public_guarded_plan(S_inner) = eps /\\ $property_unset_private_guarded_plan(S_inner) = eps',
        '$heap_owners($heap_graph(S_inner),HOBJECT n_receiver) = 2',
        '$pu_guard(S_inner)',
        'PhpStep: S_inner ~> S_inner_step',
        'S_inner_done = $pu_after(S_inner,S_inner_step)',
        'S_inner_done.TODO = ptask_inner_tail*',
        'S_inner_done.RESULT = KNOWN PNULL /\\ S_inner_done.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_inner_done.OBJECTPROPS = S_inner.OBJECTPROPS /\\ S_inner_done.STORE = S_inner.STORE',
        'S_inner_done.ALLOCATIONS = S_inner.ALLOCATIONS /\\ S_inner_done.EVENTS = S_inner.EVENTS',
        'S_inner_done.HELD = S_inner.HELD',
        '$heap_owners($heap_graph(S_inner_done),HOBJECT n_receiver) = 2',
        '$pu_guard(S_inner_done)',
    ]


def checks(case, fixture, filename):
    row = ROWS[CASES[case]]
    conditions = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
    ] + seek('S', 'S_initial', 'PU_PLAN') + [
        'S.TODO = UNSET_ARRAY :: ptask_tail*',
        'S.ORIGIN = (porigin_site)',
        'S.BASE = BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ptbytes_name)) z_receiver',
        '$property_unset_absent_candidate(S) = ((S_target,ppropertyunset))',
        '$property_unset_plan(S) = (ppropertyunset)',
        'ppropertyunset.PROPERTY = eps /\\ ppropertyunset.SITE = porigin_site',
        'ppropertyunset.NAME = ptbytes_name /\\ ppropertyunset.LINE = $property_current_line(S)',
        'n_receiver = ppropertyunset.OBJECT',
        'S_target.BASE = BASE_PROPERTY (POBJECT n_receiver) ptbytes_name',
        '$property_unset_source(S,ppropertyunset)',
        '$property_unset_valid(S,ppropertyunset) /\\ $property_unset_capture(S,ppropertyunset)',
        '$property_unset_capture_state(S,ppropertyunset)',
        '$property_effective_desc(S,n_receiver,ptbytes_name) = eps',
        '$property_resolve(S,n_receiver,ptbytes_name) = PROPERTY_ACCESS ptbytes_name',
        '$object_table_at(S.OBJECTTABLES,n_receiver) = eps',
        '$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,ptbytes_name) = eps',
        '$property_unset_method(S,n_receiver) = (pmethoddesc)',
        '$property_magic_method_source(S,pmethoddesc,"__unset")',
        '$property_unset_function(S,ppropertyunset) = (pmethoddesc.FUNCTION)',
        '~$property_unset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ptbytes_name)',
        '$property_unset_absent_guarded_plan(S) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        '$pu_guard(S)',
        '~$property_unset_valid(S,ppropertyunset[.PROPERTY = (porigin_site)])',
        '~$property_unset_valid(S,ppropertyunset[.SITE = ppropertyunset.METHOD])',
        '~$property_unset_valid(S,ppropertyunset[.NAME = $ptascii("forged")])',
        '~$property_unset_valid(S,ppropertyunset[.LINE = $(ppropertyunset.LINE + 1)])',
        '~$property_unset_valid(S,ppropertyunset[.METHOD = porigin_site])',
        '~$property_unset_valid(S[.SOURCES = eps],ppropertyunset)',
        'PhpStep: S ~> S_call_step',
        'S_call = $pu_after(S,S_call_step)',
        'S_call.TODO = (CALL_ARGS (PROPERTY_UNSET_TARGET ppropertyunset) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) ppropertyunset.LINE) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*',
        'S_call.RESULT = KNOWN PNULL /\\ S_call.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_call.HELD = S.HELD /\\ S_call.EVENTS = S.EVENTS',
        '$property_unset_pending_call(S_call,ppropertyunset)',
        '$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_receiver]',
        '$target_nodes(PROPERTY_UNSET_TARGET ppropertyunset) = eps',
        '$target_instance(PROPERTY_UNSET_TARGET ppropertyunset) = eps',
        '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
        '$pu_guard(S_call)',
    ] + seek('S_receive', 'S_call', 'PU_RECEIVE ppropertyunset.METHOD') + [
        'S_receive.CURRENT = (pcallcontext_unset)',
        'pcallcontext_unset.TARGET = PROPERTY_UNSET_TARGET ppropertyunset',
        'S_receive.FRAMES = [pframe_unset]',
        '$property_unset_frame(S_receive,pcallcontext_unset,pframe_unset,ppropertyunset)',
        '$property_unset_context(S_receive,pcallcontext_unset)',
        '$call_receiver_roots(pcallcontext_unset) = eps',
        '$property_unset_guard(S_receive,S_receive.CURRENT,S_receive.FRAMES,n_receiver,ptbytes_name)',
        '$heap_owners($heap_graph(S_receive),HOBJECT n_receiver) = 2',
        '$pu_guard(S_receive)',
    ]
    next_state = 'S_receive'
    if case == 'selection':
        conditions += [
            '$pu_output(S.EVENTS) = $ptascii("BYPASS;")',
            'ptbytes_name = $ptascii("virtual")',
            '$property_slot_at(ppropertyslot*,$ptascii("ready")) = (ppropertyslot_ready)',
            '$property_slot_at(ppropertyslot*,$ptascii("pending")) = (ppropertyslot_pending)',
            'ppropertyslot_ready.STATE = PROP_UNSET /\\ ppropertyslot_pending.STATE = PROP_UNSET',
            'ppropertyslot_dynamic = {DECL eps, NAME ptbytes_name, STATE (PROP_VALUE (DIRECT (PINT 7)))}',
            'S_populated = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,ppropertyslot* ++ [ppropertyslot_dynamic])],n_receiver)',
            '$property_unset_valid(S_populated,ppropertyunset) /\\ ~$property_unset_capture(S_populated,ppropertyunset)',
            '~$property_unset_needed(S_populated,n_receiver,ptbytes_name)',
            '$property_unset_absent_candidate(S_populated) = eps',
            '$property_unset_plan(S_populated) = eps',
            '$pu_guard(S_populated)',
            'S_retired = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,ppropertyslot* ++ [ppropertyslot_dynamic[.STATE = PROP_UNSET]])],n_receiver)',
            '$property_slot_at(ppropertyslot* ++ [ppropertyslot_dynamic[.STATE = PROP_UNSET]],ptbytes_name) = eps',
            '$property_unset_capture(S_retired,ppropertyunset) /\\ $property_unset_plan(S_retired) = (ppropertyunset)',
            '$pu_guard(S_retired)',
        ]
    elif case == 'active':
        conditions += inner('S_receive')
        next_state = 'S_inner_done'
    else:
        conditions += seek('S_return', 'S_receive', 'PU_RETURN') + [
            '$lookup(S_return.ENV,$ptascii("probe")) = (n_probe_cell)',
            'S_return.STORE[n_probe_cell] = DEFINED (POBJECT n_probe)',
        ] + seek('S_exit', 'S_return', 'PU_EXIT') + [
            'S_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*',
            '$property_unset_public_exit(S_exit,S_exit.TODO,ppropertyunset) = (pdestructionframe)',
            'pdestructionframe <- S_exit.DESTRUCTION.FRAMES',
            'pdestructionframe.FUNCTION = ppropertyunset.METHOD /\\ pdestructionframe.VALUE = KNOWN PNULL',
            '$property_unset_public_exit_guard(S_exit,PROPERTY_UNSET_RESULT ppropertyunset,n_receiver,ptbytes_name)',
            '$property_unset_guard(S_exit,S_exit.CURRENT,S_exit.FRAMES,n_receiver,ptbytes_name)',
            '$pu_guard(S_exit)',
            'S_missing_frame = S_exit[.DESTRUCTION.FRAMES = eps]',
            '$property_unset_public_exit(S_missing_frame,S_missing_frame.TODO,ppropertyunset) = (pdestructionframe)',
            '~$property_unset_public_exit_guard(S_missing_frame,PROPERTY_UNSET_RESULT ppropertyunset,n_receiver,ptbytes_name)',
            '~$property_unset_guard(S_missing_frame,S_missing_frame.CURRENT,S_missing_frame.FRAMES,n_receiver,ptbytes_name)',
        ]
        for suffix, update in (
                ('value', '.VALUE = KNOWN (PINT 1)'),
                ('function', '.FUNCTION = ppropertyunset.SITE'),
                ('origin', '.ORIGIN = (ppropertyunset.METHOD)'),
                ('caller', '.CALLER = (pcallcontext_unset)')):
            conditions += [
                'pdestructionframe_' + suffix + ' = pdestructionframe[' + update + ']',
                'S_bad_' + suffix + ' = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_' + suffix + ') :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*][.DESTRUCTION.FRAMES = [pdestructionframe_' + suffix + ']]',
                '$property_unset_public_exit(S_bad_' + suffix + ',S_bad_' + suffix + '.TODO,ppropertyunset) = eps',
            ]
        conditions += [
            'S_bad_release = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.USER = ~pdestructionrelease.USER]) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*]',
            '$property_unset_public_exit(S_bad_release,S_bad_release.TODO,ppropertyunset) = eps',
        ] + inner('S_exit') + [
            'S_inner.CURRENT = (pcallcontext_probe)',
            '$destructor_context_call(pcallcontext_probe,S_inner.CURRENT,S_inner.FRAMES) = (pdestructorcall_probe)',
            'pdestructorcall_probe.OBJECT = n_probe',
            'pdestructorcall_probe.FRAME = (pdestructionframe)',
            'S_inner.FRAMES = pframe_probe :: pframe_probe_tail*',
            'S_saved = $constant_frame_view(S_inner,pframe_probe,pframe_probe_tail*)',
            '$property_unset_public_exit(S_saved,S_saved.TODO,ppropertyunset) = (pdestructionframe)',
        ]
        next_state = 'S_inner_done'
    conditions += seek('S_result', next_state, 'PU_RESULT') + [
        'S_result.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*',
        'S_result.RESULT = KNOWN PNULL',
        '$property_unset_valid(S_result,ppropertyunset)',
        '$property_unset_tail(S_result,ppropertyunset,S_result.TODO)',
        '~$property_unset_guard(S_result,S_result.CURRENT,S_result.FRAMES,n_receiver,ptbytes_name)',
        '$property_unset_public_exit(S_result,S_result.TODO,ppropertyunset) = eps',
        '$pu_guard(S_result)',
        'S_zero = $drive_steps(S_result,0)',
        'S_zero = S_result[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        *([
            'PhpStep: S_result ~> S_marker',
            'S_marker = S_result[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$heap_owners($heap_graph(S_marker),HOBJECT n_receiver) = 1',
            'S_one.COMPLETION = BUDGET /\\ S_one.TODO =/= ptask_tail* /\\ S_one.TODO =/= S_result.TODO',
            '|S_one.TODO| = 5',
            '~((PROPERTY_UNSET_RESULT ppropertyunset) <- S_one.TODO)',
            'S_one.RESULT = KNOWN PNULL /\\ S_one.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2',
        ] if case == 'local' else [
            'S_one.COMPLETION = BUDGET /\\ S_one.TODO = ptask_tail*',
            'S_one.RESULT = KNOWN PNULL /\\ S_one.BASE = BASE_VALUE (KNOWN PNULL)',
            '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
        ]),
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(S_result,4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps',
        '$pu_output(S_full.EVENTS) = $base64(' + json.dumps(row['stdout_template_base64']) + ')',
        '$class_state_valid(S_full) /\\ $pu_guard(S_full)',
    ]
    if case == 'local':
        conditions.append('~((HOBJECT n_probe) <- S_full.ALLOCATIONS)')
    return conditions


def render(case, fixture, filename):
    conditions = checks(case['id'], fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') +
                    condition + '\n' for condition in conditions), len(conditions))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: {'id': name, 'source': ROWS[CASES[name]]['source']}
                  for name in args.case or CASES},
                 (Path(__file__), CATALOGUE, Path(public.__file__)), fixture_renderer=render)
