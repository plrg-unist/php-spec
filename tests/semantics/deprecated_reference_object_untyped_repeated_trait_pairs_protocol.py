#!/usr/bin/env python3
"""Reach repeated raw-trait pair calls and their resolved use-name receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_parented_trait_pairs_protocol as prior
import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_repeated_trait_pairs')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture, source, kind):
    actual = kind == 'actual'
    namespace = 'Ns281TraitActualShortBlock' if actual else 'Ns281TraitImplicitBlockShort'
    old_name = json.dumps(pair.b64((namespace + chr(92) + 'Box281').encode()))
    new_name = json.dumps(pair.b64((namespace.replace('281','282') + chr(92) + 'Box282').encode()))
    checks = []
    for check in prior.fields(fixture, source, kind):
        if check.startswith('U = '):
            checks.append(check)
            continue
        check = check.replace(old_name,new_name).replace('input281sb','input282sb')
        check = check.replace('pclassdesc_consumer.PARENT = (ptbytes_parent)','pclassdesc_consumer.PARENT = eps')
        check = check.replace('[ppropertyslot_pad,ppropertyslot_get]','[ppropertyslot_get]')
        check = check.replace('[ppropertyslot_pad,ppropertyslot_after]','[ppropertyslot_after]')
        check = check.replace('|$trait_plan(S_get,pclassdesc_consumer).TRAITS| = 1',
                              '$trait_plan(S_get,pclassdesc_consumer) = {TRAITS ([pclassdesc_trait.NAME,pclassdesc_trait.NAME]), PRECEDENCES eps, ALIASES eps}')
        if actual: check = check.replace('$default_parameter_line(S_set,pfunction_set_clone.ORIGIN,0) = 6',
                                          '$default_parameter_line(S_set,pfunction_set_clone.ORIGIN,0) = 7')
        if any(name in check for name in ('ptbytes_parent','porigin_parent','pclassdesc_parent','ppropertydesc_pad',
                                         'ppropertyslot_pad','S_parent_','S_bad_link','S_wrong_link')):
            continue
        checks.append(check)
    at = next(i for i,c in enumerate(checks) if c.startswith('S_set = $pair_pause'))
    checks[at:at] = [
        '$trait_fetch(S_get,$trait_plan(S_get,pclassdesc_consumer).TRAITS,eps) = TRAITFETCHED ([pclassdesc_trait])',
        '$property_hook_pair_untyped_import(S_get,pclassdesc_consumer,ppropertydesc,[pclassdesc_trait])',
        '$ppproperty_desc_at(pclassdesc_trait.PROPERTIES,ppropertydesc.NAME) = (ppropertydesc)',
        '$property_hook_pair_export(S_get,pclassdesc_consumer,ppropertydesc) = (ppropertydesc)',
        '$property_hook_pair_import(S_get,pclassdesc_consumer,ppropertydesc,ppropertydesc)',
        '~$property_hook_pair_untyped_import(S_get,pclassdesc_consumer,ppropertydesc,eps)',
        '~$property_hook_pair_untyped_import(S_get,pclassdesc_consumer,ppropertydesc,[pclassdesc_trait,pclassdesc_trait])',
        'pclassdesc_consumer.ORIGIN = PORIGIN n_source pcpath_consumer',
        '$origin_node(S_get.SOURCES,pclassdesc_consumer.ORIGIN) = (NStmtClass phpType14_consumer phpType24_consumer phpType3_consumer ABSENT phpType42_consumer (SEQUENCE ([statement_use])) metadata_consumer)',
        'statement_use = NStmtTraitUse (SEQUENCE ([name_first,name_second])) (SEQUENCE eps) metadata_use',
        'name_first = NName (BYTES text_first) metadata_first',
        'name_second = NName (BYTES text_second) metadata_second',
        '$base64(text_first) = $ptascii("Pair282")',
        '$base64(text_second) = $ptascii("' + ('Alias282' if actual else 'Pair282') + '")',
        '$code_at(S_get.CODE,n_source) = (pcode_unit)',
        '$code_name(pcode_unit.NAMES,pcpath_consumer ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) = ((pclassdesc_trait.NAME,eps))',
        '$code_name(pcode_unit.NAMES,pcpath_consumer ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 1]) = ((pclassdesc_trait.NAME,eps))',
        'pfunction_set.LINE = ' + ('6' if actual else '9'),
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('implicit','actual'))
    args = parser.parse_args(); actual = args.kind == 'actual'
    source = SOURCE_DIR / ('aliased-repeat-trait-actual-short-get-block-set.php' if actual else 'repeated-trait-implicit-block-get-short-set.php')
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
        pause = pair.PAUSE.replace('275','282')
        target = 'PROPERTY_HOOK_TARGET' if actual else 'PROPERTY_SET_TARGET'
        pause = pause.replace('pcallcontext.TARGET = ' + target + ' ppropertyhook\n  -- if S.TODO = (STMT statement)', 'pcallcontext.TARGET = ' + target + ' ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        if actual: pause = pause.replace('$ptascii("value")','$ptascii("input282sb")')
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
