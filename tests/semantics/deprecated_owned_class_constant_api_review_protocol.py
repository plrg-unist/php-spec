#!/usr/bin/env python3
"""Check direct-global owning API Closure publication and result handoff."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_owned_review_protocol import EXTRA
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_owned_class_constant_api_review'
SELECTIONS = {'closure': SOURCE / 'interface-closure.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = r'''
dec $interface_review_closure_ready(pstate,nat) : bool
def $interface_review_closure_ready(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
def $interface_review_closure_ready(S,n) = false -- otherwise
dec $interface_review_closure_pause(pstate,nat,nat) : pstate
def $interface_review_closure_pause(S,n_donor,n) = S -- if $interface_review_closure_ready(S,n_donor)
def $interface_review_closure_pause(S,n_donor,n) = $interface_review_closure_pause(S_next[.COMPLETION = NORMAL],n_donor,$nabs($(n - 1)))
  -- if ~$interface_review_closure_ready(S,n_donor)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $interface_review_closure_pause(S,n_donor,n) = S -- otherwise
dec $interface_review_output_item(pevent) : ptbytes
def $interface_review_output_item(OUTPUT ptbytes) = ptbytes
def $interface_review_output_item(pevent) = eps -- otherwise
dec $interface_review_output(pevent*) : ptbytes
def $interface_review_output(eps) = eps
def $interface_review_output(pevent :: pevent_tail*) = $interface_review_output_item(pevent) ++ $interface_review_output(pevent_tail*)
'''


def closure(fixture, path):
    expected = json.loads((SOURCE / 'cases.json').read_text())[path.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],30000)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.COPIED = eps', '$task_nodes(perrorcall.RESUME) = eps',
        '$interface_review_output(S_warn.EVENTS) = $ptascii("C|")',
        'S_warn.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.SELECTION = CLASS_CONST_CALL pconfigcall',
        'pclassconstantcontext.ORIGIN = (pconfigcall.SITE)', 'pconfigcall.LINE = 19',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'pconstantcontext.ORIGIN = pclassconstantcontext.DECL',
        '$class_constant_origin(S_warn.CLASSES,pclassconstantcontext.DECL) = (pclassconstantdesc)',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)',
        'pclassdesc.KIND = "interface"', '$owned_class_constant_source(S_warn,pclassconstantdesc)',
        '$class_constant_deprecated(S_warn,pclassconstantdesc)',
        '~$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        '$class_constant_protected(pclassconstantcontext.SELECTION,pclassconstantcontext.PREVIOUS)',
        '$class_constant_visited(S_warn.CLASSCONSTANTINIT,pclassconstantdesc.ORIGIN)',
        '$class_constant_context_valid(S_warn,pconstantcontext)',
        'S_view = $class_constant_restore(S_warn,pclassconstantcontext,pclassconstantcontext_tail*)',
        '$class_constant_api_selection(S_view,pconfigcall) = (pclassconstantdesc)',
        '$class_constant_api_owned_global(S_view,pclassconstantdesc) = (puserconstant)',
        'puserconstant.VALUE = POBJECT n_donor',
        '~$class_constant_api_global_scalar(S_view,puserconstant.NAME)',
        '$dynamic_class_constant_initializer(S_view,pclassconstantdesc) = false',
        '$class_constant_api_resume_present(S_warn.TODO,pclassconstantdesc.ORIGIN,pconfigcall)',
        '$task_nodes(DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall pclassconstantdesc.ORIGIN true) = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = eps',
        '$deprecated_constant_class_ast(S_warn,pdeprecatedconstant.SITE)',
        '$call_descriptors_valid(S_warn)',
        'S_bind = $class_owned_parent_pause(S_warn,pclassconstantcontext,30000)',
        '$class_owned_parent_ready(S_bind,pclassconstantcontext)',
        'S_bind.TODO = (CLASS_CONST_BIND pclassconstantdesc.ORIGIN) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall pclassconstantdesc.ORIGIN true) :: ptask_tail*',
        'S_bind.RESULT = KNOWN (POBJECT n_donor)',
        'S_bind.CONSTCONTEXT = (pconstantcontext_bind)',
        '$class_constant_context_valid(S_bind,pconstantcontext_bind)',
        '$constant_fact_at(pconstantcontext_bind.FACTS,pclassconstantdesc.INITIALIZER) = (pconstantfact)',
        'pconstantfact.LOOKUP = (pconstantlookup)',
        '$global_constant_lookup_valid(S_bind,pclassconstantdesc.ORIGIN,pconstantfact,S_bind.USERCONSTANTS)',
        '$class_constant_pending_cache(S_bind,pclassconstantcontext)',
        '$call_descriptors_valid(S_bind)',
        'S_bound_raw = $drive_steps(S_bind,1)', 'S_bound_raw.COMPLETION = BUDGET',
        'S_bound = S_bound_raw[.COMPLETION = NORMAL]',
        'S_bound.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall pclassconstantdesc.ORIGIN true) :: ptask_tail*',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = puserconstant.VALUE', 'pdefaultcache.CLASS = puserconstant.CLASS',
        '$class_constant_row_payload_valid(S_bound,pclassconstantdesc,pdefaultcache)',
        '$class_constant_roots(S_bound.CLASSCONSTANTCACHE) = [HOBJECT n_donor]',
        'S_bound.RESULT = KNOWN (POBJECT n_donor)',
        '$heap_owners($heap_graph(S_bound),HOBJECT n_donor) = $($heap_owners($heap_graph(S_bind),HOBJECT n_donor) + 1)',
        'S_zero = $drive_steps(S_bound,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S_bound.TODO',
        'S_one_raw = $drive_steps(S_bound,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_after = S_one_raw[.COMPLETION = NORMAL]',
        'S_after.RESULT = KNOWN (POBJECT n_donor)', 'S_after.TODO = ptask_tail*',
        '$heap_owners($heap_graph(S_after),HOBJECT n_donor) = $heap_owners($heap_graph(S_bound),HOBJECT n_donor)',
        'S_after.CLASSCONSTANTCACHE = S_bound.CLASSCONSTANTCACHE',
        'S_after.CLASSCONSTANTHISTORY = S_bound.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_after,pclassconstantdesc.ORIGIN)',
        'S_live = $interface_review_closure_pause(S_after,n_donor,30000)',
        '$interface_review_closure_ready(S_live,n_donor)', 'S_live.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = eps', 'pcallcontext.CALLED_CLASS = eps', 'pcallcontext.RECEIVER = eps',
        '$class_named(S_live.CLASSNAMES,$ptlc(' + quoted('Ns216Closure' + chr(92) + 'Child216') + ')) = (porigin_child)',
        '$class_named(S_live.CLASSNAMES,$ptlc(' + quoted('Ns216Closure' + chr(92) + 'Implementer216') + ')) = (porigin_implementer)',
        '$class_constant_lookup(S_live,porigin_child,$ptascii("VALUE"),|S_live.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_live,porigin_implementer,$ptascii("VALUE"),|S_live.CLASSES|) = (pclassconstantdesc)',
        '|S_live.CLASSCONSTANTCACHE| = 1',
        'S_done = $drive(S_live,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_review_output(S_done.EVENTS) = ' + quoted(expected),
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        '|S_done.CLASSCONSTANTCACHE| = 1',
        '$class_constant_history_valid(S_done)',
        '$class_constant_caches_valid(S_done,S_done.CLASSCONSTANTCACHE)',
        '$lookup(S_done.ENV,$ptascii("first")) = (n_first)',
        '$lookup(S_done.ENV,$ptascii("second")) = (n_second)',
        '$lookup(S_done.ENV,$ptascii("third")) = (n_third)',
        'S_done.STORE[n_first] = DEFINED (POBJECT n_donor)',
        'S_done.STORE[n_second] = DEFINED (POBJECT n_donor)',
        'S_done.STORE[n_third] = DEFINED (POBJECT n_donor)',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_after,30000) = S_done',
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
    (out / 'protocol.watsup').write_text(PREFIX + EXTRA + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
            for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_owned_review_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
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
