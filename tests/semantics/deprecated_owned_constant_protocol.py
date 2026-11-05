#!/usr/bin/env python3
"""Authenticate prewarning copies and postwarning selected constant facts."""
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
SOURCE = Path(__file__).with_name('deprecated_global_constant')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()
PREFIX += '''
dec $owned_ready(ptask*) : bool
def $owned_ready((DEPRECATED_CONSTANT_RESULT pdeprecatedconstant) :: ptask*) = true
def $owned_ready((DEPRECATED_GLOBAL_CONSTANT_RESULT pconfigcall n) :: ptask*) = true
def $owned_ready(ptask*) = $dep_ready(ptask*) -- otherwise
dec $owned_pause(pstate,nat) : pstate
def $owned_pause(S,n) = S -- if $owned_ready(S.TODO)
def $owned_pause(S,n) = $owned_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if ~$owned_ready(S.TODO)
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_pause(S,n) = S -- otherwise
dec $owned_observer_ready(pstate,porigin) : bool
def $owned_observer_ready(S,porigin) = true
  -- if S.TODO = (CONSTANT_OBSERVE porigin) :: ptask*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $constant_fact_at(pconstantcontext.FACTS,porigin) = (pconstantfact)
  -- if pconstantfact.LOOKUP =/= eps
def $owned_observer_ready(S,porigin) = false -- otherwise
dec $owned_observer_pause(pstate,porigin,nat) : pstate
def $owned_observer_pause(S,porigin,n) = S -- if $owned_observer_ready(S,porigin)
def $owned_observer_pause(S,porigin,n) = $owned_observer_pause(S_next[.COMPLETION = NORMAL],porigin,n_next)
  -- if ~$owned_observer_ready(S,porigin)
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_observer_pause(S,porigin,n) = S -- otherwise
dec $owned_clean_head(ptask) : perrorcall?
def $owned_clean_head(ERROR_HANDLER_CLEAN perrorcall) = (perrorcall)
def $owned_clean_head(ptask) = eps -- otherwise
dec $owned_clean_task(ptask*) : perrorcall?
def $owned_clean_task(ptask_head :: ptask_tail*) = (perrorcall)
  -- if $owned_clean_head(ptask_head) = (perrorcall)
def $owned_clean_task(ptask_head :: ptask_tail*) = $owned_clean_task(ptask_tail*)
  -- if $owned_clean_head(ptask_head) = eps
def $owned_clean_task(eps) = eps
dec $owned_clean_pause(pstate,nat) : pstate
def $owned_clean_pause(S,n) = S -- if $owned_clean_task(S.TODO) =/= eps
def $owned_clean_pause(S,n) = $owned_clean_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if $owned_clean_task(S.TODO) = eps
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_clean_pause(S,n) = S -- otherwise
dec $owned_parked_pause(pstate,nat) : pstate
def $owned_parked_pause(S,n) = S -- if $deprecated_handler_eval_frames(S.FRAMES) =/= S.FRAMES
def $owned_parked_pause(S,n) = $owned_parked_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if $deprecated_handler_eval_frames(S.FRAMES) = S.FRAMES
  -- if $(n > 0) /\\ S.COMPLETION = NORMAL /\\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_parked_pause(S,n) = S -- otherwise
dec $eval_control_remove(ptask*,nat) : ptask*
def $eval_control_remove(eps,n) = eps
def $eval_control_remove(ptask :: ptask_tail*,n) = $eval_control_remove(ptask_tail*,n)
  -- if $eval_marker_id(ptask) = (n)
def $eval_control_remove(ptask :: ptask_tail*,n) = ptask :: $eval_control_remove(ptask_tail*,n)
  -- if $eval_marker_id(ptask) =/= (n)
dec $eval_control_replace(ptask*,nat,nat) : ptask*
def $eval_control_replace(eps,n,n_new) = eps
def $eval_control_replace(ptask :: ptask_tail*,n,n_new) = (EVAL_END n_new) :: ptask_tail*
  -- if $eval_marker_id(ptask) = (n)
def $eval_control_replace(ptask :: ptask_tail*,n,n_new) = ptask :: $eval_control_replace(ptask_tail*,n,n_new)
  -- if $eval_marker_id(ptask) =/= (n)
'''


def prepare(out):
    cases = json.loads((SOURCE / 'cases.json').read_text())
    selected = ('array-source-pending', 'owned-array-source-cow', 'owned-stdclass-shadow',
        'owned-closure-shadow', 'owned-api-throw-rebind', 'owned-retval-protected-mutation',
        'owned-source-throw', 'owned-source-exit-cancel', 'owned-parameter-default-pending',
        'owned-class-default-pending', 'owned-static-default-pending',
        'owned-global-ast-exit', 'owned-global-ast-exit-cancel')
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name in selected:
            path = SOURCE / cases[name]['source']; tag = name.replace('-', '_')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            start = 'S_start_' + tag; state = 'S_pending_' + tag
            checks += ['U_' + tag + ' = ' + checked['fixture'],
                start + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')',
                start + '.COMPLETION = BUDGET']
            if name.endswith('default-pending'):
                checks += ['S_refuse_' + tag + ' = $drive(' + start + '[.COMPLETION = NORMAL],10000)',
                    'S_refuse_' + tag + '.COMPLETION = UNSUPPORTED "Deprecated constant owning value"']
                continue
            running = start + '[.COMPLETION = NORMAL]'
            if name in ('owned-global-ast-exit', 'owned-global-ast-exit-cancel'):
                code, = [base64.b64decode(node['fields'][0]['bytes']) for node, _ in nodes(parsed['ast']['program'])
                    if node['node'] == 'Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'const Y185 =')]
                parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': b64(code)})
                assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
                checked_eval = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})
                assert checked_eval['ok']
                response = 'SOURCE_ACCEPT 1 ($ptascii(' + json.dumps(code.decode()) + ')) ' + checked_eval['fixture']
                wait = 'S_wait_' + tag; entered = 'S_entered_' + tag
                checks += [wait + ' = $drive(' + running + ',10000)', wait + '.COMPLETION = SOURCE_PENDING',
                    '$call_descriptors_valid(' + wait + ')', '$eval_response_valid(' + wait + ',' + response + ')',
                    entered + ' = $eval_resume(' + wait + ',' + response + ')', entered + '.COMPLETION = NORMAL',
                    '$call_descriptors_valid(' + entered + ')']
                running = entered
            checks += [state + ' = $owned_pause(' + running + ',10000)',
                state + '.COMPLETION = NORMAL', '$call_descriptors_valid(' + state + ')']
            error = 'perrorcall_' + tag; dep = 'pdeprecatedconstant_' + tag; tail = 'ptask_' + tag + '*'
            if name == 'array-source-pending':
                checks += [state + '.TODO = (DEPRECATED_CONSTANT_RESULT ' + dep + ') :: ' + tail]
                resume = 'DEPRECATED_CONSTANT_RESULT ' + dep
            else:
                checks += [state + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ' + tail]
                if name == 'owned-api-throw-rebind':
                    config = 'pconfigcall_' + tag; prefix = 'n_prefix_' + tag
                    checks += [error + '.RESUME = DEPRECATED_GLOBAL_CONSTANT_RESULT ' + config + ' ' + prefix,
                        '$deprecated_api_query(' + config + ') = (preqbytes_' + tag + ')',
                        '$deprecated_api_value(' + state + ',preqbytes_' + tag + ') = (PARRAY n_array_' + tag + ')',
                        '$heap_count(HARRAY n_array_' + tag + ',$task_nodes(' + error + '.RESUME)) = 0',
                        '$task_nodes(' + error + '.RESUME) = $config_nodes(' + config + ')',
                        'S_done_' + tag + ' = $drive(' + state + ',10000)',
                        'S_done_' + tag + '.COMPLETION = NORMAL', '$call_descriptors_valid(S_done_' + tag + ')']
                    continue
                checks += [error + '.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep]
                resume = error + '.RESUME'
            if name in ('owned-global-ast-exit', 'owned-global-ast-exit-cancel'):
                marker_state = 'S_marker_' + tag
                cleanup = 'pdestructioncleanup_' + tag
                saved = 'ptask_saved_' + tag + '*'
                status = 'z_marker_' + tag
                marker = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ' + saved
                context = 'pconstantcontext_' + tag
                checks += [dep + '.COPIED = eps', state + '.CONSTCONTEXT = (' + context + ')']
                if name == 'owned-global-ast-exit':
                    checks += [marker_state + ' = $dep_exit_pause(' + state + ',10000)',
                        marker_state + '.TODO = (' + marker + ') :: eps']
                else:
                    checks += [marker_state + ' = $dep_throw_pause(' + state + ',10000)',
                        marker_state + '.TODO = (THROW_SEARCH n_throw_' + tag + ') :: (' + marker + ') :: eps']
                checks += [cleanup + '.SOURCE = ERROR_HANDLER_RESULT perrorcall_marker_' + tag,
                    saved + ' = (ERROR_HANDLER_RESULT perrorcall_marker_' + tag + ') :: ptask_marker_tail_' + tag + '*',
                    marker_state + '.CONSTCONTEXT = (' + context + ')',
                    '$constant_bindings(' + marker_state + ',' + marker_state + '.TODO) = [' + context + '.ORIGIN]',
                    '$constant_context_valid(' + marker_state + ')', '$call_descriptors_valid(' + marker_state + ')',
                    '$task_nodes(perrorcall_marker_' + tag + '.RESUME) = eps']
                if name == 'owned-global-ast-exit':
                    checks += ['PhpStep: ' + marker_state + ' ~> S_marker_released_' + tag,
                        'S_marker_released_' + tag + '.TODO = (DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved + ') :: eps',
                        '$constant_context_valid(S_marker_released_' + tag + ')',
                        '$call_descriptors_valid(S_marker_released_' + tag + ')']
                else:
                    checks += ['S_marker_step_' + tag + ' = $drive_steps(' + marker_state + ',1)',
                        'S_marker_step_' + tag + '.COMPLETION = BUDGET',
                        'S_marker_released_' + tag + ' = $dep_throw_pause(S_marker_step_' + tag + '[.COMPLETION = NORMAL],10000)',
                        'S_marker_released_' + tag + '.TODO = (THROW_SEARCH n_released_' + tag + ') :: (DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved + ') :: eps',
                        '$constant_context_valid(S_marker_released_' + tag + ')',
                        '$call_descriptors_valid(S_marker_released_' + tag + ')']
                for label, changed in (('status', 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' $(' + status + ' + 1) ' + saved),
                        ('target', 'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.TARGET.INTERNAL = false] ' + status + ' ' + saved),
                        ('binder', 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ([(ERROR_HANDLER_RESULT perrorcall_marker_' + tag + ')])'),
                        ('context', 'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.CONSTCONTEXT = eps] ' + status + ' ' + saved)):
                    bad = 'S_marker_bad_' + label + '_' + tag
                    # Use the actual fresh marker suffix; prepend only its real throw cursor.
                    prefix = '(THROW_SEARCH n_throw_' + tag + ') :: ' if name == 'owned-global-ast-exit-cancel' else ''
                    checks += [bad + ' = ' + marker_state + '[.TODO = ' + prefix + '(' + changed + ') :: eps]',
                        '~$call_descriptors_valid(' + bad + ')']
                # Keep the same EHR, binder and live marker; corrupt only its retained eval control.
                checks += [marker_state + '.EVALCONTEXTS = pevalcontext_' + tag + ' :: eps',
                    '$eval_marker_count(' + saved + ',pevalcontext_' + tag + '.UNIT) = 1']
                for label, changed_saved in (('missing', '$eval_control_remove(' + saved + ',pevalcontext_' + tag + '.UNIT)'),
                        ('duplicate', '(ERROR_HANDLER_RESULT perrorcall_marker_' + tag + ') :: (EVAL_END pevalcontext_' + tag + '.UNIT) :: ptask_marker_tail_' + tag + '*'),
                        ('unit', '$eval_control_replace(' + saved + ',pevalcontext_' + tag + '.UNIT,$(pevalcontext_' + tag + '.UNIT + 1))'),
                        ('tail', saved + ' ++ [DISCARD]')):
                    bad = 'S_bad_eval_' + label + '_' + tag
                    prefix = '(THROW_SEARCH n_throw_' + tag + ') :: ' if name == 'owned-global-ast-exit-cancel' else ''
                    checks += [bad + ' = ' + marker_state + '[.TODO = ' + prefix + '(DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' (' + changed_saved + ')) :: eps]',
                        '~$call_descriptors_valid(' + bad + ')']
                    if label == 'duplicate':
                        checks += ['$eval_marker_count((' + changed_saved + '),pevalcontext_' + tag + '.UNIT) = 2']
                checks += ['$deprecated_handler_eval_tasks([(DEPRECATED_HANDLER_EXIT ' + cleanup + '[.SOURCE = DISCARD] ' + status + ' ' + saved + ')]) = [(DEPRECATED_HANDLER_EXIT ' + cleanup + '[.SOURCE = DISCARD] ' + status + ' ' + saved + ')]']
                if name == 'owned-global-ast-exit-cancel':
                    checks += ['S_parked_' + tag + ' = $owned_parked_pause(' + state + ',10000)',
                        'S_parked_' + tag + '.CONSTCONTEXT = eps',
                        '$deprecated_handler_eval_frames(S_parked_' + tag + '.FRAMES) =/= S_parked_' + tag + '.FRAMES',
                        '$eval_state_valid(S_parked_' + tag + ')', '$call_descriptors_valid(S_parked_' + tag + ')']
                checks += ['S_done_' + tag + ' = $drive(' + marker_state + ',10000)',
                    'S_done_' + tag + '.COMPLETION = ' + ('EXITED 0' if name == 'owned-global-ast-exit' else 'NORMAL'),
                    '$call_descriptors_valid(S_done_' + tag + ')']
                continue
            if name in ('owned-stdclass-shadow', 'owned-closure-shadow'):
                checks += [dep + '.COPIED = eps', state + '.CONSTCONTEXT = (pconstantcontext_' + tag + ')',
                    '$task_nodes(' + resume + ') = eps',
                    'pvalue_' + tag + ' = $deprecated_constant_value(' + state + ',' + dep + '.SITE)',
                    'pvalueclass_' + tag + ' = $deprecated_constant_class(' + state + ',' + dep + '.SITE)',
                    'S_bad_copy_' + tag + ' = ' + state + '[.TODO = (ERROR_HANDLER_INVOKE ' + error + '[.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep + '[.COPIED = ((pvalue_' + tag + ',pvalueclass_' + tag + '))]]) :: ' + tail + ']',
                    '~$call_descriptors_valid(S_bad_copy_' + tag + ')',
                    'S_observe_' + tag + ' = $owned_observer_pause(' + state + ',' + dep + '.SITE,10000)',
                    'S_observe_' + tag + '.CONSTCONTEXT = (pconstantcontext_after_' + tag + ')',
                    '$constant_fact_at(pconstantcontext_after_' + tag + '.FACTS,' + dep + '.SITE) = (pconstantfact_' + tag + ')',
                    'pconstantfact_' + tag + '.CLASS = pvalueclass_' + tag,
                    'pconstantfact_' + tag + '.VALUE = eps',
                    'pconstantfact_' + tag + '.LOOKUP = (pconstantlookup_' + tag + ')',
                    'pconstantlookup_' + tag + '.PREFIX = ' + dep + '.PREFIX',
                    '$(pconstantlookup_' + tag + '.PREFIX < |S_observe_' + tag + '.USERCONSTANTS|)',
                    '$global_constant_observation_lookup(S_observe_' + tag + ',' + dep + '.SITE,pvalue_' + tag + ',pvalueclass_' + tag + ') = (pconstantlookup_' + tag + ')',
                    '$global_constant_observation_prior(S_observe_' + tag + '[.TODO = [DISCARD]],' + dep + '.SITE,pvalue_' + tag + ',pvalueclass_' + tag + ') = eps',
                    '$global_constant_observation_prior(S_observe_' + tag + '[.RESULT = KNOWN (PINT 0)],' + dep + '.SITE,pvalue_' + tag + ',pvalueclass_' + tag + ') = eps']
                for label, mutation in (('prefix', '.PREFIX = $(|S_observe_' + tag + '.USERCONSTANTS| + 1)'),
                        ('site', '.SITE = pconstantcontext_after_' + tag + '.ORIGIN'),
                        ('decl', '.DECL = pconstantcontext_after_' + tag + '.ORIGIN')):
                    bad = 'S_bad_lookup_' + label + '_' + tag
                    checks += [bad + ' = S_observe_' + tag + '[.CONSTCONTEXT = (pconstantcontext_after_' + tag + '[.FACTS = $constant_fact_put(pconstantcontext_after_' + tag + '.FACTS,pconstantfact_' + tag + '[.LOOKUP = (pconstantlookup_' + tag + '[' + mutation + '])])])]',
                        '$global_constant_observation_lookup(' + bad + ',' + dep + '.SITE,pvalue_' + tag + ',pvalueclass_' + tag + ') = eps']
                checks += ['S_done_' + tag + ' = $drive(S_observe_' + tag + ',10000)',
                    'S_done_' + tag + '.COMPLETION = NORMAL', '$call_descriptors_valid(S_done_' + tag + ')']
                continue
            checks += [state + '.CONSTCONTEXT = eps', dep + '.COPIED = ((PARRAY n_array_' + tag + ',pvalueclass_' + tag + '))',
                '$task_nodes(' + resume + ') = [HARRAY n_array_' + tag + ']',
                '$heap_count(HARRAY n_array_' + tag + ',$task_nodes(' + resume + ')) = 1',
                state + '.RESULT = KNOWN PNULL',
                '$constant_value_class_valid(' + state + ',PARRAY n_array_' + tag + ',pvalueclass_' + tag + ')']
            for label, copied in (('missing', 'eps'), ('class', '((PARRAY n_array_' + tag + ',PVSCALAR))'),
                    ('value', '((PINT 0,PVSCALAR))')):
                bad_dep = dep + '[.COPIED = ' + copied + ']'; bad = 'S_bad_' + label + '_' + tag
                task = 'DEPRECATED_CONSTANT_RESULT ' + bad_dep if name == 'array-source-pending' else 'ERROR_HANDLER_INVOKE ' + error + '[.RESUME = DEPRECATED_CONSTANT_RESULT ' + bad_dep + ']'
                checks += [bad + ' = ' + state + '[.TODO = (' + task + ') :: ' + tail + ']', '~$call_descriptors_valid(' + bad + ')']
            if name == 'owned-retval-protected-mutation':
                clean = 'S_clean_' + tag; clean_error = 'perrorcall_clean_' + tag
                checks += [clean + ' = $owned_clean_pause(' + state + ',10000)',
                    '$owned_clean_task(' + clean + '.TODO) = (' + clean_error + ')',
                    clean_error + '.RESUME = ' + resume,
                    '$call_descriptors_valid(' + clean + ')',
                    '$heap_count(HARRAY n_array_' + tag + ',$task_nodes(ERROR_HANDLER_CLEAN ' + clean_error + ')) = 1']
            if name == 'owned-source-exit-cancel':
                marker_state = 'S_owned_marker_' + tag
                cleanup = 'pdestructioncleanup_owned_' + tag; saved = 'ptask_owned_saved_' + tag + '*'
                status = 'z_owned_' + tag
                marker = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ' + saved
                released = 'DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved
                checks += [marker_state + ' = $dep_throw_pause(' + state + ',10000)',
                    marker_state + '.TODO = (THROW_SEARCH n_owned_' + tag + ') :: (' + marker + ') :: eps',
                    cleanup + '.SOURCE = ERROR_HANDLER_RESULT perrorcall_owned_' + tag,
                    'perrorcall_owned_' + tag + '.RESUME = ' + resume,
                    '~' + cleanup + '.RELEASED',
                    '$call_descriptors_valid(' + marker_state + ')',
                    '$heap_count(HARRAY n_array_' + tag + ',$task_nodes(' + marker + ')) = 1',
                    'S_owned_marker_step_' + tag + ' = $drive_steps(' + marker_state + ',1)',
                    'S_owned_marker_step_' + tag + '.COMPLETION = BUDGET',
                    'S_owned_released_' + tag + ' = $dep_throw_pause(S_owned_marker_step_' + tag + '[.COMPLETION = NORMAL],10000)',
                    'S_owned_released_' + tag + '.TODO = (THROW_SEARCH n_owned_released_' + tag + ') :: (' + released + ') :: eps',
                    '$call_descriptors_valid(S_owned_released_' + tag + ')',
                    '$heap_count(HARRAY n_array_' + tag + ',$task_nodes(' + released + ')) = 1']
            checks += ['S_done_' + tag + ' = $drive(' + state + ',10000)',
                'S_done_' + tag + '.COMPLETION = NORMAL', '$call_descriptors_valid(S_done_' + tag + ')']
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), ROOT / 'tests/semantics/deprecated_global_constant_protocol.py', *modules,
        SOURCE / 'cases.json', SOURCE / 'hashes.json', *(SOURCE / p for p in json.loads((SOURCE / 'hashes.json').read_text())),
        *(ROOT / p for p in ('spec/semantics/modules.json', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
            'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
