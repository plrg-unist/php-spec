#!/usr/bin/env python3
"""Check object selection retirement, notice reentry and supplied throw cancellation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / 'tests/semantics/deprecated_object_selector_notice_review'
SOURCES = {name: SOURCE_DIR / (name + '.php') for name in ('destructor-reentry', 'destructor-throw')}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $object_review_ready(pstate,nat) : bool
def $object_review_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier phpType33 metadata) z) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = INSTANCE porigin
def $object_review_ready(S,1) = true
  -- if $ccn_ready(S,0)
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_FETCH porigin ptbytes_class ptbytes_member z
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|")
def $object_review_ready(S,2) = true
  -- if $ccn_ready(S,0)
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|H|9|")
def $object_review_ready(S,3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_FETCH porigin ptbytes_class ptbytes_member z
  -- if pdestructionoperation.PENDING = (n)
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|")
def $object_review_ready(S,n) = false -- otherwise
dec $object_review_pause(pstate,nat,nat) : pstate
def $object_review_pause(S,n_mode,n) = S -- if $object_review_ready(S,n_mode)
def $object_review_pause(S,n_mode,n) = $object_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$object_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $object_review_pause(S,n_mode,n) = S -- otherwise
'''


def recipe(fixture, name, source):
    namespace = 'Ns238Reentry' if name == 'destructor-reentry' else 'Ns238Throw'
    member = 'A' if name == 'destructor-reentry' else 'TREE'
    child = quoted(namespace + '\\Child238'); base = quoted(namespace + '\\Base238')
    expected = json.loads((SOURCE_DIR / 'cases.json').read_text())[name]['stdout']
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw = $object_review_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$object_review_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) :: ptask_tail*',
        '$base64(text_member) = $ptascii("' + member + '")',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = KNOWN (POBJECT n_receiver)',
        '$class_named(S_raw.CLASSNAMES,$ptlc(' + child + ')) = (porigin_child)',
        '$class_named(S_raw.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_child',
        '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS', '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING ' + child + ')',
        '$heap_owners($heap_graph(S_class),HOBJECT n_receiver) = 0',
        '$class_constant_lookup(S_class,porigin_child,$ptascii("' + member + '"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.FOLDED',
        '$class_constant_object_entry(S_class,S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_object_entry(S_class,REFERENCE 0,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class,KNOWN PNULL,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class[.RESULT = KNOWN (PSTRING ' + base + ')],S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class[.HELD = [HOBJECT n_receiver]],S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        'PhpStep: S_raw ~> S_neutral',
        'ptask_cursor = CLASS_CONST_OBJECT_FETCH porigin_site ' + child + ' $ptascii("' + member + '") z',
        'S_neutral.TODO = ptask_cursor :: ptask_tail*', 'S_neutral.COMPLETION = NORMAL',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_cursor) = eps', '~$class_constant_notice_task(ptask_cursor,porigin_decl)',
        '~$class_constant_notice_protected(S_neutral,porigin_decl)',
        '$class_constant_object_fetch_valid(S_neutral,porigin_site,' + child + ',$ptascii("' + member + '"),z)',
        '$class_constant_object_fetch_valid(S_neutral,porigin_site,' + base + ',$ptascii("' + member + '"),z)',
        '$call_task_valid(S_neutral,ptask_cursor)',
        '(HOBJECT n_receiver) <- $eager_slots(S_raw,S_neutral)',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) = ptask_cursor',
        'S_release_raw = $drive_steps(S_raw,1)', 'S_release_raw.COMPLETION = BUDGET',
        'S_release = S_release_raw[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = ptask_cursor', 'pdestructionoperation.PENDING = eps',
        'pdestructionoperation.COMPLETION = NORMAL', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$destructor_operation_live(S_release,pdestructionoperation)',
        '$call_descriptors_valid(S_release)', '$ccn_output(S_release.EVENTS) = $ptascii("B|C|")']
    for tag, change in [('class', '.SOURCE = CLASS_CONST_OBJECT_FETCH porigin_site ' + base + ' $ptascii("' + member + '") z'),
                        ('value', '.VALUE = KNOWN (PINT 1)'), ('base', '.BASE = BASE_VALUE (KNOWN (POBJECT n_receiver))'),
                        ('completion', '.COMPLETION = BUDGET')]:
        checks += ['pdestructionoperation_' + tag + ' = pdestructionoperation[' + change + ']',
            'S_counter_' + tag + ' = S_neutral[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_' + tag + ') :: S_neutral.TODO]',
            '~$class_constant_object_operation(pdestructionoperation_' + tag + ',(S_counter_' + tag + '))']
    if name == 'destructor-reentry':
        checks += ['S_inner = $object_review_pause(S_release,1,30000)', '$object_review_ready(S_inner,1)',
            'S_inner.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_inner*',
            'perrorcall_inner.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("A") z_inner',
            'S_inner.ORIGIN = (porigin_inner)', 'porigin_inner =/= porigin_site',
            '(HOBJECT n_receiver) <- S_inner.ALLOCATIONS',
            '$ref_return_retire_operation_scope(S_inner,pdestructionoperation) = (S_scope)',
            'S_scope.ORIGIN = (porigin_site)', 'S_scope.CURRENT = eps',
            '$class_constant_object_operation(pdestructionoperation,(S_scope))',
            '$eager_operation_source_guard(S_inner,pdestructionoperation)',
            '$class_constant_notice_protected(S_inner,porigin_decl)', '$call_descriptors_valid(S_inner)',
            'S_outer = $object_review_pause(S_inner,2,30000)', '$object_review_ready(S_outer,2)',
            'S_outer.TODO = (ERROR_HANDLER_INVOKE perrorcall_outer) :: ptask_outer*',
            'perrorcall_outer.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("A") z',
            'S_outer.ORIGIN = (porigin_site)', '~((HOBJECT n_receiver) <- S_outer.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_outer),HOBJECT n_receiver) = 0',
            '$class_constant_notice_valid(S_outer,porigin_decl,' + child + ',$ptascii("A"),z)',
            '$class_constant_notice_protected(S_outer,porigin_decl)', '$error_call_valid(S_outer,perrorcall_outer)',
            'S_resume = $ccn_pause(S_outer,1,30000)', '$ccn_ready(S_resume,1)',
            '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|9|H|")',
            '$call_descriptors_valid(S_resume)', 'S_done = $drive(S_resume,30000)']
    else:
        checks += ['S_global = $global_table_view(S_raw)',
            '$lookup(S_global.ENV,$ptascii("exception238")) = (n_exception_slot)',
            'S_global.STORE[n_exception_slot] = DEFINED (POBJECT n_exception)',
            '$lookup(S_global.ENV,$ptascii("value238")) = (n_value_slot)',
            '$compiled_read(S_raw,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
            'S_pending = $object_review_pause(S_release,3,30000)', '$object_review_ready(S_pending,3)',
            'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_pending*',
            'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_exception)]',
            'ptask_pending* = ptask_cursor :: ptask_tail*',
            '$task_nodes(ptask_cursor) = eps',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_exception]',
            '$destructor_operation_live(S_pending,pdestructionoperation_pending)',
            '$eager_operation_source_guard(S_pending,pdestructionoperation_pending)',
            '$class_constant_object_fetch_valid(S_pending,porigin_site,' + child + ',$ptascii("TREE"),z)',
            '$class_constant_object_fetch_valid(S_pending[.COMPLETION = THROWING n_exception],porigin_site,' + child + ',$ptascii("TREE"),z)',
            '~((HOBJECT n_receiver) <- S_pending.ALLOCATIONS)',
            '~$class_constant_notice_protected(S_pending,porigin_decl)',
            'S_pending.CLASSCONSTANTCACHE = eps', 'S_pending.CLASSCONSTANTINIT = eps',
            '$heap_owners($heap_graph(S_pending),HARRAY n_donor) = $heap_owners($heap_graph(S_raw),HARRAY n_donor)',
            '$call_descriptors_valid(S_pending)',
            'S_pending_global = $global_table_view(S_pending)',
            'S_pending_global.STORE[n_exception_slot] = DEFINED (POBJECT n_exception)',
            'S_pending_global.STORE[n_value_slot] = DEFINED pvalue_old',
            '$string_bytes(pvalue_old) = ($ptascii("old"))',
            'S_done = $drive(S_pending,30000)']
    checks += ['S_done.COMPLETION = NORMAL', '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_done.DESTRUCTION.OPERATIONS = eps', 'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_release,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_release',
        'S_one = $drive_steps(S_release,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    suffix = '_reentry' if name == 'destructor-reentry' else '_throw'
    import re
    return [re.sub(r'\b(U|S_[A-Za-z0-9_]+|n_[A-Za-z0-9_]+|porigin_[A-Za-z0-9_]+|expression_[A-Za-z0-9_]+|text_member|metadata_member|z|z_inner|ptask_[A-Za-z0-9_]+|pclassconstantdesc|pdestructionoperation[A-Za-z0-9_]*|perrorcall_[A-Za-z0-9_]+|pvalue_old)\b', lambda match: match.group() + suffix, check) for check in checks]


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name, source in SOURCES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            checks += recipe(checked['fixture'], name, source)
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *SOURCES.values(), SOURCE_DIR / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__':
    main()
