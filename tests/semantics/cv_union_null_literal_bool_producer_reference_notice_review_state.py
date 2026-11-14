"""Ground ordered literal-Boolean/null unions and separate error priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_nullable_literal_bool_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_null_literal_bool_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice72', 'ReviewNotice73')


def union(kind, null_first):
    members = ['null', kind] if null_first else [kind, 'null']
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + member + '"]))' for member in members) + ']'


def raw_union(literal, nil, null_first, metadata):
    members = [nil, literal] if null_first else [literal, nil]
    return 'NUnionType (SEQUENCE ([' + ', '.join(members) + '])) ' + metadata


def normal(initial, case, front):
    reached, _ = prior.normal(initial, case, front)
    kind = case['return_kind']
    parameter = raw_union('NIdentifier (BYTES text_type) metadata_type',
        'NIdentifier (BYTES text_null_parameter) metadata_null_parameter',
        case['formal_null_first'], 'metadata_union_parameter')
    returns = raw_union('NIdentifier (BYTES text_return) metadata_return',
        'NIdentifier (BYTES text_null_return) metadata_null_return',
        case['return_null_first'], 'metadata_union_return')
    result = []
    for line in reached:
        if line.startswith('psparam.TYPE = '):
            line = line.replace(prior.nullable(kind), union(kind, case['formal_null_first']))
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = line.replace(prior.nullable(kind), union(kind, case['return_null_first']))
        if line.startswith('phpType17 = '):
            old = 'NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable'
            assert line.count(old) == 1
            result += [line.replace(old, parameter), '$ptlc($base64(text_null_parameter)) = $ptascii("null")']
        elif line.startswith('phpType18 = '):
            result += ['phpType18 = ' + returns, '$ptlc($base64(text_null_return)) = $ptascii("null")']
        else:
            result.append(line)
    derived = []
    if not front:
        arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
        header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
        proof = '$reference_notice_producer_arguments(' + arguments + 'pfunction_producer.SIGNATURE[.RETURNS = eps])'
        for null_first, template, suffix in ((case['return_null_first'], header, 'return'),
                (case['formal_null_first'], proof, 'formal')):
            malformed = [union('true' if kind == 'false' else 'false', null_first),
                '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))]', union(kind, not null_first),
                union(kind, null_first)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]']
            for normalized in malformed:
                if suffix == 'return':
                    derived += ['~' + template.replace('pfunction_producer.SIGNATURE)',
                        'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
                else:
                    derived += ['~' + template.replace('.RETURNS = eps]',
                        '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]]')]
        derived += ['~' + header.replace('phpType18,', 'NIdentifier (BYTES text_return) metadata_return,'),
            '~' + header.replace('phpType18,', 'NName (BYTES text_return) metadata_return,'),
            '~' + header.replace('pfunction_producer.SIGNATURE)',
                'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
            '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
        for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false',
                '.DEFAULT = PSDEFAULTUNSUPPORTED "forged union default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]',
                '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        for other in ('int', 'true' if kind == 'false' else 'false'):
            wider = raw_union('NIdentifier (BYTES text_return) metadata_return',
                'NIdentifier (BYTES "' + base64.b64encode(other.encode()).decode() + '") metadata_return',
                False, 'metadata_union_return')
            normalized = '[(PTBRANCH ([PTBUILTIN "' + kind + '"])), (PTBRANCH ([PTBUILTIN "' + other + '"]))]'
            derived += [('' if other == 'int' else '~') + header.replace('phpType18,', wider + ',').replace(
                'pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
            raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + wider + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            derived += [('' if other == 'int' else '~') + '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + raw_parameter + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        wider = 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return, NIdentifier (BYTES "aW50") metadata_return])) metadata_union_return'
        normalized = union(kind, False)[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'
        derived += [header.replace('phpType18,', wider + ',').replace(
            'pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
        raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + wider + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        derived += ['$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + raw_parameter + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        for literal_kind in ('false', 'true'):
            for null_first in (False, True):
                for strict in ('false', 'true'):
                    for accepted in ('PNULL', 'PBOOL ' + literal_kind):
                        derived += ['$typed_conversion_at(S_return, ' + union(literal_kind, null_first) + ', ' + accepted + ', ' + strict + ') = TYPEVALUE (' + accepted + ')']
                    for rejected in ('PBOOL ' + ('true' if literal_kind == 'false' else 'false'), 'PINT 0', 'PINT 1', 'PSTRING eps', 'PFLOAT 0'):
                        derived += ['$typed_conversion_at(S_return, ' + union(literal_kind, null_first) + ', ' + rejected + ', ' + strict + ') = TYPEREJECT']
        for name in ('receive', 'return', 'notice'):
            stage = 'S_' + name
            derived += ['S_zero_' + name + ' = $drive(' + stage + ', 0)',
                'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + stage,
                '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + stage + ', 2)']
    return result, derived


def receive_priority(initial, case):
    reached, derived = prior.receive_priority(initial, case)
    result = []
    for line in reached:
        if line.startswith('psparam.TYPE = '):
            line = line.replace(prior.nullable('false'), union('false', case['formal_null_first']))
        if line.startswith('phpType17 = '):
            raw = raw_union('NIdentifier (BYTES text_type) metadata_type',
                'NIdentifier (BYTES text_null_parameter) metadata_null_parameter',
                case['formal_null_first'], 'metadata_union_parameter')
            old = 'NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable'
            assert line.count(old) == 1
            result += [line.replace(old, raw), '$ptlc($base64(text_null_parameter)) = $ptascii("null")']
        else:
            result.append(line)
    return result, derived


def return_priority(initial, case):
    reached, derived = prior.return_priority(initial, case)
    result = []
    for line in reached:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = line.replace(prior.nullable('true'), union('true', case['return_null_first']))
        if line.startswith('phpType18 = '):
            raw = raw_union('NIdentifier (BYTES text_return) metadata_return',
                'NIdentifier (BYTES text_null_return) metadata_null_return',
                case['return_null_first'], 'metadata_union_return')
            result += ['phpType18 = ' + raw, '$ptlc($base64(text_null_return)) = $ptascii("null")']
        else:
            result.append(line)
    return result, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native = json.loads(provenance.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__), Path(prior.prior.prior.return_prior.__file__), Path(prior.formal_prior.__file__), Path(prior.formal_prior.prior.__file__)]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
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
            conditions, current_derived = normal(initial, case, args.front) if index < 2 else (receive_priority(initial, case) if index == 2 else return_priority(initial, case))
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scfr_case' + str(i) + '()\n' for i in range(4)))
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-union-null-literal-bool-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
