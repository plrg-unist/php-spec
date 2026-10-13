#!/usr/bin/env python3
"""Source-owned exit replacement and independent request status at real fronts."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_static_retirement_protocol as retirement
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT, inputs, types = retirement.ROOT, retirement.inputs, retirement.types
seq, byte_expr, b64 = retirement.seq, retirement.byte_expr, retirement.b64
STAGES = {
    'eval-owner': ('static-native-v14', 'eval-exit-two-throws-zero'),
    'file-owner': ('static-native-v14', 'file-exit-two-throws-zero'),
    'eval-status': ('static-native-v2', 'eval-destructor-exit'),
    'eval-empty': ('static-native-v15', 'eval-empty-string-after-catch'),
    'nested-status': ('static-native-v13', 'eval-reset-inside-destructor-0'),
}
PREFIX = r'''dec $stage(pstate,text,text) : bool
def $stage(S,"invoke",text) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if pexitcall.SENT = [KNOWN (PINT 7)]
def $stage(S,"string",text) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if pexitcall.SENT = [KNOWN pvalue_string]
  -- if $string_bytes(pvalue_string) = (eps)
def $stage(S,"status-operation",text) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 7) :: (EVAL_END 1) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = EXIT_UNWIND 7
def $stage(S,"exit",text) = true
  -- if S.TODO = (EXIT_UNWIND 0) :: ptask_end :: ptask_tail*
  -- if $eval_end_marker(ptask_end)
def $stage(S,"callback",text) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if $object_name(S,pdestructorcall.OBJECT) = $ptascii(text)
def $stage(S,"result",text) = true
  -- if S.TODO = (THROW_SEARCH n) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if $object_name(S,pdestructorcall.OBJECT) = $ptascii(text)
def $stage(S,"exit-operation",text) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 0) :: ptask_end :: ptask_tail*
  -- if $eval_end_marker(ptask_end)
  -- if pdestructionoperation.SOURCE = EXIT_UNWIND 0
  -- if pdestructionoperation.PENDING =/= eps
def $stage(S,"throw-operation",text) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_end :: ptask_tail*
  -- if $eval_end_marker(ptask_end)
  -- if pdestructionoperation.SOURCE = THROW_SEARCH n
  -- if pdestructionoperation.PENDING =/= eps
def $stage(S,text,text_class) = false -- otherwise
dec $seek(pstate,text,text,nat) : pstate
def $seek(S,text,text_class,n) = S -- if $stage(S,text,text_class)
def $seek(S,text,text_class,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),text,text_class,$nabs($(n - 1)))
  -- if ~$stage(S,text,text_class)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek(S,text,text_class,n) = S -- otherwise
''' + retirement.PREFIX[retirement.PREFIX.index('dec $one'):]


def reached(name, expression):
    return [name + '_found = ' + expression,
        name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
        name + ' = ' + name + '_found[.COMPLETION = NORMAL]']


def public(name):
    return ['$call_descriptors_valid(' + name + ')', '$declaration_entry_check(' + name + ') = ' + name,
        '$heap_valid($heap_graph(' + name + '))']


def status_record(sources, suite, case):
    report = json.loads((sources / suite / 'report.json').read_text())
    row, = [row for row in report.get('records', report.get('rows')) if row.get('id', row.get('name')) == case]
    assert report.get('target', report.get('profile')) == types.PROFILE
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = sources / suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit']
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode() == b''
    for name, digest in row['originals'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    return directory, row


def status_checks(name, native, inner):
    checks = ['S_ready.COMPLETION = NORMAL', 'S_ready.EXITSTATUS = 0']
    if name == 'eval-status':
        assert native['exit'] == 7
        checks += [*reached('S', '$seek(S_ready,"invoke","",1800)'), 'S.EXITSTATUS = 0',
            'S.TODO = (EXIT_INVOKE pexitcall) :: ptask_invoke_tail*',
            '$source_static_exit_tail(S,ptask_invoke_tail*) = (EVAL_END 1) :: ptask_tail*',
            'pexitcall.SENT = [KNOWN (PINT 7)]', *public('S'),
            '~$call_descriptors_valid(S[.EXITSTATUS = 2147483648])',
            '~$call_descriptors_valid(S[.EXITSTATUS = -2147483649])',
            'S_written = $one(S)', 'S_written.EXITSTATUS = 7', 'S_written.COMPLETION = NORMAL',
            'S_written.TODO = (EXIT_UNWIND 7) :: (EVAL_END 1) :: ptask_tail*',
            '$exit_status_valid(S_written)', '$exit_unwind_valid(S_written,7)', *public('S_written'),
            *reached('S_callback', '$seek(S,"callback","Box",600)'), 'S_callback.EXITSTATUS = 7',
            'S_callback.FRAMES = [pframe]', 'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_callback_tail*',
            'S_scope = $destructor_boundary_scope(S_callback,pdestructorcall,S_callback.FRAMES)',
            'S_scope.EXITSTATUS = 7', 'S_scope.CURRENT = eps', 'pdestructorcall.USER', *public('S_callback'),
            *reached('S_pending', '$seek(S_callback,"status-operation","",600)'),
            'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 7) :: (EVAL_END 1) :: ptask_tail*',
            'pdestructionoperation.PENDING = (n)', 'pdestructionoperation.SOURCE = EXIT_UNWIND 7',
            'S_pending.EXITSTATUS = 7', '$throwable_previous_id(S_pending,n) = eps', *public('S_pending'),
            'S_cancelled = $one(S_pending)', 'S_cancelled.EXITSTATUS = 7',
            'S_cancelled.TODO = (THROW_SEARCH n) :: (EVAL_END 1) :: ptask_tail*', *public('S_cancelled'),
            'S_finished = $drive_steps(S_pending,1800)', 'S_finished.COMPLETION = NORMAL',
            'S_finished.EXITSTATUS = 7', 'S_finished.EVALCONTEXTS = eps', 'S_finished.STATICS = eps']
    elif name == 'eval-empty':
        assert native['exit'] == 7
        checks += [*reached('S', '$seek(S_ready,"string","",2400)'), 'S.EXITSTATUS = 7',
            'S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*', 'pexitcall.SENT = [KNOWN pvalue_string]',
            '$string_bytes(pvalue_string) = (eps)', 'S.EVALCONTEXTS = eps',
            '$test_outputs(S.EVENTS) = $ptascii("B|D|TypeError|null|A|")', *public('S'),
            'S_written = $one(S)', 'S_written.EXITSTATUS = 7', 'S_written.COMPLETION = EXITED 7',
            'S_written.EVENTS = S.EVENTS', 'S_written.TODO = eps', *public('S_written'),
            'S_finished = $drive_steps(S,1800)', 'S_finished.COMPLETION = EXITED 7',
            'S_finished.EXITSTATUS = 7']
    else:
        assert name == 'nested-status' and native['exit'] == 0
        inner_bytes, inner_fixture = inner
        checks += ['S_wait_inner = $drive_steps(S_ready,1800)', 'S_wait_inner.COMPLETION = SOURCE_PENDING',
            'S_wait_inner.EXITSTATUS = 7', 'S_wait_inner.EVALCONTEXTS = [pevalcontext_inner,pevalcontext_outer]',
            'pevalcontext_inner.UNIT = 2', 'pevalcontext_inner.PHASE = PARSER_WAIT', 'pevalcontext_outer.UNIT = 1',
            'pevalcontext_outer.PHASE = UNIT_RUN', *public('S_wait_inner'),
            'S_ready_inner = $eval_resume(S_wait_inner,SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
            'S_ready_inner.COMPLETION = NORMAL', 'S_ready_inner.EXITSTATUS = 7',
            *reached('S', '$seek(S_ready_inner,"status-operation","",1800)'),
            'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXIT_UNWIND 7) :: (EVAL_END 1) :: ptask_tail*',
            'pdestructionoperation.SOURCE = EXIT_UNWIND 7', 'pdestructionoperation.PENDING = eps',
            'S.EXITSTATUS = 0', 'S.FRAMES = eps', 'S.CURRENT = eps', 'S.EVALCONTEXTS = [pevalcontext_outer]',
            '$test_outputs(S.EVENTS) = $ptascii("OB|OD|IB|ID|IC|OE|")', *public('S'),
            'S_restored = $one(S)', 'S_restored.TODO = (EXIT_UNWIND 7) :: (EVAL_END 1) :: ptask_tail*',
            'S_restored.EXITSTATUS = 0', 'S_restored.DESTRUCTION.OPERATIONS = eps',
            '$exit_unwind_valid(S_restored,7)', '$exit_status_valid(S_restored)', *public('S_restored'),
            '~$call_descriptors_valid(S_restored[.EXITSTATUS = 2147483648])',
            'S_finished = $drive_steps(S,1800)', 'S_finished.COMPLETION = EXITED 7', 'S_finished.EXITSTATUS = 0']
    return checks + ['$test_outputs(S_finished.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
        '$test_clean_events(S_finished.EVENTS)', *public('S_finished')]


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(source, mode, child=None, unit=1):
            request = {'op': 'parse', 'source': b64(source)} if mode == 'main' else {
                'op': 'parse-' + mode, 'id': str(unit), 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(child)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            return parsed['ast'], fixture

        for name in names:
            suite, case = STAGES[name]
            directory, native = retirement.native_record(sources, suite, case) if name.endswith('-owner') else status_record(sources, suite, case)
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            is_file = name.startswith('file-')
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
            else:
                evaluation, = [node for _, node, ancestors in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval' and 'Stmt_ClassMethod' not in ancestors]
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
            _, child_fixture = checked(child_bytes, 'file' if is_file else 'eval', child_path if is_file else None)
            checks = ['S_wait = $php_file_run(' + main_fixture + ',1800,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                checks += ['S_wait.FILECONTEXTS = [pfilecontext_wait]',
                    'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING',
                    'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker, contexts, context = 'FILE_END 1', 'FILECONTEXTS', 'pfilecontext'
            else:
                checks += ['S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker, contexts, context = 'EVAL_END 1', 'EVALCONTEXTS', 'pevalcontext'
            if not name.endswith('-owner'):
                inner = None
                if name == 'nested-status':
                    evaluation_inner, = [node for _, node, ancestors in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval' and 'Stmt_ClassMethod' in ancestors]
                    inner_bytes = base64.b64decode(evaluation_inner['fields'][0]['fields'][0]['bytes'])
                    _, inner_fixture = checked(inner_bytes, 'eval', unit=2)
                    inner = (inner_bytes, inner_fixture)
                checks += status_checks(name, native, inner)
            else:
                checks += ['S_ready.COMPLETION = NORMAL', *reached('S', '$seek(S_ready,"exit","",1800)'),
                    'S.TODO = (EXIT_UNWIND 0) :: (' + marker + ') :: ptask_tail*',
                    'S.' + contexts + ' = [' + context + ']', context + '.OWNER = |S.FRAMES|',
                    context + '.TAIL = ptask_tail*', 'S.CURRENT = eps', 'S.ORIGIN = eps',
                    'S.STATICS = [pstaticcell_a,pstaticcell_b]', '$source_static_next(S,1) = (pstaticcell_a.ORIGIN)',
                    'S.STORE[pstaticcell_a.CELL] = DEFINED (POBJECT n_a)',
                    'S.STORE[pstaticcell_b.CELL] = DEFINED (POBJECT n_b)',
                    '$source_static_user_source(S)', '$test_outputs(S.EVENTS) = $ptascii("B|")', *public('S'),
                    'S_raw = $one(S)', 'S_raw.STATICS = [pstaticcell_b]', 'S_raw.TODO = S.TODO',
                    'S_raw.' + contexts + ' = S.' + contexts, *public('S_raw'),
                    *reached('S_production', '$drive_steps(S,1)'), 'S_production.STATICS = [pstaticcell_b]',
                    'S_production.DESTRUCTION.OPERATIONS = [pdestructionoperation_a]',
                    'pdestructionoperation_a.SOURCE = EXIT_UNWIND 0', 'pdestructionoperation_a.PENDING = eps',
                    *public('S_production'), *reached('S_callback', '$seek(S_production,"callback","A",600)'),
                    'S_callback.FRAMES = [pframe_a]',
                    'pframe_a.TODO = (DESTRUCTOR_RESULT pdestructorcall_a) :: ptask_callback_tail*',
                    'pdestructorcall_a.OBJECT = n_a', 'pdestructorcall_a.USER',
                    'pdestructorcall_a.OPERATION = (pdestructionoperation_a)',
                    '$destructor_boundary_frame(pframe_a,pdestructorcall_a)',
                    'S_scope = $destructor_boundary_scope(S_callback,pdestructorcall_a,S_callback.FRAMES)',
                    'S_scope.CURRENT = eps', 'S_scope.FRAMES = eps', 'S_scope.TODO = pframe_a.TODO',
                    '$source_static_user_source(S_scope)', '$destructor_boundary_valid(S_callback,pdestructorcall_a)',
                    *public('S_callback'),
                    '~$call_descriptors_valid(S_callback[.DESTRUCTION.CALLS = eps])',
                    '~$source_static_user_source(S_scope[.' + contexts + ' = eps])',
                    '~$call_descriptors_valid(S_callback[.' + contexts + ' = eps])',
                    *reached('S_result', '$seek(S_callback,"result","A",600)'),
                    'S_result.TODO = (THROW_SEARCH n_first) :: (DESTRUCTOR_RESULT pdestructorcall_a) :: ptask_result_tail*',
                    'S_result.FRAMES = eps', 'S_result.CURRENT = eps', 'S_result.ORIGIN = eps',
                    '$throwable_live(S_result,n_first)', '$source_static_user_source(S_result)',
                    '$source_static_exit_throw(S_result,n_first,(DESTRUCTOR_RESULT pdestructorcall_a) :: ptask_result_tail*,0)',
                    '~$exception_terminal_tail(S_result,(DESTRUCTOR_RESULT pdestructorcall_a) :: ptask_result_tail*)',
                    '$eager_bailout_source(S_result) = eps', *public('S_result'),
                    '~$call_descriptors_valid(S_result[.DESTRUCTION.CALLS = eps])',
                    '~$source_static_exit_throw(S_result,n_a,(DESTRUCTOR_RESULT pdestructorcall_a) :: ptask_result_tail*,0)',
                    '~$exit_unwind_valid(S_result[.TODO = (THROW_SEARCH n_first) :: (EXIT_UNWIND 0) :: (' + marker + ') :: ptask_tail*],0)',
                    *reached('S_pending', '$seek(S_result,"exit-operation","",600)'),
                    'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (EXIT_UNWIND 0) :: (' + marker + ') :: ptask_tail*',
                    'pdestructionoperation_pending = pdestructionoperation_a[.PENDING = (n_first)]',
                    '$eager_operation_completion_roots(pdestructionoperation_pending) = [HOBJECT n_first]',
                    '$source_static_exit_prefix(S_pending,DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending,0)',
                    '~$exit_unwind_operation((pdestructionoperation_pending),0)', *public('S_pending'),
                    '~$call_descriptors_valid(S_pending[.DESTRUCTION.OPERATIONS = eps])',
                    '~$source_static_exit_operation(S_pending,(pdestructionoperation_pending[.PENDING = (n_b)]),0)',
                    'S_cancelled = $one(S_pending)',
                    'S_cancelled.TODO = (THROW_SEARCH n_first) :: (' + marker + ') :: ptask_tail*',
                    'S_cancelled.DESTRUCTION.OPERATIONS = eps', 'S_cancelled.STATICS = [pstaticcell_b]',
                    'S_cancelled.' + contexts + ' = S.' + contexts, '$source_static_user_source(S_cancelled)',
                    '$destructor_user_source(S_cancelled)', *public('S_cancelled'),
                    *reached('S_second', '$drive_steps(S_cancelled,1)'), 'S_second.STATICS = eps',
                    'S_second.DESTRUCTION.OPERATIONS = [pdestructionoperation_b]',
                    'pdestructionoperation_b.SOURCE = THROW_SEARCH n_first', 'pdestructionoperation_b.PENDING = (n_first)',
                    '$eager_operation_completion_roots(pdestructionoperation_b) = [HOBJECT n_first]', *public('S_second'),
                    *reached('S_callback_b', '$seek(S_second,"callback","B",600)'),
                    'S_callback_b.FRAMES = [pframe_b]',
                    'pframe_b.TODO = (DESTRUCTOR_RESULT pdestructorcall_b) :: ptask_callback_b_tail*',
                    'pdestructorcall_b.OBJECT = n_b', 'pdestructorcall_b.USER',
                    'pdestructorcall_b.PENDING = (n_first)', 'pdestructorcall_b.OPERATION = (pdestructionoperation_b)',
                    '$destructor_boundary_valid(S_callback_b,pdestructorcall_b)', *public('S_callback_b'),
                    *reached('S_done', '$seek(S_callback_b,"throw-operation","",600)'),
                    'S_done.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done) :: (' + marker + ') :: ptask_tail*',
                    'pdestructionoperation_done.PENDING = (n_last)', 'n_last =/= n_first',
                    '$throwable_live(S_done,n_last)', '$throwable_previous_id(S_done,n_last) = (n_first)',
                    '$object_name(S_done,n_last) = $ptascii("TypeError")',
                    '$test_outputs(S_done.EVENTS) = $ptascii("B|a|b|")', *public('S_done'),
                    'S_restored = $one(S_done)',
                    'S_restored.TODO = (THROW_SEARCH n_last) :: (' + marker + ') :: ptask_tail*',
                    'S_restored.DESTRUCTION.OPERATIONS = eps', '$source_static_user_source(S_restored)', *public('S_restored'),
                    'S_crossed = $one(S_restored)', 'S_crossed.' + contexts + ' = eps',
                    'S_crossed.TODO = (THROW_SEARCH n_last) :: ptask_tail*',
                    '~$source_static_user_source(S_crossed)', '$throwable_live(S_crossed,n_last)', *public('S_crossed'),
                    'S_finished = $drive_steps(S_done,1800)', 'S_finished.COMPLETION = NORMAL',
                    '$test_outputs(S_finished.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                    '$test_clean_events(S_finished.EVENTS)', 'S_finished.STATICS = eps', *public('S_finished')]
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names = args.stage or list(STAGES)
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    paths = [Path(__file__), Path(retirement.__file__), ROOT / 'tests/semantics/recorded_worker.py',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    for name in names:
        suite, case = STAGES[name]
        directory = sources / suite / case
        paths += [sources / suite / 'report.json', *sorted(directory.glob('*.php')),
                  *[directory / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                directory = out / name
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(directory / 'protocol.watsup')],
                    directory / label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((directory / 'assertions.json').read_text()))
                report['records'].append({'id': name, 'pass': passed, 'runtime_assertions': count})
                report['runtime_assertions'] += count if passed else 0
                print(name, passed, flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
