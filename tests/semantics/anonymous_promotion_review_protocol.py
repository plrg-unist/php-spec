#!/usr/bin/env python3
"""Independent anonymous promoted origins, eval scopes and error boundaries."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_promotion_cases.json'
PREFIX = r'''
dec $class175_review_front(pstate,nat) : bool
def $class175_review_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) =/= eps
def $class175_review_front(S,1) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
def $class175_review_front(S,2) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("accepts")
def $class175_review_front(S,n) = false -- otherwise
dec $class175_review_seek(pstate,nat,nat) : pstate
def $class175_review_seek(S,n_front,0) = S
def $class175_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class175_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class175_review_seek(S,n_front,n) = $class175_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class175_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class175_review_output_item(pevent) : ptbytes
def $class175_review_output_item(OUTPUT ptbytes) = ptbytes
def $class175_review_output_item(pevent) = eps -- otherwise
dec $class175_review_outputs(pevent*) : ptbytes
def $class175_review_outputs(eps) = eps
def $class175_review_outputs(pevent :: pevent_tail*) = $class175_review_output_item(pevent) ++ $class175_review_outputs(pevent_tail*)
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
    stderr = base64.b64decode(row['stderr_template_base64'])
    return stderr.split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]


def final_checks(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [
        state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps /\\ ' + state + '.CURRENT = eps',
        '$class175_review_outputs(' + state + '.EVENTS) = ' + term(expected),
        '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
        '$declaration_history_valid(' + state + ')',
    ]


def promotion_checks(row, fixture, filename):
    private_final = row['id'] == 'promotion-final-private-native-order'
    prefix = b'class@anonymous' if private_final else b'Probe175Base@anonymous'
    name = prefix + b'\0' + filename + b':3$0'
    value = 7 if private_final else 5
    out = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
        'S_pre = $class175_review_seek(S_initial,1,1600)',
        '$class175_review_front(S_pre,1) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
        'S_pre.CURRENT = (pcallcontext)',
        'pcallcontext.FUNCTION = porigin_ctor /\\ pcallcontext.RECEIVER = (n_object)',
        'S_pre.OBJECTS[n_object] = INSTANCE porigin_class',
        '$class_at(S_pre.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(name),
        'pcallcontext.LEXICAL_CLASS = (porigin_class) /\\ pcallcontext.CALLED_CLASS = (porigin_class)',
        '$call_current_valid(S_pre)',
        '$receiving_function(S_pre,porigin_ctor) = (pfunction)',
        'porigin_ctor = PORIGIN 0 pcpath_ctor',
        '$promotion_task_valid(S_pre,porigin_ctor,0)',
        '$promotion_descriptor(S_pre,pfunction,0) = (ppropertydesc_value)',
        'ppropertydesc_value.ORIGIN = PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 0])',
        'ppropertydesc_value.VISIBILITY = PROPERTY_PRIVATE /\\ ~ppropertydesc_value.STATIC',
        'ppropertydesc_value.KEY = [0] ++ pclassdesc.NAME ++ [0] ++ $ptascii("value")',
        'ppropertydesc_value.DEFAULT = PROP_UNINITIALIZED',
        '$objectprops_at(S_pre.OBJECTPROPS,n_object) = (ppropertyslot_pre*)',
        '$property_slot_at(ppropertyslot_pre*,ppropertydesc_value.KEY) = (ppropertyslot_value)',
        'ppropertyslot_value.STATE = PROP_INITIAL',
        '$lookup(S_pre.ENV,$ptascii("value")) = (n_cell_value)',
        'S_pre.STORE[n_cell_value] = DEFINED (PINT ' + str(value) + ')',
        'S_bad_origin = S_pre[.ORIGIN = (porigin_class)]',
        '~$promotion_task_valid(S_bad_origin,porigin_ctor,0)',
    ]
    if private_final:
        out += [
            'pclassdesc.PROPERTIES = [ppropertydesc_value]',
            'ppropertydesc_tail* = eps',
            'ppropertydesc_value.FINAL /\\ ppropertydesc_value.SETVISIBILITY = eps',
            '$origin_node(S_pre.SOURCES,PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 36) phpType18 phpType4_ref phpType4_var phpType10 phpType5 (SEQUENCE eps) metadata)',
        ]
    else:
        out += [
            'pclassdesc.PROPERTIES = [ppropertydesc_value,ppropertydesc_hint]',
            'ppropertydesc_tail* = [ppropertydesc_hint]',
            '~ppropertydesc_value.FINAL',
            '$promotion_descriptor(S_pre,pfunction,1) = (ppropertydesc_hint)',
            'ppropertydesc_hint.ORIGIN = PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 1])',
            'ppropertydesc_hint.DEFAULT = PROP_UNINITIALIZED /\\ ppropertydesc_hint.VISIBILITY = PROPERTY_PROTECTED',
            'ppropertydesc_hint.KEY = [0,42,0] ++ $ptascii("hint")',
            '$property_slot_at(ppropertyslot_pre*,ppropertydesc_hint.KEY) = (ppropertyslot_hint)',
            'ppropertyslot_hint.STATE = PROP_INITIAL',
            '$lookup(S_pre.ENV,$ptascii("hint")) = (n_cell_hint)',
            'S_pre.STORE[n_cell_hint] = DEFINED (PSTRING ($ptascii("h")))',
            '$location_slot(S_pre,PROPERTY n_object ([0] ++ $ptascii("Probe175Base") ++ [0] ++ $ptascii("value"))) = DEFINED (PINT 1)',
        ]
    return out + [
        'S_bad_key = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc[.PROPERTIES = [ppropertydesc_value[.KEY = $c_string(ppropertydesc_value.KEY)]] ++ ppropertydesc_tail*])]',
        '$promotion_descriptor(S_bad_key,pfunction,0) = eps',
        '~$promotion_task_valid(S_bad_key,porigin_ctor,0)',
        '~$promotion_task_valid(S_pre,porigin_ctor,99)',
        'S_written = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_written.COMPLETION = BUDGET',
        '$location_slot(S_written,PROPERTY n_object ppropertydesc_value.KEY) = DEFINED (PINT ' + str(value) + ')',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL],4000)',
        *final_checks(row,'S_done',filename),
        '$location_slot(S_done,PROPERTY n_object ppropertydesc_value.KEY) = DEFINED (PINT ' + str(value) + ')',
    ]


def dynamic_checks(row, fixture, filename, code, responses):
    virtual = [filename + b'(' + str(line).encode() + b") : eval()'d code" for line in [6,7]]
    names = [b'class@anonymous\0' + file + b':1$' + str(index).encode() for index,file in enumerate(virtual)]
    out = [
        'program_source = ' + fixture,
        'S_wait1 = $php_run(program_source,1600,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_wait1.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_promote1 = $class175_review_seek($eval_resume(S_wait1,' + responses[0] + '),1,1600)',
        '$class175_review_front(S_promote1,1) /\\ S_promote1.COMPLETION = BUDGET',
        'S_wait2 = $drive_steps(S_promote1[.COMPLETION = NORMAL],2000)',
        'S_wait2.COMPLETION = SOURCE_PENDING /\\ S_wait2.EVENTS = eps',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_promote2 = $class175_review_seek($eval_resume(S_wait2,' + responses[1] + '),1,1600)',
        '$class175_review_front(S_promote2,1) /\\ S_promote2.COMPLETION = BUDGET',
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
            cls + '.NAME = ' + term(names[number-1]),
            '$anonymous_history_seed(' + state + ',' + str(number) + ') = (' + str(number-1) + ')',
            '$declaration_unit_complete(' + state + '.DECLARATIONS,' + str(number) + ')',
            cls + '.PROPERTIES = [' + prop + ']',
            prop + '.ORIGIN = PORIGIN ' + str(number) + ' pcpath_parameter_' + label,
            prop + '.DEFAULT = PROP_UNINITIALIZED /\\ ' + prop + '.KEY = $ptascii("value")',
            '$receiving_function(' + state + ',porigin_ctor_' + label + ') = (pfunction_ctor_' + label + ')',
            '$promotion_descriptor(' + state + ',pfunction_ctor_' + label + ',0) = (' + prop + ')',
            '$promotion_task_valid(' + state + ',porigin_ctor_' + label + ',0)',
        ]
    out += [
        'porigin_class_one =/= porigin_class_two /\\ pclassdesc_one.NAME =/= pclassdesc_two.NAME',
        'ppropertydesc_one.ORIGIN =/= ppropertydesc_two.ORIGIN /\\ n_one =/= n_two',
        'S_receive1 = $class175_review_seek(S_promote2,2,2400)',
        '$class175_review_front(S_receive1,2) /\\ S_receive1.COMPLETION = BUDGET',
        'S_receive2 = $class175_review_seek($drive_steps(S_receive1[.COMPLETION = NORMAL],1),2,2400)',
        '$class175_review_front(S_receive2,2) /\\ S_receive2.COMPLETION = BUDGET',
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
        '$location_slot(S_done,PROPERTY n_one $ptascii("value")) = DEFINED (PINT 9)',
        '$location_slot(S_done,PROPERTY n_two $ptascii("value")) = DEFINED (PINT 5)',
    ]


def boundary_checks(row, fixture, filename):
    out = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
    ]
    if row['id'] == 'promotion-outside-constructor-warning-before-fatal':
        raw = base64.b64decode(row['stderr_template_base64'])
        notice = raw.split(b'Deprecated: ',1)[1].split(b' in {FILE} on line ',1)[0]
        return out + [
            'S_initial.COMPLETION = STATICBYTES ' + term(fatal_message(row)) + ' 4',
            'S_initial.EVENTS = [DIAGNOSTIC "Deprecated" (' + term(notice) + ') 4]',
            'S_initial.OBJECTS = eps',
        ]
    name = b'Probe175FinalBase@anonymous\0' + filename + b':5$0'
    return out + [
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
        'S_pre = $class175_review_seek(S_initial,0,1000)',
        '$class175_review_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(name),
        '~pclassdesc.EARLY',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.PROPERTIES = [ppropertydesc_value]',
        'ppropertydesc_value.DEFAULT = PROP_UNINITIALIZED /\\ ~ppropertydesc_value.FINAL',
        '$method_named(pclassdesc.METHODS,$ptascii("__construct")) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_ctor',
        'ppropertydesc_value.ORIGIN = PORIGIN 0 (pcpath_ctor ++ [PCFIELD 4,PCINDEX 0])',
        'S_pre.EVENTS = [OUTPUT $ptascii("before;")]',
        'S_fatal = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_fatal.COMPLETION = STATICBYTES ' + term(fatal_message(row)) + ' 5',
        'S_fatal.EVENTS = S_pre.EVENTS /\\ S_fatal.OBJECTS = eps',
        '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc.ORIGIN)',
    ]


def main():
    os.environ.update(LC_ALL='C',TZ='UTC',GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']:row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['promotion-private-parent-slot-identity',
                'promotion-eval-recompiled-values-and-self-scopes',
                'promotion-final-private-native-order',
                'promotion-outside-constructor-warning-before-fatal',
                'promotion-parent-final-conflict-before-argument']
    raw = Path(tempfile.mkdtemp(prefix='class175-review-state-',dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json',CATALOGUE,Path(__file__),
               ROOT / '.tools/php/bin/php',ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe',ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    watched += [ROOT / 'spec/semantics' / name for name in
                ['10-bytes.watsup','16-static-types.watsup','17-signatures.watsup',
                 '35-scalar-operations.watsup','36-arrays.watsup','141-method-compiler.watsup',
                 '383-anonymous-classes.watsup']]
    before = {str(path):sha(path) for path in watched}
    report = {'passed':False,'raw':str(raw),'inputs_before':before,
              'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'affinity':sorted(os.sched_getaffinity(0)),'environment':{'LC_ALL':'C','TZ':'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,
                           '-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],raw / 'adapter')
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
            if name == 'promotion-eval-recompiled-values-and-self-scopes':
                body, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'return new class')]
                responses = []
                for unit in [1,2]:
                    parsed_body = frontend.request(dict(op='parse-eval',id=str(unit),mode='eval',
                                                        profile='cli-raw-85',source=base64.b64encode(body).decode()))
                    assert parsed_body['accepted']
                    body_fixture = adapter.request({'op':'check','ast':parsed_body['ast'],'fixture':True})['fixture']
                    responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(body) + ' ' + body_fixture)
                conditions = dynamic_checks(row,checked['fixture'],os.fsencode(path),body,responses)
            elif name in ['promotion-private-parent-slot-identity','promotion-final-private-native-order']:
                conditions = promotion_checks(row,checked['fixture'],os.fsencode(path))
            else:
                conditions = boundary_checks(row,checked['fixture'],os.fsencode(path))
            group = '$class175_review_group' + str(index)
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

