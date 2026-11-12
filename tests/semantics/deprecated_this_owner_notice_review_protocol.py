#!/usr/bin/env python3
"""Check direct This source authority, saved receiver ownership and result COW."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_this_owner_notice_review/receiver-and-result.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $this_owner_handler_ready(pstate) : bool
def $this_owner_handler_ready(S) = true
  -- if S.TODO = (STMT (NStmtReturn phpType5 metadata)) :: ptask*
  -- if $ccn_output(S.EVENTS) = $ptascii("B|H|")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.CONTEXT = (pcallcontext_reader)
  -- if pcallcontext_reader.RECEIVER = (n_receiver)
def $this_owner_handler_ready(S) = false -- otherwise
dec $this_owner_handler_pause(pstate,nat) : pstate
def $this_owner_handler_pause(S,n) = S -- if $this_owner_handler_ready(S)
def $this_owner_handler_pause(S,n) = $this_owner_handler_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$this_owner_handler_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $this_owner_handler_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns237Owner\\Child237')
    base = quoted('Ns237Owner\\Base237')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") z',
        'S_warn.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath_site',
        '$origin_node(S_warn.SOURCES,porigin_site) = (NExprClassConstFetch (NExprVariable (BYTES text_this) metadata_this) expression_member metadata_fetch)',
        '$direct_this(BYTES text_this)',
        '$class_named(S_warn.CLASSNAMES,$ptlc(' + child + ')) = (porigin_child)',
        '$class_named(S_warn.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_base', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        'pclassconstantdesc.FOLDED',
        '$compiled_read(S_warn,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_warn.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_warn.CURRENT = (pcallcontext)', 'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.LEXICAL_CLASS = (porigin_base)', 'pcallcontext.CALLED_CLASS = (porigin_child)',
        'S_warn.OBJECTS[n_receiver] = INSTANCE porigin_child', '(HOBJECT n_receiver) <- S_warn.ALLOCATIONS',
        '$target_function(S_warn,pcallcontext.TARGET) = (pfunction)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pcpath_site) = ((z,false))',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pcpath_site ++ [PCFIELD 1]) = ((z_member,true))',
        '$compiled_read(S_warn,PORIGIN n_unit (pcpath_site ++ [PCFIELD 1])) = (PSTRING $ptascii("TREE"))',
        '$class_constant_this_selector(S_warn,porigin_site,' + child + ')',
        '$class_constant_this_source(S_warn,porigin_decl,' + child + ',$ptascii("TREE"),z)',
        '$class_constant_notice_valid(S_warn,porigin_decl,' + child + ',$ptascii("TREE"),z)',
        '$class_constant_visible(S_warn,pclassconstantdesc)',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PROTECTED])',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$ccn_output(S_warn.EVENTS) = $ptascii("B|")',
        'S_warn.RESULT = KNOWN PNULL', 'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        '$call_context_roots(S_warn.CURRENT) = [HOBJECT n_receiver]',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_machine_roots(S_warn) = eps',
        '~$class_constant_this_selector(S_warn,porigin_site,' + base + ')',
        '~$class_constant_this_selector(S_warn,porigin_site,' + quoted('\\Ns237Owner\\Child237') + ')',
        '~$class_constant_this_selector(S_warn[.CURRENT = eps],porigin_site,' + child + ')',
        '~$class_constant_this_selector(S_warn[.CURRENT = (pcallcontext[.RECEIVER = eps])],porigin_site,' + child + ')',
        '~$class_constant_this_selector(S_warn[.CURRENT = (pcallcontext[.CALLSITE = eps])],porigin_site,' + child + ')',
        '~$class_constant_this_selector(S_warn[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_child)])],porigin_site,' + child + ')',
        '~$class_constant_this_selector(S_warn[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_base)])],porigin_site,' + child + ')',
        '~$class_constant_this_selector(S_warn[.ALLOCATIONS = eps],porigin_site,' + child + ')',
        '~$class_constant_this_source(S_warn,porigin_decl,' + child + ',$ptascii("TREE"),$(z + 1))',
        '~$class_constant_this_source(S_warn,porigin_decl,' + child + ',$ptascii("MISSING"),z)',
        '~$class_constant_this_source(S_warn,porigin_base,' + child + ',$ptascii("TREE"),z)',
        '~$class_constant_notice_valid(S_warn[.ORIGIN = (porigin_base)],porigin_decl,' + child + ',$ptascii("TREE"),z)',
        '$class_constant_notice_valid(S_warn[.RESULT = KNOWN (PSTRING $ptascii("MISSING"))],porigin_decl,' + child + ',$ptascii("TREE"),z)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + base + ' $ptascii("TREE") z])',
        'S_handler = $this_owner_handler_pause(S_warn,30000)', '$this_owner_handler_ready(S_handler)',
        'S_handler.FRAMES = pframe_reader :: pframe_tail*', 'pframe_reader.CONTEXT = (pcallcontext)',
        '$call_context_roots(S_handler.CURRENT) = eps',
        '(HOBJECT n_receiver) <- $frames_roots(S_handler.FRAMES)',
        '$task_nodes(perrorcall.RESUME) = eps',
        'S_handler_global = $global_table_view(S_handler)',
        '$lookup(S_handler_global.ENV,$ptascii("receiver237")) = (n_receiver_slot)',
        'S_handler_global.STORE[n_receiver_slot] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_handler),HOBJECT n_receiver) = 1',
        'S_saved = $constant_frame_scope(S_handler,pframe_reader,pframe_tail*)',
        '$class_constant_this_selector(S_saved,porigin_site,' + child + ')',
        '$class_constant_notice_valid(S_saved,porigin_decl,' + child + ',$ptascii("TREE"),z)',
        'S_resume = $ccn_pause(S_handler,1,30000)', '$ccn_ready(S_resume,1)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*', 'S_resume.CURRENT = (pcallcontext)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|H|")',
        'S_resume_global = $global_table_view(S_resume)',
        'S_resume_global.STORE[n_receiver_slot] = DEFINED PNULL',
        '(HOBJECT n_receiver) <- S_resume.ALLOCATIONS',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_receiver) = 1',
        '$class_constant_this_selector(S_resume,porigin_site,' + child + ')',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),z)',
        'S_resume.RESULT =/= KNOWN (PARRAY n_donor)',
        'S_resume.CLASSCONSTANTCACHE = eps',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one = $drive_steps(S_resume,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]', 'S_after.RESULT = KNOWN (PARRAY n_donor)',
        'S_after.CURRENT = (pcallcontext)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_after),HARRAY n_donor) = $($heap_owners($heap_graph(S_resume),HARRAY n_donor) + 1)',
        '~$class_constant_notice_protected(S_after,porigin_decl)',
        'S_after.CLASSCONSTANTCACHE = eps', 'S_after.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        'S_warm = $ccn_pause(S_after,0,30000)', '$ccn_ready(S_warm,0)',
        'S_warm.CURRENT = eps', 'S_warm.FRAMES = eps',
        '$ccn_output(S_warm.EVENTS) = $ptascii("B|H|D|O|1|MUT|7|")',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_warm),HOBJECT n_receiver) = 0',
        '~$class_constant_this_selector(S_warm,porigin_site,' + child + ')',
        'S_warm.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals_done = $global_table_view(S_done)',
        '$lookup(S_globals_done.ENV,$ptascii("result237")) = (n_result_slot)',
        '$lookup(S_globals_done.ENV,$ptascii("again237")) = (n_again_slot)',
        'S_globals_done.STORE[n_result_slot] = DEFINED (PARRAY n_copy)',
        'S_globals_done.STORE[n_again_slot] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTINIT = eps', 'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_after,30000) = S_done']
    return checks


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = fields(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, SOURCE.parent / 'cases.json', *modules, *(ROOT / path for path in (
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
