#!/usr/bin/env python3
"""Independent own-constant tables, callable scope and fatal source fronts."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_own_constant_cases.json'
PREFIX = r'''
dec $class172_review_front(pstate, nat) : bool
def $class172_review_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) =/= eps
def $class172_review_front(S,1) = true
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if $(n < |S.OBJECTS|)
  -- if S.OBJECTS[n] = INSTANCE porigin
def $class172_review_front(S,2) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.OBJECTS[n] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin porigin_site porigin_called eps)
def $class172_review_front(S,n) = false -- otherwise
dec $class172_review_seek(pstate,nat,nat) : pstate
def $class172_review_seek(S,n_front,0) = S
def $class172_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class172_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class172_review_seek(S,n_front,n) = $class172_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class172_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class172_review_output_item(pevent) : ptbytes
def $class172_review_output_item(OUTPUT ptbytes) = ptbytes
def $class172_review_output_item(pevent) = eps -- otherwise
dec $class172_review_outputs(pevent*) : ptbytes
def $class172_review_outputs(eps) = eps
def $class172_review_outputs(pevent :: pevent_tail*) = $class172_review_output_item(pevent) ++ $class172_review_outputs(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def message(row):
    stderr = base64.b64decode(row['stderr_template_base64'])
    return stderr.split(b'Fatal error: ', 1)[1].split(b' in {FILE} on line ', 1)[0]


def nodes(value):
    if isinstance(value, dict):
        if 'node' in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def dynamic_checks(row, fixture, filename, code, responses):
    virtual = [filename + b'(' + str(line).encode() + b") : eval()'d code" for line in [6, 7]]
    names = [b'class@anonymous\0' + file + b':1$' + str(i).encode() for i, file in enumerate(virtual)]
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    out = [
        'program_source = ' + fixture,
        'S_wait1 = $php_run(program_source,1600,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_wait1.COMPLETION = SOURCE_PENDING',
        '$eval_context_at(S_wait1.EVALCONTEXTS,1) = (pevalcontext)',
        'pevalcontext.BYTES = ' + term(code),
        '$eval_response_valid(S_wait1,' + responses[0] + ')',
        'S_body1 = $eval_resume(S_wait1,' + responses[0] + ')',
        'S_new1 = $class172_review_seek(S_body1,0,800)',
        '$class172_review_front(S_new1,0)',
        'S_new1.ORIGIN = (PORIGIN 1 pcpath_new1)',
        '$anonymous_new_descriptor(S_new1,PORIGIN 1 pcpath_new1) = (pclassdesc_one)',
        'pclassdesc_one.NAME = ' + term(names[0]),
        '$anonymous_history_seed(S_new1,1) = (0)',
        '$declaration_unit_complete(S_new1.DECLARATIONS,1)',
        'S_wait2 = $drive_steps(S_new1[.COMPLETION = NORMAL],2000)',
        'S_wait2.COMPLETION = SOURCE_PENDING',
        'S_wait2.EVENTS = eps',
        '$lookup($global_table_view(S_wait2).ENV,$ptascii("first")) = (n_cell_first)',
        'S_wait2.STORE[n_cell_first] = DEFINED (POBJECT n_first)',
        'S_wait2.OBJECTS[n_first] = INSTANCE pclassdesc_one.ORIGIN',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_body2 = $eval_resume(S_wait2,' + responses[1] + ')',
        'S_new2 = $class172_review_seek(S_body2,0,800)',
        '$class172_review_front(S_new2,0)',
        'S_new2.ORIGIN = (PORIGIN 2 pcpath_new2)',
        '$anonymous_new_descriptor(S_new2,PORIGIN 2 pcpath_new2) = (pclassdesc_two)',
        'pclassdesc_two.NAME = ' + term(names[1]),
        'pclassdesc_one.NAME =/= pclassdesc_two.NAME /\\ pclassdesc_one.ORIGIN =/= pclassdesc_two.ORIGIN',
        '$anonymous_history_seed(S_new2,2) = (1)',
        '$declaration_unit_complete(S_new2.DECLARATIONS,2)',
        '$source_unit(S_new2.SOURCES,1) = (pcunit_one)',
        '$source_unit(S_new2.SOURCES,2) = (pcunit_two)',
        'pcunit_one.AST = pcunit_two.AST',
        'S_receive1 = $class172_review_seek(S_new2,2,1600)',
        '$class172_review_front(S_receive1,2) /\\ S_receive1.COMPLETION = BUDGET',
        'S_after_first = $drive_steps(S_receive1[.COMPLETION = NORMAL],1)',
        'S_receive2 = $class172_review_seek(S_after_first,2,1600)',
        '$class172_review_front(S_receive2,2) /\\ S_receive2.COMPLETION = BUDGET',
        '$lookup($global_table_view(S_receive2).ENV,$ptascii("second")) = (n_cell_second)',
        'S_receive2.STORE[n_cell_second] = DEFINED (POBJECT n_second)',
        'S_receive2.OBJECTS[n_second] = INSTANCE pclassdesc_two.ORIGIN',
        'n_first =/= n_second',
    ]
    for number, label, argument in [(1, 'one', 'first'), (2, 'two', 'second')]:
        cls, const, method = ['pclassdesc_' + label, 'pclassconstantdesc_' + label, 'pmethoddesc_' + label]
        state = 'S_receive' + str(number)
        out += [
            cls + '.CONSTANTS = [' + const + ']',
            const + '.NAME = $ptascii("CAPTURE") /\\ ~' + const + '.FOLDED',
            const + '.OWNER = ' + cls + '.ORIGIN /\\ ' + const + '.OWNERNAME = ' + cls + '.NAME',
            const + '.ORIGIN = PORIGIN ' + str(number) + ' pcpath_constant_' + label,
            '$method_named(' + cls + '.METHODS,$ptascii("m")) = (' + method + ')',
            method + '.OWNER = ' + cls + '.ORIGIN',
            method + '.FUNCTION.ORIGIN = PORIGIN ' + str(number) + ' pcpath_method_' + label,
            method + '.FUNCTION.SIGNATURE.PARAMETERS = [psparam_' + label + ']',
            'psparam_' + label + '.TYPE = [(PTBRANCH ([PTCLASS ' + cls + '.NAME]))]',
            state + '.TODO = (TYPE_RECEIVE ' + method + '.FUNCTION.ORIGIN 0) :: ptask_' + label + '*',
            state + '.CURRENT = (pcallcontext_' + label + ')',
            'pcallcontext_' + label + '.TARGET = CLOSURE_TARGET n_capture_' + label,
            'pcallcontext_' + label + '.LEXICAL_CLASS = (' + cls + '.ORIGIN) /\\ pcallcontext_' + label + '.CALLED_CLASS = (' + cls + '.ORIGIN)',
            state + '.OBJECTS[n_capture_' + label + '] = CONSTANTCLOSURE ' + const + '.INITIALIZER (METHODCLOSURE ' + method + '.FUNCTION.ORIGIN ' + const + '.INITIALIZER ' + cls + '.ORIGIN eps)',
            '$closure_scope_at(' + state + '.CLOSURESCOPES,n_capture_' + label + ') = (pclosurescope_' + label + ')',
            'pclosurescope_' + label + '.LEXICAL = ' + cls + '.ORIGIN /\\ pclosurescope_' + label + '.CALLED = ' + cls + '.ORIGIN',
            '$lookup(' + state + '.ENV,$ptascii("value")) = (n_value_' + label + ')',
            state + '.STORE[n_value_' + label + '] = DEFINED (POBJECT n_' + argument + ')',
            '$method_closure_functions(' + state + ',n_capture_' + label + ',' + method + ') = (' + method + '.FUNCTION,' + method + '.FUNCTION)',
            '$call_current_valid(' + state + ')',
        ]
    return out + [
        'n_capture_one =/= n_capture_two',
        'pmethoddesc_one.FUNCTION.ORIGIN =/= pmethoddesc_two.FUNCTION.ORIGIN',
        'pclassconstantdesc_one.INITIALIZER =/= pclassconstantdesc_two.INITIALIZER',
        'S_done = $drive_steps(S_receive2[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.CURRENT = eps /\\ S_done.EVALCONTEXTS = eps',
        '$class172_review_outputs(S_done.EVENTS) = ' + term(expected),
        '$declaration_history_valid(S_done) /\\ $class_state_valid(S_done)',
    ]


def checks(row, fixture, filename):
    compile_error = row['id'] in ['own-typed-constant-wrong-value', 'own-private-final-constant-error']
    final = row['id'] == 'own-final-parent-conflict-before-argument'
    capture = row['id'] == 'own-self-callable-constant'
    out = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
    ]
    if compile_error:
        return out + [
            'S_initial.COMPLETION = STATICBYTES ' + term(message(row)) + ' 4',
            'S_initial.EVENTS = eps',
            'S_initial.OBJECTS = eps',
        ]
    line = next(n for n, source in enumerate(row['source'].splitlines(), 1) if '$object = new class' in source)
    name = (b'Probe172FinalBase@anonymous' if final else b'class@anonymous') + b'\0' + filename + b':' + str(line).encode() + b'$0'
    out += [
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
        'S_pre = $class172_review_seek(S_initial,0,800)',
        '$class172_review_front(S_pre,0) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (PORIGIN 0 pcpath_new)',
        'porigin_new = PORIGIN 0 pcpath_new',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.ORIGIN = PORIGIN 0 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc_raw.NAME = ' + term(name),
        '$source_unit(S_pre.SOURCES,0) = (pcunit)',
        '$compilation_projection(S_pre,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        '$class_at(S_pre.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        'pclassdesc_raw.CONSTANTS = pclassconstantdesc_first :: pclassconstantdesc_tail*',
        'pclassconstantdesc_first.OWNER = pclassdesc_raw.ORIGIN /\\ pclassconstantdesc_first.OWNERNAME = pclassdesc_raw.NAME',
        'pclassconstantdesc_first.ORIGIN = PORIGIN 0 pcpath_constant',
        'S_wrong_owner = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.CONSTANTS = pclassconstantdesc_first[.OWNERNAME = $c_string(pclassconstantdesc_first.OWNERNAME)] :: pclassconstantdesc_tail*])]',
        '$anonymous_new_descriptor(S_wrong_owner,porigin_new) = eps',
        'S_wrong_name = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.NAME = $c_string(pclassdesc_raw.NAME)])]',
        '$anonymous_new_descriptor(S_wrong_name,porigin_new) = eps',
    ]
    if final:
        return out + [
            '~pclassdesc_raw.EARLY',
            '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
            '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
            '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
            'S_pre.EVENTS = [OUTPUT $ptascii("before;")]',
            '$class_named(S_pre.CLASSNAMES,$ptascii("probe172finalbase")) = (porigin_base)',
            '$class_at(S_pre.CLASSES,porigin_base) = (pclassdesc_base)',
            '$class_constant_desc(pclassdesc_base.CONSTANTS,$ptascii("VALUE")) = (pclassconstantdesc_base)',
            'pclassconstantdesc_base.FINAL /\\ ~pclassconstantdesc_first.FINAL',
            'pclassconstantdesc_first.NAME = $ptascii("VALUE")',
            '$class_constant_override_issue(S_pre,pclassdesc_raw,pclassconstantdesc_base,pclassconstantdesc_first) = METHOD_COMPILEISSUE ' + term(message(row)) + ' ' + str(line),
            'S_fatal = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
            'S_fatal.COMPLETION = STATICBYTES ' + term(message(row)) + ' ' + str(line),
            'S_fatal.EVENTS = S_pre.EVENTS',
            'S_fatal.OBJECTS = eps',
            '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
            '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        ]
    out += [
        'pclassdesc_raw.EARLY /\\ pclassdesc_raw.PARENT = eps /\\ pclassdesc_raw.INTERFACES = eps',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = (pclassdesc_raw.ORIGIN)',
        '$anonymous_new_available(S_pre,pclassdesc_raw)',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        'S_allocate = $class172_review_seek($drive_steps(S_pre[.COMPLETION = NORMAL],1),1,800)',
        '$class172_review_front(S_allocate,1) /\\ S_allocate.COMPLETION = BUDGET',
        'S_allocate.RESULT = KNOWN (POBJECT n_object)',
        'S_allocate.OBJECTS[n_object] = INSTANCE pclassdesc_raw.ORIGIN',
        '(HOBJECT n_object) <- S_allocate.ALLOCATIONS',
        '$anonymous_new_descriptor(S_allocate,porigin_new) = (pclassdesc_raw)',
        '$class_state_valid(S_allocate[.COMPLETION = NORMAL])',
    ]
    if capture:
        return out + [
            'pclassdesc_raw.CONSTANTS = [pclassconstantdesc_first]',
            'pclassconstantdesc_first.NAME = $ptascii("CAPTURE") /\\ ~pclassconstantdesc_first.FOLDED',
            'pclassconstantdesc_first.VISIBILITY = PROPERTY_PUBLIC',
            '$method_named(pclassdesc_raw.METHODS,$ptascii("m")) = (pmethoddesc)',
            'pmethoddesc.OWNER = pclassdesc_raw.ORIGIN',
            'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
            'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.TYPE = [(PTBRANCH ([PTCLASS pclassdesc_raw.NAME]))]',
            'S_receive = $class172_review_seek(S_allocate,2,800)',
            '$class172_review_front(S_receive,2) /\\ S_receive.COMPLETION = BUDGET',
            'S_receive.TODO = (TYPE_RECEIVE pmethoddesc.FUNCTION.ORIGIN 0) :: ptask_tail*',
            'S_receive.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
            'pcallcontext.LEXICAL_CLASS = (pclassdesc_raw.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_raw.ORIGIN)',
            'S_receive.OBJECTS[n_capture] = CONSTANTCLOSURE pclassconstantdesc_first.INITIALIZER (METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN pclassconstantdesc_first.INITIALIZER pclassdesc_raw.ORIGIN eps)',
            '$constant_callable_record(S_receive.CONSTANTCLOSURES,n_capture) = (pconstantclosure)',
            'pconstantclosure.DECL = pclassconstantdesc_first.ORIGIN',
            '$closure_scope_at(S_receive.CLOSURESCOPES,n_capture) = (pclosurescope)',
            'pclosurescope.LEXICAL = pclassdesc_raw.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_raw.ORIGIN',
            '$class_constant_callable_method_history_ordinary(S_receive,pmethoddesc,pclassconstantdesc_first.INITIALIZER,pclassdesc_raw.ORIGIN,pclosurescope) = (pclassdesc_raw.ORIGIN)',
            '$method_closure_functions(S_receive,n_capture,pmethoddesc) = (pmethoddesc.FUNCTION,pmethoddesc.FUNCTION)',
            '$call_current_valid(S_receive)',
        ]
    return out


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['own-self-callable-constant', 'eval-own-callable-recompile-scopes',
                'own-final-parent-conflict-before-argument', 'own-typed-constant-wrong-value',
                'own-private-final-constant-error']
    raw = Path(tempfile.mkdtemp(prefix='class172-review-state-', dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / '.tools/php/bin/php', ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    watched += [ROOT / 'spec/semantics' / name for name in
                ['183-class-constant-compiler.watsup', '184-class-constants.watsup',
                 '238-trait-data.watsup', '383-anonymous-classes.watsup']]
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before,
              'revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'affinity': sorted(os.sched_getaffinity(0)), 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')],raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],raw / 'adapter')
        code, groups, counts = PREFIX, [], {}
        for i, name in enumerate(selected):
            row = rows[name]
            path = raw / (name + '.php')
            path.write_text(row['source'])
            assert sha(path) == row['source_sha256']
            parsed = frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok']
            if name == 'eval-own-callable-recompile-scopes':
                body, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'return new class')]
                responses = []
                for unit in [1, 2]:
                    parsed_body = frontend.request(dict(op='parse-eval',id=str(unit),mode='eval',
                                                        profile='cli-raw-85',source=base64.b64encode(body).decode()))
                    assert parsed_body['accepted']
                    body_fixture = adapter.request({'op':'check','ast':parsed_body['ast'],'fixture':True})['fixture']
                    responses.append('SOURCE_ACCEPT ' + str(unit) + ' ' + term(body) + ' ' + body_fixture)
                conditions = dynamic_checks(row,checked['fixture'],os.fsencode(path),body,responses)
            else:
                conditions = checks(row,checked['fixture'],os.fsencode(path))
            group = '$class172_review_group' + str(i)
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
            if adapter: adapter.close()
        finally:
            if frontend: frontend.close()
        report['inputs_after'] = {str(path):sha(path) for path in watched}
        report['inputs_stable'] = before == report['inputs_after']
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
        print(raw / 'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
