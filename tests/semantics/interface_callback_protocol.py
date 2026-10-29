#!/usr/bin/env python3
"""Reach valid source-interface publication before restricted class callbacks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/interface_callback_cases.json'
CASES = {'interface-callback-inherited-unit': ('ReviewUnitI', 'ReviewUnitC', 'UnitEnum', 1),
         'interface-callback-inherited-backed': ('ReviewBackedI', 'ReviewBackedC', 'BackedEnum', 3)}
PREFIX = r'''
dec $callback_is_output(pevent) : bool
def $callback_is_output(OUTPUT ptbytes) = true
def $callback_is_output(pevent) = false -- otherwise
dec $callback_output(pevent*) : ptbytes
def $callback_output(eps) = eps
def $callback_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $callback_output(pevent*)
def $callback_output(pevent :: pevent_tail*) = $callback_output(pevent_tail*)
  -- if ~$callback_is_output(pevent)
dec $callback_seek(pstate,nat) : pstate
def $callback_seek(S,n) = S -- if $callback_output(S.EVENTS) = $ptascii("BEFORE|")
def $callback_seek(S,0) = S -- if $callback_output(S.EVENTS) =/= $ptascii("BEFORE|")
def $callback_seek(S,n) = $callback_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ $callback_output(S.EVENTS) =/= $ptascii("BEFORE|")
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $callback_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(fixture, filename, interface, concrete, builtin, count):
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_found = $callback_seek(S_initial,4096)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_front = S_found[.COMPLETION = NORMAL]',
        '$callback_output(S_front.EVENTS) = $ptascii("BEFORE|")',
        '$class_named(S_front.CLASSNAMES,$ptlc($ptascii(' + json.dumps(interface) + '))) = (porigin_interface)',
        '$class_named(S_front.CLASSNAMES,$ptlc($ptascii(' + json.dumps(concrete) + '))) = eps',
        '$class_at(S_front.CLASSES,porigin_interface) = (pclassdesc)',
        'pclassdesc.KIND = "interface"',
        '~pclassdesc.EARLY',
        'pclassdesc.INTERFACES = [$ptascii(' + json.dumps(builtin) + ')]',
        '$pil_at(S_front.LINKEDINTERFACES,porigin_interface) = (PILTARGETS ([PILBUILTIN $ptascii(' + json.dumps(builtin) + ')]))',
        '$pil_targets_valid(S_front,pclassdesc.INTERFACES,[(PILBUILTIN $ptascii(' + json.dumps(builtin) + '))])',
        '~$pil_targets_valid(S_front,[$ptascii("Exception")],[(PILBUILTIN $ptascii("Exception"))])',
        '$pil_type_headers(S_front,porigin_interface,$(|S_front.CLASSES| + 2)) = PILHEADERS pilmethod_headers*',
        '|pilmethod_headers*| = ' + str(count),
        '$pil_header_at(pilmethod_headers*,$ptascii("cases")) = (pilmethod_cases)',
        'pilmethod_cases.DECLARATION.OWNER = $ptascii("UnitEnum")',
        'pilmethod_cases.ORIGIN = eps',
        'pilmethod_cases.STATIC',
        'pilmethod_cases.ABSTRACT',
        'pilmethod_cases.VISIBILITY = PROPERTY_PUBLIC',
        '$declaration_entry_check(S_front) = S_front',
        '$class_state_valid(S_front)',
        '$call_descriptors_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    raw = Path(tempfile.mkdtemp(prefix='interface-callback-protocol-', dir=ROOT / '.tools'))
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
        assert len(rows) == len(CASES) and {row['id'] for row in rows} == set(CASES)
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
            checks = assertions(checked['fixture'], base64.b64encode(os.fsencode(source)).decode(), *CASES[row['id']])
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
