#!/usr/bin/env python3
"""Ground Param-first normalization of ordinary FORMAL and singleton RETURN aliases."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import scoped_stdclass_formal_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_stdclass_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('PeerScopedFormal124', 'PeerScopedReturn127')


def normal(initial, case, front):
    original, inherited = prior.normal(initial, case, 0, front)
    reached = []
    for line in original:
        if line.startswith('phpType18 = '):
            line = 'phpType18 = NName (BYTES text_return) metadata_return'
        elif line.startswith('$base64(text_return) = '):
            line = '$base64(text_return) = $ptascii(' + json.dumps(case['return_alias']) + ')'
        elif line.startswith('$ptlc($base64(text_return)) = '):
            line = '$ptlc($base64(text_return)) = $ptascii(' + json.dumps(case['return_alias'].lower()) + ')'
        reached.append(line)
    env = 'pfunction_producer.ENV'
    canonical = prior.prior.prior.class_type('stdClass')
    context = '$pltypecontext(' + env + ', PTGLOBAL, PTRETURN, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 })'
    reached += ['$ptvalidname($base64(text_return), true)',
        '$ptsingle(' + context + ', PTPLAIN, $base64(text_return)) = PTOK (' + canonical + ') eps']
    if front:
        return reached, []
    derived = [line for line in inherited if line.startswith(('~$error_call_valid(', '~$typed_return_task_valid(', 'S_zero_', '$drive($drive(S_zero_', '~$named_reference_notice_object(', '$typed_conversion_at('))]
    parameter = next(line.removeprefix('phpType17 = ') for line in reached if line.startswith('phpType17 = '))
    viewed = parameter.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    fqn_return = 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_return'
    scoped = '$reference_notice_producer_scoped_header(' + env + ', SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    def proof(raw='phpType18', parameter_view='phpType17', context_env=env, returns=None):
        signature = 'pfunction_producer.SIGNATURE' + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context_env + ', SEQUENCE ([phpType7]), SEQUENCE ([' + parameter_view + ']), ' + raw + ', ' + signature + ')'
    helper = lambda raw: '$reference_notice_producer_scoped_parameter_view(' + env + ', ' + raw + ')'
    derived += [helper('phpType17') + ' = (' + viewed + ')', helper(viewed) + ' = (' + viewed + ')',
        proof(parameter_view=viewed), proof(raw=fqn_return), proof(raw=fqn_return, parameter_view=viewed),
        proof(returns='eps'), scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE eps,', 1),
        '~' + scoped.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),', 1),
        proof(context_env=env + '[.NAMESPACE = eps]'),
        proof(context_env=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~' + proof(context_env=env + '[.CLASSES = eps]')]
    for spelling in ('PeerBox', 'pEeRbOx', 'PEERBOX'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(spelling.encode()).decode()) + ') metadata_return'
        derived.append(proof(raw=raw))
    for tag in ('NNameFullyQualified', 'NNameRelative', 'NIdentifier'):
        derived.append('~' + proof(raw=tag + ' (BYTES text_return) metadata_return'))
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        derived.append('~' + proof(raw=raw))
    for name in ('int', 'mixed', 'self', 'array', 'callable'):
        raw = 'NName (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return'
        context_env = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        derived.append('~' + proof(raw=raw, parameter_view=viewed, context_env=context_env))
    for target in ('Other', 'STDCLASS', 'StDcLaSs'):
        context_env = env + '[.CLASSES = [($ptascii("peerbox"), $ptascii(' + json.dumps(target) + '))]]'
        derived.append('~' + proof(parameter_view=viewed, context_env=context_env))
    for returns in (prior.prior.prior.class_type('Other'), prior.prior.prior.class_type('STDCLASS'),
            prior.prior.prior.prior.branches(['object']), canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        derived.append('~' + proof(returns=returns))
    nullable = canonical[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'
    for raw in ('NNullableType (NName (BYTES text_return) metadata_return) metadata_return',
            'NUnionType (SEQUENCE ([NName (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return'):
        derived.append(('' if raw.startswith('NNullableType ') else '~') + proof(raw=raw, returns=nullable))
    derived += [proof(raw='NName (BYTES text_return) eps'),
        proof(parameter_view=parameter.replace('metadata_parameter', 'eps'))]
    for strict in ('true', 'false'):
        derived.append('$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PNULL, ' + strict + ') = TYPEREJECT')
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
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    for case in cases:
        row = rows[case['id']]
        source = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
        paths += [source, Path(row['stdout']), Path(row['stderr'])]
    source = Path(rows[cases[0]['id']]['command'][-1])
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached, derived = normal(initial, cases[0], args.front)
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + derived))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[cases[0]['id']], unchanged_return_controls=[cases[1]['id']], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('scoped-stdclass-return-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
