"""Ground FQN class/builtin entry coercions, RETURN promotion and private ownership."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

import multi_cv_scalar_formal_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_fqn_stdclass_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('MultiCvScalarFormalString57', 'ReviewFqnBuiltinString80').replace('MultiCvScalarFormal57', 'ReviewFqnBuiltin80')


def ordered(kind, class_first, name='sTdClAsS'):
    atoms = ['(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))', '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))']
    return '[' + ', '.join(atoms if class_first else atoms[::-1]) + ']'


def raw_union(kind_text, field, class_first, class_tag='NNameFullyQualified', builtin_tag='NIdentifier', class_text=None):
    atoms = [class_tag + ' (BYTES ' + (class_text or 'text_' + field + '_class') + ') metadata_' + field + '_class',
        builtin_tag + ' (BYTES ' + kind_text + ') metadata_' + field + '_type']
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms if class_first else atoms[::-1]) + '])) metadata_' + field + '_union'


def normal(initial, case, index, front):
    reached = [initial] + prior.front_lines(index, case)
    for field, kind, first in zip(('first', 'last'), case['formal_kinds'], case['formal_class_first']):
        old = '(NIdentifier (BYTES text_' + field + '_type) metadata_' + field + '_type)'
        raw = raw_union('text_' + field + '_type', field, first)
        reached = [line.replace(old, '(' + raw + ')') if line.startswith('phpType17_' + field + ' = NParam') else line for line in reached]
        reached = ['psparam_' + field + '.TYPE = ' + ordered(kind, first) if line.startswith('psparam_' + field + '.TYPE =') else line for line in reached]
        reached += ['$base64(text_' + field + '_class) = $ptascii("sTdClAsS")']
    returns = ordered(case['return_kind'], case['return_class_first'], 'stdClass')
    reached = ['pfunction_producer.SIGNATURE.RETURNS = ' + returns + r' /\ ~pfunction_producer.SIGNATURE.BYREF' if line.startswith('pfunction_producer.SIGNATURE.RETURNS =') else line for line in reached]
    reached = ['phpType18_return = ' + raw_union('text_return', 'return', case['return_class_first']) if line.startswith('phpType18_return =') else line for line in reached]
    reached = [line.replace('$ptascii("int")', '$ptascii(' + json.dumps(case['return_kind']) + ')') if line.startswith('$ptlc($base64(text_return)) =') else line for line in reached]
    reached += ['$base64(text_return_class) = $ptascii("stdClass")', '~pfunction_producer.CODE.STRICT']
    if index == 1:
        reached = [line.replace('(PINT 37)', '(PFLOAT 4630404104378646528)') if line.startswith(('S_checked.COMPLETION =', 'S_after_return.TODO =', 'S_pre.RESULT =')) else line for line in reached]
        reached += ['S_return.RESULT = KNOWN (PINT 37)', '$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 37, false) = TYPEVALUE (PFLOAT 4630404104378646528)']
    if front:
        return reached, []
    reached = [line.removeprefix('~') if line.startswith(('~$reference_notice_producer_header(', '~$reference_notice_producer_arguments(')) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in reached]
    full = prior.full_lines(index, case)
    if index == 1:
        full = [line.replace('(PINT 37)', '(PFLOAT 4630404104378646528)') if line.startswith(('S_notice.STORE[n_private]', 'S_resume.STORE[n_private]')) else line for line in full]
    reached += full
    derived = [line for line in prior.controls(index) if not line.startswith('phpType17_nullable =') and 'phpType17_nullable,' not in line]
    proof = '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), pfunction_producer.SIGNATURE[.RETURNS = eps]'
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    for first in (False, True):
        for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true'):
            encoded = '"' + base64.b64encode(kind.upper().encode()).decode() + '"'
            class_text = '"' + base64.b64encode(b'sTdClAsS').decode() + '"'
            raw = raw_union(encoded, 'first', first, class_text=class_text)
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
            normalized = ordered(kind, first)
            derived += [proof.replace('phpType17_first,', parameter + ',') + '[.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])',
                header + raw + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
            for bad in (ordered(kind, not first), ordered(kind, first, 'STDCLASS'),
                    normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
                derived += ['~' + header + raw + ', pfunction_producer.SIGNATURE[.RETURNS = ' + bad + '])']
            for tag in ('NName', 'NNameRelative', 'NIdentifier'):
                derived += ['~' + header + raw_union(encoded, 'first', first, class_tag=tag, class_text=class_text) + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
        for kind in ('object', 'mixed', 'void', 'never', 'callable', 'iterable'):
            encoded = '"' + base64.b64encode(kind.encode()).decode() + '"'
            raw = raw_union(encoded, 'first', first, class_text='"c1RkQ2xBc1M="')
            derived += [('' if kind in ('callable', 'iterable') else '~') + header + raw + ', pfunction_producer.SIGNATURE[.RETURNS = ' + ordered(kind, first) + '])']
        for kind, value in (('false', 'PINT 0'), ('true', 'PBOOL false'), ('array', 'PINT 1'), ('null', 'PINT 0')):
            for strict in ('false', 'true'):
                derived += ['$typed_conversion_at(S_return, ' + ordered(kind, first) + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        for kind, value, conversion in (('bool', 'PINT 1', 'TYPEBOOL (PINT 1)'), ('string', 'PINT 37', 'TYPESTRING (PINT 37)'),
                ('int', 'pvalue_original' if index == 0 else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("17"))', 'TYPEINTEGER ' + ('pvalue_original' if index == 0 else '(PSTRING_CARRIER INTERNED_STRING ($ptascii("17")))'))):
            derived += ['$typed_conversion_at(S_return, ' + ordered(kind, first) + ', ' + value + ', false) = ' + conversion,
                '$typed_conversion_at(S_return, ' + ordered(kind, first) + ', ' + value + ', true) = TYPEREJECT']
        for strict in ('false', 'true'):
            derived += ['$typed_conversion_at(S_return, ' + ordered('float', first) + ', PINT 37, ' + strict + ') = TYPEVALUE (PFLOAT 4630404104378646528)']
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
    print('cv-builtin-fqn-stdclass-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
