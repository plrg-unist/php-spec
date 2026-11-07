#!/usr/bin/env python3
"""Check shared attribute metadata with distinct interface constant identities."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_owned_review_protocol import EXTRA
from deprecated_interface_constant_read_review_protocol import EXTRA as NOTICE
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_multi_constant_group_review'
SELECTIONS = {'siblings': SOURCE / 'interface-siblings.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def siblings(fixture, path):
    expected = json.loads((SOURCE / 'cases.json').read_text())[path.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_first = $interface_notice_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_first*',
        'perrorcall_first.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_first ptbytes_requested_first ptbytes_member_first 16',
        'ptbytes_member_first = $ptascii("FIRST")',
        '$class_constant_origin(S_first.CLASSES,porigin_first) = (pclassconstantdesc_first)',
        '$class_constant_lookup(S_first,pclassconstantdesc_first.OWNER,$ptascii("SECOND"),|S_first.CLASSES|) = (pclassconstantdesc_second)',
        'pclassconstantdesc_first.OWNER = pclassconstantdesc_second.OWNER',
        'pclassconstantdesc_first.ORIGIN =/= pclassconstantdesc_second.ORIGIN',
        'pclassconstantdesc_first.OWNER = PORIGIN n_unit pcpath_owner',
        'pclassconstantdesc_first.ORIGIN = PORIGIN n_unit (pcpath_owner ++ [PCFIELD 3,PCINDEX 0,PCFIELD 3,PCINDEX 0])',
        'pclassconstantdesc_second.ORIGIN = PORIGIN n_unit (pcpath_owner ++ [PCFIELD 3,PCINDEX 0,PCFIELD 3,PCINDEX 1])',
        'pclassconstantdesc_first.FOLDED', '~pclassconstantdesc_second.FOLDED',
        'pclassconstantdesc_first.LINE = 6', 'pclassconstantdesc_second.LINE = 6',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_first) =/= eps',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_second) = $class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_first)',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_second[.ORIGIN = pclassconstantdesc_first.ORIGIN]) = eps',
        '$class_constant_deprecated(S_first,pclassconstantdesc_first)',
        '$class_constant_deprecated(S_first,pclassconstantdesc_second)',
        '~$class_constant_inline_allowed(S_first.SOURCES,pclassconstantdesc_first)',
        '~$class_constant_inline_allowed(S_first.SOURCES,pclassconstantdesc_second)',
        '$class_constant_notice_protected(S_first,pclassconstantdesc_first.ORIGIN)',
        '~$class_constant_notice_protected(S_first,pclassconstantdesc_second.ORIGIN)',
        '$default_cache_at(S_first.CLASSCONSTANTCACHE,pclassconstantdesc_second.ORIGIN) = eps',
        '$error_call_valid(S_first,perrorcall_first)',
        '$call_descriptors_valid(S_first)',
        'S_first_resume = $interface_notice_review_pause(S_first,1,30000)',
        'S_first_value_raw = $drive_steps(S_first_resume,1)',
        'S_first_value_raw.COMPLETION = BUDGET',
        'S_first_value = S_first_value_raw[.COMPLETION = NORMAL]',
        'S_first_value.RESULT = KNOWN (PINT 7)',
        '~$class_constant_notice_protected(S_first_value,pclassconstantdesc_first.ORIGIN)',
        'S_second = $interface_notice_review_pause(S_first_value,0,30000)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_second.ORIGIN ptbytes_requested_second ptbytes_member_second 17',
        'ptbytes_member_second = $ptascii("SECOND")',
        '$class_constant_notice_protected(S_second,pclassconstantdesc_second.ORIGIN)',
        '~$class_constant_notice_protected(S_second,pclassconstantdesc_first.ORIGIN)',
        '$owned_class_constant_source(S_second,pclassconstantdesc_second)',
        '~$owned_class_constant_source(S_second,pclassconstantdesc_second[.INITIALIZER = pclassconstantdesc_first.INITIALIZER])',
        '$error_call_valid(S_second,perrorcall_second)',
        '~$class_constant_notice_valid(S_second,pclassconstantdesc_first.ORIGIN,ptbytes_requested_second,ptbytes_member_second,17)',
        'S_second_resume = $interface_notice_review_pause(S_second,1,30000)',
        'S_entered_raw = $drive_steps(S_second_resume,1)', 'S_entered_raw.COMPLETION = BUDGET',
        'S_bind = $class_owned_pause(S_entered_raw[.COMPLETION = NORMAL],0,pclassconstantdesc_second.ORIGIN,30000)',
        '$class_owned_ready(S_bind,0,pclassconstantdesc_second.ORIGIN)',
        'S_bind.RESULT = KNOWN (PARRAY n_donor)',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.DECL = pclassconstantdesc_second.ORIGIN',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$constant_fact_at(pconstantcontext.FACTS,pclassconstantdesc_second.INITIALIZER) = (pconstantfact)',
        '$global_constant_lookup_valid(S_bind,pclassconstantdesc_second.ORIGIN,pconstantfact,S_bind.USERCONSTANTS)',
        '$class_constant_context_valid(S_bind,pconstantcontext)',
        '$call_descriptors_valid(S_bind)',
        'S_bound_raw = $drive_steps(S_bind,1)', 'S_bound_raw.COMPLETION = BUDGET',
        'S_bound = S_bound_raw[.COMPLETION = NORMAL]',
        'S_bound.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,pclassconstantdesc_second.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_donor',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,pclassconstantdesc_first.ORIGIN) = eps',
        '$class_constant_roots(S_bound.CLASSCONSTANTCACHE) = [HARRAY n_donor]',
        '$class_constant_row_payload_valid(S_bound,pclassconstantdesc_second,pdefaultcache)',
        'S_zero = $drive_steps(S_bound,0)', 'S_zero.COMPLETION = BUDGET',
        'S_one = $drive_steps(S_bound,1)', 'S_one.COMPLETION = BUDGET',
        'S_warm = $interface_notice_review_pause(S_bound,0,30000)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_second.ORIGIN ptbytes_requested_warm ptbytes_member_second 20',
        '$default_cache_at(S_warm.CLASSCONSTANTCACHE,pclassconstantdesc_second.ORIGIN) = (pdefaultcache)',
        '$class_constant_notice_protected(S_warm,pclassconstantdesc_second.ORIGIN)',
        '~$class_constant_notice_protected(S_warm,pclassconstantdesc_first.ORIGIN)',
        '$class_constant_row_payload_valid(S_warm,pclassconstantdesc_second,pdefaultcache)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + quoted(expected),
        '|S_done.CLASSCONSTANTCACHE| = 1',
        '$class_constant_history_valid(S_done)',
        '$class_constant_caches_valid(S_done,S_done.CLASSCONSTANTCACHE)',
        '$lookup(S_done.ENV,$ptascii("first")) = (n_first)',
        '$lookup(S_done.ENV,$ptascii("second")) = (n_second)',
        'S_done.STORE[n_first] = DEFINED (PARRAY n_copy)',
        'S_done.STORE[n_second] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)',
        '$call_descriptors_valid(S_done)']


def prepare(out, group):
    path = SELECTIONS[group]
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = globals()[group](checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + NOTICE + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_owned_review_protocol.py',
        'tests/semantics/deprecated_interface_constant_read_review_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules),
        'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
