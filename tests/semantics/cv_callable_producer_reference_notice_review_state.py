"""Ground registered callable strings, ordinary typed BYREF writes and private cells."""
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
CATALOGUE = Path(__file__).with_name('cv_callable_producer_reference_notice_review_cases.json')
CALLABLE = '[(PTBRANCH ([PTBUILTIN "callable"]))]'


def prefix(case):
    result = prior.PREFIX
    for method in ('make', 'take'):
        old = '[' + ', '.join('$ptascii(' + json.dumps(name + '\\' + method) + ')' for name in ('MultiCvScalarFormal57', 'MultiCvScalarFormalString57')) + ']'
        result = result.replace(old, '[$ptascii(' + json.dumps('ReviewCallable82\\' + method) + ')]')
    old = 'I;M:1:1:1:1;H:8:0:body;F:29:17:1;R:41:31:37:1:1;'
    for before, after in ((old, case['native_stdout'].split('P:43:')[0]), (old + 'P:43:1:1;', case['native_stdout'].split('Q:43:')[0])):
        result = result.replace(json.dumps(before), json.dumps(after))
    return result


def controls(case):
    lines = prior.controls(0)
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    for tag in ('NName', 'NNameRelative', 'NNameFullyQualified'):
        lines += ['~' + header + tag + ' (BYTES text_return) metadata_return, pfunction_producer.SIGNATURE)']
    for normalized in ('[(PTBRANCH ([PTBUILTIN "CALLABLE"]))]', '[(PTBRANCH ([PTCLASS ($ptascii("callable"))]))]'):
        lines += ['~' + header + 'phpType18_return, pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
    raw = '(NIdentifier (BYTES text_return) metadata_return)'
    nullable = 'NNullableType ' + raw + ' metadata_first_parameter'
    nullable_type = '[(PTBRANCH ([PTBUILTIN "callable"])), (PTBRANCH ([PTBUILTIN "null"]))]'
    lines += [header + nullable + ', pfunction_producer.SIGNATURE[.RETURNS = ' + nullable_type + '])']
    for kinds in (('callable', 'null'), ('null', 'callable'), ('callable', 'int', 'string')):
        atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return' for kind in kinds)
        normalized = '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in kinds) + ']'
        lines += [('~' if len(kinds) > 2 else '') + header + 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_first_parameter, pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
    missing = '$ptascii("ReviewCallable82\\\\doesNotExist")'
    lines += ['~$typed_registered(S_return, ' + missing + ')', '$typed_callable(S_return, PSTRING (' + missing + ')) = (false)']
    for strict in ('false', 'true'):
        for value in ('PINT 17', 'PNULL', 'PBOOL false', 'PSTRING eps', 'PSTRING (' + missing + ')'):
            lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', pvalue_saved, ' + strict + ') = TYPEVALUE pvalue_saved']
    for name in (case['value_name'], case['value_name'][1:], 'REVIEWCALLABLE82\\FIRST', case['changed_name']):
        lines += ['$typed_callable(S_return, PSTRING ($ptascii(' + json.dumps(name) + '))) = (true)']
    return lines


def normal(initial, case, index, front):
    reached = [initial] + prior.front_lines(0, case)
    replacements = {
        'pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))] /\\ ~pfunction_producer.SIGNATURE.BYREF': 'pfunction_producer.SIGNATURE.RETURNS = ' + CALLABLE + r' /\ ~pfunction_producer.SIGNATURE.BYREF',
        '$ptlc($base64(text_return)) = $ptascii("int")': '$ptlc($base64(text_return)) = $ptascii("callable")',
        'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_original_string) ($ptascii("17"))': 'pvalue_original = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(case['value_name']) + '))',
        'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))': 'pvalue_y_original = PSTRING_CARRIER (REQUEST_STRING n_y_string) ($ptascii(' + json.dumps(case['changed_name']) + '))',
        'pvalue_saved = PINT 17': 'pvalue_saved = pvalue_original',
        'pvalue_received_last = PBOOL false': 'pvalue_received_last = pvalue_y_original',
        '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEINTEGER pvalue_original': '$typed_parameter_conversion(S_receive_first, psparam_first, pvalue_original) = TYPEVALUE pvalue_original',
        '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEBOOL pvalue_y_original': '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE pvalue_y_original',
    }
    reached = [replacements.get(line, line) for line in reached]
    reached = [line.replace('(PINT 17)', 'pvalue_saved') if line.startswith(('S_checked.COMPLETION =', 'S_after_return.TODO =', 'S_pre.RESULT =')) else line for line in reached]
    reached += ['~pfunction_producer.CODE.STRICT', 'S_resolved_return = $resolve_at(S_return, S_return.RESULT, z_return)', 'S_resolved_return.RESULT = KNOWN pvalue_saved', 'S_checked = S_resolved_return',
        '$typed_callable(S_args, pvalue_original) = (true)', '$typed_callable(S_args, pvalue_y_original) = (true)',
        '$string_carrier_valid(S_args, pvalue_y_original)', '$string_carrier_valid(S_pre, pvalue_y_original)',
        '$string_carrier_valid(S_pre, pvalue_saved)']
    if front:
        return reached, []
    reached = [line.removeprefix('~') if line.startswith(('~$reference_notice_producer_header(', '~$reference_notice_producer_arguments(')) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in reached]
    full = prior.full_lines(0, case)
    full = [line.replace('(PINT 17)', 'pvalue_saved') if line.startswith(('S_notice.STORE[n_private]', 'S_resume.STORE[n_private]')) else line for line in full]
    reached += full + ['$string_carrier_valid(S_notice, pvalue_saved)', '$string_carrier_valid(S_full, pvalue_y_original)']
    return reached, controls(case)


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
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
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
    fixture.write_text(prefix(cases[0]) + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n')
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
    print('cv-callable-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
