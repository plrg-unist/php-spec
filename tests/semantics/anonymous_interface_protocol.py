#!/usr/bin/env python3
"""Check retained interface publication and the real eval RTD counter."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_interface_cases.json'
CASES = ('anonymous-interface-author-link-before-argument-failure',
         'anonymous-interface-independent-private-helper-assignment-composition')

PREFIX = r'''
dec $interface_is_output(pevent) : bool
def $interface_is_output(OUTPUT ptbytes) = true
def $interface_is_output(pevent) = false -- otherwise
dec $interface_output(pevent*) : ptbytes
def $interface_output(eps) = eps
def $interface_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $interface_output(pevent*)
def $interface_output(pevent :: pevent_tail*) = $interface_output(pevent_tail*)
  -- if ~$interface_is_output(pevent)
dec $interface_retry_front(pstate) : bool
def $interface_retry_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S, porigin) = (pclassdesc)
  -- if pclassdesc.INTERFACES = [$ptascii("I145Retry")]
def $interface_retry_front(S) = false -- otherwise
dec $interface_retry_seek(pstate, nat) : pstate
def $interface_retry_seek(S, n) = S -- if $interface_retry_front(S)
def $interface_retry_seek(S, 0) = S -- if ~$interface_retry_front(S)
def $interface_retry_seek(S, n) = $interface_retry_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$interface_retry_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $interface_retry_seek(S, n) = S -- otherwise
dec $interface_catch_seek(pstate, nat) : pstate
def $interface_catch_seek(S, n) = S -- if $interface_output(S.EVENTS) = $ptascii("stop|")
def $interface_catch_seek(S, 0) = S -- if $interface_output(S.EVENTS) =/= $ptascii("stop|")
def $interface_catch_seek(S, n) = $interface_catch_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ $interface_output(S.EVENTS) =/= $ptascii("stop|")
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $interface_catch_seek(S, n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, fixture, filename, stdout, eval_response=None, eval_code=None):
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
    ]
    if case == CASES[0]:
        checks += [
            'S_found = $interface_retry_seek(S_initial,4096)',
            r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
            'S_front = S_found[.COMPLETION = NORMAL]',
            '$interface_retry_front(S_front)',
            'S_front.ORIGIN = (porigin_front)',
            'S_front.TODO = (EVAL expression_new) :: ptask_tail*',
            '$anonymous_new_task_valid(S_front,expression_new)',
            '$anonymous_new_pending(S_front,porigin_front) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("I145Retry@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ $ptascii(":9$0")',
            '~pclassdesc.EARLY',
            'pclassdesc.PARENT = eps',
            '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
            '$pil_at(S_front.LINKEDINTERFACES,pclassdesc.ORIGIN) = eps',
            '~$dynamic_new_known(S_front,pclassdesc.NAME)',
            '$class_named(S_front.CLASSNAMES,$ptlc($ptascii("I145Retry"))) = (porigin_interface)',
            'pdeclcause = $declaration_cause(S_front)',
            '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
            '$class_state_valid(S_front)',
            '$call_descriptors_valid(S_front)',
            '$heap_valid($heap_graph(S_front))',
            'S_linked_raw = $drive_steps(S_front,1)',
            r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
            'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
            'S_linked.TODO = S_front.TODO',
            'S_linked.ORIGIN = S_front.ORIGIN',
            'S_linked.EVENTS = S_front.EVENTS',
            'S_linked.OBJECTS = S_front.OBJECTS',
            'S_linked.OBJECTPROPS = S_front.OBJECTPROPS',
            'S_linked.ALLOCATIONS = S_front.ALLOCATIONS',
            'S_linked.DECLARATIONS = S_front.DECLARATIONS ++ [PDRCLASS pclassdesc.ORIGIN pdeclcause]',
            'S_linked.LINKEDINTERFACES = S_front.LINKEDINTERFACES ++ [{OWNER pclassdesc.ORIGIN,TARGETS ([PILSOURCE $ptascii("I145Retry") porigin_interface])}]',
            'S_linked.LINKEDPARENTS = S_front.LINKEDPARENTS',
            '$anonymous_new_available(S_linked,pclassdesc)',
            '$dynamic_new_known(S_linked,pclassdesc.NAME)',
            '$class_state_valid(S_linked)',
            'S_caught_raw = $interface_catch_seek(S_linked,4096)',
            r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
            'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
            '$interface_output(S_caught.EVENTS) = $ptascii("stop|")',
            'S_caught.DECLARATIONS = S_linked.DECLARATIONS',
            'S_caught.LINKEDINTERFACES = S_linked.LINKEDINTERFACES',
            '$anonymous_new_available(S_caught,pclassdesc)',
            '$class_state_valid(S_caught)',
            '$heap_valid($heap_graph(S_caught))',
            'S_done = $drive_steps(S_caught,4096)',
            'S_done.DECLARATIONS = S_linked.DECLARATIONS',
            'S_done.LINKEDINTERFACES = S_linked.LINKEDINTERFACES',
            '$anonymous_new_available(S_done,pclassdesc)',
        ]
    else:
        checks += [
            'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
            'S_wait.COMPLETION = SOURCE_PENDING',
            'S_wait.EVALCONTEXTS = pevalcontext :: eps',
            'pevalcontext.UNIT = 1',
            'pevalcontext.BYTES = $base64(' + json.dumps(base64.b64encode(eval_code).decode()) + ')',
            'ptbytes_eval_file = $base64(' + json.dumps(filename) + ') ++ $ptascii("(10) : eval()\'d code")',
            'pevalcontext.FILE = ptbytes_eval_file',
            '$eval_response_valid(S_wait,' + eval_response + ')',
            'S_body = $eval_resume(S_wait,' + eval_response + ')',
            'S_body.COMPLETION = NORMAL',
            'S_done = $drive_steps(S_body,4096)',
            'ptbytes_dynamic_name = $ptascii("class@anonymous") ++ [0] ++ ptbytes_eval_file ++ $ptascii(":1$1")',
            '$class_named(S_done.CLASSNAMES,$ptlc(ptbytes_dynamic_name)) = (porigin_dynamic)',
            '$class_at(S_done.CLASSES,porigin_dynamic) = (pclassdesc_dynamic)',
            'pclassdesc_dynamic.ORIGIN = PORIGIN 1 pcpath_dynamic',
            'pclassdesc_dynamic.NAME = ptbytes_dynamic_name',
            'pclassdesc_dynamic.LINE = 1',
            'pclassdesc_dynamic.PARENT = eps',
            'pclassdesc_dynamic.INTERFACES = eps',
            '$call_sourcefile(S_done.FILES,porigin_dynamic) = ptbytes_eval_file',
            '$source_unit(S_done.SOURCES,1) = (pcunit_dynamic)',
            '$effective_method(S_done,porigin_dynamic,$ptascii("hidden"),|S_done.CLASSES|) = (pmethoddesc_private)',
            'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
            '$effective_method(S_done,porigin_dynamic,$ptascii("value"),|S_done.CLASSES|) = (pmethoddesc_public)',
            'pmethoddesc_public.VISIBILITY = PROPERTY_PUBLIC',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$interface_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    rows = [row for row in json.loads(CATALOGUE.read_text())['cases']
            if row['id'] in CASES and args.match in row['id']]
    assert rows
    raw = Path(tempfile.mkdtemp(prefix='anonymous-interface-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__), CATALOGUE,
               ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'inputs_before': before, 'records': [],
              'parent_affinity': sorted(os.sched_getaffinity(0)), 'raw': str(raw)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
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
            stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(b'{FILE}', os.fsencode(source))
            eval_response, eval_code = None, None
            if row['id'] == CASES[1]:
                eval_code = next(base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                                 if node['node'] == 'Scalar_String' and
                                 base64.b64decode(node['fields'][0]['bytes']).startswith(b'$helper = new class'))
                parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                                'profile': 'cli-raw-85',
                                                'source': base64.b64encode(eval_code).decode()})
                assert parsed_eval['accepted'] is True
                checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
                assert checked_eval['ok'] is True
                eval_response = 'SOURCE_ACCEPT 1 $base64(' + json.dumps(base64.b64encode(eval_code).decode()) + ') ' + checked_eval['fixture']
            checks = assertions(row['id'], checked['fixture'], base64.b64encode(os.fsencode(source)).decode(), stdout, eval_response, eval_code)
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           *map(str, modules), str(fixture)], directory / 'numeric', 300, ROOT)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['records'].append({'id': row['id'], 'pass': passed, 'assertions': len(checks),
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
