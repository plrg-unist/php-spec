#!/usr/bin/env python3
"""Check exact lexical import contexts, named RTD replay and anonymous identities."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_namespace_dependency_cases.json'
CASES = {'anonymous-namespace-dependency-mixed-namespace-alias-identities'}
PREFIX = r'''
dec $namespace_dependency_is_output(pevent) : bool
def $namespace_dependency_is_output(OUTPUT ptbytes) = true
def $namespace_dependency_is_output(pevent) = false -- otherwise
dec $namespace_dependency_output(pevent*) : ptbytes
def $namespace_dependency_output(eps) = eps
def $namespace_dependency_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $namespace_dependency_output(pevent*)
def $namespace_dependency_output(pevent :: pevent_tail*) = $namespace_dependency_output(pevent_tail*)
  -- if ~$namespace_dependency_is_output(pevent)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, fixture, filename, stdout):
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$namespace_dependency_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$source_unit(S_initial.SOURCES,0) = (pcunit)',
        'S_initial.CLASSES = [pclassdesc_contract_first,pclassdesc_contract_second,pclassdesc_base,pclassdesc_named,pclassdesc_first,pclassdesc_second,pclassdesc_third]',
        'S_done.CLASSES = S_initial.CLASSES',
        'pclassdesc_named.NAME = $ptascii("Review147Use\\\\Deferred147")',
        'pclassdesc_named.INTERFACES = [$ptascii("Review147Vendor\\\\First147")]',
        '~pclassdesc_named.EARLY',
        'pclassdesc_named.ORIGIN = PORIGIN 0 pcpath_named',
        'pclassdesc_first.ORIGIN = PORIGIN 0 pcpath_first',
        'pclassdesc_second.ORIGIN = PORIGIN 0 pcpath_second',
        'pclassdesc_third.ORIGIN = PORIGIN 0 pcpath_third',
        '$plclasscontext(pcunit,pcpath_named,$base64(' + json.dumps(filename) + '),pclassdesc_named.LINE) = (ptcontext_named)',
        '$plclasscontext(pcunit,pcpath_first,$base64(' + json.dumps(filename) + '),pclassdesc_first.LINE) = (ptcontext_first)',
        '$plclasscontext(pcunit,pcpath_second,$base64(' + json.dumps(filename) + '),pclassdesc_second.LINE) = (ptcontext_second)',
        '$plclasscontext(pcunit,pcpath_third,$base64(' + json.dumps(filename) + '),pclassdesc_third.LINE) = (ptcontext_third)',
        'ptcontext_named.NAMESPACE = $ptascii("Review147Use")',
        'ptcontext_named.IMPORTS = [($ptascii("contract147"),$ptascii("Review147Vendor\\\\First147"))]',
        'ptcontext_first.NAMESPACE = $ptascii("Review147Use")',
        'ptcontext_first.IMPORTS = ptcontext_named.IMPORTS',
        'ptcontext_second.NAMESPACE = $ptascii("Review147Use")',
        'ptcontext_second.IMPORTS = [($ptascii("contract147"),$ptascii("Review147Vendor\\\\Base147"))]',
        'ptcontext_third.NAMESPACE = eps',
        'ptcontext_third.IMPORTS = [($ptascii("contract147"),$ptascii("Review147Vendor\\\\Second147"))]',
        '$occurrence_node(pcunit.OCCURRENCES,pcpath_named) = (pcnode_named)',
        '$anonymous_named_header(pcnode_named,ptcontext_named) = ((pchheader_named,z_line_named))',
        'pchheader_named.NAME = pclassdesc_named.NAME',
        'pchheader_named.INTERFACES = pclassdesc_named.INTERFACES',
        'pclassdesc_first.PARENT = eps',
        'pclassdesc_first.INTERFACES = [$ptascii("Review147Vendor\\\\First147")]',
        'pclassdesc_second.PARENT = ($ptascii("Review147Vendor\\\\Base147"))',
        'pclassdesc_second.INTERFACES = eps',
        'pclassdesc_third.PARENT = eps',
        'pclassdesc_third.INTERFACES = [$ptascii("Review147Vendor\\\\Second147")]',
        'pclassdesc_first.NAME = $ptascii("Review147Vendor\\\\First147@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":11$1")',
        'pclassdesc_second.NAME = $ptascii("Review147Vendor\\\\Base147@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":19$2")',
        'pclassdesc_third.NAME = $ptascii("Review147Vendor\\\\Second147@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":24$3")',
        '$anonymous_class_count(pcunit,$base64(' + json.dumps(filename) + '),S_initial.CLASSES,eps,0) = (4)',
        '$reference_origin_parent(pclassdesc_first.ORIGIN,1) = ((porigin_first,[PCFIELD 0]))',
        '$anonymous_new_descriptor(S_initial,porigin_first) = (pclassdesc_first)',
        '$class_named(S_initial.CLASSNAMES,$ptlc(pclassdesc_first.NAME)) = eps',
        '$anonymous_new_available(S_done,pclassdesc_first)',
        '$anonymous_new_available(S_done,pclassdesc_second)',
        '$anonymous_new_available(S_done,pclassdesc_third)',
        '$(|S_done.OBJECTS| = 3)',
        '$class_state_valid(S_initial)',
        'pclassdesc_wrong = pclassdesc_first[.INTERFACES = [$ptascii("Review147Vendor\\\\Second147")]][.NAME = $ptascii("Review147Vendor\\\\Second147@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":11$1")]',
        'S_wrong = S_initial[.CLASSES = [pclassdesc_contract_first,pclassdesc_contract_second,pclassdesc_base,pclassdesc_named,pclassdesc_wrong,pclassdesc_second,pclassdesc_third]]',
        '$anonymous_class_count(pcunit,$base64(' + json.dumps(filename) + '),S_wrong.CLASSES,eps,0) = eps',
        '$anonymous_new_descriptor(S_wrong,porigin_first) = eps',
        '~$class_state_valid(S_wrong)',
        '$class_state_valid(S_done)',
        '$call_descriptors_valid(S_done)',
        '$declaration_entry_check(S_done) = S_done',
        '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    raw = Path(tempfile.mkdtemp(prefix='anonymous-namespace-dependency-protocol-', dir=ROOT / '.tools'))
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
                                           *map(str, modules), str(fixture)], directory / 'numeric', 600, ROOT)
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
