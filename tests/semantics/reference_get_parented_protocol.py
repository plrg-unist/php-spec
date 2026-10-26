"""Frozen source comparisons and reached checks for parented reference Get."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import reference_get_chain_protocol as chain
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'reference_get_parented_cases.json'
EXPECTATIONS = HERE / 'reference_get_parented_expectations.json'
FROZEN = 'ab46a74bc213d5dd6ce0ba6ce94e8dea095aa98b44cc5621326bcc3165d48563'
CONFIG = {
    'parented-typed-latest': ('LeafA140', 'ChildA140', 'GetterA140', 11, True, ['ChildA140', 'LeafA140']),
    'parented-untyped-null': ('LeafB140', 'GetterB140', 'GetterB140', 'NULL', False, ['ChildB140', 'LeafB140']),
    'parented-rebind-error': ('LeafC140', 'ChildC140', 'GetterC140', 11, True, ['ChildC140', 'LeafC140']),
    'ordinary-override-control': ('LeafD140', 'GetterD140', 'GetterD140', 7, True, ['LeafD140']),
}
BASE = {
    'parented-typed-latest': ('BaseA140', 'GetterA140', 'absent'),
    'parented-untyped-null': ('BaseB140', 'GetterB140', 'absent'),
    'parented-rebind-error': ('BaseC140', 'GetterC140', 'absent'),
    'ordinary-override-control': ('BaseD140', 'GetterD140', 'plain'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quote(value):
    return json.dumps(value)


def conditions(case, program, path, expected):
    base_case = 'deep-rebind-error' if case == 'parented-rebind-error' else case
    chain.CONFIG[base_case] = CONFIG[case]
    checks = chain.conditions(base_case, program, path, expected)
    if case == 'parented-untyped-null':
        checks = [item.replace('PINT NULL', 'PNULL') for item in checks]
    if case == 'parented-rebind-error':
        checks = [item.replace('ppropertyhook.LINE = 16', 'ppropertyhook.LINE = 19')
                      .replace(' 16]', ' 19]')
                      .replace('DEFINED (PINT 17)', 'DEFINED (PINT 23)')
                  for item in checks]
    base, getter, kind = BASE[case]
    checks += chain.lines(f'''
    $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(base)}))) = (porigin_base)
    $class_at(S_front.CLASSES,porigin_base) = (pclassdesc_base)
    pclassdesc_base.KIND = "class" /\\ pclassdesc_base.PARENT = eps
    $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(getter)}))) = (porigin_getter)
    $class_at(S_front.CLASSES,porigin_getter) = (pclassdesc_getter)
    pclassdesc_getter.PARENT =/= eps
    $class_link_at(S_front.LINKEDPARENTS,porigin_getter) = (SOURCE_PARENT porigin_base)
    $property_desc_at(pclassdesc_base.PROPERTIES,$ptascii("baseSide")) = (ppropertydesc_base_side)
    $property_desc_at($property_layout(S_front,porigin_receiver,|S_front.CLASSES|),$ptascii("baseSide")) = (ppropertydesc_base_side)
    $property_hook_reference_ancestor(S_front,porigin_getter,ppropertydesc_getter)
    S_missing_base_link = S_front[.LINKEDPARENTS = $rc_without(S_front.LINKEDPARENTS,porigin_getter)]
    ~$property_hook_reference_ancestor(S_missing_base_link,porigin_getter,ppropertydesc_getter)
    ~$property_hook_reference_decl(S_missing_base_link,ppropertydesc_getter)
    ''')
    if kind == 'absent':
        checks += chain.lines('''
        $property_desc_at($property_layout(S_front,porigin_base,|S_front.CLASSES|),$ptascii("value")) = eps
        ''')
    else:
        checks += chain.lines('''
        $property_desc_at(pclassdesc_base.PROPERTIES,$ptascii("value")) = (ppropertydesc_base_value)
        $property_desc_at($property_layout(S_front,porigin_base,|S_front.CLASSES|),$ptascii("value")) = (ppropertydesc_base_value)
        $property_default_state(S_front,ppropertydesc_base_value) = (PROP_VALUE (DIRECT (PINT 3)))
        $property_default_state(S_front,ppropertydesc_getter) = (PROP_VALUE (DIRECT (PINT 7)))
        ppropertydesc_base_value.ORIGIN =/= ppropertydesc_getter.ORIGIN
        $property_hook_backed_over_ordinary(S_front,ppropertydesc_base_value,ppropertydesc_getter)
        ''')
    if case == 'parented-typed-latest':
        checks += chain.lines('''
        pclassdesc_base.CONSTANTS = [pclassconstantdesc_base]
        pclassconstantdesc_base.NAME = $ptascii("TAG")
        pclassconstantdesc_base.OWNER = porigin_base
        ''')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--group', choices=list(CONFIG))
    args = parser.parse_args()
    assert sha(CATALOGUE) == FROZEN
    data = json.loads(CATALOGUE.read_text())
    expected = json.loads(EXPECTATIONS.read_text())
    assert expected['catalogue_sha256'] == FROZEN
    php = ROOT / '.tools/php/bin/php'
    profile = HERE / 'profile.json'
    assert sha(php) == expected['oracle_sha256']
    assert sha(profile) == expected['native_profile_sha256']
    flags = [part for key, value in json.loads(profile.read_text()).items()
             for part in ('-d', key + '=' + value)]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='reference-get-parented-', dir=ROOT / '.tools'))
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'catalogue_sha256': FROZEN, 'expectations_sha256': sha(EXPECTATIONS),
              'semantic_sha256': sha(ROOT / 'spec/semantics/382-backed-get-hooks.watsup'),
              'protocol_sha256': sha(Path(__file__)), 'source_only': args.source_only,
              'selected_group': args.group, 'groups': [], 'passed': False}
    print(out, flush=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    for case in data['cases']:
        if args.group and case['id'] != args.group:
            continue
        key = case['id']
        source = out / (key + '.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        native = chain.old.base.run([str(php), '-n', *flags, str(source)], out / (key + '-native'), 25)
        entry = expected['cases'][key]
        assert native.returncode == entry['exit_status']
        assert base64.b64encode(native.stdout).decode() == entry['stdout_base64']
        assert base64.b64encode(native.stderr).decode() == entry['stderr_base64']
        model = chain.old.base.run([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '75'], out / (key + '-model'), 90)
        outcome = json.loads(model.stdout)
        row = {'group': key, 'source_sha256': sha(source), 'native_exit': native.returncode,
               'model_status': outcome['status'], 'source_agreement': False, 'state': None}
        assert model.stderr == b'' and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
        assert model.returncode == 0 and outcome['status'] == 'normal'
        assert outcome['exit_status'] == native.returncode
        assert base64.b64decode(outcome['stdout']) == native.stdout
        assert base64.b64decode(outcome['stderr']) == native.stderr
        row['source_agreement'] = True
        if not args.source_only:
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], out / (key + '-frontend'))
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / (key + '-adapter'))
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                adapter.close()
            checks = conditions(key, checked['fixture'], source, entry)
            fixture = out / (key + '-state.watsup')
            fixture.write_text(chain.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- ' + ('' if item.startswith('PhpStep:') else 'if ') + item + '\n'
                                       for item in checks))
            compiler = chain.old.base.run([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
                                           *map(str, modules), str(fixture)], out / (key + '-algo'), 120)
            assert compiler.returncode == 0 and compiler.stderr == b'' and b'\ndef $main : bool =\n' in compiler.stdout
            state = chain.old.base.run([str(HERE / '_build/default/numeric_runner.exe'), '--sl',
                                        *map(str, modules), str(fixture)], out / (key + '-state'), 120)
            assert state.returncode == 0 and state.stderr == b'' and state.stdout == b'true\n'
            row['state'] = {'premises': len(checks), 'raw_steps': sum(item.startswith('PhpStep:') for item in checks),
                            'fixture_sha256': sha(fixture), 'result': 'true'}
        report['groups'].append(row)
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(key, row, flush=True)
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
