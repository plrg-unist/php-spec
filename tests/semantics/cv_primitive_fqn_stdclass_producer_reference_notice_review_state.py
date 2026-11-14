"""Ground ordered FQN stdClass triples, scalar choices and private Notice ownership."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

import cv_distinct_builtin_union_formal_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_primitive_fqn_stdclass_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('CvDistinctBuiltinUnionFormalString62', 'ReviewFqnPrimitiveString81').replace('CvDistinctBuiltinUnionFormal62', 'ReviewFqnPrimitive81')


def ordered(members, name='sTdClAsS'):
    return '[' + ', '.join('(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))' if kind == 'class' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw_union(members, field='first', primary=None, class_tag='NNameFullyQualified', name='sTdClAsS'):
    atoms = []
    for index, kind in enumerate(members):
        encoded = json.dumps(base64.b64encode((name if kind == 'class' else kind).encode()).decode())
        metadata = 'metadata_first_type'
        if primary is not None:
            if kind == 'class':
                encoded, metadata = 'text_' + field + '_class', 'metadata_' + field + '_class'
            elif kind == primary:
                encoded, metadata = ('text_return' if field == 'return' else 'text_' + field + '_type'), 'metadata_' + field + '_type'
            else:
                metadata = 'metadata_' + field + '_member_' + str(index)
        atoms.append((class_tag if kind == 'class' else 'NIdentifier') + ' (BYTES ' + encoded + ') ' + metadata)
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_' + field + '_union'


def controls():
    derived = [line for line in prior.prior.controls(0) if not line.startswith('phpType17_nullable =') and 'phpType17_nullable,' not in line]
    helper = '$reference_notice_producer_stdclass_union_members('
    arguments = '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE (['
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    signature = 'pfunction_producer.SIGNATURE[.RETURNS = eps]'
    def check(members, normalized=None, accepted=True, class_tag='NNameFullyQualified', name='sTdClAsS'):
        raw = raw_union(members, class_tag=class_tag, name=name)
        normalized = ordered(members) if normalized is None else normalized
        return ('' if accepted else '~') + helper + raw.split('SEQUENCE (', 1)[1].split(')) metadata_first_union', 1)[0] + ', ' + normalized + ', false, eps)'
    # Each primitive count, Boolean kind, class position and both source orders.
    for count in range(2, 7):
        for boolean in ('bool', 'false', 'true'):
            primitives = ['array', 'int', 'float', 'string', 'null'][:count - 1] + [boolean]
            for position in range(count + 1):
                for reverse in (False, True):
                    members = list(reversed(primitives)) if reverse else primitives[:]
                    members.insert(position, 'class')
                    derived.append(check(members))
            members = primitives[:]
            members.insert(count // 2, 'class')
            raw, normalized = raw_union(members), ordered(members)
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
            derived += [arguments + parameter + ', phpType17_last]), ' + signature + '[.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])',
                header + raw + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
    members = ['class', 'int', 'float']
    for normalized in (ordered(members[::-1]), ordered(members, 'STDCLASS'), ordered(members[:-1]), ordered(members + ['null'])):
        derived.append(check(members, normalized, False))
    for tag in ('NName', 'NNameRelative', 'NIdentifier'):
        derived.append(check(members, accepted=False, class_tag=tag))
    for name in ('Other', 'Vendor\\stdClass', 'stdClass\x00'):
        derived.append(check(members, accepted=False, name=name))
    for members in (['int', 'float'], ['class', 'class', 'int'], ['class', 'int', 'int'],
            ['class', 'bool', 'false'], ['class', 'true', 'false'], ['class', 'true', 'bool']):
        derived.append(check(members, accepted=False))
    for kind in ('object', 'mixed', 'void', 'never', 'callable', 'iterable', 'INTEGER'):
        members = ['class', 'int', kind]
        derived += [check(members, accepted=kind == 'callable'), ('' if kind == 'callable' else '~') + header + raw_union(members) + ', pfunction_producer.SIGNATURE[.RETURNS = ' + ordered(members) + '])']
    raw = raw_union(['class', 'float', 'int'])
    normalized = ordered(['class', 'float', 'int'])
    parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
    for patch in ('.REQUIRED = false', '.VARIADIC = true', '.BYREF = true', '.TYPE = ' + ordered(['int', 'float', 'class'])):
        derived += ['~' + arguments + parameter + ', phpType17_last]), ' + signature + '[.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '][' + patch + '], psparam_last]])']
    derived += ['$typed_conversion_at(S_return, ' + ordered(['float', 'int', 'class']) + ', PINT 17, false) = TYPEVALUE (PINT 17)',
        '$typed_conversion_at(S_return, ' + ordered(['class', 'int', 'string']) + ', pvalue_original, false) = TYPEVALUE pvalue_original',
        '$typed_conversion_at(S_return, ' + ordered(['class', 'int', 'float']) + ', pvalue_original, true) = TYPEREJECT']
    return derived


def normal(initial, case, index, front):
    reached = [initial] + prior.front_lines(0, case)
    for field, kind, members in zip(('first', 'last'), case['formal_kinds'], case['formal_members']):
        raw = raw_union(members, field, kind)
        reached = ['phpType17_' + field + ' = NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN ' + ('false' if field == 'first' else 'true') + ') (BOOLEAN false) phpType10_' + field + ' ABSENT (SEQUENCE eps) metadata_' + field + '_parameter' if line.startswith('phpType17_' + field + ' = NParam') else line for line in reached]
        reached = ['psparam_' + field + '.TYPE = ' + ordered(members) if line.startswith('psparam_' + field + '.TYPE =') else line for line in reached]
        reached += ['$base64(text_' + field + '_class) = $ptascii("sTdClAsS")']
    reached = ['pfunction_producer.SIGNATURE.RETURNS = ' + ordered(case['return_members'], 'stdClass') + r' /\ ~pfunction_producer.SIGNATURE.BYREF' if line.startswith('pfunction_producer.SIGNATURE.RETURNS =') else line for line in reached]
    reached = ['phpType18_return = ' + raw_union(case['return_members'], 'return', 'int') if line.startswith('phpType18_return =') else line for line in reached]
    reached += ['$base64(text_return_class) = $ptascii("stdClass")', '~pfunction_producer.CODE.STRICT', 'S_return.RESULT = KNOWN (PINT 17)']
    if index == 1:
        replacements = {'pvalue_saved = PINT 17': 'pvalue_saved = pvalue_original', '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEVALUE (PINT 17)': '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEVALUE pvalue_original'}
        reached = [replacements.get(line, line) for line in reached]
        reached += ['$string_carrier_valid(S_return, pvalue_saved)']
    if front:
        return reached, []
    reached = [line.removeprefix('~') if line.startswith(('~$reference_notice_producer_header(', '~$reference_notice_producer_arguments(')) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in reached]
    reached += prior.full_lines(0, case)
    return reached, controls()


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
    print('cv-primitive-fqn-stdclass-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
