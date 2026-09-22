#!/usr/bin/env python3
"""Paused property-name tasks and temporary receiver ownership."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker
import request_environment as request

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'static': b'<?php class C { public $x=1; } echo (new C)->x;',
    'computed': b'<?php class C { public $x=1; } function chosen(){echo "N"; return "x";} echo (new C)->{chosen()};',
    'abrupt': b'<?php class C { public $x=1; } echo (new C)->{1/0};',
}
PREFIX = '''
dec $property_prep_head(pstate) : bool
def $property_prep_head(S) = true -- if S.TODO = (PROPERTY_PREP phpType20 z) :: ptask*
def $property_prep_head(S) = false -- otherwise
dec $property_name_head(pstate) : bool
def $property_name_head(S) = true -- if S.TODO = (PROPERTY_NAME pvalue z) :: ptask*
def $property_name_head(S) = false -- otherwise
dec $property_seek_prep(pstate, nat) : pstate
def $property_seek_prep(S, n) = S -- if $property_prep_head(S)
def $property_seek_prep(S, 0) = S -- if ~$property_prep_head(S)
def $property_seek_prep(S, n) = $property_seek_prep($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$property_prep_head(S) /\\ $(n > 0)
dec $property_seek_name(pstate, nat) : pstate
def $property_seek_name(S, n) = S -- if $property_name_head(S)
def $property_seek_name(S, 0) = S -- if ~$property_name_head(S)
def $property_seek_name(S, n) = $property_seek_name($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$property_name_head(S) /\\ $(n > 0)
dec $property_outputs(pevent*) : nat*
def $property_outputs(eps) = eps
def $property_outputs((OUTPUT n*) :: pevent*) = n* ++ $property_outputs(pevent*)
def $property_outputs((WARNING n* z) :: pevent*) = $property_outputs(pevent*)
def $property_outputs((DIAGNOSTIC text n* z) :: pevent*) = $property_outputs(pevent*)
'''


def checked_source(source, directory, frontend, adapter):
    path = directory / 'source.php'
    path.write_bytes(source)
    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
    assert parsed['accepted'], parsed
    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
    assert checked['ok'], checked
    return checked['fixture'], path


def main():
    out = Path(tempfile.mkdtemp(prefix='properties-task-protocol-', dir=ROOT / '.tools'))
    before = request.t.syntax_validation.implementation_fingerprint()
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    records = []
    try:
        for name, source in SOURCES.items():
            directory = out / name
            directory.mkdir()
            fixture, path = checked_source(source, directory, frontend, adapter)
            initial = '$php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
            checks = [
                'S_initial = ' + initial,
                'S_prep = $property_seek_prep(S_initial[.COMPLETION = NORMAL], 1024)[.COMPLETION = NORMAL]',
                'S_prep.TODO = (PROPERTY_PREP phpType20 z) :: ptask_prep*',
                'S_prep.ORIGIN = (porigin)',
                'S_prep.RESULT = KNOWN (POBJECT n_object)',
                '$call_descriptors_valid(S_prep)',
                '$call_tasks_valid(S_prep, S_prep.TODO)',
                '~$call_task_valid(S_prep, PROPERTY_PREP phpType20 $(z + 1))',
                '~$call_task_valid(S_prep[.ORIGIN = eps], PROPERTY_PREP phpType20 z)',
                '$heap_valid($heap_graph(S_prep))',
                '$($heap_owners($heap_graph(S_prep), HOBJECT n_object) > 0)',
            ]
            if name == 'static':
                checks += [
                    'phpType20 = NIdentifier (BYTES "eA==") metadata_name',
                    '~$call_task_valid(S_prep, PROPERTY_PREP (NIdentifier (BYTES "YmFk") metadata_name) z)',
                    'S_done = $drive(S_prep, 1024)',
                    'S_done.COMPLETION = NORMAL',
                    '$property_outputs(S_done.EVENTS) = [49]',
                    '$heap_valid($heap_graph(S_done))',
                    '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
                ]
            elif name == 'computed':
                checks += [
                    'S_name = $property_seek_name(S_prep, 1024)[.COMPLETION = NORMAL]',
                    'S_name.TODO = (PROPERTY_NAME (POBJECT n_object) z_name) :: ptask_name*',
                    '$call_descriptors_valid(S_name)',
                    '$call_tasks_valid(S_name, S_name.TODO)',
                    '~$call_task_valid(S_name, PROPERTY_NAME (POBJECT n_object) $(z_name + 1))',
                    '~$call_task_valid(S_name[.ORIGIN = eps], PROPERTY_NAME (POBJECT n_object) z_name)',
                    '$heap_valid($heap_graph(S_name))',
                    '$($heap_owners($heap_graph(S_name), HOBJECT n_object) > 0)',
                    '$property_outputs(S_name.EVENTS) = [78]',
                    'S_done = $drive(S_name, 1024)',
                    'S_done.COMPLETION = NORMAL',
                    '$property_outputs(S_done.EVENTS) = [78,49]',
                    '$heap_valid($heap_graph(S_done))',
                    '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
                ]
            else:
                checks += [
                    'S_done = $drive(S_prep, 1024)',
                    'S_done.COMPLETION = THROWN text_error nat_error* z_error',
                    '$heap_valid($heap_graph(S_done))',
                    '$heap_owners($heap_graph(S_done), HOBJECT n_object) = 0',
                ]
            script = out / (name + '.watsup')
            script.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                              ''.join('  -- if ' + check + '\n' for check in checks))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(script)], capture_output=True, text=True, timeout=180)
            (out / (name + '.stdout')).write_text(result.stdout)
            (out / (name + '.stderr')).write_text(result.stderr)
            (out / (name + '.status.json')).write_text(json.dumps({'exit_status': result.returncode}) + '\n')
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name, result.stderr[:2500])
            records.append({'case': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'assertions': len(checks)})
    finally:
        frontend.close()
        adapter.close()
    assert before == request.t.syntax_validation.implementation_fingerprint()
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'fingerprint': before,
                                                 'records': records}, indent=2) + '\n')
    print('PASS property tasks:', sum(row['assertions'] for row in records), out)


if __name__ == '__main__':
    main()
