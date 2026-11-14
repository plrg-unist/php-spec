"""Ground nullable FQN stdClass headers with actual object/NULL private-cell ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_object_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_nullable_fqn_stdclass_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice76', 'ReviewNotice78')


def class_type(name):
    return '[(PTBRANCH ([PTCLASS ($ptascii("' + name + '"))]))]'


def nullable(name):
    return class_type(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'


def normal(initial, case, index, front):
    original, old_derived = prior.normal(initial, case, index, front)
    reached = []
    for line in original:
        if line.startswith('$ptlc($base64(text_return_null))'):
            continue
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + nullable('sTdClAsS')
        elif line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + nullable('stdClass')
        elif line.startswith('phpType17 = '):
            if index == 0:
                line = line.replace('(NIdentifier (BYTES text_formal) metadata_formal)',
                    '(NNullableType (NNameFullyQualified (BYTES text_formal) metadata_formal) metadata_formalnullable)')
            else:
                line = line.replace('NIdentifier (BYTES text_formal)', 'NNameFullyQualified (BYTES text_formal)')
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = NNullableType (NNameFullyQualified (BYTES text_return) metadata_return) metadata_nullable'
        elif line.startswith('$ptlc($base64(text_'):
            line = line.replace('$ptascii("object")', '$ptascii("stdclass")')
        reached.append(line)
    reached += ['$base64(text_formal) = $ptascii("sTdClAsS")', '$base64(text_return) = $ptascii("stdClass")']
    if front:
        return reached, []
    derived = [line for line in old_derived if line.startswith(('~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_'))]
    proof = '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    if index == 0:
        for formal in (True, False):
            name = 'sTdClAsS' if formal else 'stdClass'
            atom = class_type(name)[1:-1]
            wrong = (('eps',) if formal else ()) + (class_type(name), nullable('stdClass' if formal else 'sTdClAsS'),
                nullable('Other'), prior.branches(['object', 'null']),
                '[(PTBRANCH ([PTBUILTIN "null"])), ' + atom + ']',
                nullable(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
                nullable(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]')
            for normalized in wrong:
                derived += ['~' + (proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]]') if formal else
                    header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])'))]
        for syntax in ('NName (BYTES text_return) metadata_return', 'NIdentifier (BYTES text_return) metadata_return',
                'NNameRelative (BYTES text_return) metadata_return',
                'NNameFullyQualified (BYTES "T3RoZXI=") metadata_return'):
            derived += ['~' + header.replace('phpType18,', 'NNullableType (' + syntax + ') metadata_nullable,')]
        raw_name = 'NNameFullyQualified (BYTES text_return) metadata_return'
        raw_union = 'NUnionType (SEQUENCE ([' + raw_name + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return'
        derived += ['~' + header.replace('phpType18,', raw_name + ','), '~' + header.replace('phpType18,', raw_union + ',')]
        for syntax in ('NName (BYTES text_formal) metadata_formal', 'NIdentifier (BYTES text_formal) metadata_formal',
                'NNameRelative (BYTES text_formal) metadata_formal', 'NNameFullyQualified (BYTES "T3RoZXI=") metadata_formal'):
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (' + syntax + ') metadata_nullable) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            derived += ['~' + proof.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + parameter + ']),')]
        for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable stdClass default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        derived += ['~' + proof.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),'),
            '~$named_reference_notice_object(S_pre[.NATIVEEXCESS = S_pre.NATIVEEXCESS ++ [HOBJECT n_old]], pvalue_input)']
    for strict in ('false', 'true'):
        accepted = ('PNULL', 'POBJECT n_old') if index == 0 else ('PNULL',)
        for value in accepted:
            derived += ['$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
        for value in ('PBOOL false', 'PINT 0', 'PSTRING ($ptascii("17"))', 'PFLOAT 0'):
            derived += ['$typed_conversion_at(S_receive, psparam.TYPE, ' + value + ', ' + strict + ') = TYPEREJECT']
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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:2]):
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n  -- if $scfr_case1()\n')
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:2]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-nullable-fqn-stdclass-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
