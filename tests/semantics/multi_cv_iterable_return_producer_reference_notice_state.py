#!/usr/bin/env python3
"""Check multiple required CV formals, bare iterable returns and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import singleton_cv_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_iterable_return_producer_reference_notice_cases.json')
PREFIX, ITERABLE = prior.PREFIX, prior.ITERABLE


def branches(kind):
    return 'eps' if kind is None else '[(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))]'


def vector(case, selected, other):
    return '[' + ', '.join([selected, other] if case['formal_index'] == 0 else [other, selected]) + ']'


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        line = line.replace('pfunction_producer.SIGNATURE.PARAMETERS = [psparam]', 'pfunction_producer.SIGNATURE.PARAMETERS = ' + vector(case, 'psparam', 'psparam_other'))
        line = line.replace('phpType6_producer = SEQUENCE ([phpType7_actual])', 'phpType6_producer = SEQUENCE (' + vector(case, 'phpType7_actual', 'phpType7_other') + ')')
        line = line.replace('phpType16 = SEQUENCE ([phpType17])', 'phpType16 = SEQUENCE (' + vector(case, 'phpType17', 'phpType17_other') + ')')
        lines.append(line)
    if case.get('priority_control'):
        lines += ['$origin_node(S_return.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
            'phpType16 = SEQUENCE (' + vector(case, 'phpType17', 'phpType17_other') + ')',
            'phpType18 = NIdentifier (BYTES text_return) metadata_return',
            '$ptlc($base64(text_return)) = $ptascii("iterable")']
    raw = 'ABSENT' if case['formal_kind'] is None else '(NIdentifier (BYTES text_formal) metadata_formal)'
    ref = str(case['formal_byref']).lower()
    lines += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN ' + ref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        'psparam.NAME = $ptascii(' + json.dumps(case['formal_name']) + ')',
        'psparam.TYPE = ' + branches(case['formal_kind']),
        'psparam.BYREF = ' + ref + r' /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE']
    if case['formal_kind'] is not None:
        lines.append('$ptlc($base64(text_formal)) = $ptascii(' + json.dumps(case['formal_kind']) + ')')
    lines += ['phpType17_other = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_other_formal) metadata_other_type) (BOOLEAN false) (BOOLEAN false) phpType10_other ABSENT (SEQUENCE eps) metadata_other_parameter',
        '$ptlc($base64(text_other_formal)) = $ptascii("int")',
        'psparam_other.NAME = $ptascii("stamp")',
        'psparam_other.TYPE = ' + branches('int'),
        r'~psparam_other.BYREF /\ psparam_other.REQUIRED /\ ~psparam_other.VARIADIC /\ psparam_other.DEFAULT = PSNONE',
        '$lookup(S_return.ENV, $ptascii("stamp")) = (n_stamp_formal)',
        'S_return.STORE[n_stamp_formal] = DEFINED (PINT 5)',
        '~(n_stamp_formal <- S_return.REFCELLS)',
        'S_return.GLOBALTABLE = (psymboltable_caller)',
        '$lookup(psymboltable_caller.ENV, $ptascii("stamp")) = (n_stamp_caller)',
        'S_return.STORE[n_stamp_caller] = DEFINED (PINT 5)',
        'n_stamp_formal =/= n_stamp_caller',
        '$typed_parameter_conversion(S_return, psparam_other, PINT 5) = TYPEVALUE (PINT 5)']
    if case.get('priority_control'):
        lines += ['$lookup(S_full.ENV, $ptascii("stamp")) = (n_stamp_caller)',
            'S_full.STORE[n_stamp_caller] = DEFINED (PINT 5)',
            '~((HCELL n_stamp_formal) <- S_full.ALLOCATIONS)',
            '$lookup(S_full.ENV, $ptascii("source")) = (n_source)',
            '$lookup(S_full.ENV, $ptascii("sourceAlias")) = (n_source)',
            'S_full.STORE[n_source] = DEFINED (PINT 19)',
            '$propref_at(S_full.PROPREFS, n_source) = eps',
            '$reference_coercion_at(S_full.REFCOERCIONS, n_source) = eps']
        return lines
    lines += ['phpType7_other = NArg ABSENT expression_other (BOOLEAN false) (BOOLEAN false) metadata_other_actual',
        'expression_other = NExprVariable (BYTES text_other_actual) metadata_other_variable',
        '$reference_cv(expression_other) = ($ptascii("stamp"))',
        '$lookup(S_pre.ENV, $ptascii("stamp")) = (n_stamp_caller)',
        'S_pre.STORE[n_stamp_caller] = DEFINED (PINT 5)',
        '~((HCELL n_stamp_formal) <- S_pre.ALLOCATIONS)']
    return lines


def completed(case):
    if case.get('priority_control'):
        return []
    return prior.completed(case) + ['$lookup(S_full.ENV, $ptascii("stamp")) = (n_stamp_caller)',
        'S_full.STORE[n_stamp_caller] = DEFINED (PINT 5)',
        r'n_private =/= n_stamp_caller /\ n_private =/= n_stamp_formal',
        '$propref_at(S_full.PROPREFS, n_stamp_caller) = eps',
        '$reference_coercion_at(S_full.REFCOERCIONS, n_stamp_caller) = eps']


def controls(case):
    lines = []
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    for line in prior.controls(case):
        if '[.PARAMETERS = [psparam[.' in line:
            continue
        lines.append(line)
    if case.get('priority_control'):
        return lines
    signature = 'pfunction_producer.SIGNATURE'
    for selected, ref in ((True, case['formal_byref']), (False, False)):
        wrong = 'bool' if selected else 'array'
        for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not ref).lower(),
                'DEFAULT = PSDEFAULTUNSUPPORTED "forged multi iterable return formal"', 'TYPE = ' + branches(wrong)):
            selected_formal, other_formal = ('psparam[.' + edit + ']', 'psparam_other') if selected else ('psparam', 'psparam_other[.' + edit + ']')
            lines.append('~' + header + 'phpType18, ' + signature + '[.PARAMETERS = ' + vector(case, selected_formal, other_formal) + '])')
    return lines


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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('multi-cv-iterable-return-front' if args.front else 'multi-cv-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
