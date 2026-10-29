#!/usr/bin/env python3
"""Source-entry visibility and request-wide anonymous class RTD counters."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_dynamic_dependency_cases.json'
SOURCE_SHA = '05f8c5101d71eed694d97d8d913eed33152c3caa70e750547203b27a68426ec8'

PREFIX = r'''
dec $counter148_output_item(pevent) : ptbytes
def $counter148_output_item(OUTPUT ptbytes) = ptbytes
def $counter148_output_item(pevent) = eps -- otherwise
dec $counter148_output(pevent*) : ptbytes
def $counter148_output(eps) = eps
def $counter148_output(pevent :: pevent_tail*) = $counter148_output_item(pevent) ++ $counter148_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    base = term(b'Review148RootBase')
    named = term(b'Review148Counter\\Named')
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_wait1 = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait1.COMPLETION = SOURCE_PENDING',
        'S_wait1.EVALCONTEXTS = pevalcontext_first :: eps',
        'pevalcontext_first.UNIT = 1',
        'pevalcontext_first.BYTES = ' + term(codes[0]),
        'pevalcontext_first.FILE = ' + term(filename) + ' ++ $ptascii("(5) : eval()\'d code")',
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_body1 = $eval_resume(S_wait1,' + responses[0] + ')',
        'S_body1.COMPLETION = NORMAL',
        'S_wait2 = $drive_steps(S_body1,4096)',
        'S_wait2.COMPLETION = SOURCE_PENDING',
        'S_wait2.EVALCONTEXTS = pevalcontext_second :: eps',
        'pevalcontext_second.UNIT = 2',
        'pevalcontext_second.BYTES = ' + term(codes[1]),
        'pevalcontext_second.FILE = ' + term(filename) + ' ++ $ptascii("(6) : eval()\'d code")',
        '$source_unit(S_wait2.SOURCES,0) = (pcunit_root)',
        '$source_unit(S_wait2.SOURCES,1) = (pcunit_first)',
        '$class_constant_compile_entry(S_wait2,1) = (S_entry1)',
        '$ppclass_external_known((S_entry1),' + base + ')',
        '$class_named(S_entry1.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        '$class_at(S_entry1.CLASSES,porigin_base) = (pclassdesc_base)',
        'pclassdesc_base.NAME = ' + base,
        'S_entry_hidden = S_entry1[.CLASSNAMES = eps]',
        '$class_at(S_entry_hidden.CLASSES,porigin_base) = (pclassdesc_base)',
        '~$ppclass_external_known((S_entry_hidden),' + base + ')',
        '$compilation_projection(S_wait2,pcunit_first) = (ppinstalled_first)',
        'ppinstalled_first.CLASSES = [pclassdesc_named,pclassdesc_inside]',
        'pclassdesc_named.NAME = ' + named,
        'pclassdesc_named.PARENT = (' + base + ')',
        'pclassdesc_named.EARLY',
        'pclassdesc_inside.PARENT = (' + named + ')',
        '~pclassdesc_inside.EARLY',
        'pclassdesc_inside.NAME = ' + named + ' ++ $ptascii("@anonymous") ++ [0] ++ pevalcontext_first.FILE ++ $ptascii(":1$1")',
        '$class_named(S_wait2.CLASSNAMES,$ptlc(pclassdesc_named.NAME)) = (pclassdesc_named.ORIGIN)',
        '$class_link_at(S_wait2.LINKEDPARENTS,pclassdesc_named.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$class_link_at(S_wait2.LINKEDPARENTS,pclassdesc_inside.ORIGIN) = (SOURCE_PARENT pclassdesc_named.ORIGIN)',
        '$anonymous_history_seed(S_wait2,1) = (1)',
        '$anonymous_rtd_count(S_wait2,pcunit_root) = (1)',
        '$anonymous_rtd_count(S_wait2,pcunit_first) = (1)',
        '$anonymous_compiled_class_count(pcunit_first,pevalcontext_first.FILE,ppinstalled_first.CLASSES,eps,(S_entry1),1) = (2)',
        '$anonymous_compiled_class_count(pcunit_first,pevalcontext_first.FILE,[pclassdesc_named],eps,(S_entry1),1) = (1)',
        '$class_state_valid(S_wait2)',
        '$anonymous_compiled_class_count(pcunit_first,pevalcontext_first.FILE,ppinstalled_first.CLASSES,eps,(S_entry_hidden),1) = eps',
        '$anonymous_compiled_class_count(pcunit_first,pevalcontext_first.FILE,ppinstalled_first.CLASSES,eps,(S_entry1),0) = eps',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_body2 = $eval_resume(S_wait2,' + responses[1] + ')',
        'S_done = $drive_steps(S_body2,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$source_unit(S_done.SOURCES,2) = (pcunit_second)',
        '$compilation_projection(S_done,pcunit_second) = (ppinstalled_second)',
        'ppinstalled_second.CLASSES = [pclassdesc_tail]',
        'pclassdesc_tail.NAME = $ptascii("class@anonymous") ++ [0] ++ pevalcontext_second.FILE ++ $ptascii(":1$2")',
        '$anonymous_history_seed(S_done,2) = (2)',
        '$anonymous_rtd_count(S_done,pcunit_second) = (1)',
        '$counter148_output(S_done.EVENTS) = ' + term(stdout),
        '$class_state_valid(S_initial)',
        '$class_state_valid(S_done)',
        '$call_descriptors_valid(S_done)',
        '$declaration_entry_check(S_done) = S_done',
        '$heap_valid($heap_graph(S_done))',
    ]


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-dependency-protocol-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64'] if 'stdout_template_base64' in row else row['stdout_base64']).replace(b'{FILE}', os.fsencode(source))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source,
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': SOURCE_SHA, 'inputs_before': before, 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        codes, responses = [], []
        for unit, prefix in [(1, b'namespace Review148Counter;'), (2, b'$tail = new class')]:
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                     if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(prefix)]
            codes.append(code)
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                                            'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            assert parsed_eval['accepted'] is True
            checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
            assert checked_eval['ok'] is True
            responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked_eval['fixture'])
        checks = assertions(checked['fixture'], os.fsencode(source), stdout, codes, responses)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *map(str, modules), str(fixture)], raw / 'numeric', 600, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, conditions=len(checks), fixture_sha256=sha(fixture))
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
