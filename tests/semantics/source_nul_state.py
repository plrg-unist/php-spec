"""Emit genuine local NUL-failure state fronts from checked original packets."""
import argparse
import ast
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
byte_term = lambda value: '$base64(' + json.dumps(base64.b64encode(value).decode()) + ')'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
OWNED_SOURCE = br'''<?php
class N{function __toString(){return "x\0y";}}
include new N;
'''


def sources():
    values = {row['id']: row['source'].encode() for row in json.loads(
        (ROOT / 'tests/semantics/source_nul_cases.json').read_bytes())}
    module = ast.parse((ROOT / 'tests/semantics/source_nul_review_sources.py').read_text())
    values['throwing-warning'] = next(ast.literal_eval(node.value) for node in module.body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == 'SOURCE')
    values['owned-conversion-boundary'] = OWNED_SOURCE
    return values


def prepare(directory):
    """Fresh syntax-only preparation makes the maintained recipe independent of old raw paths."""
    sys.path.insert(0, str(ROOT / 'frontend'))
    import wire
    ids = ('include-nul-suffix', 'include_once-nul-included-main', 'require-nul-leading',
           'throwing-warning', 'owned-conversion-boundary')
    values = sources(); rows = {}; packets = {}
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    requests = [{'op': 'parse', 'source': base64.b64encode(values[identity]).decode()} for identity in ids]
    frontend = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')]
    parsed_run = subprocess.run(frontend, input=''.join(wire.dumps(q) + '\n' for q in requests),
        text=True, capture_output=True, timeout=15, env=environment)
    assert parsed_run.returncode == 0 and parsed_run.stderr == ''
    parsed = [wire.loads(line) for line in parsed_run.stdout.splitlines()]
    assert len(parsed) == len(ids) and all(row['ok'] and row['accepted'] for row in parsed)
    checks = [{'op': 'check', 'ast': row['ast'], 'fixture': True} for row in parsed]
    check_run = subprocess.run([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
        input=''.join(wire.dumps(q) + '\n' for q in checks), text=True, capture_output=True,
        timeout=15, env=environment)
    assert check_run.returncode == 0 and check_run.stderr == ''
    checked = [wire.loads(line) for line in check_run.stdout.splitlines()]
    assert len(checked) == len(ids) and all(row['ok'] and row['fixture'] for row in checked)
    for identity, request, response, check, result in zip(ids, requests, parsed, checks, checked, strict=True):
        packet = directory / identity; packet.mkdir(parents=True)
        source = packet / 'main.php'; source.write_bytes(values[identity])
        (packet / '00-frontend.json').write_text(json.dumps({'request': request, 'response': response}) + '\n')
        (packet / 'checked.json').write_text(json.dumps({'request': check, 'response': result}) + '\n')
        rows[identity] = {'source': str(source.resolve()), 'source_sha256': sha(source)}
        packets[identity] = packet
    return rows, packets
PREFIX = r'''
dec $np_stage(pstate, nat) : bool
dec $np_seek(pstate, nat, nat) : pstate
def $np_seek(S, n_stage, n) = S[.COMPLETION = NORMAL]
  -- if $np_stage(S[.COMPLETION = NORMAL], n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $np_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $np_seek(S, n_stage, 0) = S
  -- if ~$np_stage(S[.COMPLETION = NORMAL], n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $np_seek(S, n_stage, n) = $np_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$np_stage(S[.COMPLETION = NORMAL], n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $np_file_unchanged(pstate, pstate) : bool
def $np_file_unchanged(S, S_after) = (S_after.FILESEQ = S.FILESEQ /\ S_after.FILECONTEXTS = S.FILECONTEXTS /\ S_after.EVALCONTEXTS = S.EVALCONTEXTS /\ S_after.FILES = S.FILES /\ S_after.SOURCES = S.SOURCES /\ S_after.CODE = S.CODE /\ S_after.POOLS = S.POOLS /\ S_after.FILEBINDINGS = S.FILEBINDINGS /\ S_after.EVALBINDINGS = S.EVALBINDINGS /\ S_after.FAILEDSOURCES = S.FAILEDSOURCES /\ S_after.INCLUDEDOPENED = S.INCLUDEDOPENED)
dec $np_public(pstate) : bool
def $np_public(S) = ($call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, help='optional accepted original-source packet')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--owned', type=Path, help='owned control packet when reusing --raw')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = None
    if args.raw is None:
        assert args.owned is None
        rows, packets = prepare(args.output / 'prepared')
    else:
        assert args.owned is not None
        report_path = args.raw / 'report.json'
        report = json.loads(report_path.read_bytes())
        assert report['complete'] and report['source_agreements'] == 10
        assert all(report[key] for key in ('inputs_stable', 'head_stable', 'status_stable'))
        rows = {row['id']: row for row in report['records']}
        assert all(row['passed'] and row['outcome']['status'] == 'normal' for row in rows.values())
        owned_report = json.loads((args.owned / 'report.json').read_bytes())
        assert owned_report['complete'] and owned_report['source_agreements'] == 0
        assert all(owned_report[key] for key in ('inputs_stable', 'head_stable', 'status_stable'))
        assert owned_report['outcome']['status'] == 'unsupported'
        assert owned_report['outcome']['reason'] == 'NUL file path with captured operand or unavailable include_path'
        owned_source = Path(owned_report['process']['argv'][3])
        assert sha(owned_source) == owned_report['inputs'][str(owned_source)]
        rows['owned-conversion-boundary'] = {'source': str(owned_source), 'source_sha256': owned_report['inputs'][str(owned_source)]}
        packets = {identity: args.owned if identity == 'owned-conversion-boundary' else args.raw / identity for identity in rows}
    records = []

    def emit(name, identity, stages, checks, mutations=()):
        row = rows[identity]
        packet = packets[identity]
        checked = json.loads((packet / 'checked.json').read_bytes())
        source = Path(row['source'])
        assert sha(source) == row['source_sha256'] and checked['response']['ok']
        assert source.read_bytes() == sources()[identity]
        parsed = json.loads((packet / '00-frontend.json').read_bytes())
        assert parsed['request']['source'] == base64.b64encode(source.read_bytes()).decode()
        assert checked['request']['ast'] == parsed['response']['ast']
        start = '$php_file_run(' + checked['response']['fixture'] + ', 0, ' + byte_term(bytes(source)) + ', ' + byte_term(bytes(ROOT)) + ')'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
            'S_start = S_initial[.COMPLETION = NORMAL]', 'S_pre = $np_seek(S_start, 0, 256)',
            '$np_stage(S_pre, 0)', '$np_public(S_pre)', 'S_pre.FILESEQ = 0',
            'S_pre.FILECONTEXTS = eps', 'S_pre.INCLUDEDOPENED = [' + byte_term(bytes(source)) + ']']
        assertions += checks
        for index, mutation in enumerate(mutations):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                f'~$call_descriptors_valid(S_bad{index})']
        assertions += ['S_pause = $drive_steps(S_pre, 0)', 'S_pause = S_pre[.COMPLETION = BUDGET]',
            'S_direct = $drive_steps(S_pre, 1)',
            'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL], 1)', 'S_one = S_direct',
            '$np_file_unchanged(S_pre, S_one)']
        if identity != 'owned-conversion-boundary':
            assertions += ['$np_public(S_one[.COMPLETION = NORMAL])']
        definitions = ''.join(f'def $np_stage(S, {n}) = true\n' + ''.join('  -- if ' + c + '\n' for c in conditions)
                              for n, conditions in stages.items())
        definitions += 'def $np_stage(S, n_stage) = false -- otherwise\n'
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + definitions + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join(('  ' + condition if condition.startswith('-- ') else '  -- if ' + condition) + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': identity, 'fixture': str(path.resolve()),
            'fixture_sha256': sha(path), 'assertions': len(assertions)})

    warning_stages = {
        0: ['S.TODO = (FILE_REQUEST porigin z 1) :: ptask_tail*', '$file_nul_operand(S)'],
        1: ['S.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = FILE_NUL_RESULT pfilenul',
            'S.FILEINCLUDEPATH = ($ptascii("changed"))'],
        2: ['S.TODO = (FILE_NUL_RESULT pfilenul) :: ptask_tail*']}
    warning_checks = [
        'S_pre.TODO = (FILE_REQUEST porigin z 1) :: ptask_tail*',
        'S_pre.RESULT = KNOWN pvalue_path', '$string_bytes(pvalue_path) = ($ptascii("prefix") ++ [0] ++ $ptascii("tail"))',
        'S_notice = $drive_steps(S_pre, 1)', 'S_notice.COMPLETION = BUDGET',
        'S_current = S_notice[.COMPLETION = NORMAL]', '$np_public(S_current)',
        'S_current.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = FILE_NUL_RESULT pfilenul',
        'pfilenul.SITE = porigin', 'pfilenul.LINE = z', 'pfilenul.KIND = 1',
        'pfilenul.REQUESTED = $ptascii("prefix") ++ [0] ++ $ptascii("tail")',
        'pfilenul.INCLUDEPATH = $ptascii(".:")', 'pfilenul.TAIL = ptask_tail*',
        '$task_nodes(FILE_NUL_RESULT pfilenul) = eps', '$np_file_unchanged(S_pre, S_current)',
        'S_current.STORE = S_pre.STORE', 'S_current.EVENTS = S_pre.EVENTS',
        'S_saved = $np_seek(S_current, 1, 256)', '$np_stage(S_saved, 1)', '$np_public(S_saved)',
        'S_saved.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = FILE_NUL_RESULT pfilenul',
        'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
        '$file_nul_valid(S_scope, pfilenul)', '$np_file_unchanged(S_pre, S_saved)',
        'S_result = $np_seek(S_saved, 2, 256)', '$np_stage(S_result, 2)', '$np_public(S_result)',
        'S_result.TODO = (FILE_NUL_RESULT pfilenul) :: ptask_tail*',
        'S_result.FILEINCLUDEPATH = ($ptascii("changed"))',
        'S_false = $drive_steps(S_result, 1)', 'S_false.COMPLETION = BUDGET',
        'S_false.RESULT = KNOWN (PBOOL false)', '$np_public(S_false[.COMPLETION = NORMAL])',
        '$np_file_unchanged(S_pre, S_false)']
    warning_bad = [
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.RESUME = FILE_NUL_RESULT (pfilenul[.SITE = PORIGIN 0 eps])])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.RESUME = FILE_NUL_RESULT (pfilenul[.LINE = $(z + 1)])])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.RESUME = FILE_NUL_RESULT (pfilenul[.KIND = 3])])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.RESUME = FILE_NUL_RESULT (pfilenul[.REQUESTED = $ptascii("prefix")])])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.RESUME = FILE_NUL_RESULT (pfilenul[.TAIL = eps])])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE (perrorcall[.MESSAGE = $ptascii("changed")])) :: ptask_tail*]',
        'S_current[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (FILE_NUL_RESULT pfilenul) :: ptask_tail*]',
        'S_saved[.FRAMES = (pframe[.TODO = (ERROR_HANDLER_RESULT (perrorcall_entered[.RESUME = FILE_NUL_RESULT (pfilenul[.OWNER = $(pfilenul.OWNER + 1)])])) :: ptask_tail*]) :: pframe_tail*]',
        'S_saved[.FRAMES = (pframe[.ORIGIN = eps]) :: pframe_tail*]']
    emit('warning-current-saved-frozen-path', 'include-nul-suffix', warning_stages, warning_checks, warning_bad)

    once_source = Path(rows['include_once-nul-included-main']['source'])
    once_requested = byte_term(bytes(once_source) + b'\0tail')
    emit('once-included-prefix-still-fails', 'include_once-nul-included-main', {
        0: ['S.TODO = (FILE_REQUEST porigin z 2) :: ptask_tail*', '$file_nul_operand(S)'],
        1: ['S.TODO = (FILE_NUL_RESULT pfilenul) :: ptask_tail*']}, [
        'S_pre.TODO = (FILE_REQUEST porigin z 2) :: ptask_tail*',
        'S_notice = $drive_steps(S_pre, 1)', 'S_notice.COMPLETION = BUDGET',
        'S_current = S_notice[.COMPLETION = NORMAL]', '$np_public(S_current)',
        'S_current.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = FILE_NUL_RESULT pfilenul', 'pfilenul.KIND = 2',
        'pfilenul.REQUESTED = ' + once_requested,
        '$c_string(pfilenul.REQUESTED) <- S_pre.INCLUDEDOPENED',
        '$np_file_unchanged(S_pre, S_current)',
        'S_result = $np_seek(S_current, 1, 256)', '$np_stage(S_result, 1)',
        'S_result.TODO = (FILE_NUL_RESULT pfilenul) :: ptask_tail*',
        '$np_public(S_result)', 'S_false = $drive_steps(S_result, 1)',
        'S_false.RESULT = KNOWN (PBOOL false)', '$np_file_unchanged(S_pre, S_false)'])

    emit('require-nul-leading-direct-error', 'require-nul-leading', {
        0: ['S.TODO = (FILE_REQUEST porigin z 3) :: ptask_tail*', '$file_nul_operand(S)']}, [
        'S_pre.TODO = (FILE_REQUEST porigin z 3) :: ptask_tail*',
        'S_pre.RESULT = KNOWN pvalue_path', '$string_bytes(pvalue_path) = ([0] ++ $ptascii("tail"))',
        'S_pre.EVENTS = [OUTPUT $ptascii("A;")]',
        'S_error = $drive_steps(S_pre, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        '$throwable_member(S_error, n_error)',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Failed opening required \'\' (include_path=\'.:\')"))',
        '$np_public(S_error[.COMPLETION = NORMAL])', '$np_file_unchanged(S_pre, S_error)',
        'S_error.EVENTS = S_pre.EVENTS', 'S_error.ERRORHANDLER = S_pre.ERRORHANDLER',
        'S_error.FILEINCLUDEPATH = S_pre.FILEINCLUDEPATH'])

    emit('throwing-handler-keyword-frame', 'throwing-warning', {
        0: ['S.TODO = (FILE_REQUEST porigin z 1) :: ptask_tail*', '$file_nul_operand(S)'],
        1: ['S.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = FILE_NUL_RESULT pfilenul', 'S.CURRENT = (pcallcontext)',
            'S.FILEINCLUDEPATH = ($ptascii("next"))']}, [
        'S_saved = $np_seek(S_pre, 1, 256)', '$np_stage(S_saved, 1)', '$np_public(S_saved)',
        'S_saved.FRAMES = pframe :: pframe_tail*', 'S_saved.CURRENT = (pcallcontext)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = FILE_NUL_RESULT pfilenul', 'pfilenul.INCLUDEPATH = $ptascii(".:")',
        'perrorcall.MESSAGE = $file_nul_message(pfilenul)',
        '$eval_trace_preparser(S_saved, S_saved.CURRENT, pframe) = [ptraceframe]',
        'ptraceframe.FUNCTION = $ptascii("include")', 'ptraceframe.LINE = 9',
        'ptraceframe.FILE = ' + byte_term(bytes(Path(rows['throwing-warning']['source']))),
        'ptraceframe.ARGS = eps', '~ptraceframe.HASARGS', '$np_file_unchanged(S_pre, S_saved)',
        'S_caller = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
        '$file_nul_valid(S_caller, pfilenul)', '$lookup(S_caller.ENV, $ptascii("x")) = (n_x)',
        'S_caller.STORE[n_x] = DEFINED (PINT 99)'])

    emit('owned-conversion-explicit-boundary', 'owned-conversion-boundary', {
        0: ['S.TODO = (SOURCE_STRING_READY psourceoperand n_object n_text*) :: ptask_tail*',
            'n_text* = $ptascii("x") ++ [0] ++ $ptascii("y")']}, [
        'S_pre.TODO = (SOURCE_STRING_READY psourceoperand n_object n_text*) :: ptask_tail*',
        '$source_operand_valid(S_pre, psourceoperand)', 'psourceoperand.KIND = 1',
        'psourceoperand.INPUT = KNOWN (POBJECT n_object)',
        '(HOBJECT n_object) <- S_pre.ALLOCATIONS',
        '$task_nodes(SOURCE_STRING_READY psourceoperand n_object n_text*) = [HOBJECT n_object]',
        '$($heap_owners($heap_graph(S_pre), HOBJECT n_object) > 0)',
        '$file_nul_owned_tail((SOURCE_OPERAND_RELEASE psourceoperand) :: psourceoperand.TAIL)',
        '-- PhpStep: S_pre ~> S_refused',
        'S_refused.COMPLETION = UNSUPPORTED "NUL file path with captured operand or unavailable include_path"',
        'S_refused.TODO = S_pre.TODO', 'S_refused.STORE = S_pre.STORE',
        'S_refused.EVENTS = S_pre.EVENTS', 'S_refused.FRAMES = S_pre.FRAMES',
        'S_refused.ALLOCATIONS = S_pre.ALLOCATIONS',
        '$heap_owners($heap_graph(S_refused), HOBJECT n_object) = $heap_owners($heap_graph(S_pre), HOBJECT n_object)',
        '$tasks_nodes(S_refused.TODO) = $tasks_nodes(S_pre.TODO)',
        '$np_file_unchanged(S_pre, S_refused)', '$heap_valid($heap_graph(S_refused))'])

    manifest = {'source_report': None if report_path is None else str(report_path.resolve()),
        'source_report_sha256': None if report_path is None else sha(report_path),
        'owned_report': None if args.owned is None else str((args.owned / 'report.json').resolve()),
        'owned_report_sha256': None if args.owned is None else sha(args.owned / 'report.json'),
        'records': records, 'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records)}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
