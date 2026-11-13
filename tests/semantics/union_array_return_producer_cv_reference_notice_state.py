#!/usr/bin/env python3
"""Check actual ordered array/null union return normalization before the old Notice fence."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
from reference_send_notice_review_state import PREFIX
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('union_array_return_producer_cv_reference_notice_cases.json')


RETURN = r'''
S_initial.COMPLETION = BUDGET
S_return = $rsn_find(S_initial[.COMPLETION = NORMAL], 2000, 2)
$rsn_stage(S_return, 2)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.CURRENT = (pcallcontext_return)
$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)
pfunction_producer.NAME = $ptascii("UnionArrayReturnProducer37\\make")
~pfunction_producer.SIGNATURE.BYREF
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
$typed_return_task_valid(S_return, z_return)
$lookup(S_return.ENV, $ptascii("input")) = (n_source_return)
S_return.STORE[n_source_return] = DEFINED (PINT 17)
n_source_return <- S_return.REFCELLS
$lookup(S_return.ENV, $ptascii("leaf")) = (n_leaf)
S_return.STORE[n_leaf] = DEFINED (PINT 5)
S_return.RESULT = KNOWN (PARRAY n_root)
S_return.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
S_return.FRAMES = [pframe_caller]
pframe_caller.LOCALS = eps
S_return.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("source")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("sourceAlias")) = (n_source_return)
$lookup(psymboltable_caller.ENV, $ptascii("leaf")) = (n_leaf)
S_return.PARAMETERBACKINGS = eps
$propref_at(S_return.PROPREFS, n_source_return) = eps /\ $reference_coercion_at(S_return.REFCOERCIONS, n_source_return) = eps
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.ALLOCATIONS = S_return.ALLOCATIONS /\ S_checked.PARAMETERBACKINGS = eps
S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_return_step = $drive(S_return, 1)
S_return_step.COMPLETION = BUDGET
S_after_return = S_return_step[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_return_tail*
S_after_return.CURRENT = S_return.CURRENT /\ S_after_return.ENV = S_return.ENV
$task_nodes(RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) = [HARRAY n_root]
H_return = $heap_graph(S_after_return)
$heap_owners(H_return, HARRAY n_root) = 1
$heap_owners(H_return, HCELL n_source_return) = 3 /\ $heap_owners(H_return, HCELL n_leaf) = 3
$heap_valid(H_return) /\ $call_descriptors_valid(S_after_return)
'''.strip().splitlines()

COMMON = r'''
S_pre = $rsn_find(S_after_return, 2000, 0)
$rsn_stage(S_pre, 0)
S_pre.COMPLETION = NORMAL /\ S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_pre, pfunction_producer)
$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer
phpType6_producer = SEQUENCE ([NArg ABSENT expression_input (BOOLEAN false) (BOOLEAN false) metadata_input])
$reference_cv(expression_input) = ($ptascii("source"))
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
pssignature = pfunction_producer.SIGNATURE
pssignature.PARAMETERS = [psparam]
psparam.BYREF /\ psparam.TYPE = eps /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
pssignature.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]
phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES text_null) metadata_null])) metadata_union
$ptlc($base64(text_null)) = $ptascii("null")
$ptlc($base64(text_return)) = $ptascii("array")
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pssignature)
$reference_notice_producer_arguments(phpType6_producer, phpType16, pssignature[.RETURNS = eps])
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$lookup(S_pre.ENV, $ptascii("source")) = (n_source_cv)
n_source_cv = n_source_return
$lookup(S_pre.ENV, $ptascii("sourceAlias")) = (n_source_cv)
S_pre.STORE[n_source_cv] = DEFINED (PINT 17)
n_source_cv <- S_pre.REFCELLS
$propref_at(S_pre.PROPREFS, n_source_cv) = eps /\ $reference_coercion_at(S_pre.REFCOERCIONS, n_source_cv) = eps
$parameter_backing_at(S_pre.PARAMETERBACKINGS, n_source_cv) = eps
$node_children(S_pre, HCELL n_source_cv) = eps
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
S_pre.STORE[n_leaf] = DEFINED (PINT 5)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$named_reference_notice_array(S_pre, PARRAY n_root)
S_pre.PARAMETERBACKINGS = eps
$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps
$rsn_outputs(S_pre.EVENTS) = $ptascii("W;M:17;")
H_pre = $heap_graph(S_pre)
$heap_owners(H_pre, HARRAY n_root) = 1
$heap_owners(H_pre, HCELL n_source_cv) = 2 /\ $heap_owners(H_pre, HCELL n_leaf) = 2
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()

PRIMARY = r'''
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)
~$positional_reference_notice_pending(S_pre)
S_blocked = $drive(S_pre, 1)
S_blocked.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
$rsn_outputs(S_blocked.EVENTS) = $ptascii("W;M:17;")
$rsn_diagnostics(S_blocked.EVENTS) = eps
'''.strip().splitlines()

PRIMARY_CONTROLS = r'''
$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.RETURNS = eps])
$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES text_return) metadata_return, pssignature[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
$reference_notice_producer_header(phpType6_producer, phpType16, NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_union, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, NIdentifier (BYTES text_return) metadata_return, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, ABSENT, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.RETURNS = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "array"]))]])
~$reference_notice_producer_header(phpType6_producer, phpType16, NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") metadata_return, NIdentifier (BYTES text_null) metadata_null])) metadata_union, pssignature)
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.BYREF = false]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.REQUIRED = false]]])
~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature[.PARAMETERS = [psparam[.VARIADIC = true]]])
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    case = json.loads(CATALOGUE.read_bytes())[0]
    record, = [row for row in native['records'] if row['id'] == case['id']]
    source = Path(record['command'][-1])
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
    assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == record['source_sha256']
    assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
    assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    function = 'UnionArrayReturnProducer37\\take'
    stage = ('\ndef $rsn_stage(S, 0) = true\n'
        '  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*\n'
        '  -- if S.RESULT = KNOWN (PARRAY n_root)\n'
        '  -- if $target_function(S, pcalltarget) = (pfunction)\n'
        '  -- if pfunction.NAME = $ptascii(' + json.dumps(function) + ')\n'
        'def $rsn_stage(S, 1) = true\n'
        '  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*\n'
        '  -- if $rsn_outputs(S.EVENTS) = $ptascii("W;M:17;H;")\n'
        'def $rsn_stage(S, 2) = true\n'
        '  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*\n'
        '  -- if S.CURRENT = (pcallcontext)\n'
        '  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)\n'
        '  -- if pfunction.NAME = $ptascii(' + json.dumps('UnionArrayReturnProducer37\\make') + ')\n'
        'def $rsn_stage(S, n_stage) = false -- otherwise\n')
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + RETURN + COMMON + PRIMARY
    derived = PRIMARY_CONTROLS
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + stage + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in reached + derived))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, native_path, Path(record['stdout']), Path(record['stderr']), Path(__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/reference_send_notice_review_state.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'part': 'union-array-return-baseline-front', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('union-array-return-baseline-front', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
