#!/usr/bin/env python3
"""Check attributed owning source authority, Closure identity and typed cache preservation."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_owned_class_constant_notice_review'
SELECTIONS = {'closure': SOURCE / 'interface-closure.php',
    'typed': SOURCE / 'typed-child-cache.php'}
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


def start(fixture, path, namespace, kind):
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],30000)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.COPIED = eps', '$task_nodes(perrorcall.RESUME) = eps',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'S_warn.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.DECL = pconstantcontext.ORIGIN',
        '$class_constant_origin(S_warn.CLASSES,pclassconstantcontext.DECL) = (pclassconstantdesc)',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)',
        'pclassdesc.KIND = "' + kind + '"', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$class_constant_deprecated(S_warn,pclassconstantdesc)',
        '$class_constant_attribute_group(S_warn.SOURCES,pclassconstantdesc) =/= eps',
        '$owned_class_constant_source(S_warn,pclassconstantdesc)',
        '~$owned_class_constant_source(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$owned_class_constant_source(S_warn,pclassconstantdesc[.INITIALIZER = pclassconstantdesc.ORIGIN])',
        '~$owned_class_constant_source(S_warn,pclassconstantdesc[.FOLDED = true])',
        '$class_constant_context_valid(S_warn,pconstantcontext)',
        '$deprecated_constant_class_ast(S_warn,pdeprecatedconstant.SITE)',
        '~$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        '$class_named(S_warn.CLASSNAMES,$ptlc(' + quoted(namespace + chr(92) + 'Child215') + ')) = (porigin_child)',
        '$class_constant_lookup(S_warn,porigin_child,$ptascii("VALUE"),|S_warn.CLASSES|) = (pclassconstantdesc)',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = eps',
        '$class_constant_pending_cache(S_warn,pclassconstantcontext)',
        '$call_descriptors_valid(S_warn)']


def bind(parent=False):
    pause = '$class_owned_parent_pause(S_warn,pclassconstantcontext,30000)' if parent else '$class_owned_pause(S_warn,0,pclassconstantcontext.DECL,30000)'
    return ['S_bind = ' + pause,
        '$class_owned_ready(S_bind,0,pclassconstantcontext.DECL)',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'S_bind.CONSTCONTEXT = (pconstantcontext_bind)',
        '$class_constant_context_valid(S_bind,pconstantcontext_bind)',
        '$class_constant_pending_cache(S_bind,pclassconstantcontext)',
        '$call_descriptors_valid(S_bind)']


def finish(group):
    row = json.loads((SOURCE / 'cases.json').read_text())[SELECTIONS[group].stem]
    return ['S_done.COMPLETION = NORMAL',
        '$interface_review_output(S_done.EVENTS) = ' + quoted(row['stdout']),
        '$class_constant_history_valid(S_done)',
        '$class_constant_caches_valid(S_done,S_done.CLASSCONSTANTCACHE)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache)',
        '|S_done.CLASSCONSTANTCACHE| = 1',
        '$class_constant_lookup(S_done,porigin_child,$ptascii("VALUE"),|S_done.CLASSES|) = (pclassconstantdesc)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)',
        '$call_descriptors_valid(S_done)']


def closure(fixture, path):
    return start(fixture, path, 'Ns215Closure', 'interface') + bind() + [
        '$interface_review_output(S_warn.EVENTS) = $ptascii("C|")',
        '$class_named(S_warn.CLASSNAMES,$ptlc(' + quoted('Ns215Closure' + chr(92) + 'Implementer215') + ')) = (porigin_implementer)',
        '$class_constant_lookup(S_warn,porigin_implementer,$ptascii("VALUE"),|S_warn.CLASSES|) = (pclassconstantdesc)',
        'S_bind.RESULT = KNOWN (POBJECT n_donor)',
        '$global_constant_alias(S_warn,S_warn.USERCONSTANTS,pclassconstantdesc.INITIALIZER) = (puserconstant_original)',
        'puserconstant_original.VALUE = POBJECT n_donor',
        '$constant_fact_at(pconstantcontext_bind.FACTS,pclassconstantdesc.INITIALIZER) = (pconstantfact)',
        'pconstantfact.LOOKUP = (pconstantlookup)',
        '$global_constant_lookup_valid(S_bind,pclassconstantcontext.DECL,pconstantfact,S_bind.USERCONSTANTS)',
        '~$global_constant_lookup_valid(S_bind,pclassconstantcontext.DECL,pconstantfact[.LOOKUP = eps],S_bind.USERCONSTANTS)',
        'S_after_raw = $drive_steps(S_bind,1)', 'S_after_raw.COMPLETION = BUDGET',
        'S_after = S_after_raw[.COMPLETION = NORMAL]',
        'S_after.CLASSCONSTANTINIT = eps', 'S_after.CONSTCONTEXT = eps',
        '$default_cache_at(S_after.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache)',
        'pdefaultcache.VALUE = POBJECT n_donor',
        '$class_constant_roots(S_after.CLASSCONSTANTCACHE) = [HOBJECT n_donor]',
        '$class_constant_history_valid(S_after)',
        '$class_constant_caches_valid(S_after,S_after.CLASSCONSTANTCACHE)',
        'S_live = $interface_review_closure_pause(S_after,n_donor,30000)',
        '$interface_review_closure_ready(S_live,n_donor)', 'S_live.CURRENT = (pcallcontext_live)',
        'pcallcontext_live.LEXICAL_CLASS = eps', 'pcallcontext_live.CALLED_CLASS = eps',
        'pcallcontext_live.RECEIVER = eps',
        '$target_function(S_live,pcallcontext_live.TARGET) = (pfunction_live)',
        'pcallcontext_live.FUNCTION = pfunction_live.ORIGIN',
        'S_done = $drive(S_live,30000)',
        'pdefaultcache.VALUE = POBJECT n_donor',
        '$class_constant_lookup(S_done,porigin_implementer,$ptascii("VALUE"),|S_done.CLASSES|) = (pclassconstantdesc)'] + finish('closure')


def typed(fixture, path):
    return start(fixture, path, 'Ns215Typed', 'class') + bind(parent=True) + [
        'S_warn.REPORTING = 0',
        'S_bind.RESULT = KNOWN (PARRAY n_rejected)',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache)',
        'pdefaultcache.VALUE = PINT 9',
        '$class_constant_runtime_type(S_bind,pclassconstantdesc.TYPE,PINT 9)',
        '~$class_constant_runtime_type(S_bind,pclassconstantdesc.TYPE,PARRAY n_rejected)',
        '$(pclassconstantcontext.HISTORY < |S_bind.CLASSCONSTANTHISTORY|)',
        '~$owned_class_cache_seen(S_bind.CLASSCONSTANTHISTORY[0:pclassconstantcontext.HISTORY],pclassconstantcontext.DECL)',
        'n_after = $nabs($(|S_bind.CLASSCONSTANTHISTORY| - pclassconstantcontext.HISTORY))',
        '$owned_class_cache_seen(S_bind.CLASSCONSTANTHISTORY[pclassconstantcontext.HISTORY:n_after],pclassconstantcontext.DECL)',
        '$interface_review_output(S_bind.EVENTS) = $ptascii("C|G|I|9|")',
        'S_zero = $drive_steps(S_bind,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_bind',
        'PhpStep: S_bind ~> S_reject',
        'S_reject.COMPLETION = THROWN "TypeError" preqbytes_error z_error',
        'S_reject.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE',
        'S_reject.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        'S_reject.CLASSCONSTANTINIT = eps', 'S_reject.CONSTCONTEXT = eps',
        'S_one_raw = $drive_steps(S_bind,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        '$default_cache_at(S_one.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache)',
        '$call_descriptors_valid(S_one)',
        'S_done = $drive(S_one,30000)', 'S_done.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '$drive(S_bind,30000) = S_done',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done'] + finish('typed')


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
