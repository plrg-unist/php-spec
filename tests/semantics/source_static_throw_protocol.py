#!/usr/bin/env python3
"""Source-table unwind through genuine eager operations and pending Throwables."""
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
    'eval-body': ('static-native-v1', 'eval-table-throw'),
    'file-body': ('static-native-v8', 'file-closure-body-throw'),
    'eval-override': ('static-native-v2', 'eval-destructor-throw'),
    'eval-remaining': ('static-native-v8', 'eval-closure-remaining-destructor-throw'),
}
PREFIX = r'''dec $stage(pstate,text) : bool
def $stage(S,"throw") = true
  -- if S.TODO = (THROW_SEARCH n) :: (EVAL_END 1) :: ptask_tail*
  -- if $source_static_next(S,1) =/= eps
def $stage(S,"throw") = true
  -- if S.TODO = (THROW_SEARCH n) :: (FILE_END 1) :: ptask_tail*
  -- if $source_static_next(S,1) =/= eps
def $stage(S,"callback") = $destructor_context_kind(S,pcallcontext)
  -- if S.CURRENT = (pcallcontext)
def $stage(S,"operation") = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EVAL_END 1) :: ptask_tail*
def $stage(S,"operation") = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FILE_END 1) :: ptask_tail*
def $stage(S,text) = false -- otherwise
dec $seek(pstate,text,nat) : pstate
def $seek(S,text,n) = S -- if $stage(S,text)
def $seek(S,text,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),text,$nabs($(n - 1)))
  -- if ~$stage(S,text) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,text,n) = S -- otherwise
''' + retirement.PREFIX[retirement.PREFIX.index('dec $one'):]


def reached(name, expression):
    return [name + '_found = ' + expression,
        name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
        name + ' = ' + name + '_found[.COMPLETION = NORMAL]']


def public(name):
    return ['$call_descriptors_valid(' + name + ')', '$declaration_entry_check(' + name + ') = ' + name,
            '$heap_valid($heap_graph(' + name + '))']


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(source, mode, child=None):
            request = {'op': 'parse', 'source': b64(source)} if mode == 'main' else {
                'op': 'parse-' + mode, 'id': '1', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(child)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            return parsed['ast'], fixture

        for name in names:
            suite, case = STAGES[name]
            directory, native = retirement.native_record(sources, suite, case)
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            is_file = name.startswith('file-')
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
            else:
                evaluation = next(node for _, node, _ in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval')
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
            _, child_fixture = checked(child_bytes, 'file' if is_file else 'eval', child_path if is_file else None)
            checks = ['S_wait = $php_file_run(' + main_fixture + ',1200,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                checks += ['S_wait.FILECONTEXTS = [pfilecontext_wait]',
                    'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING',
                    'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker, contexts, context = 'FILE_END 1', 'FILECONTEXTS', 'pfilecontext'
                ownership = ['S.FILECONTEXTS = [pfilecontext]', 'pfilecontext.UNIT = (1)', 'pfilecontext.PHASE = FILE_UNIT_RUN']
            else:
                checks += ['S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
                marker, contexts, context = 'EVAL_END 1', 'EVALCONTEXTS', 'pevalcontext'
                ownership = ['S.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 1', 'pevalcontext.PHASE = UNIT_RUN']
            checks += ['S_ready.COMPLETION = NORMAL', *reached('S', '$seek(S_ready,"throw",1200)'),
                'S.TODO = (THROW_SEARCH n_pending) :: (' + marker + ') :: ptask_tail*',
                *ownership, context + '.OWNER = |S.FRAMES|', context + '.TAIL = ptask_tail*',
                'S.STATICS = [pstaticcell]', '$source_static_next(S,1) = (pstaticcell.ORIGIN)',
                '$source_static_origin(S,pstaticcell.ORIGIN)', '$source_static_running(S,1)',
                'S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_box)', '$throwable_live(S,n_pending)',
                '$task_nodes(THROW_SEARCH n_pending) = [HOBJECT n_pending]', *public('S'),
                '~$call_descriptors_valid(S[.' + contexts + ' = [' + context + '[.OWNER = $nabs($( |S.FRAMES| + 1 ))]]])',
                '~$source_static_running(S[.TODO = [(THROW_SEARCH n_pending)]],1)',
                '~$call_descriptors_valid(S[.TODO = [(THROW_SEARCH n_pending)]])']
            if name == 'eval-remaining':
                checks += ['$test_outputs(S.EVENTS) = $ptascii("B|a|")',
                    '$object_name(S,n_pending) = $ptascii("TypeError")', '$throwable_previous_id(S,n_pending) = eps',
                    '~(HOBJECT n_pending <- $machine_roots(S[.TODO = ptask_tail*]))',
                    '$heap_owners($heap_graph(S),HOBJECT n_pending) = 1']
            else:
                checks += ['$lookup(S.ENV,$ptascii("held")) = (n_held_cell)',
                    'S.STORE[n_held_cell] = DEFINED (POBJECT n_pending)', '$test_outputs(S.EVENTS) = eps']
            checks += ['S_raw = $one(S)', 'S_raw.STATICS = eps', 'S_raw.TODO = S.TODO',
                'S_raw.' + contexts + ' = S.' + contexts, 'S_raw.CURRENT = S.CURRENT', 'S_raw.ORIGIN = S.ORIGIN',
                '$task_nodes(THROW_SEARCH n_pending) = [HOBJECT n_pending]', *public('S_raw'),
                *reached('S_production', '$drive_steps(S,1)'), 'S_production.STATICS = eps',
                'S_production.' + contexts + ' = S.' + contexts,
                'S_production.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
                'pdestructionoperation.PENDING = (n_pending)', 'pdestructionoperation.SOURCE = THROW_SEARCH n_pending',
                'pdestructionoperation.CALLER = S.CURRENT', 'pdestructionoperation.ORIGIN = S.ORIGIN',
                '$eager_operation_completion_roots(pdestructionoperation) = [HOBJECT n_pending]',
                '(HOBJECT n_pending) <- $tasks_nodes(S_production.TODO)', '$throwable_live(S_production,n_pending)',
                '$destructor_operation_valid(S_production,pdestructionoperation)', *public('S_production'),
                *reached('S_callback', '$seek(S_production,"callback",600)'),
                'S_callback.CURRENT = (pcallcontext_destructor)',
                '$destructor_context_kind(S_callback,pcallcontext_destructor)',
                'S_callback.FRAMES = pframe :: pframe_tail*', 'pframe_tail* = S.FRAMES',
                'pframe.CONTEXT = S.CURRENT', 'pframe.ORIGIN = S.ORIGIN',
                'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_callback_tail*',
                'pdestructorcall.OBJECT = n_box', 'pdestructorcall.PENDING = (n_pending)',
                'pdestructorcall.OPERATION = (pdestructionoperation)',
                'S_callback.' + contexts + ' = S.' + contexts, *public('S_callback'),
                *reached('S_done', '$seek(S_callback,"operation",600)'),
                'S_done.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done) :: (' + marker + ') :: ptask_tail*',
                'S_done.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
                'pdestructionoperation_done.PENDING = (n_current)',
                'S_done.' + contexts + ' = S.' + contexts,
                '$eager_operation_completion_roots(pdestructionoperation_done) = [HOBJECT n_current]',
                '$destructor_operation_valid(S_done,pdestructionoperation_done)', *public('S_done')]
            if name == 'eval-override':
                checks += ['n_current =/= n_pending', '$object_name(S_done,n_current) = $ptascii("TypeError")',
                    '$throwable_previous_id(S_done,n_current) = (n_pending)',
                    '$test_outputs(S_done.EVENTS) = $ptascii("D|")']
            else:
                checks += ['n_current = n_pending', 'pdestructionoperation_done = pdestructionoperation',
                    '$test_outputs(S_done.EVENTS) = $ptascii(' + json.dumps('B|a|b|' if name == 'eval-remaining' else 'D|') + ')']
            checks += ['S_restored = $one(S_done)',
                'S_restored.TODO = (THROW_SEARCH n_current) :: (' + marker + ') :: ptask_tail*',
                'S_restored.DESTRUCTION.OPERATIONS = eps', 'S_restored.CURRENT = S.CURRENT',
                'S_restored.ORIGIN = S.ORIGIN', 'S_restored.' + contexts + ' = S.' + contexts,
                '$source_static_next(S_restored,1) = eps', '$throwable_live(S_restored,n_current)', *public('S_restored'),
                'S_crossed = $one(S_restored)', 'S_crossed.' + contexts + ' = eps',
                'S_crossed.TODO = (THROW_SEARCH n_current) :: ptask_tail*',
                '~$source_static_running(S_crossed,1)', '$throwable_live(S_crossed,n_current)', *public('S_crossed'),
                'S_finished = $drive_steps(S_done,1200)', 'S_finished.COMPLETION = NORMAL',
                '$test_clean_events(S_finished.EVENTS)',
                '$test_outputs(S_finished.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')',
                'S_finished.STATICS = eps', *public('S_finished')]
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
