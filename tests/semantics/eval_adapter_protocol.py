#!/usr/bin/env python3
"""Keep one adapter state across a rejected and then valid eval response."""
import base64
import hashlib
import importlib.machinery
import json
from pathlib import Path
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CLI = importlib.machinery.SourceFileLoader('php_semantics', str(ROOT / 'bin/php-semantics')).load_module()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-adapter-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    source = b"<?php echo eval('return 4;');"
    eval_bytes = b'return 4;'
    source_path = out / 'source.php'
    source_path.write_bytes(source)
    inputs = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs += [ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                     'extension=' + str(ROOT / '.tools/php-file.so'),
                     str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = CLI.AdapterSession([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    try:
        parsed = worker.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
        first = adapter.request({'op': 'execute', 'ast': parsed['ast'], 'steps': 500,
                                 'filename': base64.b64encode(str(source_path).encode()).decode()}, 30)
        assert first['ok'] and first['pending'] == {
            'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85',
            'source': base64.b64encode(eval_bytes).decode()}
        parsed_eval = worker.request({'op': 'parse-eval', **first['pending']})
        assert parsed_eval['accepted']
        response = {key: value for key, value in parsed_eval.items()
                    if key not in {'ok', 'diagnostics'}}
        wrong = dict(response, id='999')
        rejected = adapter.request({'op': 'resume_eval', 'response': wrong}, 30)
        assert not rejected['ok'] and rejected['category'] == 'adapter_rejection'
        valid = adapter.request({'op': 'resume_eval', 'response': response}, 30)
        assert valid['ok'] and 'pending' not in valid
        observed = CLI.observe(valid['state'], source_path)
        assert observed['status'] == 'normal' and observed['stdout'] == base64.b64encode(b'4').decode()
        replay = adapter.request({'op': 'resume_eval', 'response': response}, 30)
        assert not replay['ok'] and replay['category'] == 'adapter_rejection'
    finally:
        adapter.close()
        worker.close()
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass', 'inputs': before, 'source_sha256': digest(source_path),
              'wrong_identity_category': rejected['category'],
              'valid_status': observed['status'], 'valid_stdout': observed['stdout'],
              'replay_category': replay['category'],
              'scope': 'One persistent adapter session; trusted worker response follows rejected identity.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('adapter-session', report['result'], flush=True)


if __name__ == '__main__':
    main()
