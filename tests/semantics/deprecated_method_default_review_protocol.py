#!/usr/bin/env python3
"""Check named method default history, cache identity and real receiver owners."""
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
SOURCE = Path(__file__).with_name('deprecated_method_default_review')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()
PREFIX += r'''
dec $method_default_review_ready(pstate,nat) : bool
def $method_default_review_ready(S,0) = true
  -- if S.TODO = (DEFAULT_BIND porigin n) :: ptask_tail*
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
def $method_default_review_ready(S,1) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin n) :: ptask_tail*
  -- if $class_method_origin(S.CLASSES,porigin) = (pmethoddesc)
  -- if $default_at(pmethoddesc.FUNCTION.DEFAULTS,n) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $method_default_review_ready(S,2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $method_default_review_ready(S,n) = false -- otherwise
dec $method_default_review_pause(pstate,nat,nat) : pstate
def $method_default_review_pause(S,n_mode,n) = S -- if $method_default_review_ready(S,n_mode)
def $method_default_review_pause(S,n_mode,n) = $method_default_review_pause(S_next[.COMPLETION = NORMAL],n_mode,n_next)
  -- if ~$method_default_review_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $method_default_review_pause(S,n_mode,n) = S -- otherwise
dec $method_default_review_frontier_ready(ptask*) : bool
def $method_default_review_frontier_ready((ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*) = true
  -- if $parameter_receive_frontier(perrorcall.RESUME) =/= eps
def $method_default_review_frontier_ready(ptask*) = false -- otherwise
dec $method_default_review_frontier_pause(pstate,nat) : pstate
def $method_default_review_frontier_pause(S,n) = S -- if $method_default_review_frontier_ready(S.TODO)
def $method_default_review_frontier_pause(S,n) = $method_default_review_frontier_pause(S_next[.COMPLETION = NORMAL],n_next)
  -- if ~$method_default_review_frontier_ready(S.TODO)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if n_next = $nabs($(n - 1))
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $method_default_review_frontier_pause(S,n) = S -- otherwise
dec $method_default_review_publication(pstate,porigin,nat) : nat?
def $method_default_review_publication(S,porigin,n) = (n)
  -- if $(n <= |S.DECLARATIONS|)
  -- if $constant_callable_published(S.DECLARATIONS[0:n],porigin)
def $method_default_review_publication(S,porigin,n) = $method_default_review_publication(S,porigin,$(n + 1))
  -- if $(n < |S.DECLARATIONS|)
  -- if ~$constant_callable_published(S.DECLARATIONS[0:n],porigin)
def $method_default_review_publication(S,porigin,n) = eps -- otherwise
'''


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name in ('receiver-retirement', 'cache-scope', 'raw-trait-frontier', 'builtin-frontier'):
            path = SOURCE / (name + '.php'); tag = name.replace('-', '_')
            parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            start = 'S_start_' + tag; warn = 'S_warn_' + tag; bind = 'S_bind_' + tag
            call = 'pcallcontext_' + tag; birth = 'preceivebirth_' + tag; owner = 'n_owner_' + tag
            method = 'pmethoddesc_' + tag; fn = 'pfunction_' + tag; default = 'pdefault_' + tag
            site = 'porigin_site_' + tag; lexical = 'porigin_lexical_' + tag; called = 'porigin_called_' + tag
            siteopt = site + '_option?'; lexicalopt = lexical + '_option?'; calledopt = called + '_option?'
            error = 'perrorcall_' + tag; dep = 'pdeprecatedconstant_' + tag; index = 'n_index_' + tag
            tail = 'pdeclcalls_' + tag; value = 'pvalue_' + tag; after = 'S_after_' + tag
            if name.endswith('-frontier'):
                frontier = 'preceivefrontier_' + tag; config = 'S_config_' + tag; cfg = 'pconfigcall_' + tag
                cut = 'preceivecut_' + tag; order = 'preceiveorder_' + tag
                checks += ['U_' + tag + ' = ' + checked['fixture'],
                    start + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')', start + '.COMPLETION = BUDGET',
                    warn + ' = $method_default_review_frontier_pause(' + start + '[.COMPLETION = NORMAL],10000)',
                    warn + '.COMPLETION = NORMAL', warn + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_warn_' + tag + '*',
                    '$parameter_receive_frontier(' + error + '.RESUME) = (' + frontier + ')',
                    '$parameter_receive_frontier_site(' + frontier + ') = (' + site + ')',
                    warn + '.CURRENT = (' + call + ')', '$class_method_origin(' + warn + '.CLASSES,' + call + '.FUNCTION) = (' + method + ')',
                    fn + ' = ' + method + '.FUNCTION', '$parameter_receive_owner(' + warn + '.CURRENT) = (' + owner + ')',
                    '$parameter_receive_birth(' + warn + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                    '$parameter_receive_method_entry(' + warn + ',' + birth + ')',
                    '$parameter_receive_frontier_valid(' + warn + ',' + birth + ',' + call + '.LEXICAL_CLASS,' + frontier + ')',
                    '$default_origin_at(' + fn + '.DEFAULTS,' + site + ') = (' + default + ')',
                    '$parameter_receive_order(' + warn + ',' + birth + ',' + default + '.ORIGIN,' + call + '.LEXICAL_CLASS,eps) = (' + order + ')',
                    order + '.EFFECTS = [' + site + ']',
                    '~$parameter_receive_user_frontier(' + warn + ',' + frontier + ')',
                    '~$parameter_receive_user_leaf(' + warn + ',' + birth + ',' + site + ')',
                    '$call_descriptors_valid(' + warn + ')',
                    config + ' = $method_default_review_pause(' + warn + ',2,10000)',
                    config + '.COMPLETION = NORMAL', config + '.TODO = (CONFIG_INVOKE ' + cfg + ') :: ptask_config_' + tag + '*',
                    cut + ' = {OWNER ' + owner + ', INDEX 1, FRONTIER ' + frontier + ', CAUSE $declaration_cause(' + config + ')}',
                    cut + '.CAUSE.CALLS[1:|' + birth + '.CAUSE.CALLS|] = ' + birth + '.CAUSE.CALLS',
                    '$parameter_receive_registration(' + config + ') = eps',
                    '~$parameter_receive_cut_source(' + config + ',' + cut + ')']
                checks += [('$parameter_receive_raw_trait(' + warn + ',' + birth + ',' + site + ',' + call + '.LEXICAL_CLASS)')
                    if name.startswith('raw-trait') else ('$parameter_receive_builtin_deprecated(' + warn + ',' + birth + ',' + site + ')')]
                continue
            checks += ['U_' + tag + ' = ' + checked['fixture'],
                start + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')', start + '.COMPLETION = BUDGET',
                warn + ' = $dep_pause(' + start + '[.COMPLETION = NORMAL],10000)',
                warn + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_warn_' + tag + '*',
                error + '.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep, dep + '.COPIED = eps',
                warn + '.CURRENT = (' + call + ')', '$class_method_origin(' + warn + '.CLASSES,' + call + '.FUNCTION) = (' + method + ')',
                fn + ' = ' + method + '.FUNCTION', '$parameter_receive_owner(' + warn + '.CURRENT) = (' + owner + ')',
                '$parameter_receive_birth(' + warn + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                birth + '.CAUSE.CALLS = (porigin_function_' + tag + ',' + siteopt + ',' + lexicalopt + ',' + calledopt + ') :: ' + tail,
                'porigin_function_' + tag + ' = ' + fn + '.ORIGIN', siteopt + ' = (' + site + ')',
                lexicalopt + ' = (' + lexical + ')', calledopt + ' = (' + called + ')', lexical + ' = ' + method + '.OWNER',
                '$parameter_method_invocation(' + warn + ',' + fn + ',' + birth + '.CAUSE.CALLS,' + birth + '.PUBLICATION)',
                '$parameter_receive_deprecated_entry(' + warn + ',' + birth + ')',
                '$deprecated_constant_parameter_ast(' + warn + ',' + dep + '.SITE)', '$task_nodes(' + error + '.RESUME) = eps',
                '$class_constant_default_location(' + warn + ',' + dep + '.SITE) = eps',
                '$call_descriptors_valid(' + warn + ')', '$heap_valid($heap_graph(' + warn + '))',
                '~$parameter_method_invocation(' + warn + ',' + fn + ',' + birth + '.CAUSE.CALLS,0)',
                '~$parameter_receive_deprecated_entry(' + warn + ',' + birth + '[.CALLSITE = (' + fn + '.ORIGIN)])',
                '~$parameter_receive_deprecated_entry(' + warn + ',' + birth + '[.FUNCTION = ' + lexical + '])',
                bind + ' = $method_default_review_pause(' + warn + ',0,10000)',
                bind + '.TODO = (DEFAULT_BIND ' + fn + '.ORIGIN ' + index + ') :: eps',
                bind + '.RESULT = KNOWN ' + value, '$default_at(' + fn + '.DEFAULTS,' + index + ') = (' + default + ')',
                '$parameter_receive_birth(' + bind + ',' + owner + ') = (' + birth + ')',
                '$default_bind_task_valid(' + bind + ',' + fn + '.ORIGIN,' + index + ')',
                '$class_constant_default_location(' + bind + ',' + dep + '.SITE) = eps',
                '~$default_bind_task_valid(' + bind + ',' + lexical + ',' + index + ')',
                '$machine_roots(' + bind + '[.PARAMETERRECEIVES = eps]) = $machine_roots(' + bind + ')',
                'PhpStep: ' + bind + ' ~> ' + after, after + '.COMPLETION = NORMAL',
                '$lookup(' + after + '.ENV,' + fn + '.SIGNATURE.PARAMETERS[' + index + '].NAME) = (n_formal_' + tag + ')',
                after + '.STORE[n_formal_' + tag + '] = DEFINED ' + value,
                '(HCELL n_formal_' + tag + ') <- $machine_roots(' + after + ')',
                '$parameter_receive_owner(' + after + '.CURRENT) = eps',
                '$parameter_receive_birth(' + after + ',' + owner + ') = (preceivebirth_closed_' + tag + ')',
                '~preceivebirth_closed_' + tag + '.ACTIVE', '$call_descriptors_valid(' + after + ')',
                'S_checkpoint_' + tag + ' = $drive_steps(' + bind + ',1)',
                'S_checkpoint_' + tag + '.COMPLETION = BUDGET',
                'S_checkpoint_' + tag + '.CURRENT = ' + after + '.CURRENT',
                'S_checkpoint_' + tag + '.STORE = ' + after + '.STORE',
                'S_checkpoint_' + tag + '.PARAMETERRECEIVES = ' + after + '.PARAMETERRECEIVES',
                'S_checkpoint_' + tag + '.DEFAULTCACHE = ' + after + '.DEFAULTCACHE',
                '$call_descriptors_valid(S_checkpoint_' + tag + ')',
                'S_resumed_' + tag + ' = $drive(S_checkpoint_' + tag + '[.COMPLETION = NORMAL],20000)',
                'S_resumed_' + tag + '.COMPLETION = NORMAL']
            if name == 'receiver-retirement':
                checks += [called + ' =/= ' + lexical, call + '.INSTANCE = eps', call + '.RECEIVER = (n_receiver)',
                    '$lookup($global_table_view(' + bind + ').ENV,$ptascii("receiver")) = (n_source)',
                    bind + '.STORE[n_source] = DEFINED PNULL', '(HOBJECT n_receiver) <- ' + bind + '.ALLOCATIONS',
                    '(HOBJECT n_receiver) <- $call_context_roots(' + bind + '.CURRENT)',
                    '$default_cache_at(' + after + '.DEFAULTCACHE,' + default + '.ORIGIN) = eps',
                    'S_done_retirement = $drive(' + after + ',10000)', 'S_done_retirement.COMPLETION = NORMAL',
                    '~((HOBJECT n_receiver) <- S_done_retirement.ALLOCATIONS)',
                    '$parameter_receive_birth(S_done_retirement,' + owner + ') = (preceivebirth_closed_' + tag + ')',
                    '$heap_valid($heap_graph(S_done_retirement))', '$call_descriptors_valid(S_done_retirement)']
            else:
                cache = 'pdefaultcache_shared'; hit = 'S_cached'; hitcall = 'pcallcontext_cached'
                checks += [called + ' = ' + lexical,
                    'porigin_bad_called? = (' + fn + '.ORIGIN)',
                    'pdeclcalls_bad_called = (porigin_function_' + tag + ',' + siteopt + ',' + lexicalopt + ',porigin_bad_called?) :: ' + tail,
                    '~$parameter_method_invocation(' + warn + ',' + fn + ',pdeclcalls_bad_called,' + birth + '.PUBLICATION)',
                    '$default_cache_at(' + after + '.DEFAULTCACHE,' + default + '.ORIGIN) = (' + cache + ')', cache + '.VALUE = ' + value,
                    '~$default_caches_valid(' + after + ',[' + cache + '[.ORIGIN = ' + fn + '.ORIGIN]])',
                    hit + ' = $method_default_review_pause(' + after + ',1,10000)',
                    hit + '.CURRENT = (' + hitcall + ')', hitcall + '.FUNCTION = ' + fn + '.ORIGIN',
                    hitcall + '.LEXICAL_CLASS = (' + lexical + ')', hitcall + '.CALLED_CLASS = (porigin_child)',
                    'porigin_child =/= ' + lexical, '$parameter_receive_owner(' + hit + '.CURRENT) = eps',
                    hit + '.TODO = (DEFAULT_RECEIVE ' + fn + '.ORIGIN ' + index + ') :: eps',
                    '$default_cache_at(' + hit + '.DEFAULTCACHE,' + default + '.ORIGIN) = (' + cache + ')',
                    '$parameter_default_recipient(' + hit + ',' + fn + ')', '$call_descriptors_valid(' + hit + ')',
                    '$method_default_review_publication(' + hit + ',porigin_child,0) = (n_child_publication)',
                    '$(n_child_publication > 0)', 'n_before_child = $nabs($(n_child_publication - 1))',
                    '$parameter_callable_function_published(' + hit + ',' + fn + ',n_before_child)',
                    '~$constant_callable_published(' + hit + '.DECLARATIONS[0:n_before_child],porigin_child)',
                    'pdeclcause_hit = $declaration_cause(' + hit + ')',
                    '$parameter_method_invocation(' + hit + ',' + fn + ',pdeclcause_hit.CALLS,|' + hit + '.DECLARATIONS|)',
                    '~$parameter_method_invocation(' + hit + ',' + fn + ',pdeclcause_hit.CALLS,n_before_child)',
                    '~$call_current_valid(' + hit + '[.CURRENT = (' + hitcall + '[.CALLED_CLASS = (' + lexical + ')])])',
                    'porigin_bad_lexical? = (porigin_child)',
                    'pdeclcalls_bad_lexical = (porigin_function_' + tag + ',' + siteopt + ',porigin_bad_lexical?,' + calledopt + ') :: ' + tail,
                    '~$parameter_method_invocation(' + warn + ',' + fn + ',pdeclcalls_bad_lexical,' + birth + '.PUBLICATION)',
                    'S_done_scope = $drive(' + hit + ',20000)', 'S_done_scope.COMPLETION = NORMAL',
                    '$call_descriptors_valid(S_done_scope)', '$heap_valid($heap_graph(S_done_scope))']
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
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), *SOURCE.glob('*.php'), *(ROOT / path for path in (
        'spec/semantics/modules.json', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/profile.json', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
