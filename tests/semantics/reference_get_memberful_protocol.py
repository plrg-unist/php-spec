"""Exact source and reached checks for memberful inherited reference Get."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import reference_get_chain_protocol as prior
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'reference_get_memberful_cases.json'
EXPECTATIONS = HERE / 'reference_get_memberful_expectations.json'
FROZEN = 'a8959d9c92a7ad362db8082355db38af7adae69efdb6a52446cc944834dc873e'
CONFIG = {
    'memberful-unchanged': ('LeafA139', 'ParentA139', 'ParentA139', 7, False, ['ChildA139', 'LeafA139']),
    'memberful-typed-redeclaration': ('LeafB139', 'ChildB139', 'ParentB139', 11, True, ['ChildB139', 'LeafB139']),
    'memberful-mixed-latest': ('LeafC139', 'LeafC139', 'ParentC139', 41, False, ['FirstC139', 'SecondC139', 'ThirdC139', 'LeafC139']),
    'memberful-rebind-error': ('LeafD139', 'MiddleD139', 'ParentD139', 11, False, ['ChildD139', 'MiddleD139', 'LeafD139']),
}
CHAINS = {
    'memberful-unchanged': [('ParentA139', None, True), ('ChildA139', 'ParentA139', False), ('LeafA139', 'ChildA139', False)],
    'memberful-typed-redeclaration': [('ParentB139', None, True), ('ChildB139', 'ParentB139', True), ('LeafB139', 'ChildB139', False)],
    'memberful-mixed-latest': [('ParentC139', None, True), ('FirstC139', 'ParentC139', False), ('SecondC139', 'FirstC139', True), ('ThirdC139', 'SecondC139', False), ('LeafC139', 'ThirdC139', True)],
    'memberful-rebind-error': [('ParentD139', None, True), ('ChildD139', 'ParentD139', False), ('MiddleD139', 'ChildD139', True), ('LeafD139', 'MiddleD139', False)],
}
SIBLINGS = {
    'memberful-unchanged': {'ChildA139': ['side', 'hidden'], 'LeafA139': ['leaf']},
    'memberful-typed-redeclaration': {'ChildB139': ['side'], 'LeafB139': ['hidden']},
    'memberful-mixed-latest': {'FirstC139': ['first'], 'SecondC139': ['hidden'], 'ThirdC139': ['third'], 'LeafC139': ['last']},
    'memberful-rebind-error': {'ChildD139': ['side'], 'MiddleD139': ['extra'], 'LeafD139': ['hidden']},
}
CONSTANTS = {
    'memberful-unchanged': {'ChildA139': 'TAG'},
    'memberful-typed-redeclaration': {'ChildB139': 'TAG'},
    'memberful-mixed-latest': {'FirstC139': 'FIRST', 'ThirdC139': 'THIRD'},
    'memberful-rebind-error': {'ChildD139': 'TAG'},
}
INTERFACES = {
    'memberful-unchanged': {'ChildA139': 'MarkA139'},
    'memberful-typed-redeclaration': {'ChildB139': 'MarkB139'},
    'memberful-mixed-latest': {'SecondC139': 'MarkC139'},
    'memberful-rebind-error': {'ChildD139': 'MarkD139'},
}
PREFIX = prior.PREFIX + r'''
dec $m139_named_property(ppropertydesc*, ptbytes) : ppropertydesc?
def $m139_named_property(eps, ptbytes) = eps
def $m139_named_property(ppropertydesc :: ppropertydesc_tail*, ptbytes) = (ppropertydesc)
  -- if ppropertydesc.NAME = ptbytes
def $m139_named_property(ppropertydesc :: ppropertydesc_tail*, ptbytes) = $m139_named_property(ppropertydesc_tail*, ptbytes)
  -- if ppropertydesc.NAME =/= ptbytes
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quote(value):
    return json.dumps(value)


def conditions(case, program, path, expected, source):
    old_case = 'deep-rebind-error' if case == 'memberful-rebind-error' else case
    prior.CONFIG[old_case] = CONFIG[case]
    checks = prior.conditions(old_case, program, path, expected)
    if case == 'memberful-rebind-error':
        line = next(i for i, text in enumerate(source.splitlines(), 1)
                    if '$object->value =& $replacement' in text)
        assert sum('ppropertyhook.LINE = 16' in text for text in checks) == 1
        assert sum(' 16]' in text for text in checks) == 1
        checks = [text.replace('ppropertyhook.LINE = 16', f'ppropertyhook.LINE = {line}')
                      .replace(' 16]', f' {line}]')
                      .replace('DEFINED (PINT 17)', 'DEFINED (PINT 23)')
                  for text in checks]
    for index, (name, parent, declared) in enumerate(CHAINS[case]):
        checks += prior.lines(f'''
        $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(name)}))) = (porigin_m{index})
        $class_at(S_front.CLASSES,porigin_m{index}) = (pclassdesc_m{index})
        $property_desc_at($property_layout(S_front,porigin_m{index},|S_front.CLASSES|),$ptascii("value")) = (ppropertydesc_m{index})
        ''')
        if parent:
            checks += prior.lines(f'''
            $class_link_at(S_front.LINKEDPARENTS,porigin_m{index}) = (SOURCE_PARENT porigin_m{index-1})
            ''')
        if index == 0:
            checks += prior.lines(f'''
            ppropertydesc_m0.ORIGIN = porigin_m0_property
            $hook_property_at(pclassdesc_m0.PROPERTIES,porigin_m0_property) = (ppropertydesc_m0)
            $property_hook_reference_decl(S_front,ppropertydesc_m0)
            ''')
        elif declared:
            checks += prior.lines(f'''
            $property_desc_at(pclassdesc_m{index}.PROPERTIES,$ptascii("value")) = (ppropertydesc_m{index})
            ppropertydesc_m{index}.ORIGIN = porigin_m{index}_property
            $hook_property_at(pclassdesc_m{index}.PROPERTIES,porigin_m{index}_property) = (ppropertydesc_m{index})
            $property_hook_plain_edge(S_front,ppropertydesc_m{index-1},ppropertydesc_m{index},|S_front.CLASSES|)
            ''')
        else:
            checks += prior.lines(f'''
            $property_desc_at(pclassdesc_m{index}.PROPERTIES,$ptascii("value")) = eps
            ppropertydesc_m{index} = ppropertydesc_m{index-1}
            ''')
        for sibling in SIBLINGS[case].get(name, []):
            tag = f'm{index}_{sibling}'
            checks += prior.lines(f'''
            $m139_named_property(pclassdesc_m{index}.PROPERTIES,$ptascii({quote(sibling)})) = (ppropertydesc_{tag})
            ppropertydesc_{tag}.NAME = $ptascii({quote(sibling)})
            ppropertydesc_{tag}.ORIGIN =/= ppropertydesc_m{index}.ORIGIN
            ''')
        if name in CONSTANTS[case]:
            checks += prior.lines(f'''
            pclassdesc_m{index}.CONSTANTS = [pclassconstantdesc_m{index}]
            pclassconstantdesc_m{index}.NAME = $ptascii({quote(CONSTANTS[case][name])})
            pclassconstantdesc_m{index}.OWNER = porigin_m{index}
            ''')
        if name in INTERFACES[case]:
            checks += prior.lines(f'''
            pclassdesc_m{index}.INTERFACES = [$ptascii({quote(INTERFACES[case][name])})]
            $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(INTERFACES[case][name])}))) = (porigin_marker_m{index})
            $class_at(S_front.CLASSES,porigin_marker_m{index}) = (pclassdesc_marker_m{index})
            pclassdesc_marker_m{index}.KIND = "interface"
            $pil_at(S_front.LINKEDINTERFACES,porigin_m{index}) = (PILTARGETS ([PILSOURCE $ptascii({quote(INTERFACES[case][name])}) porigin_marker_m{index}]))
            ''')
    checks += prior.lines(f'''
    ppropertydesc_m{len(CHAINS[case])-1} = ppropertydesc_storage
    ppropertydesc_m0 = ppropertydesc_getter
    ''')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--group', choices=list(CONFIG) + ['same-name-hook-control', 'changed-type-control'])
    args = parser.parse_args()
    assert sha(CATALOGUE) == FROZEN
    data = json.loads(CATALOGUE.read_text())
    expected = json.loads(EXPECTATIONS.read_text())
    assert expected['catalogue_sha256'] == FROZEN
    php = ROOT / '.tools/php/bin/php'
    assert sha(php) == expected['oracle_sha256']
    profile = HERE / 'profile.json'
    assert sha(profile) == expected['native_profile_sha256']
    flags = [part for key, value in json.loads(profile.read_text()).items()
             for part in ('-d', key + '=' + value)]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='reference-get-memberful-', dir=ROOT / '.tools'))
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
        source = out / (case['id'] + '.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        native = prior.old.base.run([str(php), '-n', *flags, str(source)], out / (case['id'] + '-native'), 25)
        entry = expected['cases'][case['id']]
        assert native.returncode == entry['exit_status']
        if case['id'] == 'changed-type-control':
            assert b'Type of ChildType139::$value must be int (as in class ParentType139)' in native.stderr
            assert str(source).encode() + b' on line 7' in native.stderr
        else:
            assert base64.b64encode(native.stdout).decode() == entry['stdout_base64']
            assert base64.b64encode(native.stderr).decode() == entry['stderr_base64']
        model = prior.old.base.run([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '75'], out / (case['id'] + '-model'), 90)
        outcome = json.loads(model.stdout)
        row = {'group': case['id'], 'source_sha256': sha(source), 'native_exit': native.returncode,
               'model_status': outcome['status'], 'source_agreement': False, 'state': None}
        assert model.stderr == b'' and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
        if case['kind'] == 'boundary':
            if case['id'] == 'changed-type-control':
                assert model.returncode == 0 and outcome['status'] == 'static_rejection'
                assert outcome['exit_status'] == 255 and outcome['stdout'] == ''
                assert outcome['diagnostic']['class'] == 'CompileError'
                assert base64.b64decode(outcome['diagnostic']['message']) == b'Type of ChildType139::$value must be int (as in class ParentType139)'
                assert outcome['diagnostic']['line'] == 7
                assert base64.b64decode(outcome['stderr']) == native.stderr
            else:
                assert model.returncode == 1 and outcome['status'] == 'unsupported'
                assert outcome['reason'] == 'set, by-reference, attributed or defaulted virtual property hook'
                assert outcome['stdout'] == '' and outcome['stderr'] == ''
            report['groups'].append(row)
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(case['id'], row, flush=True)
            continue
        assert model.returncode == 0 and outcome['status'] == 'normal'
        assert outcome['exit_status'] == native.returncode
        assert base64.b64decode(outcome['stdout']) == native.stdout
        assert base64.b64decode(outcome['stderr']) == native.stderr
        row['source_agreement'] = True
        if not args.source_only:
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / (case['id'] + '-frontend'))
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / (case['id'] + '-adapter'))
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                adapter.close()
            checks = conditions(case['id'], checked['fixture'], source, entry, case['source'])
            fixture = out / (case['id'] + '-state.watsup')
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + ('' if text.startswith('PhpStep:') else 'if ') + text + '\n' for text in checks))
            compiler = prior.old.base.run([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *map(str, modules), str(fixture)], out / (case['id'] + '-algo'), 120)
            assert compiler.returncode == 0 and compiler.stderr == b'' and b'\ndef $main : bool =\n' in compiler.stdout
            state = prior.old.base.run([str(HERE / '_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)], out / (case['id'] + '-state'), 120)
            assert state.returncode == 0 and state.stderr == b'' and state.stdout == b'true\n'
            row['state'] = {'premises': len(checks), 'raw_steps': sum(text.startswith('PhpStep:') for text in checks),
                            'fixture_sha256': sha(fixture), 'result': 'true'}
        report['groups'].append(row)
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(case['id'], row, flush=True)
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
