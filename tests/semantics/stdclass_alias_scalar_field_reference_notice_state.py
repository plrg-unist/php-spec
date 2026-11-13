#!/usr/bin/env python3
"""Ground scalar ALIAS field cells, repeated physical edges and sole-child ownership before Notices."""
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
CATALOGUE = Path(__file__).with_name('stdclass_alias_scalar_field_reference_notice_cases.json')

PREFIX = r"""
dec $asf_output(pevent*) : ptbytes
def $asf_output(eps) = eps
def $asf_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $asf_output(pevent*)
dec $asf_ready(pstate, nat) : bool
def $asf_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("StdClassAliasScalarNotice43\\make") \/ pcallcontext.NAME = $ptascii("StdClassAliasScalarThrow43\\make")
def $asf_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("StdClassAliasScalarNotice43\\take") \/ pfunction.NAME = $ptascii("StdClassAliasScalarThrow43\\take")
def $asf_ready(S, n_stage) = false -- otherwise
dec $asf_seek(pstate, nat, nat) : pstate
def $asf_seek(S, n_stage, n) = S
  -- if $asf_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $asf_seek(S, n_stage, n) = $asf_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$asf_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $asf_seek(S, n_stage, n) = S -- otherwise
"""

RETURN = r"""
S_initial.COMPLETION = BUDGET
S_return = $asf_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_return, 0)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("StdClassAliasScalarNotice43\\make")
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
$lookup(S_return.ENV, $ptascii("input")) = (n_source)
S_return.STORE[n_source] = DEFINED (POBJECT n_object)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(psymboltable_caller.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(psymboltable_caller.ENV, $ptascii("holder")) = (n_holder)
$lookup(psymboltable_caller.ENV, $ptascii("replacement")) = (n_replacement)
S_return.STORE[n_keeper] = DEFINED (POBJECT n_object)
S_return.STORE[n_leaf] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_return, pvalue_original)
S_return.STORE[n_replacement] = DEFINED pvalue_replacement
pvalue_replacement = PSTRING_CARRIER (REQUEST_STRING n_replacement_string) ($ptascii("31"))
$string_carrier_valid(S_return, pvalue_replacement)
$objectprops_record_at(S_return.OBJECTPROPS, n_object) = (pobjectprops)
pobjectprops.SLOTS = [ppropertyslot_a, ppropertyslot_b]
ppropertyslot_a = {DECL eps, NAME ($ptascii("a")), STATE (PROP_VALUE (ALIAS n_leaf))}
ppropertyslot_b = {DECL eps, NAME ($ptascii("b")), STATE (PROP_VALUE (ALIAS n_leaf))}
S_return.STORE[n_holder] = DEFINED (POBJECT n_holder_object)
$objectprops_record_at(S_return.OBJECTPROPS, n_holder_object) = (pobjectprops_holder)
pobjectprops_holder.SLOTS = [{DECL eps, NAME ($ptascii("p")), STATE (PROP_VALUE (ALIAS n_leaf))}]
$node_children(S_return, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_return, HOBJECT n_holder_object) = [HCELL n_leaf]
$node_children(S_return, HCELL n_leaf) = eps /\ $node_children(S_return, HCELL n_snapshot) = eps
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return_tail*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HCELL n_source) = 3 /\ $heap_owners(H_return, HOBJECT n_object) = 3
$heap_owners(H_return, HCELL n_leaf) = 5 /\ $heap_owners(H_return, HOBJECT n_holder_object) = 1
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
""".strip().splitlines()

COMMON = r"""
S_pre = $asf_seek(S_after_return, 1, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_pre, 1)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("source")) = (n_source)
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source)
$lookup(S_pre.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("leafAlias")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("holder")) = (n_holder)
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops)
$objectprops_record_at(S_pre.OBJECTPROPS, n_holder_object) = (pobjectprops_holder)
S_pre.STORE[n_leaf] = DEFINED pvalue_original
$call_reference_operand_valid(S_pre, REFERENCE n_leaf) /\ $named_reference_notice_root_value(S_pre, pvalue_original)
$objectprops_valid(S_pre, [pobjectprops])
$property_release_nodes(pobjectprops.SLOTS) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HOBJECT n_object) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_pre, HCELL n_leaf) = eps
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps /\ S_pre.CONTAINERINITS = eps
~(n_leaf <- S_pre.LITERALREFRETAINED) /\ ~(n_leaf <- S_pre.LITERALREFDEBTS)
~$foreach_released_cell(S_pre, n_leaf) /\ $heap_count(HCELL n_leaf, S_pre.NATIVEEXCESS) = 0
$object_table_at(S_pre.OBJECTTABLES, n_object) = eps
S_pre.GC.ACTIVE = eps /\ S_pre.GC.PLAN = eps /\ S_pre.GC.WORKER = eps
~$weakmap_key_waiting(S_pre, n_object)
$asf_output(S_pre.EVENTS) = $ptascii("A;M:1:1;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HCELL n_source) = 2 /\ $heap_owners(H_pre, HOBJECT n_object) = 3
$heap_owners(H_pre, HCELL n_leaf) = 5
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
""".strip().splitlines()

THROW = r"""
S_throw_return = $asf_seek(S_throw_initial, 0, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_throw_return, 0)
S_throw_return.CURRENT = (pcallcontext_throw)
$function_at($all_functions(S_throw_return), pcallcontext_throw.FUNCTION) = (pfunction_throw)
pfunction_throw.NAME = $ptascii("StdClassAliasScalarThrow43\\make")
$lookup(S_throw_return.ENV, $ptascii("input")) = (n_throw_formal)
$lookup(S_throw_return.ENV, $ptascii("source")) = (n_throw_source)
S_throw_return.STORE[n_throw_formal] = DEFINED (POBJECT n_throw_object)
S_throw_return.STORE[n_throw_source] = DEFINED (PINT 7)
$objectprops_record_at(S_throw_return.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
pobjectprops_throw.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (ALIAS n_throw_leaf))}]
S_throw_return.STORE[n_throw_leaf] = DEFINED pvalue_throw
pvalue_throw = PSTRING_CARRIER (REQUEST_STRING n_throw_string) ($ptascii("17"))
$string_carrier_valid(S_throw_return, pvalue_throw)
S_throw_return.GLOBALTABLE = (psymboltable_throw)
$lookup(psymboltable_throw.ENV, $ptascii("leaf")) = eps
$lookup(psymboltable_throw.ENV, $ptascii("snapshot")) = (n_throw_snapshot)
$lookup(psymboltable_throw.ENV, $ptascii("watch")) = (n_throw_watch)
S_throw_return.STORE[n_throw_snapshot] = DEFINED pvalue_throw
S_throw_return.STORE[n_throw_watch] = DEFINED (POBJECT n_throw_weak)
S_throw_return.OBJECTS[n_throw_weak] = WEAKREFERENCE (n_throw_object)
$node_children(S_throw_return, HOBJECT n_throw_weak) = eps
S_throw_after_return = $drive(S_throw_return, 1)[.COMPLETION = NORMAL]
H_throw_return = $heap_graph(S_throw_after_return)
$heap_owners(H_throw_return, HOBJECT n_throw_object) = 2 /\ $heap_owners(H_throw_return, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_return)
S_throw_pre = $asf_seek(S_throw_after_return, 1, 3000)[.COMPLETION = NORMAL]
$asf_ready(S_throw_pre, 1)
S_throw_pre.TODO = (CALL_SEND pcalltarget_throw eps 0 eps (porigin_throw_call) z_throw) :: ptask_throw_tail*
S_throw_pre.RESULT = KNOWN (POBJECT n_throw_object)
~((HCELL n_throw_formal) <- S_throw_pre.ALLOCATIONS)
$lookup(S_throw_pre.ENV, $ptascii("input")) = eps
$lookup(S_throw_pre.ENV, $ptascii("leaf")) = eps
$call_reference_operand_valid(S_throw_pre, REFERENCE n_throw_leaf)
$named_reference_notice_root_value(S_throw_pre, pvalue_throw)
$objectprops_record_at(S_throw_pre.OBJECTPROPS, n_throw_object) = (pobjectprops_throw)
$objectprops_valid(S_throw_pre, [pobjectprops_throw])
$node_children(S_throw_pre, HOBJECT n_throw_object) = [HCELL n_throw_leaf] /\ $node_children(S_throw_pre, HCELL n_throw_leaf) = eps
S_throw_pre.PARAMETERBACKINGS = eps /\ S_throw_pre.PROPREFS = eps /\ S_throw_pre.REFCOERCIONS = eps /\ S_throw_pre.CONTAINERINITS = eps
$positional_reference_notice_source(S_throw_pre, pcalltarget_throw, 0, (porigin_throw_call))
$asf_output(S_throw_pre.EVENTS) = $ptascii("T;M;")
H_throw_pre = $heap_graph(S_throw_pre)
$heap_owners(H_throw_pre, HOBJECT n_throw_object) = 1 /\ $heap_owners(H_throw_pre, HCELL n_throw_leaf) = 1
$heap_valid(H_throw_pre) /\ $call_descriptors_valid(S_throw_pre)
""".strip().splitlines()

FRONT = r"""
~$named_reference_notice_object_slots(S_pre, pobjectprops.SLOTS)
~$named_reference_notice_object(S_pre, POBJECT n_object)
~$positional_reference_notice_pending(S_pre)
S_direct = S_pre[.OBJECTPROPS = $objectprops_set(S_pre.OBJECTPROPS, n_object, [ppropertyslot_a[.STATE = PROP_VALUE (DIRECT pvalue_original)], ppropertyslot_b[.STATE = PROP_VALUE (DIRECT pvalue_original)]])]
$named_reference_notice_object(S_direct, POBJECT n_object) /\ $positional_reference_notice_pending(S_direct)
S_fenced = $drive(S_pre, 1)
S_fenced.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_fenced.EVENTS = S_pre.EVENTS /\ S_fenced.STORE = S_pre.STORE ++ [DEFINED (POBJECT n_object)]
~$named_reference_notice_object(S_throw_pre, POBJECT n_throw_object) /\ ~$positional_reference_notice_pending(S_throw_pre)
S_throw_direct = S_throw_pre[.OBJECTPROPS = $objectprops_set(S_throw_pre.OBJECTPROPS, n_throw_object, [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_throw))}])]
$named_reference_notice_object(S_throw_direct, POBJECT n_throw_object) /\ $positional_reference_notice_pending(S_throw_direct)
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    assert args.front
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    selected = [0, 1]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    for i in selected:
        case, record = cases[i], records[cases[i]['id']]
        assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == record['source_sha256']
        assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in selected:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
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
    reached = [initial('S_initial', 0)] + RETURN + COMMON + [initial('S_throw_initial', 1)] + THROW
    derived = FRONT
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    paths += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        paths += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'stdclass-alias-scalar-field-front', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
