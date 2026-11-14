"""Ground literal-Boolean identity, local-object ownership and weak rejection."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_null_formal_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_literal_bool_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX.replace('ReviewNotice69\\\\Strict', 'ReviewNotice70\\\\Strict').replace(
    'pcallcontext.NAME = $ptascii("ReviewNotice69\\\\Priority\\\\make")',
    'pcallcontext.NAME <- [$ptascii("ReviewNotice70\\\\FalsePriority\\\\make"), $ptascii("ReviewNotice70\\\\TruePriority\\\\make")]')


def normal(initial, case, front):
    reached, _ = prior.normal(initial, case, front)
    reached = [line.replace('psparam.TYPE = [(PTBRANCH ([PTBUILTIN "null"]))]',
                           'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "true"]))]')
        .replace('$ptlc($base64(text_formal)) = $ptascii("null")',
                 '$ptlc($base64(text_formal)) = $ptascii("true")')
        .replace('pvalue_input = PNULL', 'pvalue_input = PBOOL true') for line in reached]
    derived = []
    if not front:
        proof = '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), pfunction_producer.SIGNATURE[.RETURNS = eps])'
        for kind in ('array', 'int', 'float', 'bool', 'string', 'mixed', 'null', 'false'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]]]]')]
        for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged literal default"'):
            derived += ['~' + proof.replace('.RETURNS = eps]', '.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']]]')]
        for raw, normalized in [
                ('NNullableType (NIdentifier (BYTES text_formal) metadata_type) metadata_type', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
                ('NUnionType (SEQUENCE ([NIdentifier (BYTES text_formal) metadata_type, NIdentifier (BYTES "bnVsbA==") metadata_type])) metadata_type', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "null"]))]'),
                ('NUnionType (SEQUENCE ([NIdentifier (BYTES text_formal) metadata_type, NIdentifier (BYTES "ZmFsc2U=") metadata_type])) metadata_type', '[(PTBRANCH ([PTBUILTIN "true"])), (PTBRANCH ([PTBUILTIN "false"]))]')]:
            derived += [('' if raw.startswith('NNullableType') or '"bnVsbA=="' in raw else '~') + '$reference_notice_producer_arguments(SEQUENCE ([phpType7]), SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']]])']
        for kind, wrong in (('false', 'true'), ('true', 'false')):
            signature = '[(PTBRANCH ([PTBUILTIN "' + kind + '"]))]'
            for strict in ('false', 'true'):
                derived += ['$typed_conversion_at(S_receive, ' + signature + ', PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')']
                for value in ('PBOOL ' + wrong, 'PINT 0', 'PINT 1', 'PSTRING eps', 'PNULL'):
                    derived += ['$typed_conversion_at(S_receive, ' + signature + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        derived += ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
        for name in ('receive', 'return', 'notice'):
            cap = 'S_' + name
            derived += ['S_zero_' + name + ' = $drive(' + cap + ', 0)', 'S_zero_' + name + r'.COMPLETION = BUDGET /\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + cap,
                '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + cap + ', 2)']
    return reached, derived


def priority(initial, index):
    kind, value, byref = ('false', 0, True) if index == 1 else ('true', 1, False)
    reached = [initial] + [line.replace('PTBUILTIN "null"', 'PTBUILTIN "' + kind + '"')
        .replace('$ptascii("null")', '$ptascii("' + kind + '")')
        .replace('pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))',
                 'pvalue_original = PINT ' + str(value))
        for line in prior.PRIORITY if '$string_carrier_valid(' not in line]
    if not byref:
        reached = [line.replace('psparam.BYREF /\\ psparam.REQUIRED', '~psparam.BYREF /\\ psparam.REQUIRED')
            .replace('(BOOLEAN true) (BOOLEAN false) phpType10 ABSENT', '(BOOLEAN false) (BOOLEAN false) phpType10 ABSENT')
            .replace('n_x <- S_receive.REFCELLS /\\ n_formal = n_x', r'n_x <- S_receive.REFCELLS /\ ~(n_formal <- S_receive.REFCELLS) /\ n_formal =/= n_x')
            .replace('(HCELL n_formal) <- S_caught.ALLOCATIONS', '~((HCELL n_formal) <- S_caught.ALLOCATIONS)') for line in reached]
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
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
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
            conditions, current_derived = normal(initial, case, args.front) if index == 0 else priority(initial, index)
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
    print('cv-literal-bool-formal-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
