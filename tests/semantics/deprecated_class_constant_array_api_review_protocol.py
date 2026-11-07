#!/usr/bin/env python3
"""Check empty/nested interface API array roots and COW aliases."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_class_constant_array_api_review'
CASE = SOURCE / 'interface-tree-cow.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

EXTRA = r'''
dec $array_api_review_ready(pstate,nat) : bool
def $array_api_review_ready(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false
def $array_api_review_ready(S,1) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false) :: ptask*
def $array_api_review_ready(S,n) = false -- otherwise
dec $array_api_review_pause(pstate,nat,nat) : pstate
def $array_api_review_pause(S,n_mode,n) = S -- if $array_api_review_ready(S,n_mode)
def $array_api_review_pause(S,n_mode,n) = $array_api_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$array_api_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $array_api_review_pause(S,n_mode,n) = S -- otherwise
dec $array_api_review_output_item(pevent) : ptbytes
def $array_api_review_output_item(OUTPUT ptbytes) = ptbytes
def $array_api_review_output_item(pevent) = eps -- otherwise
dec $array_api_review_output(pevent*) : ptbytes
def $array_api_review_output(eps) = eps
def $array_api_review_output(pevent :: pevent_tail*) = $array_api_review_output_item(pevent) ++ $array_api_review_output(pevent_tail*)
'''


def assertions(fixture):
    expected = json.loads((SOURCE / 'cases.json').read_text())[CASE.stem]['stdout'].encode()
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(CASE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_empty_warn = $array_api_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$array_api_review_ready(S_empty_warn,0)',
        'S_empty_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_empty) :: ptask_warn*',
        'perrorcall_empty.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_empty porigin_empty false',
        'pconfigcall_empty.LINE = 24',
        'perrorcall_empty.MESSAGE = $ptascii("Constant ArrayAPI214::EMPTY is deprecated")',
        '$class_constant_api_selection(S_empty_warn,pconfigcall_empty) = (pclassconstantdesc_empty)',
        'pclassconstantdesc_empty.ORIGIN = porigin_empty',
        'pclassconstantdesc_empty.OWNERNAME = $ptascii("ArrayAPI214")',
        '$class_at(S_empty_warn.CLASSES,pclassconstantdesc_empty.OWNER) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "interface"', 'pclassconstantdesc_empty.FOLDED',
        '$pool_class(S_empty_warn.POOLS,pclassconstantdesc_empty.INITIALIZER) = (PVARRAY true eps)',
        '$compiled_read(S_empty_warn,pclassconstantdesc_empty.INITIALIZER) = (PARRAY n_empty)',
        '$array_immutable(S_empty_warn,n_empty)', 'S_empty_warn.ARRAYS[n_empty].ITEMS = eps',
        '$class_constant_api_initializer(S_empty_warn,pclassconstantdesc_empty)',
        '~$class_constant_api_scalar(PVARRAY true eps)',
        '$dynamic_class_constant_array_tree(S_empty_warn,PARRAY n_empty,PVARRAY true eps)',
        '(HARRAY n_empty) <- $heap_graph(S_empty_warn).ROOTS',
        'S_empty_warn.RESULT = KNOWN PNULL', 'S_empty_warn.CLASSCONSTANTINIT = eps',
        '$task_nodes(perrorcall_empty.RESUME) = eps',
        '$class_constant_notice_protected(S_empty_warn,porigin_empty)',
        '~$class_constant_query_readable(S_empty_warn,pclassconstantdesc_empty)',
        '$error_call_valid(S_empty_warn,perrorcall_empty)',
        'S_empty_resume = $array_api_review_pause(S_empty_warn,1,30000)',
        '$array_api_review_ready(S_empty_resume,1)',
        'S_empty_resume.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_empty porigin_empty false) :: ptask_empty_tail*',
        '$array_api_review_output(S_empty_resume.EVENTS) = $ptascii("H|9|")',
        'S_empty_resume.ARRAYS[n_empty] = S_empty_warn.ARRAYS[n_empty]',
        '$heap_owners($heap_graph(S_empty_resume),HARRAY n_empty) = $heap_owners($heap_graph(S_empty_warn),HARRAY n_empty)',
        'S_empty_raw = $drive_steps(S_empty_resume,1)', 'S_empty_raw.COMPLETION = BUDGET',
        'S_empty = S_empty_raw[.COMPLETION = NORMAL]',
        'S_empty.RESULT = KNOWN (PARRAY n_empty)', 'S_empty.TODO = ptask_empty_tail*',
        'S_empty.ARRAYS = S_empty_resume.ARRAYS', 'S_empty.ALLOCATIONS = S_empty_resume.ALLOCATIONS',
        '$heap_owners($heap_graph(S_empty),HARRAY n_empty) = $($heap_owners($heap_graph(S_empty_resume),HARRAY n_empty) + 1)',
        '~$class_constant_notice_protected(S_empty,porigin_empty)',
        '$call_descriptors_valid(S_empty)', '$heap_valid($heap_graph(S_empty))',
        'S_empty_again = $array_api_review_pause(S_empty,0,30000)',
        '$array_api_review_ready(S_empty_again,0)',
        'S_empty_again.TODO = (ERROR_HANDLER_INVOKE perrorcall_empty_again) :: ptask_empty_again*',
        'perrorcall_empty_again.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_empty_again porigin_empty false',
        'pconfigcall_empty_again.LINE = 27',
        'S_tree_warn = $array_api_review_pause($array_api_review_pause(S_empty_again,1,30000),0,30000)',
        '$array_api_review_ready(S_tree_warn,0)',
        'S_tree_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_tree) :: ptask_tree_warn*',
        'perrorcall_tree.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_tree porigin_tree false',
        'pconfigcall_tree.LINE = 29', 'porigin_tree =/= porigin_empty',
        'perrorcall_tree.MESSAGE = $ptascii("Constant ArrayAPI214::TREE is deprecated")',
        '$class_constant_api_selection(S_tree_warn,pconfigcall_tree) = (pclassconstantdesc_tree)',
        'pclassconstantdesc_tree.ORIGIN = porigin_tree',
        'pclassconstantdesc_tree.OWNER = pclassconstantdesc_empty.OWNER',
        '$compiled_read(S_tree_warn,pclassconstantdesc_tree.INITIALIZER) = (PARRAY n_tree)',
        '$pool_class(S_tree_warn.POOLS,pclassconstantdesc_tree.INITIALIZER) = (PVARRAY false ([(KINT 0,PVARRAY true eps)]))',
        'S_tree_warn.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child))]',
        'S_tree_warn.ARRAYS[n_child].ITEMS = eps', '$array_immutable(S_tree_warn,n_child)',
        'S_tree_warn.RESULT = KNOWN PNULL',
        '$task_nodes(perrorcall_tree.RESUME) = eps',
        'S_tree_resume = $array_api_review_pause(S_tree_warn,1,30000)',
        '$array_api_review_ready(S_tree_resume,1)',
        'S_tree_resume.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_tree porigin_tree false) :: ptask_tree_tail*',
        'S_tree_resume.ARRAYS[n_tree] = S_tree_warn.ARRAYS[n_tree]',
        'S_tree_resume.ARRAYS[n_child] = S_tree_warn.ARRAYS[n_child]',
        '$heap_owners($heap_graph(S_tree_resume),HARRAY n_tree) = $heap_owners($heap_graph(S_tree_warn),HARRAY n_tree)',
        'parray_tree = S_tree_resume.ARRAYS[n_tree]',
        'S_bad = S_tree_resume[.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_tree porigin_tree true) :: ptask_tree_tail*][.ARRAYS = $array_replace(S_tree_resume.ARRAYS,n_tree,parray_tree[.NEXT = $(parray_tree.NEXT + 1)])]',
        'S_bad_value = $class_constant_api_value(S_bad,pconfigcall_tree,pclassconstantdesc_tree)',
        'S_bad_value.COMPLETION = UNSUPPORTED "Deprecated class constant API value"',
        'S_zero = $drive_steps(S_tree_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.TODO = S_tree_resume.TODO',
        'S_one = $drive_steps(S_tree_resume,1)', 'S_one.COMPLETION = BUDGET',
        'S_tree = S_one[.COMPLETION = NORMAL]',
        'S_tree.RESULT = KNOWN (PARRAY n_tree)', 'S_tree.TODO = ptask_tree_tail*',
        'S_tree.ARRAYS = S_tree_resume.ARRAYS', 'S_tree.ALLOCATIONS = S_tree_resume.ALLOCATIONS',
        'S_tree.EVENTS = S_tree_resume.EVENTS',
        '$heap_owners($heap_graph(S_tree),HARRAY n_tree) = $($heap_owners($heap_graph(S_tree_resume),HARRAY n_tree) + 1)',
        '~$class_constant_notice_protected(S_tree,porigin_tree)',
        '$call_descriptors_valid(S_tree)', '$heap_valid($heap_graph(S_tree))',
        'S_done = $drive(S_tree,30000)', 'S_done.COMPLETION = NORMAL',
        '$array_api_review_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(expected).decode()) + ')',
        '$lookup(S_done.ENV,$ptascii("empty")) = (n_empty_cell)',
        'S_done.STORE[n_empty_cell] = DEFINED (PARRAY n_empty_copy)', 'n_empty_copy =/= n_empty',
        'S_done.ARRAYS[n_empty_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '$lookup(S_done.ENV,$ptascii("again")) = (n_again_cell)',
        'S_done.STORE[n_again_cell] = DEFINED (PARRAY n_empty)',
        '$lookup(S_done.ENV,$ptascii("tree")) = (n_tree_cell)',
        'S_done.STORE[n_tree_cell] = DEFINED (PARRAY n_tree_copy)', 'n_tree_copy =/= n_tree',
        'S_done.ARRAYS[n_tree_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child_copy))]',
        'n_child_copy =/= n_child',
        'S_done.ARRAYS[n_child_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '$lookup(S_done.ENV,$ptascii("alias")) = (n_alias_cell)',
        'S_done.STORE[n_alias_cell] = DEFINED (PARRAY n_tree)',
        'S_done.ARRAYS[n_empty].ITEMS = eps',
        'S_done.ARRAYS[n_tree] = S_tree_resume.ARRAYS[n_tree]',
        'S_done.ARRAYS[n_child].ITEMS = eps',
        'S_done.CLASSCONSTANTCACHE = eps',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(CASE.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = assertions(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), CASE, SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
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


if __name__ == '__main__': main()
