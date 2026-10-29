#!/usr/bin/env python3
"""Compiled trait/enum chronology, pruned declarations and authentic kind metadata."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_enum_cases.json'
SOURCE_SHA = '717beff3423b9c45dc5db156709345065dc54aaa1a37d79f034875c13f554994'

PREFIX = r'''
dec $counter150_output_item(pevent) : ptbytes
def $counter150_output_item(OUTPUT ptbytes) = ptbytes
def $counter150_output_item(pevent) = eps -- otherwise
dec $counter150_output(pevent*) : ptbytes
def $counter150_output(eps) = eps
def $counter150_output(pevent :: pevent_tail*) = $counter150_output_item(pevent) ++ $counter150_output(pevent_tail*)
dec $counter150_named(pcnode) : ptbytes?
def $counter150_named(NStmtTrait phpType14 (NIdentifier (BYTES text) metadata_name) phpType23 metadata) = ($base64(text))
def $counter150_named(NStmtEnum phpType14 (NIdentifier (BYTES text) metadata_name) phpType50 phpType42 phpType23 metadata) = ($base64(text))
def $counter150_named(pcnode) = eps -- otherwise
dec $counter150_path(pcoccurrence*,ptbytes) : pcpath?
def $counter150_path(eps,ptbytes) = eps
def $counter150_path((PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*,ptbytes) = (pcpath)
  -- if $counter150_named(pcnode) = (ptbytes)
def $counter150_path((PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*,ptbytes) = $counter150_path(pcoccurrence_tail*,ptbytes)
  -- if $counter150_named(pcnode) =/= (ptbytes)
dec $counter150_replace(pclassdesc*,pclassdesc) : pclassdesc*
def $counter150_replace(eps,pclassdesc_new) = eps
def $counter150_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc_new :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $counter150_replace(pclassdesc :: pclassdesc_tail*,pclassdesc_new) = pclassdesc :: $counter150_replace(pclassdesc_tail*,pclassdesc_new)
  -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    file_one = filename + b"(3) : eval()'d code"
    file_two = filename + b"(13) : eval()'d code"
    def name(file, line, counter):
        return term(b'class@anonymous\0' + file + b':' + str(line).encode() + b'$' + str(counter).encode())
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext_one)',
        'pevalcontext_one.BYTES = ' + term(codes[0]),
        'pevalcontext_one.FILE = ' + term(file_one),
        '$eval_response_valid(S_wait,' + responses[0] + ')',
        'S_one = $eval_resume(S_wait,' + responses[0] + ')',
        'S_one.COMPLETION = NORMAL',
        'S_wait_two = $drive_steps(S_one,4096)',
        'S_wait_two.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_two.EVALCONTEXTS,2) = (pevalcontext_two)',
        'pevalcontext_two.BYTES = ' + term(codes[1]),
        'pevalcontext_two.FILE = ' + term(file_two),
        '$eval_response_valid(S_wait_two,' + responses[1] + ')',
        'S_two = $eval_resume(S_wait_two,' + responses[1] + ')',
        'S_two.COMPLETION = NORMAL',
        'S_done = $drive_steps(S_two,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$counter150_output(S_done.EVENTS) = ' + term(stdout),
        '$source_unit(S_done.SOURCES,0) = (pcunit_root)',
        '$source_unit(S_done.SOURCES,1) = (pcunit_one)',
        '$source_unit(S_done.SOURCES,2) = (pcunit_two)',
        '$declaration_unit_complete(S_done.DECLARATIONS,1)',
        '$declaration_unit_complete(S_done.DECLARATIONS,2)',
        '$anonymous_history_seed(S_done,1) = (0)',
        '$anonymous_history_seed(S_done,2) = (8)',
        '$anonymous_rtd_unit(pcunit_one) = (4)',
        '$anonymous_rtd_count(S_done,pcunit_root) = (0)',
        '$anonymous_rtd_count(S_done,pcunit_one) = (8)',
        '$anonymous_rtd_count(S_done,pcunit_two) = (1)',
        '$compilation_projection(S_done,pcunit_one) = (ppinstalled)',
        'ppinstalled.CLASSES = [pclassdesc_zero,pclassdesc_one,pclassdesc_coalesce,pclassdesc_backed,pclassdesc_four,pclassdesc_branch,pclassdesc_unit,pclassdesc_seven]',
        '$class_constant_compile_entry(S_done,1) = (S_entry)',
        '$anonymous_compiled_class_count(pcunit_one,' + term(file_one) + ',ppinstalled.CLASSES,eps,(S_entry),0) = (8)',
    ]
    for symbol, line, counter in [('zero',2,0),('one',4,1),('four',6,4),('seven',9,7)]:
        checks += [
            'pclassdesc_' + symbol + '.NAME = ' + name(file_one,line,counter),
            'pclassdesc_' + symbol + '.EARLY',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_' + symbol + '.NAME)) = (pclassdesc_' + symbol + '.ORIGIN)',
        ]
    for symbol, kind in [('coalesce','trait'),('backed','enum'),('branch','trait'),('unit','enum')]:
        checks += [
            'pclassdesc_' + symbol + '.KIND = ' + json.dumps(kind),
            '~pclassdesc_' + symbol + '.EARLY',
            '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_' + symbol + '.NAME)) = eps',
        ]
    checks += [
        'pclassdesc_coalesce.INTERFACES = eps',
        'pclassdesc_branch.INTERFACES = eps',
        'pclassdesc_backed.INTERFACES = [$ptascii("UnitEnum"),$ptascii("BackedEnum")]',
        'pclassdesc_unit.INTERFACES = [$ptascii("UnitEnum")]',
        '$compilation_projection(S_done,pcunit_two) = (ppinstalled_tail)',
        'ppinstalled_tail.CLASSES = [pclassdesc_tail]',
        'pclassdesc_tail.NAME = ' + name(file_two,1,8),
        'pclassdesc_tail.EARLY',
        '$class_state_valid(S_done)',
    ]
    for spelling in [b'DeadAnd150', b'DeadAndEnum150', b'DeadOr150', b'DeadOrEnum150']:
        checks += [
            '$counter150_path(pcunit_one.OCCURRENCES,' + term(spelling) + ') = (pcpath_pruned_' + spelling.decode().lower() + ')',
            '$class_at(ppinstalled.CLASSES,PORIGIN 1 pcpath_pruned_' + spelling.decode().lower() + ') = eps',
        ]
    checks += [
        '$anonymous_compiled_class_count(pcunit_one,' + term(file_one) + ',$counter150_replace(ppinstalled.CLASSES,pclassdesc_coalesce[.EARLY = true]),eps,(S_entry),0) = eps',
        '$anonymous_compiled_class_count(pcunit_one,' + term(file_one) + ',$counter150_replace(ppinstalled.CLASSES,pclassdesc_backed[.INTERFACES = [$ptascii("BackedEnum"),$ptascii("UnitEnum")]]),eps,(S_entry),0) = eps',
        '$anonymous_compiled_class_count(pcunit_one,' + term(file_one) + ',$counter150_replace(ppinstalled.CLASSES,pclassdesc_branch[.KIND = "class"]),eps,(S_entry),0) = eps',
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-enum-counter-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'false &&'), (2, b'echo (new class {})::class;')]:
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
                                       *map(str, modules), str(fixture)], raw / 'numeric', 900, ROOT)
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
