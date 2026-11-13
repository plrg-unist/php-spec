#!/usr/bin/env python3
"""Check same-name plain-parent pair authority, child slots and first writes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
import deprecated_reference_object_untyped_set_backed_class_pairs_protocol as backed
import deprecated_reference_object_untyped_automatic_short_set_class_pairs_protocol as automatic
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_same_name_parent_class_pairs')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture, source, kind):
    actual = kind == 'actual'
    prior = automatic if actual else backed
    old_number = '286' if actual else '285'
    old_namespace = 'Ns286ClassActualAutomaticShortSet' if actual else 'Ns285ClassImplicitSetBacked'
    namespace = 'Ns288SameNameParentClass' + kind.title() + 'Pair'
    quoted = lambda value: json.dumps(pair.b64(value.encode()))
    checks = []
    for check in prior.fields(fixture, source, kind):
        if check.startswith(('U = ', 'S_start = ')):
            checks.append(check)
            continue
        check = check.replace(quoted(old_namespace + chr(92) + 'Box' + old_number), quoted(namespace + chr(92) + 'Box288'))
        check = check.replace(old_number, '288')
        if check == 'pclassdesc.PARENT = eps':
            check = 'pclassdesc.PARENT = (ptbytes_parent)'
        check = check.replace('([ppropertyslot_get])', '([ppropertyslot_anchor,ppropertyslot_get])')
        check = check.replace('([ppropertyslot_after])', '([ppropertyslot_anchor,ppropertyslot_after])')
        if check.startswith('pfunction_get.LINE = '):
            check = 'pfunction_get.LINE = ' + ('18' if actual else '9')
        elif check.startswith('pfunction_get.ENDLINE = '):
            check = 'pfunction_get.ENDLINE = ' + ('21' if actual else '12')
        elif check.startswith('pfunction_set.LINE = '):
            check = 'pfunction_set.LINE = ' + ('12' if actual else '13')
        elif check.startswith('pfunction_set.ENDLINE = '):
            check = 'pfunction_set.ENDLINE = ' + ('17' if actual else '18')
        elif check.startswith('$default_parameter_line(S_set,porigin_set,0) = '):
            check = '$default_parameter_line(S_set,porigin_set,0) = 13'
        check = check.replace('$psline(metadata_param) = 9', '$psline(metadata_param) = 13')
        check = check.replace('pcpath_param) = ((9,false))', 'pcpath_param) = ((13,false))')
        checks.append(check)
    at = checks.index('pclassdesc.PARENT = (ptbytes_parent)') + 1
    checks[at:at] = [
        'ptbytes_parent = $base64(' + quoted(namespace + chr(92) + 'Parent288') + ')',
        '$class_named(S_get.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$class_at(S_get.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.NAME = ptbytes_parent', 'pclassdesc_parent.KIND = "class"',
        'pclassdesc_parent.PARENT = eps', '~pclassdesc_parent.READONLY',
        'pclassdesc_parent.METHODS = eps', 'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_parenttag]',
        '$class_link_at(S_get.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_parent)',
        '$property_hook_pair_source_headers(S_get,pclassdesc,pclassdesc_parent)',
        '$property_hook_pair_plain_parent(S_get,[ppropertydesc_anchor,ppropertydesc_parenttag])',
        '$ppproperty_desc_at($property_info_layout(S_get,porigin_parent,|S_get.CLASSES|),$ptascii("tag")) = (ppropertydesc_parenttag)',
        '$property_hook_pair_linked(S_get,pclassdesc,$ptascii("tag"))',
    ]
    at = checks.index('S_set = $pair_pause(S_get,"set",30000)')
    checks[at:at] = [
        '$source_unit(S_get.SOURCES,n_source) = (pcunit)', 'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$property_slot_descriptor(S_get,n_object,ppropertyslot_anchor) = (ppropertydesc_anchor)',
        'ppropertyslot_anchor.DECL = (ppropertydesc_anchor.ORIGIN)',
        'ppropertyslot_anchor.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'ppropertydesc_anchor.ORIGIN = PORIGIN n_source pcpath_anchor',
        '$property_declaring_class(S_get.CLASSES,PORIGIN n_source pcpath_anchor) = (porigin_parent)',
        '$property_layout(S_get,porigin_owner,|S_get.CLASSES|) = [ppropertydesc_anchor,ppropertydesc]',
        '$property_hook_pair_own_parented(S_get,ppropertydesc)',
        '$property_default_state(S_get,ppropertydesc_parenttag) = (PROP_VALUE (DIRECT (PINT 99)))',
        '$property_hook_reference_plain_parent(S_get,ppropertydesc_parenttag,ppropertydesc)',
        '$property_hook_child_own_slot(S_get,ppropertydesc_parenttag,ppropertydesc)',
        '$property_layout_parent(S_get,[ppropertydesc_anchor,ppropertydesc_parenttag],[ppropertydesc]) = [ppropertydesc_anchor]',
        '$property_hook_pair_over_ordinary(S_get,ppropertydesc_parenttag,ppropertydesc)',
        '~$property_hook_parent_match(S_get,ppropertydesc,(ppropertydesc_parenttag))',
        '~$property_hook_pair_over_ordinary(S_get,ppropertydesc_anchor,ppropertydesc)',
        '~$property_hook_pair_over_ordinary(S_get,ppropertydesc_parenttag[.FINAL = true],ppropertydesc)',
        '~$property_hook_child_own_slot(S_get,ppropertydesc_parenttag,ppropertydesc_parenttag)',
        '$property_layout_parent(S_get,[ppropertydesc_anchor,ppropertydesc_parenttag],[ppropertydesc_parenttag]) = [ppropertydesc_anchor,ppropertydesc_parenttag]',
        '~$property_hook_child_own_slot(S_get,ppropertydesc,ppropertydesc)',
        '$property_layout_parent(S_get,[ppropertydesc],[ppropertydesc]) = [ppropertydesc]',
        'pclassdesc_parented_decl = pclassdesc_parent[.PARENT = (pclassdesc.NAME)]',
        'S_parented_decl = S_get[.CLASSES = [pclassdesc_parented_decl,pclassdesc]]',
        '~$property_hook_child_own_slot(S_parented_decl,ppropertydesc_parenttag,ppropertydesc)',
        '$property_layout_parent(S_parented_decl,[ppropertydesc_anchor,ppropertydesc_parenttag],[ppropertydesc]) = [ppropertydesc_anchor,ppropertydesc_parenttag]',
        'pclassdesc_bad_rawparent = pclassdesc_parent[.ORIGIN = pclassdesc.ORIGIN]',
        'S_bad_rawparent = S_get[.CLASSES = [pclassdesc_bad_rawparent,pclassdesc]]',
        '~$property_hook_child_own_slot(S_bad_rawparent,ppropertydesc_parenttag,ppropertydesc)',
        '~$property_hook_pair_own_parented(S_get,ppropertydesc_anchor)',
        '~$property_hook_parent_match(S_get,ppropertydesc,eps)',
        'S_no_link = S_get[.LINKEDPARENTS = eps]',
        '~$property_hook_pair_own_parented(S_no_link,ppropertydesc)',
        '$property_hook_pair_origins(S_no_link,ppropertydesc) = eps',
        'S_wrong_link = S_get[.LINKEDPARENTS = [CLASSLINK porigin_owner (SOURCE_PARENT porigin_owner)]]',
        '$property_hook_pair_origins(S_wrong_link,ppropertydesc) = eps',
        '$origin_node(S_get.SOURCES,pclassdesc.ORIGIN) = (NStmtClass phpType14_owner phpType24_owner phpType3_owner phpType44_parent phpType42_owner phpType23_owner metadata_owner)',
        'phpType44_parent =/= ABSENT',
        'pchheader = {KIND "class",NAME pclassdesc.NAME,ABSTRACT pclassdesc.ABSTRACT,FINAL pclassdesc.FINAL,READONLY pclassdesc.READONLY,PARENT pclassdesc.PARENT,INTERFACES pclassdesc.INTERFACES,BODY phpType23_owner}',
        'P_seed = $ppstart(n_source,PROGRAM eps,$base64(' + quoted(str(source)) + '))',
        'P_compile = P_seed[.ENV = pfunction_set.ENV][.FOLD = P_seed.FOLD[.SOURCE = pcunit]]',
        '$pphook_pair_nodes(P_compile,pcpath_get,ppropertydesc,pchheader) = [phpType38_get,phpType38_set]',
        '$pphook_pair_nodes(P_compile,pcpath_set,ppropertydesc,pchheader) = [phpType38_get,phpType38_set]',
        '$pphook_pair_backed(P_compile,pcpath_get,ppropertydesc,pchheader)',
        '~$pphook_pair_virtual(P_compile,pcpath_get,ppropertydesc,pchheader)',
        '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_group) = (statement_group)',
        'statement_group = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group phpType37_group metadata_group',
        'PPROPERTIES P_group ppropertydesc_group* = $ppproperty_hook_group(P_compile,pcpath_group,statement_group,eps,pchheader)',
        'P_group.COMPLETION = PPCNORMAL', 'ppropertydesc_group* = [ppropertydesc]',
        '$function_at(P_group.FUNCTIONS,porigin_get) = (pfunction_get_compiler)',
        '$function_at(P_group.FUNCTIONS,porigin_set) = (pfunction_set_compiler)',
        'pfunction_get_compiler.SIGNATURE = pfunction_get.SIGNATURE',
        'pfunction_set_compiler.SIGNATURE = pfunction_set.SIGNATURE',
        'pfunction_get_compiler.BODY = pfunction_get.BODY', 'pfunction_set_compiler.BODY = pfunction_set.BODY',
        'P_abrupt = $pplocate($ppunsupported(P_compile,"compiler288 control"),pcpath_group,$source_line(metadata_group))',
        '$ppproperty_hook_group(P_abrupt,pcpath_group,statement_group,eps,pchheader) = PPROPERTIES P_abrupt eps',
    ]
    for field, change in [('private','[.VISIBILITY = PROPERTY_PRIVATE]'),('setter','[.SETVISIBILITY = (PROPERTY_PRIVATE)]'),
                          ('static','[.STATIC = true]'),('readonly','[.READONLY = true]'),('final','[.FINAL = true]'),
                          ('name','[.NAME = $ptascii("forged")]')]:
        checks += ['$pphook_pair_nodes(P_compile,pcpath_get,ppropertydesc' + change + ',pchheader) = eps']
    for change in ['[.KIND = "trait"]','[.READONLY = true]']:
        checks += ['$pphook_pair_nodes(P_compile,pcpath_get,ppropertydesc,pchheader' + change + ') = eps']
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('implicit','actual'))
    args = parser.parse_args(); actual = args.kind == 'actual'
    source = SOURCE_DIR / ('same-name-parent-class-' + args.kind + '-pair.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), Path(backed.__file__), Path(automatic.__file__), source, *modules, *(ROOT / p for p in (
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
        pause = pair.PAUSE.replace('275','288')
        if actual:
            pause = pause.replace('pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
            pause = pause.replace('$ptascii("value")','$ptascii("incoming288")')
        else:
            pause = pause.replace('pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
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
