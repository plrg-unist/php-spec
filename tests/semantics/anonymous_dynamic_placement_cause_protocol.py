#!/usr/bin/env python3
"""Independent later-unit named/Closure factory publication and argument retry."""
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
SOURCE_SHA = 'bbc014aaa50a9132efd2f9679eb6b242d782925665afe8466b1cbe9770caa7ce'

PREFIX = r"""
dec $review_site_is_output(pevent) : bool
def $review_site_is_output(OUTPUT ptbytes) = true
def $review_site_is_output(pevent) = false -- otherwise
dec $review_site_output(pevent*) : ptbytes
def $review_site_output(eps) = eps
def $review_site_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_site_output(pevent*)
def $review_site_output(pevent :: pevent_tail*) = $review_site_output(pevent_tail*)
  -- if ~$review_site_is_output(pevent)
dec $review_site_front(pstate,int) : bool
def $review_site_front(S,z) = true
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if $origin_node(S.SOURCES,PORIGIN 1 pcpath) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata_class) = z
def $review_site_front(S,z) = false -- otherwise
dec $review_site_phase(pstate,nat) : bool
def $review_site_phase(S,0) = $review_site_front(S,5)
def $review_site_phase(S,1) = ($review_site_output(S.EVENTS) = $ptascii("before|first|second|argument|"))
def $review_site_phase(S,2) = $review_site_front(S,20)
def $review_site_phase(S,3) = true
  -- if $review_site_output(S.EVENTS) = $ptascii("before|first|second|argument|first|second|")
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
  -- if pcallcontext.CALLED_CLASS = (porigin_called)
  -- if $class_at(S.CLASSES,porigin_called) = (pclassdesc)
  -- if pclassdesc.LINE = 5 /\ pclassdesc.PARENT = ($ptascii("Review149Base"))
def $review_site_phase(S,n) = false -- otherwise
dec $review_site_seek(pstate,nat,nat) : pstate
def $review_site_seek(S,n_mode,n) = S -- if $review_site_phase(S,n_mode)
def $review_site_seek(S,n_mode,0) = S -- if ~$review_site_phase(S,n_mode)
def $review_site_seek(S,n_mode,n) = $review_site_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_site_phase(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $review_site_seek(S,n_mode,n) = S -- otherwise
dec $review_site_receipt(pdeclaration,porigin) : bool
def $review_site_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $review_site_receipt(pdeclaration,porigin) = false -- otherwise
dec $review_site_bit(bool) : nat
def $review_site_bit(true) = 1
def $review_site_bit(false) = 0
dec $review_site_count(pdeclaration*,porigin) : nat
def $review_site_count(eps,porigin) = 0
def $review_site_count(pdeclaration :: pdeclaration_tail*,porigin) = $($review_site_bit($review_site_receipt(pdeclaration,porigin)) + $review_site_count(pdeclaration_tail*,porigin))
dec $review_site_marker(ptask*) : porigin?
def $review_site_marker(eps) = eps
def $review_site_marker(ptask :: ptask_tail*) = (porigin)
  -- if $finally_marker_origin(ptask) = (porigin)
def $review_site_marker(ptask :: ptask_tail*) = $review_site_marker(ptask_tail*)
  -- if $finally_marker_origin(ptask) = eps
dec $review_site_function(pfunction*,ptbytes) : porigin?
def $review_site_function(eps,ptbytes) = eps
def $review_site_function(pfunction :: pfunction_tail*,ptbytes) = (pfunction.ORIGIN)
  -- if pfunction.NAME = ptbytes
def $review_site_function(pfunction :: pfunction_tail*,ptbytes) = $review_site_function(pfunction_tail*,ptbytes)
  -- if pfunction.NAME =/= ptbytes
dec $review_site_first_function(pdeclcalls) : porigin
def $review_site_first_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail) = porigin_function
dec $review_site_wrong_function(pdeclcalls,porigin) : pdeclcalls
def $review_site_wrong_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail,porigin_wrong) = (porigin_wrong,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    outer_file = filename + b"(28) : eval()'d code"
    name = b'Review149Base@anonymous\0' + outer_file + b':5$0'
    closure_name = b'Review149Base@anonymous\0' + outer_file + b':20$1'
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_wait = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.EVALCONTEXTS = pevalcontext :: eps',
        'pevalcontext.UNIT = 1',
        'pevalcontext.BYTES = ' + term(codes[0]),
        'pevalcontext.FILE = ' + term(outer_file),
        '$eval_response_valid(S_wait,' + responses[0] + ')',
        'S_body = $eval_resume(S_wait,' + responses[0] + ')',
        'S_body.COMPLETION = NORMAL',
        'S_front_raw = $review_site_seek(S_body,0,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$review_site_front(S_front,5)',
        'S_front.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_pending(S_front,PORIGIN 1 pcpath_new) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN 1 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc.NAME = ' + term(name),
        '~pclassdesc.EARLY',
        '$anonymous_history_seed(S_front,1) = (0)',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_named(S_front.CLASSNAMES,$ptascii("review149base")) = (porigin_base)',
        '$class_named(S_front.CLASSNAMES,$ptascii("review149read")) = (porigin_interface)',
        '$review_site_count(S_front.DECLARATIONS,pclassdesc.ORIGIN) = 0',
        'S_front.CURRENT = (pcallcontext_factory)',
        'pcallcontext_factory.FUNCTION = PORIGIN 1 pcpath_factory',
        'pcallcontext_factory.LEXICAL_CLASS = eps',
        'pcallcontext_factory.CALLED_CLASS = eps',
        'S_front.FRAMES = pframe_outer :: eps',
        'S_saved = $constant_frame_scope(S_front,pframe_outer,eps)',
        '$review_site_marker(S_saved.TODO) = (porigin_try)',
        'porigin_try = PORIGIN 1 pcpath_try',
        '$source_unit(S_saved.SOURCES,1) = (pcunit_saved)',
        '$ppfinally_scope(pcunit_saved.OCCURRENCES,pcpath_try) = eps',
        '$ppfinally_scope(pcunit_saved.OCCURRENCES,pcpath_factory) = pcpath_factory',
        '$declaration_entry_site(S_saved.DECLARATIONS,1) = (porigin_entry)',
        '$finally_current_complete(S_saved)',
        '$finally_outer_origin_valid(S_saved,porigin_try,(porigin_entry))',
        '~$finally_outer_origin_valid(S_saved,pcallcontext_factory.FUNCTION,(porigin_entry))',
        'S_saved.EVALCONTEXTS = pevalcontext_running :: eps',
        'pevalcontext_running.PHASE = UNIT_RUN',
        'pevalcontext_running.OWNER = |S_saved.FRAMES|',
        '~$finally_outer_origin_valid(S_saved[.EVALCONTEXTS = eps],porigin_try,(porigin_entry))',
        '~$finally_outer_origin_valid(S_saved[.EVALCONTEXTS = [pevalcontext_running[.OWNER = $(pevalcontext_running.OWNER + 1)]]],porigin_try,(porigin_entry))',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'pdeclcause = $declaration_cause(S_front)',
        'pdeclcause.UNIT = 1',
        'pdeclcause.AUTOLOAD = eps',
        '|pdeclcause.CALLS| = 1',
        '$review_site_first_function(pdeclcause.CALLS) = pcallcontext_factory.FUNCTION',
        '$declaration_caller_lexical(pdeclcause.CALLS) = eps',
        '$declaration_caller_called(pdeclcause.CALLS) = eps',
        '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.UNIT = 0])',
        '$review_site_function($all_functions(S_front),$ptascii("review149_first")) = (porigin_wrong)',
        '$function_at($all_functions(S_front),porigin_wrong) = (pfunction_wrong)',
        '~$finally_outer_origin_valid(S_saved,porigin_try,(porigin_wrong))',
        '$declaration_callable_available(S_front,pfunction_wrong,|S_front.DECLARATIONS|)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.CALLS = $review_site_wrong_function(pdeclcause.CALLS,porigin_wrong)])',
        'S_linked_raw = $drive_steps(S_front,1)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        'S_linked.ORIGIN = S_front.ORIGIN',
        'S_linked.TODO = S_front.TODO',
        'S_linked.EVENTS = S_front.EVENTS',
        'S_linked.OBJECTS = S_front.OBJECTS',
        'S_linked.OBJECTPROPS = S_front.OBJECTPROPS',
        'S_linked.ALLOCATIONS = S_front.ALLOCATIONS',
        'S_linked.DECLARATIONS = S_front.DECLARATIONS ++ [PDRCLASS pclassdesc.ORIGIN pdeclcause]',
        '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$pil_at(S_linked.LINKEDINTERFACES,pclassdesc.ORIGIN) = (PILTARGETS ([PILSOURCE ($ptascii("Review149Read")) porigin_interface]))',
        '$review_site_count(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$anonymous_new_pending(S_linked,PORIGIN 1 pcpath_new) = eps',
        '$call_descriptors_valid(S_linked)',
        '$class_state_valid(S_linked)',
        'S_caught_raw = $review_site_seek(S_linked,1,4096)',
        r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
        'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
        '$review_site_phase(S_caught,1)',
        '$class_named(S_caught.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$review_site_count(S_caught.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$call_descriptors_valid(S_caught)',
        '$heap_valid($heap_graph(S_caught))',
        'S_retry_raw = $review_site_seek(S_caught,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        'S_retry.ORIGIN = (PORIGIN 1 pcpath_new)',
        '$anonymous_new_descriptor(S_retry,PORIGIN 1 pcpath_new) = (pclassdesc)',
        '$anonymous_new_name(S_retry,PORIGIN 1 pcpath_new) = (pclassdesc.NAME)',
        '$anonymous_new_pending(S_retry,PORIGIN 1 pcpath_new) = eps',
        'S_retry.DECLARATIONS = S_linked.DECLARATIONS',
        'S_ctor_raw = $review_site_seek(S_retry,3,4096)',
        r'S_ctor_raw.COMPLETION = NORMAL \/ S_ctor_raw.COMPLETION = BUDGET',
        'S_ctor = S_ctor_raw[.COMPLETION = NORMAL]',
        '$review_site_phase(S_ctor,3)',
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_ctor.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_ctor.CALLSITE = (PORIGIN 1 pcpath_new)',
        '$class_method_origin(S_ctor.CLASSES,pcallcontext_ctor.FUNCTION) = (pmethoddesc_ctor)',
        'pmethoddesc_ctor.OWNER = porigin_base',
        '$call_descriptors_valid(S_ctor)',
        '$class_state_valid(S_ctor)',
        'S_closure_raw = $review_site_seek(S_ctor,2,4096)',
        r'S_closure_raw.COMPLETION = NORMAL \/ S_closure_raw.COMPLETION = BUDGET',
        'S_closure = S_closure_raw[.COMPLETION = NORMAL]',
        '$review_site_front(S_closure,20)',
        'S_closure.ORIGIN = (PORIGIN 1 pcpath_closure)',
        '$anonymous_new_pending(S_closure,PORIGIN 1 pcpath_closure) = (pclassdesc_closure)',
        'pclassdesc_closure.NAME = ' + term(closure_name),
        'pclassdesc_closure.ORIGIN = PORIGIN 1 (pcpath_closure ++ [PCFIELD 0])',
        'pdeclcause_closure = $declaration_cause(S_closure)',
        'pdeclcause_closure.UNIT = 1',
        'pdeclcause_closure.AUTOLOAD = eps',
        '|pdeclcause_closure.CALLS| = 1',
        '$review_site_first_function(pdeclcause_closure.CALLS) =/= pcallcontext_factory.FUNCTION',
        '$declaration_cause_valid(S_closure,pclassdesc_closure.ORIGIN,pdeclcause_closure)',
        '~$declaration_cause_valid(S_closure,pclassdesc_closure.ORIGIN,pdeclcause_closure[.CALLS = $review_site_wrong_function(pdeclcause_closure.CALLS,pcallcontext_factory.FUNCTION)])',
        '$call_descriptors_valid(S_closure)',
        '$class_state_valid(S_closure)',
        'S_closure_linked_raw = $drive_steps(S_closure,1)',
        r'S_closure_linked_raw.COMPLETION = NORMAL \/ S_closure_linked_raw.COMPLETION = BUDGET',
        'S_closure_linked = S_closure_linked_raw[.COMPLETION = NORMAL]',
        'S_closure_linked.DECLARATIONS = S_closure.DECLARATIONS ++ [PDRCLASS pclassdesc_closure.ORIGIN pdeclcause_closure]',
        'S_closure_linked.OBJECTS = S_closure.OBJECTS',
        'S_closure_linked.EVENTS = S_closure.EVENTS',
        'S_done = $drive_steps(S_closure_linked,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_site_output(S_done.EVENTS) = ' + term(stdout),
        '$review_site_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$review_site_count(S_done.DECLARATIONS,pclassdesc_closure.ORIGIN) = 1',
        '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        '$class_named(S_done.CLASSNAMES,$ptlc(pclassdesc_closure.NAME)) = (pclassdesc_closure.ORIGIN)',
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
    raw = Path(tempfile.mkdtemp(prefix='anonymous-dynamic-placement-cause-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'namespace Review149Factory;')]:
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
