#!/usr/bin/env python3
"""Genuine source slots, caller Closure tables, cached cells and escaped aliases."""
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
    'eval-cache': 'eval-closure-cache-reference',
    'file-cache': 'file-closure-cache-reference',
    'nested-eval': 'eval-closure-nested-isolation',
}
PREFIX = r'''dec $at_init(pstate,nat) : bool
def $at_init(S,n) = true -- if S.TODO = (STATIC_INIT (PORIGIN n pcpath)) :: ptask_tail*
def $at_init(S,n) = false -- otherwise
dec $at_end(pstate,nat) : bool
def $at_end(S,n) = true -- if S.TODO = (EVAL_END n) :: ptask_tail*
def $at_end(S,n) = true -- if S.TODO = (FILE_END n) :: ptask_tail*
def $at_end(S,n) = false -- otherwise
dec $seek_init(pstate,nat,nat) : pstate
def $seek_init(S,n,n_steps) = S -- if $at_init(S,n)
def $seek_init(S,n,n_steps) = $seek_init($drive_steps(S[.COMPLETION = NORMAL],1),n,$nabs($(n_steps - 1)))
  -- if ~$at_init(S,n) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n_steps > 0)
def $seek_init(S,n,n_steps) = S -- otherwise
dec $seek_end(pstate,nat,nat) : pstate
def $seek_end(S,n,n_steps) = S -- if $at_end(S,n)
def $seek_end(S,n,n_steps) = $seek_end($drive_steps(S[.COMPLETION = NORMAL],1),n,$nabs($(n_steps - 1)))
  -- if ~$at_end(S,n) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n_steps > 0)
def $seek_end(S,n,n_steps) = S -- otherwise
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
            directory, native = retirement.native_record(sources, 'static-native-v7', STAGES[name])
            main_path = directory / 'main.php'
            main_ast, main_fixture = checked(main_path.read_bytes(), 'main')
            is_file = name == 'file-cache'
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
            else:
                evaluation = next(node for _, node, _ in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval')
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
            child_ast, child_fixture = checked(child_bytes, 'file' if is_file else 'eval', child_path if is_file else None)

            def resume(state, number, result):
                if not is_file:
                    return [result + ' = $eval_resume(' + state + ',SOURCE_ACCEPT ' + str(number) + ' ' + seq(child_bytes) + ' ' + child_fixture + ')', result + '.COMPLETION = NORMAL']
                return [state + '.FILECONTEXTS = [pfilecontext_' + str(number) + ']',
                    result + '_parse = $file_open_resume(' + state + ',FILE_OPENED pfilecontext_' + str(number) + '.NONCE pfilecontext_' + str(number) + '.CALLER pfilecontext_' + str(number) + '.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    result + '_parse.COMPLETION = SOURCE_PENDING',
                    result + ' = $file_parse_resume(' + result + '_parse,SOURCE_ACCEPT ' + str(number) + ' ' + seq(child_bytes) + ' ' + child_fixture + ')', result + '.COMPLETION = NORMAL']

            checks = ['S_wait = $php_file_run(' + main_fixture + ',1200,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING', *resume('S_wait', 1, 'S_ready'),
                *reached('S', '$seek_init(S_ready,1,600)'),
                'S.TODO = (STATIC_INIT porigin_source) :: ptask_tail*', 'porigin_source = PORIGIN 1 pcpath_source',
                'S.CURRENT = (pcallcontext)', 'pcallcontext.INSTANCE = (n_closure)',
                '$object_body(S.OBJECTS[n_closure]) = REALCLOSURE porigin_template pitem* ([pstaticcell_own])',
                '$function_at(S.CLOSURETEMPLATES,porigin_template) = (pfunction)',
                'S.STATICS = eps', '~$source_static_origin(S,pstaticcell_own.ORIGIN)',
                '$source_static_origin(S,porigin_source)', '$source_static_running(S,1)',
                '$static_task_valid(S,porigin_source,false)',
                '$state_static_at(S,pstaticcell_own.ORIGIN) = (pstaticcell_own.CELL)',
                '$state_static_at(S,porigin_source) = eps', *public('S'),
                'S_added = $one(S)', 'S_added.STATICS = [pstaticcell_source]',
                'pstaticcell_source.ORIGIN = porigin_source', 'pstaticcell_source.CELL =/= pstaticcell_own.CELL',
                'S_added.OBJECTS = S.OBJECTS', 'S_added.CLOSURESCOPES = S.CLOSURESCOPES',
                'S_added.CLOSUREBINDINGS = S.CLOSUREBINDINGS', 'S_added.CURRENT = S.CURRENT',
                '$lookup(S_added.ENV,$ptascii("own")) = (pstaticcell_own.CELL)',
                '$lookup(S_added.ENV,$ptascii("x")) = (pstaticcell_source.CELL)',
                '$state_static_at(S_added,porigin_source) = (pstaticcell_source.CELL)',
                '$closure_static_cells_valid(S_added,pfunction,[pstaticcell_own])', *public('S_added'),
                'S_bad = S_added[.STATICS = eps][.OBJECTS = $object_set(S_added.OBJECTS,n_closure,REALCLOSURE porigin_template pitem* ([pstaticcell_own,pstaticcell_source]))]',
                '~$closure_static_cells_valid(S_bad,pfunction,[pstaticcell_own,pstaticcell_source])',
                '~$call_descriptors_valid(S_bad)']

            if name != 'nested-eval':
                checks += [*reached('S_repeat', '$seek_init(S_added,1,600)'),
                    'S_repeat.TODO = (STATIC_INIT porigin_source) :: ptask_repeat*',
                    'S_repeat.STATICS = [pstaticcell_source]', 'S_repeat.STORE[pstaticcell_source.CELL] = DEFINED (PINT 1)',
                    '$lookup(S_repeat.ENV,$ptascii("refs")) = (n_refs)', 'S_repeat.STORE[n_refs] = DEFINED (PARRAY n_array)',
                    'S_repeat.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS pstaticcell_source.CELL)]', *public('S_repeat'),
                    'S_rebound = $one(S_repeat)', 'S_rebound.STATICS = S_repeat.STATICS',
                    'S_rebound.OBJECTS = S_repeat.OBJECTS', '$lookup(S_rebound.ENV,$ptascii("x")) = (pstaticcell_source.CELL)',
                    *public('S_rebound'), *reached('S_end', '$seek_end(S_rebound,1,600)'),
                    'S_end.STATICS = [pstaticcell_source]', 'S_end.STORE[pstaticcell_source.CELL] = DEFINED (PINT 2)',
                    'S_end.STORE[n_refs] = DEFINED (PARRAY n_end_array)',
                    'S_end.ARRAYS[n_end_array].ITEMS = [ENTRY (KINT 0) (ALIAS pstaticcell_source.CELL),ENTRY (KINT 1) (ALIAS pstaticcell_source.CELL)]',
                    'S_end.STORE[pstaticcell_own.CELL] = DEFINED (PINT 100)', *public('S_end'),
                    'S_dropped = $one(S_end)', 'S_dropped.STATICS = eps', 'S_dropped.OBJECTS = S_end.OBJECTS',
                    'S_dropped.TODO = S_end.TODO', 'S_dropped.STORE[pstaticcell_source.CELL] = DEFINED (PINT 2)',
                    '(HCELL pstaticcell_source.CELL) <- S_dropped.ALLOCATIONS', *public('S_dropped'),
                    'S_retired = $one(S_dropped)', '~$source_static_running(S_retired,1)', *public('S_retired'),
                    'S_pending = $drive_steps(S_retired,1200)', 'S_pending.COMPLETION = SOURCE_PENDING',
                    'S_pending.STATICS = eps', *public('S_pending'), *resume('S_pending', 2, 'S_second'),
                    *reached('S_fresh', '$seek_init(S_second,2,600)'),
                    'S_fresh.TODO = (STATIC_INIT porigin_fresh) :: ptask_fresh*', 'porigin_fresh = PORIGIN 2 pcpath_source',
                    'S_fresh.CURRENT = (pcallcontext_fresh)', 'pcallcontext_fresh.INSTANCE = (n_closure)',
                    'S_fresh.STATICS = eps', '$state_static_at(S_fresh,porigin_source) = eps',
                    '$state_static_at(S_fresh,porigin_fresh) = eps', *public('S_fresh'),
                    'S_installed = $one(S_fresh)', 'S_installed.STATICS = [pstaticcell_fresh]',
                    'pstaticcell_fresh.ORIGIN = porigin_fresh', 'pstaticcell_fresh.CELL =/= pstaticcell_source.CELL',
                    'pstaticcell_fresh.CELL =/= pstaticcell_own.CELL', 'S_installed.STORE[pstaticcell_fresh.CELL] = DEFINED (PINT 0)',
                    'S_installed.STORE[pstaticcell_source.CELL] = DEFINED (PINT 2)', 'S_installed.OBJECTS = S_fresh.OBJECTS',
                    '$object_body(S_installed.OBJECTS[n_closure]) = REALCLOSURE porigin_template pitem* ([pstaticcell_own])',
                    *public('S_installed')]
            else:
                inner = next(node for _, node, _ in retirement.nodes(child_ast['program']) if node['node'] == 'Expr_Eval')
                inner_bytes = base64.b64decode(inner['fields'][0]['fields'][0]['bytes'])
                _, inner_fixture = checked(inner_bytes, 'eval')
                checks += ['S_pending = $drive_steps(S_added,1200)', 'S_pending.COMPLETION = SOURCE_PENDING',
                    'S_pending.STATICS = [pstaticcell_source]', '$lookup(S_pending.ENV,$ptascii("held")) = (pstaticcell_source.CELL)',
                    *public('S_pending'), 'S_inner_ready = $eval_resume(S_pending,SOURCE_ACCEPT 2 ' + seq(inner_bytes) + ' ' + inner_fixture + ')',
                    'S_inner_ready.COMPLETION = NORMAL', *reached('S_inner', '$seek_init(S_inner_ready,2,600)'),
                    'S_inner.TODO = (STATIC_INIT porigin_inner) :: ptask_inner*', 'porigin_inner = PORIGIN 2 pcpath_inner',
                    '$state_static_at(S_inner,porigin_source) = (pstaticcell_source.CELL)',
                    '$state_static_at(S_inner,porigin_inner) = eps', *public('S_inner'),
                    'S_inner_added = $one(S_inner)', 'S_inner_added.STATICS = [pstaticcell_source,pstaticcell_inner]',
                    'pstaticcell_inner.ORIGIN = porigin_inner', 'pstaticcell_inner.CELL =/= pstaticcell_source.CELL',
                    'pstaticcell_inner.CELL =/= pstaticcell_own.CELL', 'S_inner_added.OBJECTS = S_inner.OBJECTS',
                    '$lookup(S_inner_added.ENV,$ptascii("held")) = (pstaticcell_source.CELL)',
                    '$lookup(S_inner_added.ENV,$ptascii("x")) = (pstaticcell_inner.CELL)',
                    'S_inner_added.STORE[pstaticcell_source.CELL] = DEFINED (PINT 5)',
                    'S_inner_added.STORE[pstaticcell_inner.CELL] = DEFINED (PINT 9)',
                    'S_inner_added.STORE[pstaticcell_own.CELL] = DEFINED (PINT 40)', *public('S_inner_added'),
                    *reached('S_inner_end', '$seek_end(S_inner_added,2,600)'),
                    'S_inner_end.STORE[pstaticcell_inner.CELL] = DEFINED (PINT 10)', *public('S_inner_end'),
                    'S_inner_dropped = $one(S_inner_end)', 'S_inner_dropped.STATICS = [pstaticcell_source]',
                    'S_inner_dropped.OBJECTS = S_inner_end.OBJECTS', *public('S_inner_dropped'),
                    'S_inner_retired = $one(S_inner_dropped)', '~$source_static_running(S_inner_retired,2)',
                    '$source_static_running(S_inner_retired,1)', '$state_static_at(S_inner_retired,porigin_inner) = eps',
                    *public('S_inner_retired'), *reached('S_outer_end', '$seek_end(S_inner_retired,1,600)'),
                    'S_outer_end.STATICS = [pstaticcell_source]', *public('S_outer_end'),
                    'S_outer_dropped = $one(S_outer_end)', 'S_outer_dropped.STATICS = eps', *public('S_outer_dropped'),
                    'S_outer_retired = $one(S_outer_dropped)', '~$source_static_running(S_outer_retired,1)',
                    *public('S_outer_retired'), 'S_next = $drive_steps(S_outer_retired,1200)',
                    'S_next.COMPLETION = SOURCE_PENDING', 'S_next.STATICS = eps', *public('S_next'),
                    '$eval_response_valid(S_next,SOURCE_ACCEPT 3 ' + seq(child_bytes) + ' ' + child_fixture + ')']
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
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', sources / 'static-native-v7/report.json']
    for name in names:
        directory = sources / 'static-native-v7' / STAGES[name]
        paths += [*sorted(directory.glob('*.php')),
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
