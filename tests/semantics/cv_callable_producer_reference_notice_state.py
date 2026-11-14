#!/usr/bin/env python3
"""Reach callable verification, producer retirement and private Notice cells."""
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
CATALOGUE = Path(__file__).with_name('cv_callable_producer_reference_notice_cases.json')
PREFIX = r"""
dec $cn_output(pevent*) : ptbytes
def $cn_output(eps) = eps
def $cn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $cn_output(pevent*)
dec $cn_ready(pstate, nat) : bool
def $cn_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("CallableSingletonByval82\\make"), $ptascii("CallableSingletonByref82\\make"), $ptascii("CallableMulti82\\make")]
def $cn_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- [$ptascii("CallableSingletonByval82\\take"), $ptascii("CallableSingletonByref82\\take"), $ptascii("CallableMulti82\\take")]
def $cn_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $cn_output(S.EVENTS) <- [$ptascii("N;M:1;H:9;"), $ptascii("N;M:17;H:10:1;"), $ptascii("N;M:1:23:0;H:9:0:23;")]
def $cn_ready(S, n_stage) = false -- otherwise
dec $cn_seek(pstate, nat, nat) : pstate
def $cn_seek(S, n_stage, n) = S
  -- if $cn_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $cn_seek(S, n_stage, n) = $cn_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$cn_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cn_seek(S, n_stage, n) = S -- otherwise
"""
CALLABLE = '[(PTBRANCH ([PTBUILTIN "callable"]))]'


def reached(case, front):
    multiple, byref = case['multiple'], case['byref']
    previous = '([REFERENCE n_y])' if multiple else 'eps'
    index = 1 if multiple else 0
    raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parameter) metadata_type) (BOOLEAN ' + str(byref).lower() + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    parameters = '[' + raw_parameter + (', NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last' if multiple else '') + ']'
    lines = [
        'S_initial.COMPLETION = BUDGET',
        'S_return = $cn_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$cn_ready(S_return, 0)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'S_return.CURRENT = (pcallcontext_return)',
        '$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\make') + ')',
        '~pfunction_producer.SIGNATURE.BYREF',
        'pfunction_producer.SIGNATURE.RETURNS = ' + CALLABLE,
        ('pfunction_producer.CODE.STRICT' if byref else '~pfunction_producer.CODE.STRICT'),
        '$typed_return_task_valid(S_return, z_return)',
        '$lookup(S_return.ENV, $ptascii("saved")) = (n_saved)',
        'S_return.STORE[n_saved] = DEFINED pvalue_original',
        '$string_bytes(pvalue_original) = (ptbytes_name)',
        'pvalue_original = PSTRING_CARRIER ' + ('(REQUEST_STRING n_string)' if multiple else 'INTERNED_STRING') + ' ptbytes_name',
        '$string_carrier_valid(S_return, pvalue_original)',
        '~$pfunction_builtin($typed_callable_name(ptbytes_name))',
        '$callable_at(S_return.CALLABLES, $ptlc($typed_callable_name(ptbytes_name))) = (porigin_target)',
        '$function_at(S_return.FUNCTIONS, porigin_target) = (pfunction_target)',
        '$typed_registered(S_return, ptbytes_name)',
        '$typed_callable(S_return, pvalue_original) = (true)',
        'S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)',
        'S_resolved.RESULT = KNOWN pvalue_original',
        '$typed_return_value(S_return, z_return) = S_resolved',
        'S_return.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii("copy")) = (n_copy)',
        'S_return.STORE[n_copy] = DEFINED pvalue_original',
        'n_copy =/= n_saved',
        'S_return.PROPREFS = eps /\\ S_return.REFCOERCIONS = eps /\\ S_return.PARAMETERBACKINGS = eps',
        'S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN pvalue_original) porigin_return?) :: ptask_return_tail*',
        '$heap_valid($heap_graph(S_after_return)) /\\ $call_descriptors_valid(S_after_return)',
        'S_pre = $cn_seek(S_after_return, 1, 2000)[.COMPLETION = NORMAL]',
        '$cn_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps ' + str(index) + ' ' + previous + ' (porigin_call) z) :: ptask_tail*',
        'S_pre.RESULT = KNOWN pvalue_original',
        'S_pre.CURRENT = eps /\\ S_pre.FRAMES = eps',
        '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
        'S_pre.STORE[n_copy] = DEFINED pvalue_original',
        '$string_carrier_valid(S_pre, pvalue_original)',
        '$call_argument_origin(S_pre, (porigin_call), ' + str(index) + ') = (porigin_argument)',
        '$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)',
        '$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        '$call_argument_expression(S_pre, (porigin_call), ' + str(index) + ') = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType16 = SEQUENCE (' + parameters + ')',
        'pfunction_producer.SIGNATURE.PARAMETERS = ' + ('[psparam, psparam_last]' if multiple else '[psparam]'),
        'psparam.TYPE = ' + CALLABLE + ' /\\ ' + ('psparam.BYREF' if byref else '~psparam.BYREF'),
        'psparam.REQUIRED /\\ ~psparam.VARIADIC /\\ psparam.DEFAULT = PSNONE',
        '$ptlc($base64(text_parameter)) = $ptascii("callable")',
        'phpType18 = NIdentifier (BYTES text_return) metadata_return',
        '$ptlc($base64(text_return)) = $ptascii("callable")',
        ('~' if front else '') + '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        ('~' if front else '') + '$positional_reference_notice_pending(S_pre)',
        'S_pre.PROPREFS = eps /\\ S_pre.REFCOERCIONS = eps /\\ S_pre.PARAMETERBACKINGS = eps',
        '$heap_valid($heap_graph(S_pre)) /\\ $call_descriptors_valid(S_pre)']
    if multiple:
        lines += ['$lookup(S_pre.ENV, $ptascii("x")) = eps',
            '$lookup(S_pre.ENV, $ptascii("yAlias")) = (n_y)',
            'S_pre.STORE[n_y] = DEFINED (PINT 23)',
            'psparam_last.TYPE = eps /\\ psparam_last.BYREF /\\ psparam_last.REQUIRED /\\ ~psparam_last.VARIADIC /\\ psparam_last.DEFAULT = PSNONE']
    else:
        lines += ['$lookup(S_pre.ENV, $ptascii("x")) = (n_source)',
            '$lookup(S_pre.ENV, $ptascii("alias")) = (n_source)',
            'S_pre.STORE[n_source] = DEFINED pvalue_original',
            '$heap_owners($heap_graph(S_pre), HCELL n_source) = 2']
    lines += (['n_saved = n_source'] if byref else ['~((HCELL n_saved) <- S_pre.ALLOCATIONS)', '$heap_owners($heap_graph(S_pre), HCELL n_saved) = 0'])
    return lines


def completed(case):
    multiple = case['multiple']
    index = 1 if multiple else 0
    sent = '([REFERENCE n_y, REFERENCE n_private])' if multiple else '([REFERENCE n_private])'
    return [
        '$named_reference_notice_root_value(S_pre, pvalue_original)',
        'n_private = |S_pre.STORE|',
        'n_private =/= n_copy',
        'S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*',
        'perrorcall.RESUME = CALL_ARGS pcalltarget eps ' + str(index + 1) + ' ' + sent + ' (porigin_call) z',
        'perrorcall.LEVEL = 8 /\\ perrorcall.LINE = ' + str(case['notice_line']),
        'S_notice.STORE[n_private] = DEFINED pvalue_original',
        '$error_call_valid(S_notice, perrorcall)',
        '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        '$node_children(S_notice, HCELL n_private) = eps',
        'S_resume = $cn_seek(S_notice, 2, 4000)[.COMPLETION = NORMAL]',
        '$cn_ready(S_resume, 2)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$error_call_valid(S_resume, perrorcall)',
        'S_resume.STORE[n_private] = DEFINED pvalue_original /\\ S_resume.STORE[n_copy] = DEFINED pvalue_original',
        '$lookup(S_resume.ENV, $ptascii("x")) = (n_changed)',
        'S_resume.STORE[n_changed] = DEFINED (PINT 37)',
        'n_changed =/= n_private',
        '$string_carrier_valid(S_resume, pvalue_original)',
        'S_resume.STRINGDATA[0:|S_notice.STRINGDATA|] = S_notice.STRINGDATA',
        'S_full = $drive(S_resume, 10000)',
        'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps /\\ S_full.CURRENT = eps /\\ S_full.FRAMES = eps',
        '$cn_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        'S_full.STORE[n_private] = DEFINED (PINT 41)',
        '$parameter_backing_at(S_full.PARAMETERBACKINGS, n_private) = eps',
        '$propref_at(S_full.PROPREFS, n_private) = eps /\\ $reference_coercion_at(S_full.REFCOERCIONS, n_private) = eps',
        '$heap_valid($heap_graph(S_full)) /\\ $call_descriptors_valid(S_full)']


def controls(case):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for strict in ('false', 'true'):
        lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
        for value in ('PINT 17', 'PNULL', 'PBOOL true', 'PSTRING ($ptascii("missingCallable82"))'):
            lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        for field in ('CALLABLES', 'FUNCTIONS'):
            lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + CALLABLE + ', pvalue_original, ' + strict + ') = TYPEREJECT']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + '.COMPLETION = BUDGET /\\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    if not case['multiple']:
        for kind in ('string', 'array', 'int', 'mixed', 'CALLABLE'):
            lines += ['~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))]])']
        for replacement in ('NName (BYTES text_return) metadata_return', 'NNameFullyQualified (BYTES text_return) metadata_return', 'NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return'):
            lines += ['~$reference_notice_producer_header(phpType6_producer, phpType16, ' + replacement + ', pfunction_producer.SIGNATURE)']
        for update in ('.TYPE = eps', '.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]', '.BYREF = ' + str(not case['byref']).lower(), '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged callable default"'):
            lines += ['~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]])']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-callable-front' if args.front else 'cv-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
