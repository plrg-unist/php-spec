#!/usr/bin/env python3
"""Check retained reference class selectors, cell retirement and interface array COW."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_reference_selector_notice_review/retired-interface-cow.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $reference_selector_ready(pstate) : bool
def $reference_selector_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier phpType33 metadata) z) :: ptask*
  -- if S.RESULT = REFERENCE n
def $reference_selector_ready(S) = false -- otherwise
dec $reference_selector_pause(pstate,nat) : pstate
def $reference_selector_pause(S,n) = S -- if $reference_selector_ready(S)
def $reference_selector_pause(S,n) = $reference_selector_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$reference_selector_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_selector_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    interface = quoted('Ns240Ref\\I240'); base = quoted('Ns240Ref\\Base240')
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw1 = $reference_selector_pause(S_start[.COMPLETION = NORMAL],30000)', '$reference_selector_ready(S_raw1)']
    for i, target, prefix in [(1, interface, 'B|C|'), (2, base, 'B|C|H|R|1|MUT|7|C|')]:
        raw = 'S_raw' + str(i); norm = 'S_class' + str(i); warn = 'S_warn' + str(i)
        resume = 'S_resume' + str(i); value = 'S_value' + str(i); n = 'n_ref' + str(i)
        site = 'porigin_site' + str(i); desc = 'pclassconstantdesc_' + str(i); line = 'z_' + str(i)
        if i == 2:
            checks += [raw + ' = $reference_selector_pause(S_value1,30000)', '$reference_selector_ready(' + raw + ')']
        checks += [raw + '.TODO = (CLASS_CONST_CLASS expression_class' + str(i) + ' (NIdentifier phpType33_' + str(i) + ' metadata_member' + str(i) + ') ' + line + ') :: ptask_tail' + str(i) + '*',
            raw + '.RESULT = REFERENCE ' + n, '$call_reference_operand_valid(' + raw + ',REFERENCE ' + n + ')',
            n + ' <- ' + raw + '.REFCELLS', '(HCELL ' + n + ') <- ' + raw + '.ALLOCATIONS',
            raw + '.STORE[' + n + '] = DEFINED pvalue_payload' + str(i),
            '$constant_value_class_valid(' + raw + ',pvalue_payload' + str(i) + ',PVSTRING false)',
            '$value_nodes(pvalue_payload' + str(i) + ') = eps',
            '$heap_owners($heap_graph(' + raw + '),HCELL ' + n + ') = 2',
            '$ccn_output(' + raw + '.EVENTS) = ' + quoted(prefix),
            raw + '.ORIGIN = (' + site + ')',
            norm + ' = $class_constant_selector(' + raw + ',expression_class' + str(i) + ',' + line + ')',
            norm + '.COMPLETION = NORMAL', norm + '.RESULT = KNOWN (PSTRING ' + target + ')',
            '$heap_owners($heap_graph(' + norm + '),HCELL ' + n + ') = 1',
            '$class_constant_reference_selector(' + norm + ',REFERENCE ' + n + ') = (pclassdesc_' + str(i) + ')',
            'pclassdesc_' + str(i) + '.NAME = ' + target,
            '$class_constant_reference_selector(' + norm + ',KNOWN pvalue_payload' + str(i) + ') = eps',
            '$class_constant_reference_selector(' + norm + '[.REFCELLS = eps],REFERENCE ' + n + ') = eps',
            '$class_constant_reference_selector(' + norm + '[.ALLOCATIONS = eps],REFERENCE ' + n + ') = eps',
            '$class_constant_rvalue_class_entry(' + norm + ',REFERENCE ' + n + ',expression_class' + str(i) + ',NIdentifier phpType33_' + str(i) + ' metadata_member' + str(i) + ',' + line + ',ptask_tail' + str(i) + '*) = eps',
            'S_step' + str(i) + ' = $drive_steps(' + raw + ',1)', 'S_step' + str(i) + '.COMPLETION = BUDGET',
            warn + ' = S_step' + str(i) + '[.COMPLETION = NORMAL]', '$ccn_ready(' + warn + ',0)',
            warn + '.TODO = (ERROR_HANDLER_INVOKE perrorcall_' + str(i) + ') :: ptask_warn' + str(i) + '*',
            'perrorcall_' + str(i) + '.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl' + str(i) + ' ' + target + ' $ptascii("TREE") ' + line,
            '$class_constant_origin(' + warn + '.CLASSES,porigin_decl' + str(i) + ') = (' + desc + ')',
            desc + '.FOLDED', '$compiled_read(' + warn + ',' + desc + '.INITIALIZER) = (PARRAY n_donor' + str(i) + ')',
            '$task_nodes(perrorcall_' + str(i) + '.RESUME) = eps',
            '$heap_owners($heap_graph(' + warn + '),HCELL ' + n + ') = 1',
            '$error_call_valid(' + warn + ',perrorcall_' + str(i) + ')', '$call_descriptors_valid(' + warn + ')',
            resume + ' = $ccn_pause(' + warn + ',1,30000)', '$ccn_ready(' + resume + ',1)',
            resume + '.ORIGIN = (' + site + ')', resume + '.CURRENT = eps', resume + '.FRAMES = eps',
            'S_global' + str(i) + ' = $global_table_view(' + resume + ')',
            '$lookup(S_global' + str(i) + '.ENV,$ptascii("selector240")) = eps',
            '~((HCELL ' + n + ') <- ' + resume + '.ALLOCATIONS)', n + ' <- ' + resume + '.REFCELLS',
            '~$call_reference_operand_valid(' + resume + ',REFERENCE ' + n + ')',
            'S_dead' + str(i) + ' = ' + resume + '[.STORE[' + n + '] = DEFINED pvalue_payload' + str(i) + '][.RESULT = KNOWN (PSTRING ' + target + ')]',
            '$class_constant_reference_selector(S_dead' + str(i) + ',REFERENCE ' + n + ') = eps',
            '$class_constant_notice_valid(' + resume + ',porigin_decl' + str(i) + ',' + target + ',$ptascii("TREE"),' + line + ')',
            '$class_constant_notice_valid(' + resume + '[.RESULT = KNOWN PNULL],porigin_decl' + str(i) + ',' + target + ',$ptascii("TREE"),' + line + ')',
            'S_value_step' + str(i) + ' = $drive_steps(' + resume + ',1)', 'S_value_step' + str(i) + '.COMPLETION = BUDGET',
            value + ' = S_value_step' + str(i) + '[.COMPLETION = NORMAL]', value + '.RESULT = KNOWN (PARRAY n_donor' + str(i) + ')',
            '$heap_owners($heap_graph(' + value + '),HARRAY n_donor' + str(i) + ') = $($heap_owners($heap_graph(' + resume + '),HARRAY n_donor' + str(i) + ') + 1)',
            '~$class_constant_notice_protected(' + value + ',porigin_decl' + str(i) + ')']
        if i == 1:
            checks += ['$string_bytes(pvalue_payload1) = (' + quoted('\\nS240rEf\\I240') + ')',
                'S_value1.ARRAYS[n_donor1].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]']
        else:
            checks += ['n_ref1 =/= n_ref2', '~((HCELL n_ref1) <- S_raw2.ALLOCATIONS)',
                '$lookup(S_raw2.ENV,$ptascii("first240")) = (n_first)',
                'S_raw2.STORE[n_first] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_donor1',
                'S_raw2.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
                'S_raw2.ARRAYS[n_donor1].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
                'S_value2.ARRAYS[n_donor2].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]']
    checks += ['S_done = $drive(S_value2,30000)', 'S_done.COMPLETION = NORMAL', '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals_done = $global_table_view(S_done)', '$lookup(S_globals_done.ENV,$ptascii("pool240")) = (n_pool)',
        'S_globals_done.STORE[n_pool] = DEFINED (PARRAY n_donor1)',
        'S_done.ARRAYS[n_donor1].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw1.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_raw1,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_raw1',
        'S_one = $drive_steps(S_raw1,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
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
