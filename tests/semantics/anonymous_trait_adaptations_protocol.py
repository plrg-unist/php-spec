#!/usr/bin/env python3
"""Source-reached ordinary anonymous trait adaptation, publication and capture."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_trait_adaptations_cases.json'
PREFIX = r'''
dec $class169_front(pstate, nat) : bool
def $class169_front(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_pending(S, porigin) =/= eps
def $class169_front(S, 1) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE eps) metadata_new)) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if $anonymous_new_name(S, porigin) =/= eps
def $class169_front(S, 2) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
def $class169_front(S, n_stage) = false -- otherwise
dec $class169_seek(pstate, nat, nat) : pstate
def $class169_seek(S, n_stage, 0) = S
def $class169_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $class169_front(S, n_stage)
def $class169_seek(S, n_stage, n) = $class169_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$class169_front(S, n_stage)
  -- if S.COMPLETION = BUDGET \/ S.COMPLETION = NORMAL
def $class169_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if ~$class169_front(S, n_stage)
  -- if S.COMPLETION =/= BUDGET /\ S.COMPLETION =/= NORMAL
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def checks(row, fixture, filename):
    if row['id'] == 'private-final-qualified-alias-warning':
        return warning_checks(fixture, filename)
    parented = row['id'] == 'interface-and-parent-multiple-adaptation'
    prefix = 'Probe169BothBase@anonymous' if parented else 'class@anonymous'
    line = next(i for i, text in enumerate(row['source'].splitlines(), 1)
                if '$object = new class' in text)
    conditions = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_pre = $class169_seek(S_initial,0,100)',
        'S_pre.COMPLETION = BUDGET /\\ $class169_front(S_pre,0)',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
        '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
        '~pclassdesc_raw.EARLY',
        'pclassdesc_raw.NAME = $ptascii(' + json.dumps(prefix) + ') ++ [0] ++ ' + term(filename)
        + ' ++ [58] ++ $ntunsigned(' + str(line) + ') ++ [36,48]',
        '$origin_node(S_pre.SOURCES,pclassdesc_raw.ORIGIN) = (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 (SEQUENCE statement*) metadata_class)',
        '$anonymous_members(statement*)',
        '$trait_plan(S_pre,pclassdesc_raw) = ptraitplan',
        '|ptraitplan.TRAITS| = ' + ('2' if parented else '1'),
        '|ptraitplan.PRECEDENCES| = ' + ('1' if parented else '0'),
        '|ptraitplan.ALIASES| = ' + ('1' if parented else '3'),
        '$class_link_at(S_pre.LINKEDPARENTS,pclassdesc_raw.ORIGIN) = eps',
        '$pil_at(S_pre.LINKEDINTERFACES,pclassdesc_raw.ORIGIN) = eps',
        'S_link = $class169_seek(S_pre,1,10)',
        'S_link.COMPLETION = BUDGET /\\ $class169_front(S_link,1)',
        '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)] = pclassdesc_raw',
        '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$declaration_history_valid(S_link)',
        '$anonymous_new_descriptor(S_link,porigin_new) = (pclassdesc_live)',
        '$anonymous_new_available(S_link,pclassdesc_live)',
        '$anonymous_new_pending(S_link,porigin_new) = eps',
        '$method_named(pclassdesc_live.METHODS,$ptascii("q")) = (pmethoddesc_q)',
        'pmethoddesc_q.OWNER = pclassdesc_live.ORIGIN /\\ pmethoddesc_q.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_q.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_source $ptascii("q")',
        'pclassdesc_forged = pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_q]]',
        'S_forged = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_forged)]',
        '~$declaration_history_valid(S_forged)',
        '$anonymous_new_descriptor(S_forged,porigin_new) = eps',
        'S_alloc = $drive_steps(S_link[.COMPLETION = NORMAL],1)',
        'S_alloc.COMPLETION = BUDGET',
        'S_alloc.RESULT = KNOWN (POBJECT n_object)',
        'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        '$class_state_valid(S_alloc[.COMPLETION = NORMAL])',
        '$heap_valid($heap_graph(S_alloc))',
        'S_receive = $class169_seek(S_alloc,2,500)',
        'S_receive.COMPLETION = BUDGET /\\ $class169_front(S_receive,2)',
        'S_receive.TODO = (TYPE_RECEIVE pmethoddesc_q.FUNCTION.ORIGIN 0) :: ptask_tail*',
        'S_receive.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_capture',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
        'S_receive.OBJECTS[n_capture] = CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_q.FUNCTION.ORIGIN porigin_site pclassdesc_live.ORIGIN eps)',
        '$closure_scope_at(S_receive.CLOSURESCOPES,n_capture) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_live.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_live.ORIGIN',
        '$constant_callable_record(S_receive.CONSTANTCLOSURES,n_capture) = (pconstantclosure)',
        '$constant_callable_record_valid(S_receive,pconstantclosure)',
        '$drive_steps(S_receive[.COMPLETION = NORMAL],0) = S_receive',
        'S_next = $drive_steps(S_receive[.COMPLETION = NORMAL],1)',
        'S_next.COMPLETION = BUDGET',
    ]
    if parented:
        conditions += [
            'pclassdesc_live.PARENT = ($ptascii("Probe169BothBase"))',
            'pclassdesc_live.INTERFACES = [$ptascii("Probe169Both")]',
            '$anonymous_parent_linked(S_link,pclassdesc_live)',
            '$anonymous_interface_targets_valid(S_link,pclassdesc_live)',
            'pmethoddesc_q.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
            'psparam.TYPE = [(PTBRANCH ([PTCLASS $ptascii("Probe169BothBase")]))]',
            '$class_method_origin(S_receive.CLASSES,porigin_source) = (pmethoddesc_source)',
            '$class_at(S_receive.CLASSES,pmethoddesc_source.OWNER) = (pclassdesc_trait)',
            'pclassdesc_trait.NAME = $ptascii("Probe169BothR")',
        ]
    else:
        conditions += [
            'pclassdesc_live.PARENT = eps /\\ pclassdesc_live.INTERFACES = eps',
            '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = eps',
            '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = eps',
            '$method_named(pclassdesc_live.METHODS,$ptascii("hidden")) = (pmethoddesc_hidden)',
            'pmethoddesc_hidden.VISIBILITY = PROPERTY_PROTECTED',
            '$method_named(pclassdesc_live.METHODS,$ptascii("privateAlias")) = (pmethoddesc_private)',
            'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
            '~$anonymous_trait_adaptations([(NStmtTraitUseAdaptationAlias ABSENT (NIdentifier (BYTES "bQ==") eps) (INTEGER 8) (NIdentifier (BYTES "cQ==") eps) eps)])',
            '~$anonymous_trait_adaptations([(NStmtTraitUseAdaptationAlias ABSENT (NIdentifier (BYTES "bQ==") eps) (INTEGER 33) (NIdentifier (BYTES "cQ==") eps) eps)])',
            '~$anonymous_trait_adaptations([(NStmtTraitUseAdaptationAlias ABSENT (NIdentifier (BYTES "bQ==") eps) ABSENT ABSENT eps)])',
            '~$anonymous_trait_adaptations([(NStmtTraitUseAdaptationPrecedence ABSENT (NIdentifier (BYTES "bQ==") eps) (SEQUENCE eps) eps)])',
            '~$anonymous_member(NStmtTraitUse (SEQUENCE eps) (SEQUENCE eps) eps)',
        ]
    return conditions



def warning_checks(fixture, filename):
    return [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(base64.b64encode(filename).decode()) + ')',
        'S_pre = $class169_seek(S_initial,0,100)',
        'S_pre.COMPLETION = BUDGET /\\ $class169_front(S_pre,0)',
        'S_pre.ORIGIN = (porigin_new)',
        '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
        'S_notice = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
        'S_notice.COMPLETION = BUDGET',
        'S_notice.TODO = (DECL_NOTICES pdeclnoticebatch) :: (AT porigin_new (EVAL expression_new)) :: ptask_tail*',
        'S_notice.ORIGIN = (pclassdesc_raw.ORIGIN)',
        'pdeclnoticebatch.KIND = NOTICE_RUNTIME /\\ pdeclnoticebatch.SITE = pclassdesc_raw.ORIGIN',
        '$origin_node(S_notice.SOURCES,porigin_new) = (expression_new)',
        '$class_at(S_notice.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
        'pclassdesc_live =/= pclassdesc_raw',
        '$class_named(S_notice.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
        '$anonymous_runtime_declaration(S_notice.DECLARATIONS,pclassdesc_live.ORIGIN)',
        '$declaration_history_valid(S_notice)',
        'pdeclnoticebatch.CLASSES = [(pclassdesc_live.ORIGIN,n_prefix)]',
        'S_notice.DECLARATIONS[n_prefix] = PDRCLASS pclassdesc_live.ORIGIN pdeclcause',
        'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE pclassdesc_live.ORIGIN n_prefix n_user pfdiagnostic)]',
        '$trait_notice_plan(S_notice,pclassdesc_live.ORIGIN,n_prefix,n_user) = (pdeclnoticebatch.NOTICES)',
        'pdeclnoticebatch.INDEX = 0 /\\ pdeclnoticebatch.LINE = 4',
        'pfdiagnostic.LEVEL = 128 /\\ pfdiagnostic.LINE = 4',
        'pfdiagnostic.MESSAGE = $ptascii("Private methods cannot be final as they are never overridden by other classes")',
        '$iterator_notice_batch_valid(S_notice,pdeclnoticebatch)',
        '~$error_handler_eligible(S_notice,128)',
        'S_notice.EVENTS = [OUTPUT $ptascii("before;")]',
        'S_notice.OBJECTS = eps',
        'S_wrong_origin = S_notice[.ORIGIN = (porigin_new)]',
        '~$iterator_notice_batch_valid(S_wrong_origin,pdeclnoticebatch)',
        '~$iterator_notice_batch_valid(S_notice,pdeclnoticebatch[.LINE = 5])',
        'pdeclnoticebatch_forged = pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE pclassdesc_live.ORIGIN n_prefix n_user pfdiagnostic[.LEVEL = 2])]]',
        '~$iterator_notice_batch_valid(S_notice,pdeclnoticebatch_forged)',
        'S_dispatch = $drive_steps(S_notice[.COMPLETION = NORMAL],1)',
        'S_dispatch.COMPLETION = BUDGET',
        'S_dispatch.ORIGIN = S_notice.ORIGIN',
        'S_dispatch.OBJECTS = eps',
        'S_dispatch.EVENTS = S_notice.EVENTS ++ [DIAGNOSTIC_SOURCE 0 "Warning" pfdiagnostic.MESSAGE 4]',
        'S_dispatch.TODO = (DECL_NOTICE_RESUME pdeclnoticebatch[.INDEX = 1]) :: (AT porigin_new (EVAL expression_new)) :: ptask_tail*',
        'S_resume = $drive_steps(S_dispatch[.COMPLETION = NORMAL],1)',
        'S_resume.TODO = (DECL_NOTICES pdeclnoticebatch[.INDEX = 1]) :: (AT porigin_new (EVAL expression_new)) :: ptask_tail*',
        'S_resume.EVENTS = S_dispatch.EVENTS',
        'S_done = $drive_steps(S_resume[.COMPLETION = NORMAL],1)',
        'S_done.TODO = (AT porigin_new (EVAL expression_new)) :: ptask_tail*',
        'S_done.ORIGIN = S_notice.ORIGIN',
        'S_enter = $drive_steps(S_done[.COMPLETION = NORMAL],1)',
        'S_enter.ORIGIN = (porigin_new)',
        'S_enter.TODO = (EVAL expression_new) :: (ORIGIN_RETURN S_notice.ORIGIN) :: ptask_tail*',
        'S_alloc = $drive_steps(S_enter[.COMPLETION = NORMAL],1)',
        'S_alloc.COMPLETION = BUDGET',
        'S_alloc.RESULT = KNOWN (POBJECT n_object)',
        'S_alloc.OBJECTS[n_object] = INSTANCE pclassdesc_live.ORIGIN',
        'S_alloc.EVENTS = S_dispatch.EVENTS',
        '$class_state_valid(S_alloc[.COMPLETION = NORMAL])',
        '$heap_valid($heap_graph(S_alloc))',
        'S_without_notice = S_notice[.COMPLETION = NORMAL][.TODO = (EVAL expression_new) :: ptask_tail*]',
        '$anonymous_link_resume(S_without_notice,porigin_new) = S_without_notice[.ORIGIN = (porigin_new)]',
    ]


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    cases = json.loads(CATALOGUE.read_text())['cases']
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    for row in [row for row in cases if row['id'] in ('parentless-multiple-aliases', 'interface-and-parent-multiple-adaptation', 'private-final-qualified-alias-warning')]:
        raw = Path(tempfile.mkdtemp(prefix='anonymous-trait-adaptations-', dir=ROOT / '.tools'))
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
            conditions = checks(row, checked['fixture'], os.fsencode(source))
            fixture = raw / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
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
