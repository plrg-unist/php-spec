#!/usr/bin/env python3
"""Independent anonymous method flags, lexical access and compile/link order."""
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
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_modifier_cases.json'
BOUNDARIES = {
    "constructor-protected-related-parent-method-factory": "<?php\nclass Probe177MethodParent {\n    public static function make() {\n        return new class (5) extends Probe177MethodParent {\n            protected function __construct(public int $value) { echo 'BODY;'; }\n            final public function read(): int { return $this->value; }\n        };\n    }\n}\n$object = Probe177MethodParent::make();\necho $object->read(), ';', $object::class, ';';\n",
    "method-abstract-with-body-error": "<?php\necho 'before;';\n$object = new class {\n    abstract public function value() { echo 'BODY;'; }\n};\necho 'BAD;';\n"
}
PREFIX = r'''
dec $class177_review_output(pevent) : ptbytes
def $class177_review_output(OUTPUT ptbytes) = ptbytes
def $class177_review_output(pevent) = eps -- otherwise
dec $class177_review_outputs(pevent*) : ptbytes
def $class177_review_outputs(eps) = eps
def $class177_review_outputs(pevent :: pevent_tail*) = $class177_review_output(pevent) ++ $class177_review_outputs(pevent_tail*)
dec $class177_review_front(pstate,nat) : bool
def $class177_review_front(S,0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_descriptor(S,porigin) = (pclassdesc)
  -- if $class_named(S.CLASSNAMES,$ptlc(pclassdesc.NAME)) = (pclassdesc.ORIGIN)
def $class177_review_front(S,1) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*
def $class177_review_front(S,2) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S,porigin) =/= eps
def $class177_review_front(S,n) = false -- otherwise
dec $class177_review_seek(pstate,nat,nat) : pstate
def $class177_review_seek(S,n_front,0) = S
def $class177_review_seek(S,n_front,n) = S
  -- if $(n > 0)
  -- if $class177_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class177_review_seek(S,n_front,n) = $class177_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class177_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def fatal_message(row):
    return base64.b64decode(row['stderr_template_base64']).split(b'Fatal error: ',1)[1].split(b' in {FILE} on line ',1)[0]


def initial(fixture, filename):
    return ['program_source = ' + fixture,
            'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            'S_initial.COMPLETION = BUDGET /\\ ~S_initial.COMPILESTOP']


def seek(parent, state, front):
    return [state + '_found = $class177_review_seek(' + parent + ',' + str(front) + ',2400)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$class177_review_front(' + state + ',' + str(front) + ')']


def complete(row, state, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}',filename)
    return [state + '.COMPLETION = NORMAL /\\ ' + state + '.TODO = eps /\\ ' + state + '.CURRENT = eps /\\ ' + state + '.FRAMES = eps',
            '$class177_review_outputs(' + state + '.EVENTS) = ' + term(expected),
            '$class_state_valid(' + state + ') /\\ $property_state_valid(' + state + ')',
            '$declaration_history_valid(' + state + ')']


def protected_checks(row, fixture, filename):
    return initial(fixture,filename) + [
        *seek('S_initial','S_pre',0),
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_pre,porigin_new) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'Probe177BoundParent@anonymous\0' + filename + b':4$0'),
        '$class_named(S_pre.CLASSNAMES,$ptascii("probe177boundparent")) = (porigin_parent)',
        '$class_link_at(S_pre.LINKEDPARENTS,pclassdesc.ORIGIN) = (SOURCE_PARENT porigin_parent)',
        'S_pre.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (porigin_parent)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_bound',
        'pcallcontext.RECEIVER = eps',
        '$method_current_scope(S_pre) = (porigin_parent)',
        '$method_named(pclassdesc.METHODS,$ptascii("__construct")) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PROTECTED /\\ ~pmethoddesc.STATIC /\\ ~pmethoddesc.FINAL',
        '$method_accessible(S_pre,pmethoddesc,(porigin_parent))',
        '~$method_accessible(S_pre,pmethoddesc,eps)',
        '$call_current_valid(S_pre)',
        'S_wrong_scope = S_pre[.CURRENT = (pcallcontext[.LEXICAL_CLASS = eps])]',
        '~$call_current_valid(S_wrong_scope)',
        '$method_current_scope(S_wrong_scope) = eps',
        'S_pre.EVENTS = eps',
        *seek('S_pre','S_promote',1),
        'S_promote.TODO = (PROMOTE_PARAMETER pmethoddesc.FUNCTION.ORIGIN 0) :: ptask_tail*',
        'S_promote.CURRENT = (pcallcontext_ctor)',
        'pcallcontext_ctor.RECEIVER = (n_object)',
        'pcallcontext_ctor.LEXICAL_CLASS = (pclassdesc.ORIGIN)',
        '$promotion_descriptor(S_promote,pmethoddesc.FUNCTION,0) = (ppropertydesc)',
        '$promotion_task_valid(S_promote,pmethoddesc.FUNCTION.ORIGIN,0)',
        '$location_slot(S_promote,PROPERTY n_object ppropertydesc.KEY) = UNDEFINED',
        'S_written = $drive_steps(S_promote,1)',
        'S_written.COMPLETION = BUDGET /\\ S_written.EVENTS = eps',
        '$location_slot(S_written,PROPERTY n_object ppropertydesc.KEY) = DEFINED (PINT 5)',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL],4000)',
        *complete(row,'S_done',filename),
    ]


def warning_checks(row, fixture, filename):
    message = term(b'Private methods cannot be final as they are never overridden by other classes')
    return initial(fixture,filename) + [
        'S_initial.EVENTS = [DIAGNOSTIC "Warning" ' + message + ' 4,DIAGNOSTIC "Warning" ' + message + ' 5]',
        'S_initial.CLASSES = [pclassdesc]',
        '$method_named(pclassdesc.METHODS,$ptascii("secret")) = (pmethoddesc_instance)',
        '$method_named(pclassdesc.METHODS,$ptascii("staticsecret")) = (pmethoddesc_static)',
        'pclassdesc.METHODS = [pmethoddesc_instance,pmethoddesc_static,pmethoddesc_read]',
        'pmethoddesc_read.NAME = $ptascii("read")',
        'pmethoddesc_instance.FINAL /\\ ~pmethoddesc_instance.STATIC /\\ pmethoddesc_instance.VISIBILITY = PROPERTY_PRIVATE',
        'pmethoddesc_static.FINAL /\\ pmethoddesc_static.STATIC /\\ pmethoddesc_static.VISIBILITY = PROPERTY_PRIVATE',
        'pmethoddesc_instance.FUNCTION.NAME = pclassdesc.NAME ++ $ptascii("::secret")',
        'pmethoddesc_static.FUNCTION.NAME = pclassdesc.NAME ++ $ptascii("::staticSecret")',
        '$origin_node(S_initial.SOURCES,pmethoddesc_instance.FUNCTION.ORIGIN) = (NStmtClassMethod (SEQUENCE eps) (INTEGER 36) (BOOLEAN false) phpType11 phpType16 phpType18 (SEQUENCE statement*) metadata)',
        '~$anonymous_member(NStmtClassMethod (SEQUENCE eps) (INTEGER 17) (BOOLEAN false) phpType11 phpType16 phpType18 (SEQUENCE statement*) metadata)',
        '~$anonymous_member(NStmtClassMethod (SEQUENCE eps) (INTEGER 36) (BOOLEAN true) phpType11 phpType16 phpType18 (SEQUENCE statement*) metadata)',
        'S_wrong_flag = S_initial[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_instance[.FINAL = false],pmethoddesc_static,pmethoddesc_read]]]]',
        '~$declaration_history_valid(S_wrong_flag)',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        *complete(row,'S_done',filename),
    ]


def promotion_checks(row, fixture, filename):
    return initial(fixture,filename) + [
        *seek('S_initial','S_promote',1),
        'S_promote.TODO = (PROMOTE_PARAMETER porigin_ctor 0) :: ptask_tail*',
        'S_promote.CURRENT = (pcallcontext)',
        'pcallcontext.RECEIVER = (n_object)',
        'S_promote.OBJECTS[n_object] = INSTANCE porigin_class',
        '$class_at(S_promote.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = ' + term(b'class@anonymous\0' + filename + b':2$0'),
        '$method_named(pclassdesc.METHODS,$ptascii("__construct")) = (pmethoddesc)',
        'pmethoddesc.FINAL /\\ ~pmethoddesc.STATIC /\\ pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'porigin_ctor = pmethoddesc.FUNCTION.ORIGIN',
        '$origin_node(S_promote.SOURCES,porigin_ctor) = (NStmtClassMethod (SEQUENCE eps) (INTEGER 32) (BOOLEAN false) phpType11 phpType16 ABSENT phpType47 metadata)',
        '$receiving_function(S_promote,porigin_ctor) = (pfunction)',
        '$promotion_raw(S_promote,pfunction,0) = (psraw)',
        'psraw.FLAGS = 1 /\\ psraw.NAME = $ptascii("value")',
        '$promotion_descriptor(S_promote,pfunction,0) = (ppropertydesc)',
        '~ppropertydesc.FINAL /\\ ~ppropertydesc.READONLY /\\ ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        '$promotion_task_valid(S_promote,porigin_ctor,0)',
        '$lookup(S_promote.ENV,$ptascii("value")) = (n_cell)',
        'S_promote.STORE[n_cell] = DEFINED (PINT 7)',
        '$location_slot(S_promote,PROPERTY n_object ppropertydesc.KEY) = UNDEFINED',
        'S_promote.EVENTS = eps',
        'S_written = $drive_steps(S_promote,1)',
        'S_written.COMPLETION = BUDGET /\\ S_written.EVENTS = eps',
        '$location_slot(S_written,PROPERTY n_object ppropertydesc.KEY) = DEFINED (PINT 7)',
        'S_done = $drive_steps(S_written[.COMPLETION = NORMAL],4000)',
        *complete(row,'S_done',filename),
    ]


def link_checks(rows, fixtures, files):
    out = []
    for index,(row,fixture,filename) in enumerate(zip(rows,fixtures,files)):
        state,pre,fatal = 'S_initial' + str(index),'S_pre' + str(index),'S_fatal' + str(index)
        line = 7 if index == 0 else 6
        prefix = b'Probe177FinalMethodParent@anonymous' if index == 0 else b'Probe177FinalCtorParent@anonymous'
        out += [
            state + ' = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            state + '.COMPLETION = BUDGET /\\ ~' + state + '.COMPILESTOP',
            *seek(state,pre,2),
            pre + '.ORIGIN = (porigin_new' + str(index) + ')',
            '$anonymous_new_pending(' + pre + ',porigin_new' + str(index) + ') = (pclassdesc_' + str(index) + ')',
            'pclassdesc_' + str(index) + '.NAME = ' + term(prefix + b'\0' + filename + b':5$0'),
            '$class_named(' + pre + '.CLASSNAMES,$ptlc(pclassdesc_' + str(index) + '.NAME)) = eps',
            pre + '.EVENTS = [OUTPUT $ptascii("before;")] /\\ ' + pre + '.OBJECTS = eps',
            fatal + ' = $drive_steps(' + pre + ',1)',
            fatal + '.COMPLETION = STATICBYTES ' + term(fatal_message(row)) + ' ' + str(line),
            fatal + '.EVENTS = ' + pre + '.EVENTS /\\ ' + fatal + '.OBJECTS = eps',
            '$class_named(' + fatal + '.CLASSNAMES,$ptlc(pclassdesc_' + str(index) + '.NAME)) = eps',
            '~$anonymous_runtime_declaration(' + fatal + '.DECLARATIONS,pclassdesc_' + str(index) + '.ORIGIN)',
        ]
    return out


def compile_checks(rows, fixtures, files, boundary_fixtures):
    out = []
    for index,(row,fixture,filename) in enumerate(zip(rows,fixtures,files)):
        state = 'S_compile' + str(index)
        line = 5 if row['id'] == 'method-duplicate-final-instance-static-error' else 4
        out += [
            state + ' = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
            state + '.COMPLETION = STATICBYTES ' + term(fatal_message(row)) + ' ' + str(line),
            state + '.EVENTS = eps /\\ ' + state + '.OBJECTS = eps',
            state + '.CLASSNAMES = eps',
        ]
    for index,fixture in enumerate(boundary_fixtures):
        out += ['pcunit_boundary' + str(index) + ' = $pcsource(0,' + fixture + ')',
                '~$anonymous_unit(pcunit_boundary' + str(index) + ')']
    return out


def main():
    os.environ.update(LC_ALL='C',TZ='UTC',GIT_OPTIONAL_LOCKS='0')
    rows = {row['id']:row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['constructor-protected-related-bound-static-factory',
                'method-private-final-instance-and-static-warnings',
                'constructor-final-default-public-normal-promotion',
                'method-parent-final-conflict-before-argument',
                'constructor-parent-final-conflict-before-argument',
                'constructor-static-before-bad-parameter-default',
                'constructor-static-valid-default-compile-error',
                'method-duplicate-final-instance-static-error']
    raw = Path(tempfile.mkdtemp(prefix='class177-review-state-',dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [ROOT / 'spec/semantics/modules.json',CATALOGUE,Path(__file__),
               ROOT / 'spec/semantics/141-method-compiler.watsup',ROOT / 'spec/semantics/383-anonymous-classes.watsup',
               ROOT / 'frontend/worker.php',ROOT / '.tools/php/bin/php',ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/profile.json',ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path):sha(path) for path in watched}
    report = {'passed':False,'raw':str(raw),'inputs_before':before,
              'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'affinity':sorted(os.sched_getaffinity(0)),'environment':{'LC_ALL':'C','TZ':'UTC'}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,
                           '-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],raw / 'adapter')
        fixtures,files,boundary_fixtures = {},{},[]
        def parsed_fixture(source):
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok']
            return checked['fixture']
        for name in selected:
            row = rows[name]
            path = raw / (name + '.php')
            path.write_text(row['source'])
            assert sha(path) == row['source_sha256']
            fixtures[name],files[name] = parsed_fixture(path.read_bytes()),os.fsencode(path)
        for name,source in BOUNDARIES.items():
            path = raw / (name + '.php')
            path.write_text(source)
            boundary_fixtures.append(parsed_fixture(path.read_bytes()))
        collections = [
            ('protected_bound_closure_scope',protected_checks(rows[selected[0]],fixtures[selected[0]],files[selected[0]])),
            ('private_final_compile_warnings',warning_checks(rows[selected[1]],fixtures[selected[1]],files[selected[1]])),
            ('final_public_constructor_promotion',promotion_checks(rows[selected[2]],fixtures[selected[2]],files[selected[2]])),
            ('inherited_final_method_and_constructor',link_checks([rows[n] for n in selected[3:5]],[fixtures[n] for n in selected[3:5]],[files[n] for n in selected[3:5]])),
            ('static_default_priority_duplicate_and_boundaries',compile_checks([rows[n] for n in selected[5:]],[fixtures[n] for n in selected[5:]],[files[n] for n in selected[5:]],boundary_fixtures)),
        ]
        code,groups,counts = PREFIX,[],{}
        for index,(name,conditions) in enumerate(collections):
            group = '$class177_review_group' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join('  -- if ' + c + '\n' for c in conditions)
            groups.append(group + '()')
            counts[name] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(groups) + '\n')
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
