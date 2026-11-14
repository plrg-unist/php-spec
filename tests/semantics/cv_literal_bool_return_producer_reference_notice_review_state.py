"""Ground exact true returns, private COW and weak false/true RETURN priority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_null_return_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_literal_bool_return_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice66', 'ReviewNotice71').replace(
    'pcallcontext.NAME = $ptascii("ReviewNotice71\\\\Priority\\\\make")',
    'pcallcontext.NAME <- [$ptascii("ReviewNotice71\\\\FalsePriority\\\\make"), $ptascii("ReviewNotice71\\\\TruePriority\\\\make")]')
for suffix in ('C:11:2:1:1;', 'C:11:2:1:1;D:11:31:23:1;'):
    PREFIX = PREFIX.replace('$scfr_output(S.EVENTS) = $ptascii("P;M:17;' + suffix + '")',
        '$scfr_output(S.EVENTS) <- [$ptascii("P;M:0;' + suffix + '"), $ptascii("P;M:1;' + suffix + '")]')


def normal(initial, case, front):
    reached = []
    for line in prior.FRONT:
        line = line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]',
                            'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]')
        line = line.replace('NNullableType (NIdentifier (BYTES text_type) metadata_type) metadata_nullable',
                            'NIdentifier (BYTES text_type) metadata_type')
        line = line.replace('$ptlc($base64(text_type)) = $ptascii("array")', '$ptlc($base64(text_type)) = $ptascii("mixed")')
        line = line.replace('PTBUILTIN "null"', 'PTBUILTIN "true"')
        line = line.replace('$ptascii("null")', '$ptascii("true")')
        line = line.replace('DEFINED PNULL', 'DEFINED (PBOOL true)').replace('KNOWN PNULL', 'KNOWN (PBOOL true)')
        line = line.replace('psparam, PNULL) = TYPEVALUE PNULL', 'psparam, PBOOL true) = TYPEVALUE (PBOOL true)')
        reached.append(line)
    header = '$reference_notice_producer_header(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), phpType18, pfunction_producer.SIGNATURE)'
    reached = [initial] + reached + [('~' if front else '') + line for line in (header, '$named_reference_notice_pending(S_pre)')]
    derived = []
    if not front:
        reached += [line.replace('DEFINED PNULL', 'DEFINED (PBOOL true)') for line in prior.FULL]
        reached += ['$scfr_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
        for kind in ('false', 'bool', 'null', 'mixed', 'array'):
            derived += ['~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]])')]
        for raw, normalized in (
                ('NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_return', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
                ('NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
                ('NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "aW50") metadata_return])) metadata_return', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "int"]))]')):
            derived += [('' if raw.startswith('NNullableType') or '"bnVsbA=="' in raw else '~') + header.replace('phpType18,', raw + ',').replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])')]
        derived += ['~' + header.replace('phpType18,', 'NIdentifier (BYTES "ZmFsc2U=") metadata_return,'),
            '~' + header.replace('phpType18,', 'NName (BYTES text_return) metadata_return,'),
            '~' + header.replace('pfunction_producer.SIGNATURE)', 'pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])'),
            '~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
        for kind, wrong in (('false', 'true'), ('true', 'false')):
            signature = '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))]'
            for strict in ('false', 'true'):
                derived += ['$typed_conversion_at(S_return, ' + signature + ', PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')']
                for value in ('PBOOL ' + wrong, 'PINT 0', 'PINT 1', 'PNULL', 'PSTRING eps'):
                    derived += ['$typed_conversion_at(S_return, ' + signature + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        derived += [
            'S_return.CURRENT = (pcallcontext_return)',
            'pcallcontext_return.CALLSITE = (PORIGIN n_caller pcpath_call)',
            '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
            'S_weak_callee = S_return[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("17")))][.FUNCTIONS = [pfunction_producer[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]][.CODE.STRICT = false]]][.CODE = [pcode_caller[.STRICT = true]]]',
            '$typed_caller_strict(S_weak_callee)',
            'S_weak_checked = $typed_return_check(S_weak_callee, z_return)',
            'S_weak_checked.COMPLETION = NORMAL /\\ S_weak_checked.RESULT = KNOWN (PINT 17)',
            'S_strict_callee = S_return[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("17")))][.FUNCTIONS = [pfunction_producer[.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]][.CODE.STRICT = true]]][.CODE = [pcode_caller[.STRICT = false]]]',
            '~$typed_caller_strict(S_strict_callee)',
            'S_strict_checked = $typed_return_check(S_strict_callee, z_return)',
            'S_strict_checked.COMPLETION = THROWN "TypeError" ptbytes_message z_return']
        for name in ('receive', 'return', 'notice'):
            stage = 'S_' + name
            derived += ['S_zero_' + name + ' = $drive(' + stage + ', 0)',
                'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + stage,
                '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + stage + ', 2)']
    return reached, derived


def priority(initial, case):
    kind, value = case['return_kind'], case['input_integer']
    reached = [initial]
    for line in prior.PRIORITY:
        if 'pvalue_original = ' in line or '$string_carrier_valid' in line:
            continue
        reached += [line.replace('pvalue_original', 'PINT ' + str(value))
            .replace('PTBUILTIN "null"', 'PTBUILTIN "' + kind + '"')
            .replace('$ptascii("null")', '$ptascii("' + kind + '")')
            .replace('P;M:17;', 'P;M:' + str(value) + ';')]
    return reached, []


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
    paths = [Path(__file__), CATALOGUE, provenance, Path(prior.__file__), Path(prior.prior.__file__), Path(prior.return_prior.__file__)]
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
            conditions, current_derived = normal(initial, case, args.front) if index == 0 else priority(initial, case)
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
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scfr_case' + str(i) + '()\n' for i in range(3)))
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
    print('cv-literal-bool-return-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
