#!/usr/bin/env python3
"""Checked main preflight validates source modifier positions before publication."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import os
import subprocess
import tempfile
import time

import static_types as types
import method_keyword_metadata as metadata_test
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GuardWorker(Worker):
    def __init__(self, command, output):
        self.launch_path = output.with_suffix('.launch.json')
        self.launch = {'supplied_argv': command, 'cwd': os.getcwd(), 'supplied_environment': dict(types.ENV),
                       'started': time.time(), 'status': 'launching'}
        self.save_launch()
        try:
            super().__init__(command, output)
            self.launch.update(popen_args=self.p.args, pid=self.p.pid, pgid=os.getpgid(self.p.pid), status='running')
        except BaseException as error:
            self.launch.update(status='launch_failure', error=type(error).__name__ + ': ' + str(error))
            raise
        finally:
            self.save_launch()

    def save_launch(self):
        self.launch_path.write_text(json.dumps(self.launch, indent=2) + '\n')

    def close(self):
        try:
            super().close()
        finally:
            close = self.output / 'close.json'
            self.launch.update(ended=time.time(), observed_exit_status=self.p.returncode,
                               status='observed_close' if self.p.returncode is not None else 'unknown_failure',
                               original_close=json.loads(close.read_text()) if close.exists() else None)
            self.save_launch()


def prepare(out):
    frontend, adapter = None, None
    originals, rows = {}, []
    try:
        frontend = GuardWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
                                'extension=' + str(ROOT / '.tools/php-file.so'),
                                str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = GuardWorker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index in (0, 3):
            source, line, order = metadata_test.COMBINED_CASES[index]
            source_path = out / ('source-' + str(index) + '.php')
            source_path.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'] and metadata_test.modifier_order(parsed['ast']) == order
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['ast'] == parsed['ast']
            positions = metadata_test.method(parsed['ast'])['meta']
            assert int(positions['methodKeywordLine']['int']) == line
            readonly = not (max(int(positions['methodAbstractTokenPos']['int']),
                                int(positions['methodFinalTokenPos']['int'])) < int(positions['methodReadonlyTokenPos']['int']))
            message = ('Cannot use the readonly modifier on a method' if readonly else
                       'Cannot use the final modifier on an abstract method')
            originals[index] = checked
            rows.append({'id': 'legitimate-' + str(index), 'fixture': checked['fixture'],
                         'completion': 'COMPILETHROWN $ptascii(' + json.dumps(message) + ') ' + str(line)})

        base = originals[0]
        metadata = metadata_test.method(base['ast'])['meta']
        name_metadata = metadata_test.method(base['ast'])['fields'][3]['meta']
        start, keyword, end = [int(metadata[key]['int']) for key in
                               ('startTokenPos', 'methodKeywordTokenPos', 'endTokenPos')]
        name_start = int(name_metadata['startTokenPos']['int'])
        attributes = ['methodKeywordTokenPos', *metadata_test.MODIFIER_ATTRIBUTES.values()]
        mutations = [(key + '-missing', 'method', key, None) for key in attributes]
        mutations += [(key + '-duplicate', 'duplicate', key, int(metadata[key]['int'])) for key in attributes]
        mutations += [('readonly-equals-abstract', 'method', 'methodReadonlyTokenPos', int(metadata['methodAbstractTokenPos']['int'])),
                      ('readonly-equals-final', 'method', 'methodReadonlyTokenPos', int(metadata['methodFinalTokenPos']['int'])),
                      ('abstract-equals-final', 'method', 'methodAbstractTokenPos', int(metadata['methodFinalTokenPos']['int']))]
        mutations += [(key + '-negative', 'method', key, -1) for key in attributes]
        mutations += [('keyword-at-name', 'method', 'methodKeywordTokenPos', name_start),
                      ('readonly-at-keyword', 'method', 'methodReadonlyTokenPos', keyword),
                      ('readonly-before-method-start', 'method', 'methodReadonlyTokenPos', start - 1),
                      ('method-start-negative', 'method', 'startTokenPos', -1),
                      ('method-end-inverted', 'method', 'endTokenPos', start - 1),
                      ('name-start-negative', 'name', 'startTokenPos', -1),
                      ('name-end-inverted', 'name', 'endTokenPos', name_start - 1),
                      ('name-end-outside-method', 'name', 'endTokenPos', end + 1),
                      ('name-start-before-method', 'name', 'startTokenPos', start - 1)]
        assert len(mutations) == 24
        for ident, target, key, value in mutations:
            if target == 'duplicate':
                token = '(M' + key + ' (' + str(value) + '))'
                assert base['fixture'].count(token) == 1
                fixture = base['fixture'].replace(token, token + ', ' + token)
            else:
                ast = copy.deepcopy(base['ast'])
                method = metadata_test.method(ast)
                destination = method['meta'] if target == 'method' else method['fields'][3]['meta']
                if value is None:
                    del destination[key]
                else:
                    destination[key] = {'int': str(value)}
                checked = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})
                assert checked['ok'] and checked['ast'] == ast
                fixture = checked['fixture']
            message = ('parser modifier order source positions' if key in ('startTokenPos', 'endTokenPos') else
                       'combined method modifier token order')
            rows.append({'id': ident, 'fixture': fixture, 'completion': 'UNSUPPORTED ' + json.dumps(message)})
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    filename = '(' + types.byte_expr(str(out / 'source-0.php')) + ')'
    conditions = []
    for index, row in enumerate(rows):
        p, s = 'P_' + str(index), 'S_' + str(index)
        conditions += [p + ' = $ppstart(0, ' + row['fixture'] + ', ' + filename + ')',
                       s + ' = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 0 ' + filename + ']], ' + p + ')',
                       s + '.COMPLETION = ' + row['completion'], s + '.SOURCES = eps', s + '.CLASSES = eps',
                       s + '.FUNCTIONS = eps', s + '.TODO = eps', s + '.EVENTS = eps',
                       s + '.DECLARATIONS = [PDENTER 0 eps 30719, PDEXIT 0 (PCSMAINREJECT ' + p + '.FOLD.SOURCE.AST)]',
                       '~' + s + '.COMPILESTOP', '$declaration_history_valid(' + s + ')']
    assert len(rows) == 26 and len(conditions) == 286
    fixture = out / 'main-preflight.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in conditions))
    (out / 'cases.json').write_text(json.dumps(rows, indent=2) + '\n')
    return fixture


def run():
    before = types.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='compiler-method-modifiers-', dir=ROOT / '.tools'))
    fixture = prepare(out)
    assert before == types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *map(str, modules), str(fixture)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    launch = {'supplied_argv': command, 'cwd': str(ROOT), 'supplied_environment': dict(types.ENV),
              'started': time.time(), 'status': 'launching', 'timeout_seconds': 120}
    launch_path = out / 'numeric.launch.json'
    save_launch = lambda: launch_path.write_text(json.dumps(launch, indent=2) + '\n')
    save_launch()
    process, status, error = None, None, None
    cleanup_errors = []
    with (out / 'stdout').open('wb') as stdout, (out / 'stderr').open('wb') as stderr:
        try:
            process = subprocess.Popen(command, cwd=ROOT, env=types.ENV, stdout=stdout, stderr=stderr)
            launch.update(popen_args=process.args, pid=process.pid, pgid=os.getpgid(process.pid), status='running')
            save_launch()
            status = process.wait(timeout=120)
        except (subprocess.TimeoutExpired, OSError) as caught:
            error = type(caught).__name__ + ': ' + str(caught)
        finally:
            if process:
                if process.poll() is None:
                    process.kill()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    cleanup_errors.append('numeric producer did not close within cleanup5; status unknown')
            launch.update(observed_exit_status=status, cleanup_exit_status=process.returncode if process else None,
                          ended=time.time(), error=error, cleanup_errors=cleanup_errors,
                          status='observed_exit' if status is not None else 'unknown_failure')
            save_launch()
    (out / 'status.json').write_text(json.dumps({'observed_exit_status': status, 'error': error,
                                               'cleanup_errors': cleanup_errors}) + '\n')
    stable = before == types.syntax_validation.implementation_fingerprint()
    passed = status == 0 and error is None and not cleanup_errors and (out / 'stdout').read_bytes() == b'true\n' and not (out / 'stderr').read_bytes() and stable
    report = {'result': 'pass' if passed else 'timeout_unknown' if status is None else 'fail',
              'exit_status': status, 'cases': 26, 'overlapping_predicates': 286, 'fingerprint': before,
              'inputs_stable': stable, 'fixture_sha256': sha(fixture),
              'stdout_sha256': sha(out / 'stdout'), 'stderr_sha256': sha(out / 'stderr')}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
