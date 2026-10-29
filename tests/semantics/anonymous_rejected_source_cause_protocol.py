#!/usr/bin/env python3
"""Independent rejected-source history and later aliased publication retry."""
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
SOURCE_SHA = 'fb0f9decd468517a1905602763dfb3b9b1cbca277e6e096f37b41144620996ae'

PREFIX = r"""
dec $review_reject_is_output(pevent) : bool
def $review_reject_is_output(OUTPUT ptbytes) = true
def $review_reject_is_output(pevent) = false -- otherwise
dec $review_reject_output(pevent*) : ptbytes
def $review_reject_output(eps) = eps
def $review_reject_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_reject_output(pevent*)
def $review_reject_output(pevent :: pevent_tail*) = $review_reject_output(pevent_tail*)
  -- if ~$review_reject_is_output(pevent)
dec $review_reject_front(pstate) : bool
def $review_reject_front(S) = true
  -- if S.ORIGIN = (PORIGIN 4 pcpath)
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if $origin_node(S.SOURCES,PORIGIN 4 pcpath) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
  -- if $source_line(metadata_class) = 10
def $review_reject_front(S) = false -- otherwise
dec $review_reject_last(pevent*,ptbytes) : ptbytes
def $review_reject_last(eps,ptbytes) = ptbytes
def $review_reject_last((OUTPUT ptbytes) :: pevent_tail*,ptbytes_old) = $review_reject_last(pevent_tail*,ptbytes)
def $review_reject_last(pevent :: pevent_tail*,ptbytes) = $review_reject_last(pevent_tail*,ptbytes)
  -- if ~$review_reject_is_output(pevent)
dec $review_reject_phase(pstate,nat) : bool
def $review_reject_phase(S,0) = $review_reject_front(S)
def $review_reject_phase(S,1) = ($review_reject_last(S.EVENTS,eps) = $ptascii("caught|"))
def $review_reject_phase(S,2) = true
  -- if $review_reject_last(S.EVENTS,eps) = $ptascii("arg|")
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,pcallcontext.FUNCTION) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__construct")
def $review_reject_phase(S,n) = false -- otherwise
dec $review_reject_seek(pstate,nat,nat) : pstate
def $review_reject_seek(S,n_mode,n) = S -- if $review_reject_phase(S,n_mode)
def $review_reject_seek(S,n_mode,0) = S -- if ~$review_reject_phase(S,n_mode)
def $review_reject_seek(S,n_mode,n) = $review_reject_seek(S_next,n_mode,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_reject_phase(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $review_reject_seek(S,n_mode,n) = S -- otherwise
dec $review_reject_receipt(pdeclaration,porigin) : bool
def $review_reject_receipt(PDRCLASS porigin pdeclcause,porigin) = true
def $review_reject_receipt(pdeclaration,porigin) = false -- otherwise
dec $review_reject_bit(bool) : nat
def $review_reject_bit(true) = 1
def $review_reject_bit(false) = 0
dec $review_reject_count(pdeclaration*,porigin) : nat
def $review_reject_count(eps,porigin) = 0
def $review_reject_count(pdeclaration :: pdeclaration_tail*,porigin) = $($review_reject_bit($review_reject_receipt(pdeclaration,porigin)) + $review_reject_count(pdeclaration_tail*,porigin))
dec $review_reject_function(pfunction*,ptbytes) : porigin?
def $review_reject_function(eps,ptbytes) = eps
def $review_reject_function(pfunction :: pfunction_tail*,ptbytes) = (pfunction.ORIGIN)
  -- if pfunction.NAME = ptbytes
def $review_reject_function(pfunction :: pfunction_tail*,ptbytes) = $review_reject_function(pfunction_tail*,ptbytes)
  -- if pfunction.NAME =/= ptbytes
dec $review_reject_first_function(pdeclcalls) : porigin
def $review_reject_first_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail) = porigin_function
dec $review_reject_wrong_function(pdeclcalls,porigin) : pdeclcalls
def $review_reject_wrong_function((porigin_function,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail,porigin_wrong) = (porigin_wrong,porigin_site?,porigin_lexical?,porigin_called?) :: pdeclcalls_tail
dec $review_reject_entry(pdeclaration*,nat) : pdeclaration?
def $review_reject_entry(eps,n) = eps
def $review_reject_entry(pdeclaration :: pdeclaration_tail*,n) = (pdeclaration)
  -- if $anonymous_rtd_enter(pdeclaration) = (n)
def $review_reject_entry(pdeclaration :: pdeclaration_tail*,n) = $review_reject_entry(pdeclaration_tail*,n)
  -- if $anonymous_rtd_enter(pdeclaration) =/= (n)
dec $review_reject_drop(pfailedsource*,nat) : pfailedsource*
def $review_reject_drop(eps,n) = eps
def $review_reject_drop(pfailedsource :: pfailedsource_tail*,n) = $review_reject_drop(pfailedsource_tail*,n)
  -- if pfailedsource.UNIT = n
def $review_reject_drop(pfailedsource :: pfailedsource_tail*,n) = pfailedsource :: $review_reject_drop(pfailedsource_tail*,n)
  -- if pfailedsource.UNIT =/= n
dec $review_reject_site(pdeclaration,porigin) : pdeclaration
def $review_reject_site(PDENTER n porigin_old? z,porigin) = PDENTER n (porigin) z
def $review_reject_site(PDENTERPRECISION n porigin_old? z z_precision,porigin) = PDENTERPRECISION n (porigin) z z_precision
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def assertions(fixture, filename, stdout, codes, responses):
    files = [filename + suffix for suffix in [b"(9) : eval()'d code", b"(7) : eval()'d code", b"(7) : eval()'d code", b"(13) : eval()'d code", b"(29) : eval()'d code"]]
    name = b'Base151Review@anonymous\0' + files[3] + b':10$1'
    tail_name = b'class@anonymous\0' + files[4] + b':1$2'
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        '~S_initial.COMPILESTOP',
        'S_wait_one = $drive_steps(S_initial[.COMPLETION = NORMAL],4096)',
        'S_wait_one.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_one.EVALCONTEXTS,1) = (pevalcontext_one)',
        'pevalcontext_one.BYTES = ' + term(codes[0]),
        'pevalcontext_one.FILE = ' + term(files[0]),
        '$eval_response_valid(S_wait_one,' + responses[0] + ')',
        'S_one = $eval_resume(S_wait_one,' + responses[0] + ')',
        'S_one.COMPLETION = NORMAL',
        'S_wait_two = $drive_steps(S_one,4096)',
        'S_wait_two.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_two.EVALCONTEXTS,2) = (pevalcontext_two)',
        'pevalcontext_two.BYTES = ' + term(codes[1]),
        'pevalcontext_two.FILE = ' + term(files[1]),
        '$eval_response_valid(S_wait_two,' + responses[1] + ')',
        'S_two = $eval_resume(S_wait_two,' + responses[1] + ')',
        'S_two.COMPLETION = NORMAL',
        '$failed_source_at(S_two.FAILEDSOURCES,2) = (pfailedsource_two)',
        'pfailedsource_two.KIND = FAILED_PARSE',
        'pfailedsource_two.SITE = pevalcontext_two.SITE',
        '$source_unit(S_two.SOURCES,2) = eps',
        '$code_at(S_two.CODE,2) = eps',
        'S_wait_three = $drive_steps(S_two,4096)',
        'S_wait_three.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_three.EVALCONTEXTS,3) = (pevalcontext_three)',
        'pevalcontext_three.BYTES = ' + term(codes[2]),
        'pevalcontext_three.FILE = ' + term(files[2]),
        'pevalcontext_three.SITE = pevalcontext_two.SITE',
        '$eval_response_valid(S_wait_three,' + responses[2] + ')',
        'S_three = $eval_resume(S_wait_three,' + responses[2] + ')',
        'S_three.COMPLETION = NORMAL',
        '$failed_source_at(S_three.FAILEDSOURCES,3) = (pfailedsource_three)',
        'pfailedsource_three.KIND = FAILED_PARSE',
        'pfailedsource_three.BYTES = ' + term(codes[2]),
        '$source_unit(S_three.SOURCES,3) = eps',
        '$code_at(S_three.CODE,3) = eps',
        'S_wait_four = $drive_steps(S_three,4096)',
        'S_wait_four.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_four.EVALCONTEXTS,4) = (pevalcontext_four)',
        'pevalcontext_four.BYTES = ' + term(codes[3]),
        'pevalcontext_four.FILE = ' + term(files[3]),
        '$eval_response_valid(S_wait_four,' + responses[3] + ')',
        'S_four = $eval_resume(S_wait_four,' + responses[3] + ')',
        'S_four.COMPLETION = NORMAL',
        'S_front_raw = $review_reject_seek(S_four,0,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$review_reject_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 4 pcpath_new)',
        '$anonymous_new_pending(S_front,PORIGIN 4 pcpath_new) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN 4 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc.NAME = ' + term(name),
        '~pclassdesc.EARLY',
        '$anonymous_history_seed(S_front,4) = (1)',
        '$class_named(S_front.CLASSNAMES,$ptascii("base151review")) = (porigin_base)',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        'S_front.SOURCES = [pcunit_root,pcunit_one,pcunit_four]',
        'pcunit_root.ID = 0',
        'pcunit_one.ID = 1',
        'pcunit_four.ID = 4',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        '$review_reject_entry(S_front.DECLARATIONS,2) = (pdeclaration_two)',
        '$review_reject_entry(S_front.DECLARATIONS,3) = (pdeclaration_three)',
        '$anonymous_parser_rejected(S_front,pdeclaration_two,2)',
        '$anonymous_parser_rejected(S_front,pdeclaration_three,3)',
        '$failed_source_record_valid(S_front,pfailedsource_two)',
        '$failed_source_record_valid(S_front,pfailedsource_three)',
        '$eval_binding_at(S_front.EVALBINDINGS,2) = eps',
        '$eval_binding_at(S_front.EVALBINDINGS,3) = eps',
        '$file_binding_at(S_front.FILEBINDINGS,2) = eps',
        '$file_binding_at(S_front.FILEBINDINGS,3) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_two,(PDEXIT 2 PCSREJECT),pdeclaration_three,(PDEXIT 3 PCSREJECT)],2,4,1) = (1)',
        '$anonymous_rtd_history(S_front,[pdeclaration_two],2,3,1) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_two,(PDEXIT 2 PCSCOMPLETE)],2,3,1) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_two,(PDEXIT 2 PCSCOMPILER)],2,3,1) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_two,(PDEXIT 3 PCSREJECT)],2,3,1) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_two,(PDEXIT 2 PCSREJECT),(PDEXIT 2 PCSREJECT)],2,3,1) = eps',
        '$anonymous_rtd_history(S_front,[pdeclaration_three,(PDEXIT 3 PCSREJECT),pdeclaration_two,(PDEXIT 2 PCSREJECT)],2,4,1) = eps',
        '~$anonymous_parser_rejected(S_front,pdeclaration_two,3)',
        '~$anonymous_parser_rejected(S_front[.FAILEDSOURCES = $review_reject_drop(S_front.FAILEDSOURCES,2)],pdeclaration_two,2)',
        '$declaration_entry_site(S_front.DECLARATIONS,1) = (porigin_other_site)',
        'porigin_other_site =/= pevalcontext_two.SITE',
        '~$anonymous_parser_rejected(S_front,$review_reject_site(pdeclaration_two,porigin_other_site),2)',
        '~$anonymous_parser_rejected(S_front[.SOURCES = S_front.SOURCES ++ [pcunit_one[.ID = 2]]],pdeclaration_two,2)',
        '$code_at(S_front.CODE,1) = (pcode_one)',
        '~$anonymous_parser_rejected(S_front[.CODE = S_front.CODE ++ [pcode_one[.UNIT = 2]]],pdeclaration_two,2)',
        '$eval_binding_at(S_front.EVALBINDINGS,1) = (pevalbinding_one)',
        '~$anonymous_parser_rejected(S_front[.EVALBINDINGS = S_front.EVALBINDINGS ++ [pevalbinding_one[.UNIT = 2]]],pdeclaration_two,2)',
        'S_front.CURRENT = (pcallcontext_factory)',
        'pcallcontext_factory.FUNCTION = PORIGIN 4 pcpath_factory',
        'pcallcontext_factory.LEXICAL_CLASS = eps',
        'pcallcontext_factory.CALLED_CLASS = eps',
        'pdeclcause = $declaration_cause(S_front)',
        'pdeclcause.UNIT = 4',
        'pdeclcause.AUTOLOAD = eps',
        '|pdeclcause.CALLS| = 1',
        '$review_reject_first_function(pdeclcause.CALLS) = pcallcontext_factory.FUNCTION',
        '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.UNIT = 2])',
        '$review_reject_function($all_functions(S_front),$ptascii("reject151Review")) = (porigin_wrong)',
        '$function_at($all_functions(S_front),porigin_wrong) = (pfunction_wrong)',
        '$declaration_callable_available(S_front,pfunction_wrong,|S_front.DECLARATIONS|)',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause[.CALLS = $review_reject_wrong_function(pdeclcause.CALLS,porigin_wrong)])',
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
        '$review_reject_count(S_linked.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$anonymous_new_pending(S_linked,PORIGIN 4 pcpath_new) = eps',
        'S_caught_raw = $review_reject_seek(S_linked,1,4096)',
        r'S_caught_raw.COMPLETION = NORMAL \/ S_caught_raw.COMPLETION = BUDGET',
        'S_caught = S_caught_raw[.COMPLETION = NORMAL]',
        '$review_reject_phase(S_caught,1)',
        'S_caught.DECLARATIONS = S_linked.DECLARATIONS',
        '$class_named(S_caught.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)',
        'S_retry_raw = $review_reject_seek(S_caught,0,4096)',
        r'S_retry_raw.COMPLETION = NORMAL \/ S_retry_raw.COMPLETION = BUDGET',
        'S_retry = S_retry_raw[.COMPLETION = NORMAL]',
        'S_retry.ORIGIN = (PORIGIN 4 pcpath_new)',
        '$anonymous_new_name(S_retry,PORIGIN 4 pcpath_new) = (pclassdesc.NAME)',
        '$anonymous_new_pending(S_retry,PORIGIN 4 pcpath_new) = eps',
        'S_retry.DECLARATIONS = S_linked.DECLARATIONS',
        'S_ctor_raw = $review_reject_seek(S_retry,2,4096)',
        r'S_ctor_raw.COMPLETION = NORMAL \/ S_ctor_raw.COMPLETION = BUDGET',
        'S_ctor = S_ctor_raw[.COMPLETION = NORMAL]',
        '$review_reject_phase(S_ctor,2)',
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        'pcallcontext_ctor.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_ctor.CALLED_CLASS = (pclassdesc.ORIGIN)',
        'pcallcontext_ctor.CALLSITE = (PORIGIN 4 pcpath_new)',
        'S_wait_five = $drive_steps(S_ctor,4096)',
        'S_wait_five.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait_five.EVALCONTEXTS,5) = (pevalcontext_five)',
        'pevalcontext_five.BYTES = ' + term(codes[4]),
        'pevalcontext_five.FILE = ' + term(files[4]),
        '$eval_response_valid(S_wait_five,' + responses[4] + ')',
        'S_five = $eval_resume(S_wait_five,' + responses[4] + ')',
        'S_five.COMPLETION = NORMAL',
        '$anonymous_history_seed(S_five,5) = (2)',
        '$class_named(S_five.CLASSNAMES,$ptlc(' + term(tail_name) + ')) = (porigin_tail)',
        '$class_at(S_five.CLASSES,porigin_tail) = (pclassdesc_tail)',
        'pclassdesc_tail.EARLY',
        'S_done = $drive_steps(S_five,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_reject_output(S_done.EVENTS) = ' + term(stdout),
        '$review_reject_count(S_done.DECLARATIONS,pclassdesc.ORIGIN) = 1',
        '$review_reject_count(S_done.DECLARATIONS,porigin_tail) = 0',
        '$anonymous_history_seed(S_done,4) = (1)',
        '$anonymous_history_seed(S_done,5) = (2)',
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
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row, = [row for row in json.loads(CATALOGUE.read_text())['cases'] if row['source_sha256'] == SOURCE_SHA]
    raw = Path(tempfile.mkdtemp(prefix='anonymous-rejected-source-cause-', dir=ROOT / '.tools'))
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
        for unit, prefix in [(1, b'$first = new class {};'), (2, b'$would = new class {};'), (3, b'class Never151Review {}'), (4, b'namespace Later151Review;'), (5, b'$tail = new class {};')]:
            code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                     if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(prefix)]
            codes.append(code)
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(unit), 'mode': 'eval',
                                            'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
            if unit in (2, 3):
                assert parsed_eval['accepted'] is False and parsed_eval['category'] == 'parser_rejection'
                assert parsed_eval['line'] > 0
                responses.append('SOURCE_PARSE_REJECT ' + str(unit) + ' ' + term(code) + ' ' +
                                 term(base64.b64decode(parsed_eval['message'])) + ' ' + str(parsed_eval['line']))
            else:
                assert parsed_eval['accepted'] is True
                checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
                assert checked_eval['ok'] is True
                responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(code) + ' ' + checked_eval['fixture'])
        checks = assertions(checked['fixture'], os.fsencode(source), stdout, codes, responses)
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
