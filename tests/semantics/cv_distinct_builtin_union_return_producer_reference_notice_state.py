#!/usr/bin/env python3
"""Ground nonnull return coercion before frame retirement and private Notice cells."""
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
CATALOGUE = Path(__file__).with_name('cv_distinct_builtin_union_return_producer_reference_notice_cases.json')
PREFIX = r'''
dec $urn_output(pevent*) : ptbytes
def $urn_output(eps) = eps
def $urn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $urn_output(pevent*)
dec $urn_ready(pstate, nat) : bool
def $urn_ready(S, 0) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps n poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("DistinctBuiltinUnionIntReturn64\\make"), $ptascii("DistinctBuiltinUnionStringReturn64\\make")]
  -- if n = |pfunction.SIGNATURE.PARAMETERS|
def $urn_ready(S, 1) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("DistinctBuiltinUnionIntReturn64\\make"), $ptascii("DistinctBuiltinUnionStringReturn64\\make")]
def $urn_ready(S, 2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_SEND pcalltarget eps n poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("DistinctBuiltinUnionIntReturn64\\take"), $ptascii("DistinctBuiltinUnionStringReturn64\\take")]
def $urn_ready(S, 3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS pcalltarget eps n poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("DistinctBuiltinUnionIntReturn64\\take"), $ptascii("DistinctBuiltinUnionStringReturn64\\take")]
  -- if n = |pfunction.SIGNATURE.PARAMETERS|
def $urn_ready(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("DistinctBuiltinUnionStringReturn64\\take")
  -- if $urn_output(S.EVENTS) = $ptascii("S;M:1:1:1:1;H:8:0:body;F:29:1:1;")
def $urn_ready(S, n_stage) = false -- otherwise
dec $urn_seek(pstate, nat, nat) : pstate
def $urn_seek(S, n_stage, n) = S -- if $urn_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $urn_seek(S, n_stage, n) = $urn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$urn_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $urn_seek(S, n_stage, n) = S -- otherwise
'''


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + k + '"]))' for k in members) + ']'


def front_lines(index, case):
    count, position = case['argument_count'], case['consumer_index']
    original = 'PSTRING_CARRIER (REQUEST_STRING n_source_string) ($ptascii("17"))' if index == 0 else 'PINT 37'
    result = 'PINT 17' if index == 0 else 'PSTRING_CARRIER (REQUEST_STRING n_result_string) ($ptascii("37"))'
    args = '[KNOWN pvalue_original]' if index == 0 else '[KNOWN pvalue_original, REFERENCE n_y]'
    prefix = 'eps' if index == 0 else '([REFERENCE n_y])'
    lines = r'''
S_initial.COMPLETION = BUDGET
S_args = $urn_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]
$urn_ready(S_args, 0)
$lookup(S_args.ENV, $ptascii("x")) = (n_source)
$lookup(S_args.ENV, $ptascii("snapshot")) = (n_snapshot)
S_args.STORE[n_source] = DEFINED pvalue_original
S_args.STORE[n_snapshot] = DEFINED pvalue_original
pvalue_original = __ORIGINAL__
S_args.TODO = (CALL_ARGS pcalltarget_producer eps __COUNT__ __ARGS__ (porigin_producer_call) z_producer) :: ptask_args*
$target_function(S_args, pcalltarget_producer) = (pfunction_producer)
pfunction_producer.SIGNATURE.PARAMETERS = psparam*
|psparam*| = __COUNT__
psparam*[0].NAME = $ptascii("saved") /\ ~psparam*[0].BYREF
psparam*[0].TYPE = __FIRST_TYPE__
psparam*[0].REQUIRED /\ psparam*[0].DEFAULT = PSNONE /\ ~psparam*[0].VARIADIC
~pfunction_producer.SIGNATURE.BYREF /\ ~pfunction_producer.CODE.STRICT
pfunction_producer.SIGNATURE.RETURNS = __RETURN_TYPES__
$origin_node(S_args.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16_parameters phpType18_return phpType23 metadata_function)
phpType18_return = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first, NIdentifier (BYTES text_last) metadata_last])) metadata_union
$ptlc($base64(text_first)) = $ptascii("__FIRST_RETURN__") /\ $ptlc($base64(text_last)) = $ptascii("__LAST_RETURN__")
$heap_valid($heap_graph(S_args)) /\ $call_descriptors_valid(S_args)
S_return = $urn_seek(S_args, 1, 10000)[.COMPLETION = NORMAL]
$urn_ready(S_return, 1)
S_return.CURRENT = (pcallcontext)
$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
$lookup(S_return.ENV, $ptascii("saved")) = (n_formal)
n_formal =/= n_source /\ ~(n_formal <- S_return.REFCELLS)
S_return.STORE[n_formal] = DEFINED pvalue_original
S_return.STORE[n_snapshot] = DEFINED pvalue_original
S_return.RESULT = VARIABLE ($ptascii("saved")) z_read
$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN pvalue_original
$typed_return_task_valid(S_return, z_return)
$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, pvalue_original, pfunction_producer.CODE.STRICT) = __CONVERSION__
S_checked = $typed_return_value(S_return, z_return)
S_checked.COMPLETION = NORMAL
S_checked.RESULT = KNOWN pvalue_result
pvalue_result = __RESULT__
S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS
S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS /\ S_checked.PROPREFS = S_return.PROPREFS /\ S_checked.REFCOERCIONS = S_return.REFCOERCIONS
S_returned_budget = $drive(S_return, 1)
S_returned_budget.COMPLETION = BUDGET
S_returned = S_returned_budget[.COMPLETION = NORMAL]
S_returned.TODO = (RETURN_UNWIND (KNOWN pvalue_result) porigin_return?) :: ptask_unwind*
S_pre = $urn_seek(S_returned, 2, 10000)[.COMPLETION = NORMAL]
$urn_ready(S_pre, 2)
S_pre.TODO = (CALL_SEND pcalltarget eps __POSITION__ __PREFIX__ (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN pvalue_result
S_pre.CURRENT = eps /\ S_pre.FRAMES = eps
$lookup(S_pre.ENV, $ptascii("saved")) = eps
~((HCELL n_formal) <- S_pre.ALLOCATIONS)
S_pre.STORE[n_snapshot] = DEFINED pvalue_original
$call_argument_origin(S_pre, (porigin_call), __POSITION__) = (porigin_producer)
$call_argument_expression(S_pre, (porigin_call), __POSITION__) = expression_producer
expression_producer = NExprFuncCall phpType19 (SEQUENCE phpType7*) metadata_call
|phpType7*| = __COUNT__
$reference_notice_producer_target(S_pre, porigin_producer) = (pfunction_producer)
$reference_notice_producer_arguments(SEQUENCE phpType7*, phpType16_parameters, pfunction_producer.SIGNATURE[.RETURNS = eps])
~$reference_notice_producer_header(SEQUENCE phpType7*, phpType16_parameters, phpType18_return, pfunction_producer.SIGNATURE)
~$positional_reference_notice_pending(S_pre)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps
$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)
'''.strip().splitlines()
    if index == 0:
        lines += ['$lookup(S_pre.ENV, $ptascii("x")) = (n_source)', 'S_pre.STORE[n_source] = DEFINED pvalue_original', '$string_carrier_valid(S_args, pvalue_original)', '$string_carrier_valid(S_pre, pvalue_original)']
    else:
        lines += ['$lookup(S_args.ENV, $ptascii("y")) = (n_y)', '$lookup(S_args.ENV, $ptascii("yAlias")) = (n_y)', '$lookup(S_args.ENV, $ptascii("ySnapshot")) = (n_y_snapshot)', r'S_args.STORE[n_y] = DEFINED PNULL /\ S_args.STORE[n_y_snapshot] = DEFINED PNULL', r'psparam*[1].NAME = $ptascii("changed") /\ psparam*[1].BYREF', 'psparam*[1].TYPE = [(PTBRANCH ([PTBUILTIN "bool"])), (PTBRANCH ([PTBUILTIN "null"]))]', r'psparam*[1].REQUIRED /\ psparam*[1].DEFAULT = PSNONE /\ ~psparam*[1].VARIADIC', '$lookup(S_return.ENV, $ptascii("changed")) = (n_y)', 'S_return.STORE[n_y] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))', '$lookup(S_pre.ENV, $ptascii("x")) = eps', '$lookup(S_pre.ENV, $ptascii("y")) = (n_y)', '$lookup(S_pre.ENV, $ptascii("yAlias")) = (n_y)', 'S_pre.STORE[n_y] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))', '$heap_owners($heap_graph(S_pre), HCELL n_y) = 3', '$string_carrier_valid(S_checked, pvalue_result)', '$string_carrier_valid(S_pre, pvalue_result)']
    lines += ['$urn_output(S_pre.EVENTS) = $ptascii(' + json.dumps('I;M:1:1;' if index == 0 else 'S;M:1:1:1:1;') + ')']
    values = dict(__ORIGINAL__=original, __COUNT__=str(count), __ARGS__='(' + args + ')', __FIRST_TYPE__=branches([case['formal_kinds'][0]]), __RETURN_TYPES__=branches(case['return_members']), __FIRST_RETURN__=case['return_members'][0], __LAST_RETURN__=case['return_members'][1], __CONVERSION__='TYPEVALUE (PINT 17)' if index == 0 else 'TYPESTRING (PINT 37)', __RESULT__=result, __POSITION__=str(position), __PREFIX__=prefix)
    for key, value in values.items():
        lines = [line.replace(key, value) for line in lines]
    return lines


def full_lines(index, case):
    count, position = case['argument_count'], case['consumer_index']
    operands = '[REFERENCE n_private]' if index == 0 else '[REFERENCE n_y, REFERENCE n_private]'
    lines = r'''
n_private = |S_pre.STORE|
S_notice_budget = $drive(S_pre, 1)
S_notice_budget.COMPLETION = BUDGET
S_notice = S_notice_budget[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps __COUNT__ __OPERANDS__ (porigin_call) z_call
perrorcall.LINE = __NOTICE_LINE__ /\ perrorcall.LEVEL = 8
S_notice.STORE[n_private] = DEFINED pvalue_result
n_private =/= n_source /\ n_private =/= n_formal
n_private <- S_notice.REFCELLS
$error_call_valid(S_notice, perrorcall)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
S_notice.PARAMETERBACKINGS = eps /\ S_notice.PROPREFS = eps /\ S_notice.REFCOERCIONS = eps
$heap_valid($heap_graph(S_notice)) /\ $call_descriptors_valid(S_notice)
S_resume = $urn_seek(S_notice, 3, 10000)[.COMPLETION = NORMAL]
$urn_ready(S_resume, 3)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED pvalue_result
$error_call_valid(S_resume, perrorcall)
$heap_valid($heap_graph(S_resume)) /\ $call_descriptors_valid(S_resume)
'''.strip().splitlines()
    if index == 0:
        lines += ['S_resume.STORE[n_source] = DEFINED (PINT 23)']
    else:
        lines += ['$lookup(S_resume.ENV, $ptascii("x")) = (n_new_source)', r'n_new_source =/= n_source /\ n_new_source =/= n_private', r'S_resume.STORE[n_new_source] = DEFINED (PINT 37) /\ S_resume.STORE[n_y] = DEFINED (PINT 29)', '$string_carrier_valid(S_resume, pvalue_result)', 'S_cow = $urn_seek(S_resume, 4, 10000)[.COMPLETION = NORMAL]', '$urn_ready(S_cow, 4)', '$lookup(S_cow.ENV, $ptascii("local")) = (n_local)', 'S_cow.STORE[n_local] = DEFINED pvalue_result', 'S_cow.STORE[n_private] = DEFINED pvalue_cow', '$string_bytes(pvalue_cow) = ($ptascii("X7"))', '$string_carrier_valid(S_cow, pvalue_result)', r'$heap_valid($heap_graph(S_cow)) /\ $call_descriptors_valid(S_cow)']
    lines += ['S_full = $drive(' + ('S_resume' if index == 0 else 'S_cow') + ', 30000)', r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps', '$lookup(S_full.ENV, $ptascii("r")) = (n_private)', 'S_full.STORE[n_private] = DEFINED (PINT ' + ('43' if index == 0 else '47') + ')', 'S_full.STORE[n_snapshot] = DEFINED pvalue_original', r'S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps', r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)', '$urn_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    if index == 0:
        lines += ['S_full.STORE[n_source] = DEFINED (PINT 23)', '$string_carrier_valid(S_full, pvalue_original)']
    else:
        lines += [r'S_full.STORE[n_new_source] = DEFINED (PINT 37) /\ S_full.STORE[n_y] = DEFINED (PINT 53)', 'S_full.STORE[n_y_snapshot] = DEFINED PNULL', r'$lookup(S_full.ENV, $ptascii("y")) = eps /\ $lookup(S_full.ENV, $ptascii("yAlias")) = (n_y)', '~((HCELL n_local) <- S_full.ALLOCATIONS)', '$heap_owners($heap_graph(S_full), HCELL n_y) = 1']
    for key, value in dict(__COUNT__=str(count), __OPERANDS__='(' + operands + ')', __NOTICE_LINE__=str(case['observed_notice_line'])).items():
        lines = [line.replace(key, value) for line in lines]
    return lines


def controls(index):
    header = '$reference_notice_producer_header(SEQUENCE phpType7*, phpType16_parameters, '
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))', '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])', '~' + header + 'ABSENT, ' + signature + ')', '~' + header + 'phpType18_return, ' + signature + '[.RETURNS = [' + signature + '.RETURNS[1], ' + signature + '.RETURNS[0]]])', 'S_zero = $drive(S_notice, 0)', r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice', '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
    kinds = ['array', 'int', 'float', 'bool', 'string']
    for first in kinds:
        for last in kinds:
            if first == last:
                continue
            raw = 'NUnionType (SEQUENCE ([' + ', '.join('NIdentifier (BYTES "' + base64.b64encode(k.encode()).decode() + '") metadata_first' for k in (first, last)) + '])) metadata_union'
            lines.append(header + raw + ', ' + signature + '[.RETURNS = ' + branches([first, last]) + '])')
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_paths = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in native_paths]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {}
    for native in natives:
        for row in native['records']:
            assert row['id'] not in records
            records[row['id']] = row
    selected = [0, 1]
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
    for i in selected:
        conditions = [initial('S_initial', i)] + front_lines(i, cases[i])
        current_derived = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line.startswith('~$reference_notice_producer_arguments(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, cases[i])
            current_derived = controls(i)
        case_specs.append('dec $mcsf_case' + str(i) + '() : bool\ndef $mcsf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcsf_case' + str(i) + '()\n' for i in selected))
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
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'cv-distinct-builtin-union-return-producer-front' if args.front else 'cv-distinct-builtin-union-return-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
