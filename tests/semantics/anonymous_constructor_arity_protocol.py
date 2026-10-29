#!/usr/bin/env python3
"""Real finite anonymous constructor formals, sends and source-bound call tasks."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_arity_cases.json'
CASES = {'anonymous-arity-root-required-four-extra-send'}

PREFIX = r'''
dec $arity_is_output(pevent) : bool
def $arity_is_output(OUTPUT ptbytes) = true
def $arity_is_output(pevent) = false -- otherwise
dec $arity_output(pevent*) : ptbytes
def $arity_output(eps) = eps
def $arity_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $arity_output(pevent*)
def $arity_output(pevent :: pevent_tail*) = $arity_output(pevent_tail*)
  -- if ~$arity_is_output(pevent)
dec $arity_front(pstate) : bool
def $arity_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if $(|phpType7*| = 5)
  -- if S.ORIGIN = (PORIGIN 0 pcpath)
  -- if $origin_node(S.SOURCES, PORIGIN 0 pcpath) = (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)
def $arity_front(S) = false -- otherwise
dec $arity_seek(pstate,nat) : pstate
def $arity_seek(S,n) = S -- if $arity_front(S)
def $arity_seek(S,0) = S -- if ~$arity_front(S)
def $arity_seek(S,n) = S -- if S.TODO = eps /\ ~$arity_front(S)
def $arity_seek(S,n) = S_next
  -- if $(n > 0) /\ ~$arity_front(S) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] = S[.COMPLETION = NORMAL]
def $arity_seek(S,n) = $arity_seek(S_next,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$arity_front(S) /\ S.TODO =/= eps
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_next = $drive_steps(S[.COMPLETION = NORMAL],1)
  -- if S_next[.COMPLETION = NORMAL] =/= S[.COMPLETION = NORMAL]
def $arity_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, initial, filename, stdout):
    checks = [
        'program_source = ' + initial,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        'S_initial.COMPLETION = BUDGET',
        '~S_initial.COMPILESTOP',
        'S_front_found = $arity_seek(S_initial[.COMPLETION = NORMAL],4096)',
        r'S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET',
        'S_front = S_front_found[.COMPLETION = NORMAL]',
        '$arity_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 0 pcpath)',
        'S_front.TODO = (EVAL expression_new) :: ptask_tail*',
        'expression_new = NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new',
        '$(|phpType7*| = 5)',
        '$anonymous_new_task_valid(S_front,expression_new)',
        '$anonymous_new_descriptor(S_front,PORIGIN 0 pcpath) = (pclassdesc)',
        '$anonymous_new_name(S_front,PORIGIN 0 pcpath) = (pclassdesc.NAME)',
        'pclassdesc.EARLY',
        '$class_state_valid(S_front)',
        '$call_descriptors_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'S_wrong_site = S_front[.ORIGIN = (PORIGIN 0 (pcpath ++ [PCFIELD 1]))]',
        '~$anonymous_new_task_valid(S_wrong_site,expression_new)',
        '$effective_method(S_front,pclassdesc.ORIGIN,$ptascii("__construct"),|S_front.CLASSES|) = (pmethoddesc)',
        'pmethoddesc.OWNER = pclassdesc.ORIGIN',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc.STATIC',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_d]',
        'psparam_a.NAME = $ptascii("a")',
        'psparam_b.NAME = $ptascii("b")',
        'psparam_c.NAME = $ptascii("c")',
        'psparam_d.NAME = $ptascii("d")',
        'psparam_a.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        'psparam_b.TYPE = eps',
        'psparam_c.TYPE = psparam_a.TYPE',
        'psparam_d.TYPE = psparam_a.TYPE',
        r'psparam_a.REQUIRED /\ psparam_b.REQUIRED /\ psparam_c.REQUIRED /\ psparam_d.REQUIRED',
        r'psparam_a.DEFAULT = PSNONE /\ psparam_b.DEFAULT = PSNONE /\ psparam_c.DEFAULT = PSNONE /\ psparam_d.DEFAULT = PSNONE',
        r'~psparam_a.BYREF /\ ~psparam_b.BYREF /\ ~psparam_c.BYREF /\ ~psparam_d.BYREF',
        r'~psparam_a.VARIADIC /\ ~psparam_b.VARIADIC /\ ~psparam_c.VARIADIC /\ ~psparam_d.VARIADIC',
        'S_selected_raw = $drive_steps(S_front,1)',
        r'S_selected_raw.COMPLETION = NORMAL \/ S_selected_raw.COMPLETION = BUDGET',
        'S_selected = S_selected_raw[.COMPLETION = NORMAL]',
        'S_selected.DECLARATIONS = S_front.DECLARATIONS',
        'S_selected.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7* 0 eps (porigin_site) z_call) :: (CTOR_RESULT n_object) :: ptask_selected*',
        'porigin_site = PORIGIN 0 pcpath',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
        'S_selected.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
        '(HOBJECT n_object) <- S_selected.ALLOCATIONS',
        '$arity_output(S_selected.EVENTS) = $arity_output(S_front.EVENTS)',
        '$call_task_valid(S_selected,S_selected.TODO[0])',
        '$call_task_valid(S_selected,CTOR_RESULT n_object)',
        '~$call_task_valid(S_selected,CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7*[0:4] 0 eps (porigin_site) z_call)',
        '~$call_task_valid(S_selected,CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7* 0 eps (PORIGIN 0 (pcpath ++ [PCFIELD 1])) z_call)',
        '$call_descriptors_valid(S_selected)',
        '$heap_valid($heap_graph(S_selected))',
        'S_done = $drive_steps(S_selected,8192)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$arity_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$class_state_valid(S_done)',
        '$call_descriptors_valid(S_done)',
        '$declaration_history_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=sorted(CASES), required=True)
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    catalogue = json.loads(CATALOGUE.read_text())
    selected = [row for row in catalogue['cases'] if row['id'] in CASES]
    assert {row['id'] for row in selected} == CASES
    row = next(row for row in selected if row['id'] == args.case)
    out = Path(tempfile.mkdtemp(prefix='anonymous-constructor-arity-' + args.case + '-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    watched = [ROOT / 'spec/semantics/383-anonymous-classes.watsup', CATALOGUE,
               ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/anonymous_constructor_arity_protocol.py']
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
        stdout = base64.b64decode(row['stdout_template_base64'] if 'stdout_template_base64' in row else row['stdout_base64']).replace(b'{FILE}', os.fsencode(source))
        checks = assertions(args.case, checked['fixture'], filename, stdout)
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + 'dec $body() : bool\ndef $body() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks) +
                           'dec $main() : bool\ndef $main() = $body()\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                       *[str(ROOT / module) for module in modules], str(fixture)],
                                      out / 'numeric', 480, ROOT)
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
