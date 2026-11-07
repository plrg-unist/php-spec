#!/usr/bin/env python3
"""Check API notice diagnostics and captured-query cold acquisition."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_class_constant_api_review'
SELECTIONS = {'owner': SOURCE / 'owner-api-line.php',
              'query': SOURCE / 'query-cold-bind.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
data = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

EXTRA = r'''
dec $api_notice_review_ready(pstate,nat) : bool
def $api_notice_review_ready(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false
def $api_notice_review_ready(S,1) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false) :: ptask*
def $api_notice_review_ready(S,2) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin true) :: ptask*
def $api_notice_review_ready(S,n) = false -- otherwise
dec $api_notice_review_pause(pstate,nat,nat) : pstate
def $api_notice_review_pause(S,n_mode,n) = S -- if $api_notice_review_ready(S,n_mode)
def $api_notice_review_pause(S,n_mode,n) = $api_notice_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$api_notice_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $api_notice_review_pause(S,n_mode,n) = S -- otherwise
dec $api_notice_review_output_item(pevent) : ptbytes
def $api_notice_review_output_item(OUTPUT ptbytes) = ptbytes
def $api_notice_review_output_item(pevent) = eps -- otherwise
dec $api_notice_review_output(pevent*) : ptbytes
def $api_notice_review_output(eps) = eps
def $api_notice_review_output(pevent :: pevent_tail*) = $api_notice_review_output_item(pevent) ++ $api_notice_review_output(pevent_tail*)
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']


def expected(group):
    return data(json.loads((SOURCE / 'cases.json').read_text())[SELECTIONS[group].stem]['stdout'])


def owner(fixture, path):
    return start(fixture, path) + [
        'S_warn = $api_notice_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$api_notice_review_ready(S_warn,0)',
        '$api_notice_review_output(S_warn.EVENTS) = $ptascii("1|")',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        'pconfigcall.KIND = INTRINSIC_CONSTANT', 'pconfigcall.LINE = 21',
        'pconfigcall.OWNER = eps', 'pconfigcall.PACKS = eps',
        'pconfigcall.SITE = perrorcall.SITE', 'S_warn.ORIGIN = (pconfigcall.SITE)',
        '$dynamic_class_constant_valid(S_warn,pconfigcall)',
        '$dynamic_defined_query(pconfigcall) = (($ptascii("BaseAPI213"),$ptascii("VALUE")))',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 21',
        'perrorcall.MESSAGE = $ptascii("Constant BaseAPI213::VALUE is deprecated")',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE 21',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = $ptascii("BaseAPI213")',
        'pclassconstantdesc.LINE = 4', 'pclassconstantdesc.FOLDED',
        '$pool_class(S_warn.POOLS,pclassconstantdesc.INITIALIZER) = (PVSCALAR)',
        '$compiled_read(S_warn,pclassconstantdesc.INITIALIZER) = (PINT 7)',
        '~$class_constant_query_readable(S_warn,pclassconstantdesc)',
        'S_warn.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        'S_warn.RESULT =/= KNOWN (PINT 7)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        '$task_nodes(perrorcall.RESUME) = $config_nodes(pconfigcall)',
        '$error_call_valid(S_warn,perrorcall)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_warn,perrorcall[.LINE = 4])',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true])',
        '$call_descriptors_valid(S_warn)',
        'S_notice = $api_notice_review_pause(S_warn,1,30000)',
        '$api_notice_review_ready(S_notice,1)',
        'S_notice.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false) :: ptask_tail*',
        'S_notice.CLASSCONSTANTINIT = eps',
        '$call_task_valid(S_notice,DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false)',
        'S_child = $api_notice_review_pause(S_notice,0,30000)',
        '$api_notice_review_ready(S_child,0)',
        'S_child.TODO = (ERROR_HANDLER_INVOKE perrorcall_child) :: ptask_child*',
        'perrorcall_child.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_child porigin_decl false',
        'pconfigcall_child.LINE = 22',
        '$dynamic_defined_query(pconfigcall_child) = (($ptascii("ChildAPI213"),$ptascii("VALUE")))',
        'perrorcall_child.MESSAGE = perrorcall.MESSAGE', '$error_call_valid(S_child,perrorcall_child)',
        'S_interface = $api_notice_review_pause($api_notice_review_pause(S_child,1,30000),0,30000)',
        '$api_notice_review_ready(S_interface,0)',
        'S_interface.TODO = (ERROR_HANDLER_INVOKE perrorcall_interface) :: ptask_interface*',
        'perrorcall_interface.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_interface porigin_interface_decl false',
        'pconfigcall_interface.LINE = 23',
        'perrorcall_interface.MESSAGE = $ptascii("Constant InterfaceAPI213::VALUE is deprecated")',
        '$class_constant_origin(S_interface.CLASSES,porigin_interface_decl) = (pclassconstantdesc_interface)',
        '$class_at(S_interface.CLASSES,pclassconstantdesc_interface.OWNER) = (pclassdesc_interface)',
        'pclassdesc_interface.KIND = "interface"',
        'porigin_interface_decl =/= porigin_decl',
        '$error_call_valid(S_interface,perrorcall_interface)',
        '~$class_constant_query_readable(S_interface,pclassconstantdesc_interface)',
        'S_derived = $api_notice_review_pause($api_notice_review_pause(S_interface,1,30000),0,30000)',
        '$api_notice_review_ready(S_derived,0)',
        'S_derived.TODO = (ERROR_HANDLER_INVOKE perrorcall_derived) :: ptask_derived*',
        'perrorcall_derived.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_derived porigin_interface_decl false',
        'pconfigcall_derived.LINE = 24',
        'perrorcall_derived.MESSAGE = perrorcall_interface.MESSAGE',
        'S_implementer = $api_notice_review_pause($api_notice_review_pause(S_derived,1,30000),0,30000)',
        '$api_notice_review_ready(S_implementer,0)',
        'S_implementer.TODO = (ERROR_HANDLER_INVOKE perrorcall_implementer) :: ptask_implementer*',
        'perrorcall_implementer.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_implementer porigin_interface_decl false',
        'pconfigcall_implementer.LINE = 25',
        'perrorcall_implementer.MESSAGE = perrorcall_interface.MESSAGE',
        '$error_call_valid(S_implementer,perrorcall_implementer)',
        'S_done = $drive(S_implementer,30000)', 'S_done.COMPLETION = NORMAL',
        '$api_notice_review_output(S_done.EVENTS) = ' + expected('owner'),
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '~$class_constant_notice_protected(S_done,porigin_interface_decl)',
        '$call_descriptors_valid(S_done)']


def query(fixture, path):
    return start(fixture, path) + [
        'S_warn = $api_notice_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$api_notice_review_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        'pconfigcall.LINE = 22',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING n_query) ptbytes_query))]',
        'ptbytes_query = $ptascii("AliasQueryAPI213::VALUE")',
        'pvalue_query = PSTRING_CARRIER (REQUEST_STRING n_query) ptbytes_query',
        '$string_carrier_valid(S_warn,pvalue_query)', '$value_nodes(pvalue_query) = eps',
        '$dynamic_class_constant_valid(S_warn,pconfigcall)',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = $ptascii("QueryAPI213")',
        '~pclassconstantdesc.FOLDED', 'pclassconstantdesc.TYPE = eps',
        '$dynamic_class_constant_global(S_warn,pclassconstantdesc) = ($ptascii("SEED_QUERY213"))',
        'S_warn.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        '$task_nodes(perrorcall.RESUME) = $config_nodes(pconfigcall)',
        '$config_nodes(pconfigcall) = eps', '$error_call_valid(S_warn,perrorcall)',
        'S_notice = $api_notice_review_pause(S_warn,1,30000)',
        '$api_notice_review_ready(S_notice,1)',
        'S_notice.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false) :: ptask_tail*',
        '$api_notice_review_output(S_notice.EVENTS) = $ptascii("H|W|")',
        'S_global = $global_table_view(S_notice)',
        '$lookup(S_global.ENV,$ptascii("query213")) = (n_rebound)',
        'S_global.STORE[n_rebound] = DEFINED pvalue_rebound',
        '$string_bytes(pvalue_rebound) = ($ptascii("OtherQueryAPI213::VALUE"))',
        'pvalue_rebound =/= pvalue_query', '$string_carrier_valid(S_notice,pvalue_query)',
        '$call_task_valid(S_notice,DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false)',
        'S_bind = $api_notice_review_pause(S_notice,2,30000)',
        '$api_notice_review_ready(S_bind,2)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_decl) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_tail*',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.SELECTION = CLASS_CONST_CALL pconfigcall',
        'pclassconstantcontext.DECL = porigin_decl',
        'pclassconstantcontext.ORIGIN = (pconfigcall.SITE)', 'pclassconstantcontext.LINE = 22',
        '~$class_constant_notice_protected(S_bind,porigin_decl)',
        '$task_nodes(DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) = $config_nodes(pconfigcall)',
        '$string_carrier_valid(S_bind,pvalue_query)',
        'S_restored = $class_constant_restore(S_bind,pclassconstantcontext,pclassconstantcontext_tail*)',
        '$class_constant_selection_valid(S_restored,pclassconstantcontext)',
        '$dynamic_class_constant_deferred(S_restored,pconfigcall) = eps',
        '~$class_constant_query_readable(S_restored,pclassconstantdesc)',
        '$call_descriptors_valid(S_bind)',
        'S_bound_raw = $drive_steps(S_bind,1)', 'S_bound_raw.COMPLETION = BUDGET',
        'S_bound = S_bound_raw[.COMPLETION = NORMAL]',
        'S_bound.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_tail*',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)',
        'pdefaultcache.VALUE = PINT 7',
        '$call_task_valid(S_bound,DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true)',
        '~$class_constant_notice_protected(S_bound,porigin_decl)',
        'S_zero = $drive_steps(S_bound,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S_bound.TODO',
        'S_one_raw = $drive_steps(S_bound,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PINT 7)',
        'S_one.TODO = ptask_tail*', 'S_one.STRINGDATA = S_bound.STRINGDATA',
        'S_warm = $api_notice_review_pause(S_one,0,30000)', '$api_notice_review_ready(S_warm,0)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_warm porigin_decl false',
        'pconfigcall_warm.LINE = 25', 'S_warm.CLASSCONSTANTINIT = eps',
        'S_warm.CLASSCONSTANTCACHE = S_bound.CLASSCONSTANTCACHE',
        '$api_notice_review_output(S_warm.EVENTS) = $ptascii("H|W|7|R|")',
        '$error_call_valid(S_warm,perrorcall_warm)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$api_notice_review_output(S_done.EVENTS) = ' + expected('query'),
        '$drive(S_zero,30000) = S_done', '$drive(S_one,30000) = S_done',
        '~$class_constant_notice_protected(S_done,porigin_decl)', '$call_descriptors_valid(S_done)']


def prepare(out, group):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        path = SELECTIONS[group]
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = globals()[group](checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
