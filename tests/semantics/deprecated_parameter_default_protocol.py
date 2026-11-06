#!/usr/bin/env python3
"""Check source-selected default values, cache reentry and rejected formal roots."""
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
SOURCE = Path(__file__).with_name('deprecated_global_constant')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()
PREFIX += r'''
dec $parameter_test_bind(ptask) : (porigin,nat)?
def $parameter_test_bind(DEFAULT_BIND porigin n) = ((porigin,n))
def $parameter_test_bind(NAMED_DEFAULT_BIND porigin n) = ((porigin,n))
def $parameter_test_bind(ptask) = eps -- otherwise
dec $parameter_test_ready(pstate,nat) : bool
def $parameter_test_ready(S,0) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $parameter_test_bind(ptask) = ((porigin,n))
  -- if $parameter_receive_owner(S.CURRENT) = (n_owner)
  -- if $parameter_receive_birth(S,n_owner) = (preceivebirth)
  -- if preceivebirth.PARENT = eps
def $parameter_test_ready(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $parameter_test_ready(S,2) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at(S.FUNCTIONS,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,n) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $parameter_test_ready(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (DEFAULT_BIND porigin n) :: ptask_tail*
def $parameter_test_ready(S,n) = false -- otherwise
dec $parameter_test_pause(pstate,nat,nat) : pstate
def $parameter_test_pause(S,n_mode,n) = S -- if $parameter_test_ready(S,n_mode)
def $parameter_test_pause(S,n_mode,n) = $parameter_test_pause(S_next[.COMPLETION = NORMAL],n_mode,n_next)
  -- if ~$parameter_test_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $parameter_test_pause(S,n_mode,n) = S -- otherwise
'''


def prepare(out):
    cases = json.loads((SOURCE / 'cases.json').read_text())
    selected = ('parameter-owned-nonempty-array-cache', 'parameter-owned-empty-array-cache',
        'parameter-owned-shadow', 'parameter-owned-reentry', 'parameter-owned-reentry-nonempty',
        'parameter-owned-named-reentry', 'parameter-owned-type-cache',
        'parameter-owned-local-exit-cancel', 'parameter-owned-closure-pending', 'parameter-owned-method-pending')
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
            start = 'S_start_' + tag; warn = 'S_warn_' + tag; bind = 'S_bind_' + tag
            error = 'perrorcall_' + tag; dep = 'pdeprecatedconstant_' + tag; tail = 'ptask_warn_' + tag + '*'
            ctx = 'pconstantcontext_' + tag; call = 'pcallcontext_' + tag; birth = 'preceivebirth_' + tag
            owner = 'n_owner_' + tag; fn = 'pfunction_' + tag; default = 'pdefault_' + tag; index = 'n_index_' + tag
            checks += ['U_' + tag + ' = ' + checked['fixture'],
                start + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')', start + '.COMPLETION = BUDGET']
            if cases[name]['status'] == 'unsupported':
                checks += ['S_stop_' + tag + ' = $drive(' + start + '[.COMPLETION = NORMAL],10000)',
                    'S_stop_' + tag + '.COMPLETION = UNSUPPORTED "Deprecated constant owning value"']
                continue
            checks += [warn + ' = $dep_pause(' + start + '[.COMPLETION = NORMAL],10000)',
                warn + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ' + tail,
                error + '.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep, dep + '.COPIED = eps',
                warn + '.CONSTCONTEXT = (' + ctx + ')', warn + '.CURRENT = (' + call + ')',
                '$parameter_receive_owner(' + warn + '.CURRENT) = (' + owner + ')',
                '$parameter_receive_birth(' + warn + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                '$parameter_receive_named_entry(' + warn + ',' + birth + ')',
                '$deprecated_constant_parameter_ast(' + warn + ',' + dep + '.SITE)',
                '$task_nodes(' + error + '.RESUME) = eps', '$call_descriptors_valid(' + warn + ')',
                'pvalue_' + tag + ' = $deprecated_constant_value(' + warn + ',' + dep + '.SITE)',
                'pvalueclass_' + tag + ' = $deprecated_constant_class(' + warn + ',' + dep + '.SITE)',
                'S_bad_copy_' + tag + ' = ' + warn + '[.TODO = (ERROR_HANDLER_INVOKE ' + error + '[.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep + '[.COPIED = ((pvalue_' + tag + ',pvalueclass_' + tag + '))]]) :: ' + tail + ']',
                '~$call_descriptors_valid(S_bad_copy_' + tag + ')']
            if name == 'parameter-owned-local-exit-cancel':
                marker_state = 'S_marker_' + tag; cleanup = 'pdestructioncleanup_' + tag; saved = 'ptask_saved_' + tag + '*'; status = 'z_status_' + tag
                marker = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' ' + status + ' ' + saved
                checks += [marker_state + ' = $dep_throw_pause(' + warn + ',10000)',
                    marker_state + '.TODO = (THROW_SEARCH n_throw_' + tag + ') :: (' + marker + ') :: eps',
                    '$constant_bindings(' + marker_state + ',' + marker_state + '.TODO) = [' + ctx + '.ORIGIN]',
                    '$constant_context_valid(' + marker_state + ')', '$call_descriptors_valid(' + marker_state + ')',
                    '$task_nodes(' + marker + ') = $tasks_nodes(' + saved + ')',
                    'S_marker_step_' + tag + ' = $drive_steps(' + marker_state + ',1)',
                    'S_marker_step_' + tag + '.COMPLETION = BUDGET',
                    'S_released_' + tag + ' = $dep_throw_pause(S_marker_step_' + tag + '[.COMPLETION = NORMAL],10000)',
                    'S_released_' + tag + '.TODO = (THROW_SEARCH n_released_' + tag + ') :: (DEPRECATED_HANDLER_EXIT ' + cleanup + '[.RELEASED = true] ' + status + ' ' + saved + ') :: eps',
                    '$constant_bindings(S_released_' + tag + ',S_released_' + tag + '.TODO) = [' + ctx + '.ORIGIN]',
                    '$constant_context_valid(S_released_' + tag + ')', '$call_descriptors_valid(S_released_' + tag + ')',
                    '$parameter_receive_birth(S_released_' + tag + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                    'PhpStep: S_released_' + tag + ' ~> S_resumed_' + tag,
                    '$parameter_receive_birth(S_resumed_' + tag + ',' + owner + ') = (' + birth + ')',
                    '$call_descriptors_valid(S_resumed_' + tag + ')',
                    'S_before_discard_' + tag + ' = $parameter_test_pause(S_resumed_' + tag + ',3,10000)',
                    '$parameter_receive_birth(S_before_discard_' + tag + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                    'PhpStep: S_before_discard_' + tag + ' ~> S_after_discard_' + tag,
                    '$parameter_receive_birth(S_after_discard_' + tag + ',' + owner + ') = (preceivebirth_discarded_' + tag + ')',
                    '~preceivebirth_discarded_' + tag + '.ACTIVE', '$parameter_receive_owner(S_after_discard_' + tag + '.CURRENT) = eps',
                    'S_after_discard_' + tag + '.CONSTCONTEXT = eps', '$call_descriptors_valid(S_after_discard_' + tag + ')',
                    'S_done_' + tag + ' = $drive(S_after_discard_' + tag + ',10000)', 'S_done_' + tag + '.COMPLETION = NORMAL',
                    '$parameter_receive_birth(S_done_' + tag + ',' + owner + ') = (preceivebirth_done_' + tag + ')',
                    '~preceivebirth_done_' + tag + '.ACTIVE', '$call_descriptors_valid(S_done_' + tag + ')']
                continue
            checks += [bind + ' = $parameter_test_pause(' + warn + ',0,10000)',
                bind + '.TODO = ptask_bind_' + tag + ' :: eps',
                '$parameter_test_bind(ptask_bind_' + tag + ') = ((' + call + '.FUNCTION,' + index + '))',
                '$function_at(' + bind + '.FUNCTIONS,' + call + '.FUNCTION) = (' + fn + ')',
                '$default_at(' + fn + '.DEFAULTS,' + index + ') = (' + default + ')',
                bind + '.CONSTCONTEXT = (pconstantcontext_bind_' + tag + ')',
                '$parameter_receive_owner(' + bind + '.CURRENT) = (' + owner + ')',
                '$parameter_receive_birth(' + bind + ',' + owner + ') = (' + birth + ')',
                '$call_descriptors_valid(' + bind + ')']
            if name in ('parameter-owned-shadow', 'parameter-owned-reentry', 'parameter-owned-reentry-nonempty', 'parameter-owned-named-reentry'):
                define = 'S_define_' + tag; config = 'pconfigcall_' + tag; row = 'puserconstant_' + tag; cut = 'preceivecut_' + tag
                checks += [define + ' = $parameter_test_pause(' + warn + ',1,10000)',
                    define + '.TODO = (CONFIG_INVOKE ' + config + ') :: ptask_define_' + tag + '*',
                    '$parameter_receive_define_registration(' + define + ',' + config + ') = [' + cut + ']',
                    cut + '.OWNER = ' + owner, '$parameter_receive_user_frontier(' + define + ',' + cut + '.FRONTIER)',
                    '$parameter_receive_define_registration(' + define + ',' + config + '[.OWNER = (0)]) = eps',
                    '|'+ bind + '.USERCONSTANTS| = $(|' + warn + '.USERCONSTANTS| + 1)',
                    row + ' = ' + bind + '.USERCONSTANTS[|' + warn + '.USERCONSTANTS|]', row + '.RECEIVES = [' + cut + ']',
                    '$parameter_receive_define_metadata_valid(' + bind + ',' + row + ')',
                    '$parameter_receive_cut_valid(' + bind + ',' + birth + ',' + dep + '.SITE,' + row + ',' + cut + ')',
                    '$parameter_receive_ingress(' + bind + ',' + owner + ',|' + bind + '.USERCONSTANTS|) = ' + birth + '.PREFIX',
                    '~$parameter_receive_define_metadata_valid(' + bind + ',' + row + '[.RECEIVES = [' + cut + '[.OWNER = $(' + owner + ' + 99)]]])']
            if name == 'parameter-owned-shadow':
                fact = 'pconstantfact_' + tag; lookup = 'pconstantlookup_' + tag
                checks += [bind + '.RESULT = KNOWN pvalue_' + tag,
                    '$constant_fact_at(pconstantcontext_bind_' + tag + '.FACTS,' + dep + '.SITE) = (' + fact + ')',
                    fact + '.CLASS = pvalueclass_' + tag, fact + '.VALUE = eps', fact + '.LOOKUP = (' + lookup + ')',
                    lookup + '.PREFIX = ' + dep + '.PREFIX',
                    '$parameter_receive_effect_value(' + bind + ',' + birth + ',' + dep + '.SITE)',
                    'S_fake2048 = ' + bind + '[.RESULT = KNOWN (PINT 2048)][.CONSTCONTEXT = (pconstantcontext_bind_' + tag + '[.FACTS = $constant_fact_put(pconstantcontext_bind_' + tag + '.FACTS,' + fact + '[.VALUE = (PINT 2048)][.CLASS = PVSCALAR][.LOOKUP = eps])])]',
                    '~$parameter_receive_effect_value(S_fake2048,' + birth + ',' + dep + '.SITE)',
                    'S_erased = ' + bind + '[.USERCONSTANTS = ' + bind + '.USERCONSTANTS[0:|' + warn + '.USERCONSTANTS|] ++ [' + row + '[.RECEIVES = eps]]]',
                    '~$parameter_default_transfer_valid(S_erased,' + fn + ',' + index + ',pvalue_' + tag + ',pvalueclass_' + tag + ')']
            if 'reentry' in name:
                cached = 'pdefaultcache_' + tag; child = 'preceivebirth_child_' + tag
                checks += ['$default_cache_at(' + bind + '.DEFAULTCACHE,' + default + '.ORIGIN) = (' + cached + ')',
                    cached + '.VALUE = PINT 9', bind + '.PARAMETERRECEIVES = [' + birth + ',' + child + ']',
                    '~' + child + '.ACTIVE', child + '.PARENT = (' + owner + ')',
                    '$default_pending_cache_valid(' + bind + ',' + default + ')']
                for label, mutation in (('active', '.ACTIVE = true'), ('parent', '.PARENT = eps'),
                        ('function', '.FUNCTION = ' + ctx + '.ORIGIN'), ('origin', '.ORIGIN = ' + fn + '.ORIGIN'), ('edge', '.PARENTEDGE = eps')):
                    bad = 'S_bad_child_' + label + '_' + tag
                    checks += [bad + ' = ' + bind + '[.PARAMETERRECEIVES = [' + birth + ',' + child + '[' + mutation + ']]]',
                        '~$default_pending_cache_valid(' + bad + ',' + default + ')']
                checks += ['S_after_' + tag + ' = $drive_steps(' + bind + ',1)', 'S_after_' + tag + '.COMPLETION = BUDGET',
                    '|S_after_' + tag + '.DEFAULTCACHE| = 1', '$default_cache_at(S_after_' + tag + '.DEFAULTCACHE,' + default + '.ORIGIN) = (pdefaultcache_after_' + tag + ')']
                if name == 'parameter-owned-reentry-nonempty':
                    checks += ['pdefaultcache_after_' + tag + ' = ' + cached]
                else:
                    checks += ['pdefaultcache_after_' + tag + '.VALUE = pvalue_' + tag,
                        'pdefaultcache_after_' + tag + '.CLASS = pvalueclass_' + tag]
            if name == 'parameter-owned-type-cache':
                raw = 'S_reject'; wrapped = 'S_wrapped'; formal = 'n_formal'; cache = 'pdefaultcache_reject'
                checks += [bind + '.RESULT = KNOWN (PARRAY n_reject_array)',
                    'PhpStep: ' + bind + ' ~> ' + raw,
                    raw + '.COMPLETION = THROWN "TypeError" preqbytes_reject z_reject',
                    raw + '.CURRENT = (' + call + '[.DEFAULTRECEIVE = eps])',
                    raw + '.CONSTCONTEXT = eps', '$parameter_receive_birth(' + raw + ',' + owner + ') = (preceivebirth_closed)', '~preceivebirth_closed.ACTIVE',
                    '$lookup(' + raw + '.ENV,' + fn + '.SIGNATURE.PARAMETERS[' + index + '].NAME) = (' + formal + ')',
                    raw + '.STORE[' + formal + '] = DEFINED (PARRAY n_reject_array)', '(HCELL ' + formal + ') <- $machine_roots(' + raw + ')',
                    '$default_cache_at(' + raw + '.DEFAULTCACHE,' + default + '.ORIGIN) = (' + cache + ')', cache + '.VALUE = PARRAY n_reject_array',
                    wrapped + ' = $throwable_transition(' + bind + ',' + raw + ')', wrapped + '.COMPLETION = THROWING n_type_error',
                    wrapped + '.STORE[' + formal + '] = DEFINED (PARRAY n_reject_array)',
                    'S_throw_checkpoint = $drive_steps(' + bind + ',1)', 'S_throw_checkpoint.COMPLETION = BUDGET',
                    'S_throw_checkpoint.TODO = (THROW_SEARCH n_checkpoint) :: eps',
                    'S_throw_checkpoint.STORE[' + formal + '] = DEFINED (PARRAY n_reject_array)',
                    '$call_descriptors_valid(S_throw_checkpoint)', '$heap_valid($heap_graph(S_throw_checkpoint))']
                for label, mutation in (('current', '.CURRENT = (' + call + '[.DEFAULTRECEIVE = eps][.ARGC = 1])'),
                        ('close', '.PARAMETERRECEIVES = ' + bind + '.PARAMETERRECEIVES'),
                        ('formal', '.STORE = $set_cell(' + raw + '.STORE,' + formal + ',DEFINED (PINT 2048))')):
                    checks += ['S_bad_reject_' + label + ' = ' + raw + '[' + mutation + ']',
                        '$throwable_continuation(' + bind + ',S_bad_reject_' + label + ').COMPLETION = UNSUPPORTED "unaudited Throwable frame transition"']
                checks += ['S_cached = $parameter_test_pause(S_throw_checkpoint[.COMPLETION = NORMAL],2,10000)',
                    '$parameter_receive_owner(S_cached.CURRENT) = eps',
                    'S_cached.TODO = (DEFAULT_RECEIVE ' + fn + '.ORIGIN ' + index + ') :: eps',
                    '~$parameter_default_error_candidate(S_cached[.TODO = [TYPE_RECEIVE ' + fn + '.ORIGIN ' + index + ']],' + fn + ',' + index + ',PARRAY n_reject_array)',
                    'PhpStep: S_cached ~> S_cached_reject', 'S_cached_reject.COMPLETION = THROWN "TypeError" preqbytes_cached z_cached',
                    '$lookup(S_cached_reject.ENV,' + fn + '.SIGNATURE.PARAMETERS[' + index + '].NAME) = (n_cached_formal)',
                    'S_cached_reject.STORE[n_cached_formal] = DEFINED (PARRAY n_reject_array)']
            checks += ['S_done_' + tag + ' = $drive(' + bind + ',20000)', 'S_done_' + tag + '.COMPLETION = NORMAL',
                '$call_descriptors_valid(S_done_' + tag + ')']
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
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 300)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
