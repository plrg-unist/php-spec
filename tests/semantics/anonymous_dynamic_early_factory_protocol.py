#!/usr/bin/env python3
"""Parentless later-unit factory publication before runtime calls or Closure creation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_dynamic_site_cases.json'
SOURCE_SHA = '920d7762902cb3e878a83a9ee1882309a8bc53e1debcaf0fe17956ba828f121c'

PREFIX = r'''
dec $placement149_output_item(pevent) : ptbytes
def $placement149_output_item(OUTPUT ptbytes) = ptbytes
def $placement149_output_item(pevent) = eps -- otherwise
dec $placement149_output(pevent*) : ptbytes
def $placement149_output(eps) = eps
def $placement149_output(pevent :: pevent_tail*) = $placement149_output_item(pevent) ++ $placement149_output(pevent_tail*)
'''



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    file = filename + b"(4) : eval()'d code"
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.EVALCONTEXTS = pevalcontext :: eps',
        'pevalcontext.UNIT = 1',
        'pevalcontext.BYTES = ' + term(codes[0]),
        'pevalcontext.FILE = ' + term(file),
        '$eval_response_valid(S_wait,' + responses[0] + ')',
        'S_ready = $eval_resume(S_wait,' + responses[0] + ')',
        'S_ready.COMPLETION = NORMAL',
        '$declaration_unit_complete(S_ready.DECLARATIONS,1)',
        'S_ready.OBJECTS = eps',
        'S_ready.CLOSUREBINDINGS = eps',
        '$placement149_output(S_ready.EVENTS) = ' + term(b'outer|'),
        '$source_unit(S_ready.SOURCES,1) = (pcunit)',
        '$compilation_projection(S_ready,pcunit) = (ppinstalled)',
        'ppinstalled.CLASSES = [pclassdesc_named,pclassdesc_closure,pclassdesc_outside]',
        'S_ready.CLASSES = ppinstalled.CLASSES',
        '$anonymous_history_seed(S_ready,1) = (0)',
        '$anonymous_rtd_count(S_ready,pcunit) = (3)',
    ]
    for symbol, line, counter in [('named',3,0),('closure',9,1),('outside',14,2)]:
        checks += [
            'pclassdesc_' + symbol + '.NAME = ' + term(b'class@anonymous\0' + file + b':' + str(line).encode() + b'$' + str(counter).encode()),
            'pclassdesc_' + symbol + '.EARLY',
            'pclassdesc_' + symbol + '.PARENT = eps',
            'pclassdesc_' + symbol + '.INTERFACES = eps',
            '$class_named(S_ready.CLASSNAMES,$ptlc(pclassdesc_' + symbol + '.NAME)) = (pclassdesc_' + symbol + '.ORIGIN)',
            '$declaration_early(S_ready.DECLARATIONS,pclassdesc_' + symbol + '.ORIGIN,PPCLASS)',
            '$anonymous_new_available(S_ready,pclassdesc_' + symbol + ')',
            '~$anonymous_runtime_declaration(S_ready.DECLARATIONS,pclassdesc_' + symbol + '.ORIGIN)',
        ]
    checks += [
        '$call_descriptors_valid(S_ready)',
        '$class_state_valid(S_ready)',
        '$heap_valid($heap_graph(S_ready))',
        'S_done = $drive_steps(S_ready,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$placement149_output(S_done.EVENTS) = ' + term(stdout),
        'S_done.DECLARATIONS = S_ready.DECLARATIONS',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$declaration_entry_check(S_done) = S_done',
        '$heap_valid($heap_graph(S_done))',
    ]
    return checks


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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-early-factory-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'namespace Review149Early;')]:
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
                                       *map(str, modules), str(fixture)], raw / 'numeric', 1800, ROOT)
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
