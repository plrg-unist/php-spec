#!/usr/bin/env python3
"""Real include factory try boundary and authenticated caller restoration."""
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
SOURCE_SHA = '6d7870336c348f8f048c71b45577bdb72ac936b8c7f97adc733cb89da0695802'

PREFIX = r'''
dec $boundary149_output_item(pevent) : ptbytes
def $boundary149_output_item(OUTPUT ptbytes) = ptbytes
def $boundary149_output_item(pevent) = eps -- otherwise
dec $boundary149_output(pevent*) : ptbytes
def $boundary149_output(eps) = eps
def $boundary149_output(pevent :: pevent_tail*) = $boundary149_output_item(pevent) ++ $boundary149_output(pevent_tail*)
dec $boundary149_front(pstate) : bool
def $boundary149_front(S) = true
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if $anonymous_new_descriptor(S,PORIGIN 1 pcpath) = (pclassdesc)
  -- if pclassdesc.LINE = 5 /\ pclassdesc.PARENT = ($ptascii("Review149FileBase"))
def $boundary149_front(S) = false -- otherwise
dec $boundary149_seek(pstate,nat) : pstate
def $boundary149_seek(S,n) = S -- if $boundary149_front(S)
def $boundary149_seek(S,0) = S -- if ~$boundary149_front(S)
def $boundary149_seek(S,n) = $boundary149_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$boundary149_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $boundary149_seek(S,n) = S -- otherwise
dec $boundary149_marker(ptask*) : porigin?
def $boundary149_marker(eps) = eps
def $boundary149_marker(ptask :: ptask_tail*) = (porigin)
  -- if $finally_marker_origin(ptask) = (porigin)
def $boundary149_marker(ptask :: ptask_tail*) = $boundary149_marker(ptask_tail*)
  -- if $finally_marker_origin(ptask) = eps
dec $boundary149_receipt(pdeclaration,porigin) : bool
def $boundary149_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $boundary149_receipt(pdeclaration,porigin) = false -- otherwise
dec $boundary149_bit(bool) : nat
def $boundary149_bit(true) = 1
def $boundary149_bit(false) = 0
dec $boundary149_count(pdeclaration*,porigin) : nat
def $boundary149_count(eps,porigin) = 0
def $boundary149_count(pdeclaration :: pdeclaration_tail*,porigin) = $($boundary149_bit($boundary149_receipt(pdeclaration,porigin)) + $boundary149_count(pdeclaration_tail*,porigin))
'''



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, code, response, child):
    opened = 'FILE_OPENED pfilecontext_open.NONCE pfilecontext_open.CALLER pfilecontext_open.REQUESTED ' + term(child) + ' ' + term(child) + ' ' + term(code)
    return [
        'program_source = ' + fixture,
        'S_initial = $php_file_run(program_source,0,' + term(filename) + ',' + term(os.fsencode(Path(os.fsdecode(filename)).parent)) + ')',
        '~S_initial.COMPILESTOP',
        'S_initial.COMPLETION = BUDGET',
        'S_open = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_open.COMPLETION = SOURCE_PENDING',
        'S_open.FILECONTEXTS = pfilecontext_open :: eps',
        'pfilecontext_open.REQUESTED = ' + term(child),
        '$file_open_response_valid(S_open,' + opened + ')',
        'S_wait = $file_open_resume(S_open,' + opened + ')',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$file_parse_response_valid(S_wait,' + response + ')',
        'S_body = $file_parse_resume(S_wait,' + response + ')',
        'S_body.COMPLETION = NORMAL',
        'S_front_raw = $boundary149_seek(S_body,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$boundary149_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_pending(S_front,PORIGIN 1 pcpath_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Review149FileBase@anonymous\0' + child + b':5$0'),
        '$class_named(S_front.CLASSNAMES,$ptascii("review149filebase")) = (porigin_base)',
        'S_front.CURRENT = (pcallcontext_factory)',
        'pcallcontext_factory.FUNCTION = PORIGIN 1 pcpath_factory',
        'S_front.FRAMES = pframe_outer :: eps',
        'S_saved = $constant_frame_scope(S_front,pframe_outer,eps)',
        '$boundary149_marker(S_saved.TODO) = (porigin_try)',
        'porigin_try = PORIGIN 1 pcpath_try',
        '$declaration_entry_site(S_saved.DECLARATIONS,1) = (porigin_entry)',
        'S_saved.FILECONTEXTS = pfilecontext_running :: eps',
        'pfilecontext_running.PHASE = FILE_UNIT_RUN',
        'pfilecontext_running.UNIT = (1)',
        'pfilecontext_running.SITE = porigin_entry',
        'pfilecontext_running.OWNER = |S_saved.FRAMES|',
        '$finally_current_complete(S_saved)',
        '$finally_outer_origin_valid(S_saved,porigin_try,(porigin_entry))',
        '~$finally_outer_origin_valid(S_saved[.FILECONTEXTS = eps],porigin_try,(porigin_entry))',
        '~$finally_outer_origin_valid(S_saved[.FILECONTEXTS = [pfilecontext_running[.OWNER = $(pfilecontext_running.OWNER + 1)]]],porigin_try,(porigin_entry))',
        '~$finally_outer_origin_valid(S_saved,porigin_try,(porigin_base))',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        'pdeclcause = $declaration_cause(S_front)',
        'pdeclcause.UNIT = 1',
        '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
        'S_linked_raw = $drive_steps(S_front,1)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        'S_linked.DECLARATIONS = S_front.DECLARATIONS ++ [PDRCLASS pclassdesc.ORIGIN pdeclcause]',
        'S_linked.OBJECTS = S_front.OBJECTS',
        'S_linked.EVENTS = S_front.EVENTS',
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$call_descriptors_valid(S_linked)',
        '$class_state_valid(S_linked)',
        'S_done = $drive_steps(S_linked,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        'S_done.FILECONTEXTS = eps',
        '$boundary149_output(S_done.EVENTS) = ' + term(stdout),
        '$boundary149_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$declaration_entry_check(S_done) = S_done',
        '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-file-boundary-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    child = raw / 'payload.php'
    childrow, = row['files']
    child.write_bytes(childrow['source'].encode())
    assert sha(child) == childrow['source_sha256']
    assert sha(source) == SOURCE_SHA
    stdout = base64.b64decode(row['stdout_template_base64'] if 'stdout_template_base64' in row else row['stdout_base64']).replace(b'{FILE}', os.fsencode(source)).replace(b'{FILE:payload.php}', os.fsencode(child))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__), source, child,
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
        parsed_child = frontend.request({'op': 'parse-file', 'id': '1', 'mode': 'file',
            'profile': 'cli-raw-85', 'source': base64.b64encode(child.read_bytes()).decode(),
            'requested': base64.b64encode(os.fsencode(child)).decode(),
            'resolved': base64.b64encode(os.fsencode(child)).decode(),
            'opened': base64.b64encode(os.fsencode(child)).decode()})
        assert parsed_child['accepted'] is True
        checked_child = adapter.request({'op': 'check', 'ast': parsed_child['ast'], 'fixture': True})
        assert checked_child['ok'] is True
        response = 'SOURCE_ACCEPT 1 ' + term(child.read_bytes()) + ' ' + checked_child['fixture']
        checks = assertions(checked['fixture'], os.fsencode(source), stdout, child.read_bytes(), response, os.fsencode(child))
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
