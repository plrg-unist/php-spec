#!/usr/bin/env python3
"""Ground singleton nullable returns, captured values and retired producer frames."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_nullable_scalar_return_producer_reference_notice_cases.json')
PREFIX = r'''
dec $scnr_output(pevent*) : ptbytes
def $scnr_output(eps) = eps
def $scnr_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $scnr_output(pevent*)
dec $scnr_ready(pstate, nat) : bool
def $scnr_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("SingletonNullableIntReturn60\\make"), $ptascii("SingletonNullableFloatReturn60\\make")]
def $scnr_ready(S, 1) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("SingletonNullableIntReturn60\\make"), $ptascii("SingletonNullableFloatReturn60\\make")]
def $scnr_ready(S, 2) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("SingletonNullableIntReturn60\\make"), $ptascii("SingletonNullableFloatReturn60\\make")]
def $scnr_ready(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("SingletonNullableIntReturn60\\take"), $ptascii("SingletonNullableFloatReturn60\\take")]
def $scnr_ready(S, 4) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("SingletonNullableIntReturn60\\take"), $ptascii("SingletonNullableFloatReturn60\\take")]
def $scnr_ready(S, n_stage) = false -- otherwise
dec $scnr_seek(pstate, nat, nat) : pstate
def $scnr_seek(S, n_stage, n) = S -- if $scnr_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $scnr_seek(S, n_stage, n) = $scnr_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$scnr_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scnr_seek(S, n_stage, n) = S -- otherwise
'''


def front_lines(index, case):
    byref = case['formal_byref']
    raw_type = '(NIdentifier (BYTES text_type) metadata_type)'
    if byref:
        raw_type = '(NNullableType ' + raw_type + ' metadata_nullable)'
    normalized = '[(PTBRANCH ([PTBUILTIN "' + case['formal_kind'] + '"]))' + (', (PTBRANCH ([PTBUILTIN "null"]))' if byref else '') + ']'
    lines = r'''
S_initial.COMPLETION = BUDGET
S_args = $scnr_seek(S_initial, 0, 4000)[.COMPLETION = NORMAL]
$scnr_ready(S_args, 0)
$lookup(S_args.ENV, $ptascii("x")) = (n_source)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
S_args.STORE[n_source] = DEFINED pvalue_original
S_args.STORE[n_snapshot] = DEFINED pvalue_original
S_args.TODO = (CALL_ARGS pcalltarget_producer eps 1 ([OPERAND]) (porigin_producer_call) z_producer) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.BYREF = RAW_BYREF /\ ~psparam.VARIADIC /\ psparam.REQUIRED /\ psparam.DEFAULT = PSNONE
psparam.TYPE = NORMALIZED
pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "RETURN_KIND"])), (PTBRANCH ([PTBUILTIN "null"]))]
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 (SEQUENCE ([phpType17])) phpType18 phpType23 metadata_function)
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) RAWTYPE (BOOLEAN RAW_BYREF) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
phpType17 = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter
$ptlc($base64(text_type)) = $ptascii("FORMAL_KIND")
phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return_nullable
$ptlc($base64(text_return)) = $ptascii("RETURN_KIND")
$heap_valid($heap_graph(S_args)) /\ $call_descriptors_valid(S_args)
S_receive = $scnr_seek(S_args, 1, 5000)[.COMPLETION = NORMAL]
$scnr_ready(S_receive, 1)
$typed_receive_valid(S_receive, pfunction_producer.ORIGIN, 0)
~$typed_caller_strict(S_receive)
$lookup(S_receive.ENV, psparam.NAME) = (n_formal)
S_receive.STORE[n_formal] = DEFINED pvalue_original
$typed_parameter_conversion(S_receive, psparam, pvalue_original) = TYPEVALUE pvalue_original
S_received_budget = $drive_steps(S_receive, 1)
S_received_budget.COMPLETION = BUDGET
S_received = S_received_budget[.COMPLETION = NORMAL]
S_received.STORE[n_formal] = DEFINED pvalue_original
S_received.STORE[n_snapshot] = DEFINED pvalue_original
$parameter_backing_at(S_received.PARAMETERBACKINGS, n_formal) = eps
$propref_at(S_received.PROPREFS, n_formal) = eps
$reference_coercion_at(S_received.REFCOERCIONS, n_formal) = eps
$heap_valid($heap_graph(S_received)) /\ $call_descriptors_valid(S_received)
S_return = $scnr_seek(S_received, 2, 5000)[.COMPLETION = NORMAL]
$scnr_ready(S_return, 2)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
S_return.RESULT = VARIABLE psparam.NAME z_read
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_original
$typed_return_task_valid(S_return, z_return)
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN pvalue_result
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_after_return_budget = $drive(S_return, 1)
S_after_return_budget.COMPLETION = BUDGET
S_after_return = S_after_return_budget[.COMPLETION = NORMAL]
S_after_return.TODO = (RETURN_UNWIND (KNOWN pvalue_result) porigin_return?) :: ptask_unwind*
S_pre = $scnr_seek(S_after_return, 3, 5000)[.COMPLETION = NORMAL]
$scnr_ready(S_pre, 3)
S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN pvalue_result
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, psparam.NAME) = eps
S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), 0) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE ([phpType7])) metadata_call
phpType7 = NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN false) metadata_arg
expression_actual = NExprVariable (BYTES text_name) metadata_actual
$reference_cv(expression_actual) = ($ptascii("x"))
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])
~$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)
~$positional_reference_notice_pending(S_pre)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()
    # Bind the concrete return value before its first verification premise.
    at = lines.index('S_checked = $typed_return_value(S_return, z_return)')
    lines.insert(at, 'pvalue_result = PNULL' if byref else 'pvalue_result = PINT 17')
    at = lines.index('S_args.STORE[n_source] = DEFINED pvalue_original') + 1
    lines.insert(at, 'pvalue_original = PNULL' if byref else 'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))')
    if byref:
        lines += ['$lookup(S_args.ENV, $ptascii("alias")) = (n_source)', 'n_formal = n_source',
            'n_source <- S_received.REFCELLS', '$heap_owners($heap_graph(S_received), HCELL n_source) = 3',
            'S_return.STORE[n_source] = DEFINED PNULL', 'S_return.GLOBALTABLE = (psymboltable_return)',
            '$lookup(psymboltable_return.ENV, $ptascii("x")) = eps',
            '$lookup(S_pre.ENV, $ptascii("x")) = eps', '$lookup(S_pre.ENV, $ptascii("alias")) = (n_source)',
            'S_pre.STORE[n_source] = DEFINED PNULL', '$heap_owners($heap_graph(S_pre), HCELL n_source) = 1']
    else:
        lines += [r'n_formal =/= n_source /\ ~(n_formal <- S_received.REFCELLS)',
            'S_received.STORE[n_source] = DEFINED pvalue_original', 'S_return.STORE[n_formal] = DEFINED pvalue_original',
            '$lookup(S_pre.ENV, $ptascii("x")) = (n_source)', 'S_pre.STORE[n_source] = DEFINED pvalue_original',
            '~((HCELL n_formal) <- S_pre.ALLOCATIONS)', '$string_carrier_valid(S_args, pvalue_original)',
            '$string_carrier_valid(S_pre, pvalue_original)']
    lines += ['$scnr_output(S_pre.EVENTS) = $ptascii(' + json.dumps(('N' if byref else 'I') + ';M:1:1;') + ')']
    values = {'RAWTYPE': raw_type, 'NORMALIZED': normalized, 'RAW_BYREF': str(byref).lower(),
              'FORMAL_KIND': case['formal_kind'], 'RETURN_KIND': case['return_kind'],
              'OPERAND': 'REFERENCE n_source' if byref else 'KNOWN pvalue_original'}
    for key, value in values.items():
        lines = [line.replace(key, value) for line in lines]
    return lines


def full_lines(index, case):
    byref = case['formal_byref']
    lines = r'''
n_private = |S_pre.STORE|
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call
perrorcall.LINE = NOTICE_LINE
S_notice.STORE[n_private] = DEFINED pvalue_result
n_private =/= n_source /\ n_private =/= n_formal
$error_call_valid(S_notice, perrorcall)
$node_children(S_notice, HCELL n_private) = eps
S_notice.PARAMETERBACKINGS = eps /\ S_notice.PROPREFS = eps /\ S_notice.REFCOERCIONS = eps
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_valid($heap_graph(S_notice)) /\ $call_descriptors_valid(S_notice)
S_resume = $scnr_seek(S_notice, 4, 7000)[.COMPLETION = NORMAL]
$scnr_ready(S_resume, 4)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED pvalue_result
$error_call_valid(S_resume, perrorcall)
S_full = $drive(S_resume, 20000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PINT FINAL_INT)
S_full.STORE[n_snapshot] = DEFINED pvalue_original
$node_children(S_full, HCELL n_private) = eps
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()
    if byref:
        lines += ['$lookup(S_resume.ENV, $ptascii("x")) = (n_new_source)',
            r'n_new_source =/= n_source /\ n_new_source =/= n_private',
            'S_resume.STORE[n_new_source] = DEFINED (PINT 37)', 'S_resume.STORE[n_source] = DEFINED (PINT 43)',
            '$lookup(S_full.ENV, $ptascii("alias")) = eps', '~((HCELL n_source) <- S_full.ALLOCATIONS)',
            'S_full.STORE[n_new_source] = DEFINED (PINT 37)']
    else:
        lines += ['S_resume.STORE[n_source] = DEFINED (PINT 23)', 'S_full.STORE[n_source] = DEFINED (PINT 23)',
                  '$string_carrier_valid(S_full, pvalue_original)']
    lines += ['$scnr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    return [line.replace('FINAL_INT', '47' if byref else '43').replace('NOTICE_LINE', str(case['observed_notice_line'])) for line in lines]


def controls(index, case):
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
    lines = ['~' + header + 'ABSENT, ' + signature + ')',
        '~' + header + 'phpType18, ' + signature + '[.RETURNS = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "' + case['return_kind'] + '"]))]])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        'S_zero = $drive(S_notice, 0)', r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
    for kind in ('array', 'int', 'float', 'bool', 'string'):
        raw = '(NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_return)'
        member = '(PTBRANCH ([PTBUILTIN "' + kind + '"]))'
        lines += [header + 'NNullableType ' + raw + ' metadata_return_nullable, ' + signature + '[.RETURNS = [' + member + ', (PTBRANCH ([PTBUILTIN "null"]))]])']
        for reverse in (False, True):
            nodes = [raw, '(NIdentifier (BYTES "bnVsbA==") metadata_return_nullable)']
            types = [member, '(PTBRANCH ([PTBUILTIN "null"]))']
            if reverse:
                nodes.reverse();types.reverse()
            lines += [header + 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_nullable, ' + signature + '[.RETURNS = [' + ', '.join(types) + ']])']
    for nullable in (False, True):
        param = 'phpType17_nullable_int' if nullable else 'phpType17_int'
        raw = '(NIdentifier (BYTES "aW50") metadata_type)'
        normalized = '[(PTBRANCH ([PTBUILTIN "int"]))' + (', (PTBRANCH ([PTBUILTIN "null"]))' if nullable else '') + ']'
        if nullable:
            raw = '(NNullableType ' + raw + ' metadata_type)'
        lines += [param + ' = NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
            header.replace('phpType17])', param + '])') + 'NNullableType (NIdentifier (BYTES "aW50") metadata_return) metadata_return_nullable, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]][.RETURNS = [(PTBRANCH ([PTBUILTIN "int"])), (PTBRANCH ([PTBUILTIN "null"]))]])']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    sources = {}
    for i, case in enumerate(cases):
        row = records[case['id']]
        sources[i] = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in sources:
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
    reached, derived, specs = [], [], []
    for i, case in enumerate(cases):
        initial = 'S_initial = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
        conditions = [initial] + front_lines(i, case)
        extra = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i, case)
        specs.append('dec $scnr_case' + str(i) + '() : bool\ndef $scnr_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scnr_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for case in cases:
        row = records[case['id']]
        paths += [Path(row['command'][-1]), Path(row['stdout']), Path(row['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('singleton-cv-nullable-scalar-return-front' if args.front else 'singleton-cv-nullable-scalar-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
