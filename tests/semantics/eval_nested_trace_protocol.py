#!/usr/bin/env python3
"""Source-derived nested eval trace order across accepted and rejected units."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('nested-runtime',
     b'''<?php try{eval('eval("1/0;");');}catch(DivisionByZeroError $e){echo 'C';}''',
     b'eval("1/0;");', b'1/0;', 'DivisionByZeroError', 2),
    ('nested-parser',
     b'''<?php try{eval('eval("echo ;");');}catch(ParseError $e){echo 'C';}''',
     b'eval("echo ;");', b'echo ;', 'ParseError', 1),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-nested-trace-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py',
              ROOT / 'tests/semantics/static_types.py', ROOT / 'frontend/wire.py',
              ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    for name, source, outer_bytes, inner_bytes, kind, frames in CASES:
        directory = out / name
        directory.mkdir()
        source_path = directory / 'source.php'
        source_path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            eval_results = []
            for index, eval_bytes in enumerate((outer_bytes, inner_bytes), 1):
                parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(index), 'mode': 'eval',
                                                'profile': 'cli-raw-85',
                                                'source': base64.b64encode(eval_bytes).decode()})
                checked_eval = (adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
                                if parsed_eval['accepted'] else None)
                eval_results.append((parsed_eval, checked_eval))
        finally:
            frontend.close()
            adapter.close()
        outer_response = '(SOURCE_ACCEPT n_outer pevalcontext_outer.BYTES ' + eval_results[0][1]['fixture'] + ')'
        inner_parsed, inner_checked = eval_results[1]
        if inner_parsed['accepted']:
            inner_response = '(SOURCE_ACCEPT n_inner pevalcontext_inner.BYTES ' + inner_checked['fixture'] + ')'
        else:
            assert inner_parsed['category'] == 'parser_rejection'
            message = list(base64.b64decode(inner_parsed['message']))
            inner_response = '(SOURCE_PARSE_REJECT n_inner pevalcontext_inner.BYTES (' + str(message) + ') ' + str(inner_parsed['line']) + ')'
        initial = '$php_run(' + checked['fixture'] + ', 500, ' + json.dumps(
            base64.b64encode(str(source_path).encode()).decode()) + ')'
        conditions = [
            'S = ' + initial,
            'S.COMPLETION = SOURCE_PENDING',
            'S.EVALCONTEXTS = pevalcontext_outer :: pevalcontext_tail*',
            'n_outer = pevalcontext_outer.UNIT',
            '$call_descriptors_valid(S)',
            'S1 = $eval_continue(S, ' + outer_response + ')',
            'S1.COMPLETION = SOURCE_PENDING',
            'S1.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_other*',
            'n_inner = pevalcontext_inner.UNIT',
            '$(n_inner > n_outer)',
            '$call_descriptors_valid(S1)',
            'S_done = $eval_continue(S1, ' + inner_response + ')',
            'S_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_done)',
            'n_object = $(|S_done.OBJECTS| - 1)',
            'S_done.OBJECTS[n_object] = THROWABLE pthrowable',
            'pthrowable.KIND = ' + json.dumps(kind),
            'pthrowable.TRACE = [' + ','.join('ptraceframe_' + str(i) for i in range(frames)) + ']',
        ]
        for index in range(frames):
            frame = 'ptraceframe_' + str(index)
            site = 'pevalcontext_inner.SITE' if frames == 2 and index == 0 else 'pevalcontext_outer.SITE'
            conditions.extend([frame + '.NAME = $ptascii("eval")',
                               frame + '.FILE = $call_sourcefile(S.FILES, ' + site + ')',
                               frame + '.LINE = 1'])
        fixture = directory / 'protocol.watsup'
        fixture.write_text('var S1 : pstate\n'
                           'dec $main() : bool\ndef $main() = true\n' + ''.join(
                               '  -- if ' + condition + '\n' for condition in conditions))
        command = [str(runner), *map(str, modules), str(fixture)]
        result = subprocess.run(command, capture_output=True, timeout=300)
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        (directory / 'stdout').write_bytes(result.stdout)
        (directory / 'stderr').write_bytes(result.stderr)
        passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        records.append({'id': name, 'pass': passed, 'assertions': len(conditions),
                        'source_sha256': digest(source_path), 'fixture_sha256': digest(fixture),
                        'runner_exit_status': result.returncode})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'inputs': before, 'records': records,
              'scope': 'Internal generated TRACE frames; getTrace source calls remain Unsupported.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
