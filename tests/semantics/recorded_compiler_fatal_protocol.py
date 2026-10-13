#!/usr/bin/env python3
"""Retained file-compiler diagnostics and independent abandoned cutoffs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_redeclare_fatal_protocol as source
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

fatal, retirement = source.fatal, source.retirement
ROOT, inputs, types = source.ROOT, source.inputs, source.types
seq, byte_expr, b64 = source.seq, source.byte_expr, source.b64


def prepare(out, sources):
    out.mkdir()
    case = sources / 'static-native-v27/file-distinct-redeclaration-fatals'
    native = json.loads((case.parent / 'report.json').read_text())
    row, = [row for row in native['records'] if row['id'] == case.name]
    adjudication = json.loads((case.parent / 'adjudication.json').read_text())
    assert native['result'] == 'fail' and native['stable_inputs']
    assert native['target'] == types.PROFILE
    assert adjudication['kind'] == 'native_observation' and adjudication['stable_inputs']
    assert adjudication['source_report_sha256'] == hashlib.sha256((case.parent / 'report.json').read_bytes()).hexdigest()
    assert adjudication['observed_f_redeclaration_count'] == 2 and adjudication['observed_g_redeclaration_count'] == 0
    assert row['exit'] == 255 and row['stdout'] == 'B|S|alive|'
    assert (case / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (case / 'native/stderr').read_bytes() == row['stderr'].encode()
    assert all(hashlib.sha256((case / name).read_bytes()).hexdigest() == digest for name, digest in row['originals'].items())
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(filename, unit):
            path = case / filename
            request = {'op': 'parse', 'source': b64(path.read_bytes())} if unit == 0 else {
                'op': 'parse-file', 'id': str(unit), 'mode': 'file', 'profile': 'cli-raw-85',
                'source': b64(path.read_bytes()),
                **{key: b64(os.fsencode(path)) for key in ['requested', 'resolved', 'opened']}}
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']

        main = checked('main.php', 0)
        checks = ['S_open_1 = $php_file_run(' + main + ',2000,' + byte_expr(os.fsencode(case / 'main.php')) + ',' + byte_expr(os.fsencode(case)) + ')',
            'S_open_1.RECORDEDCOMPILEERROR = eps']
        for unit, caller, filename in [(1, 'main.php', 'unit.php'), (2, 'unit.php', 'inner.php'), (3, 'main.php', 'late.php')]:
            fixture = checked(filename, unit)
            opened, parsed, compiled = 'S_open_' + str(unit), 'S_parse_' + str(unit), 'S_compiled_' + str(unit)
            context = 'pfilecontext_open_' + str(unit)
            if unit > 1:
                checks += [opened + ' = $drive_steps(S_compiled_' + str(unit - 1) + ',2000)']
            response = 'FILE_OPENED ' + context + '.NONCE ' + context + '.CALLER ' + context + '.REQUESTED ' + seq(os.fsencode(case / filename)) + ' ' + seq(os.fsencode(case / filename)) + ' ' + seq((case / filename).read_bytes())
            accepted = 'SOURCE_ACCEPT ' + str(unit) + ' ' + seq((case / filename).read_bytes()) + ' ' + fixture
            checks += [opened + '.COMPLETION = SOURCE_PENDING',
                opened + '.FILECONTEXTS = ' + context + ' :: pfilecontext_tail_' + str(unit) + '*',
                context + '.CALLER = ' + seq(os.fsencode(case / caller)),
                context + '.REQUESTED = ' + seq(os.fsencode(case / filename)),
                *fatal.public(opened), '$file_open_response_valid(' + opened + ',' + response + ')',
                parsed + ' = $file_open_resume(' + opened + ',' + response + ')',
                *fatal.public(parsed), '$file_parse_response_valid(' + parsed + ',' + accepted + ')',
                compiled + ' = $file_parse_resume(' + parsed + ',' + accepted + ')']
            if unit == 1:
                checks += [compiled + '.COMPLETION = NORMAL', compiled + '.RECORDEDCOMPILEERROR = eps']
            elif unit == 2:
                checks += ['pcompletion_first = S_compiled_2.COMPLETION', '$recorded_compile_fatal(pcompletion_first)',
                    'S_compiled_2.COMPILESTOP', 'S_compiled_2.ERRORORIGIN = (PORIGIN 2 eps)',
                    'S_compiled_2.RECORDEDCOMPILEERROR = (n_receipt_first)',
                    'S_compiled_2.DECLARATIONS[n_receipt_first] = PDCOMPILERFATAL 2 pcompletion_first (PORIGIN 2 eps) pcompletion_first (PORIGIN 2 eps)',
                    '$recorded_compile_at(S_compiled_2.DECLARATIONS,S_compiled_2.RECORDEDCOMPILEERROR) = ((pcompletion_first,(PORIGIN 2 eps)))']
            else:
                checks += ['S_open_3.RECORDEDCOMPILEERROR = (n_receipt_first)',
                    'S_open_3.DESTRUCTION.ABANDONED = [pdestructioncleanup_first]',
                    'pdestructioncleanup_first.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_first',
                    'pdestructionfatal_first.DECLARATIONS = S_compiled_2.DECLARATIONS',
                    '$eager_fatal_valid(S_open_3,pdestructioncleanup_first,pdestructionfatal_first)',
                    'S_compiled_3.COMPILESTOP', 'S_compiled_3.RECORDEDCOMPILEERROR = eps',
                    'S_compiled_3.COMPLETION = pcompletion_first', 'S_compiled_3.ERRORORIGIN = (PORIGIN 2 eps)',
                    'n_receipt_last = $nabs($(|S_compiled_3.DECLARATIONS| - 1))',
                    'S_compiled_3.DECLARATIONS[n_receipt_last] = PDCOMPILERFATAL 3 pcompletion_raw (PORIGIN 3 eps) pcompletion_first (PORIGIN 2 eps)',
                    'pcompletion_raw = FATAL ($ptascii("Cannot redeclare function g() (previously declared in ") ++ ' + byte_expr(os.fsencode(case / 'main.php')) + ' ++ $ptascii(":3)")) 1',
                    'pcompletion_raw =/= pcompletion_first',
                    '$recorded_compile_cutoff(S_compiled_3.DECLARATIONS) = ((3,pcompletion_first,(PORIGIN 2 eps)))']
        checks += ['S_final = $drive_steps(S_compiled_3,2000)',
            'S_final.DESTRUCTION.ABANDONED = [pdestructioncleanup_first,pdestructioncleanup_last]',
            'pdestructioncleanup_last.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_last',
            'pdestructionfatal_last.DECLARATIONS = S_compiled_3.DECLARATIONS',
            '$eager_fatal_compiler_valid(S_final,pdestructioncleanup_first,pdestructionfatal_first)',
            '$eager_fatal_compiler_valid(S_final,pdestructioncleanup_last,pdestructionfatal_last)',
            '$eager_fatal_valid(S_final,pdestructioncleanup_first,pdestructionfatal_first)',
            '$eager_fatal_valid(S_final,pdestructioncleanup_last,pdestructionfatal_last)',
            *fatal.public('S_final'), 'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S_final.COMPLETION = pdestructionfatal_last.FROZEN', 'S_final.EXITSTATUS = 255',
            'S_final.RECORDEDCOMPILEERROR = eps', 'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps',
            'S_final.STATICS = [pstaticcell]', 'S_final.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
            '$weakref_find(S_final,S_final.ALLOCATIONS,n_object) = (n_weak)',
            '$weakref_get(S_final,n_weak) = POBJECT n_object', 'n_object <- S_final.DESTRUCTION.CALLED',
            '$test_outputs(S_final.EVENTS) = $ptascii("B|S|alive|")',
            '$(|S_parse_2.DECLARATIONS| < |pdestructionfatal_first.DECLARATIONS|)',
            'pdestructionfatal_stale = pdestructionfatal_first[.DECLARATIONS = S_parse_2.DECLARATIONS]',
            'pdestructioncleanup_stale = pdestructioncleanup_first[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_stale]',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = S_final.DESTRUCTION.ABANDONED ++ [pdestructioncleanup_stale]])',
            'pdestructionfatal_wrong = pdestructionfatal_last[.ERRORORIGIN = (PORIGIN 3 eps)]',
            'pdestructioncleanup_wrong = pdestructioncleanup_last[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_wrong]',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_first,pdestructioncleanup_wrong]])',
            '$shutdown_compiler_snapshot(pcompletion_raw) = (pcompletion_frozen)',
            'pdestructionfatal_raw = pdestructionfatal_last[.COMPLETION = pcompletion_raw][.FROZEN = pcompletion_frozen]',
            'pdestructioncleanup_raw = pdestructioncleanup_last[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_raw]',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_first,pdestructioncleanup_raw]])',
            '~$call_descriptors_valid(S_final[.RECORDEDCOMPILEERROR = (n_receipt_first)])',
            '~$call_descriptors_valid(S_open_3[.RECORDEDCOMPILEERROR = (|S_open_3.DECLARATIONS|)])',
            'S_forged = S_final[.DECLARATIONS[n_receipt_last] = PDCOMPILERFATAL 3 (FATAL ($ptascii("forged")) 1) (PORIGIN 3 eps) pcompletion_first (PORIGIN 2 eps)]',
            'pdestructionfatal_forged = pdestructionfatal_last[.DECLARATIONS = S_forged.DECLARATIONS]',
            'pdestructioncleanup_forged = pdestructioncleanup_last[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_forged]',
            '~$call_descriptors_valid(S_forged[.DESTRUCTION.ABANDONED = [pdestructioncleanup_first,pdestructioncleanup_forged]])']
        (out / 'protocol.watsup').write_text(source.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    out, sources = args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0
    case = sources / 'static-native-v27/file-distinct-redeclaration-fatals'
    paths = [Path(__file__), Path(source.__file__), Path(fatal.__file__), Path(retirement.__file__),
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml', case.parent / 'run.py', case.parent / 'report.json',
        case.parent / 'adjudication.json', *sorted(case.glob('*.php')),
        *[case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        paths += [out / 'protocol.watsup', out / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(out / 'protocol.watsup')], out / label, 90, ROOT)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['result'] = 'pass' if passed else 'fail'
            report['runtime_assertions'] = len(json.loads((out / 'assertions.json').read_text())) if passed else 0
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
