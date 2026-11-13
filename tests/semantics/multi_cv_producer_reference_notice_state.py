#!/usr/bin/env python3
"""Ground multiple-CV snapshots, true caller unset, formal retirement and compiled Notice lines."""
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
CATALOGUE = Path(__file__).with_name('multi_cv_producer_reference_notice_cases.json')

PREFIX = r"""
dec $mcv_output(pevent*) : ptbytes
def $mcv_output(eps) = eps
def $mcv_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mcv_output(pevent*)
dec $mcv_ready(pstate, nat) : bool
def $mcv_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* 2 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("MultiCvNotice49\\make") \/ pfunction.NAME = $ptascii("MultiCvThrow49\\make")
def $mcv_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("MultiCvNotice49\\make") \/ pcallcontext.NAME = $ptascii("MultiCvThrow49\\make")
def $mcv_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("MultiCvNotice49\\take") \/ pfunction.NAME = $ptascii("MultiCvThrow49\\take")
def $mcv_ready(S, 3) = true
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $mcv_output(S.EVENTS) = $ptascii("K;M:17:23:0;F:23:17;U:0;R:X7:31:37:1;")
def $mcv_ready(S, n_stage) = false -- otherwise
dec $mcv_seek(pstate, nat, nat) : pstate
def $mcv_seek(S, n_stage, n) = S -- if $mcv_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $mcv_seek(S, n_stage, n) = $mcv_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mcv_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $mcv_seek(S, n_stage, n) = S -- otherwise
"""

COMMON = r"""
S_initial.COMPLETION = BUDGET
S_args = $mcv_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$mcv_ready(S_args, 0)
$lookup(S_args.ENV, $ptascii("x")) = (n_original_x)
$lookup(S_args.ENV, $ptascii("y")) = (n_y)
$lookup(S_args.ENV, $ptascii("yAlias")) = (n_y)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S_args.ENV, $ptascii("wOld")) = (n_weak_cv)
S_args.STORE[n_original_x] = DEFINED (POBJECT n_object)
S_args.STORE[n_y] = DEFINED (PINT 5)
S_args.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))
$string_carrier_valid(S_args, pvalue_original)
S_args.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)
$weakref_get(S_args, n_weak) = POBJECT n_object
S_args.TODO = (CALL_ARGS pcalltarget_producer eps 2 ([KNOWN (POBJECT n_object), REFERENCE n_y]) (porigin_producer_call) z_producer) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam_first, psparam_last]
~psparam_first.BYREF /\ psparam_last.BYREF
psparam_first.NAME = $ptascii("saved") /\ psparam_last.NAME = $ptascii("changed")
psparam_first.TYPE = eps /\ psparam_last.TYPE = eps
psparam_first.REQUIRED /\ psparam_last.REQUIRED /\ ~psparam_first.VARIADIC /\ ~psparam_last.VARIADIC
pfunction_producer.SIGNATURE.RETURNS = eps /\ ~pfunction_producer.SIGNATURE.BYREF
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17_first, phpType17_last])) ABSENT phpType23 metadata_function)
$objectprops_record_at(S_args.OBJECTPROPS, n_object) = (pobjectprops_original)
pobjectprops_original.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT pvalue_original))}]
H_args = $heap_graph(S_args)
$heap_owners(H_args, HOBJECT n_object) = 2 /\ $heap_owners(H_args, HCELL n_y) = 4
$heap_valid(H_args) /\ $call_descriptors_valid(S_args)
S_return = $mcv_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]
$mcv_ready(S_return, 1)
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
$lookup(S_return.ENV, $ptascii("saved")) = (n_saved)
$lookup(S_return.ENV, $ptascii("changed")) = (n_y)
n_saved =/= n_original_x /\ n_saved =/= n_y /\ ~(n_saved <- S_return.REFCELLS)
S_return.STORE[n_saved] = DEFINED (POBJECT n_object)
S_return.STORE[n_y] = DEFINED (PINT 23)
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("x")) = eps
$lookup(psymboltable_caller.ENV, $ptascii("y")) = (n_y)
$lookup(psymboltable_caller.ENV, $ptascii("yAlias")) = (n_y)
H_formals = $heap_graph(S_return)
$heap_owners(H_formals, HOBJECT n_object) = 1 /\ $heap_owners(H_formals, HCELL n_y) = 4
$heap_valid(H_formals) /\ $call_descriptors_valid(S_return)
S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (POBJECT n_object)) porigin_return?) :: ptask_return*
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HOBJECT n_object) = 2
$heap_valid(H_return)
S_pre = $mcv_seek(S_after_return, 2, 5000)[.COMPLETION = NORMAL]
$mcv_ready(S_pre, 2)
S_pre.TODO = (CALL_SEND pcalltarget eps 1 ([REFERENCE n_y]) (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (POBJECT n_object)
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, $ptascii("x")) = eps
$lookup(S_pre.ENV, $ptascii("y")) = (n_y)
S_pre.STORE[n_y] = DEFINED (PINT 23)
~((HCELL n_saved) <- S_pre.ALLOCATIONS)
$lookup(S_pre.ENV, $ptascii("saved")) = eps /\ $lookup(S_pre.ENV, $ptascii("changed")) = eps
$objectprops_record_at(S_pre.OBJECTPROPS, n_object) = (pobjectprops_original)
$named_reference_notice_object(S_pre, POBJECT n_object)
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HOBJECT n_object) = 1 /\ $heap_owners(H_pre, HCELL n_y) = 3
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$call_argument_origin(S_pre, (porigin_call), 1) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), 1) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([phpType7_first, phpType7_last])) metadata_call
phpType7_first = NArg ABSENT expression_first (BOOLEAN false) (BOOLEAN false) metadata_first_arg
phpType7_last = NArg ABSENT expression_last (BOOLEAN false) (BOOLEAN false) metadata_last_arg
expression_first = NExprVariable (BYTES text_first) metadata_first
expression_last = NExprVariable (BYTES text_last) metadata_last
$reference_cv(expression_first) = ($ptascii("x"))
$reference_cv(expression_last) = ($ptascii("y"))
porigin_producer = PORIGIN n_unit pcpath_producer
porigin_last = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1])
$origin_node(S_pre.SOURCES, porigin_last) = (expression_last)
$source_line(metadata_first) = 8 /\ $source_line(metadata_last) = 9
$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = 8
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE)
~$positional_reference_notice_pending(S_pre)
""".strip().splitlines()

QUIET = r"""
S_quiet = $mcv_seek(S_quiet_initial, 3, 10000)[.COMPLETION = NORMAL]
$mcv_ready(S_quiet, 3)
~$error_handler_eligible(S_quiet, 8)
$lookup(S_quiet.ENV, $ptascii("r")) = (n_quiet_private)
$lookup(S_quiet.ENV, $ptascii("yAlias")) = (n_quiet_y)
$lookup(S_quiet.ENV, $ptascii("x")) = (n_quiet_x)
$lookup(S_quiet.ENV, $ptascii("snapshot")) = (n_quiet_snapshot)
$lookup(S_quiet.ENV, $ptascii("wOld")) = (n_quiet_weak_cv)
S_quiet.STORE[n_quiet_private] = DEFINED (POBJECT n_quiet_object)
S_quiet.STORE[n_quiet_x] = DEFINED (PINT 37) /\ S_quiet.STORE[n_quiet_y] = DEFINED (PINT 31)
$objectprops_record_at(S_quiet.OBJECTPROPS, n_quiet_object) = (pobjectprops_quiet)
pobjectprops_quiet.SLOTS = [{DECL eps, NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PSTRING ($ptascii("X7")))))}]
S_quiet.STORE[n_quiet_snapshot] = DEFINED pvalue_quiet
pvalue_quiet = PSTRING_CARRIER (REQUEST_STRING n_quiet_string) ($ptascii("17"))
$string_carrier_valid(S_quiet, pvalue_quiet)
S_quiet.STORE[n_quiet_weak_cv] = DEFINED (POBJECT n_quiet_weak)
$weakref_get(S_quiet, n_quiet_weak) = POBJECT n_quiet_object
H_quiet = $heap_graph(S_quiet)
$heap_owners(H_quiet, HOBJECT n_quiet_object) = 1 /\ $heap_owners(H_quiet, HCELL n_quiet_y) = 2
$heap_valid(H_quiet) /\ $call_descriptors_valid(S_quiet)
S_quiet_full = $drive(S_quiet, 10000)
S_quiet_full.COMPLETION = NORMAL /\ S_quiet_full.CURRENT = eps /\ S_quiet_full.FRAMES = eps /\ S_quiet_full.TODO = eps
S_quiet_full.STORE[n_quiet_private] = DEFINED (PINT 41) /\ S_quiet_full.STORE[n_quiet_x] = DEFINED (PINT 37) /\ S_quiet_full.STORE[n_quiet_y] = DEFINED (PINT 43)
$lookup(S_quiet_full.ENV, $ptascii("y")) = eps
~((HOBJECT n_quiet_object) <- S_quiet_full.ALLOCATIONS)
$weakref_get(S_quiet_full, n_quiet_weak) = PNULL
$heap_owners($heap_graph(S_quiet_full), HCELL n_quiet_y) = 1
$string_carrier_valid(S_quiet_full, pvalue_quiet)
$heap_valid($heap_graph(S_quiet_full)) /\ $call_descriptors_valid(S_quiet_full)
""".strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    assert args.front, 'only pre-law front is prepared'
    native_paths = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in native_paths]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {}
    for native in natives:
        for row in native['records']:
            assert row['id'] not in records
            records[row['id']] = row
    selected = [0, 1, 2]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for native in natives:
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
    case_specs = []
    reached = []
    derived = []
    for i in (0, 1):
        conditions = [initial('S_initial', i)] + COMMON
        conditions += ['$mcv_output(S_pre.EVENTS) = $ptascii(' + json.dumps(('A' if i == 0 else 'T') + ';M:17:23:0;') + ')']
        case_specs.append('dec $mcv_case' + str(i) + '() : bool\ndef $mcv_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions))
        reached += conditions
    quiet_conditions = [initial('S_quiet_initial', 2)] + QUIET
    quiet_conditions += ['$mcv_output(S_quiet_full.EVENTS) = $ptascii(' + json.dumps(cases[2]['native_stdout']) + ')']
    reached += quiet_conditions
    case_specs.append('dec $mcv_case2() : bool\ndef $mcv_case2() = true\n' + ''.join('  -- if ' + line + '\n' for line in quiet_conditions))
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $mcv_case0()\n  -- if $mcv_case1()\n  -- if $mcv_case2()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'multi-cv-producer-front', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
