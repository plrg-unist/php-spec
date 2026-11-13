#!/usr/bin/env python3
"""Ground per-property DIRECT array edges, late field retargeting and an actual object cycle."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('stdclass_direct_array_field_reference_notice_review_cases.json')

PREFIX = r"""
dec $nrpr_output(pevent*) : ptbytes
def $nrpr_output(eps) = eps
def $nrpr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $nrpr_output(pevent*)
dec $nrpr_ready(pstate, nat) : bool
def $nrpr_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("ReviewNotice45\\Primary\\make")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 1) = true
  -- if S.TODO = (NAMED_SEND pcalltarget phpType7* n pnamedargs porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice45\\Primary\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("J;M:17:17;")
def $nrpr_ready(S, 9) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("ReviewNotice45\\Cycle\\take")
  -- if $nrpr_output(S.EVENTS) = $ptascii("U;M;")
def $nrpr_ready(S, n_stage) = false -- otherwise
dec $nrpr_seek(pstate, nat, nat) : pstate
def $nrpr_seek(S, n_stage, n) = S
  -- if $nrpr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $nrpr_seek(S, n_stage, n) = $nrpr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$nrpr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nrpr_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $nrpr_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_return, 0)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("ReviewNotice45\\Primary\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_formal)
$lookup(S_return.ENV, $ptascii("source")) = (n_source_return)
n_formal =/= n_source_return
~(n_formal <- S_return.REFCELLS) /\ n_source_return <- S_return.REFCELLS
S_return.STORE[n_formal] = DEFINED (PARRAY n_root)
S_return.STORE[n_source_return] = DEFINED (PINT 31)
S_return.RESULT = VARIABLE ($ptascii("input")) z_input
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("obj")) = (n_obj_cv)
$lookup(psymboltable_caller.ENV, $ptascii("keep")) = (n_keep)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("outside")) = (n_outside)
$lookup(psymboltable_caller.ENV, $ptascii("next")) = (n_next_cv)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("watch")) = (n_watch)
$lookup(psymboltable_caller.ENV, $ptascii("data")) = eps /\ $lookup(psymboltable_caller.ENV, $ptascii("seed")) = eps /\ $lookup(psymboltable_caller.ENV, $ptascii("nextText")) = eps
S_return.STORE[n_obj_cv] = DEFINED PNULL
S_return.STORE[n_keep] = DEFINED (POBJECT n_object)
S_return.STORE[n_outside] = DEFINED (PARRAY n_old_array)
S_return.STORE[n_next_cv] = DEFINED (PARRAY n_next_array)
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
S_return.STORE[n_leaf] = DEFINED pvalue_shared
pvalue_shared = PSTRING_CARRIER (REQUEST_STRING n_shared_string) ($ptascii("19"))
$string_carrier_valid(S_return, pvalue_original) /\ $string_carrier_valid(S_return, pvalue_shared)
n_leaf <- S_return.REFCELLS /\ n_snapshot =/= n_leaf
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("obj"))) (DIRECT (POBJECT n_object))]
S_return.ARRAYS[n_old_array].ITEMS = [ENTRY (KSTRING ($ptascii("branch"))) (DIRECT (PARRAY n_child)), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_original)]
S_return.ARRAYS[n_next_array].ITEMS = [ENTRY (KSTRING ($ptascii("branch"))) (DIRECT (PARRAY n_next_child)), ENTRY (KSTRING ($ptascii("alias"))) (ALIAS n_leaf)]
S_return.ARRAYS[n_next_child].ITEMS = [ENTRY (KSTRING ($ptascii("text"))) (DIRECT pvalue_next)]
pvalue_next = PSTRING_CARRIER (REQUEST_STRING n_next_string) ($ptascii("23"))
$string_carrier_valid(S_return, pvalue_next)
n_next_array =/= n_old_array /\ n_next_child =/= n_child
S_return.OBJECTS[n_object] = STDINSTANCE
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot_one, ppropertyslot_two]
ppropertyslot_one = {DECL eps, NAME ($ptascii("one")), STATE (PROP_VALUE (DIRECT (PARRAY n_old_array)))}
ppropertyslot_two = {DECL eps, NAME ($ptascii("two")), STATE (PROP_VALUE (DIRECT (PARRAY n_old_array)))}
$objectprops_valid(S_return, [pobjectprops])
S_return.STORE[n_watch] = DEFINED (POBJECT n_weak)
S_return.OBJECTS[n_weak] = WEAKREFERENCE (n_object)
$weakref_get(S_return, n_weak) = POBJECT n_object
S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_object) = 2 /\ $heap_owners(H_return, HARRAY n_old_array) = 3
$heap_owners(H_return, HARRAY n_child) = 1 /\ $heap_owners(H_return, HCELL n_leaf) = 3
$heap_owners(H_return, HARRAY n_next_array) = 1 /\ $heap_owners(H_return, HARRAY n_next_child) = 1
$heap_owners(H_return, HCELL n_formal) = 1 /\ $heap_owners(H_return, HCELL n_source_return) = 3
$node_children(S_after_return, HOBJECT n_object) = [HARRAY n_old_array, HARRAY n_old_array]
$node_children(S_after_return, HARRAY n_old_array) = [HARRAY n_child, HCELL n_leaf]
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $nrpr_seek(S_after_return, 1, 4000)[.COMPLETION = NORMAL]
$nrpr_ready(S_pre, 1)
S_pre.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 4))] /\ pnamedargs.NAMED = eps
$named_origin(S_pre, (porigin_call), 1) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice45\\Primary\\make")
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
pfunction_producer.NAME = preqbytes /\ pfunction_producer.EARLY
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_type)) = $ptascii("array")
$named_expression($named_source(S_pre, (porigin_call), 1)) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer_call
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType18 = NIdentifier (BYTES text_return) metadata_return
$ptlc($base64(text_return)) = $ptascii("array")
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)
(PDEFUNCTION n_unit pfunction_producer.ORIGIN) <- S_pre.DECLARATIONS
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$named_reference_notice_source(S_pre, pcalltarget, 1, (porigin_call))
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
S_pre.FRAMES = eps /\ S_pre.CURRENT = eps
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("input")) = eps
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
n_source_cv = n_source_return
S_pre.STORE[n_source_cv] = DEFINED (PINT 31) /\ S_pre.STORE[n_obj_cv] = DEFINED PNULL
S_pre.STORE[n_keep] = DEFINED (POBJECT n_object)
S_pre.STORE[n_outside] = DEFINED (PARRAY n_old_array)
S_pre.STORE[n_next_cv] = DEFINED (PARRAY n_next_array)
S_pre.STORE[n_leaf] = DEFINED pvalue_shared /\ S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
$named_reference_notice_root_value(S_pre, pvalue_original) /\ $named_reference_notice_root_value(S_pre, pvalue_next) /\ $named_reference_notice_root_value(S_pre, pvalue_shared)
$call_reference_operand_valid(S_pre, REFERENCE n_leaf)
~$foreach_released_cell(S_pre, n_leaf)
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
$heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
$named_reference_notice_object_ancestors(S_pre, [n_root, n_old_array, n_child, n_next_array, n_next_child])
$named_reference_notice_array(S_pre, PARRAY n_old_array) /\ $named_reference_notice_array(S_pre, PARRAY n_next_array)
$update_warning_no_objects($heap_reach([HARRAY n_old_array], eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
$update_warning_no_objects($heap_reach([HARRAY n_next_array], eps, $allocation_edges(S_pre, S_pre.ALLOCATIONS)))
$node_children(S_pre, HOBJECT n_object) = $property_release_nodes(pobjectprops.SLOTS)
$node_children(S_pre, HOBJECT n_object) = [HARRAY n_old_array, HARRAY n_old_array]
$node_children(S_pre, HARRAY n_old_array) = [HARRAY n_child, HCELL n_leaf]
$node_children(S_pre, HARRAY n_child) = eps /\ $node_children(S_pre, HCELL n_leaf) = eps
$weakref_get(S_pre, n_weak) = POBJECT n_object
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps /\ ~$weakmap_key_waiting(S_pre, n_object)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1 /\ $heap_owners(H_pre, HOBJECT n_object) = 2
$heap_owners(H_pre, HARRAY n_old_array) = 3 /\ $heap_owners(H_pre, HARRAY n_child) = 1
$heap_owners(H_pre, HCELL n_leaf) = 3 /\ $heap_owners(H_pre, HCELL n_source_cv) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
""".strip().splitlines()

CYCLE = r"""
S_cycle = $nrpr_seek(S_cycle_initial, 9, 5000)[.COMPLETION = NORMAL]
$nrpr_ready(S_cycle, 9)
S_cycle.TODO = (CALL_SEND pcalltarget_cycle eps 0 eps (porigin_cycle_call) z_cycle) :: ptask_cycle_tail*
S_cycle.RESULT = KNOWN (PARRAY n_cycle_root)
S_cycle.ARRAYS[n_cycle_root].ITEMS = [ENTRY (KSTRING ($ptascii("obj"))) (DIRECT (POBJECT n_cycle_object))]
$objectprops_record_at(S_cycle.OBJECTPROPS, n_cycle_object) = (pobjectprops_cycle)
pobjectprops_cycle.SLOTS = [ppropertyslot_cycle]
ppropertyslot_cycle = {DECL eps, NAME ($ptascii("items")), STATE (PROP_VALUE (DIRECT (PARRAY n_cycle_array)))}
S_cycle.ARRAYS[n_cycle_array].ITEMS = [ENTRY (KSTRING ($ptascii("self"))) (DIRECT (POBJECT n_cycle_object))]
$node_children(S_cycle, HOBJECT n_cycle_object) = [HARRAY n_cycle_array]
$node_children(S_cycle, HARRAY n_cycle_array) = [HOBJECT n_cycle_object]
$objectprops_valid(S_cycle, [pobjectprops_cycle])
$positional_reference_notice_source(S_cycle, pcalltarget_cycle, 0, (porigin_cycle_call))
~$update_warning_no_objects($heap_reach([HARRAY n_cycle_array], eps, $allocation_edges(S_cycle, S_cycle.ALLOCATIONS)))
H_cycle = $heap_graph(S_cycle)
$heap_owners(H_cycle, HOBJECT n_cycle_object) = 3 /\ $heap_owners(H_cycle, HARRAY n_cycle_array) = 1
$heap_valid(H_cycle) /\ $call_descriptors_valid(S_cycle)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object)
~$named_reference_notice_array(S_pre, PARRAY n_root) /\ ~$named_reference_notice_pending(S_pre)
S_scalar = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot_one[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_two[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object_slots(S_scalar, [ppropertyslot_one[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_two[.STATE = PROP_VALUE (DIRECT pvalue_original)]])
$named_reference_notice_object(S_scalar, POBJECT n_object) /\ $named_reference_notice_pending(S_scalar)
$node_children(S_scalar, HOBJECT n_object) = eps
H_scalar = $heap_graph(S_scalar)
$heap_owners(H_scalar, HARRAY n_old_array) = 1 /\ $heap_owners(H_scalar, HARRAY n_child) = 1
$heap_owners(H_scalar, HOBJECT n_object) = 2 /\ $heap_owners(H_scalar, HCELL n_leaf) = 3
$heap_valid(H_scalar) /\ $call_descriptors_valid(S_scalar)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (PARRAY n_root)]
~$named_reference_notice_object(S_cycle, POBJECT n_cycle_object) /\ ~$positional_reference_notice_pending(S_cycle)
S_cycle_fenced = $drive(S_cycle, 1)
S_cycle_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_cycle_fenced.EVENTS = S_cycle.EVENTS
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    assert args.front
    provenance = [path.resolve() for path in args.native_provenance]
    natives = [json.loads(path.read_bytes()) for path in provenance]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in natives}
    assert len(records) == len(natives) == len(cases) == 2
    sources = {i: Path(records[row['id']]['command'][-1]) for i, row in enumerate(cases)}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for i, row in enumerate(cases):
        native, source = records[row['id']], sources[i]
        assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable'] and native['head_stable']
        assert source.read_bytes() == row['source'].encode() and sha(source) == native['source_sha256'] == row['source_sha256']
        assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
        assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
        assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
        assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
        assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i, source in sources.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    reached = [initial('S_initial', 0)] + RETURN + COMMON + [initial('S_cycle_initial', 1)] + CYCLE
    derived = FRONT
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, Path(__file__), CATALOGUE, *provenance]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    for source in sources.values():
        paths += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'fixture_sha256': sha(fixture), 'part': 'stdclass-direct-array-field-front' if args.front else 'stdclass-direct-array-field-notice', 'conditions': len(reached) + len(derived),
        'reached_conditions': len(reached), 'derived_conditions': len(derived),
        'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('stdclass-direct-array-field', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
