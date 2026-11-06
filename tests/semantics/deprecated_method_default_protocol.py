#!/usr/bin/env python3
"""Check scoped default callback cuts, reentry cache writes and rejected roots."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_parameter_default_protocol import PREFIX
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_global_constant')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def prepare(out):
    selected = ('method-owned-reentry', 'method-owned-reentry-nonempty',
        'method-owned-type-cache', 'method-owned-type-nonempty', 'method-owned-local-exit-cancel')
    cases = json.loads((SOURCE / 'cases.json').read_text())
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
                start + ' = $php_run(U_' + tag + ',0,' + json.dumps(b64(bytes(path))) + ')', start + '.COMPLETION = BUDGET',
                warn + ' = $dep_pause(' + start + '[.COMPLETION = NORMAL],10000)', warn + '.COMPLETION = NORMAL',
                warn + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ' + tail,
                error + '.RESUME = DEPRECATED_CONSTANT_RESULT ' + dep, dep + '.COPIED = eps',
                warn + '.CONSTCONTEXT = (' + ctx + ')', warn + '.CURRENT = (' + call + ')',
                '$parameter_receive_owner(' + warn + '.CURRENT) = (' + owner + ')',
                '$parameter_receive_birth(' + warn + ',' + owner + ') = (' + birth + ')', birth + '.ACTIVE',
                '$receiving_function(' + warn + ',' + call + '.FUNCTION) = (' + fn + ')',
                '$default_origin_at(' + fn + '.DEFAULTS,' + dep + '.SITE) = (' + default + ')', index + ' = ' + default + '.INDEX',
                '$parameter_receive_method_entry(' + warn + ',' + birth + ')',
                '$deprecated_constant_parameter_ast(' + warn + ',' + dep + '.SITE)',
                '$task_nodes(' + error + '.RESUME) = eps', '$call_descriptors_valid(' + warn + ')',
                '$class_constant_default_location(' + warn + ',' + dep + '.SITE) = eps',
                '~$parameter_method_invocation(' + warn + ',' + fn + ',' + birth + '.CAUSE.CALLS,0)',
                '~$parameter_receive_method_entry(' + warn + ',' + birth + '[.CALLSITE = eps])',
                '~$parameter_receive_method_entry(' + warn + ',' + birth + '[.CAUSE = ' + birth + '.CAUSE[.CALLS = eps]])']
            if name == 'method-owned-local-exit-cancel':
                marker = 'S_marker_' + tag; cleanup = 'pdestructioncleanup_' + tag; saved = 'ptask_saved_' + tag + '*'
                marker_task = 'DEPRECATED_HANDLER_EXIT ' + cleanup + ' z_status_' + tag + ' ' + saved
                checks += [marker + ' = $dep_throw_pause(' + warn + ',10000)',
                    marker + '.TODO = (THROW_SEARCH n_throw_' + tag + ') :: (' + marker_task + ') :: eps',
                    '$constant_bindings(' + marker + ',' + marker + '.TODO) = [' + ctx + '.ORIGIN]',
                    '$constant_context_valid(' + marker + ')', '$call_descriptors_valid(' + marker + ')',
                    'S_done_' + tag + ' = $drive(' + marker + ',10000)', 'S_done_' + tag + '.COMPLETION = NORMAL',
                    '$parameter_receive_birth(S_done_' + tag + ',' + owner + ') = (preceivebirth_closed_' + tag + ')',
                    '~preceivebirth_closed_' + tag + '.ACTIVE', '$call_descriptors_valid(S_done_' + tag + ')']
                continue
            if 'reentry' in name:
                config = 'S_config_' + tag; cfg = 'pconfigcall_' + tag; cut = 'preceivecut_' + tag
                checks += [config + ' = $parameter_test_pause(' + warn + ',1,10000)',
                    config + '.TODO = (CONFIG_INVOKE ' + cfg + ') :: ptask_config_' + tag + '*',
                    '$parameter_receive_define_registration(' + config + ',' + cfg + ') = [' + cut + ']',
                    cut + '.OWNER = ' + owner, cut + '.INDEX = 1',
                    '$parameter_receive_user_frontier(' + config + ',' + cut + '.FRONTIER)',
                    '$parameter_receive_user_leaf(' + config + ',' + birth + ',' + dep + '.SITE)',
                    cut + '.CAUSE.CALLS[1:|' + birth + '.CAUSE.CALLS|] = ' + birth + '.CAUSE.CALLS',
                    '$parameter_receive_cut_source(' + config + ',' + cut + ')',
                    '~$parameter_receive_cut_source(' + config + ',' + cut + '[.INDEX = 0])',
                    '~$parameter_receive_cut_source(' + config + ',' + cut + '[.CAUSE = ' + cut + '.CAUSE[.CALLS = ' + cut + '.CAUSE.CALLS[0:1]]])']
            checks += [bind + ' = $parameter_test_pause(' + warn + ',0,10000)', bind + '.COMPLETION = NORMAL',
                bind + '.TODO = (DEFAULT_BIND ' + fn + '.ORIGIN ' + index + ') :: eps',
                bind + '.RESULT = KNOWN (PARRAY n_array_' + tag + ')',
                '$class_constant_default_location(' + bind + ',' + dep + '.SITE) = eps', '$call_descriptors_valid(' + bind + ')']
            if 'reentry' in name:
                cached = 'pdefaultcache_' + tag; child = 'preceivebirth_child_' + tag; after = 'S_after_' + tag
                checks += ['$default_cache_at(' + bind + '.DEFAULTCACHE,' + default + '.ORIGIN) = (' + cached + ')',
                    cached + '.VALUE = PINT 9', bind + '.PARAMETERRECEIVES = [' + birth + ',' + child + ']',
                    '~' + child + '.ACTIVE', child + '.PARENT = (' + owner + ')', '$default_pending_cache_valid(' + bind + ',' + default + ')',
                    '$parameter_receive_cache_child(' + bind + ',' + birth + ',' + owner + ',' + child + ')']
                for mutation in ('.ACTIVE = true', '.PARENT = eps', '.ORIGIN = ' + fn + '.ORIGIN', '.PARENTEDGE = eps'):
                    checks += ['~$parameter_receive_cache_child(' + bind + ',' + birth + ',' + owner + ',' + child + '[' + mutation + '])']
                checks += [after + ' = $drive_steps(' + bind + ',1)', after + '.COMPLETION = BUDGET',
                    '$default_cache_at(' + after + '.DEFAULTCACHE,' + default + '.ORIGIN) = (pdefaultcache_after_' + tag + ')']
                checks += [('pdefaultcache_after_' + tag + ' = ' + cached) if name.endswith('nonempty') else
                    ('pdefaultcache_after_' + tag + '.VALUE = PARRAY n_array_' + tag)]
            else:
                raw = 'S_reject_' + tag; formal = 'n_formal_' + tag; checkpoint = 'S_throw_' + tag
                checks += ['PhpStep: ' + bind + ' ~> ' + raw, raw + '.COMPLETION = THROWN "TypeError" preqbytes_reject_' + tag + ' z_reject_' + tag,
                    raw + '.CURRENT = (' + call + '[.DEFAULTRECEIVE = eps])', raw + '.CONSTCONTEXT = eps',
                    '$parameter_receive_birth(' + raw + ',' + owner + ') = (preceivebirth_closed_' + tag + ')', '~preceivebirth_closed_' + tag + '.ACTIVE',
                    '$lookup(' + raw + '.ENV,' + fn + '.SIGNATURE.PARAMETERS[' + index + '].NAME) = (' + formal + ')',
                    raw + '.STORE[' + formal + '] = DEFINED (PARRAY n_array_' + tag + ')', '(HCELL ' + formal + ') <- $machine_roots(' + raw + ')',
                    '$throwable_continuation(' + bind + ',' + raw + ').COMPLETION = THROWN "TypeError" preqbytes_reject_' + tag + ' z_reject_' + tag,
                    checkpoint + ' = $drive_steps(' + bind + ',1)', checkpoint + '.COMPLETION = BUDGET',
                    checkpoint + '.TODO = (THROW_SEARCH n_checkpoint_' + tag + ') :: eps',
                    checkpoint + '.STORE[' + formal + '] = DEFINED (PARRAY n_array_' + tag + ')',
                    '$call_descriptors_valid(' + checkpoint + ')', '$heap_valid($heap_graph(' + checkpoint + '))']
                if name.endswith('cache'):
                    checks += ['$default_cache_at(' + raw + '.DEFAULTCACHE,' + default + '.ORIGIN) = (pdefaultcache_reject_' + tag + ')',
                        'pdefaultcache_reject_' + tag + '.VALUE = PARRAY n_array_' + tag]
                else:
                    checks += ['$default_cache_at(' + raw + '.DEFAULTCACHE,' + default + '.ORIGIN) = eps',
                        'hgraph_' + tag + ' = $heap_graph(' + checkpoint + ')',
                        '(HARRAY n_array_' + tag + ') <- $heap_reach(hgraph_' + tag + '.ROOTS,eps,hgraph_' + tag + '.EDGES)']
                for label, mutation in (('close', '.PARAMETERRECEIVES = ' + bind + '.PARAMETERRECEIVES'),
                        ('formal', '.STORE = $set_cell(' + raw + '.STORE,' + formal + ',DEFINED (PINT 2048))')):
                    checks += ['$throwable_continuation(' + bind + ',' + raw + '[' + mutation + ']).COMPLETION = UNSUPPORTED "unaudited Throwable frame transition"']
            checks += ['S_done_' + tag + ' = $drive(' + bind + ',20000)', 'S_done_' + tag + '.COMPLETION = NORMAL',
                '$call_descriptors_valid(S_done_' + tag + ')']
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + c + '\n' if c.startswith('PhpStep:') else '  -- if ' + c + '\n' for c in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), ROOT / 'tests/semantics/deprecated_parameter_default_protocol.py',
        ROOT / 'tests/semantics/deprecated_global_constant_protocol.py', *modules,
        SOURCE / 'cases.json', SOURCE / 'hashes.json', *(SOURCE / p for p in json.loads((SOURCE / 'hashes.json').read_text())),
        *(ROOT / p for p in ('spec/semantics/modules.json', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
            'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
