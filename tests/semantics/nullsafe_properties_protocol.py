#!/usr/bin/env python3
"""Paused source, short-circuit and temporary-owner controls."""
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
    (
        'source-base',
        b'<?php\nclass C{}\n$o=new C;\necho ($o?->missing\n    ->x)===null?"Z":"X";\n',
        'S.TODO = (NULLSAFE_PROP_PREP phpType20 z b) :: ptask*',
        [
            'S.TODO = (NULLSAFE_PROP_PREP phpType20 z b) :: ptask*',
            'S.BASE = BASE_CHAIN_PROPERTY pvalue ptbytes z_prefix',
            'z_prefix = 4',
            '$call_tasks_valid(S, S.TODO)',
            '$nullsafe_base_phase_valid(S)',
            '~$nullsafe_base_phase_valid(S[.BASE = BASE_CHAIN_PROPERTY pvalue ptbytes 99])',
            '~$nullsafe_base_phase_valid(S[.BASE = BASE_CHAIN_PROPERTY pvalue $ptascii("forged") z_prefix])',
            '$origin_child(S.ORIGIN, [PCFIELD 0]) = (porigin_child)',
            '$origin_node(S.SOURCES, porigin_child) = (NExprNullsafePropertyFetch expression_receiver (NIdentifier (BYTES text) metadata_name) metadata)',
            '~$call_task_valid(S[.ORIGIN = (porigin_child)], EVAL (NExprNullsafePropertyFetch expression_receiver (NIdentifier (BYTES "eQ==") metadata_name) metadata))',
        ],
    ),
    (
        'taken-short',
        b'<?php $o=null;function ix(){echo "I";return 0;}echo ($o?->p[ix()]->q)===null?"Z":"X";',
        'S.BASE = BASE_SHORT',
        [
            'S.BASE = BASE_SHORT',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_bad = S[.TODO = eps]',
            '~$nullsafe_base_phase_valid(S_bad)',
            'S_done = $drive(S,1000)',
            'S_done.COMPLETION = NORMAL',
            '$outputs(S_done.EVENTS) = [90]',
            '$heap_valid($heap_graph(S_done))',
            'S_done.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_done.HELD = eps',
            'S_done.FRAMES = eps',
            'S_final = $drive(S_initial[.COMPLETION = NORMAL],1000)',
            'S_done = S_final',
        ],
    ),
    (
        'saved-owner',
        b'<?php class C{public $p=7;}function make(){return new C;}function name(){echo "N";return "p";}echo make()?->{name()};',
        'S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("name")',
        [
            'S.CURRENT = (pcallcontext)',
            'S.FRAMES = pframe :: pframe_tail*',
            '$class_state_valid(S)',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S.OBJECTPROPS = [pobjectprops]',
            '$($heap_owners($heap_graph(S),HOBJECT pobjectprops.OBJECT) > 0)',
            '~$nullsafe_base_phase_valid(S[.BASE = BASE_SHORT])',
            'S_done = $drive(S,1000)',
            'S_done.COMPLETION = NORMAL',
            '$outputs(S_done.EVENTS) = [78,55]',
            '$heap_valid($heap_graph(S_done))',
            '$heap_owners($heap_graph(S_done),HOBJECT pobjectprops.OBJECT) = 0',
            'S_done.OBJECTPROPS = eps',
            'S_done.HELD = eps',
            'S_done.FRAMES = eps',
            'S_final = $drive(S_initial[.COMPLETION = NORMAL],1000)',
            'S_done = S_final',
        ],
    ),
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
    out = Path(tempfile.mkdtemp(prefix='nullsafe-properties-protocol-', dir=ROOT / '.tools'))
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
