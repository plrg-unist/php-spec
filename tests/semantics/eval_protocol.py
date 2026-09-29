#!/usr/bin/env python3
"""Source-derived eval parser pause and one-shot response guards."""
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
    out = Path(tempfile.mkdtemp(prefix='eval-protocol-', dir=ROOT / '.tools'))
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
    source = b'<?php $x=eval("return 4;"); echo "after";'
    eval_bytes = b'return 4;'
    source_path = out / 'source.php'
    source_path.write_bytes(source)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        eval_parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85',
                                        'source': base64.b64encode(eval_bytes).decode()})
        assert eval_parsed['accepted'], eval_parsed
        eval_checked = adapter.request({'op': 'check', 'ast': eval_parsed['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    initial = '$php_run(' + checked['fixture'] + ', 300, ' + json.dumps(
        base64.b64encode(str(source_path).encode()).decode()) + ')'
    response = '(SOURCE_ACCEPT 1 (' + str(list(eval_bytes)) + ') ' + eval_checked['fixture'] + ')'
    response_wrong_id = response.replace('SOURCE_ACCEPT 1 ', 'SOURCE_ACCEPT 999 ', 1)
    response_wrong_bytes = response.replace('[114,', '[115,', 1)
    conditions = [
        'S = ' + initial,
        'S.COMPLETION = SOURCE_PENDING',
        'S.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
        'S.TODO = (EVAL_AWAIT n) :: ptask_tail*',
        'n = pevalcontext.UNIT',
        '$call_descriptors_valid(S)',
        '~$call_descriptors_valid(S[.TODO = ptask_tail*])',
        '~$call_descriptors_valid(S[.TODO = (EVAL_AWAIT n) :: S.TODO])',
        '~$call_descriptors_valid(S[.TODO = (EVAL_AWAIT 999) :: ptask_tail*])',
        '~$call_descriptors_valid(S[.TODO = (AT pevalcontext.SITE (EVAL_AWAIT n)) :: ptask_tail*])',
        '~$call_descriptors_valid(S[.TODO = (CHOOSE S.TODO eps 0) :: ptask_tail*])',
        'pfailedsource = {UNIT n, SITE pevalcontext.SITE, BYTES pevalcontext.BYTES, FILE pevalcontext.FILE, KIND FAILED_PARSE, MESSAGE ([88]), LINE 1}',
        '~$call_descriptors_valid(S[.FAILEDSOURCES = [pfailedsource]])',
        '$eval_response_valid(S, ' + response + ')',
        '~$eval_response_valid(S, ' + response_wrong_id + ')',
        '~$eval_response_valid(S, ' + response_wrong_bytes + ')',
        'S_bad = $eval_resume(S, (SOURCE_PARSE_REJECT n pevalcontext.BYTES eps 1))',
        'S_bad = S[.COMPLETION = UNSUPPORTED "invalid eval parser response"]',
        'S_bad.EVALCONTEXTS = S.EVALCONTEXTS',
        'S_done = $eval_continue(S, ' + response + ')',
        'S_done.COMPLETION = NORMAL',
        'S_done.EVALCONTEXTS = eps',
        '$call_descriptors_valid(S_done)',
        'S_done.EVALBINDINGS = [pevalbinding]',
        '~$call_descriptors_valid(S_done[.EVALBINDINGS = eps])',
        '~$call_descriptors_valid(S_done[.EVALBINDINGS = [pevalbinding,pevalbinding]])',
        '~$eval_response_valid(S_done, ' + response + ')',
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
    report = {'result': 'pass' if passed else 'fail', 'assertions': len(conditions),
              'inputs': before, 'source_sha256': digest(source_path),
              'fixture_sha256': digest(fixture), 'runner_exit_status': result.returncode,
              'scope': 'Source-derived pending state; accepted AST from pinned checked worker.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('pending-response', passed, len(conditions), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
