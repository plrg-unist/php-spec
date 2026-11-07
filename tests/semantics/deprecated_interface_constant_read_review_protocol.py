#!/usr/bin/env python3
"""Check interface notice provenance and eval/default fences."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_interface_constant_read_review'
SELECTIONS = {'owner': [SOURCE / 'owner-fetch-line.php'],
    'formal': [SOURCE / 'eval-default-fold.php']}

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
data = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

EXTRA = r'''
dec $interface_notice_review_ready(pstate,nat) : bool
def $interface_notice_review_ready(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z
def $interface_notice_review_ready(S,1) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z) :: ptask*
def $interface_notice_review_ready(S,2) = true
  -- if $interface_notice_review_ready(S,0)
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("formal212")
def $interface_notice_review_ready(S,3) = true
  -- if $interface_notice_review_ready(S,1)
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("formal212")
def $interface_notice_review_ready(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("formal212")
  -- if S.TODO = (DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: eps
  -- if $receiving_function(S,pcallcontext.FUNCTION) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,0) = (pdefault)
  -- if $default_current_cache(S,pdefault.ORIGIN) =/= eps
def $interface_notice_review_ready(S,n) = false -- otherwise
dec $interface_notice_review_pause(pstate,nat,nat) : pstate
def $interface_notice_review_pause(S,n_mode,n) = S -- if $interface_notice_review_ready(S,n_mode)
def $interface_notice_review_pause(S,n_mode,n) = $interface_notice_review_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$interface_notice_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $interface_notice_review_pause(S,n_mode,n) = S -- otherwise
dec $interface_notice_review_output_item(pevent) : ptbytes
def $interface_notice_review_output_item(OUTPUT ptbytes) = ptbytes
def $interface_notice_review_output_item(pevent) = eps -- otherwise
dec $interface_notice_review_output(pevent*) : ptbytes
def $interface_notice_review_output(eps) = eps
def $interface_notice_review_output(pevent :: pevent_tail*) = $interface_notice_review_output_item(pevent) ++ $interface_notice_review_output(pevent_tail*)
'''


def start(fixture, path):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']


def expected(group):
    row = json.loads((SOURCE / 'cases.json').read_text())[SELECTIONS[group][0].stem]
    return data(row['stdout'])


def owner(fixture, path, responses):
    return start(fixture, path) + [
        'S_warn = $interface_notice_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$interface_notice_review_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z',
        'ptbytes_class = $ptascii("I212")', 'ptbytes_member = $ptascii("VALUE")', 'z = 15',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 15',
        'perrorcall.MESSAGE = $ptascii("Constant I212::VALUE is deprecated")',
        'S_warn.ORIGIN = (perrorcall.SITE)',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = $ptascii("I212")',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "interface"',
        'pclassconstantdesc.LINE = 4', 'pclassconstantdesc.FOLDED',
        '$compiled_read(S_warn,pclassconstantdesc.INITIALIZER) = (PINT 7)',
        '~$class_constant_inline_allowed(S_warn.SOURCES,pclassconstantdesc)',
        '$class_constant_compile_value(S_warn,pclassconstantdesc) = eps',
        '$compiled_read(S_warn,perrorcall.SITE) = eps',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CONSTCONTEXT = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_warn,perrorcall[.LINE = 4])',
        '$call_descriptors_valid(S_warn)',
        'S_resume = $interface_notice_review_pause(S_warn,1,30000)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z) :: ptask_tail*',
        '$call_task_valid(S_resume,DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,$ptascii("OTHER"),z)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,$ptascii("J212"),ptbytes_member,z)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,4)',
        'S_resume.CLASSCONSTANTINIT = eps', 'S_resume.RESULT =/= KNOWN (PINT 7)',
        '$call_descriptors_valid(S_resume)',
        'S_value_raw = $drive_steps(S_resume,1)', 'S_value_raw.COMPLETION = BUDGET',
        'S_value = S_value_raw[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 7)',
        '~$class_constant_notice_protected(S_value,porigin_decl)',
        'S_child = $interface_notice_review_pause(S_value,0,30000)',
        'S_child.TODO = (ERROR_HANDLER_INVOKE perrorcall_child) :: ptask_child*',
        'perrorcall_child.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class_child ptbytes_member 16',
        'ptbytes_class_child = $ptascii("J212")',
        'perrorcall_child.MESSAGE = perrorcall.MESSAGE', 'perrorcall_child.LINE = 16',
        '$class_constant_notice_protected(S_child,porigin_decl)',
        '$error_call_valid(S_child,perrorcall_child)',
        'S_child_resume = $interface_notice_review_pause(S_child,1,30000)',
        'S_child_value_raw = $drive_steps(S_child_resume,1)', 'S_child_value_raw.COMPLETION = BUDGET',
        'S_implementer = $interface_notice_review_pause(S_child_value_raw[.COMPLETION = NORMAL],0,30000)',
        'S_implementer.TODO = (ERROR_HANDLER_INVOKE perrorcall_implementer) :: ptask_implementer*',
        'perrorcall_implementer.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class_implementer ptbytes_member 17',
        'ptbytes_class_implementer = $ptascii("K212")',
        'perrorcall_implementer.MESSAGE = perrorcall.MESSAGE',
        '$class_named(S_implementer.CLASSNAMES,$ptlc(ptbytes_class_implementer)) = (porigin_implementer)',
        '$class_at(S_implementer.CLASSES,porigin_implementer) = (pclassdesc_implementer)',
        'pclassdesc_implementer.KIND = "class"', '$error_call_valid(S_implementer,perrorcall_implementer)',
        'S_done = $drive(S_implementer,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + expected('owner'),
        '~$class_constant_notice_protected(S_done,porigin_decl)', '$call_descriptors_valid(S_done)']


def formal(fixture, path, responses):
    return start(fixture, path) + [
        'S_request_one = $drive_steps(S_start[.COMPLETION = NORMAL],30000)',
        'S_request_one.COMPLETION = SOURCE_PENDING',
        '$eval_response_valid(S_request_one,' + responses[0] + ')',
        'S_entered_one = $eval_resume(S_request_one,' + responses[0] + ')',
        'S_request_two = $drive_steps(S_entered_one,30000)', 'S_request_two.COMPLETION = SOURCE_PENDING',
        '$interface_notice_review_output(S_request_two.EVENTS) = $ptascii("H|7|H|7|")',
        '$eval_response_valid(S_request_two,' + responses[1] + ')',
        'S_entered_two = $eval_resume(S_request_two,' + responses[1] + ')',
        'S_warn = $interface_notice_review_pause(S_entered_two,2,30000)',
        '$interface_notice_review_ready(S_warn,2)', 'S_warn.CURRENT = (pcallcontext)',
        '$receiving_function(S_warn,pcallcontext.FUNCTION) = (pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'pconstantcontext.ORIGIN = $default_parameter_origin(S_warn,pfunction.ORIGIN,pdefault.INDEX)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        '~pclassconstantdesc.FOLDED', 'porigin_decl =/= pdefault.ORIGIN',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_class)',
        'pdefaultcache_class.VALUE = PINT 7',
        '~$class_constant_inline_allowed(S_warn.SOURCES,pclassconstantdesc)',
        '$class_constant_compile_value(S_warn,pclassconstantdesc) = eps',
        '$default_current_cache(S_warn,pdefault.ORIGIN) = eps',
        'S_warn.CLASSCONSTANTINIT = eps', '$call_descriptors_valid(S_warn)',
        'S_resume = $interface_notice_review_pause(S_warn,3,30000)',
        '$interface_notice_review_ready(S_resume,3)',
        'S_resume.CONSTCONTEXT = S_warn.CONSTCONTEXT',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z) :: ptask_tail*',
        '$call_task_valid(S_resume,DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z)',
        '$task_nodes(DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z) = eps',
        '$call_descriptors_valid(S_resume)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PINT 7)',
        '$default_cache_at(S_one.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_class)',
        'S_warm = $interface_notice_review_pause(S_one,4,30000)',
        '$interface_notice_review_ready(S_warm,4)',
        '$default_current_cache(S_warm,pdefault.ORIGIN) = (pdefaultcache_formal)',
        'pdefaultcache_formal.VALUE = PINT 7',
        '~$class_constant_notice_protected(S_warm,porigin_decl)',
        '$interface_notice_review_output(S_warm.EVENTS) = $ptascii("H|7|H|7|H|7|")',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + expected('formal'),
        '$drive(S_one,30000) = S_done', '$drive(S_resume,30000) = S_done',
        '$call_descriptors_valid(S_done)']


def prepare(out, group):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    fixtures, responses = [], []
    try:
        for path in SELECTIONS[group]:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            fixtures.append(checked['fixture'])
        if group == 'formal':
            codes = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program']) if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith((b'echo K212::VALUE', b'function formal212('))]
            assert len(codes) == 2
            for index, code in enumerate(codes, 1):
                parsed_eval = frontend.request({'op': 'parse-eval', 'id': str(index), 'mode': 'eval', 'profile': 'cli-raw-85', 'source': base64.b64encode(code).decode()})
                assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
                checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True}); assert checked_eval['ok']
                responses.append('SOURCE_ACCEPT ' + str(index) + ' (' + data(code.decode()) + ') ' + checked_eval['fixture'])
                (out / ('eval' + str(index) + '.php')).write_bytes(code)
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = globals()[group](fixtures[0], SELECTIONS[group][0], responses)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
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
