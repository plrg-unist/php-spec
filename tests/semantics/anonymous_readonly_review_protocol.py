#!/usr/bin/env python3
"""Independent readonly anonymous clone, parent, eval and linking fronts."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_readonly_cases.json'
PREFIX = r'''
dec $class176_review_outputs(pevent*) : ptbytes
dec $class176_review_output(pevent) : ptbytes
def $class176_review_outputs(eps) = eps
def $class176_review_outputs(pevent :: pevent_tail*) = $class176_review_output(pevent) ++ $class176_review_outputs(pevent_tail*)
def $class176_review_output(OUTPUT ptbytes) = ptbytes
def $class176_review_output(pevent) = eps -- otherwise
dec $class176_review_front(pstate,nat) : bool
def $class176_review_front(S,0) = true
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
def $class176_review_front(S,1) = (S.CLONES =/= eps /\ $class176_review_outputs(S.EVENTS) = $ptascii("clone;"))
def $class176_review_front(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if $class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__clone")
  -- if S.CLONES = eps
def $class176_review_front(S,3) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*
def $class176_review_front(S,4) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("accepts")
def $class176_review_front(S,5) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) =/= eps
def $class176_review_front(S,n) = false -- otherwise
dec $class176_review_seek(pstate,nat,nat) : pstate
def $class176_review_seek(S,n_front,0) = S
def $class176_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class176_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class176_review_seek(S,n_front,n) = $class176_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class176_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
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


def fatal_message(row):
    return base64.b64decode(row['stderr_template_base64']).split(b'Fatal error: ',1)[1].split(b' in {FILE} on line ',1)[0]


def initial(fixture, filename):
    return ['program_source = ' + fixture,
            'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']


def seek(parent, state, front):
    return [state + '_found = $class176_review_seek(' + parent + ',' + str(front) + ',2400)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$class176_review_front(' + state + ',' + str(front) + ')']


def final_checks(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps /\\ ' + state + '.CURRENT = eps /\\ ' + state + '.FRAMES = eps',
            '$class176_review_outputs(' + state + '.EVENTS) = ' + term(expected),
            '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
            '$declaration_history_valid(' + state + ')']


def clone_checks(row, fixture, filename):
    return initial(fixture,filename) + [
        *seek('S_initial','S_enter',0),
        'S_enter.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_enter_tail*',
        'S_enter.CLONES = [pclonewindow]',
        'pclonewindow.OPERATION = pcloneoperation /\\ pclonewindow.PHASE = CLONE_CALLBACK',
        'pclonewindow.AVAILABLE = [$ptascii("value")] /\\ pclonewindow.REVISIONS = [{KEY $ptascii("value"), COUNT 0}]',
        'n_source = pcloneoperation.SOURCE',
        'n_copy = pcloneoperation.TARGET',
        'n_source =/= n_copy /\\ pcloneoperation.CALL = eps',
        'S_enter.OBJECTS[n_source] = INSTANCE porigin_class',
        'S_enter.OBJECTS[n_copy] = INSTANCE porigin_class',
        '$class_at(S_enter.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.READONLY',
        'pclassdesc.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.READONLY /\\ ppropertydesc.KEY = $ptascii("value")',
        '$clone_operation_valid(S_enter,pcloneoperation)',
        '$call_task_valid(S_enter,CLONE_CALLBACK_ENTER pcloneoperation)',
        '$clone_windows_valid(S_enter)',
        '$clone_reinitable(S_enter,n_copy,ppropertydesc.KEY) /\\ ~$clone_reinitable(S_enter,n_source,ppropertydesc.KEY)',
        '$location_slot(S_enter,PROPERTY n_source ppropertydesc.KEY) = DEFINED (PINT 5)',
        '$location_slot(S_enter,PROPERTY n_copy ppropertydesc.KEY) = DEFINED (PINT 5)',
        *seek('S_enter','S_written',1),
        'S_written.CLONES = [pclonewindow[.AVAILABLE = eps][.REVISIONS = [{KEY $ptascii("value"), COUNT 1}]]]',
        '$location_slot(S_written,PROPERTY n_source ppropertydesc.KEY) = DEFINED (PINT 5)',
        '$location_slot(S_written,PROPERTY n_copy ppropertydesc.KEY) = DEFINED (PINT 6)',
        '~$clone_reinitable(S_written,n_copy,ppropertydesc.KEY)',
        '$clone_windows_valid(S_written)',
        'S_reopened = S_written[.CLONES = [pclonewindow[.REVISIONS = [{KEY $ptascii("value"), COUNT 1}]]]]',
        '~$clone_windows_valid(S_reopened)',
        *seek('S_written','S_manual',2),
        'S_manual.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_copy porigin_method',
        '~$clone_context_kind(S_manual,pcallcontext) /\\ S_manual.CLONES = eps',
        '~$clone_reinitable(S_manual,n_copy,ppropertydesc.KEY)',
        'S_done = $drive_steps(S_manual,4000)',
        *final_checks(row,'S_done',filename),
        'S_done.CLONES = eps /\\ $clone_windows_valid(S_done)',
        '$location_slot(S_done,PROPERTY n_source ppropertydesc.KEY) = DEFINED (PINT 5)',
        '$location_slot(S_done,PROPERTY n_copy ppropertydesc.KEY) = DEFINED (PINT 6)',
    ]


def parent_checks(row, fixture, filename):
    name = b'Probe176Base@anonymous\0' + filename + b':7$0'
    return initial(fixture,filename) + [
        *seek('S_initial','S_promote',3),
        'S_promote.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
        'S_promote.CURRENT = (pcallcontext)',
        'pcallcontext.RECEIVER = (n_object)',
        'S_promote.OBJECTS[n_object] = INSTANCE porigin_class',
        '$class_at(S_promote.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.READONLY /\\ pclassdesc.NAME = ' + term(name),
        '$class_named(S_promote.CLASSNAMES,$ptascii("probe176base")) = (porigin_parent)',
        '$class_at(S_promote.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.READONLY',
        'pclassdesc_parent.PROPERTIES = [ppropertydesc_parent]',
        'pclassdesc.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.READONLY /\\ ppropertydesc_parent.READONLY',
        'ppropertydesc.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("value")',
        'ppropertydesc_parent.KEY = [0] ++ $ptascii("Probe176Base") ++ [0] ++ $ptascii("value")',
        'ppropertydesc.KEY =/= ppropertydesc_parent.KEY',
        'porigin_ctor = PORIGIN 0 pcpath_ctor',
        'ppropertydesc.ORIGIN = PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 0])',
        '$origin_node(S_promote.SOURCES,PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 4) phpType18 phpType4_ref phpType4_var phpType10 phpType5 (SEQUENCE eps) metadata)',
        '$receiving_function(S_promote,porigin_ctor) = (pfunction)',
        '$promotion_descriptor(S_promote,pfunction,0) = (ppropertydesc)',
        '$promotion_task_valid(S_promote,porigin_ctor,0)',
        '$location_slot(S_promote,PROPERTY n_object ppropertydesc.KEY) = UNDEFINED',
        '$location_slot(S_promote,PROPERTY n_object ppropertydesc_parent.KEY) = UNDEFINED',
        'S_wrong_property = S_promote[.CLASSES = $trait_class_set(S_promote.CLASSES,pclassdesc[.PROPERTIES = [ppropertydesc[.READONLY = false]]])]',
        '$promotion_descriptor(S_wrong_property,pfunction,0) = eps',
        'S_wrong_header = S_promote[.CLASSES = $trait_class_set(S_promote.CLASSES,pclassdesc[.READONLY = false])]',
        '~$declaration_history_valid(S_wrong_header)',
        '$source_unit(S_promote.SOURCES,0) = (pcunit)',
        '$compilation_projection(S_promote,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,porigin_class) = (pclassdesc_compiled)',
        '$anonymous_class_count(pcunit,' + term(filename) + ',ppinstalled.CLASSES,eps,0) = (1)',
        '$anonymous_class_count(pcunit,' + term(filename) + ',$trait_class_set(ppinstalled.CLASSES,pclassdesc_compiled[.READONLY = false]),eps,0) = eps',
        'S_written = $drive_steps(S_promote,1)',
        'S_written.COMPLETION = BUDGET',
        '$location_slot(S_written,PROPERTY n_object ppropertydesc.KEY) = DEFINED (PINT 5)',
        '$location_slot(S_written,PROPERTY n_object ppropertydesc_parent.KEY) = UNDEFINED',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL],4000)',
        *final_checks(row,'S_done',filename),
        '$location_slot(S_done,PROPERTY n_object ppropertydesc.KEY) = DEFINED (PINT 5)',
        '$location_slot(S_done,PROPERTY n_object ppropertydesc_parent.KEY) = DEFINED (PINT 1)',
    ]


def dynamic_checks(row, fixture, filename, responses):
    virtual = [filename + b'(' + str(line).encode() + b") : eval()'d code" for line in [6,7]]
    names = [b'class@anonymous\0' + file + b':1$' + str(index).encode() for index,file in enumerate(virtual)]
    out = [
        'program_source = ' + fixture,
        'S_wait1 = $php_run(program_source,1600,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_wait1.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_promote1 = $class176_review_seek($eval_resume(S_wait1,' + responses[0] + '),3,1600)',
        '$class176_review_front(S_promote1,3) /\\ S_promote1.COMPLETION = BUDGET',
        'S_wait2 = $drive_steps(S_promote1[.COMPLETION = NORMAL],2000)',
        'S_wait2.COMPLETION = SOURCE_PENDING /\\ S_wait2.EVENTS = eps',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_promote2 = $class176_review_seek($eval_resume(S_wait2,' + responses[1] + '),3,1600)',
        '$class176_review_front(S_promote2,3) /\\ S_promote2.COMPLETION = BUDGET',
        '$source_unit(S_promote2.SOURCES,1) = (pcunit_one)',
        '$source_unit(S_promote2.SOURCES,2) = (pcunit_two)',
        'pcunit_one.AST = pcunit_two.AST',
    ]
    for number,label in [(1,'one'),(2,'two')]:
        state,cls,prop = 'S_promote' + str(number),'pclassdesc_' + label,'ppropertydesc_' + label
        out += [
            state + '.TODO = (PROMOTE_PARAMETER porigin_ctor_' + label + ' 0) :: ptask_' + label + '*',
            state + '.CURRENT = (pcallcontext_' + label + ')',
            'pcallcontext_' + label + '.RECEIVER = (n_' + label + ')',
            state + '.OBJECTS[n_' + label + '] = INSTANCE porigin_class_' + label,
            '$class_at(' + state + '.CLASSES,porigin_class_' + label + ') = (' + cls + ')',
            cls + '.NAME = ' + term(names[number-1]) + ' /\\ ' + cls + '.READONLY',
            '$anonymous_history_seed(' + state + ',' + str(number) + ') = (' + str(number-1) + ')',
            '$declaration_unit_complete(' + state + '.DECLARATIONS,' + str(number) + ')',
            cls + '.PROPERTIES = [' + prop + ']',
            prop + '.ORIGIN = PORIGIN ' + str(number) + ' pcpath_parameter_' + label,
            prop + '.READONLY /\\ ' + prop + '.DEFAULT = PROP_UNINITIALIZED /\\ ' + prop + '.KEY = $ptascii("value")',
            '$receiving_function(' + state + ',porigin_ctor_' + label + ') = (pfunction_ctor_' + label + ')',
            '$promotion_descriptor(' + state + ',pfunction_ctor_' + label + ',0) = (' + prop + ')',
            '$promotion_task_valid(' + state + ',porigin_ctor_' + label + ',0)',
            'S_bad_' + label + ' = ' + state + '[.CLASSES = $trait_class_set(' + state + '.CLASSES,' + cls + '[.READONLY = false])]',
            '~$declaration_history_valid(S_bad_' + label + ')',
        ]
    out += [
        'porigin_class_one =/= porigin_class_two /\\ pclassdesc_one.NAME =/= pclassdesc_two.NAME',
        'ppropertydesc_one.ORIGIN =/= ppropertydesc_two.ORIGIN /\\ n_one =/= n_two',
        'S_receive1 = $class176_review_seek(S_promote2,4,2400)',
        '$class176_review_front(S_receive1,4) /\\ S_receive1.COMPLETION = BUDGET',
        'S_receive2 = $class176_review_seek($drive_steps(S_receive1[.COMPLETION = NORMAL],1),4,2400)',
        '$class176_review_front(S_receive2,4) /\\ S_receive2.COMPLETION = BUDGET',
    ]
    for number,label in [(1,'one'),(2,'two')]:
        state,cls = 'S_receive' + str(number),'pclassdesc_' + label
        out += [
            '$method_named(' + cls + '.METHODS,$ptascii("accepts")) = (pmethoddesc_' + label + ')',
            'pmethoddesc_' + label + '.FUNCTION.SIGNATURE.PARAMETERS = [psparam_' + label + ']',
            'psparam_' + label + '.TYPE = [(PTBRANCH ([PTCLASS ' + cls + '.NAME]))]',
            state + '.TODO = (TYPE_RECEIVE pmethoddesc_' + label + '.FUNCTION.ORIGIN 0) :: ptask_receive_' + label + '*',
            state + '.CURRENT = (pcallcontext_receive_' + label + ')',
            'pcallcontext_receive_' + label + '.TARGET = METHOD_TARGET n_' + label + ' pmethoddesc_' + label + '.FUNCTION.ORIGIN',
            'pcallcontext_receive_' + label + '.LEXICAL_CLASS = (' + cls + '.ORIGIN) /\\ pcallcontext_receive_' + label + '.CALLED_CLASS = (' + cls + '.ORIGIN)',
            '$lookup(' + state + '.ENV,$ptascii("object")) = (n_argument_' + label + ')',
            state + '.STORE[n_argument_' + label + '] = DEFINED (POBJECT n_' + label + ')',
            '$call_current_valid(' + state + ')',
        ]
    return out + [
        'S_done = $drive_steps(S_receive2[.COMPLETION = NORMAL],4000)',
        *final_checks(row,'S_done',filename),
        'S_done.EVALCONTEXTS = eps',
        '$location_slot(S_done,PROPERTY n_one $ptascii("value")) = DEFINED (PINT 5)',
        '$location_slot(S_done,PROPERTY n_two $ptascii("value")) = DEFINED (PINT 5)',
    ]


def boundary_checks(row, fixture, filename, compile_fixture=None, compile_row=None):
    prefix = b'class@anonymous' if 'trait' in row['id'] else b'Probe176OrdinaryParent@anonymous'
    name = prefix + b'\0' + filename + b':5$0'
    out = initial(fixture,filename) + [
        *seek('S_initial','S_pre',5),
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(name) + ' /\\ pclassdesc.READONLY /\\ ~pclassdesc.EARLY',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        'S_pre.EVENTS = [OUTPUT $ptascii("before;")] /\\ S_pre.OBJECTS = eps',
        'S_fatal = $drive_steps(S_pre,1)',
        'S_fatal.COMPLETION = STATICBYTES ' + term(fatal_message(row)) + ' 5',
        'S_fatal.EVENTS = S_pre.EVENTS /\\ S_fatal.OBJECTS = eps',
        '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc.ORIGIN)',
    ]
    if compile_fixture is not None:
        out += [
            'S_compile = $php_run(' + compile_fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            'S_compile.COMPLETION = STATICBYTES ' + term(fatal_message(compile_row)) + ' 4',
            'S_compile.OBJECTS = eps /\\ S_compile.EVENTS = eps',
        ]
    return out


def main():
    os.environ.update(LC_ALL='C',TZ='UTC',GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']:row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['readonly-clone-once-and-manual-clone-refusal',
                'readonly-parent-private-slot-identities',
                'readonly-eval-recompiled-values-and-self-scopes',
                'readonly-nonreadonly-trait-before-argument',
                'readonly-nonreadonly-parent-before-argument']
    raw = Path(tempfile.mkdtemp(prefix='class176-review-state-',dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json',CATALOGUE,Path(__file__),
               ROOT / '.tools/php/bin/php',ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe',ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / 'frontend/worker.php',ROOT / 'spec/semantics/383-anonymous-classes.watsup',
               ROOT / 'spec/semantics/238-trait-data.watsup']
    before = {str(path):sha(path) for path in watched}
    report = {'passed':False,'raw':str(raw),'inputs_before':before,
              'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'affinity':sorted(os.sched_getaffinity(0)),'environment':{'LC_ALL':'C','TZ':'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,
                           '-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],raw / 'adapter')
        compile_row = rows['readonly-untyped-property-compile-error']
        parsed_compile = frontend.request({'op':'parse','source':base64.b64encode(compile_row['source'].encode()).decode()})
        assert parsed_compile['accepted']
        checked_compile = adapter.request({'op':'check','ast':parsed_compile['ast'],'fixture':True})
        assert checked_compile['ok']
        code,groups,counts = PREFIX,[],{}
        for index,name in enumerate(selected):
            row = rows[name]
            path = raw / (name + '.php')
            path.write_text(row['source'])
            assert sha(path) == row['source_sha256']
            parsed = frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok']
            if name == 'readonly-eval-recompiled-values-and-self-scopes':
                body, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'return new readonly class')]
                responses = []
                for unit in [1,2]:
                    parsed_body = frontend.request(dict(op='parse-eval',id=str(unit),mode='eval',
                                                        profile='cli-raw-85',source=base64.b64encode(body).decode()))
                    assert parsed_body['accepted']
                    body_fixture = adapter.request({'op':'check','ast':parsed_body['ast'],'fixture':True})['fixture']
                    responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(body) + ' ' + body_fixture)
                conditions = dynamic_checks(row,checked['fixture'],os.fsencode(path),responses)
            elif name == 'readonly-clone-once-and-manual-clone-refusal':
                conditions = clone_checks(row,checked['fixture'],os.fsencode(path))
            elif name == 'readonly-parent-private-slot-identities':
                conditions = parent_checks(row,checked['fixture'],os.fsencode(path))
            else:
                conditions = boundary_checks(row,checked['fixture'],os.fsencode(path),
                    checked_compile['fixture'] if name == 'readonly-nonreadonly-parent-before-argument' else None,
                    compile_row)
            group = '$class176_review_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join(
                '  -- if ' + condition + '\n' for condition in conditions)
            groups.append(group + '()')
            counts[name] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(groups) + '\n')
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)]
        result = cross.invoke.process(command,raw / 'numeric',1200,ROOT)
        report.update(command=command,exit=result.returncode,stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'),conditions=counts,fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:adapter.close()
        finally:
            if frontend:frontend.close()
        report['inputs_after'] = {str(path):sha(path) for path in watched}
        report['inputs_stable'] = report['inputs_after'] == before
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
        print(raw / 'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
