#!/usr/bin/env python3
"""Ground global nullable stdClass RETURN authority and object/NULL private cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess


import global_plain_stdclass_return_producer_reference_notice_state as objects
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_nullable_stdclass_return_producer_reference_notice_cases.json')

PREFIX = objects.PREFIX + r'''
dec $pln_ready(pstate, nat) : bool
def $pln_ready(S, 0) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("make")
def $pln_ready(S, 1) = true
  -- if S.TODO = (CALL_SEND pcalltarget eps 0 eps porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.RESULT = KNOWN PNULL
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $pln_ready(S, 2) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) porigin? z) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("take")
def $pln_ready(S, n) = false -- otherwise
dec $pln_seek(pstate, nat, nat) : pstate
def $pln_seek(S, n_stage, n) = S
  -- if $pln_ready(S, n_stage) \/ n = 0 \/ S.TODO = eps
def $pln_seek(S, n_stage, n) = $pln_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$pln_ready(S, n_stage) /\ $(n > 0) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $pln_seek(S, n_stage, n) = S -- otherwise
'''


def nullable(name):
    return objects.prior.class_type(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'


def raw_nullable(name, tag='NName'):
    return 'NNullableType (' + objects.prior.raw_class(name, tag).replace('metadata_function', 'metadata_return') + ') metadata_nullable'


def null_front(case):
    role = case['role_index']
    saved = 'saved' if role == 0 else 'keep'
    lines = ['S_initial.COMPLETION = BUDGET',
        'S_return = $pln_seek(S_initial, 0, 1536)[.COMPLETION = NORMAL]', '$pln_ready(S_return, 0)',
        'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*', 'S_return.CURRENT = (pcallcontext_return)',
        '$function_at($all_functions(S_return), pcallcontext_return.FUNCTION) = (pfunction_producer)',
        'pfunction_producer.NAME = $ptascii("make")', '~pfunction_producer.SIGNATURE.BYREF',
        'pfunction_producer.SIGNATURE.RETURNS = ' + nullable(case['class_return']),
        'pfunction_producer.CODE.STRICT = ' + str(case['callee_strict']).lower(),
        '$lookup(S_return.ENV, $ptascii(' + json.dumps(saved) + ')) = (n_saved)',
        'S_return.STORE[n_saved] = DEFINED PNULL',
        '$resolve_at(S_return, S_return.RESULT, z_return).RESULT = KNOWN PNULL',
        '$typed_return_task_valid(S_return, z_return)',
        '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PNULL, pfunction_producer.CODE.STRICT) = TYPEVALUE PNULL',
        'S_return.FRAMES = [pframe_caller]', 'pframe_caller.LOCALS = eps',
        r'S_return.PARAMETERBACKINGS = eps /\ S_return.PROPREFS = eps /\ S_return.REFCOERCIONS = eps',
        'S_checked = $typed_return_value(S_return, z_return)',
        r'S_checked.COMPLETION = NORMAL /\ S_checked.RESULT = KNOWN PNULL',
        r'S_checked.STORE = S_return.STORE /\ S_checked.OBJECTPROPS = S_return.OBJECTPROPS',
        'S_return_step = $drive(S_return, 1)', 'S_return_step.COMPLETION = BUDGET',
        'S_after_return = S_return_step[.COMPLETION = NORMAL]',
        'S_after_return.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_return?) :: ptask_return_tail*',
        '$task_nodes(RETURN_UNWIND (KNOWN PNULL) porigin_return?) = eps',
        'S_pre = $pln_seek(S_after_return, 1, 1536)[.COMPLETION = NORMAL]', '$pln_ready(S_pre, 1)',
        'S_pre.TODO = (CALL_SEND pcalltarget eps 0 eps (porigin_call) z_call) :: ptask_tail*',
        r'S_pre.CURRENT = eps /\ S_pre.FRAMES = eps /\ S_pre.RESULT = KNOWN PNULL',
        '~((HCELL n_saved) <- S_pre.ALLOCATIONS)',
        '$lookup(S_pre.ENV, $ptascii(' + json.dumps(saved) + ')) = eps',
        '$lookup(S_pre.ENV, $ptascii("x")) = (n_caller)', '$lookup(S_pre.ENV, $ptascii("alias")) = (n_caller)',
        '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)', r'n_copy =/= n_caller /\ n_saved =/= n_caller',
        'S_pre.STORE[n_caller] = DEFINED ' + ('PNULL' if role == 0 else '(PINT 11)'),
        'S_pre.STORE[n_copy] = DEFINED PNULL', '$node_children(S_pre, HCELL n_caller) = eps',
        '$named_reference_notice_operand(S_pre, KNOWN PNULL)',
        '$call_argument_origin(S_pre, (porigin_call), 0) = (porigin_argument)',
        '$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)',
        '$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
        '$call_argument_expression(S_pre, (porigin_call), 0) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer',
        'phpType6_producer = SEQUENCE phpType7*', '|phpType7*| = ' + str(role + 1),
        'phpType7*[' + str(role) + '] = NArg ABSENT (NExprVariable (BYTES text_variable) metadata_variable) (BOOLEAN false) (BOOLEAN false) metadata_arg',
        '$base64(text_variable) = $ptascii("x")',
        '$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])',
        '$reference_notice_producer_line(S_pre, (porigin_argument), NExprFuncCall phpType19_producer phpType6_producer metadata_producer) = ' + str(case['notice_line']),
        '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)',
        '~$positional_reference_notice_pending(S_pre)',
        r'$error_handler_eligible(S_pre, 8) /\ S_pre.SOURCEPENDING = eps',
        r'S_pre.PARAMETERBACKINGS = eps /\ S_pre.PROPREFS = eps /\ S_pre.REFCOERCIONS = eps',
        'H_pre = $heap_graph(S_pre)', '$heap_owners(H_pre, HCELL n_caller) = 2',
        r'$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)']
    if role == 0:
        lines += ['pfunction_producer.SIGNATURE.PARAMETERS = [psparam]']
    else:
        lines += ['pfunction_producer.SIGNATURE.PARAMETERS = [psparam_tag, psparam]',
            'psparam_tag.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]', '~psparam_tag.BYREF',
            '$lookup(S_pre.ENV, $ptascii("stamp")) = (n_stamp)',
            '$lookup(S_pre.ENV, $ptascii("stampAlias")) = (n_stamp)', 'S_pre.STORE[n_stamp] = DEFINED (PINT 2)']
    return lines + ['psparam.NAME = $ptascii("saved")', 'psparam.TYPE = eps',
        'psparam.BYREF = ' + str(role == 1).lower(), r'psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE']


def front_lines(case, front):
    if case['kind'] == 'object':
        lines = []
        for line in objects.front_lines(case, front):
            if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
                line = 'pfunction_producer.SIGNATURE.RETURNS = ' + nullable(case['class_return'])
            if line.startswith('phpType18 = NName '):
                line = 'phpType18 = NNullableType (NName (BYTES text_return) metadata_return) metadata_nullable'
            lines.append(line)
        return lines
    lines = null_front(case) + ['pfunction_producer.ENV.NAMESPACE = eps', 'pfunction_producer.ENV.CLASSES = eps',
        'phpType18 = NNullableType (NName (BYTES text_return) metadata_return) metadata_nullable',
        '$base64(text_return) = $ptascii(' + json.dumps(case['class_return']) + ')']
    if not front:
        lines = [line.removeprefix('~') if line == '~$positional_reference_notice_pending(S_pre)' else line for line in lines]
        lines += ['$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)']
    return lines


def completed(case):
    if case['kind'] == 'object':
        return [line.replace('perrorcall.LINE = 8', 'perrorcall.LINE = ' + str(case['notice_line'])) for line in objects.prior.full_lines(case['role_index'], case)]
    lines = r'''
n_private = |S_pre.STORE|
n_private =/= n_caller /\ n_private =/= n_saved
S_notice_step = $drive(S_pre, 1)
S_notice_step.COMPLETION = BUDGET
S_notice = S_notice_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice*
perrorcall.RESUME = CALL_ARGS pcalltarget eps 1 ([REFERENCE n_private]) (porigin_call) z_call
S_notice.STORE[n_private] = DEFINED PNULL
n_private <- S_notice.REFCELLS
$node_children(S_notice, HCELL n_private) = eps
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_valid(H_notice)
S_resume = $pln_seek(S_notice, 2, 1536)[.COMPLETION = NORMAL]
$pln_ready(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_resume*
S_resume.STORE[n_private] = DEFINED PNULL
S_resume.STORE[n_caller] = DEFINED (PINT 17)
S_resume.STORE[n_copy] = DEFINED PNULL
S_resume.PARAMETERBACKINGS = eps /\ S_resume.PROPREFS = eps /\ S_resume.REFCOERCIONS = eps
$error_call_valid(S_resume, perrorcall) /\ $heap_valid($heap_graph(S_resume))
S_full = $drive(S_resume, 10000)
S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.FRAMES = eps /\ S_full.CURRENT = eps
S_full.ENV = eps /\ n_private <- S_full.REFCELLS
~((HCELL n_private) <- S_full.ALLOCATIONS)
~((HCELL n_caller) <- S_full.ALLOCATIONS) /\ ~((HCELL n_copy) <- S_full.ALLOCATIONS)
S_full.PARAMETERBACKINGS = eps /\ S_full.PROPREFS = eps /\ S_full.REFCOERCIONS = eps
$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)
'''.strip().splitlines()
    lines += ['perrorcall.LINE = ' + str(case['notice_line']) + r' /\ perrorcall.LEVEL = 8',
        '$objn_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    if case['role_index'] == 1:
        lines += ['S_resume.STORE[n_stamp] = DEFINED (PINT 29)', '~((HCELL n_stamp) <- S_full.ALLOCATIONS)']
    return lines


def controls(case):
    signature, env = 'pfunction_producer.SIGNATURE', 'pfunction_producer.ENV'
    header = '$reference_notice_producer_scoped_header(' + env + ', phpType6_producer, phpType16, '
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])', '~$typed_return_task_valid(S_return, $(z_return + 1))',
        header + 'phpType18, ' + signature + '[.RETURNS = eps])']
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        norm, raw = nullable(spelling), raw_nullable(spelling)
        proof = header + raw + ', ' + signature + '[.RETURNS = ' + norm + '])'
        lines += [proof, '~' + proof.replace(env + ',', env + '[.NAMESPACE = $ptascii("Other")],', 1),
            ('' if spelling == 'stdClass' else '~') + proof.replace(env + ',', env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
            '~$reference_notice_producer_header(phpType6_producer, phpType16, ' + raw + ', ' + signature + '[.RETURNS = ' + norm + '])',
            proof.replace(raw, raw_nullable(spelling, 'NNameFullyQualified'))]
        wrong_types = [objects.prior.class_type(spelling), nullable(spelling.swapcase()),
            '[(PTBRANCH ([PTBUILTIN "null"])), ' + objects.prior.class_type(spelling)[1:],
            norm[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]', norm[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]']
        lines += ['~' + proof.replace(norm, wrong) for wrong in wrong_types]
        for tag in ('NIdentifier', 'NNameRelative'):
            lines.append(('' if tag == 'NNameRelative' else '~') + proof.replace(raw, raw_nullable(spelling, tag)))
        bare = objects.prior.raw_class(spelling, 'NName').replace('metadata_function', 'metadata_return')
        union = 'NUnionType (SEQUENCE ([' + bare + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable'
        lines += ['~' + proof.replace(raw, bare), proof.replace(raw, union)]
    for spelling in ('Other', 'Other\\stdClass', '\\stdClass', 'stdClass\x00'):
        lines.append('~' + header + raw_nullable(spelling) + ', ' + signature + '[.RETURNS = ' + nullable(spelling) + '])')
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
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
    paths = [Path(__file__), Path(objects.__file__), Path(objects.prior.__file__), Path(objects.prior.prior.__file__), CATALOGUE, provenance]
    specs, reached, derived = [], [], []
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
            current = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $plc_case' + str(index) + '() : bool\ndef $plc_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached += current
            derived += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $plc_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-nullable-stdclass-return-front' if args.front else 'global-plain-nullable-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
