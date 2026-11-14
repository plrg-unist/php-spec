"""Ground larger primitive literal unions and weak scalar selection."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_nonnull_literal_bool_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_primitive_literal_bool_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice74', 'ReviewNotice75')


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in members) + ']'


def raw_members(members, stem):
    atoms, guards = [], []
    for index, kind in enumerate(members):
        name = stem + str(index)
        atoms += ['NIdentifier (BYTES text_' + name + ') metadata_' + name]
        guards += ['$ptlc($base64(text_' + name + ')) = $ptascii("' + kind + '")']
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_union_' + stem, guards


def raw_constants(members):
    atoms = ['NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_return0' for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_union_return'


def normal(initial, case, front):
    reached, _ = prior.normal(initial, case, front)
    result = []
    for line in reached:
        if any(line.startswith('$ptlc($base64(' + name + '))') for name in
                ('text_type', 'text_partner_parameter', 'text_return', 'text_partner_return')):
            continue
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + branches(case['formal_members'])
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + branches(case['return_members'])
        if line.startswith('$typed_parameter_conversion('):
            line = '$typed_parameter_conversion(S_receive, psparam, (' + case['original_value'] + ')) = ' + case['receive_conversion']
        if line.startswith('phpType17 = '):
            raw, guards = raw_members(case['formal_members'], 'formal')
            result += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN ' + ('true' if case['formal_byref'] else 'false') + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'] + guards
        elif line.startswith('phpType18 = '):
            raw, guards = raw_members(case['return_members'], 'return')
            result += ['phpType18 = ' + raw] + guards
        else:
            result.append(line)
    derived = []
    if not front:
        arguments = 'SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), '
        header = '$reference_notice_producer_header(' + arguments + 'phpType18, pfunction_producer.SIGNATURE)'
        proof = '$reference_notice_producer_arguments(' + arguments + 'pfunction_producer.SIGNATURE[.RETURNS = eps])'
        for members, formal in ((case['return_members'], False), (case['formal_members'], True)):
            for malformed in (members[::-1], members[:-1], members + [members[0]]):
                normalized = branches(malformed)
                derived += ['~' + (proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]]') if formal else
                    header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])'))]
        byref = 'true' if case['formal_byref'] else 'false'
        vectors = [(['false', 'array', 'int'], True), (['float', 'string', 'true'], True),
            (['array', 'int', 'float', 'string', 'null', 'false'], True),
            (['true', 'null', 'string', 'float', 'int', 'array'], True),
            (['array', 'int', 'float', 'string', 'null', 'bool'], True),
            (['false', 'false', 'int'], False), (['bool', 'false', 'int'], False),
            (['true', 'false', 'array'], False),
            (['array', 'int', 'float', 'string', 'null', 'false', 'true'], False),
            (['object', 'false', 'int'], True), (['mixed', 'false', 'int'], False)]
        for members, accepted in vectors:
            raw, normalized = raw_constants(members), branches(members)
            mark = '' if accepted else '~'
            derived += [mark + header.replace('phpType18,', raw + ',').replace(
                'pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
            param = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN ' + byref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            derived += [mark + '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([' + param + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        for update in ('.BYREF = ' + ('false' if case['formal_byref'] else 'true'), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged primitive union default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        derived += ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
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
        if any(line.startswith('$ptlc($base64(' + name + '))') for name in ('text_type', 'text_partner_parameter')):
            continue
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + branches(case['formal_members'])
        if line.startswith('phpType17 = '):
            raw, guards = raw_members(case['formal_members'], 'formal')
            result += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'] + guards
        else:
            result.append(line)
    return result, derived


def return_priority(initial, case):
    reached, derived = prior.return_priority(initial, case)
    result = []
    for line in reached:
        if any(line.startswith('$ptlc($base64(' + name + '))') for name in ('text_return', 'text_partner_return')):
            continue
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + branches(case['return_members'])
        if line.startswith('phpType18 = '):
            raw, guards = raw_members(case['return_members'], 'return')
            result += ['phpType18 = ' + raw] + guards
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
    paths = [Path(__file__), CATALOGUE, provenance] + [ROOT / "tests/semantics" / name for name in ['cv_nonnull_literal_bool_producer_reference_notice_review_state.py', 'cv_union_null_literal_bool_producer_reference_notice_review_state.py', 'cv_nullable_literal_bool_producer_reference_notice_review_state.py', 'cv_literal_bool_return_producer_reference_notice_review_state.py', 'cv_literal_bool_formal_producer_reference_notice_review_state.py', 'cv_null_return_producer_reference_notice_review_state.py', 'cv_null_formal_producer_reference_notice_review_state.py', 'singleton_cv_typed_formal_producer_reference_notice_review_state.py', 'singleton_cv_nullable_scalar_return_producer_reference_notice_review_state.py']]
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
    print('cv-primitive-literal-bool-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
