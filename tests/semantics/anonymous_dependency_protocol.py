#!/usr/bin/env python3
"""Check skipped unresolved identities and ordinary named-class RTD metadata."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_dependency_cases.json'
CASES = {'anonymous-dependency-skipped-unresolved-parent-type',
         'anonymous-dependency-unused-magic-full-identity'}
PREFIX = r'''
dec $dependency_is_output(pevent) : bool
def $dependency_is_output(OUTPUT ptbytes) = true
def $dependency_is_output(pevent) = false -- otherwise
dec $dependency_output(pevent*) : ptbytes
def $dependency_output(eps) = eps
def $dependency_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dependency_output(pevent*)
def $dependency_output(pevent :: pevent_tail*) = $dependency_output(pevent_tail*)
  -- if ~$dependency_is_output(pevent)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, fixture, filename, stdout):
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$dependency_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
    ]
    if case == 'anonymous-dependency-skipped-unresolved-parent-type':
        checks += [
            'S_initial.CLASSES = [pclassdesc]',
            'S_done.CLASSES = S_initial.CLASSES',
            'S_done.CLASSNAMES = S_initial.CLASSNAMES',
            'S_done.DECLARATIONS = S_initial.DECLARATIONS',
            'S_done.LINKEDPARENTS = eps',
            'S_done.LINKEDINTERFACES = eps',
            'S_done.OBJECTS = eps',
            'S_done.ALLOCATIONS = S_initial.ALLOCATIONS',
            'pclassdesc.KIND = "class"',
            '~pclassdesc.EARLY',
            'pclassdesc.PARENT = ($ptascii("Review146MissingBase"))',
            'pclassdesc.INTERFACES = [$ptascii("Review146MissingRead")]',
            'pclassdesc.LINE = 4',
            'pclassdesc.NAME = $ptascii("Review146MissingBase@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":4$0")',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
            '$class_named(S_done.CLASSNAMES,$ptlc($ptascii("Review146MissingBase"))) = eps',
            '$class_named(S_done.CLASSNAMES,$ptlc($ptascii("Review146MissingRead"))) = eps',
            '$reference_origin_parent(pclassdesc.ORIGIN,1) = ((porigin_new,[PCFIELD 0]))',
            '$origin_node(S_done.SOURCES,porigin_new) = (NExprNew phpType28 (SEQUENCE eps) metadata)',
            '$anonymous_new_descriptor(S_done,porigin_new) = (pclassdesc)',
            '$anonymous_new_pending(S_done,porigin_new) = (pclassdesc)',
            '~$anonymous_dependencies_ready(S_done,pclassdesc)',
            '~$anonymous_new_available(S_done,pclassdesc)',
            '$ppproperty_desc_at(pclassdesc.PROPERTIES,$ptascii("parentSlot")) = (ppropertydesc_parent)',
            'ppropertydesc_parent.TYPE = [PTBRANCH ([PTCLASS $ptascii("Review146MissingBase")])]',
            'ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED',
            'S_wrong = S_done[.CLASSES = [pclassdesc[.PARENT = ($ptascii("OtherMissing"))]]]',
            '$anonymous_new_descriptor(S_wrong,porigin_new) = eps',
            '~$class_state_valid(S_wrong)',
        ]
    else:
        checks += [
            'S_initial.CLASSES = [pclassdesc_string,pclassdesc_destructor,pclassdesc_anonymous]',
            'S_done.CLASSES = S_initial.CLASSES',
            'pclassdesc_string.NAME = $ptascii("Review146UnusedString")',
            'pclassdesc_string.INTERFACES = [$ptascii("Stringable")]',
            '~pclassdesc_string.EARLY',
            '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_string.NAME)) = eps',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_string.NAME)) = (pclassdesc_string.ORIGIN)',
            'pclassdesc_destructor.NAME = $ptascii("Review146UnusedDestructor")',
            'pclassdesc_destructor.INTERFACES = eps',
            'pclassdesc_destructor.EARLY',
            'pclassdesc_anonymous.PARENT = eps',
            'pclassdesc_anonymous.INTERFACES = eps',
            'pclassdesc_anonymous.EARLY',
            'pclassdesc_anonymous.LINE = 4',
            'pclassdesc_anonymous.NAME = $ptascii("class@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":4$1")',
            '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_anonymous.NAME)) = (pclassdesc_anonymous.ORIGIN)',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_anonymous.NAME)) = (pclassdesc_anonymous.ORIGIN)',
            '$source_unit(S_done.SOURCES,0) = (pcunit)',
            '$anonymous_class_count(pcunit,$base64(' + json.dumps(filename) + '),S_done.CLASSES,eps,0) = (2)',
        ]
    return checks + [
        '$class_state_valid(S_initial)',
        '$class_state_valid(S_done)',
        '$call_descriptors_valid(S_done)',
        '$declaration_entry_check(S_done) = S_done',
        '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dependency-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__), CATALOGUE,
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'records': [], 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        rows = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] in CASES]
        assert len(rows) == len(CASES) and {row['id'] for row in rows} == CASES
        for row in rows:
            directory = raw / row['id']
            directory.mkdir()
            source = directory / 'source.php'
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            stdout = base64.b64decode(row.get('stdout_template_base64',row['stdout_base64'])).replace(b'{FILE}',os.fsencode(source))
            checks = assertions(row['id'],checked['fixture'],base64.b64encode(os.fsencode(source)).decode(),stdout)
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           *map(str, modules), str(fixture)], directory / 'numeric', 180, ROOT)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['records'].append({'id': row['id'], 'pass': passed, 'conditions': len(checks),
                                      'source_sha256': sha(source), 'fixture_sha256': sha(fixture)})
            print(row['id'], passed, len(checks), flush=True)
            assert passed
        report['passed'] = True
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
