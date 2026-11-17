#!/usr/bin/env python3
"""Ground global plain stdClass return context, priority and private Notice ownership."""
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
CATALOGUE = Path(__file__).with_name('global_plain_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace(r'[$ptascii("ReviewNotice77\\ObjectNamed\\make"), $ptascii("ReviewNotice77\\NullNamed\\make")]', '[$ptascii("make")]')
assert 'ReviewNotice77' not in PREFIX


def normal(initial, case, index, front):
    original, old_derived = prior.normal(initial, case, index, front)
    reached = []
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    for line in original:
        if line.startswith('phpType18 = '):
            line = 'phpType18 = NName (BYTES text_return) metadata_return'
        if line.lstrip('~').startswith('$reference_notice_producer_arguments('):
            line = line.lstrip('~')
        if line.lstrip('~') == header:
            reached.append('~' + header)
            if not front:
                reached.append(scoped)
            continue
        reached.append(line)
        if line == '~pfunction_producer.SIGNATURE.BYREF':
            reached += [r'pfunction_producer.ENV.NAMESPACE = eps /\ pfunction_producer.ENV.CLASSES = eps']
    if front:
        return reached, []
    derived = [line for line in old_derived if not line.startswith('~$reference_notice_producer_header(')]
    def proof(env='pfunction_producer.ENV', raw='phpType18', returns=None):
        signature = 'pfunction_producer.SIGNATURE' + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + env + ', SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), ' + raw + ', ' + signature + ')'
    imported = '[($ptascii("stdclass"), $ptascii("stdClass"))]'
    contexts = ['pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")]',
        'pfunction_producer.ENV[.CLASSES = ' + imported + ']',
        'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")][.CLASSES = ' + imported + ']']
    for env in contexts:
        derived.append('~' + proof(env=env))
        derived.append(proof(env=env, raw='NNameFullyQualified (BYTES text_return) metadata_return'))
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()) + ') metadata_return'
        derived.append(proof(raw=raw, returns=prior.class_type(spelling)))
    for returns in ('eps', prior.class_type('sTdClAsS'), prior.class_type('Other'),
            prior.prior.branches(['object']), prior.class_type('stdClass')[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        derived.append(('' if returns == 'eps' else '~') + proof(returns=returns))
    for raw in ('NNameRelative (BYTES text_return) metadata_return', 'NIdentifier (BYTES text_return) metadata_return',
            'NName (BYTES "T3RoZXI=") metadata_return',
            'NNullableType (NName (BYTES text_return) metadata_return) metadata_return',
            'NUnionType (SEQUENCE ([NName (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return'):
        derived.append('~' + proof(raw=raw))
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    derived.append('~' + scoped.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + parameter.replace('NNameFullyQualified', 'NName') + ']),'))
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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
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
            for control_index, control in enumerate([] if args.front else case.get('scope_controls', [])):
                source_control = out / ('scope-control-' + str(control_index) + '.php')
                source_control.write_bytes(control['source'].encode())
                assert sha(source_control) == control['source_sha256'] and control['source_agreements'] == 0
                parsed_control = frontend.request({'op': 'parse', 'source': base64.b64encode(source_control.read_bytes()).decode()})
                assert parsed_control['accepted']
                checked_control = adapter.request({'op': 'check', 'ast': parsed_control['ast'], 'fixture': True})
                assert checked_control['ok'] and checked_control['fixture']
                suffix = str(control_index)
                state, function = 'S_scope' + suffix, 'pfunction_scope' + suffix
                argument, result = 'phpType17_scope' + suffix, 'phpType18_scope' + suffix
                name, body, metadata = 'phpType11_scope' + suffix, 'phpType23_scope' + suffix, 'metadata_scope' + suffix
                text, metadata_return = 'text_scope_return' + suffix, 'metadata_scope_return' + suffix
                current_derived += [state + ' = $php_run(' + checked_control['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source_control)).decode()) + ')',
                    state + '.COMPLETION = BUDGET', state + '.FUNCTIONS = [' + function + ']',
                    function + '.ENV.NAMESPACE = $ptascii(' + json.dumps(control['namespace']) + ')',
                    function + '.ENV.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]',
                    function + '.SIGNATURE.RETURNS = ' + prior.class_type('stdClass'),
                    '$origin_node(' + state + '.SOURCES, ' + function + '.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) ' + name + ' (SEQUENCE ([' + argument + '])) ' + result + ' ' + body + ' ' + metadata + ')',
                    result + ' = NName (BYTES ' + text + ') ' + metadata_return,
                    '$base64(' + text + ') = $ptascii("stdClass")',
                    '~$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([' + argument + ']), ' + result + ', ' + function + '.SIGNATURE)']
                if not args.front:
                    tail = ', SEQUENCE ([phpType7]), SEQUENCE ([' + argument + ']), ' + result + ', ' + function + '.SIGNATURE)'
                    current_derived += ['~$reference_notice_producer_scoped_header(' + function + '.ENV' + tail,
                        '$reference_notice_producer_scoped_header(' + function + '.ENV[.NAMESPACE = eps][.CLASSES = eps]' + tail]
                paths.append(source_control)
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
    print('global-plain-stdclass-return-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
