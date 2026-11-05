#!/usr/bin/env python3
"""Independent dynamic-source publication, counter and copied-scope guards."""
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
CATALOGUE = ROOT / 'tests/semantics/dynamic_anonymous_trait_cases.json'
PREFIX = r'''
dec $class171_review_front(pstate, nat) : bool
def $class171_review_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN 1 pcpath)
  -- if $anonymous_new_pending(S, PORIGIN 1 pcpath) =/= eps
def $class171_review_front(S, 1) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.OBJECTS[n] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin porigin_site porigin_called eps)
def $class171_review_front(S, n) = false -- otherwise
dec $class171_review_seek(pstate, nat, nat) : pstate
def $class171_review_seek(S, n_front, 0) = S
def $class171_review_seek(S, n_front, n) = S
  -- if $(n > 0)
  -- if $class171_review_front(S,n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $class171_review_seek(S,n_front,n) = $class171_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_front,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$class171_review_front(S,n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $class171_review_drop_close(pdeclaration*, nat) : pdeclaration*
def $class171_review_drop_close(eps,n) = eps
def $class171_review_drop_close((PDEXIT n PCSCOMPLETE) :: pdeclaration_tail*,n) = $class171_review_drop_close(pdeclaration_tail*,n)
def $class171_review_drop_close(pdeclaration :: pdeclaration_tail*,n) = pdeclaration :: $class171_review_drop_close(pdeclaration_tail*,n)
  -- if pdeclaration =/= PDEXIT n PCSCOMPLETE
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


def assertions(row, main, response, code, case):
    include = bool(row.get('files'))
    missing = row['id'] == 'eval-stringable-missing-parent-receive'
    mainfile = os.fsencode(case / 'main.php')
    if include:
        sourcefile = os.fsencode(case / 'child.php')
        line, counter, count = 2, 0, 1
        name = b'Probe171Base@anonymous\0' + sourcefile + b':2$0'
        opened = ('FILE_OPENED pfilecontext.NONCE pfilecontext.CALLER pfilecontext.REQUESTED '
                  + term(sourcefile) + ' ' + term(sourcefile) + ' ' + term(code))
        checks = [
            'program_source = ' + main,
            'S_open = $php_file_run(program_source,1000,' + term(mainfile) + ',' + term(os.fsencode(case)) + ')',
            'S_open.COMPLETION = SOURCE_PENDING',
            'S_open.FILECONTEXTS = pfilecontext :: eps',
            '$file_open_response_valid(S_open,' + opened + ')',
            'S_wait = $file_open_resume(S_open,' + opened + ')',
            'S_wait.COMPLETION = SOURCE_PENDING',
            '$file_parse_response_valid(S_wait,' + response + ')',
            'S_body = $file_parse_resume(S_wait,' + response + ')',
        ]
    else:
        call_line = next(n for n, text in enumerate(row['source'].splitlines(), 1)
                         if '$object = eval(' in text)
        sourcefile = mainfile + b'(' + str(call_line).encode() + b") : eval()'d code"
        line, counter, count = (1, 0, 1) if missing else (2, 1, 2)
        name = b'class@anonymous\0' + sourcefile + b':' + str(line).encode() + b'$' + str(counter).encode()
        checks = [
            'program_source = ' + main,
            'S_wait = $php_run(program_source,1000,' + json.dumps(base64.b64encode(mainfile).decode()) + ')',
            'S_wait.COMPLETION = SOURCE_PENDING',
            'S_wait.EVALCONTEXTS = pevalcontext :: eps',
            'pevalcontext.UNIT = 1 /\\ pevalcontext.BYTES = ' + term(code),
            '$eval_response_valid(S_wait,' + response + ')',
            'S_body = $eval_resume(S_wait,' + response + ')',
        ]
    checks += [
        'S_pre = $class171_review_seek(S_body,0,800)',
        '$class171_review_front(S_pre,0)',
        'S_pre.ORIGIN = (PORIGIN 1 pcpath_new)',
        'porigin_new = PORIGIN 1 pcpath_new',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        'pclassdesc_raw.ORIGIN = PORIGIN 1 (pcpath_new ++ [PCFIELD 0])',
        '~pclassdesc_raw.EARLY',
        'pclassdesc_raw.NAME = ' + term(name),
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '$declaration_unit_complete(S_pre.DECLARATIONS,1)',
        'S_pre.SOURCES = [pcunit_root,pcunit_dynamic]',
        'pcunit_root.ID = 0 /\\ pcunit_dynamic.ID = 1',
        '$anonymous_rtd_unit(pcunit_dynamic) = (' + str(count) + ')',
        '$class_constant_compile_entry(S_pre,1) = (S_entry)',
        '$anonymous_history_seed(S_pre,1) = (0)',
        '$compilation_projection(S_pre,pcunit_dynamic) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_raw)',
        '$anonymous_compiled_class_count(pcunit_dynamic,' + term(sourcefile) + ',ppinstalled.CLASSES,eps,(S_entry),0) = (' + str(count) + ')',
        '$anonymous_compiled_class_count(pcunit_dynamic,' + term(sourcefile) + ',ppinstalled.CLASSES,eps,(S_entry),1) = eps',
        'S_link = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_link.COMPLETION = BUDGET',
        '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live.NAME = pclassdesc_raw.NAME',
        '$anonymous_trait_projection(pclassdesc_raw,pclassdesc_live)',
        '$declaration_history_valid(S_link)',
        '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$anonymous_new_descriptor(S_link,porigin_new) = (pclassdesc_live)',
        '$anonymous_new_available(S_link,pclassdesc_live)',
        '$call_sourcefile(S_link.FILES,pclassdesc_live.ORIGIN) = (' + term(sourcefile) + ')',
        'S_no_close = S_link[.DECLARATIONS = $class171_review_drop_close(S_link.DECLARATIONS,1)]',
        '~$declaration_unit_complete(S_no_close.DECLARATIONS,1)',
        '$anonymous_new_descriptor(S_no_close,porigin_new) = eps',
        'S_wrong_unit = S_link[.SOURCES = [pcunit_root,pcunit_dynamic[.ID = 2]]]',
        '$anonymous_new_descriptor(S_wrong_unit,porigin_new) = eps',
        'S_unpublished = S_link[.CLASSNAMES = S_pre.CLASSNAMES]',
        '$anonymous_new_descriptor(S_unpublished,porigin_new) = eps',
        'pclassdesc_wrong = pclassdesc_live[.NAME = $ptascii("wrong171")]',
        '~$anonymous_trait_projection(pclassdesc_raw,pclassdesc_wrong)',
        'S_wrong_name = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_wrong)]',
        '$anonymous_new_descriptor(S_wrong_name,porigin_new) = eps',
        'S_allocate = $drive_steps(S_link[.COMPLETION = NORMAL],1)',
        'S_allocate.COMPLETION = BUDGET',
        'S_allocate.RESULT = KNOWN (POBJECT n_object)',
        'S_allocate.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '(HOBJECT n_object) <- S_allocate.ALLOCATIONS',
        '$class_state_valid(S_allocate[.COMPLETION = NORMAL])',
        '$method_named(pclassdesc_live.METHODS,$ptascii("' + ('q' if include else 'm') + '")) = (pmethoddesc_capture)',
        'pmethoddesc_capture.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_method_source pmethoddesc_capture.NAME',
        'porigin_method_source = PORIGIN 0 pcpath_method_source',
        '$class_method_origin(S_link.CLASSES,porigin_method_source) = (pmethoddesc_source)',
        'pmethoddesc_source.NAME = $ptascii("m")',
        'pmethoddesc_capture.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
        'psparam.TYPE = [(PTBRANCH ([' + ('PTCLASS $ptascii("Probe171Base")' if include else 'PTPARENT' if missing else 'PTCLASS pclassdesc_live.NAME') + ']))]',
        'S_receive = $class171_review_seek(S_allocate,1,800)',
        '$class171_review_front(S_receive,1) /\\ S_receive.COMPLETION = BUDGET',
        'S_receive.TODO = (TYPE_RECEIVE pmethoddesc_capture.FUNCTION.ORIGIN 0) :: ptask_tail*',
        'S_receive.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
        'S_receive.OBJECTS[n_capture] = CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_capture.FUNCTION.ORIGIN porigin_site pclassdesc_live.ORIGIN eps)',
        '$closure_scope_at(S_receive.CLOSURESCOPES,n_capture) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_live.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_live.ORIGIN',
        '$class_constant_callable_method_history_ordinary(S_receive,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
        '$call_current_valid(S_receive)',
    ]
    if include:
        checks += [
            'pclassdesc_raw.INTERFACES = [$ptascii("Probe171I")]',
            'pclassdesc_live.INTERFACES = [$ptascii("Probe171I"),$ptascii("Stringable")]',
            '$class_at(S_link.CLASSES,pmethoddesc_source.OWNER) = (pclassdesc_trait)',
            'pclassdesc_trait.NAME = $ptascii("Probe171Excluded")',
            '$method_closure_functions(S_receive,n_capture,pmethoddesc_capture) = (pmethoddesc_capture.FUNCTION,pmethoddesc_capture.FUNCTION)',
        ]
    elif missing:
        checks += [
            'pclassdesc_raw.INTERFACES = eps /\\ pclassdesc_live.INTERFACES = [$ptascii("Stringable")]',
            '$trait_real_birth_at(S_receive.CLASSCONSTANTHISTORY,n_capture) = eps',
            '$trait_fcc_scope_owner(S_receive,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
            '$trait_fcc_parameter_function(S_receive,n_capture,pmethoddesc_capture) = (pfunction_view)',
            'pfunction_view.SIGNATURE.PARAMETERS = psparam :: eps',
            '~$ppsupported_signature(pfunction_view.SIGNATURE)',
            '$call_supported_signature(S_receive,pfunction_view)',
            'S_receive.LINKEDINTERFACES = [{OWNER pclassdesc_live.ORIGIN,TARGETS ([PILBUILTIN $ptascii("Stringable")])}]',
            'pclassdesc_double = pclassdesc_live[.INTERFACES = [$ptascii("Stringable"),$ptascii("Stringable")]]',
            'S_synced = S_receive[.CLASSES = $trait_class_set(S_receive.CLASSES,pclassdesc_double)][.LINKEDINTERFACES = [{OWNER pclassdesc_live.ORIGIN,TARGETS ([PILBUILTIN $ptascii("Stringable"),PILBUILTIN $ptascii("Stringable")])}]]',
            '$anonymous_interface_targets_valid(S_synced,pclassdesc_double)',
            '$class_constant_callable_method_history_ordinary(S_synced,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
            '~$declaration_history_valid(S_synced)',
            '$trait_fcc_scope_owner(S_synced,pmethoddesc_capture,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = eps',
            'S_receive.EVENTS = [OUTPUT $ptascii("before;"),OUTPUT $ptascii("captured;")]',
            'S_fatal = $drive_steps(S_receive[.COMPLETION = NORMAL],1)',
            'S_fatal.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("Cannot access \\"parent\\" when current class scope has no parent") 4',
        ]
    else:
        checks += [
            'pclassdesc_raw.INTERFACES = eps /\\ pclassdesc_live.INTERFACES = eps',
            '$method_closure_functions(S_receive,n_capture,pmethoddesc_capture) = (pmethoddesc_capture.FUNCTION,pmethoddesc_capture.FUNCTION)',
            'ppinstalled.CLASSES = [pclassdesc_skipped,pclassdesc_raw]',
            'pclassdesc_skipped.ORIGIN = PORIGIN 1 pcpath_skipped',
            'pclassdesc_skipped.NAME = ' + term(b'class@anonymous\0' + sourcefile + b':1$0'),
            '$class_at(S_link.CLASSES,pclassdesc_skipped.ORIGIN) = (pclassdesc_skipped)',
            '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc_skipped.NAME)) = eps',
            '~$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_skipped.ORIGIN)',
            '$lookup(S_receive.ENV,$ptascii("value")) = (n_value)',
            'S_receive.STORE[n_value] = DEFINED (POBJECT n_object)',
            '$trace_value_text(S_receive,POBJECT n_object) = $ptascii("Object(class@anonymous)")',
        ]
    return checks


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
    selected = ['include-parent-interface-excluded-alias-capture',
                'eval-skipped-trait-conflict-counter',
                'eval-stringable-missing-parent-receive']
    raw = Path(tempfile.mkdtemp(prefix='class171-review-state-', dir=ROOT / '.tools'))
    watched = [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/383-anonymous-classes.watsup',
               ROOT / 'spec/semantics/307-trait-callable-target-fixups.watsup', ROOT / 'tests/semantics/profile.json',
               ROOT / '.tools/php/bin/php', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe', CATALOGUE, Path(__file__)]
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'affinity': sorted(os.sched_getaffinity(0))}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        fixture_text, groups, counts = PREFIX, [], {}
        for n, name in enumerate(selected):
            row = cases[name]
            case = raw / name
            case.mkdir()
            source = case / 'main.php'
            source.write_text(row['source'])
            assert sha(source) == row['source_sha256']
            for file in row.get('files', []):
                path = case / file['name']
                path.write_text(file['source'])
                assert sha(path) == file['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            if row.get('files'):
                code = (case / 'child.php').read_bytes()
                request = dict(op='parse-file', id='1', mode='file', profile='cli-raw-85',
                               source=base64.b64encode(code).decode(),
                               requested=base64.b64encode(os.fsencode(case / 'child.php')).decode(),
                               resolved=base64.b64encode(os.fsencode(case / 'child.php')).decode(),
                               opened=base64.b64encode(os.fsencode(case / 'child.php')).decode())
            else:
                prefix = b'if (false)' if name == 'eval-skipped-trait-conflict-counter' else b'return new class'
                code, = [base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast'])
                         if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(prefix)]
                request = dict(op='parse-eval', id='1', mode='eval', profile='cli-raw-85', source=base64.b64encode(code).decode())
            child = frontend.request(request)
            assert child['accepted']
            child_fixture = adapter.request({'op': 'check', 'ast': child['ast'], 'fixture': True})['fixture']
            response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + child_fixture
            conditions = assertions(row, checked['fixture'], response, code, case)
            group = '$class171_review_group' + str(n)
            fixture_text += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n' + ''.join(
                '  -- if ' + condition + '\n' for condition in conditions)
            groups.append(group + '()')
            counts[name] = len(conditions)
        fixture = raw / 'protocol.watsup'
        fixture.write_text(fixture_text + 'dec $main() : bool\ndef $main() = ' + ' /\\ '.join(groups) + '\n')
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)]
        result = cross.invoke.process(command, raw / 'numeric', 1200, ROOT)
        report.update(command=command, exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
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
        report['inputs_stable'] = before == report['inputs_after']
        report['passed'] = report['passed'] and report['inputs_stable']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
