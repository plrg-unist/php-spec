#!/usr/bin/env python3
"""Reach iterable return verification, retired producer frames and private Notice cells."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_iterable_return_producer_reference_notice_cases.json')
ITERABLE = '[(PTBRANCH ([PTBUILTIN "iterable"]))]'
PREFIX = r'''
dec $ir_output(pevent*) : ptbytes
def $ir_output(eps) = eps
def $ir_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ir_output(pevent*)
dec $ir_quiet(pevent*) : bool
def $ir_quiet(eps) = true
def $ir_quiet((OUTPUT ptbytes) :: pevent*) = $ir_quiet(pevent*)
def $ir_quiet(pevent*) = false -- otherwise
dec $ir_ready(pstate, nat) : bool
def $ir_ready(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- NAMES_MAKE
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
def $ir_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- NAMES_TAKE
def $ir_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME <- NAMES_TAKE
def $ir_ready(S, n_stage) = false -- otherwise
dec $ir_seek(pstate, nat, nat) : pstate
def $ir_seek(S, n_stage, n) = S -- if $ir_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $ir_seek(S, n_stage, n) = $ir_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ir_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ir_seek(S, n_stage, n) = S -- otherwise
'''


def reached(case, front):
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_return = $ir_seek(S_initial, 0, 5000)[.COMPLETION = NORMAL]',
        '$ir_ready(S_return, 0)', 'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
        'S_return.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_return), pcallcontext.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii(' + json.dumps(case['namespace'] + '\\make') + ')',
        r'~pfunction_producer.SIGNATURE.BYREF /\ ~$function_generator(S_return, pfunction_producer)',
        'pfunction_producer.SIGNATURE.RETURNS = ' + ITERABLE,
        'pfunction_producer.SIGNATURE.PARAMETERS = [psparam]',
        '$typed_return_task_valid(S_return, z_return)',
        'S_resolved = $resolve_at(S_return, S_return.RESULT, z_return)',
        'S_checked = $typed_return_value(S_return, z_return)']
    if case.get('priority_control'):
        return lines + ['S_resolved.RESULT = KNOWN (PINT 17)',
            '$typed_conversion_at(S_return, ' + ITERABLE + ', PINT 17, pfunction_producer.CODE.STRICT) = TYPEREJECT',
            'S_checked.COMPLETION = THROWN "TypeError" ptbytes_message z_return',
            r'S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS',
            'S_full = $drive(S_return, 10000)',
            r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
            '$ir_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
            '$ir_quiet(S_full.EVENTS)',
            r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    parameter = 'input' if case['formal_kind'] == 'array' else 'saved'
    lines += ['S_resolved.RESULT = KNOWN (PARRAY n_root)',
        r'S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN (PARRAY n_root)',
        r'S_checked.STORE = S_return.STORE /\ S_checked.ARRAYS = S_return.ARRAYS',
        r'S_checked.ALLOCATIONS = S_return.ALLOCATIONS /\ S_checked.PARAMETERBACKINGS = S_return.PARAMETERBACKINGS',
        '$lookup(S_return.ENV, $ptascii(' + json.dumps(parameter) + ')) = (n_formal)',
        'S_after_return = $drive(S_return, 1)[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN (PARRAY n_root)) porigin_return?) :: ptask_unwind*',
        r'$heap_valid($heap_graph(S_after_return)) /\ $call_descriptors_valid(S_after_return)',
        'S_pre = $ir_seek(S_after_return, 1, 5000)[.COMPLETION = NORMAL]',
        '$ir_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z) :: ptask_tail*',
        'S_pre.RESULT = KNOWN (PARRAY n_root)',
        r'S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.PARAMETERBACKINGS = eps',
        '$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType6_producer = SEQUENCE ([phpType7_actual])',
        'phpType7_actual = NArg ABSENT expression_actual (BOOLEAN false) (BOOLEAN false) metadata_actual',
        'expression_actual = NExprVariable (BYTES text_actual) metadata_variable',
        '$reference_cv(expression_actual) = (ptbytes_actual)',
        '$lookup(S_pre.ENV, ptbytes_actual) = (n_caller)',
        '$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        'phpType16 = SEQUENCE ([phpType17])',
        'phpType18 = NIdentifier (BYTES text_return) metadata_return',
        '$ptlc($base64(text_return)) = $ptascii("iterable")',
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE)',
        '$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])',
        ('~' if front else '') + '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        '$named_reference_notice_array(S_pre, PARRAY n_root)',
        r'$heap_valid($heap_graph(S_pre)) /\ $call_descriptors_valid(S_pre)']
    lines += ['n_formal = n_caller'] if case['formal_byref'] else [
        'n_formal =/= n_caller', '~((HCELL n_formal) <- S_pre.ALLOCATIONS)']
    return lines


def completed(case):
    if case.get('priority_control'):
        return []
    return ['$positional_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))',
        '$positional_reference_notice_pending(S_pre)', 'n_private = |S_pre.STORE|',
        r'n_private =/= n_caller /\ n_private =/= n_formal',
        'S_notice = $drive(S_pre, 1)[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*',
        'perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z',
        'perrorcall.LINE = $reference_notice_producer_line(S_pre, $call_argument_origin(S_pre, (porigin_call), 0), $call_argument_expression(S_pre, (porigin_call), 0))',
        'S_notice.STORE[n_private] = DEFINED (PARRAY n_root)',
        '$node_children(S_notice, HCELL n_private) = [HARRAY n_root]',
        '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        r'$error_call_valid(S_notice, perrorcall) /\ $heap_valid($heap_graph(S_notice))',
        'S_resume = $ir_seek(S_notice, 2, 5000)[.COMPLETION = NORMAL]', '$ir_ready(S_resume, 2)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_resume.STORE[n_private] = DEFINED (PARRAY n_root)',
        'S_resume.PARAMETERBACKINGS = eps',
        r'$propref_at(S_resume.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_resume.REFCOERCIONS, n_private) = eps',
        r'$error_call_valid(S_resume, perrorcall) /\ $heap_valid($heap_graph(S_resume))',
        'S_full = $drive(S_resume, 10000)',
        r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
        '$ir_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
        '$ir_quiet(S_full.EVENTS)', '$lookup(S_full.ENV, $ptascii("r")) = (n_private)',
        'S_full.STORE[n_private] = DEFINED (PINT 29)',
        '$node_children(S_full, HCELL n_private) = eps',
        r'$propref_at(S_full.PROPREFS, n_private) = eps /\ $reference_coercion_at(S_full.REFCOERCIONS, n_private) = eps',
        'S_full.PARAMETERBACKINGS = eps',
        r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']


def controls(case):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        'S_zero = $drive(S_return, 0)',
        r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_return',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_return, 2)']
    if case.get('priority_control'):
        return lines
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    raw = 'NIdentifier (BYTES text_return) metadata_return'
    lines += [header + 'NIdentifier (BYTES "SVRFUkFCTEU=") metadata_return, ' + signature + ')',
        '~' + header + 'NIdentifier (BYTES "YXJyYXk=") metadata_return, ' + signature + ')',
        '~' + header + raw + ', ' + signature + '[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])',
        '~' + header + 'NName (BYTES text_return) metadata_return, ' + signature + ')',
        '~' + header + 'NNameFullyQualified (BYTES text_return) metadata_return, ' + signature + ')',
        header + 'NNullableType (' + raw + ') metadata_return, ' + signature + '[.RETURNS = ' + ITERABLE[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]])',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), ' + signature + '[.PARAMETERS = [psparam, psparam]][.RETURNS = eps])',
        '~$reference_notice_producer_header(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), phpType18, ' + signature + '[.PARAMETERS = [psparam, psparam]])']
    for suffix in ('null', 'false'):
        atom = '(NIdentifier (BYTES ' + json.dumps(base64.b64encode(suffix.encode()).decode()) + ') metadata_return)'
        for reverse in (False, True):
            nodes = ['(' + raw + ')', atom]
            branches = ['(PTBRANCH ([PTBUILTIN "iterable"]))', '(PTBRANCH ([PTBUILTIN ' + json.dumps(suffix) + ']))']
            if reverse:
                nodes.reverse()
                branches.reverse()
            lines += [('' if suffix == 'null' else '~') + header + 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return, ' + signature + '[.RETURNS = [' + ', '.join(branches) + ']])']
    for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not case['formal_byref']).lower(),
                 'TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]'):
        lines += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = [psparam[.' + edit + ']]])']
    lines += ['~$reference_notice_producer_header(SEQUENCE ([NArg ABSENT (NExprVariable (BYTES "aHR0cF9yZXNwb25zZV9oZWFkZXI=") metadata_variable) (BOOLEAN false) (BOOLEAN false) metadata_actual]), phpType16, phpType18, ' + signature + ')']
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
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
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
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
    print('singleton-cv-iterable-return-front' if args.front else 'singleton-cv-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
