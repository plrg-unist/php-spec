#!/usr/bin/env python3
"""Source-reached parented anonymous trait alias publication and capture."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_alias_capture_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def positive(fixture, filename):
    return [
        'program_source = ' + fixture,
        'S = $php_run(program_source,12,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S.COMPLETION = BUDGET /\\ ~S.COMPILESTOP',
        'S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*',
        'statement* = [statement_use]',
        'statement_use = NStmtTraitUse (SEQUENCE (name_trait :: eps)) (SEQUENCE phpType63*) metadata_use',
        '$anonymous_member(statement_use)',
        '$anonymous_trait_adaptations(phpType63*)',
        'phpType63* = (NStmtTraitUseAdaptationAlias ABSENT phpType11_method ABSENT phpType3_alias metadata_adaptation) :: eps',
        '~$anonymous_trait_adaptations((NStmtTraitUseAdaptationAlias ABSENT phpType11_method (INTEGER 8) phpType3_alias metadata_adaptation) :: eps)',
        '$anonymous_trait_adaptations((NStmtTraitUseAdaptationAlias phpType44 phpType11_method ABSENT phpType3_alias metadata_adaptation) :: eps)',
        '$anonymous_trait_adaptations(phpType63* ++ phpType63*)',
        '$anonymous_members(statement*)',
        '$anonymous_trait_use_count(statement*) = 1',
        '$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
        '$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 ABSENT (SEQUENCE eps) (SEQUENCE statement*) metadata_class)',
        '$anonymous_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE eps) (SEQUENCE (statement_use :: statement_use :: eps)) metadata_class)',
        '$anonymous_interface_class_node(NStmtClass phpType14 phpType24 phpType3 phpType44 (SEQUENCE (name_trait :: eps)) (SEQUENCE statement*) metadata_class)',
        'S.ORIGIN = (PORIGIN 0 pcpath)',
        '$source_unit(S.SOURCES,0) = (pcunit)',
        '$compilation_projection(S,pcunit) = (ppinstalled)',
        '$class_at(ppinstalled.CLASSES,PORIGIN 0 (pcpath ++ [PCFIELD 0])) = (pclassdesc_raw)',
        '$class_at(S.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)] = pclassdesc_raw',
        'pclassdesc_live.NAME = $ptascii("Base168@anonymous") ++ [0] ++ ' + term(filename) + ' ++ [58,57,36,48]',
        'pclassdesc_live.PARENT = ($ptascii("Base168")) /\\ pclassdesc_live.INTERFACES = eps',
        '$class_named(S.CLASSNAMES,$ptascii("base168")) = (porigin_base)',
        '$class_link_at(S.LINKEDPARENTS,pclassdesc_live.ORIGIN) = (SOURCE_PARENT porigin_base)',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$declaration_history_valid(S)',
        '$anonymous_new_descriptor(S,PORIGIN 0 pcpath) = (pclassdesc_live)',
        '$anonymous_new_available(S,pclassdesc_live)',
        'pclassdesc_live.METHODS = pmethoddesc_q :: pmethoddesc_tail*',
        'pmethoddesc_q.NAME = $ptascii("q") /\\ pmethoddesc_q.OWNER = pclassdesc_live.ORIGIN',
        'pmethoddesc_q.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_source $ptascii("q")',
        'pmethoddesc_q.FUNCTION.NAME = pclassdesc_live.NAME ++ $ptascii("::q")',
        'pmethoddesc_q.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
        'psparam.TYPE = [(PTBRANCH ([PTCLASS $ptascii("Base168")]))]',
        'pclassdesc_forged = pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_q]]',
        'S_forged = S[.CLASSES = $trait_class_set(S.CLASSES,pclassdesc_forged)]',
        '~$declaration_history_valid(S_forged)',
        '$anonymous_new_descriptor(S_forged,PORIGIN 0 pcpath) = eps',
        'S_one = $drive_steps(S[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = KNOWN (POBJECT n_object)',
        'S_one.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '(HOBJECT n_object) <- S_one.ALLOCATIONS',
        '$class_state_valid(S_one[.COMPLETION = NORMAL])',
        '$heap_valid($heap_graph(S_one))',
    ]


def wrong_type(fixture, filename):
    run = lambda steps: '$php_run(program_source,' + str(steps) + ',' + json.dumps(base64.b64encode(filename).decode()) + ')'
    return [
        'program_source = ' + fixture,
        'S = ' + run(87),
        'S.COMPLETION = BUDGET',
        'S.TODO = (TYPE_RECEIVE porigin_method 0) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
        'pcallcontext.INSTANCE = (n_capture)',
        'pcallcontext.FUNCTION = porigin_method',
        'S.OBJECTS[n_capture] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_owner eps)',
        '$closure_scope_at(S.CLOSURESCOPES,n_capture) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_owner /\\ pclosurescope.CALLED = porigin_owner',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner) /\\ pcallcontext.CALLED_CLASS = (porigin_owner)',
        '$class_at(S.CLASSES,porigin_owner) = (pclassdesc)',
        'pclassdesc.KIND = "class" /\\ pclassdesc.PARENT = ($ptascii("Base168")) /\\ pclassdesc.INTERFACES = eps',
        'pclassdesc.NAME = $ptascii("Base168@anonymous") ++ [0] ++ ' + term(filename) + ' ++ [58,57,36,48]',
        '$class_named(S.CLASSNAMES,$ptascii("base168")) = (porigin_base)',
        '$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_base)',
        '$anonymous_runtime_declaration(S.DECLARATIONS,porigin_owner)',
        '$closure_method_origin(S,porigin_method) = (pmethoddesc_q)',
        'pmethoddesc_q.NAME = $ptascii("q") /\\ pmethoddesc_q.OWNER = porigin_owner',
        'pmethoddesc_q.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_owner porigin_source $ptascii("q")',
        'pmethoddesc_q.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
        'psparam.TYPE = [(PTBRANCH ([PTCLASS $ptascii("Base168")]))]',
        '$constant_callable_record(S.CONSTANTCLOSURES,n_capture) = (pconstantclosure)',
        '$constant_callable_record_valid(S,pconstantclosure)',
        '$class_constant_callable_method_history_ordinary(S,pmethoddesc_q,porigin_site,porigin_owner,pclosurescope) = (porigin_owner)',
        '$lookup(S.ENV,$ptascii("value")) = (n_value_cell)',
        'S.STORE[n_value_cell] = DEFINED (POBJECT n_wrong)',
        'S.OBJECTS[n_wrong] = INSTANCE porigin_wrong',
        '$class_at(S.CLASSES,porigin_wrong) = (pclassdesc_wrong)',
        'pclassdesc_wrong.NAME = $ptascii("Other168")',
        'S.EVENTS = [OUTPUT $ptascii("pre;"), OUTPUT $ptascii("cap:"), OUTPUT pclassdesc.NAME, OUTPUT $ptascii(";")]',
        'S_one = $drive_steps(S[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        'S_one.EVENTS = S.EVENTS',
        'S_final = ' + run(100),
        'S_final.COMPLETION = UNCAUGHT n_error',
        'S_final.ERRORORIGIN = porigin_method',
        'S_final.EVENTS = S.EVENTS',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = json.loads(CATALOGUE.read_text())['cases']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    for row, checks in ((cases[0], positive), (cases[1], wrong_type)):
        raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-alias-', dir=ROOT / '.tools'))
        source = raw / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256']
        watched = [ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/383-anonymous-classes.watsup',
                   CATALOGUE, source, Path(__file__), ROOT / '_build/default/adapter/main.exe',
                   ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
        before = {str(path): sha(path) for path in watched}
        report = {'passed': False, 'case': row['id'], 'source_sha256': row['source_sha256'],
                  'inputs_before': before, 'raw': str(raw)}
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
            conditions = checks(checked['fixture'], os.fsencode(source))
            fixture = raw / 'protocol.watsup'
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + condition + '\n' for condition in conditions))
            result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                           '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 1200, ROOT)
            report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                          stderr=result.stderr.decode(errors='replace'),
                          conditions=len(conditions), fixture_sha256=sha(fixture))
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
