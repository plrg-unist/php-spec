#!/usr/bin/env python3
"""Independent source-reached anonymous constructor publication history check."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_typed_property_cases.json'
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $review_cause_is_output(pevent) : bool
def $review_cause_is_output(OUTPUT ptbytes) = true
def $review_cause_is_output(pevent) = false -- otherwise
dec $review_cause_output(pevent*) : ptbytes
def $review_cause_output(eps) = eps
def $review_cause_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $review_cause_output(pevent*)
def $review_cause_output(pevent :: pevent_tail*) = $review_cause_output(pevent_tail*)
  -- if ~$review_cause_is_output(pevent)
dec $review_cause_front(pstate) : bool
def $review_cause_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S, porigin) = (pclassdesc)
  -- if pclassdesc.PARENT = ($ptascii("Base144CauseA"))
def $review_cause_front(S) = false -- otherwise
dec $review_cause_seek(pstate, nat) : pstate
def $review_cause_seek(S, n) = S -- if $review_cause_front(S)
def $review_cause_seek(S, 0) = S -- if ~$review_cause_front(S)
def $review_cause_seek(S, n) = $review_cause_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$review_cause_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $review_cause_seek(S, n) = S -- otherwise
dec $review_cause_function(pdeclcalls) : porigin
def $review_cause_function((porigin,porigin_site?,porigin_scope?,porigin_called?) :: pdeclcalls) = porigin
dec $review_cause_site(pdeclcalls) : porigin?
def $review_cause_site((porigin,porigin_site?,porigin_scope?,porigin_called?) :: pdeclcalls) = porigin_site?
dec $review_cause_wrong_calls(pdeclcalls) : pdeclcalls
def $review_cause_wrong_calls([(porigin_make,porigin_make_site?,porigin_make_scope?,porigin_make_called?),(porigin_ctor,porigin_ctor_site?,porigin_ctor_scope?,porigin_ctor_called?)]) = [(porigin_make,porigin_make_site?,porigin_make_scope?,porigin_make_called?),(porigin_ctor,porigin_ctor_site?,porigin_ctor_scope?,porigin_ctor_scope?)]
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checks(fixture, filename, stdout):
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_found = $review_cause_seek(S_initial,4096)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_front = S_found[.COMPLETION = NORMAL]',
        '$review_cause_front(S_front)',
        'S_front.ORIGIN = (porigin_front)',
        '$anonymous_new_pending(S_front,porigin_front) = (pclassdesc)',
        '~pclassdesc.EARLY',
        'pclassdesc.PARENT = (ptbytes_parent)',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$class_link_at(S_front.LINKEDPARENTS,pclassdesc.ORIGIN) = eps',
        '~$anonymous_runtime_declaration(S_front.DECLARATIONS,pclassdesc.ORIGIN)',
        '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'pdeclcause = $declaration_cause(S_front)',
        'pdeclcause.UNIT = 0',
        'pdeclcause.AUTOLOAD = eps',
        '|pdeclcause.CALLS| = 2',
        '$declaration_caller_lexical(pdeclcause.CALLS) = eps',
        '$declaration_caller_called(pdeclcause.CALLS) = eps',
        'pdeclcalls_ctor = pdeclcause.CALLS[1:1]',
        'porigin_ctor = $review_cause_function(pdeclcalls_ctor)',
        '$review_cause_site(pdeclcalls_ctor) = (porigin_ctor_site)',
        '$declaration_caller_lexical(pdeclcalls_ctor) = (porigin_owner)',
        '$declaration_caller_called(pdeclcalls_ctor) = (porigin_called)',
        'porigin_called =/= porigin_owner',
        '$class_at(S_front.CLASSES,porigin_owner) = (pclassdesc_owner)',
        'pclassdesc_owner.NAME = $ptascii("Base144CauseB")',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc_owner.NAME)) = (porigin_owner)',
        '$class_at(S_front.CLASSES,porigin_called) = (pclassdesc_called)',
        '$class_named(S_front.CLASSNAMES,$ptlc(pclassdesc_called.NAME)) = (porigin_called)',
        '$class_method_origin(S_front.CLASSES,porigin_ctor) = (pmethoddesc_ctor)',
        'pmethoddesc_ctor.OWNER = porigin_owner',
        '$effective_method(S_front,porigin_owner,$ptascii("__construct"),|S_front.CLASSES|) = (pmethoddesc_ctor)',
        '$origin_node(S_front.SOURCES,porigin_ctor_site) = (NExprNew phpType28_ctor (SEQUENCE phpType7_ctor*) metadata_ctor)',
        '$declaration_new_selection(S_front,porigin_ctor_site,phpType28_ctor,porigin_called,eps)',
        '~$declaration_new_selection(S_front,porigin_ctor_site,phpType28_ctor,porigin_owner,eps)',
        '$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause)',
        'pdeclcause_wrong_called = pdeclcause[.CALLS = $review_cause_wrong_calls(pdeclcause.CALLS)]',
        '~$declaration_cause_valid(S_front,pclassdesc.ORIGIN,pdeclcause_wrong_called)',
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
        '$class_link_at(S_linked.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_parent)',
        '$anonymous_runtime_declaration(S_linked.DECLARATIONS,pclassdesc.ORIGIN)',
        '$anonymous_new_pending(S_linked,porigin_front) = eps',
        '$anonymous_new_name(S_linked,porigin_front) = (pclassdesc.NAME)',
        '$call_descriptors_valid(S_linked)',
        '$class_state_valid(S_linked)',
        '$heap_valid($heap_graph(S_linked))',
        'S_done = $drive_steps(S_linked,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$review_cause_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases']
               if row['source_sha256'] == 'f3c734088e2669e77c0183e1178fea6f86e0bfb7e507d676f2ea63783d8b5063')
    raw = Path(tempfile.mkdtemp(prefix='anonymous-typed-cause-', dir=ROOT / '.tools'))
    source = raw / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(
        b'{FILE}', os.fsencode(source))
    watched = [ROOT / 'spec/semantics' / name for name in (
        '30-storage.watsup', '53-incdec.watsup', '95-type-values.watsup',
        '135-property-compiler.watsup', '136-property-runtime.watsup',
        '138-property-references.watsup', '190-declaration-publication.watsup',
        '195-declaration-history.watsup', '196-declaration-causes.watsup',
        '238-trait-data.watsup', '359-instance-storage-pin.watsup',
        '383-anonymous-classes.watsup', 'modules.json')]
    watched += [ROOT / '_build/default/adapter/main.exe',
                ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                CATALOGUE, Path(__file__), source]
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'source_sha256': sha(source), 'inputs_before': before,
              'parent_affinity': sorted(os.sched_getaffinity(0)), 'raw': str(raw)}
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
        assertions = checks(checked['fixture'], base64.b64encode(os.fsencode(source)).decode(),
                            stdout)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in assertions))
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *[str(ROOT / module) for module in modules], str(fixture)],
                                      raw / 'numeric', 180, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(assertions), fixture_sha256=sha(fixture))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
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
