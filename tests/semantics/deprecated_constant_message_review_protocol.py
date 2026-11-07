#!/usr/bin/env python3
"""Check interface declaration context, nullable fields and OP/API notice parity."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from deprecated_class_constant_api_protocol import SELECTED as API_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_constant_message_review/interface-messages.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def interface(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    owner = 'Ns220Interface\\Base220'
    since = 'Constant ' + owner + '::SINCE_ONLY is deprecated since 8.5'
    quiet = 'Constant ' + owner + '::QUIET is deprecated'
    other = 'Constant ' + owner + '::OTHER is deprecated'
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 20',
        'ptbytes_class = ' + quoted(owner), 'ptbytes_member = $ptascii("SINCE_ONLY")',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)',
        'pclassdesc.KIND = "interface"', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.LINE = 6',
        'pclassdesc.CONSTANTS = [pclassconstantdesc,pclassconstantdesc_quiet,pclassconstantdesc_other]',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc) = DEPRECATED_ATTRIBUTE eps $ptascii("8.5")',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc_quiet) = DEPRECATED_ATTRIBUTE eps eps',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc_other) = DEPRECATED_ATTRIBUTE eps eps',
        '$class_constant_deprecated(S_warn,pclassconstantdesc)',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE]) = NO_DEPRECATED',
        'pclassconstantdesc.OWNER = PORIGIN n_unit pcpath_owner',
        '$source_unit(S_warn.SOURCES,n_unit) = (pcunit)', '$code_at(S_warn.CODE,n_unit) = (pcode)',
        '$plclasscontext(pcunit,pcpath_owner,$call_sourcefile(S_warn.FILES,pclassconstantdesc.OWNER),pclassdesc.LINE) = (ptcontext_source)',
        'ptcontext_source.NAMESPACE = $ptascii("Ns220Interface")',
        'ptcontext_source.FILE = ' + quoted(str(SOURCE)), 'ptcontext_source.SCOPE = PTGLOBAL',
        '$ptresolve(ptcontext_source,PTPLAIN,$ptascii("Mark")) = $ptascii("Deprecated")',
        'perrorcall.SITE = PORIGIN n_unit pcpath_site',
        '$plclasscontext(pcunit,pcpath_site,ptcontext_source.FILE,20) = (ptcontext_reader)',
        'ptcontext_reader.NAMESPACE = $ptascii("Ns220Reader")', 'ptcontext_reader.IMPORTS = eps',
        '$ptresolve(ptcontext_reader,PTPLAIN,$ptascii("Mark")) = ' + quoted('Ns220Reader\\Mark'),
        '$class_constant_attribute_group(S_warn.SOURCES,pclassconstantdesc) = ((PORIGIN n_unit pcpath_group,phpType15*))',
        'pcpath_null = pcpath_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]',
        'pcpath_since = pcpath_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]',
        '$ppconstant_metadata_root(pcunit,pcpath_null)', '$ppconstant_metadata_root(pcunit,pcpath_since)',
        '$pool_value(S_warn.POOLS,PORIGIN n_unit pcpath_null) = (PNULL)',
        '$pool_class(S_warn.POOLS,PORIGIN n_unit pcpath_null) = (PVSCALAR)',
        '$pool_value(S_warn.POOLS,PORIGIN n_unit pcpath_since) = (PSTRING $ptascii("8.5"))',
        '$pool_class(S_warn.POOLS,PORIGIN n_unit pcpath_since) = (PVSTRING false)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_null) = eps',
        '$code_expression(pcode.EXPRESSIONS,pcpath_since) = eps',
        'pclassconstantdesc.INITIALIZER = PORIGIN n_unit pcpath_initializer',
        '~$ppconstant_metadata_root(pcunit,pcpath_initializer)',
        '~$ppconstant_metadata_root(pcunit,pcpath_null ++ [PCFIELD 0])',
        '$class_constant_notice_text(S_warn,pclassconstantdesc,ptbytes_member) = ' + quoted(since),
        'perrorcall.MESSAGE = ' + quoted(since), 'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 20',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = ' + quoted(since + ', ') + '])',
        '$task_nodes(perrorcall.RESUME) = eps', 'S_warn.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$call_task_valid(S_resume,perrorcall.RESUME)',
        'S_value_raw = $drive_steps(S_resume,1)', 'S_value_raw.COMPLETION = BUDGET',
        'S_value = S_value_raw[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 7)',
        '~$class_constant_notice_protected(S_value,porigin_decl)',
        'S_api = $api_pause(S_value,0,30000)', '$api_ready(S_api,0)',
        'S_api.TODO = (ERROR_HANDLER_INVOKE perrorcall_api) :: ptask_api*',
        'perrorcall_api.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        '$dynamic_defined_query(pconfigcall) = ((' + quoted('Ns220Interface\\Child220') + ',ptbytes_member))',
        '$class_constant_api_selection(S_api,pconfigcall) = (pclassconstantdesc)',
        'perrorcall_api.LINE = 21', 'perrorcall_api.MESSAGE = perrorcall.MESSAGE',
        '$error_call_valid(S_api,perrorcall_api)', '$call_descriptors_valid(S_api)',
        '~$error_call_valid(S_api,perrorcall_api[.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)])',
        '$config_nodes(pconfigcall) = eps', '$task_nodes(perrorcall_api.RESUME) = eps',
        'S_api_notice = $api_pause(S_api,1,30000)', '$api_ready(S_api_notice,1)',
        '$class_constant_notice_protected(S_api_notice,porigin_decl)',
        'S_zero = $drive_steps(S_api_notice,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_api_notice',
        'S_one_raw = $drive_steps(S_api_notice,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PINT 7)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_one.CLASSCONSTANTINIT = eps', 'S_one.CLASSCONSTANTCACHE = eps',
        'S_quiet = $ccn_pause(S_one,0,30000)', '$ccn_ready(S_quiet,0)',
        'S_quiet.TODO = (ERROR_HANDLER_INVOKE perrorcall_quiet) :: ptask_quiet*',
        'perrorcall_quiet.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_quiet.ORIGIN ptbytes_quiet_class $ptascii("QUIET") 22',
        'ptbytes_quiet_class = ' + quoted('Ns220Interface\\Implementer220'),
        'perrorcall_quiet.MESSAGE = ' + quoted(quiet),
        '$class_constant_notice_text(S_quiet,pclassconstantdesc_quiet,$ptascii("QUIET")) = $class_constant_notice_message(pclassconstantdesc_quiet,$ptascii("QUIET"))',
        '$error_call_valid(S_quiet,perrorcall_quiet)',
        '$class_constant_attribute_group(S_quiet.SOURCES,pclassconstantdesc_quiet) = ((PORIGIN n_unit pcpath_quiet_group,phpType15_quiet*))',
        '$class_constant_attribute_group(S_quiet.SOURCES,pclassconstantdesc_other) = ((PORIGIN n_unit pcpath_quiet_group,phpType15_quiet*))',
        'pclassconstantdesc_quiet.ORIGIN =/= pclassconstantdesc_other.ORIGIN',
        'pcpath_empty = pcpath_quiet_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]',
        '$ppconstant_metadata_root(pcunit,pcpath_empty)',
        '$pool_value(S_quiet.POOLS,PORIGIN n_unit pcpath_empty) = (PSTRING eps)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_empty) = eps',
        'S_quiet_api = $api_pause(S_quiet,0,30000)', '$api_ready(S_quiet_api,0)',
        'S_quiet_api.TODO = (ERROR_HANDLER_INVOKE perrorcall_quiet_api) :: ptask_quiet_api*',
        'perrorcall_quiet_api.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_quiet pclassconstantdesc_quiet.ORIGIN false',
        'perrorcall_quiet_api.MESSAGE = perrorcall_quiet.MESSAGE',
        '$error_call_valid(S_quiet_api,perrorcall_quiet_api)',
        'S_other = $ccn_pause(S_quiet_api,0,30000)', '$ccn_ready(S_other,0)',
        'S_other.TODO = (ERROR_HANDLER_INVOKE perrorcall_other) :: ptask_other*',
        'perrorcall_other.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_other.ORIGIN ptbytes_other_class $ptascii("OTHER") 24',
        'ptbytes_other_class = ' + quoted('Ns220Interface\\Child220'),
        'perrorcall_other.MESSAGE = ' + quoted(other), '$error_call_valid(S_other,perrorcall_other)',
        'S_other_api = $api_pause(S_other,0,30000)', '$api_ready(S_other_api,0)',
        'S_other_api.TODO = (ERROR_HANDLER_INVOKE perrorcall_other_api) :: ptask_other_api*',
        'perrorcall_other_api.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_other pclassconstantdesc_other.ORIGIN false',
        'perrorcall_other_api.MESSAGE = perrorcall_other.MESSAGE',
        '$error_call_valid(S_other_api,perrorcall_other_api)',
        'S_done = $drive(S_other_api,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        '$drive(S_api_notice,30000) = S_done',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one,30000) = S_done',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_quiet.ORIGIN)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_other.ORIGIN)',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)']


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = interface(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + FETCH_SELECTED + API_SELECTED
        + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, SOURCE.parent / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_class_constant_api_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
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
