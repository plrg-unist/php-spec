#!/usr/bin/env python3
"""Independent later-unit dependency retry, entry visibility and publication causes."""
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
SOURCE_SHA = 'a1939b9f19d5e89be1ccbaa49d40b9ad19a1f67bc9dc9a4894e31475989bf5a5'

PREFIX = r"""
dec $review_dynamic_is_output(pevent) : bool
def $review_dynamic_is_output(OUTPUT ptbytes) = true
def $review_dynamic_is_output(pevent) = false -- otherwise
dec $review_dynamic_output(pevent*) : ptbytes
def $review_dynamic_output(eps) = eps
def $review_dynamic_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_dynamic_output(pevent*)
def $review_dynamic_output(pevent :: pevent_tail*) = $review_dynamic_output(pevent_tail*)
  -- if ~$review_dynamic_is_output(pevent)
dec $review_dynamic_front(pstate) : bool
def $review_dynamic_front(S) = true
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata)) :: ptask_tail*
  -- if $anonymous_new_descriptor(S,PORIGIN 1 pcpath) = (pclassdesc)
  -- if pclassdesc.PARENT = (__BASE__)
  -- if pclassdesc.INTERFACES = [__READ__]
def $review_dynamic_front(S) = false -- otherwise
dec $review_dynamic_phase(pstate,nat) : bool
def $review_dynamic_phase(S,0) = $review_dynamic_front(S)
def $review_dynamic_phase(S,1) = ($review_dynamic_output(S.EVENTS) = __PAUSE__)
def $review_dynamic_phase(S,2) = true
  -- if ptbytes_name = __PREFIX__ ++ [0] ++ $call_sourcefile(S.FILES,PORIGIN 1 eps) ++ $ptascii(":1$0")
  -- if $class_named(S.CLASSNAMES,$ptlc(ptbytes_name)) =/= eps
def $review_dynamic_phase(S,n) = false -- otherwise
dec $review_dynamic_seek(pstate,nat,nat) : pstate
def $review_dynamic_seek(S,n_mode,n) = S -- if $review_dynamic_phase(S,n_mode)
def $review_dynamic_seek(S,n_mode,0) = S -- if ~$review_dynamic_phase(S,n_mode)
def $review_dynamic_seek(S,n_mode,n) = $review_dynamic_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_dynamic_phase(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $review_dynamic_seek(S,n_mode,n) = S -- otherwise
dec $review_dynamic_receipt(pdeclaration,porigin) : bool
def $review_dynamic_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $review_dynamic_receipt(pdeclaration,porigin) = false -- otherwise
dec $review_dynamic_bit(bool) : nat
def $review_dynamic_bit(true) = 1
def $review_dynamic_bit(false) = 0
dec $review_dynamic_count(pdeclaration*,porigin) : nat
def $review_dynamic_count(eps,porigin) = 0
def $review_dynamic_count(pdeclaration :: pdeclaration_tail*,porigin) = $($review_dynamic_bit($review_dynamic_receipt(pdeclaration,porigin)) + $review_dynamic_count(pdeclaration_tail*,porigin))
dec $review_dynamic_cause(pdeclaration*,porigin) : pdeclcause?
def $review_dynamic_cause(eps,porigin) = eps
def $review_dynamic_cause((PDRCLASS porigin pdeclcause) :: pdeclaration_tail*,porigin) = (pdeclcause)
def $review_dynamic_cause(pdeclaration :: pdeclaration_tail*,porigin) = $review_dynamic_cause(pdeclaration_tail*,porigin)
  -- if ~$review_dynamic_receipt(pdeclaration,porigin)
dec $review_dynamic_without_exit(pdeclaration*,nat) : pdeclaration*
def $review_dynamic_without_exit(eps,n) = eps
def $review_dynamic_without_exit(pdeclaration :: pdeclaration_tail*,n) = $review_dynamic_without_exit(pdeclaration_tail*,n)
  -- if $declaration_complete_item(pdeclaration,n)
def $review_dynamic_without_exit(pdeclaration :: pdeclaration_tail*,n) = pdeclaration :: $review_dynamic_without_exit(pdeclaration_tail*,n)
  -- if ~$declaration_complete_item(pdeclaration,n)
"""
for marker, value in {
    '__BASE__': b'Review148Loaded\\Base',
    '__READ__': b'Review148Loaded\\Read',
    '__PREFIX__': b'Review148Loaded\\Base@anonymous',
    '__PAUSE__': b'load:Review148Loaded\\Base|load:Review148Loaded\\Read|pause|',
}.items():
    PREFIX = PREFIX.replace(marker, '$base64(' + json.dumps(base64.b64encode(value).decode()) + ')')



def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    base = term(b'Review148Loaded\\Base')
    read = term(b'Review148Loaded\\Read')
    outer_file = term(filename + b"(15) : eval()'d code")
    expected_name = term(b'Review148Loaded\\Base@anonymous\0' + filename + b"(15) : eval()'d code:1$0")
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_wait_outer = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait_outer.COMPLETION = SOURCE_PENDING',
        'S_wait_outer.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        'pevalcontext_outer.BYTES = ' + term(codes[0]),
        'pevalcontext_outer.FILE = ' + outer_file,
        '$eval_response_valid(S_wait_outer,' + responses[0] + ')',
        'S_outer = $eval_resume(S_wait_outer,' + responses[0] + ')',
        'S_outer.COMPLETION = NORMAL',
        'S_first_raw = $review_dynamic_seek(S_outer,0,4096)',
        r'S_first_raw.COMPLETION = NORMAL \/ S_first_raw.COMPLETION = BUDGET',
        'S_first = S_first_raw[.COMPLETION = NORMAL]',
        '$review_dynamic_front(S_first)',
        'S_first.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_descriptor(S_first,PORIGIN 1 pcpath_new) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN 1 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc.NAME = ' + expected_name,
        '~pclassdesc.EARLY',
        '$declaration_unit_complete(S_first.DECLARATIONS,1)',
        '$anonymous_history_seed(S_first,1) = (0)',
        '$class_state_valid(S_first)',
        '$class_named(S_first.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_named(S_first.CLASSNAMES,$ptlc(' + base + ')) = eps',
        '$class_named(S_first.CLASSNAMES,$ptlc(' + read + ')) = eps',
        '$review_dynamic_count(S_first.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        '$anonymous_new_descriptor(S_first,PORIGIN 0 pcpath_new) = eps',
        'S_open = S_first[.DECLARATIONS = $review_dynamic_without_exit(S_first.DECLARATIONS,1)]',
        '~$declaration_unit_complete(S_open.DECLARATIONS,1)',
        '$anonymous_new_descriptor(S_open,PORIGIN 1 pcpath_new) = eps',
        'S_wait_base = $drive_steps(S_first,4096)',
        'S_wait_base.COMPLETION = SOURCE_PENDING',
        'S_wait_base.EVALCONTEXTS = pevalcontext_base :: pevalcontext_running :: eps',
        'pevalcontext_base.UNIT = 2',
        'pevalcontext_running.UNIT = 1',
        'pevalcontext_running.PHASE = UNIT_RUN',
        'pevalcontext_base.BYTES = ' + term(codes[1]),
        'pevalcontext_base.FILE = ' + term(filename + b"(7) : eval()'d code"),
        '$review_dynamic_output(S_wait_base.EVENTS) = ' + term(b'load:Review148Loaded\\Base|'),
        '$eval_response_valid(S_wait_base,' + responses[1] + ')',
        'S_body_base = $eval_resume(S_wait_base,' + responses[1] + ')',
        'S_body_base.COMPLETION = NORMAL',
        'S_caught_raw = $review_dynamic_seek(S_body_base,1,4096)',
        r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
        'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
        '$review_dynamic_phase(S_caught,1)',
        '$class_named(S_caught.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        '$class_named(S_caught.CLASSNAMES,$ptlc(' + read + ')) = eps',
        '$class_named(S_caught.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_link_at(S_caught.LINKEDPARENTS,pclassdesc.ORIGIN) = eps',
        '$pil_at(S_caught.LINKEDINTERFACES,pclassdesc.ORIGIN) = eps',
        '$review_dynamic_count(S_caught.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        'S_retry_raw = $review_dynamic_seek(S_caught,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        '$review_dynamic_front(S_retry)',
        'S_retry.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_descriptor(S_retry,PORIGIN 1 pcpath_new) = (pclassdesc)',
        '$anonymous_history_seed(S_retry,1) = (0)',
        '$class_constant_compile_entry(S_retry,1) = (S_entry)',
        '$class_named(S_entry.CLASSNAMES,$ptlc(' + base + ')) = eps',
        '~$ppclass_external_known((S_entry),' + base + ')',
        '$ppclass_external_known((S_retry),' + base + ')',
        '$class_state_valid(S_retry)',
        'S_wait_interface = $drive_steps(S_retry,4096)',
        'S_wait_interface.COMPLETION = SOURCE_PENDING',
        'S_wait_interface.EVALCONTEXTS = pevalcontext_interface :: pevalcontext_running_interface :: eps',
        'pevalcontext_interface.UNIT = 3',
        'pevalcontext_running_interface.UNIT = 1',
        'pevalcontext_running_interface.PHASE = UNIT_RUN',
        'pevalcontext_interface.BYTES = ' + term(codes[2]),
        'pevalcontext_interface.FILE = ' + term(filename + b"(11) : eval()'d code"),
        '$declaration_autoload(S_wait_interface) = [(n_call,pautoloadcall,pautoloadentry)]',
        'pautoloadcall.NAME = ' + read,
        'pautoloadcall.KEY = $ptlc(pautoloadcall.NAME)',
        'pautoloadcall.SITE = pclassdesc.ORIGIN',
        'pautoloadcall.RESUME = AUTO_INTERFACE pclassdesc.ORIGIN (' + read + ')',
        '$autoload_declaration_resume(S_wait_interface,pautoloadcall)',
        '~$autoload_declaration_resume(S_wait_interface,pautoloadcall[.SITE = PORIGIN 1 pcpath_new])',
        '$call_descriptors_valid(S_wait_interface)',
        '$eval_response_valid(S_wait_interface,' + responses[2] + ')',
        'S_body_interface = $eval_resume(S_wait_interface,' + responses[2] + ')',
        'S_body_interface.COMPLETION = NORMAL',
        'S_linked_raw = $review_dynamic_seek(S_body_interface,2,4096)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        '$review_dynamic_phase(S_linked,2)',
        '$review_dynamic_output(S_linked.EVENTS) = ' + term(b'load:Review148Loaded\\Base|load:Review148Loaded\\Read|pause|load:Review148Loaded\\Read|'),
        'S_linked.OBJECTS = S_retry.OBJECTS',
        '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_named(S_linked.CLASSNAMES,$ptlc(' + read + ')) = (porigin_interface)',
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$pil_at(S_linked.LINKEDINTERFACES,pclassdesc.ORIGIN) = (PILTARGETS ([PILSOURCE ' + read + ' porigin_interface]))',
        '$review_dynamic_count(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$review_dynamic_cause(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = (pdeclcause)',
        'pdeclcause.UNIT = 1',
        'pdeclcause.AUTOLOAD = eps',
        '$declaration_cause_valid(S_linked,pclassdesc.ORIGIN,pdeclcause)',
        '~$declaration_cause_valid(S_linked,pclassdesc.ORIGIN,pdeclcause[.UNIT = 0])',
        '$call_descriptors_valid(S_linked)',
        '$class_state_valid(S_linked)',
        'S_done = $drive_steps(S_linked,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_dynamic_output(S_done.EVENTS) = ' + term(stdout),
        '$review_dynamic_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$anonymous_history_seed(S_done,1) = (0)',
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-dependency-cause-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'namespace Review148Retry;'), (2, b'namespace Review148Loaded; class Base '), (3, b'namespace Review148Loaded; interface Read ')]:
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
