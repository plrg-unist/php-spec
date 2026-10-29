#!/usr/bin/env python3
"""Check source-reached anonymous inheritance selection and constructor order."""
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
CASES = {'anonymous-parent-inherited-constructor',
         'anonymous-parent-override-parent-constructor'}
CATALOGUE = ROOT / 'tests/semantics/anonymous_parent_cases.json'

PREFIX = r'''
dec $anon_parent_is_output(pevent) : bool
def $anon_parent_is_output(OUTPUT ptbytes) = true
def $anon_parent_is_output(pevent) = false -- otherwise
dec $anon_parent_output(pevent*) : ptbytes
def $anon_parent_output(eps) = eps
def $anon_parent_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $anon_parent_output(pevent*)
def $anon_parent_output(pevent :: pevent_tail*) = $anon_parent_output(pevent_tail*)
  -- if ~$anon_parent_is_output(pevent)
dec $anon_parent_publication(pdeclaration,porigin) : nat
def $anon_parent_publication(PDRCLASS porigin pdeclcause,porigin) = 1
def $anon_parent_publication(pdeclaration,porigin) = 0 -- otherwise
dec $anon_parent_publications(pdeclaration*,porigin) : nat
def $anon_parent_publications(eps,porigin) = 0
def $anon_parent_publications(pdeclaration :: pdeclaration_tail*,porigin) = $($anon_parent_publication(pdeclaration,porigin) + $anon_parent_publications(pdeclaration_tail*,porigin))
dec $anon_parent_front(pstate) : bool
def $anon_parent_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN 0 pcpath)
  -- if phpType7* =/= eps
def $anon_parent_front(S) = false -- otherwise
dec $anon_parent_seek(pstate,nat) : pstate
def $anon_parent_seek(S,n) = S -- if $anon_parent_front(S)
def $anon_parent_seek(S,0) = S -- if ~$anon_parent_front(S)
def $anon_parent_seek(S,n) = $anon_parent_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_parent_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $anon_parent_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, fixture, filename, stdout):
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_front_found = $anon_parent_seek(S_initial,4096)',
        r'S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET',
        'S_front = S_front_found[.COMPLETION = NORMAL]',
        '$anon_parent_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 0 pcpath)',
        'S_front.TODO = (EVAL expression_new) :: ptask_tail*',
        '$anonymous_new_task_valid(S_front,expression_new)',
        '$anonymous_new_descriptor(S_front,PORIGIN 0 pcpath) = (pclassdesc)',
        'ptbytes_class = pclassdesc.NAME',
        'porigin_class = pclassdesc.ORIGIN',
        '~pclassdesc.EARLY',
        '$anonymous_new_pending(S_front,PORIGIN 0 pcpath) = (pclassdesc)',
        '$anonymous_new_name(S_front,PORIGIN 0 pcpath) = eps',
        '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_class)) = eps',
        '$class_at(S_front.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.PARENT = (ptbytes_parent)',
        'ptbytes_class = ptbytes_parent ++ $ptascii("@anonymous") ++ [0] ++ $base64(' + json.dumps(filename) + ') ++ [58] ++ $ntunsigned(pclassdesc.LINE) ++ [36,48]',
        '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$class_link_at(S_front.LINKEDPARENTS,porigin_class) = eps',
        '$anon_parent_publications(S_front.DECLARATIONS,porigin_class) = 0',
        '$class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.PROPERTIES =/= eps',
        'pclassdesc_parent.METHODS =/= eps',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'S_forged = S_front[.ORIGIN = (PORIGIN 0 (pcpath ++ [PCFIELD 1]))]',
        '~$anonymous_new_task_valid(S_forged,expression_new)',
        'expression_new = NExprNew phpType28 (SEQUENCE phpType7*) metadata_new',
        'expression_wrong = NExprNew phpType28 (SEQUENCE eps) metadata_new',
        '~$anonymous_new_task_valid(S_front,expression_wrong)',
        'S_linked_raw = $drive_steps(S_front,1)',
        r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
        'S_linked = S_linked_raw[.COMPLETION = NORMAL]',
        'S_linked.TODO = S_front.TODO',
        'S_linked.ORIGIN = S_front.ORIGIN',
        'S_linked.OBJECTS = S_front.OBJECTS',
        'S_linked.ALLOCATIONS = S_front.ALLOCATIONS',
        'S_linked.EVENTS = S_front.EVENTS',
        '$class_named(S_linked.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_class)',
        '$class_link_at(S_linked.LINKEDPARENTS,porigin_class) = (SOURCE_PARENT porigin_parent)',
        '$anon_parent_publications(S_linked.DECLARATIONS,porigin_class) = 1',
        '~$declaration_early(S_linked.DECLARATIONS,porigin_class,PPCLASS)',
        '$anonymous_new_name(S_linked,PORIGIN 0 pcpath) = (ptbytes_class)',
        '$anonymous_new_pending(S_linked,PORIGIN 0 pcpath) = eps',
        '$class_state_valid(S_linked)',
        '$heap_valid($heap_graph(S_linked))',
        'S_selected_raw = $drive_steps(S_linked,1)',
        r'S_selected_raw.COMPLETION = NORMAL \/ S_selected_raw.COMPLETION = BUDGET',
        'S_selected = S_selected_raw[.COMPLETION = NORMAL]',
        'S_selected.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7* 0 eps (porigin_site) z_call) :: (CTOR_RESULT n_object) :: ptask_selected*',
        'porigin_site = PORIGIN 0 pcpath',
        'S_selected.OBJECTS[n_object] = INSTANCE porigin_class',
        '$effective_method(S_selected,porigin_class,$ptascii("__construct"),|S_selected.CLASSES|) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$effective_method(S_selected,porigin_parent,$ptascii("__construct"),|S_selected.CLASSES|) = (pmethoddesc_parent)',
        '$call_task_valid(S_selected,S_selected.TODO[0])',
        '$class_state_valid(S_selected)',
        '$heap_valid($heap_graph(S_selected))',
    ]
    if case == 'anonymous-parent-inherited-constructor':
        checks.append('pmethoddesc = pmethoddesc_parent')
    else:
        checks.append('pmethoddesc.FUNCTION.ORIGIN =/= pmethoddesc_parent.FUNCTION.ORIGIN')
    checks += [
        'S_done = $drive_steps(S_selected,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$anon_parent_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$anon_parent_publications(S_done.DECLARATIONS,porigin_class) = 1',
        '$class_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=sorted(CASES), required=True)
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == args.case)
    out = Path(tempfile.mkdtemp(prefix='anonymous-parent-' + args.case + '-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    watched = [ROOT / 'spec/semantics/383-anonymous-classes.watsup', CATALOGUE,
               ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe']
    watched += [ROOT / 'spec/semantics' / name for name in (
        '30-storage.watsup', '53-incdec.watsup', '95-type-values.watsup',
        '135-property-compiler.watsup', '136-property-runtime.watsup',
        '138-property-references.watsup', '238-trait-data.watsup',
        '359-instance-storage-pin.watsup')]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'passed': False, 'case': args.case, 'source_sha256': sha(source),
              'inputs_before': before, 'raw': str(out)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        filename = base64.b64encode(os.fsencode(source)).decode()
        checks = assertions(args.case, checked['fixture'], filename,
                            base64.b64decode(row['stdout_base64']))
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + 'dec $body() : bool\ndef $body() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks) +
                           'dec $main() : bool\ndef $main() = $body()\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *[str(ROOT / module) for module in modules], str(fixture)],
                                      out / 'numeric', 120, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(checks), fixture_sha256=sha(fixture))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['inputs_after'] = {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
