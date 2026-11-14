"""Ground quiet float reception, strict integer widening and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

import cv_int_callable_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_float_callable_producer_reference_notice_review_cases.json')
FORWARD = '[(PTBRANCH ([PTBUILTIN "callable"])), (PTBRANCH ([PTBUILTIN "float"]))]'
REVERSE = '[(PTBRANCH ([PTBUILTIN "float"])), (PTBRANCH ([PTBUILTIN "callable"]))]'


def prefix(case):
    return prior.prefix(case).replace('ReviewCallableInt86', 'ReviewCallableFloat87')


def controls(case):
    args = 'SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(' + args + 'phpType18_return, '
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])',
        '~$positional_reference_notice_pending(S_pre[.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_pre.STRINGDATA|)) ($ptascii("forged87")))])',
        '~$named_reference_notice_operand(S_pre[.REFCELLS = eps], REFERENCE n_y)',
        '~$error_call_valid(S_notice[.REFCELLS = eps], perrorcall)']
    for role, opposite in (('first', REVERSE), ('last', FORWARD)):
        for wrong in ('eps', '[(PTBRANCH ([PTBUILTIN "callable"]))]', opposite,
                FORWARD[:-1] + ', (PTBRANCH ([PTBUILTIN "float"]))]'):
            params = '[psparam_first[.TYPE = ' + wrong + '], psparam_last]' if role == 'first' else '[psparam_first, psparam_last[.TYPE = ' + wrong + ']]'
            lines += ['~$reference_notice_producer_arguments(' + args + signature + '[.RETURNS = eps][.PARAMETERS = ' + params + '])']
    for wrong in (FORWARD, '[(PTBRANCH ([PTBUILTIN "callable"]))]', REVERSE[:-1] + ', (PTBRANCH ([PTBUILTIN "float"]))]'):
        lines += ['~' + header + signature + '[.RETURNS = ' + wrong + '])']
    for kinds in (('callable', 'float'), ('float', 'callable'), ('callable', 'int'), ('int', 'callable'), ('callable', 'string'), ('string', 'callable'), ('callable', 'null'), ('null', 'callable')):
        raw, normalized = prior.raw_types.union(kinds)
        lines += ['$reference_notice_producer_header(' + args + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for kinds in (('callable', 'bool'), ('bool', 'callable'), ('array', 'callable'), ('callable', 'object'), ('callable', 'null', 'int'), ('callable', 'int', 'string'), ('callable', 'callable')):
        raw, normalized = prior.raw_types.union(kinds)
        lines += ['~$reference_notice_producer_header(' + args + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
        raw_param = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
        lines += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([' + raw_param + ', phpType17_last]), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])']
    for update in ('.BYREF = true', '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged callable float default"'):
        lines += ['~$reference_notice_producer_arguments(' + args + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[' + update + '], psparam_last]])']
    callable_value = 'PSTRING ($ptascii(' + json.dumps(case['callable_name']) + '))'
    lines += ['$typed_registered(S_args, $ptascii(' + json.dumps(case['callable_name']) + '))',
        '$typed_callable(S_args, ' + callable_value + ') = (true)']
    for normalized in (FORWARD, REVERSE):
        for strict in ('false', 'true'):
            for value in ('PFLOAT $float_of_int(17)', 'PFLOAT $float_of_int(19)', callable_value):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
            for value in ('PFLOAT $float_of_int(17)', 'PFLOAT $float_of_int(19)'):
                lines += ['$typed_exact(' + normalized + ', ' + value + ')',
                    '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
            for value in ('PNULL', 'PSTRING eps', 'PSTRING ($ptascii("notRegistered87"))'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        for value, integer in (('pvalue_original', 17), ('pvalue_y_original', 19), ('PBOOL true', 1)):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', false) = TYPEVALUE (PFLOAT $float_of_int(' + str(integer) + '))',
                '$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', true) = TYPEREJECT']
        for integer in (17, 19):
            for strict in ('false', 'true'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', PINT ' + str(integer) + ', ' + strict + ') = TYPEVALUE (PFLOAT $float_of_int(' + str(integer) + '))']
    for stage in ('notice', 'receive_last'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return lines


def normal(initial, case, index, front):
    adapted = dict(case, formal_kinds=['int', 'int'])
    reached, _ = prior.normal(initial, adapted, index, front)
    result = []
    for line in reached:
        line = line.replace(prior.FORWARD, FORWARD).replace(prior.REVERSE, REVERSE)
        line = line.replace('$ptascii("int")', '$ptascii("float")')
        line = line.replace('PINT 17', 'PFLOAT $float_of_int(17)').replace('PINT 19', 'PFLOAT $float_of_int(19)')
        line = line.replace('= TYPEINTEGER pvalue_original', '= TYPEVALUE pvalue_saved')
        line = line.replace('= TYPEINTEGER pvalue_y_original', '= TYPEVALUE pvalue_received_last')
        result.append(line)
    return result, [] if front else controls(case)


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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prefix_prior.__file__), Path(prior.raw_types.__file__), CATALOGUE, provenance]
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
    print('cv-float-callable-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
