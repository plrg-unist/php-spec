#!/usr/bin/env python3
"""Check a source-derived eval barrier saved by a nested function call."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-saved-protocol-', dir=ROOT / '.tools'))
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
    source = b'''<?php eval('function f(){eval("return 3;");} f();'); echo 'after';'''
    outer = b'function f(){eval("return 3;");} f();'
    inner = b'return 3;'
    source_path = out / 'source.php'
    source_path.write_bytes(source)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        fixtures = []
        for unit, data in [(1, outer), (2, inner)]:
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                                            'profile': 'cli-raw-85',
                                            'source': base64.b64encode(data).decode()})
            assert parsed_eval['accepted'], parsed_eval
            fixtures.append(adapter.request({'op': 'check', 'ast': parsed_eval['ast'],
                                             'fixture': True})['fixture'])
    finally:
        frontend.close()
        adapter.close()
    initial = '$php_run(' + checked['fixture'] + ', 500, ' + json.dumps(
        base64.b64encode(str(source_path).encode()).decode()) + ')'
    responses = ['(SOURCE_ACCEPT ' + str(unit) + ' (' + str(list(data)) + ') ' + fixture + ')'
                 for unit, data, fixture in [(1, outer, fixtures[0]), (2, inner, fixtures[1])]]
    conditions = [
        'S = ' + initial,
        'S.COMPLETION = SOURCE_PENDING',
        '$call_descriptors_valid(S)',
        'S.SERVICELEFT = (n_first)',
        '$(n_first < 500)',
        '$(n_first > 1)',
        'n_low = $(501 - n_first)',
        'S_low = $php_run(' + checked['fixture'] + ', n_low, ' + json.dumps(
            base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_low.COMPLETION = SOURCE_PENDING',
        'S_low.SERVICELEFT = (1)',
        '$call_descriptors_valid(S_low)',
        'S_low_after = $eval_continue(S_low, ' + responses[0] + ')',
        'S_low_after.COMPLETION = BUDGET',
        'S_inner = $eval_continue(S, ' + responses[0] + ')',
        'S_inner.COMPLETION = SOURCE_PENDING',
        'S_inner.SERVICELEFT = (n_second)',
        '$(n_second < n_first)',
        '$call_descriptors_valid(S_inner)',
        'S_inner.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer :: eps',
        'S_inner.EVALBINDINGS = [pevalbinding]',
        '~$call_descriptors_valid(S_inner[.EVALBINDINGS = eps])',
        '~$call_descriptors_valid(S_inner[.EVALBINDINGS = [pevalbinding, pevalbinding]])',
        'pevalcontext_inner.PHASE = PARSER_WAIT',
        'pevalcontext_outer.PHASE = UNIT_RUN',
        '$(pevalcontext_inner.UNIT > pevalcontext_outer.UNIT)',
        'S_inner.TODO = (EVAL_AWAIT n_inner) :: ptask_current*',
        'n_inner = pevalcontext_inner.UNIT',
        'S_inner.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = ptask_a :: ptask_b :: ptask_c :: (EVAL_END n_outer) :: ptask_saved_tail*',
        'n_outer = pevalcontext_outer.UNIT',
        '~$call_descriptors_valid(S_inner[.FRAMES = pframe[.TODO = ptask_a :: ptask_b :: ptask_c :: ptask_saved_tail*] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner[.FRAMES = pframe[.TODO = ptask_a :: ptask_b :: ptask_c :: (EVAL_END 999) :: ptask_saved_tail*] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner[.FRAMES = pframe[.TODO = (EVAL_END n_outer) :: ptask_a :: ptask_b :: ptask_c :: ptask_saved_tail*] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner[.EVALCONTEXTS = pevalcontext_outer :: pevalcontext_inner :: eps])',
        '~$call_descriptors_valid(S_inner[.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer[.PHASE = PARSER_WAIT] :: eps])',
        '~$call_descriptors_valid(S_inner[.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer[.OWNER = $(pevalcontext_outer.OWNER + 1)] :: eps])',
        '~$call_descriptors_valid(S_inner[.EVALCONTEXTS = pevalcontext_inner :: pevalcontext_outer[.TAIL = pevalcontext_outer.TAIL ++ [DISCARD]] :: eps])',
        'S_done = $eval_continue(S_inner, ' + responses[1] + ')',
        'S_done.COMPLETION = NORMAL',
        'S_done.EVALCONTEXTS = eps',
        'S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done)',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in conditions))
    command = [str(runner), *map(str, modules), str(fixture)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    result = subprocess.run(command, capture_output=True, timeout=300)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    (out / 'report.json').write_text(json.dumps({
        'result': 'pass' if passed else 'fail', 'assertions': len(conditions),
        'inputs': before, 'source_sha256': digest(source_path),
        'fixture_sha256': digest(fixture), 'runner_exit_status': result.returncode,
        'scope': 'Source-derived nested eval with saved outer barrier and intact replay.'
    }, indent=2) + '\n')
    print('saved-barrier', passed, len(conditions), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
