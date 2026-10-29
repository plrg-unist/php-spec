#!/usr/bin/env python3
"""Opened-file parser rejection, retained once hits and later class-key history."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_rejected_source_cases.json'
SOURCE_SHA = '02ccd5f840e45a9df1698fd594d888588fed0b285054c44b24cb4c489d13f098'

PREFIX = r'''
dec $rejected151_output_item(pevent) : ptbytes
def $rejected151_output_item(OUTPUT ptbytes) = ptbytes
def $rejected151_output_item(pevent) = eps -- otherwise
dec $rejected151_output(pevent*) : ptbytes
def $rejected151_output(eps) = eps
def $rejected151_output(pevent :: pevent_tail*) = $rejected151_output_item(pevent) ++ $rejected151_output(pevent_tail*)
dec $rejected151_entry(pdeclaration*,nat) : pdeclaration?
def $rejected151_entry(eps,n) = eps
def $rejected151_entry(pdeclaration :: pdeclaration_tail*,n) = (pdeclaration)
  -- if $anonymous_rtd_enter(pdeclaration) = (n)
def $rejected151_entry(pdeclaration :: pdeclaration_tail*,n) = $rejected151_entry(pdeclaration_tail*,n)
  -- if $anonymous_rtd_enter(pdeclaration) =/= (n)
dec $rejected151_site(pdeclaration,porigin) : pdeclaration
def $rejected151_site(PDENTER n porigin_old? z,porigin) = PDENTER n (porigin) z
def $rejected151_site(PDENTERPRECISION n porigin_old? z z_precision,porigin) = PDENTERPRECISION n (porigin) z z_precision
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, payloads, bad_response, good_response, tail_code, tail_response):
    bad, good = payloads
    def opened(symbol, path, code):
        return 'FILE_OPENED pfilecontext_' + symbol + '.NONCE pfilecontext_' + symbol + '.CALLER pfilecontext_' + symbol + '.REQUESTED ' + term(path) + ' ' + term(path) + ' ' + term(code)
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_file_run(program_source,0,' + term(filename) + ',' + term(os.fsencode(Path(os.fsdecode(filename)).parent)) + ')',
        '~S_initial.COMPILESTOP', 'S_initial.COMPLETION = BUDGET',
        'S_open_bad = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_open_bad.COMPLETION = SOURCE_PENDING',
        'S_open_bad.FILECONTEXTS = pfilecontext_bad :: eps',
        'pfilecontext_bad.REQUESTED = ' + term(bad[0]),
        '$file_open_response_valid(S_open_bad,' + opened('bad',*bad) + ')',
        'S_wait_bad = $file_open_resume(S_open_bad,' + opened('bad',*bad) + ')',
        'S_wait_bad.COMPLETION = SOURCE_PENDING',
        '$file_parse_response_valid(S_wait_bad,' + bad_response + ')',
        'S_bad = $file_parse_resume(S_wait_bad,' + bad_response + ')',
        'S_bad.COMPLETION = NORMAL',
        '$failed_source_at(S_bad.FAILEDSOURCES,1) = (pfailedsource)',
        'pfailedsource.ISFILE', 'pfailedsource.KIND = FAILED_PARSE',
        'pfailedsource.FILE = ' + term(bad[0]),
        'pfailedsource.BYTES = ' + term(bad[1]),
        'pfailedsource.LINE = 5',
        '$source_unit(S_bad.SOURCES,1) = eps', '$code_at(S_bad.CODE,1) = eps',
        '$file_binding_at(S_bad.FILEBINDINGS,1) = eps',
        '$eval_binding_at(S_bad.EVALBINDINGS,1) = eps',
        term(bad[0]) + ' <- S_bad.INCLUDEDOPENED',
        '$rejected151_entry(S_bad.DECLARATIONS,1) = (pdeclaration_bad)',
        '$anonymous_parser_rejected(S_bad,pdeclaration_bad,1)',
        'S_open_bad_two = $drive_steps(S_bad,4096)',
        'S_open_bad_two.COMPLETION = SOURCE_PENDING',
        'S_open_bad_two.FILECONTEXTS = pfilecontext_bad_two :: eps',
        'pfilecontext_bad_two.REQUESTED = ' + term(bad[0]),
        '$file_open_response_valid(S_open_bad_two,' + opened('bad_two',*bad) + ')',
        'S_skip_bad = $file_open_resume(S_open_bad_two,' + opened('bad_two',*bad) + ')',
        'S_skip_bad.COMPLETION = NORMAL',
        'S_skip_bad.RESULT = KNOWN (PBOOL true)',
        'S_skip_bad.FAILEDSOURCES = S_bad.FAILEDSOURCES',
        'S_skip_bad.DECLARATIONS = S_bad.DECLARATIONS',
        'S_skip_bad.FILES = S_bad.FILES',
        'S_open_good = $drive_steps(S_skip_bad,4096)',
        'S_open_good.COMPLETION = SOURCE_PENDING',
        'S_open_good.FILECONTEXTS = pfilecontext_good :: eps',
        'pfilecontext_good.REQUESTED = ' + term(good[0]),
        '$file_open_response_valid(S_open_good,' + opened('good',*good) + ')',
        'S_wait_good = $file_open_resume(S_open_good,' + opened('good',*good) + ')',
        'S_wait_good.COMPLETION = SOURCE_PENDING',
        '$file_parse_response_valid(S_wait_good,' + good_response + ')',
        'S_good = $file_parse_resume(S_wait_good,' + good_response + ')',
        'S_good.COMPLETION = NORMAL',
        '$anonymous_history_seed(S_good,2) = (0)',
        '$source_unit(S_good.SOURCES,2) = (pcunit_good)',
        '$code_at(S_good.CODE,2) = (pcode_good)',
        '$file_binding_at(S_good.FILEBINDINGS,2) = (pfilebinding_good)',
        '$class_state_valid(S_good)',
        '~$anonymous_parser_rejected(S_good[.FAILEDSOURCES = eps],pdeclaration_bad,1)',
        '~$anonymous_parser_rejected(S_good[.FILECWD = eps],pdeclaration_bad,1)',
        '~$anonymous_parser_rejected(S_good[.FAILEDSOURCES = [pfailedsource[.ISFILE = false]]],pdeclaration_bad,1)',
        '~$anonymous_parser_rejected(S_good,$rejected151_site(pdeclaration_bad,pfilecontext_good.SITE),1)',
        '~$anonymous_parser_rejected(S_good[.SOURCES = S_good.SOURCES ++ [pcunit_good[.ID = 1]]],pdeclaration_bad,1)',
        '~$anonymous_parser_rejected(S_good[.CODE = S_good.CODE ++ [pcode_good[.UNIT = 1]]],pdeclaration_bad,1)',
        '~$anonymous_parser_rejected(S_good[.FILEBINDINGS = S_good.FILEBINDINGS ++ [pfilebinding_good[.UNIT = 1]]],pdeclaration_bad,1)',
        '$anonymous_rtd_history(S_good,[pdeclaration_bad,(PDEXIT 1 PCSREJECT)],1,2,0) = (0)',
        '$anonymous_rtd_history(S_good,[pdeclaration_bad,(PDEXIT 1 PCSCOMPLETE)],1,2,0) = eps',
        '$anonymous_rtd_history(S_good,[pdeclaration_bad],1,2,0) = eps',
        'S_open_good_two = $drive_steps(S_good,4096)',
        'S_open_good_two.COMPLETION = SOURCE_PENDING',
        'S_open_good_two.FILECONTEXTS = pfilecontext_good_two :: eps',
        'pfilecontext_good_two.REQUESTED = ' + term(good[0]),
        '$file_open_response_valid(S_open_good_two,' + opened('good_two',*good) + ')',
        'S_skip_good = $file_open_resume(S_open_good_two,' + opened('good_two',*good) + ')',
        'S_skip_good.COMPLETION = NORMAL',
        'S_skip_good.RESULT = KNOWN (PBOOL true)',
        'S_skip_good.DECLARATIONS = S_open_good_two.DECLARATIONS',
        'S_skip_good.FILES = S_open_good_two.FILES',
        'S_eval = $drive_steps(S_skip_good,4096)',
        'S_eval.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_eval.EVALCONTEXTS,3) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(tail_code),
        '$eval_response_valid(S_eval,' + tail_response + ')',
        'S_tail = $eval_resume(S_eval,' + tail_response + ')',
        'S_tail.COMPLETION = NORMAL',
        '$anonymous_history_seed(S_tail,3) = (1)',
        'S_done = $drive_steps(S_tail,4096)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '$rejected151_output(S_done.EVENTS) = ' + term(stdout),
        '$source_unit(S_done.SOURCES,1) = eps',
        'S_done.SOURCES = [pcunit_root,pcunit_good,pcunit_tail]',
        'pcunit_root.ID = 0', 'pcunit_tail.ID = 3',
        '$anonymous_rtd_count(S_done,pcunit_root) = (0)',
        '$anonymous_rtd_count(S_done,pcunit_good) = (1)',
        '$anonymous_rtd_count(S_done,pcunit_tail) = (1)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$file_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-rejected-file-state-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    children = []
    stdout = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(source))
    for childrow in row['files']:
        child = raw / childrow['name']; child.write_bytes(childrow['source'].encode())
        assert sha(child) == childrow['source_sha256']
        children.append(child)
        stdout = stdout.replace(b'{FILE:' + childrow['name'].encode() + b'}', os.fsencode(child))
    assert sha(source) == SOURCE_SHA
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source, *children,
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
        child_by_name = {p.name:p for p in children}
        bad,good = child_by_name['bad.php'],child_by_name['good.php']
        responses=[]
        for unit,path in [(1,bad),(2,good)]:
            encoded=base64.b64encode(os.fsencode(path)).decode()
            parsed_child=frontend.request({'op':'parse-file','id':str(unit),'mode':'file','profile':'cli-raw-85',
                'source':base64.b64encode(path.read_bytes()).decode(),'requested':encoded,'resolved':encoded,'opened':encoded})
            if unit==1:
                assert parsed_child['accepted'] is False and parsed_child['category']=='parser_rejection'
                responses.append('SOURCE_PARSE_REJECT 1 '+term(path.read_bytes())+' '+term(base64.b64decode(parsed_child['message']))+' '+str(parsed_child['line']))
            else:
                assert parsed_child['accepted'] is True
                checked_child=adapter.request({'op':'check','ast':parsed_child['ast'],'fixture':True});assert checked_child['ok']
                responses.append('SOURCE_ACCEPT 2 '+term(path.read_bytes())+' '+checked_child['fixture'])
        tail_code=b'echo (new class {})::class;'
        parsed_tail=frontend.request({'op':'parse-eval','id':'3','mode':'eval','profile':'cli-raw-85','source':base64.b64encode(tail_code).decode()})
        assert parsed_tail['accepted'] is True
        checked_tail=adapter.request({'op':'check','ast':parsed_tail['ast'],'fixture':True});assert checked_tail['ok']
        tail_response='SOURCE_ACCEPT 3 '+term(tail_code)+' '+checked_tail['fixture']
        checks=assertions(checked['fixture'],os.fsencode(source),stdout,[(os.fsencode(bad),bad.read_bytes()),(os.fsencode(good),good.read_bytes())],responses[0],responses[1],tail_code,tail_response)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
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
