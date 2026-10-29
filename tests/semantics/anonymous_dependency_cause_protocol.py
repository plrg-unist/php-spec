#!/usr/bin/env python3
"""Independent real autoload failure, retry and anonymous publication causes."""
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
SOURCE_SHA = '61f255bfe3a666804fa7fe3ecef79bfc1004af831bd61610c5cc460a9c15603a'

PREFIX = r'''
dec $review_dependency_is_output(pevent) : bool
def $review_dependency_is_output(OUTPUT ptbytes) = true
def $review_dependency_is_output(pevent) = false -- otherwise
dec $review_dependency_output(pevent*) : ptbytes
def $review_dependency_output(eps) = eps
def $review_dependency_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_dependency_output(pevent*)
def $review_dependency_output(pevent :: pevent_tail*) = $review_dependency_output(pevent_tail*)
  -- if ~$review_dependency_is_output(pevent)
dec $review_dependency_front(pstate) : bool
def $review_dependency_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) = (pclassdesc)
  -- if pclassdesc.PARENT = (ptbytes_parent)
  -- if ptbytes_parent = $ptascii("Review146LoadBase")
  -- if pclassdesc.INTERFACES = [$ptascii("Review146LoadRead")]
def $review_dependency_front(S) = false -- otherwise
dec $review_dependency_phase(pstate,nat) : bool
def $review_dependency_phase(S,0) = $review_dependency_front(S)
def $review_dependency_phase(S,1) = ($review_dependency_output(S.EVENTS) = $ptascii("load:Review146LoadBase|load:Review146LoadRead|pause|"))
def $review_dependency_phase(S,2) = true
  -- if ptbytes_name = $ptascii("Review146LoadBase@anonymous") ++ [0] ++ $call_sourcefile(S.FILES,PORIGIN 0 eps) ++ $ptascii(":17$0")
  -- if $class_named(S.CLASSNAMES,$ptlc(ptbytes_name)) =/= eps
def $review_dependency_phase(S,n) = false -- otherwise
dec $review_dependency_seek(pstate,nat,nat) : pstate
def $review_dependency_seek(S,n_mode,n) = S -- if $review_dependency_phase(S,n_mode)
def $review_dependency_seek(S,n_mode,0) = S -- if ~$review_dependency_phase(S,n_mode)
def $review_dependency_seek(S,n_mode,n) = $review_dependency_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_dependency_phase(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $review_dependency_seek(S,n_mode,n) = S -- otherwise
dec $review_dependency_receipt(pdeclaration,porigin) : bool
def $review_dependency_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $review_dependency_receipt(pdeclaration,porigin) = false -- otherwise
dec $review_dependency_bit(bool) : nat
def $review_dependency_bit(true) = 1
def $review_dependency_bit(false) = 0
dec $review_dependency_count(pdeclaration*,porigin) : nat
def $review_dependency_count(eps,porigin) = 0
def $review_dependency_count(pdeclaration :: pdeclaration_tail*,porigin) = $($review_dependency_bit($review_dependency_receipt(pdeclaration,porigin)) + $review_dependency_count(pdeclaration_tail*,porigin))
dec $review_dependency_cause(pdeclaration*,porigin) : pdeclcause?
def $review_dependency_cause(eps,porigin) = eps
def $review_dependency_cause((PDRCLASS porigin pdeclcause) :: pdeclaration_tail*,porigin) = (pdeclcause)
def $review_dependency_cause(pdeclaration :: pdeclaration_tail*,porigin) = $review_dependency_cause(pdeclaration_tail*,porigin)
  -- if ~$review_dependency_receipt(pdeclaration,porigin)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_first_raw = $review_dependency_seek(S_initial,0,4096)',
        r'S_first_raw.COMPLETION = NORMAL \/ S_first_raw.COMPLETION = BUDGET',
        'S_first = S_first_raw[.COMPLETION = NORMAL]',
        '$review_dependency_front(S_first)',
        'S_first.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_first,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = $ptascii("Review146LoadBase@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii(":17$0")',
        '~pclassdesc.EARLY',
        '$class_named(S_first.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_named(S_first.CLASSNAMES,$ptlc($ptascii("Review146LoadBase"))) = eps',
        '$class_named(S_first.CLASSNAMES,$ptlc($ptascii("Review146LoadRead"))) = eps',
        '$review_dependency_count(S_first.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        'S_wait_base = $drive_steps(S_first,4096)',
        'S_wait_base.COMPLETION = SOURCE_PENDING',
        'S_wait_base.EVALCONTEXTS = pevalcontext_base :: eps',
        'pevalcontext_base.UNIT = 1',
        'pevalcontext_base.BYTES = ' + term(codes[0]),
        'pevalcontext_base.FILE = ' + term(filename) + ' ++ $ptascii("(7) : eval()\'d code")',
        '$review_dependency_output(S_wait_base.EVENTS) = $ptascii("load:Review146LoadBase|")',
        '$eval_response_valid(S_wait_base,' + responses[0] + ')',
        'S_body_base = $eval_resume(S_wait_base,' + responses[0] + ')',
        'S_body_base.COMPLETION = NORMAL',
        'S_caught_raw = $review_dependency_seek(S_body_base,1,4096)',
        r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
        'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
        '$review_dependency_phase(S_caught,1)',
        '$class_named(S_caught.CLASSNAMES,$ptlc($ptascii("Review146LoadBase"))) = (porigin_base)',
        '$class_named(S_caught.CLASSNAMES,$ptlc($ptascii("Review146LoadRead"))) = eps',
        '$class_named(S_caught.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_link_at(S_caught.LINKEDPARENTS,pclassdesc.ORIGIN) = eps',
        '$pil_at(S_caught.LINKEDINTERFACES,pclassdesc.ORIGIN) = eps',
        '$review_dependency_count(S_caught.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        'S_retry_raw = $review_dependency_seek(S_caught,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        '$review_dependency_front(S_retry)',
        'S_retry.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_retry,porigin_new) = (pclassdesc)',
        '~$dynamic_new_known(S_retry,pclassdesc.NAME)',
        '$review_dependency_count(S_retry.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        '$class_state_valid(S_retry)',
        'S_wait_interface = $drive_steps(S_retry,4096)',
        'S_wait_interface.COMPLETION = SOURCE_PENDING',
        'S_wait_interface.EVALCONTEXTS = pevalcontext_interface :: eps',
        'pevalcontext_interface.UNIT = 2',
        'pevalcontext_interface.BYTES = ' + term(codes[1]),
        'pevalcontext_interface.FILE = ' + term(filename) + ' ++ $ptascii("(11) : eval()\'d code")',
        '$declaration_autoload(S_wait_interface) = [(0,pautoloadcall,pautoloadentry)]',
        'pautoloadcall.NAME = $ptascii("Review146LoadRead")',
        'pautoloadcall.KEY = $ptlc(pautoloadcall.NAME)',
        'pautoloadcall.SITE = pclassdesc.ORIGIN',
        'pautoloadcall.RESUME = AUTO_INTERFACE pclassdesc.ORIGIN ($ptascii("Review146LoadRead"))',
        '$autoload_declaration_resume(S_wait_interface,pautoloadcall)',
        '~$autoload_declaration_resume(S_wait_interface,pautoloadcall[.SITE = porigin_new])',
        '$call_descriptors_valid(S_wait_interface)',
        '$eval_response_valid(S_wait_interface,' + responses[1] + ')',
        'S_body_interface = $eval_resume(S_wait_interface,' + responses[1] + ')',
        'S_body_interface.COMPLETION = NORMAL',
        'S_linked_raw = $review_dependency_seek(S_body_interface,2,4096)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        '$review_dependency_phase(S_linked,2)',
        '$review_dependency_output(S_linked.EVENTS) = $ptascii("load:Review146LoadBase|load:Review146LoadRead|pause|load:Review146LoadRead|")',
        'S_linked.OBJECTS = S_retry.OBJECTS',
        '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_named(S_linked.CLASSNAMES,$ptlc($ptascii("Review146LoadRead"))) = (porigin_interface)',
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$pil_at(S_linked.LINKEDINTERFACES,pclassdesc.ORIGIN) = (PILTARGETS ([PILSOURCE $ptascii("Review146LoadRead") porigin_interface]))',
        '$review_dependency_count(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$review_dependency_cause(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = (pdeclcause)',
        'pdeclcause.UNIT = 0',
        'pdeclcause.AUTOLOAD = eps',
        '|pdeclcause.CALLS| = 1',
        '$declaration_cause_valid(S_linked,pclassdesc.ORIGIN,pdeclcause)',
        '$call_descriptors_valid(S_linked)',
        '$class_state_valid(S_linked)',
        'S_done = $drive_steps(S_linked,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_dependency_output(S_done.EVENTS) = ' + term(stdout),
        '$review_dependency_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dependency-cause-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'class Review146LoadBase '), (2, b'interface Review146LoadRead ')]:
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
