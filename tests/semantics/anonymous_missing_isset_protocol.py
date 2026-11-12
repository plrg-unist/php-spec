#!/usr/bin/env python3
"""Reached missing-declaration isset selection, receiver lifetime and refusals."""
import argparse
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_isset_protocol as magic

CATALOGUE = Path(__file__).with_name('anonymous_missing_isset_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASES = {
    'selection': 'anonymous-missing-isset-public-slot-bypass',
    'retirement': 'anonymous-missing-isset-receiver-retirement',
}
PREFIX = magic.PREFIX + r'''
dec $amis_stage(pstate,nat) : bool
def $amis_stage(S,0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("virtual"))
def $amis_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset
  -- if $lookup(S.ENV,$ptascii("name")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PSTRING ($ptascii("virtual")))
def $amis_stage(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if S.RESULT = KNOWN (PBOOL true)
def $amis_stage(S,3) = true
  -- if $amis_stage(S,1)
  -- if $lookup($global_table_view(S).ENV,$ptascii("o")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
def $amis_stage(S,n) = false -- otherwise
dec $amis_seek(pstate,nat,nat) : pstate
def $amis_seek(S,n_stage,n) = S -- if $amis_stage(S,n_stage)
def $amis_seek(S,n_stage,0) = S -- if ~$amis_stage(S,n_stage)
def $amis_seek(S,n_stage,n) = $amis_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$amis_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $amis_seek(S,n_stage,n) = S -- otherwise
'''


def seek(target, source, phase):
    return [
        target + '_raw = $amis_seek(' + source + ',' + str(phase) + ',2048)',
        target + '_raw.COMPLETION = NORMAL \\/ ' + target + '_raw.COMPLETION = BUDGET',
        target + ' = ' + target + '_raw[.COMPLETION = NORMAL]',
        '$amis_stage(' + target + ',' + str(phase) + ')',
    ]


def checks(case, fixture, filename):
    row = ROWS[CASES[case]]
    result = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
    ] + seek('S', 'S_initial', 0) + [
        'S.TODO = (ISSET_RESULT false z) :: ptask_tail*',
        'S.ORIGIN = (porigin_site)',
        'S.BASE = BASE_PROPERTY (POBJECT n_receiver) ($ptascii("virtual"))',
        '$property_isset_needed(S,n_receiver,$ptascii("virtual"))',
        '$property_isset_pending(S)',
        '$property_isset_plan(S) = (ppropertyisset)',
        'ppropertyisset.PROPERTY = eps /\\ ppropertyisset.OBJECT = n_receiver',
        'ppropertyisset.SITE = porigin_site /\\ ppropertyisset.LINE = z',
        '$property_isset_source(S,ppropertyisset) /\\ ~$property_isset_empty(S,ppropertyisset)',
        '$property_isset_valid(S,ppropertyisset) /\\ $property_isset_capture(S,ppropertyisset)',
        '$property_effective_desc(S,n_receiver,ppropertyisset.NAME) = eps',
        '$property_resolve(S,n_receiver,ppropertyisset.NAME) = PROPERTY_ACCESS ppropertyisset.NAME',
        '$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,ppropertyisset.NAME) = eps',
        '$property_get_method(S,n_receiver) = eps',
        '$property_isset_method(S,n_receiver) = (pmethoddesc)',
        '$property_magic_method_source(S,pmethoddesc,"__isset")',
        '$property_isset_function(S,ppropertyisset) = (pmethoddesc.FUNCTION)',
        '~$property_isset_untyped(S,ppropertyisset) /\\ ~$property_isset_rv_ready(S,ppropertyisset)',
        '$mi_guard(S)',
        '~$property_isset_valid(S,ppropertyisset[.PROPERTY = (porigin_site)])',
        '~$property_isset_valid(S,ppropertyisset[.SITE = ppropertyisset.METHOD])',
        '~$property_isset_valid(S,ppropertyisset[.NAME = $ptascii("absent")])',
        '~$property_isset_valid(S,ppropertyisset[.LINE = $(z + 1)])',
        '~$property_isset_valid(S,ppropertyisset[.METHOD = porigin_site])',
        '~$property_isset_valid(S,ppropertyisset[.CLASS = porigin_site])',
        '~$property_isset_valid(S,ppropertyisset[.OBJECT = (|S.OBJECTS|)])',
        '~$property_isset_valid(S[.SOURCES = eps],ppropertyisset)',
        '$property_isset_plan(S[.TODO = (ISSET_RESULT true z) :: ptask_tail*]) = eps',
        'ppropertyslot_dynamic = {DECL eps, NAME ppropertyisset.NAME, STATE (PROP_VALUE (DIRECT (PINT 7)))}',
        'S_populated = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,ppropertyslot* ++ [ppropertyslot_dynamic])],n_receiver)',
        '$property_isset_valid(S_populated,ppropertyisset) /\\ ~$property_isset_capture(S_populated,ppropertyisset)',
        '$property_isset_plan(S_populated) = eps',
        'S_unset = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_receiver,ppropertyslot* ++ [ppropertyslot_dynamic[.STATE = PROP_UNSET]])],n_receiver)',
        '$property_state_valid(S_populated) /\\ $property_state_valid(S_unset)',
        '$property_isset_needed(S_unset,n_receiver,ppropertyisset.NAME)',
        '$property_slot_at(ppropertyslot* ++ [ppropertyslot_dynamic[.STATE = PROP_UNSET]],ppropertyisset.NAME) = eps',
        '$property_isset_capture(S_unset,ppropertyisset) /\\ $property_isset_plan(S_unset) = (ppropertyisset)',
        'S_call_raw = $drive_steps(S,1)',
        'S_call_raw.COMPLETION = BUDGET',
        'S_call = S_call_raw[.COMPLETION = NORMAL]',
        'S_call.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ppropertyisset.NAME)]) (porigin_site) z) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*',
        'S_call.RESULT = KNOWN PNULL /\\ S_call.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_call.HELD = S.HELD /\\ S_call.EVENTS = S.EVENTS',
        '$property_isset_pending_call(S_call,ppropertyisset)',
        '$call_task_valid(S_call,S_call.TODO[0]) /\\ $call_task_valid(S_call,PROPERTY_ISSET_RESULT ppropertyisset)',
        '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
        '$target_nodes(PROPERTY_ISSET_TARGET ppropertyisset) = eps',
        '$target_instance(PROPERTY_ISSET_TARGET ppropertyisset) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = $heap_owners($heap_graph(S_call),HOBJECT n_receiver)',
        '~$property_isset_pending_call(S_call[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ($ptascii("wrong")))]) (porigin_site) z) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*],ppropertyisset)',
        '~$property_isset_pending_call(S_call[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ppropertyisset.NAME)]) (porigin_site) z) :: ptask_tail*],ppropertyisset)',
    ] + seek('S_entered', 'S_call', 1) + [
        'S_entered.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset',
        'S_entered.FRAMES = [pframe]',
        '$property_isset_frame(S_entered,pcallcontext,pframe,ppropertyisset)',
        '$property_isset_entered(S_entered,S_entered.CURRENT,S_entered.FRAMES,ppropertyisset)',
        '$property_isset_context(S_entered,pcallcontext) /\\ $call_current_valid(S_entered)',
        '$call_receiver_roots(pcallcontext) = eps',
        '$heap_owners($heap_graph(S_entered),HOBJECT n_receiver) = 2',
        '$mi_guard(S_entered)',
        '~$property_isset_frame(S_entered,pcallcontext[.LINE = $(z + 1)],pframe,ppropertyisset)',
        '~$property_isset_frame(S_entered,pcallcontext[.RECEIVER = eps],pframe,ppropertyisset)',
        '~$property_isset_frame(S_entered,pcallcontext,pframe[.TODO = ptask_tail*],ppropertyisset)',
    ]
    if case == 'selection':
        result += [
            '$mi_output(S.EVENTS) = $ptascii("LIVE;NULL;")',
            'porigin_site = PORIGIN n_unit pcpath_site',
            'pcpath_isset = pcpath_site[0:$nabs($(|pcpath_site| - 2))]',
            '$origin_node(S.SOURCES,porigin_site) = (NExprPropertyFetch expression_receiver (NIdentifier (BYTES text_name) metadata_name) metadata)',
            '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_isset) = (NExprIsset (SEQUENCE ([expression_site])) metadata_isset)',
            'S.SOURCES = [pcunit_source]',
        ]
        for suffix, encoded in [('blank', ''), ('nul', 'AHg=')]:
            result += [
                'expression_' + suffix + ' = NExprPropertyFetch expression_receiver (NIdentifier (BYTES ' + json.dumps(encoded) + ') metadata_name) metadata',
                'S_' + suffix + ' = S[.SOURCES = [pcunit_source[.OCCURRENCES = $mi_replace($mi_replace(pcunit_source.OCCURRENCES,pcpath_site,expression_' + suffix + '),pcpath_isset,NExprIsset (SEQUENCE ([expression_' + suffix + '])) metadata_isset)]]]',
                'ppropertyisset_' + suffix + ' = ppropertyisset[.NAME = $base64(' + json.dumps(encoded) + ')]',
                '$property_isset_source(S_' + suffix + ',ppropertyisset_' + suffix + ')',
                '~$property_isset_valid(S_' + suffix + ',ppropertyisset_' + suffix + ')',
            ]
    else:
        result += seek('S_removed', 'S_entered', 3) + [
            'S_removed.CURRENT = (pcallcontext)',
            '$property_isset_context(S_removed,pcallcontext)',
            'S_caller = $constant_frame_scope(S_removed,pframe,eps)',
            '$property_isset_valid(S_caller,ppropertyisset) /\\ ~$property_isset_capture(S_caller,ppropertyisset)',
            '$heap_owners($heap_graph(S_removed),HOBJECT n_receiver) = 1',
            '$mi_guard(S_removed)',
        ]
    result += seek('S_returned', 'S_entered', 2) + [
        'S_returned.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*',
        '$property_isset_valid(S_returned,ppropertyisset)',
        '$property_isset_tail(S_returned,ppropertyisset,S_returned.TODO)',
        '$call_task_valid(S_returned,PROPERTY_ISSET_RESULT ppropertyisset) /\\ $mi_guard(S_returned)',
        'S_history = $objectprops_mark(S_returned[.OBJECTPROPS = $objectprops_set(S_returned.OBJECTPROPS,n_receiver,ppropertyslot* ++ [ppropertyslot_dynamic])],n_receiver)',
        '$mi_guard(S_history)',
        '$property_isset_valid(S_history,ppropertyisset) /\\ ~$property_isset_capture(S_history,ppropertyisset)',
        '$call_task_valid(S_history,PROPERTY_ISSET_RESULT ppropertyisset)',
        'S_history_after = $drive_steps(S_history,1)',
        'S_history_after.COMPLETION = BUDGET /\\ S_history_after.RESULT = KNOWN (PBOOL true)',
        'S_history_after.TODO = ptask_tail*',
        'S_one = $drive_steps(S_returned,1)',
        'S_one.COMPLETION = BUDGET /\\ S_one.RESULT = KNOWN (PBOOL true)',
        'S_one.TODO = ptask_tail*',
        'S_split = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_full = $drive_steps(S_returned,4097)',
        'S_split = S_full',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps',
        '$mi_output(S_full.EVENTS) = $base64(' + json.dumps(row['stdout_template_base64']) + ')',
        '$class_state_valid(S_full) /\\ $mi_guard(S_full)',
    ]
    if case == 'retirement':
        result += [
            '$heap_owners($heap_graph(S_returned),HOBJECT n_receiver) = 1',
            '~((HOBJECT n_receiver) <- S_full.ALLOCATIONS)',
        ]
    return result


def render(case, fixture, filename):
    clauses = checks(case['id'], fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=sorted(CASES), action='append')
    args = parser.parse_args()
    selected = args.case or CASES
    protocol.run({name: {'id': name, 'source': ROWS[CASES[name]]['source']} for name in selected},
                 (Path(__file__), CATALOGUE, Path(magic.__file__)), fixture_renderer=render)
