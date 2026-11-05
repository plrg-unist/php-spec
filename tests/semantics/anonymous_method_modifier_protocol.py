#!/usr/bin/env python3
"""Final method dispatch, cloned FCC scope and denied constructor lifecycle."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_modifier_cases.json'
PREFIX = r'''
dec $method177_front(pstate, nat) : bool
def $method177_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_name(S,porigin) =/= eps
def $method177_front(S, 1) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
def $method177_front(S, 2) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $lookup($global_table_view(S).ENV,$ptascii("copy")) = (n_copy)
  -- if S.STORE[n_copy] = DEFINED (POBJECT n)
def $method177_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $method177_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $lookup(S.ENV,$ptascii("value")) = (n_value)
  -- if S.STORE[n_value] = DEFINED (PINT 3)
def $method177_front(S, n) = false -- otherwise
dec $method177_seek(pstate, nat, nat) : pstate
def $method177_seek(S, n_front, 0) = S
def $method177_seek(S, n_front, n) = S
  -- if $(n > 0) /\ $method177_front(S,n_front)
def $method177_seek(S, n_front, n) = $method177_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$method177_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $method177_seek(S, n_front, n) = S -- otherwise
dec $method177_output_item(pevent) : ptbytes
def $method177_output_item(OUTPUT ptbytes) = ptbytes
def $method177_output_item(pevent) = eps -- otherwise
dec $method177_output(pevent*) : ptbytes
def $method177_output(eps) = eps
def $method177_output(pevent :: pevent_tail*) = $method177_output_item(pevent) ++ $method177_output(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def final_checks(row, filename):
    expected = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', filename)
    return [r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$method177_output(S_done.EVENTS) = ' + term(expected),
            r'$class_state_valid(S_done) /\ $property_state_valid(S_done)',
            r'$declaration_history_valid(S_done) /\ $heap_valid($heap_graph(S_done))']


def checks(row, fixture, filename):
    out = ['S_start = $php_run(' + fixture + ',0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
           r'S_start.COMPLETION = BUDGET /\ ~S_start.COMPILESTOP',
           'S_new = $method177_seek(S_start,0,1000)',
           r'$method177_front(S_new,0) /\ S_new.COMPLETION = BUDGET',
           'S_new.ORIGIN = (porigin_new)',
           '$anonymous_new_descriptor(S_new,porigin_new) = (pclassdesc)',
           'S_new.CLASSES = [pclassdesc]',
           'S_new.OBJECTS = eps',
           '$anonymous_new_name(S_new,porigin_new) = (pclassdesc.NAME)',
           '$declaration_history_valid(S_new)']
    if row['id'] == 'method-final-instance-protected-and-default-static':
        for name, visibility, static, flags in [('value','PROPERTY_PUBLIC',False,33),('hidden','PROPERTY_PROTECTED',False,34),('staticValue','PROPERTY_PUBLIC',True,40),('read','PROPERTY_PUBLIC',False,32)]:
            method = 'pmethoddesc_' + name
            out += ['$method_named(pclassdesc.METHODS,$ptascii("' + name + '")) = (' + method + ')',
                    method + '.FINAL', method + '.STATIC = ' + str(static).lower(),
                    method + '.VISIBILITY = ' + visibility,
                    method + '.OWNER = pclassdesc.ORIGIN',
                    '$origin_node(S_new.SOURCES,' + method + '.FUNCTION.ORIGIN) = (NStmtClassMethod (SEQUENCE eps) (INTEGER ' + str(flags) + ') (BOOLEAN false) phpType11_' + name + ' phpType16_' + name + ' phpType18_' + name + ' phpType47_' + name + ' metadata_' + name + ')']
        out += ['$method_accessible(S_new,pmethoddesc_value,eps)',
                '~$method_accessible(S_new,pmethoddesc_hidden,eps)',
                '$method_accessible(S_new,pmethoddesc_hidden,(pclassdesc.ORIGIN))',
                'pclassdesc_bad = pclassdesc[.METHODS = [pmethoddesc_value[.FINAL = false],pmethoddesc_hidden,pmethoddesc_staticValue,pmethoddesc_read]]',
                'S_bad = S_new[.CLASSES = [pclassdesc_bad]]',
                '$anonymous_new_descriptor(S_bad,porigin_new) = eps',
                '~$declaration_history_valid(S_bad)',
                'S_receive = $method177_seek(S_new,1,2000)',
                r'$method177_front(S_receive,1) /\ S_receive.COMPLETION = BUDGET',
                'S_receive.TODO = (TYPE_RECEIVE pmethoddesc_value.FUNCTION.ORIGIN 0) :: ptask_tail*',
                'S_receive.CURRENT = (pcallcontext)',
                'pcallcontext.TARGET = METHOD_TARGET n_object pmethoddesc_value.FUNCTION.ORIGIN',
                'pcallcontext.RECEIVER = (n_object)',
                r'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN) /\ pcallcontext.CALLED_CLASS = (pclassdesc.ORIGIN)',
                '$lookup(S_receive.ENV,$ptascii("value")) = eps',
                '$call_current_valid(S_receive)',
                '$call_task_valid(S_receive,TYPE_RECEIVE pmethoddesc_value.FUNCTION.ORIGIN 0)',
                '~$call_task_valid(S_receive,TYPE_RECEIVE pmethoddesc_hidden.FUNCTION.ORIGIN 0)',
                'S_received = $method177_seek(S_receive,4,1000)',
                r'$method177_front(S_received,4) /\ S_received.COMPLETION = BUDGET',
                '$lookup(S_received.ENV,$ptascii("value")) = (n_value)',
                'S_received.STORE[n_value] = DEFINED (PINT 3)',
                '$call_current_valid(S_received)',
                'S_received.EVENTS = eps',
                'S_done = $drive_steps(S_received[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename)]
    elif row['id'] == 'method-final-firstclass-clone-self-scope':
        out += ['$method_named(pclassdesc.METHODS,$ptascii("accepts")) = (pmethoddesc)',
                r'pmethoddesc.FINAL /\ ~pmethoddesc.STATIC',
                'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam]',
                'psparam.TYPE = [(PTBRANCH ([PTCLASS pclassdesc.NAME]))]',
                'S_clone = $method177_seek(S_new,2,4000)',
                r'$method177_front(S_clone,2) /\ S_clone.COMPLETION = BUDGET',
                'S_clone.TODO = (TYPE_RECEIVE pmethoddesc.FUNCTION.ORIGIN 0) :: ptask_tail*',
                'S_clone.CURRENT = (pcallcontext)',
                'pcallcontext.TARGET = CLOSURE_TARGET n_clone',
                'pcallcontext.INSTANCE = (n_clone)',
                'pcallcontext.RECEIVER = (n_object)',
                r'pcallcontext.LEXICAL_CLASS = (pclassdesc.ORIGIN) /\ pcallcontext.CALLED_CLASS = (pclassdesc.ORIGIN)',
                '$lookup($global_table_view(S_clone).ENV,$ptascii("call")) = (n_call_cell)',
                'S_clone.STORE[n_call_cell] = DEFINED (POBJECT n_call)',
                'n_call =/= n_clone',
                'S_clone.OBJECTS[n_clone] = S_clone.OBJECTS[n_call]',
                '$closure_scope_at(S_clone.CLOSURESCOPES,n_clone) = (pclosurescope)',
                r'pclosurescope.LEXICAL = pclassdesc.ORIGIN /\ pclosurescope.CALLED = pclassdesc.ORIGIN',
                'pclosurescope.RECEIVER = (n_object)',
                '$method_closure_scope_valid(S_clone,pclosurescope)',
                '~$method_closure_scope_valid(S_clone,pclosurescope[.LEXICAL = pmethoddesc.FUNCTION.ORIGIN])',
                '$lookup(S_clone.ENV,$ptascii("value")) = (n_value)',
                'S_clone.STORE[n_value] = DEFINED (POBJECT n_object)',
                'S_clone.OBJECTS[n_object] = INSTANCE pclassdesc.ORIGIN',
                '$receiving_function(S_clone,pmethoddesc.FUNCTION.ORIGIN) = (pfunction)',
                'pfunction.SIGNATURE.PARAMETERS = [psparam]',
                '$call_current_valid(S_clone)',
                '~$call_current_valid(S_clone[.CURRENT = (pcallcontext[.RECEIVER = eps])])',
                '$method177_output(S_clone.EVENTS) = $ptascii("scope;")',
                'S_done = $drive_steps(S_clone[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename)]
    else:
        out += ['$method_named(pclassdesc.METHODS,$ptascii("__construct")) = (pmethoddesc)',
                r'pmethoddesc.FINAL /\ ~pmethoddesc.STATIC',
                'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
                '$method_named(pclassdesc.METHODS,$ptascii("__destruct")) = (pmethoddesc_destructor)',
                '~$method_accessible(S_new,pmethoddesc,eps)',
                '$method_accessible(S_new,pmethoddesc,(pclassdesc.ORIGIN))',
                'S_new.CURRENT = eps',
                '$method177_output(S_new.EVENTS) = $ptascii("before;")',
                'S_fail = $drive_steps(S_new[.COMPLETION = NORMAL],1)',
                r'S_fail.COMPLETION = BUDGET /\ $method177_front(S_fail,3)',
                'S_fail.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                'S_fail.DESTRUCTION.CALLED = [n_failed]',
                '(HOBJECT n_failed) <- S_fail.ALLOCATIONS',
                '~$destructor_uncalled_node(S_fail,HOBJECT n_failed)',
                '$method177_output(S_fail.EVENTS) = $ptascii("before;")',
                '$string_bytes($throwable_field(S_fail,n_error,"message")) = ($ptascii("Call to private class@anonymous::__construct() from global scope"))',
                'S_done = $drive_steps(S_fail[.COMPLETION = NORMAL],8192)',
                *final_checks(row,filename)]
    return out


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    selected = ['method-final-instance-protected-and-default-static',
                'method-final-firstclass-clone-self-scope',
                'constructor-final-private-denial-before-argument-and-destructor']
    rows = json.loads(CATALOGUE.read_text())['cases']
    raw = Path(tempfile.mkdtemp(prefix='anonymous-method-modifiers-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOGUE, Path(__file__),
               ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        code, counts, names = PREFIX, {}, []
        for index, name in enumerate(selected):
            row, = [r for r in rows if r['id'] == name]
            source = raw / (name + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            function = '$method177_group' + str(index)
            code += 'dec ' + function + '() : bool\ndef ' + function + '() = true\n' + ''.join('  -- if ' + check + '\n' for check in conditions)
            counts[name] = len(conditions)
            names.append(function + '()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(names) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), conditions=counts, fixture_sha256=sha(fixture))
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
