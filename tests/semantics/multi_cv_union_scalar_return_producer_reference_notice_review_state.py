"""Check ordered scalar/null INT/BOOL conversion, duplicate CVs and strict return-error priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
import multi_cv_nullable_scalar_return_producer_reference_notice_review_state as nullable
import multi_cv_scalar_return_producer_reference_notice_review_state as scalar
import multi_cv_union_array_return_producer_reference_notice_review_state as union
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_union_scalar_return_producer_reference_notice_review_cases.json')
RAW_RETURN = 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return_first) metadata_return_first, NIdentifier (BYTES text_return_last) metadata_return_last])) metadata_union'
ORDERED = '[(PTBRANCH ([PTBUILTIN text_return_first_kind])), (PTBRANCH ([PTBUILTIN text_return_last_kind]))]'
PREFIX = nullable.PREFIX.replace('ReviewNotice54', 'ReviewNotice55')
RETURN = [line.replace('[(PTBRANCH ([PTBUILTIN text_kind]))]', ORDERED)
    .replace('(NIdentifier (BYTES text_type) metadata_type) phpType23', '(' + RAW_RETURN + ') phpType23')
    .replace('$ptlc($base64(text_type)) = $ptascii(text_kind)',
        '$ptlc($base64(text_return_first)) = $ptascii(text_return_first_kind) /\\ $ptlc($base64(text_return_last)) = $ptascii(text_return_last_kind)')
    for line in scalar.RETURN]
PRIORITY_RAW = 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_type) metadata_type, NIdentifier (BYTES "bnVsbA==") metadata_null])) metadata_union'
PRIORITY = [line.replace(nullable.RAW_RETURN, PRIORITY_RAW) for line in nullable.PRIORITY]


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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), CATALOGUE, provenance, Path(scalar.__file__), Path(union.__file__), Path(nullable.__file__)]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
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
            current_derived = []
            if index < 2:
                kind = 'int' if index == 0 else 'bool'
                values = ['text_kind = ' + json.dumps(kind), 'pvalue_expected = ' + ('PINT 17' if kind == 'int' else 'PBOOL false'),
                    'text_return_first_kind = ' + json.dumps('null' if kind == 'int' else 'bool'),
                    'text_return_last_kind = ' + json.dumps('int' if kind == 'int' else 'null')]
                payload = ('pvalue_string = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))' if kind == 'int'
                    else 'pvalue_string = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))')
                conditions = [initial] + values + RETURN + [payload] + scalar.PRE
                conditions += ['$runtime_line(S_pre[.ORIGIN = (porigin_last)], eps, expression_last) = ' + str(case['notice_line'])]
                header = '$reference_notice_producer_header(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ' + RAW_RETURN + ', pfunction_producer.SIGNATURE)'
                conditions += [('~' if args.front else '') + header, ('~' if args.front else '') + '$named_reference_notice_pending(S_pre)']
                if not args.front:
                    conditions += scalar.PRIVATE + ['perrorcall.LINE = ' + str(case['notice_line']),
                        '$mcsr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
                    if kind == 'int':
                        conditions += ['S_prefinal.STORE[n_private] = DEFINED (PARRAY n_private_array)',
                            'S_prefinal.ARRAYS[n_private_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]',
                            '$node_children(S_prefinal, HCELL n_private) = [HARRAY n_private_array]']
                    else:
                        conditions += ['S_prefinal.STORE[n_private] = DEFINED (PSTRING ($ptascii("Xody")))',
                            '$lookup(S_prefinal.ENV, $ptascii("hold")) = (n_hold)',
                            'S_prefinal.STORE[n_hold] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("body")))',
                            '$lookup(S_full.ENV, $ptascii("hold")) = eps']
                    scalar_member = ('NIdentifier (BYTES text_return_last) metadata_return_last' if kind == 'int'
                        else 'NIdentifier (BYTES text_return_first) metadata_return_first')
                    current_derived = [
                        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
                        '~' + header.replace(RAW_RETURN, 'ABSENT'),
                        '~' + header.replace(RAW_RETURN, scalar_member),
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN text_kind]))]])'),
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN text_return_last_kind])), (PTBRANCH ([PTBUILTIN text_return_first_kind]))]])'),
                        '~' + header.replace('text_return_first)', '"YXJyYXk=")'),
                        '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam_first[.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]], psparam_last]])'),
                        '~' + header.replace(RAW_RETURN, 'NUnionType (SEQUENCE ([' + scalar_member + ', ' + scalar_member + '])) metadata_union')
                            .replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN text_kind])), (PTBRANCH ([PTBUILTIN text_kind]))]])'),
                        '~' + header.replace(RAW_RETURN, 'NUnionType (SEQUENCE ([' + scalar_member + ', NIdentifier (BYTES "ZmxvYXQ=") metadata_union])) metadata_union')
                            .replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN text_kind])), (PTBRANCH ([PTBUILTIN "float"]))]])'),
                        '~' + header.replace(RAW_RETURN, 'NUnionType (SEQUENCE ([' + scalar_member + ', ' + scalar_member + ', ' + scalar_member + '])) metadata_union'),
                        header.replace(RAW_RETURN, 'NNullableType (' + scalar_member + ') metadata_union')
                            .replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN text_kind])), (PTBRANCH ([PTBUILTIN "null"]))]])'),
                        'S_zero = $drive(S_notice, 0)',
                        'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S_notice',
                        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)',
                    ]
            else:
                conditions = [initial] + PRIORITY + ['$mcsr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
            case_specs.append('dec $mcusr_case' + str(index) + '() : bool\ndef $mcusr_case' + str(index) + '() = true\n' +
                ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) +
        '\ndec $main() : bool\ndef $main() = true\n  -- if $mcusr_case0()\n  -- if $mcusr_case1()\n  -- if $mcusr_case2()\n')
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json',
        'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable,
        head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true',
        front=args.front, conditions=len(reached) + len(derived), reached_conditions=len(reached),
        derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-union-scalar-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
