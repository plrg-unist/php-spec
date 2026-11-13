#!/usr/bin/env python3
"""Reach constant GET entries backed by block SET and resume the first write."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
import deprecated_reference_object_untyped_trait_pairs_protocol as prior
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_trait_pairs')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture, source, kind):
    actual = kind == 'actual'
    old = 'Ns280TraitActualShortShort' if actual else 'Ns280TraitImplicitShortBlock'
    new = 'Ns283TraitActualSetBacked' if actual else 'Ns283TraitImplicitSetBacked'
    quoted = lambda value: json.dumps(pair.b64(value.encode()))
    checks = []
    for check in prior.fields(fixture, source, kind):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for name in ('Box', 'Pair'):
            check = check.replace(quoted(old + chr(92) + name + '280'), quoted(new + chr(92) + name + '283'))
        check = check.replace('input280ss', 'incoming283')
        check = check.replace('expression_set', '(SEQUENCE statement_set*)')
        if 'z_set_rhs' in check or 'PORIGIN n_source pfunction_set.BODY)' in check:
            continue
        if check.startswith('pfunction_get.LINE = '):
            check = 'pfunction_get.LINE = ' + ('13' if actual else '5')
        elif check.startswith('pfunction_get.ENDLINE = '):
            check = 'pfunction_get.ENDLINE = ' + ('16' if actual else '8')
        elif check.startswith('pfunction_set.LINE = '):
            check = 'pfunction_set.LINE = ' + ('5' if actual else '9')
        elif check.startswith('pfunction_set.ENDLINE = '):
            check = 'pfunction_set.ENDLINE = ' + ('12' if actual else '14')
        if actual:
            check = check.replace('pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0]', 'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 1]')
            check = check.replace('pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]', 'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 0]')
            check = check.replace('= 10', '= 6').replace('((10,false))', '((6,false))')
            check = check.replace('>= 5 /\\ z_get_expr <= 8', '>= 13 /\\ z_get_expr <= 16')
            check = check.replace('>= 5 /\\ z_get_arrow <= 8', '>= 13 /\\ z_get_arrow <= 16')
        else:
            check = check.replace('ppropertydesc.DEFAULT = PROP_NULL', 'ppropertydesc.DEFAULT = PROP_STORED porigin_default')
            check = check.replace('ppropertyslot_get.STATE = PROP_VALUE (DIRECT PNULL)', 'ppropertyslot_get.STATE = PROP_VALUE (DIRECT (PINT 17))')
        checks.append(check)
    at = next(i for i, c in enumerate(checks) if c.startswith('S_set = $pair_pause'))
    checks[at:at] = [
        '$origin_node(S_get.SOURCES,porigin_get) = (phpType38_get)',
        '$origin_node(S_get.SOURCES,porigin_set) = (phpType38_set)',
        '$hook_pair_untyped_trait_headers(phpType38_get,phpType38_set,ppropertydesc.NAME)',
        '~$hook_body_backed(expression_get,ppropertydesc.NAME)',
        '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc.NAME)',
        '$hook_pair_untyped_trait_bodies(expression_get,SEQUENCE statement_set*,ppropertydesc.NAME)',
        'phpType39_quiet_block = SEQUENCE ([NStmtReturn (NScalarInt (INTEGER 0) eps) eps])',
        '~$hook_pair_untyped_trait_bodies(expression_get,phpType39_quiet_block,ppropertydesc.NAME)',
        'S_get_code = S_get[.FUNCTIONS = [pfunction_get[.CODE.EXPRESSIONS = eps],pfunction_set]]',
        '$property_hook_pair_origins(S_get_code,ppropertydesc) = eps',
        '$property_hook_trait_pair_functions(S_get_code,ppropertydesc_imported) = eps',
    ]
    if actual:
        checks[at + 2:at + 2] = [
            '~$hook_pair_untyped_parameter_headers(phpType38_get,phpType38_set,ppropertydesc.NAME)',
            '$hook_pair_untyped_trait_set_backed_headers(phpType38_get,phpType38_set,ppropertydesc.NAME)',
        ]
    checks += [
        'S_after_global = $global_table_view(S_after)',
        '$lookup(S_after_global.ENV,$ptascii("before283execution")) = (n_before)',
        '$lookup(S_after_global.ENV,$ptascii("stored283execution")) = (n_stored)',
        'S_after.STORE[n_before] = DEFINED ' + ('PNULL' if actual else '(PINT 17)'),
        'S_after.STORE[n_stored] = DEFINED (PBOOL true)',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('implicit','actual'))
    args = parser.parse_args(); actual = args.kind == 'actual'
    source = SOURCE_DIR / ('set-backed-trait-actual-short-get-block-set.php' if actual else 'set-backed-trait-implicit-short-get-block-set.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(pair.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php','frontend/SourcePrinter.php',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/profile.json','.tools/php/bin/php','.tools/php-file.so',
        '_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report = {'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'kind':args.kind,'mode':'fixture-SL','passed':False}
    try:
        frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        try:
            parsed = frontend.request({'op':'parse','source':pair.b64(source.read_bytes())}); assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'],source,args.kind); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
        pause = pair.PAUSE.replace('275','283').replace('pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        if actual: pause = pause.replace('$ptascii("value")','$ptascii("incoming283")')
        (out / 'protocol.watsup').write_text(pair.PREFIX + pair.SELECTED + pause + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally: (out / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
    if not report['passed']: print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed']; print('pass',report['premises'])


if __name__ == '__main__': main()
