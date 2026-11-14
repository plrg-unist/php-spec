"""Ground ordered FQN stdClass/null headers with actual object/NULL private-cell ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_nullable_fqn_stdclass_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_fqn_stdclass_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice78', 'ReviewNotice79')


def ordered(name, class_first):
    atoms = [prior.class_type(name)[1:-1], '(PTBRANCH ([PTBUILTIN "null"]))']
    return '[' + ', '.join(atoms if class_first else atoms[::-1]) + ']'


def raw_union(field, class_first, class_tag='NNameFullyQualified', null_tag='NIdentifier', null_text=None):
    atoms = [class_tag + ' (BYTES text_' + field + ') metadata_' + field,
        null_tag + ' (BYTES ' + (null_text or 'text_' + field + '_null') + ') metadata_' + field + '_null']
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms if class_first else atoms[::-1]) + '])) metadata_' + field + '_union'


def normal(initial, case, index, front):
    original, compatible = prior.normal(initial, case, index, front)
    formal_first, return_first = index == 1, index == 0
    byref = 'true' if index == 0 else 'false'
    reached = []
    for line in original:
        if line.startswith('psparam.TYPE = '):
            line = 'psparam.TYPE = ' + ordered('sTdClAsS', formal_first)
        elif line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + ordered('stdClass', return_first)
        elif line.startswith('phpType17 = '):
            line = 'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union('formal', formal_first) + ') (BOOLEAN ' + byref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        elif line.startswith('phpType18 = '):
            line = 'phpType18 = ' + raw_union('return', return_first)
        reached.append(line)
    reached += ['$ptlc($base64(text_formal_null)) = $ptascii("null")', '$ptlc($base64(text_return_null)) = $ptascii("null")']
    if front:
        return reached, []
    derived = [line for line in compatible if line.startswith(('~$error_call_valid(', 'S_zero_', '$drive($drive(S_zero_',
        '$typed_conversion_at(', '~$named_reference_notice_object('))]
    proof = '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    if index == 0:
        # Exercise the exact current78 union control on this fresh class-first return.
        changed = [line for line in compatible if line.lstrip('~').startswith('$reference_notice_producer_header(') and 'NUnionType' in line]
        assert len(changed) == 1
        derived += [changed[0].removeprefix('~')]
        for formal, first in ((True, formal_first), (False, return_first)):
            name = 'sTdClAsS' if formal else 'stdClass'
            field = 'formal' if formal else 'return'
            normalized = ordered(name, first)
            wrong = (('eps',) if formal else ()) + (prior.class_type(name), ordered(name, not first),
                ordered('stdClass' if formal else 'sTdClAsS', first), ordered('Other', first),
                prior.prior.branches(['object', 'null'] if first else ['null', 'object']),
                normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
                normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]')
            for bad in wrong:
                derived += ['~' + (proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + bad + ']]]') if formal else
                    header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + bad + '])'))]
            for syntax in [raw_union(field, first, tag) for tag in ('NName', 'NIdentifier', 'NNameRelative')] + [
                    raw_union(field, first, null_tag='NName'), raw_union(field, first, null_text='"ZmFsc2U="')]:
                if formal:
                    parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + syntax + ') (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
                    derived += ['~' + proof.replace('SEQUENCE ([phpType17]),', 'SEQUENCE ([' + parameter + ']),')]
                else:
                    derived += ['~' + header.replace('phpType18,', syntax + ',')]
        for update in ('.BYREF = false', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged ordered stdClass default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        derived += ['~' + proof.replace('SEQUENCE ([phpType7]),', 'SEQUENCE ([phpType7, phpType7]),')]
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
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
    print('cv-union-fqn-stdclass-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
