#!/usr/bin/env python3
"""Check protected constant visibility and owning cache authority."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_nonpublic_constant_review'
SELECTIONS = {'protected': SOURCE / 'protected-access.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

ACCESS = r'''
dec $nonpublic_access_ready(pstate,int) : bool
def $nonpublic_access_ready(S,z) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CLASS_CONST_CLASS name (NIdentifier (BYTES text) metadata_member) z) :: ptask_tail*
  -- if $base64(text) = $ptascii("C")
def $nonpublic_access_ready(S,z) = false -- otherwise
dec $nonpublic_access_pause(pstate,int,nat) : pstate
def $nonpublic_access_pause(S,z,n) = S -- if $nonpublic_access_ready(S,z)
def $nonpublic_access_pause(S,z,n) = $nonpublic_access_pause(S_next[.COMPLETION = NORMAL],z,$nabs($(n - 1)))
  -- if ~$nonpublic_access_ready(S,z)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $nonpublic_access_pause(S,z,n) = S -- otherwise
'''


def protected(fixture, path):
    expected = json.loads((SOURCE / 'cases.json').read_text())[path.stem]['stdout']
    message = expected.split('|')[1]
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_cold = $nonpublic_access_pause(S_start[.COMPLETION = NORMAL],21,30000)',
        '$nonpublic_access_ready(S_cold,21)',
        'S_cold.ORIGIN = (porigin_cold)',
        '$class_named(S_cold.CLASSNAMES,$ptlc(' + quoted('Ns219Protected' + chr(92) + 'Base219') + ')) = (porigin_base)',
        '$class_at(S_cold.CLASSES,porigin_base) = (pclassdesc_base)',
        '$class_constant_lookup(S_cold,porigin_base,$ptascii("C"),|S_cold.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.VISIBILITY = PROPERTY_PROTECTED', '~pclassconstantdesc.FOLDED',
        '$class_constant_lookup(S_cold,porigin_base,$ptascii("OPEN"),|S_cold.CLASSES|) = (pclassconstantdesc_public)',
        'pclassconstantdesc_public.VISIBILITY = PROPERTY_PUBLIC',
        '$class_constant_deprecated(S_cold,pclassconstantdesc)',
        '$class_constant_deprecated(S_cold,pclassconstantdesc_public)',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PROTECTED])',
        '$class_constant_attribute_group(S_cold.SOURCES,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC]) =/= eps',
        '~$class_constant_inline_allowed(S_cold.SOURCES,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_query_readable(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '$owned_class_constant_source(S_cold,pclassconstantdesc)',
        '~$class_constant_visible(S_cold,pclassconstantdesc)',
        '~$class_constant_notice_valid(S_cold,pclassconstantdesc.ORIGIN,pclassdesc_base.NAME,$ptascii("C"),21)',
        '~$call_task_valid(S_cold,DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc_base.NAME $ptascii("C") 21)',
        '$default_cache_at(S_cold.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = eps',
        '~$class_constant_notice_protected(S_cold,pclassconstantdesc.ORIGIN)',
        '$interface_notice_review_output(S_cold.EVENTS) = eps',
        'PhpStep: S_cold ~> S_denied',
        'S_denied.COMPLETION = THROWN "Error" ' + quoted(message) + ' 21',
        'S_denied.CLASSCONSTANTCACHE = S_cold.CLASSCONSTANTCACHE',
        'S_denied.CLASSCONSTANTHISTORY = S_cold.CLASSCONSTANTHISTORY',
        'S_denied.CLASSCONSTANTINIT = eps', 'S_denied.EVENTS = S_cold.EVENTS',
        'S_warn = $interface_notice_review_pause(S_cold,0,30000)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc_base.NAME ptbytes_member 12',
        'ptbytes_member = $ptascii("C")', 'S_warn.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (porigin_child)', 'porigin_child =/= porigin_base',
        'pcallcontext.CALLED_CLASS = (porigin_child)', 'pcallcontext.RECEIVER = eps',
        '$class_link_at(S_warn.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_base)',
        '$class_constant_visible(S_warn,pclassconstantdesc)',
        '$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,pclassdesc_base.NAME,ptbytes_member,12)',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = eps',
        '$interface_notice_review_output(S_warn.EVENTS) = ' + quoted('C|' + message + '|'),
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        'S_resume = $interface_notice_review_pause(S_warn,1,30000)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc_base.NAME ptbytes_member 12) :: ptask_tail*',
        'S_entered_raw = $drive_steps(S_resume,1)', 'S_entered_raw.COMPLETION = BUDGET',
        'S_bind = $class_owned_pause(S_entered_raw[.COMPLETION = NORMAL],0,pclassconstantdesc.ORIGIN,30000)',
        '$class_owned_ready(S_bind,0,pclassconstantdesc.ORIGIN)',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$constant_fact_at(pconstantcontext.FACTS,pclassconstantdesc.INITIALIZER) = (pconstantfact)',
        '$global_constant_fact_lookup_valid(S_bind,pclassconstantdesc.ORIGIN,pconstantfact)',
        '$class_constant_context_valid(S_bind,pconstantcontext)',
        'S_bind.RESULT = KNOWN (PARRAY n_donor)', '$call_descriptors_valid(S_bind)',
        'S_bound_raw = $drive_steps(S_bind,1)', 'S_bound_raw.COMPLETION = BUDGET',
        'S_bound = S_bound_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_donor',
        '$class_constant_row_payload_valid(S_bound,pclassconstantdesc,pdefaultcache)',
        'S_zero = $drive_steps(S_bound,0)', 'S_zero.COMPLETION = BUDGET',
        'S_one = $drive_steps(S_bound,1)', 'S_one.COMPLETION = BUDGET',
        'S_warm = $nonpublic_access_pause(S_bound,29,30000)',
        '$nonpublic_access_ready(S_warm,29)',
        '$default_cache_at(S_warm.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        '~$class_constant_visible(S_warm,pclassconstantdesc)',
        '~$class_constant_notice_valid(S_warm,pclassconstantdesc.ORIGIN,pclassdesc_base.NAME,ptbytes_member,29)',
        '~$call_task_valid(S_warm,DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc_base.NAME ptbytes_member 29)',
        '~$class_constant_notice_protected(S_warm,pclassconstantdesc.ORIGIN)',
        'PhpStep: S_warm ~> S_denied_warm',
        'S_denied_warm.COMPLETION = THROWN "Error" ' + quoted(message) + ' 29',
        'S_denied_warm.CLASSCONSTANTCACHE = S_warm.CLASSCONSTANTCACHE',
        'S_denied_warm.EVENTS = S_warm.EVENTS',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + quoted(expected),
        '|S_done.CLASSCONSTANTCACHE| = 1', '$class_constant_state_valid(S_done)',
        '$call_descriptors_valid(S_done)',
        '$lookup(S_done.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_done.ENV,$ptascii("again")) = (n_again)',
        'S_done.STORE[n_value] = DEFINED (PARRAY n_copy)',
        'S_done.STORE[n_again] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


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
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + NOTICE + ACCESS + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
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
