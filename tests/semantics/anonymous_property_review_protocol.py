#!/usr/bin/env python3
"""Independent anonymous private slots, eval statics and fatal ordering."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_property_cases.json'
PREFIX = r'''
dec $class173_review_front(pstate) : bool
def $class173_review_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) =/= eps
def $class173_review_front(S) = false -- otherwise
dec $class173_review_seek(pstate,nat) : pstate
def $class173_review_seek(S,0) = S
def $class173_review_seek(S,n) = S
  -- if $(n > 0)
  -- if $class173_review_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class173_review_seek(S,n) = $class173_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class173_review_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class173_review_output_item(pevent) : ptbytes
def $class173_review_output_item(OUTPUT ptbytes) = ptbytes
def $class173_review_output_item(pevent) = eps -- otherwise
dec $class173_review_outputs(pevent*) : ptbytes
def $class173_review_outputs(eps) = eps
def $class173_review_outputs(pevent :: pevent_tail*) = $class173_review_output_item(pevent) ++ $class173_review_outputs(pevent_tail*)
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
        'S_new1 = $class173_review_seek($eval_resume(S_wait1,' + responses[0] + '),800)',
        '$class173_review_front(S_new1)',
        'S_new1.ORIGIN = (PORIGIN 1 pcpath_new1)',
        '$anonymous_new_descriptor(S_new1,PORIGIN 1 pcpath_new1) = (pclassdesc_one)',
        'pclassdesc_one.NAME = ' + term(names[0]),
        '$anonymous_history_seed(S_new1,1) = (0)',
        '$declaration_unit_complete(S_new1.DECLARATIONS,1)',
        'S_wait2 = $drive_steps(S_new1[.COMPLETION = NORMAL],2000)',
        'S_wait2.COMPLETION = SOURCE_PENDING /\\ S_wait2.EVENTS = eps',
        '$lookup($global_table_view(S_wait2).ENV,$ptascii("first")) = (n_cell_first)',
        'S_wait2.STORE[n_cell_first] = DEFINED (POBJECT n_first)',
        'S_wait2.OBJECTS[n_first] = INSTANCE pclassdesc_one.ORIGIN',
        '$eval_response_valid(S_wait2,' + responses[1] + ')',
        'S_new2 = $class173_review_seek($eval_resume(S_wait2,' + responses[1] + '),800)',
        '$class173_review_front(S_new2)',
        'S_new2.ORIGIN = (PORIGIN 2 pcpath_new2)',
        '$anonymous_new_descriptor(S_new2,PORIGIN 2 pcpath_new2) = (pclassdesc_two)',
        'pclassdesc_two.NAME = ' + term(names[1]),
        'pclassdesc_one.NAME =/= pclassdesc_two.NAME /\\ pclassdesc_one.ORIGIN =/= pclassdesc_two.ORIGIN',
        '$anonymous_history_seed(S_new2,2) = (1)',
        '$declaration_unit_complete(S_new2.DECLARATIONS,2)',
        '$source_unit(S_new2.SOURCES,1) = (pcunit_one)',
        '$source_unit(S_new2.SOURCES,2) = (pcunit_two)',
        'pcunit_one.AST = pcunit_two.AST',
    ]
    for label, unit in [('one', 1), ('two', 2)]:
        cls, prop = 'pclassdesc_' + label, 'ppropertydesc_' + label
        out += [
            cls + '.PROPERTIES = [' + prop + ']',
            prop + '.NAME = $ptascii("count") /\\ ' + prop + '.STATIC /\\ ~' + prop + '.READONLY',
            prop + '.VISIBILITY = PROPERTY_PRIVATE',
            prop + '.KEY = [0] ++ ' + cls + '.NAME ++ [0] ++ $ptascii("count")',
            prop + '.ORIGIN = PORIGIN ' + str(unit) + ' pcpath_property_' + label,
            prop + '.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        ]
    return out + [
        'ppropertydesc_one.ORIGIN =/= ppropertydesc_two.ORIGIN /\\ ppropertydesc_one.KEY =/= ppropertydesc_two.KEY',
        'S_bad_key = S_new2[.CLASSES = $trait_class_set(S_new2.CLASSES,pclassdesc_two[.PROPERTIES = [ppropertydesc_two[.KEY = ppropertydesc_one.KEY]]])]',
        '$anonymous_new_descriptor(S_bad_key,PORIGIN 2 pcpath_new2) = eps',
        'S_done = $drive_steps(S_new2[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.CURRENT = eps /\\ S_done.EVALCONTEXTS = eps',
        '$lookup($global_table_view(S_done).ENV,$ptascii("second")) = (n_cell_second)',
        'S_done.STORE[n_cell_second] = DEFINED (POBJECT n_second)',
        'S_done.OBJECTS[n_second] = INSTANCE pclassdesc_two.ORIGIN /\\ n_first =/= n_second',
        '$class_static_at(S_done.CLASSSTATICS,ppropertydesc_one.ORIGIN) = (pclassstatic_one)',
        '$class_static_at(S_done.CLASSSTATICS,ppropertydesc_two.ORIGIN) = (pclassstatic_two)',
        'pclassstatic_one.STATE = PROP_VALUE (DIRECT (PINT 5))',
        'pclassstatic_two.STATE = PROP_VALUE (DIRECT (PINT 4))',
        '$class173_review_outputs(S_done.EVENTS) = ' + term(expected),
        '$declaration_history_valid(S_done) /\\ $class_state_valid(S_done) /\\ $class_statics_valid(S_done)',
    ]


def checks(row, fixture, filename):
    compile_error = row['id'] == 'ordinary-property-static-readonly-before-default-compile-error'
    link_error = row['id'] == 'ordinary-property-parent-static-conflict-before-argument'
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
    line = 5 if link_error else 7
    prefix = b'Probe173StaticBase@anonymous' if link_error else b'Probe173Base@anonymous'
    name = prefix + b'\0' + filename + b':' + str(line).encode() + b'$0'
    out += [
        'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP',
        'S_pre = $class173_review_seek(S_initial,800)',
        '$class173_review_front(S_pre) /\\ S_pre.COMPLETION = BUDGET',
        'S_pre.ORIGIN = (PORIGIN 0 pcpath_new)',
        'porigin_new = PORIGIN 0 pcpath_new',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.ORIGIN = PORIGIN 0 (pcpath_new ++ [PCFIELD 0])',
        'pclassdesc_raw.NAME = ' + term(name),
        '~pclassdesc_raw.EARLY',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '$ppproperty_desc_at(pclassdesc_raw.PROPERTIES,$ptascii("x")) = (ppropertydesc_x)',
    ]
    if link_error:
        return out + [
            'S_pre.EVENTS = [OUTPUT $ptascii("before;")]',
            '$class_named(S_pre.CLASSNAMES,$ptascii("probe173staticbase")) = (porigin_base)',
            '$class_at(S_pre.CLASSES,porigin_base) = (pclassdesc_base)',
            '$ppproperty_desc_at(pclassdesc_base.PROPERTIES,$ptascii("x")) = (ppropertydesc_base)',
            'ppropertydesc_base.STATIC /\\ ~ppropertydesc_x.STATIC',
            'S_fatal = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
            'S_fatal.COMPLETION = STATICBYTES ' + term(message(row)) + ' ' + str(line),
            'S_fatal.EVENTS = S_pre.EVENTS /\\ S_fatal.OBJECTS = eps',
            '$class_named(S_fatal.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
            '~$anonymous_runtime_declaration(S_fatal.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        ]
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return out + [
        'pclassdesc_raw.PROPERTIES = [ppropertydesc_x,ppropertydesc_p]',
        'ppropertydesc_x.VISIBILITY = PROPERTY_PRIVATE /\\ ~ppropertydesc_x.STATIC',
        'ppropertydesc_x.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
        'ppropertydesc_x.KEY = [0] ++ pclassdesc_raw.NAME ++ [0] ++ $ptascii("x")',
        'ppropertydesc_p.NAME = $ptascii("p") /\\ ppropertydesc_p.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertydesc_p.KEY = [0,42,0] ++ $ptascii("p")',
        'S_bad_key = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.PROPERTIES = [ppropertydesc_x[.KEY = $c_string(ppropertydesc_x.KEY)],ppropertydesc_p]])]',
        '$anonymous_new_descriptor(S_bad_key,porigin_new) = eps',
        'S_bad_static = S_pre[.CLASSES = $trait_class_set(S_pre.CLASSES,pclassdesc_raw[.PROPERTIES = [ppropertydesc_x[.STATIC = true],ppropertydesc_p]])]',
        '$anonymous_new_descriptor(S_bad_static,porigin_new) = eps',
        'S_done = $drive_steps(S_pre[.COMPLETION = NORMAL],4000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps',
        '$lookup($global_table_view(S_done).ENV,$ptascii("object")) = (n_cell)',
        'S_done.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S_done.OBJECTS[n_object] = INSTANCE pclassdesc_raw.ORIGIN',
        '$location_slot(S_done,PROPERTY n_object ppropertydesc_x.KEY) = DEFINED (PSTRING ($ptascii("child")))',
        '$location_slot(S_done,PROPERTY n_object ([0] ++ $ptascii("Probe173Base") ++ [0] ++ $ptascii("x"))) = DEFINED (PINT 1)',
        '$location_slot(S_done,PROPERTY n_object ppropertydesc_p.KEY) = DEFINED (PINT 3)',
        '$property_resolve(S_done,n_object,$ptascii("x")) = PROPERTY_DENIED ppropertydesc_x',
        '$class173_review_outputs(S_done.EVENTS) = ' + term(expected),
        '$anonymous_new_descriptor(S_done,porigin_new) = (pclassdesc_raw)',
        '$declaration_history_valid(S_done) /\\ $class_state_valid(S_done)',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['ordinary-property-private-parent-slot-identity',
                'eval-ordinary-property-static-separate-compilations',
                'ordinary-property-parent-static-conflict-before-argument',
                'ordinary-property-static-readonly-before-default-compile-error']
    raw = Path(tempfile.mkdtemp(prefix='class173-review-state-', dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / '.tools/php/bin/php', ROOT / 'tests/semantics/profile.json',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    watched += [ROOT / 'spec/semantics' / name for name in
                ['135-property-compiler.watsup', '153-property-visibility-compiler.watsup',
                 '154-property-visibility-runtime.watsup', '294-readonly-lifecycle.watsup',
                 '383-anonymous-classes.watsup']]
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
            if name == 'eval-ordinary-property-static-separate-compilations':
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
            group = '$class173_review_group' + str(i)
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
        report['inputs_stable'] = report['inputs_after'] == before
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
        print(raw / 'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
