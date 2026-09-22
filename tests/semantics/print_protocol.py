#!/usr/bin/env python3
"""Print paused origins, queued continuations and temporary-owner controls."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('array-owner', b'<?php function f($x){return [$x];}echo print f(2);',
     'S.TODO = (PRINT_EMIT porigin z) :: ptask*', [
        'S.TODO = (PRINT_EMIT porigin z) :: ptask*',
        'S.RESULT = KNOWN (PARRAY n_array)',
        '$print_task_valid(S, porigin, z)',
        '$call_tasks_valid(S, S.TODO)',
        '~$print_task_valid(S, porigin, 999)',
        '~$print_task_valid(S[.SOURCES = eps], porigin, z)',
        '~$print_task_valid(S[.CODE = eps], porigin, z)',
        'S_bad = $drive(S[.TODO = (PRINT_EMIT porigin 999) :: ptask*], 1000)',
        'S_bad.COMPLETION = UNSUPPORTED text',
        '~$print_task_valid(S[.ORIGIN = eps], porigin, z)',
        '~$print_task_valid(S, PORIGIN 999 eps, z)',
        '$heap_valid($heap_graph(S))',
        '$($heap_owners($heap_graph(S), HARRAY n_array) > 0)',
        'S_done = $drive(S,1000)',
        'S_done.COMPLETION = NORMAL',
        '$outputs(S_done.EVENTS) = [65,114,114,97,121,49]',
        '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
        '$heap_valid($heap_graph(S_done))',
        'S_done.HELD = eps',
        'S_done.FRAMES = eps',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
    ('suspended-child', b'<?php function f(){return print "A";}echo print f();',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("f")', [
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        '$call_descriptors_valid(S)',
        '$call_frames_valid(S, S.FRAMES)',
        'S_done = $drive(S,1000)',
        'S_done.COMPLETION = NORMAL',
        '$outputs(S_done.EVENTS) = [65,49,49]',
        '$heap_valid($heap_graph(S_done))',
        'S_done.HELD = eps',
        'S_done.FRAMES = eps',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
    ('nested-queue', b'<?php echo print print "A";',
     'S.TODO = (PRINT_EMIT porigin z) :: ptask*', [
        'S.TODO = (PRINT_EMIT porigin z) :: ptask*',
        '$call_tasks_valid(S, S.TODO)',
        '$print_task_valid(S, porigin, z)',
        'porigin_outer = PORIGIN 0 ([PCINDEX 0, PCFIELD 0, PCINDEX 0])',
        '~$print_task_valid(S, porigin_outer, z)',
        'S_done = $drive(S,1000)',
        'S_done.COMPLETION = NORMAL',
        '$outputs(S_done.EVENTS) = [65,49,49]',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
    ('object-abrupt', b'<?php print new stdClass; echo "unreachable";',
     'S.TODO = (PRINT_EMIT porigin z) :: ptask*', [
        'S.TODO = (PRINT_EMIT porigin z) :: ptask*',
        'S.RESULT = KNOWN (POBJECT n_object)',
        '$call_tasks_valid(S, S.TODO)',
        '$heap_valid($heap_graph(S))',
        'S_done = $drive(S,1000)',
        'S_done.COMPLETION =/= NORMAL',
        '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
        '$outputs(S_done.EVENTS) = eps',
        '$heap_valid($heap_graph(S_done))',
        'S_done.HELD = eps',
        'S_done.FRAMES = eps',
        'S_done = $drive(S_initial[.COMPLETION = NORMAL],1000)',
     ]),
]

PREFIX = '''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate, nat) : pstate
def $seek(S, n) = S -- if $stage(S)
def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$stage(S)
  -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''


def main():
    out = Path(tempfile.mkdtemp(prefix='print-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    results = []
    for name, source, stage, checks in CASES:
        directory = out / name
        directory.mkdir()
        path = directory / 'source.php'
        path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]'] + checks
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + line + '\n' for line in conditions))
        process = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                  *modules, str(fixture)], capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stderr[-2400:])
        results.append({'name': name, 'assertions': len(conditions),
                        'source_sha256': hashlib.sha256(source).hexdigest()})
        print(name, len(conditions), flush=True)
    assert before == request.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'assertions': sum(r['assertions'] for r in results),
              'cases': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, 'pass')


if __name__ == '__main__':
    main()
