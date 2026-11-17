#!/usr/bin/env python3
"""Ground bare global class FORMAL reception and separate private Notice ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_fqn_stdclass_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_stdclass_formal_producer_reference_notice_review_cases.json')
PREFIX = '\n'.join('  -- if pcallcontext.NAME = $ptascii("make")' if line.startswith('  -- if pcallcontext.NAME <- ') else line for line in prior.PREFIX.splitlines()) + '\n'


def normal(initial, case, index, front):
    assert index == 0
    old, old_derived = prior.normal(initial, case, 0, front)
    reached = []
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    for line in old:
        if line.startswith('phpType17 = '):
            line = line.replace('NNameFullyQualified', 'NName', 1)
        bare = line.removeprefix('~')
        if bare.startswith(('$reference_notice_producer_arguments(', '$reference_notice_producer_header(')):
            line = '~' + bare
        if bare == '$named_reference_notice_pending(S_pre)':
            reached += [r'pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = eps', ('~' if front else '') + scoped]
        reached.append(line)
    if front:
        return reached, []
    derived = [line for line in old_derived if line.startswith(('~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object(', '$typed_conversion_at('))]
    derived += ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
        scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1)]
    for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged bare class formal default"'):
        derived.append('~' + scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[' + update + ']]])'))
    for normalized in ('eps', prior.prior.branches(['object']), prior.class_type('stdClass'), prior.class_type('Other')):
        derived.append('~' + scoped.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])'))
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    def raw_proof(value):
        return scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + value + ']),', 1)
    for tag in ('NNameRelative', 'NIdentifier'):
        derived.append('~' + raw_proof(parameter.replace('NName (BYTES text_formal)', tag + ' (BYTES text_formal)', 1)))
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass'):
        value = parameter.replace('NName (BYTES text_formal)', 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ')', 1)
        derived.append('~' + raw_proof(value))
    derived += ['~' + raw_proof(parameter.replace('(INTEGER 0)', '(INTEGER 1)', 1)),
        '~' + raw_proof(parameter.replace('(BOOLEAN true) (BOOLEAN false)', '(BOOLEAN true) (BOOLEAN true)', 1)),
        '~' + raw_proof(parameter.replace('phpType10 ABSENT', 'phpType10 (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps)', 1)),
        '~' + raw_proof(parameter.replace('(NName (BYTES text_formal) metadata_formal)', '(NNullableType (NName (BYTES text_formal) metadata_formal) eps)', 1))]
    return reached, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:1]):
            row = rows[case['id']]
            source = Path(row['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            conditions, current_derived = normal(initial, case, index, args.front)
            case_specs.append('dec $scfr_case' + str(index) + '() : bool\ndef $scfr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
            reached += conditions
            derived += current_derived
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:1]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-stdclass-formal-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
