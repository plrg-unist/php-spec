#!/usr/bin/env python3
"""Require known absent headers for genuine raw and scoped implicit SET origins."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('property_hook_header_presence_review') / 'authority.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b64 = lambda b: base64.b64encode(b).decode()
PREFIX = '''
var U : program
dec $hpr_without_fact(metadata) : metadata
def $hpr_without_fact(eps) = eps
def $hpr_without_fact((MhookParameterList b) :: metadata_tail) = $hpr_without_fact(metadata_tail)
def $hpr_without_fact(metadataEntry :: metadata_tail) = metadataEntry :: $hpr_without_fact(metadata_tail)
  -- if ~$hook_parameter_entry(metadataEntry)
'''


def fields(fixture):
    checks = ['U = ' + fixture, 'S = $php_run(U,1000,' + json.dumps(b64(bytes(SOURCE))) + ')',
        'S.COMPLETION = NORMAL', 'S.EVENTS = [OUTPUT $ptascii("AUTH|")]', 'S.SOURCES = [pcunit]']
    for tag, name in [('class', 'Class'), ('trait', 'Trait'), ('consumer', 'Consumer')]:
        checks += ['$class_named(S.CLASSNAMES,$ptlc($ptascii("HeaderPresence' + name + '274Review"))) = (porigin_' + tag + ')',
            '$class_at(S.CLASSES,porigin_' + tag + ') = (pclassdesc_' + tag + ')',
            'pclassdesc_' + tag + '.PROPERTIES = [ppropertydesc_' + tag + ']']
    checks += ['porigin_property_trait = ppropertydesc_trait.ORIGIN',
        'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_trait',
        '$property_set_origin(S,ppropertydesc_consumer) = (porigin_scoped)',
        '$property_hook_trait_function(S,ppropertydesc_consumer) = (pfunction_scoped)']
    changes = [('empty', '(MhookParameterList true) :: eps'), ('unknown', 'eps'),
        ('duplicate', '(MhookParameterList false) :: (MhookParameterList false) :: eps'),
        ('conflict', '(MhookParameterList false) :: (MhookParameterList true) :: eps')]
    for tag in ['class', 'trait']:
        checks += ['ppropertydesc_' + tag + '.ORIGIN = PORIGIN n_' + tag + ' pcpath_property_' + tag,
            'pcpath_group_' + tag + ' = pcpath_property_' + tag + '[0:$nabs($( |pcpath_property_' + tag + '| - 2))]',
            'pcpath_hook_' + tag + ' = pcpath_group_' + tag + ' ++ [PCFIELD 4,PCINDEX 0]',
            'porigin_hook_' + tag + ' = PORIGIN n_' + tag + ' pcpath_hook_' + tag,
            '$origin_node(S.SOURCES,porigin_hook_' + tag + ') = (phpType38_' + tag + ')',
            'phpType38_' + tag + ' = NPropertyHook phpType14_' + tag + ' phpType24_' + tag + ' phpType4_' + tag + ' phpType11_' + tag + ' (SEQUENCE eps) phpType39_' + tag + ' metadata_hook_' + tag,
            '$origin_node(S.SOURCES,PORIGIN n_' + tag + ' pcpath_group_' + tag + ') = (NStmtProperty phpType14_group_' + tag + ' phpType24_group_' + tag + ' ABSENT phpType56_group_' + tag + ' (SEQUENCE ([phpType38_' + tag + '])) metadata_group_' + tag + ')',
            '$hook_parameter_facts(metadata_hook_' + tag + ') = [false]',
            '$property_set_origin_body(S,ppropertydesc_' + tag + ') = (porigin_hook_' + tag + ')',
            '$property_set_origin(S,ppropertydesc_' + tag + ') = (porigin_hook_' + tag + ')']
        for kind, facts in changes:
            suffix = tag + '_' + kind
            hook = 'phpType38_' + suffix
            state = 'S_' + suffix
            checks += ['metadata_' + suffix + ' = (' + facts + ') ++ $hpr_without_fact(metadata_hook_' + tag + ')',
                hook + ' = NPropertyHook phpType14_' + tag + ' phpType24_' + tag + ' phpType4_' + tag + ' phpType11_' + tag + ' (SEQUENCE eps) phpType39_' + tag + ' metadata_' + suffix,
                'pcnode_' + suffix + ' = NStmtProperty phpType14_group_' + tag + ' phpType24_group_' + tag + ' ABSENT phpType56_group_' + tag + ' (SEQUENCE ([' + hook + '])) metadata_group_' + tag,
                state + ' = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group_' + tag + ' pcnode_' + suffix + ') :: (PCOCCURRENCE pcpath_hook_' + tag + ' ' + hook + ') :: pcunit.OCCURRENCES]]]',
                '$property_set_origin_body(' + state + ',ppropertydesc_' + tag + ') = (porigin_hook_' + tag + ')',
                '$property_set_origin(' + state + ',ppropertydesc_' + tag + ') = eps']
            if tag == 'trait':
                checks += ['$property_set_origin(' + state + ',ppropertydesc_consumer) = eps',
                    '$property_hook_trait_function(' + state + ',ppropertydesc_consumer) = eps']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': b64(SOURCE.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
