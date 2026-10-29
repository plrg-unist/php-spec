#!/usr/bin/env python3
"""Compiler-visited anonymous sites, raw counters and uncompiled-site rejection."""
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
SOURCE_SHA = 'd9134d9aa638c9a2b5e1ddfadc875bbe62ca414420b925a04e607b504e31af4a'

PREFIX = r'''
dec $placement149_output_item(pevent) : ptbytes
def $placement149_output_item(OUTPUT ptbytes) = ptbytes
def $placement149_output_item(pevent) = eps -- otherwise
dec $placement149_output(pevent*) : ptbytes
def $placement149_output(eps) = eps
def $placement149_output(pevent :: pevent_tail*) = $placement149_output_item(pevent) ++ $placement149_output(pevent_tail*)
dec $placement149_class_line(pcnode,int) : bool
def $placement149_class_line(NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata,z) = ($source_line(metadata) = z)
def $placement149_class_line(pcnode,z) = false -- otherwise
dec $placement149_path(pcoccurrence*,int) : pcpath?
def $placement149_path(eps,z) = eps
def $placement149_path((PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*,z) = (pcpath)
  -- if $placement149_class_line(pcnode,z)
def $placement149_path((PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*,z) = $placement149_path(pcoccurrence_tail*,z)
  -- if ~$placement149_class_line(pcnode,z)
'''



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    file = filename + b"(4) : eval()'d code"
    def name(prefix, line, counter):
        return term(prefix + b'@anonymous\0' + file + b':' + str(line).encode() + b'$' + str(counter).encode())
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
        'S_body = $eval_resume(S_wait,' + responses[0] + ')',
        'S_body.COMPLETION = NORMAL',
        'S_done = $drive_steps(S_body,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$placement149_output(S_done.EVENTS) = ' + term(stdout),
        '$source_unit(S_done.SOURCES,0) = (pcunit_root)',
        '$source_unit(S_done.SOURCES,1) = (pcunit)',
        '$declaration_unit_complete(S_done.DECLARATIONS,1)',
        '$anonymous_history_seed(S_done,1) = (0)',
        '$anonymous_rtd_unit(pcunit) = (8)',
        '$anonymous_rtd_count(S_done,pcunit_root) = (0)',
        '$anonymous_rtd_count(S_done,pcunit) = (6)',
        '$compilation_projection(S_done,pcunit) = (ppinstalled)',
        'ppinstalled.CLASSES = [pclassdesc_one,pclassdesc_two,pclassdesc_coalesce,pclassdesc_three,pclassdesc_branch,pclassdesc_four]',
        'S_done.CLASSES = ppinstalled.CLASSES',
        '$class_constant_compile_entry(S_done,1) = (S_entry)',
        '$anonymous_compiled_class_count(pcunit,pevalcontext.FILE,ppinstalled.CLASSES,eps,(S_entry),0) = (6)',
    ]
    for symbol, line, counter in [('one',4,0),('two',7,1),('three',10,3),('four',16,5)]:
        checks += [
            'pclassdesc_' + symbol + '.NAME = ' + name(b'class',line,counter),
            'pclassdesc_' + symbol + '.EARLY',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_' + symbol + '.NAME)) = (pclassdesc_' + symbol + '.ORIGIN)',
            '$anonymous_new_available(S_done,pclassdesc_' + symbol + ')',
        ]
    for symbol, parent, line, counter in [('coalesce',b'Review149Counter\\MissingCoalesce149',9,2),('branch',b'Review149Counter\\MissingBranch149',14,4)]:
        checks += [
            'pclassdesc_' + symbol + '.NAME = ' + name(parent,line,counter),
            'pclassdesc_' + symbol + '.PARENT = (' + term(parent) + ')',
            '~pclassdesc_' + symbol + '.EARLY',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_' + symbol + '.NAME)) = eps',
            '$class_link_at(S_done.LINKEDPARENTS,pclassdesc_' + symbol + '.ORIGIN) = eps',
            '~$anonymous_runtime_declaration(S_done.DECLARATIONS,pclassdesc_' + symbol + '.ORIGIN)',
        ]
    checks += [
        '$placement149_path(pcunit.OCCURRENCES,3) = (pcpath_and)',
        '$placement149_path(pcunit.OCCURRENCES,6) = (pcpath_or)',
        '$anonymous_rtd_site(pcunit,pcpath_and)',
        '$anonymous_rtd_site(pcunit,pcpath_or)',
        '$class_at(ppinstalled.CLASSES,PORIGIN 1 pcpath_and) = eps',
        '$class_at(ppinstalled.CLASSES,PORIGIN 1 pcpath_or) = eps',
        'pcpath_and_new = pcpath_and[0:$nabs($(|pcpath_and| - 1))]',
        'pcpath_or_new = pcpath_or[0:$nabs($(|pcpath_or| - 1))]',
        '$anonymous_new_descriptor(S_done,PORIGIN 1 pcpath_and_new) = eps',
        '$anonymous_new_descriptor(S_done,PORIGIN 1 pcpath_or_new) = eps',
        '$class_state_valid(S_done)',
        'pclassdesc_forged = pclassdesc_coalesce[.ORIGIN = PORIGIN 1 pcpath_and][.NAME = ' + name(b'Review149Counter\\MissingAnd149',3,6) + '][.LINE = 3][.PARENT = (' + term(b'Review149Counter\\MissingAnd149') + ')]',
        'S_forged = S_done[.CLASSES = S_done.CLASSES ++ [pclassdesc_forged]]',
        '$anonymous_new_descriptor(S_forged,PORIGIN 1 pcpath_and_new) = eps',
        '~$class_state_valid(S_forged)',
        '$call_descriptors_valid(S_done)',
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-placement-protocol-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'namespace Review149Counter;')]:
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
