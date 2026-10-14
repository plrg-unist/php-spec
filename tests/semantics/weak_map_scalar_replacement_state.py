#!/usr/bin/env python3
"""Two genuine occupied-entry fronts; complete endings belong to source2."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as q
import shutdown_state_review as runner
from incdec_warning_protocol import transitioned

CATALOG = ROOT / 'tests/semantics/cycle_collection_cases.json'
SOURCE_IDS = {
    'object-to-scalar': 'weak-map-object-to-scalar-replacement-71',
    'scalar-to-object': 'weak-map-scalar-to-object-replacement-71',
}
CATALOG_ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
SOURCES = {name: CATALOG_ROWS[source_id] for name, source_id in SOURCE_IDS.items()}
HELPERS = r'''
dec $weak71_capture(pstate) : paccess?
def $weak71_capture(S) = (paccess[.SELECTED = $rcontainer_selected(S, paccess.RHS)][.VALUE = pvalue][.OFFSET = pvalue_key])
  -- if $access_set_plan(S) = (paccess)
  -- if S_value = $quiet_operand(S, paccess.RHS)
  -- if S_value.COMPLETION = NORMAL
  -- if S_value.RESULT = KNOWN pvalue
  -- if S_key = $quiet_operand(S, paccess.INPUT)
  -- if S_key.COMPLETION = NORMAL
  -- if S_key.RESULT = KNOWN pvalue_key
def $weak71_capture(S) = eps -- otherwise
dec $weak71_resume(pstate) : bool
def $weak71_resume(S) = true
  -- if S.TODO = (ACCESS_RESUME paccess) :: ptask_tail*
  -- if $weakmap_set_resume(S, paccess)
  -- if S.CURRENT = eps
  -- if S.DESTRUCTION.CALLS = eps /\ S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $weak71_resume(S) = false -- otherwise
dec $weak71_object(pstate) : bool
def $weak71_object(S) = true
  -- if $weak71_capture(S) = (paccess)
  -- if paccess.OBJECT = (n_map)
  -- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry)
  -- if pweakmapentry.VALUE = PBOOL false
  -- if paccess.VALUE = POBJECT n_new
  -- if $weakmap_replace_allowed(S, paccess)
def $weak71_object(S) = false -- otherwise
dec $weak71_found(pstate, bool) : bool
def $weak71_found(S, true) = $weak71_resume(S[.COMPLETION = NORMAL])
def $weak71_found(S, false) = $weak71_object(S[.COMPLETION = NORMAL])
dec $weak71_seek(pstate, bool, nat) : pstate
def $weak71_seek(S, b_resume, n) = S -- if $weak71_found(S, b_resume)
def $weak71_seek(S, b_resume, n) = $weak71_seek($drive_steps(S[.COMPLETION = NORMAL], 1), b_resume, $nabs($(n - 1)))
  -- if ~$weak71_found(S, b_resume)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $weak71_seek(S, b_resume, n) = S
  -- if ~$weak71_found(S, b_resume)
  -- if (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ n = 0
dec $weak71_output(pevent) : bool
def $weak71_output(OUTPUT ptbytes) = true
def $weak71_output(pevent) = false -- otherwise
dec $weak71_outputs(pevent*) : ptbytes
def $weak71_outputs(eps) = eps
def $weak71_outputs((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $weak71_outputs(pevent_tail*)
def $weak71_outputs(pevent :: pevent_tail*) = $weak71_outputs(pevent_tail*)
  -- if ~$weak71_output(pevent)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


COMMON = [
    '$weak71_capture(S) = (paccess)',
    'paccess.OBJECT = (n_map)', 'paccess.OFFSET = POBJECT n_key',
    'S.OBJECTS[n_map] = WEAKMAP (pweakmapentry)',
    'pweakmapentry.KEY = n_key', '$weakmap_before_valid(S, pweakmapentry)',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_map]',
    'S.TODO = paccess.TASK :: ptask_tail*',
    '$weakmap_replace_allowed(S, paccess)',
    '$access_valid(S, paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")])',
    '~$weakmap_replace_allowed(S[.TODO = DISCARD :: ptask_tail*], paccess)',
    '~$weakmap_replace_allowed(S[.RESULT = KNOWN PNULL], paccess)',
    '~$weakmap_replace_allowed(S[.CODE = eps], paccess)',
    '~$weakmap_replace_allowed(S, paccess[.LINE = $(paccess.LINE + 1)])',
    '~$weakmap_replace_allowed(S, paccess[.LATCH = true])',
    '~$weakmap_replace_allowed(S, paccess[.KEYHOLE = true])',
    '~$weakmap_replace_allowed(S, paccess[.OFFSET = POBJECT n_map])',
    '~$weakmap_replace_allowed(S, paccess[.RHS = KNOWN PNULL])',
    '~$weakmap_replace_allowed(S, paccess[.SELECTED = KNOWN PNULL])',
    '~$weakmap_free_value_allowed(S, POBJECT n_map)',
    '~$weakmap_free_value_allowed(S, PARRAY (|S.ARRAYS|))',
    '~$weakmap_free_value_allowed(S, PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("invalid")))',
    *valid('S'),
]

PRIMARY = [
    *COMMON,
    'pweakmapentry.VALUE = POBJECT n_old',
    '$string_bytes(paccess.VALUE) = ($ptascii("captured"))',
    '$weakmap_write_value_allowed(S, paccess)',
    '$value_nodes(paccess.VALUE) = eps',
    '$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_old) = 1',
    '$lookup(S.ENV, $ptascii("rhs")) = (n_rhs)',
    '$lookup(S.ENV, $ptascii("result")) = (n_result)',
    '$lookup(S.ENV, $ptascii("oldWeak")) = (n_weak_cell)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.STORE[n_result] = DEFINED pvalue_before_result',
    '$string_bytes(pvalue_before_result) = ($ptascii("before"))',
    '$weakref_get(S, n_weak) = POBJECT n_old',
    'PhpStep: S ~> S_published',
    'S_published.OBJECTS[n_map] = WEAKMAP (pweakmapentry[.VALUE = paccess.VALUE])',
    'S_published.TODO = (ACCESS_RESUME paccess_resume) :: ptask_tail*',
    'paccess_resume = paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    '$weakmap_set_resume(S_published, paccess_resume)',
    '$heap_owners($heap_prune($heap_graph(S_published)), HOBJECT n_old) = 0',
    'S_published.STORE[n_result] = S.STORE[n_result]',
    'S_live = ' + transitioned('S', 'S_published'),
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ACCESS_RESUME paccess_resume) :: ptask_tail*',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_old)]',
    '$destructor_release_valid(S_live, pdestructionrelease)',
    '$destructor_operation_valid(S_live, pdestructionoperation)',
    *valid('S_live'),
    'S_resume = $weak71_seek(S_live, true, 2000)[.COMPLETION = NORMAL]',
    'S_resume.TODO = (ACCESS_RESUME paccess_resume) :: ptask_tail*',
    'S_resume.OBJECTS[n_map] = S_published.OBJECTS[n_map]',
    'S_resume.STORE[n_result] = S.STORE[n_result]',
    'S_resume.STORE[n_rhs] = DEFINED pvalue_rhs_changed',
    '$string_bytes(pvalue_rhs_changed) = ($ptascii("changed"))',
    '$weakref_get(S_resume, n_weak) = PNULL',
    '~((HOBJECT n_old) <- S_resume.ALLOCATIONS)',
    '$heap_owners($heap_prune($heap_graph(S_resume)), HOBJECT n_old) = 0',
    '$weak71_outputs(S_resume.EVENTS) = ($ptascii("replace|D-entry:captured|D-result:before|D-rhs:captured|D|"))',
    *valid('S_resume'),
    'PhpStep: S_resume ~> S_readback',
    'S_readback.RESULT = KNOWN pvalue_readback',
    '$string_bytes(pvalue_readback) = ($ptascii("changed"))',
    'S_readback.OBJECTS[n_map] = S_resume.OBJECTS[n_map]',
    'S_readback.STORE[n_result] = S.STORE[n_result]',
    'S_readback.EVENTS = S_resume.EVENTS',
    *valid('S_readback'),
    '$drive_steps(S_resume, 0) = S_resume[.COMPLETION = BUDGET]',
    '$drive_steps(S_resume, 1) = ' + transitioned('S_resume', 'S_readback') + '[.COMPLETION = BUDGET]',
]

COMPANION = [
    *COMMON,
    '$string_bytes(pweakmapentry.VALUE) = ($ptascii("first"))',
    'paccess.VALUE = PBOOL false', '$value_nodes(pweakmapentry.VALUE) = eps',
    'PhpStep: S ~> S_false',
    'S_false.OBJECTS[n_map] = WEAKMAP (pweakmapentry[.VALUE = PBOOL false])',
    'S_false.TODO = (ACCESS_RESUME paccess_false) :: ptask_tail*',
    'paccess_false = paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    'S_false_live = ' + transitioned('S', 'S_false'),
    'S_false_live.DESTRUCTION.OPERATIONS = eps',
    'S_false_live.DESTRUCTION.RELEASES = eps',
    'S_false_live.EVENTS = S.EVENTS',
    *valid('S_false_live'),
    'PhpStep: S_false_live ~> S_false_result',
    'S_false_result.RESULT = KNOWN (PBOOL false)',
    'S_object = $weak71_seek(' + transitioned('S_false_live', 'S_false_result') + ', false, 2000)[.COMPLETION = NORMAL]',
    '$weak71_capture(S_object) = (paccess_object)',
    'paccess_object.OBJECT = (n_map)', 'paccess_object.OFFSET = POBJECT n_key',
    'paccess_object.VALUE = POBJECT n_new',
    'S_object.OBJECTS[n_map] = WEAKMAP (pweakmapentry[.VALUE = PBOOL false])',
    '$weakmap_replace_allowed(S_object, paccess_object)',
    '$heap_owners($heap_prune($heap_graph(S_object)), HOBJECT n_new) = 1',
    *valid('S_object'),
    'PhpStep: S_object ~> S_object_published',
    'S_object_published.TODO = (ACCESS_RESUME paccess_object_resume) :: ptask_object_tail*',
    'paccess_object_resume = paccess_object[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    'S_object_published.OBJECTS[n_map] = WEAKMAP (pweakmapentry[.VALUE = POBJECT n_new])',
    '$node_children(S_object_published, HOBJECT n_map) = [HOBJECT n_new]',
    '$heap_owners($heap_prune($heap_graph(S_object_published)), HOBJECT n_new) = 2',
    'S_object_live = ' + transitioned('S_object', 'S_object_published'),
    'S_object_live.DESTRUCTION.OPERATIONS = eps',
    'S_object_live.DESTRUCTION.RELEASES = eps',
    *valid('S_object_live'),
    'PhpStep: S_object_live ~> S_object_result',
    'S_object_result.RESULT = KNOWN (POBJECT n_new)',
    'S_object_result.OBJECTS[n_map] = S_object_live.OBJECTS[n_map]',
    '$heap_owners($heap_prune($heap_graph(S_object_result)), HOBJECT n_new) = 3',
    *valid('S_object_result'),
    '$drive_steps(S_object_live, 0) = S_object_live[.COMPLETION = BUDGET]',
    '$drive_steps(S_object_live, 1) = ' + transitioned('S_object_live', 'S_object_result') + '[.COMPLETION = BUDGET]',
]


CASES = {
    'object-to-scalar': {'source': SOURCES['object-to-scalar']['source'],
        'stage': 'S_stage = S[.COMPLETION = NORMAL] -- if $weak71_capture(S_stage) = (paccess_stage) -- if paccess_stage.OBJECT = (n_map_stage) -- if S_stage.OBJECTS[n_map_stage] = WEAKMAP (pweakmapentry_stage) -- if pweakmapentry_stage.VALUE = POBJECT n_old_stage -- if $string_bytes(paccess_stage.VALUE) = ($ptascii("captured")) -- if $weakmap_replace_allowed(S_stage, paccess_stage)',
        'checks': PRIMARY},
    'scalar-to-object': {'source': SOURCES['scalar-to-object']['source'],
        'stage': 'S_stage = S[.COMPLETION = NORMAL] -- if $weak71_capture(S_stage) = (paccess_stage) -- if paccess_stage.OBJECT = (n_map_stage) -- if S_stage.OBJECTS[n_map_stage] = WEAKMAP (pweakmapentry_stage) -- if $string_bytes(pweakmapentry_stage.VALUE) = ($ptascii("first")) -- if paccess_stage.VALUE = PBOOL false -- if $weakmap_replace_allowed(S_stage, paccess_stage)',
        'checks': COMPANION},
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=SOURCES)
    args = parser.parse_args()
    assert Path.cwd() == ROOT == runner.ROOT == q.ROOT
    watched = [Path(__file__), CATALOG, Path(runner.__file__), ROOT / 'tests/semantics/incdec_warning_protocol.py']
    for row in SOURCES.values():
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    before = q.inputs()
    before.update({str(path): q.describe(path) for path in watched})
    runner.CASES = CASES
    outputs = []

    def recorded(command, directory, stem, environment, timeout):
        command = list(map(str, command))
        assert command[0] == str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        fixture = Path(command[-1])
        fixture.write_text(HELPERS + fixture.read_text())
        process = q.recorded([command[0], '--sl', *command[1:]], directory / stem, timeout)
        assert process['interruption'] is None and not process['group_after']
        outputs.append(directory.parent)
        return process

    runner.recorded = recorded
    passed = runner.run(args.case)
    after = q.inputs()
    after.update({str(path): q.describe(path) for path in watched})
    assert before == after
    out = outputs[0]
    report_path = out / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(inputs=before, mode='SL source-reached fronts only; no terminal replay',
                  affinity=sorted(__import__('os').sched_getaffinity(0)))
    for row in report['records']:
        assert row['source_sha256'] == SOURCES[row['id']]['source_sha256']
        fixture = Path(row['process']['argv'][-1])
        row['fixture_sha256'] = hashlib.sha256(fixture.read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
