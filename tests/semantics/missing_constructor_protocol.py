#!/usr/bin/env python3
"""Reach the ordinary literal/computed missing-constructor rejection in strict SL."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

import error_handler_run as recorder
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/missing-constructor-literal-computed-call.php'
CLASS_GUARDS = (' -- if S.ORIGIN = (porigin_site) '
    '-- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a) '
    '-- if $class_at(S.CLASSES, porigin_a) = (pclassdesc_a)')
LITERAL_STAGE = ('S.TODO = (SCOPED_CLASS (NName (BYTES text_class) metadata_class) '
    '(NIdentifier (BYTES text_method) metadata_method) phpType7* z) :: ptask_tail* '
    '-- if $ptlc($base64(text_class)) = $ptascii("a") '
    '-- if $ptlc($base64(text_method)) = $ptascii("__construct")' + CLASS_GUARDS)
COMPUTED_STAGE = ('S.TODO = (SCOPED_NAME (NName (BYTES text_class) metadata_class) '
    '(KNOWN (PSTRING n_class*)) phpType7* z) :: ptask_tail* '
    '-- if $ptlc($base64(text_class)) = $ptascii("a") '
    '-- if n_class* = $ptascii("A") '
    '-- if S.RESULT = VARIABLE preqbytes_method z_method '
    '-- if preqbytes_method = $ptascii("method")' + CLASS_GUARDS
    + ' -- if $lookup(S.ENV, $ptascii("method")) = (n_cell_method) '
    '-- if S.STORE[n_cell_method] = DEFINED (PSTRING n_method*) '
    '-- if n_method* = $ptascii("__construct")')
LITERAL_CHECKS = [
    '$scoped_class_task(S, NName (BYTES text_class) metadata_class, NIdentifier (BYTES text_method) metadata_method, phpType7*, z)',
    '$call_task_valid(S, SCOPED_CLASS (NName (BYTES text_class) metadata_class) (NIdentifier (BYTES text_method) metadata_method) phpType7* z)',
    r'pclassdesc_a.NAME = $ptascii("A") /\ pclassdesc_a.KIND = "class" /\ ~pclassdesc_a.ABSTRACT',
    '$scoped_source_name(S, NName (BYTES text_class) metadata_class) = (pclassdesc_a.NAME)',
    '$effective_method(S, porigin_a, $ptascii("__construct"), |S.CLASSES|) = eps',
    '$scoped_ctor_arm(S)',
    '$origin_node(S.SOURCES, porigin_site) = (NExprStaticCall (NName (BYTES text_class) metadata_class) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7*) metadata_call)',
    'phpType7* = [(NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument)]',
    r'S.CURRENT = eps /\ $scoped_current_receiver(S) = eps',
    'PhpStep: S ~> S_rejected',
    'S_rejected.COMPLETION = THROWN "Error" $ptascii("Cannot call constructor") z',
    r'S_rejected.TODO = eps /\ S_rejected.CURRENT = S.CURRENT',
    r'S_rejected.OBJECTS = S.OBJECTS /\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\ S_rejected.EVENTS = S.EVENTS',
    '$class_constant_state_valid(S_rejected)',
    '$call_descriptors_valid(S_rejected)',
    '$declaration_history_valid(S_rejected)',
    '$heap_valid($heap_graph(S_rejected))',
]
COMPUTED_CHECKS = [
    '$call_task_valid(S, SCOPED_NAME (NName (BYTES text_class) metadata_class) (KNOWN (PSTRING n_class*)) phpType7* z)',
    '$origin_node(S.SOURCES, porigin_site) = (NExprStaticCall (NName (BYTES text_class) metadata_class) (NExprVariable phpType32 metadata_method) (SEQUENCE phpType7*) metadata_call)',
    '$cv_name(phpType32) = ($ptascii("method"))',
    '~$scoped_ctor_arm(S)',
    '$effective_method(S, porigin_a, $ptascii("__construct"), |S.CLASSES|) = eps',
    '$lookup(S.ENV, $ptascii("method")) = (n_cell_method)',
    'S.STORE[n_cell_method] = DEFINED (PSTRING n_method*)',
    'phpType7* = [(NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN false) metadata_argument)]',
    r'S.CURRENT = eps /\ $scoped_current_receiver(S) = eps',
    'PhpStep: S ~> S_rejected',
    'S_rejected.COMPLETION = THROWN "Error" $ptascii("Call to undefined method A::__construct()") z',
    r'S_rejected.TODO = eps /\ S_rejected.CURRENT = S.CURRENT',
    r'S_rejected.OBJECTS = S.OBJECTS /\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\ S_rejected.EVENTS = S.EVENTS',
    '$class_constant_state_valid(S_rejected)',
    '$call_descriptors_valid(S_rejected)',
    '$declaration_history_valid(S_rejected)',
    '$heap_valid($heap_graph(S_rejected))',
]
CASES = {'literal': (LITERAL_STAGE, LITERAL_CHECKS), 'computed': (COMPUTED_STAGE, COMPUTED_CHECKS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = {args.case: CASES[args.case]} if args.case else CASES
    recorder.ROOT = ROOT
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    php, adapter, runner = (ROOT / name for name in ['.tools/php/bin/php', '_build/default/adapter/main.exe',
                          'tests/semantics/_build/default/numeric_runner.exe'])
    bridge, worker = ROOT / '.tools/php-file.so', ROOT / 'frontend/worker.php'
    watched = [SOURCE, Path(__file__), manifest, *modules, php, adapter, runner, bridge, worker,
               ROOT / 'tests/semantics/profile.json', ROOT / 'spec/schema.json',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py']
    before = {str(path): sha(path) for path in watched}
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    out = Path(tempfile.mkdtemp(prefix='missing-constructor-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'revision': revision, 'working_tree_status': status, 'inputs': before, 'profile': profile,
              'mode': 'SL', 'cache': False, 'det': True, 'source_agreements': 0, 'records': [],
              'selection': list(selected),
              'evaluated': False, 'application_evaluations': 0,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'], parsed
        finally:
            frontend.close()
        checked_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
        try:
            checked = checked_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
        finally:
            checked_worker.close()
        for name, (stage, checks) in selected.items():
            fixture = out / (name + '.watsup')
            fixture.write_text(
                'dec $stage(pstate) : bool\ndef $stage(S) = true -- if ' + stage + '\n'
                'def $stage(S) = false -- otherwise\ndec $seek(pstate, nat) : pstate\n'
                'def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
                'def $seek(S, n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'def $seek(S, 0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) '
                '-- if ~$stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
                'dec $main() : bool\ndef $main() = true\n'
                '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
                + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')\n'
                '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
                '  -- if S_found = $seek(S_initial, 2000)\n'
                '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
                '  -- if S = S_found[.COMPLETION = NORMAL]\n  -- if ' + stage + '\n'
                + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks)
                + 'def $main() = false -- otherwise\n')
            row = {'id': name, 'fixture': str(fixture), 'fixture_sha256': sha(fixture),
                   'reached_premises': len(checks), 'setup_premises': 6, 'evaluated': False, 'passed': args.prepare_only}
            report['records'].append(row)
            if not args.prepare_only:
                row['evaluated'] = report['evaluated'] = True
                report['application_evaluations'] += 1
                row['process'] = process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)],
                                                              out / name, 120)
                row['passed'] = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
                                 and (out / (name + '.stdout')).read_bytes() == b'true\n'
                                 and not (out / (name + '.stderr')).read_bytes())
                print(name, row['passed'], flush=True)
                assert row['passed'], name
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = (len(report['records']) == len(selected) and all(row['passed'] for row in report['records'])
                            and all(report[key] for key in ['inputs_stable', 'head_stable', 'status_stable']))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    assert all(report[key] for key in ['passed', 'inputs_stable', 'head_stable', 'status_stable'])


if __name__ == '__main__':
    main()
