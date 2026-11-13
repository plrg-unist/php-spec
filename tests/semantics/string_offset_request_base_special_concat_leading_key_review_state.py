#!/usr/bin/env python3
"""Independent special-CONCAT pool authority, name boundaries and lifetimes."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_special_concat_leading_key_cases as cases
import string_offset_request_base_literal_leading_key_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
lines = prior.lines
HELPERS = prior.HELPERS + r'''
dec $special_review_fact(pconstant, pcpath) : bool
def $special_review_fact(PCONSTANT pcpath pvalue, pcpath) = true
def $special_review_fact(pconstant, pcpath) = false -- otherwise
dec $special_review_constants(pconstant*, pcpath, pvalue?) : pconstant*
def $special_review_constants(eps, pcpath, pvalue?) = eps
def $special_review_constants((PCONSTANT pcpath pvalue_old) :: pconstant*, pcpath, eps) = pconstant*
def $special_review_constants((PCONSTANT pcpath pvalue_old) :: pconstant*, pcpath, (pvalue_new)) = (PCONSTANT pcpath pvalue_new) :: pconstant*
def $special_review_constants(pconstant :: pconstant_tail*, pcpath, pvalue?) = pconstant :: $special_review_constants(pconstant_tail*, pcpath, pvalue?)
  -- if ~$special_review_fact(pconstant, pcpath)
dec $special_review_pools(ppool*, porigin, pvalue?) : ppool*
def $special_review_pools(eps, porigin, pvalue?) = eps
def $special_review_pools(ppool :: ppool_tail*, PORIGIN n pcpath, pvalue?) = ppool[.CONSTANTS = $special_review_constants(ppool.CONSTANTS, pcpath, pvalue?)] :: ppool_tail*
  -- if ppool.UNIT = n
def $special_review_pools(ppool :: ppool_tail*, PORIGIN n pcpath, pvalue?) = ppool :: $special_review_pools(ppool_tail*, PORIGIN n pcpath, pvalue?)
  -- if ppool.UNIT =/= n
dec $special_review_concat_path(pcoccurrence*) : pcpath?
dec $special_review_is_concat(pcnode) : bool
def $special_review_is_concat(NExprBinaryOpConcat expression_1 expression_2 metadata) = true
def $special_review_is_concat(pcnode) = false -- otherwise
def $special_review_concat_path(eps) = eps
def $special_review_concat_path((PCOCCURRENCE pcpath (NExprBinaryOpConcat expression_1 expression_2 metadata)) :: pcoccurrence*) = (pcpath)
def $special_review_concat_path((PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*) = $special_review_concat_path(pcoccurrence_tail*)
  -- if ~$special_review_is_concat(pcnode)
'''

CONTROLS = {
    'qualified-missing-special': b"<?php $x = \\DefinitelyMissing\\true . 'x';\n",
    'relative-missing-special': b"<?php namespace DefinitelyMissing; $x = namespace\\true . 'x';\n",
    'imported-missing-special': b"<?php use const DefinitelyMissing\\true as Leaf; $x = Leaf . 'x';\n",
    'mixed-leading-numeric-string-unary-special': b"<?php $x = (+(+\"1.0tail\") . false) . 'x';\n",
}


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    key = '3x' if index == 2 else '1x'
    root = '$origin_node(S.SOURCES, porigin_key) = (NScalarString (BYTES text) metadata)'
    value = '$base64(text) = $ptascii("' + key + '")'
    assert checks.count(root) == checks.count(value) == 1
    checks[checks.index(root)] = '$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata_key)'
    checks[checks.index(value)] = '$compiled_special_concat_bytes(S, porigin_key) = ($ptascii("' + key + '"))'
    checks = [check.replace('PSTRING_CARRIER (REQUEST_STRING 0)', 'PSTRING_CARRIER (REQUEST_STRING n_base_identity)') for check in checks]
    at = checks.index('pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_base_identity) ($ptascii("abc"))') + 1
    checks.insert(at, 'S.STRINGDATA[n_base_identity] = $ptascii("abc")')
    for at, check in enumerate(checks):
        if check.startswith('S_nul = '):
            checks[at] = 'S_nul = S[.STRINGDATA[n_base_identity] = [97,0,99]][.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_base_identity) ([97,0,99]))][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_base_identity) ([97,0,99]))]'
        elif check.startswith('S_equal = '):
            checks[at] = 'S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))]'
    special_path = '[PCFIELD 0]' if index == 0 else '[PCFIELD 0, PCFIELD 1]'
    special_value = ('PBOOL true', 'PNULL', 'PBOOL false')[index]
    ast = [
        '$compiled_precision(S, (porigin_key)) = (14)',
        '$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 14) = eps',
        '$compiled_string_value(S, porigin_key, PSTRING ($ptascii("' + key + '"))) = pstringread.READ.VALUE',
        '$origin_child((porigin_key), ' + special_path + ') = (porigin_special)',
        '$origin_node(S.SOURCES, porigin_special) = (NExprConstFetch name metadata_special)',
        '$compiled_read(S, porigin_special) = (' + special_value + ')',
        '$parser_literal_at(NExprConstFetch name metadata_special, 14) = eps',
        '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = eps',
    ]
    if index == 0:
        ast += lines(r'''
expression_1 = NExprConstFetch name metadata_special
expression_2 = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_suffix) = $ptascii("x")
''')
    else:
        ast += lines(r'''
expression_1 = NExprBinaryOpConcat expression_11 expression_12 metadata_inner
expression_11 = NScalarString (BYTES text_prefix) metadata_prefix
expression_12 = NExprConstFetch name metadata_special
expression_2 = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_suffix) = $ptascii("x")
$origin_child((porigin_key), [PCFIELD 0]) = (porigin_inner)
''') + ['$base64(text_prefix) = $ptascii("' + ('3' if index == 2 else '1') + '")',
        '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + ('3' if index == 2 else '1') + '")))']
    at = checks.index('$compiled_special_concat_bytes(S, porigin_key) = ($ptascii("' + key + '"))') + 1
    checks[at:at] = ast
    extra = lines(r'''
S_drop_child = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_special, eps)]
$compiled_read(S_drop_child, porigin_special) = eps
$compiled_special_concat_bytes(S_drop_child, porigin_key) = eps
$string_read_request_base_saved(S_drop_child, pstringread) = eps
S_wrong_type = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_special, (PFLOAT 4607182418800017408))]
$compiled_read(S_wrong_type, porigin_special) = (PFLOAT 4607182418800017408)
$compiled_special_concat_bytes(S_wrong_type, porigin_key) = eps
$string_read_request_base_saved(S_wrong_type, pstringread) = eps
S_drop_root = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_key, eps)]
$compiled_read(S_drop_root, porigin_key) = eps
$compiled_special_concat_bytes(S_drop_root, porigin_key) = eps
$string_read_request_base_saved(S_drop_root, pstringread) = eps
S_wrong_root = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_key, (PSTRING ($ptascii("wrong"))))]
$compiled_special_concat_bytes(S_wrong_root, porigin_key) = eps
$compiled_string_value(S_wrong_root, porigin_key, PSTRING ($ptascii("wrong"))) = PSTRING ($ptascii("wrong"))
''') + ['$compiled_read(S_drop_child, porigin_key) = (PSTRING ($ptascii("' + key + '")))',
        '$compiled_string_value(S_drop_child, porigin_key, PSTRING ($ptascii("' + key + '"))) = PSTRING ($ptascii("' + key + '"))',
        'S_wrong_child = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_special, (PBOOL ' + ('false' if index == 0 else 'true') + '))]',
        '$compiled_special_concat_bytes(S_wrong_child, porigin_key) = eps',
        '$string_read_request_base_saved(S_wrong_child, pstringread) = eps']
    if index > 0:
        extra += lines(r'''
S_drop_inner = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_inner, eps)]
$compiled_read(S_drop_inner, porigin_inner) = eps
$compiled_special_concat_bytes(S_drop_inner, porigin_key) = eps
$string_read_request_base_saved(S_drop_inner, pstringread) = eps
''')
    checks += extra
    return checks, derived + len(extra)


def compiler_conditions(checked, paths):
    checks = []
    for index, (name, value) in enumerate(checked.items()):
        suffix = str(index)
        state, origin, child = ('S_control_' + suffix, 'porigin_control_' + suffix, 'porigin_child_' + suffix)
        path = 'pcpath_control_' + suffix
        checks += [state + ' = $php_run(' + value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
            state + '.COMPLETION = BUDGET',
            state + '.SOURCES[0].ID = 0',
            '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (' + path + ')',
            origin + ' = PORIGIN 0 ' + path,
            '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
            '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING ($ptascii("1x"))']
        checks += ['$compiled_read(' + state + ', ' + origin + ') = eps']
        if name != 'mixed-leading-numeric-string-unary-special':
            qualifier = ('PTFULL', 'PTRELATIVE', 'PTPLAIN')[index]
            checks += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                '$origin_node(' + state + '.SOURCES, ' + child + ') = (NExprConstFetch name_control_' + suffix + ' metadata_control_' + suffix + ')',
                '$ptast(name_control_' + suffix + ') = PTNAME ' + qualifier + ' ptbytes_control_' + suffix,
                '$compiled_read(' + state + ', ' + child + ') = eps']
    return checks


def main(expected_outputs=prior.cases.OUTPUTS):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controls-only', action='store_true')
    parser.add_argument('--control', action='append')
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile and report['selection'] == list(cases.CASES)
    assert cases.OUTPUTS == expected_outputs
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    controls = {name: CONTROLS[name] for name in args.control} if args.control else CONTROLS
    sources = ({} if args.controls_only else dict(cases.CASES)) | controls
    control_paths = {name: out / (name + '.php') for name in controls}
    for name, path in control_paths.items():
        path.write_bytes(controls[name])
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in sources.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    fixtures, originals, selections = [], list(control_paths.values()), []
    source_cases = {} if args.controls_only else cases.CASES
    for index, (name, source_bytes) in enumerate(source_cases.items()):
        row = rows[name]
        native, outcome = row['native'], row['outcome']
        assert row['passed'] and outcome['status'] == 'normal' and outcome['exit_status'] == 0
        assert base64.b64decode(outcome['stdout']) == cases.OUTPUTS[index] and not base64.b64decode(outcome['stderr'])
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source, stdout, stderr = Path(native['argv'][-1]), Path(row['native_stdout']), Path(row['native_stderr'])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert stdout.read_bytes() == cases.OUTPUTS[index] and not stderr.read_bytes()
        originals += [source, stdout, stderr]
        checks, derived = conditions(checked[name]['fixture'], source, index)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived, 'compiler_conditions': 0, 'source_credit': 0})
    checks = compiler_conditions({name: checked[name] for name in controls}, control_paths)
    fixture = out / 'compiler-name-shape-controls.watsup'
    fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    fixtures.append(fixture)
    selections.append({'id': 'compiler-name-shape-controls', 'conditions': len(checks), 'derived_conditions': 0, 'compiler_conditions': len(checks), 'source_credit': 0})
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(prior.cases.__file__), Path(prior.shared.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path.endswith('/.tools/php/bin/php') or path == '.tools/php/bin/php'] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(selections, fixtures):
        stem = out / (row['id'] + '-model')
        process = recorded([str(runner), *map(str, modules), str(fixture)], stem, 180)
        row['model'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and stem.with_suffix('.stdout').read_bytes() == b'true\n' and not stem.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], process['elapsed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in selections)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'module_entries': len(modules), 'selection': [row['id'] for row in selections], 'selected_controls': list(controls), 'controls_only': args.controls_only, 'rows': selections, 'conditions': sum(row['conditions'] for row in selections), 'derived_conditions': sum(row['derived_conditions'] for row in selections), 'compiler_conditions': len(checks), 'inputs': before, 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
