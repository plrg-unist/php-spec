#!/usr/bin/env python3
"""Quiet private CV return checks preserve generated TypeError cleanup and reports."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

from recorded_worker import Worker
import output_final_return_type_review_state as prior
import output_final_cv_return_type_sources as sources

ROOT = Path(__file__).resolve().parents[2]
CASES = {'core': sources.STRICT, 'weak': sources.CASES['native-cv-weak'],
         'catch': sources.CATCH, 'override': sources.OVERRIDE, 'cleanup': sources.CLEANUP}
PREFIX = prior.OVERRIDE_PREFIX.replace('  -- if S.RESULT = KNOWN (PINT 42)\n', '')


def cell_bindings():
    return ['S.RESULT = VARIABLE n_name* z_origin',
            '$lookup(S.ENV, n_name*) = (n_return_cell)',
            'S.STORE[n_return_cell] = DEFINED pvalue_cell',
            'S_read = $resolve_at(S, S.RESULT, z)',
            'porigin_return = PORIGIN n_unit pcpath_return',
            '$origin_node(S.SOURCES, porigin_return) = (NStmtReturn expression_return metadata_return)',
            '$origin_node(S.SOURCES, PORIGIN n_unit (pcpath_return ++ [PCFIELD 0])) = (NExprVariable (BYTES text_name) metadata_variable)']


def retired(state):
    return f'~((HCELL n_return_cell) <- {state}.ALLOCATIONS) /\\ $heap_count(HCELL n_return_cell, $machine_roots({state})) = 0'


def core(fixture, path):
    bindings, checks = prior.core(fixture, path)
    bindings += cell_bindings() + [
        'S.CLASSES = [pclassdesc]', 'pclassdesc.METHODS = [pmethoddesc]',
        'pmethoddesc.FUNCTION = pfunction',
        'pfunction_global = pfunction[.CODE = pfunction.CODE[.GLOBALS = [pcpath_return]]]',
        'pfunction_static = pfunction[.CODE = pfunction.CODE[.EXPRESSIONS = pfunction.CODE.EXPRESSIONS ++ [CODESTATIC pcpath_return n_name* z_origin z false]]]',
        'S_global = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.FUNCTION = pfunction_global]]]]]',
        'S_static = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc[.FUNCTION = pfunction_static]]]]]',
        'S_ref = S[.REFCELLS = S.REFCELLS ++ [n_return_cell]]',
        'S_extra = S[.HELD = [HCELL n_return_cell]]',
        'S_undefined = S[.STORE = $set_cell(S.STORE, n_return_cell, UNDEFINED)]',
        'S_owning = S[.STORE = $set_cell(S.STORE, n_return_cell, DEFINED (POBJECT n_object))]',
        'S_backed = S[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_return_cell, LINE z, VALUE n_name*}]]',
    ]
    checks.insert(0, ('actual direct private cell and quiet-read refusals',
        r'n_name* = $ptascii("r") /\ n_name* = $base64(text_name) /\ z_origin = 7 /\ pvalue_cell = PINT 42 /\ '
        r'$ob_object_return_error_operand(S, z) /\ S_read = S[.RESULT = KNOWN pvalue_cell] /\ '
        r'$typed_return_value(S, z) = $typed_return_check(S_read, z) /\ '
        r'$heap_count(HCELL n_return_cell, $machine_roots(S)) = 1 /\ $heap_owners($heap_graph(S), HCELL n_return_cell) = 1 /\ '
        r'~$ob_object_return_error_operand(S[.RESULT = VARIABLE ($ptascii("other")) z_origin], z) /\ '
        r'~$ob_object_return_error_operand(S[.RESULT = VARIABLE n_name* $(z_origin + 1)], z) /\ '
        r'~$ob_object_return_error_operand(S_ref, z) /\ ~$ob_object_return_error_operand(S_extra, z) /\ '
        r'~$ob_object_return_error_operand(S_undefined, z) /\ ~$ob_object_return_error_operand(S_owning, z) /\ '
        r'~$ob_object_return_error_operand(S_backed, z) /\ ~$ob_object_return_error_operand(S_global, z) /\ '
        r'~$ob_object_return_error_operand(S_static, z) /\ '
        r'$ob_object_return_error_operand(S_global[.RESULT = KNOWN pvalue_cell], z) /\ '
        r'$ob_object_return_error_operand(S_static[.RESULT = KNOWN pvalue_cell], z) /\ ' + prior.public('S')))
    checks[5] = (checks[5][0], checks[5][1] + r' /\ ' + retired('S_exit'))
    return bindings, checks


def weak(fixture, path):
    bindings, checks = prior.weak(fixture, path)
    bindings += cell_bindings()
    checks[0] = (checks[0][0], checks[0][1] + r' /\ pvalue_cell = PINT 42 /\ $ob_object_return_error_operand(S, z) /\ S_read = S[.RESULT = KNOWN pvalue_cell]')
    checks[1] = (checks[1][0], checks[1][1] + r' /\ ' + retired('S_restored'))
    return bindings, checks


def clearing(name, fixture, path):
    bindings, checks = prior.clearing(name, fixture, path)
    bindings += cell_bindings()
    checks[-1] = (checks[-1][0], checks[-1][1] + r' /\ ' + retired('S_restored'))
    return bindings, checks


def cleanup(fixture, path):
    bindings, checks = prior.cleanup(fixture, path)
    bindings += cell_bindings()
    checks[-1] = (checks[-1][0], checks[-1][1] + r' /\ ' + retired('S_exit'))
    return bindings, checks


def fingerprint(fixture):
    paths = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [Path(__file__), Path(prior.__file__), Path(prior.runner.__file__),
              ROOT / 'tests/semantics/output_final_cv_return_type_sources.py',
              ROOT / 'tests/semantics/profile.json', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', fixture]
    return {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): prior.common.sha(path) for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['all', *CASES], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--checked-root', type=Path)
    parser.add_argument('--native-root', type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-cv-return-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'profile': prior.common.PROFILE, 'native_agreement_credit': 0, 'records': [], 'passed': False}
    try:
        for name in CASES if args.stage == 'all' else [args.stage]:
            directory = out / name
            directory.mkdir()
            source = CASES[name]
            if args.native_root and name in ('core', 'weak'):
                path = args.native_root / ('native-01' if name == 'core' else 'native-02') / 'source.php'
                assert path.read_bytes() == source
            elif args.checked_root and name != 'core':
                path = args.checked_root / 'control-preparation-01' / name / 'source.php'
                assert path.read_bytes() == source
            else:
                path = directory / 'source.php'
                path.write_bytes(source)
            if args.checked_root:
                cached = args.checked_root / ('baseline-01/checked.json' if name == 'core' else f'control-preparation-01/{name}/checked.json')
                checked = json.loads(cached.read_text())
            else:
                frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                                   'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': prior.common.base64.b64encode(source).decode()})
                finally:
                    frontend.close()
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            (directory / 'checked.json').write_text(json.dumps(checked) + '\n')
            emit = core if name == 'core' else weak if name == 'weak' else cleanup if name == 'cleanup' else lambda f, p: clearing(name, f, p)
            bindings, checks = emit(checked['fixture'], path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' + ', '.join('(' + condition + ')' for _, condition in checks) + ']\n' + ''.join('  -- if ' + binding + '\n' for binding in bindings))
            record = {'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(), 'fixture_sha256': prior.common.sha(fixture),
                      'groups': [label for label, _ in checks], 'before': fingerprint(fixture), 'passed': False}
            report['records'].append(record)
            if args.prepare_only:
                record.update(prepared=True, semantic_execution_credit=0)
                continue
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
            started = time.monotonic()
            try:
                result = prior.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                          *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            finally:
                record['seconds'] = round(time.monotonic() - started, 3)
                record['after'] = fingerprint(fixture)
            record['observed'] = [item == b'true' for item in re.findall(rb'true|false', result.stdout)]
            assert result.returncode == 0 and not result.stderr and record['observed'] == [True] * len(checks), (result.returncode, result.stderr, record['observed'])
            assert record['before'] == record['after'], 'watched inputs changed'
            record['passed'] = True
        assert report['records'], 'no fixture selected'
        report['passed'] = not args.prepare_only and all(record['passed'] for record in report['records'])
        report['prepared'] = args.prepare_only
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
