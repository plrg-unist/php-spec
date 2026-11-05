#!/usr/bin/env python3
"""Keep unmodeled callback creation and nested-handler starts explicit."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import request_environment as request_env
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REASON = 'output-handler start after output deactivation'
CASES = {
    'reentrant': b'FX|D1|H1|',
    'invalid_ob08': b'FX|D1|',
}


def run():
    out = Path(tempfile.mkdtemp(prefix='output-post-deactivate-boundaries-',
                                dir=ROOT / '.tools'))
    frontend = Worker([str(request_env.t.PHP), '-n', *request_env.t.FLAGS,
                       '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     out / 'adapter', seconds=120)
    records = []
    try:
        for name, expected_stdout in CASES.items():
            source = HERE / ('output_executor_post_deactivate_' + name + '.php')
            path = out / (name + '.php')
            path.write_bytes(source.read_bytes())
            parsed = frontend.request({'op': 'parse', 'source': request_env.b64(path.read_bytes())})
            assert parsed['accepted'], name
            context = {'env': [[request_env.b64(key), request_env.b64(value)]
                               for key, value in ((b'LC_ALL', b'C'), (b'TZ', b'UTC'),
                                                  (b'FIRST', b'one'))],
                       'argv': [request_env.b64(os.fsencode(path))],
                       'file': request_env.b64(os.fsencode(path)),
                       'seconds': '1700000000', 'microseconds': 125000,
                       'variables': request_env.b64(b'EGPCS'), 'jit': True,
                       'cwd': request_env.b64(os.fsencode(out))}
            result = adapter.request({'op': 'execute', 'ast': parsed['ast'],
                                      'steps': 10000,
                                      'filename': request_env.b64(os.fsencode(path)),
                                      'request': context})
            state = result['state']
            completion = state['COMPLETION']
            stdout = b''.join(bytes(map(int, event['args'][0]))
                              for event in state['EVENTS'] if event['tag'] == 'OUTPUT')
            passed = (completion == {'tag': 'UNSUPPORTED', 'args': [REASON]}
                      and stdout == expected_stdout and not state['OUTPUTBUFFERS']
                      and int(state['OUTPUTSEQ']) == 1)
            records.append({'case': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'completion': completion, 'stdout': stdout.decode('ascii'),
                            'output_seq': state['OUTPUTSEQ'], 'passed': passed})
            print(name, passed, completion['tag'], flush=True)
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    report = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                               text=True).strip(),
              'reason': REASON, 'records': records, 'passed': all(row['passed'] for row in records),
              'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['passed'])
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
