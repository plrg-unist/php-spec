#!/usr/bin/env python3
"""Source-reached dynamic trait projection with authentic compiler counters."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from anonymous_trait_adaptations_protocol import PREFIX
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/dynamic_anonymous_trait_cases.json'
OUTPUT = r'''
dec $class171_output_item(pevent) : ptbytes
def $class171_output_item(OUTPUT ptbytes) = ptbytes
def $class171_output_item(pevent) = eps -- otherwise
dec $class171_output(pevent*) : ptbytes
def $class171_output(eps) = eps
def $class171_output(pevent :: pevent_tail*) = $class171_output_item(pevent) ++ $class171_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def checks(row, fixture, filename, code, response):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [
        'S_initial = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait,' + response + ')',
        'S_entered = $eval_resume(S_wait,' + response + ')',
        'S_entered.COMPLETION = NORMAL',
        '$source_unit(S_entered.SOURCES,1) = (pcunit)',
        '$anonymous_rtd_unit(pcunit) =/= eps',
        '$declaration_unit_complete(S_entered.DECLARATIONS,1)',
        'S_pre = $class169_seek(S_entered,0,500)',
        'S_pre.COMPLETION = BUDGET /\\ $class169_front(S_pre,0)',
        'S_pre.ORIGIN = (porigin_new)',
        'porigin_new = PORIGIN 1 pcpath_new',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.ORIGIN = PORIGIN 1 (pcpath_new ++ [PCFIELD 0])',
        '~pclassdesc_raw.EARLY',
        'pclassdesc_raw.NAME = $ptascii("Stringable@anonymous") ++ [0] ++ ' + term(filename) + ' ++ $ptascii("(5) : eval()\'d code:9$2")',
        'pclassdesc_raw.INTERFACES = [$ptascii("Stringable")]',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '|S_pre.OBJECTS| = 1',
        '$class_constant_compile_entry(S_pre,1) = (S_entry)',
        '$anonymous_history_seed(S_pre,1) = (2)',
        '$compilation_projection(S_pre,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        '$anonymous_compiled_class_count(pcunit,$call_sourcefile(S_pre.FILES,pclassdesc_raw.ORIGIN),ppinstalled.CLASSES,eps,(S_entry),2) = (3)',
        'S_link = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_link.COMPLETION = BUDGET',
        '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        '$anonymous_trait_projection(pclassdesc_raw,pclassdesc_live)',
        'pclassdesc_live.NAME = pclassdesc_raw.NAME /\\ pclassdesc_live.INTERFACES = pclassdesc_raw.INTERFACES',
        '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$declaration_history_valid(S_link)',
        '$anonymous_new_descriptor(S_link,porigin_new) = (pclassdesc_live)',
        '$anonymous_new_available(S_link,pclassdesc_live)',
        '$anonymous_interface_targets_valid(S_link,pclassdesc_live)',
        '~((INSTANCE pclassdesc_live.ORIGIN) <- S_link.OBJECTS)',
        '$trait_plan(S_link,pclassdesc_live) = ptraitplan',
        '|ptraitplan.TRAITS| = 2 /\\ |ptraitplan.PRECEDENCES| = 1 /\\ |ptraitplan.ALIASES| = 2',
        '$method_named(pclassdesc_live.METHODS,$ptascii("q")) = (pmethoddesc_q)',
        '$method_named(pclassdesc_live.METHODS,$ptascii("take")) = (pmethoddesc_take)',
        'pmethoddesc_take.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
        'psparam.TYPE = [(PTBRANCH ([PTCLASS pclassdesc_live.NAME]))]',
        'pclassdesc_duplicate = pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_q]]',
        '$anonymous_trait_projection(pclassdesc_raw,pclassdesc_duplicate)',
        'S_duplicate = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_duplicate)]',
        '~$declaration_history_valid(S_duplicate)',
        '$anonymous_new_descriptor(S_duplicate,porigin_new) = eps',
        '$class_constant_compile_prefix(S_link.DECLARATIONS,1,0) = (n_prefix)',
        'n_after_entry = $(n_prefix + 1)',
        'n_tail = $nabs($(|S_link.DECLARATIONS| - n_after_entry))',
        'S_no_entry = S_link[.DECLARATIONS = S_link.DECLARATIONS[0:n_prefix] ++ S_link.DECLARATIONS[n_after_entry:n_tail]]',
        '$class_constant_compile_entry(S_no_entry,1) = eps',
        '~$declaration_history_valid(S_no_entry)',
        '$anonymous_new_descriptor(S_no_entry,porigin_new) = eps',
        'S_alloc = $drive_steps(S_link[.COMPLETION = NORMAL],1)',
        'S_alloc.COMPLETION = BUDGET',
        'S_alloc.RESULT = KNOWN (POBJECT n_object)',
        'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        'S_receive = $class169_seek(S_alloc,2,1000)',
        'S_receive.COMPLETION = BUDGET /\\ $class169_front(S_receive,2)',
        'S_receive.TODO = (TYPE_RECEIVE pmethoddesc_take.FUNCTION.ORIGIN 0) :: ptask_tail*',
        'S_receive.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
        '$closure_scope_at(S_receive.CLOSURESCOPES,n_capture) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_live.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_live.ORIGIN',
        '$method_closure_functions(S_receive,n_capture,pmethoddesc_take) = (pmethoddesc_take.FUNCTION,pmethoddesc_take.FUNCTION)',
        '$call_current_valid(S_receive) /\\ $call_descriptors_valid(S_receive)',
        'S_done = $drive_steps(S_receive[.COMPLETION = NORMAL],8192)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.EVALCONTEXTS = eps /\\ S_done.FILECONTEXTS = eps /\\ S_done.CURRENT = eps',
        '$class171_output(S_done.EVENTS) = ' + term(expected),
        '$anonymous_history_seed(S_done,1) = (2)',
        '$anonymous_rtd_count(S_done,pcunit) = (1)',
        '$declaration_history_valid(S_done) /\\ $class_state_valid(S_done)',
        '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    row, = [r for r in json.loads(CATALOGUE.read_text())['cases'] if r['id'] == 'author-eval-seeded-imported-capture']
    raw = Path(tempfile.mkdtemp(prefix='dynamic-anonymous-trait-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, source, Path(__file__),
               ROOT / 'tests/semantics/anonymous_trait_adaptations_protocol.py',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'source_sha256': row['source_sha256'], 'inputs_before': before}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        code, = [base64.b64decode(n['fields'][0]['bytes']) for n in nodes(parsed['ast'])
                 if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'namespace Author171;')]
        parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
        assert parsed_eval['accepted'] is True
        checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
        assert checked_eval['ok'] is True
        response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked_eval['fixture']
        conditions = checks(row, checked['fixture'], os.fsencode(source), code, response)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + OUTPUT + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions))
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=len(conditions), fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
