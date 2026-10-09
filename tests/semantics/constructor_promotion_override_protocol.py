"""Reach promoted Override certificates, property writes and failed publication."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
from constructor_promotion_protocol import PARAM, METHOD, PREFIX

ATTR = '(NAttribute name_param (SEQUENCE eps) metadata_attribute)'
GROUP = '(NAttributeGroup (SEQUENCE ([' + ATTR + '])) metadata_group)'
ATTRS = '(SEQUENCE ([' + GROUP + ']))'
USER = '(NName (BYTES "T3RoZXI=") metadata_attribute)'
USER_ATTRS = ATTRS.replace('name_param', USER)
REPEATED = '(SEQUENCE ([' + GROUP + ', ' + GROUP + ']))'
MIXED = '(SEQUENCE ([(NAttributeGroup (SEQUENCE ([' + ATTR + ', '
MIXED += ATTR.replace('name_param', USER) + '])) metadata_group)]))'
ARG = '(NArg ABSENT (NScalarInt (INTEGER 1) metadata_param) (BOOLEAN false) (BOOLEAN false) metadata_param)'
WITH_ARGUMENT = ATTRS.replace('(SEQUENCE eps)', '(SEQUENCE ([' + ARG + ']))', 1)
HOOK = '(NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) '
HOOK += '(NIdentifier (BYTES "Z2V0") metadata_param) (SEQUENCE eps) '
HOOK += '(NScalarInt (INTEGER 1) metadata_param) metadata_param)'
METHOD_NODE = '(' + METHOD.replace('PARAM', PARAM) + ')'

STAGE = ('S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if $receiving_function(S, porigin) = (pfunction) '
    '-- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc) '
    '-- if $class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc) '
    '-- if pclassdesc.NAME = ptbytes '
    '-- if pcallcontext.RECEIVER = (n_receiver) '
    '-- if $promotion_raw(S, pfunction, 0) = (psraw) '
    '-- if $promotion_descriptor(S, pfunction, 0) = (ppropertydesc) '
    '-- if $lookup(S.ENV, psraw.NAME) = (n_cell)')
CLASS_NODE = '(NStmtClass phpType14_class phpType24_class phpType3_class phpType44_class phpType42_class phpType23_class metadata_class)'
ROLLBACK_STAGE = ('S.TODO = (STMT ' + CLASS_NODE + ') :: ptask_tail* '
    '-- if S.ORIGIN = (porigin) '
    '-- if $origin_node(S.SOURCES, porigin) = (' + CLASS_NODE + ') '
    '-- if $class_at(S.CLASSES, porigin) = (pclassdesc) '
    '-- if pclassdesc.NAME = $ptascii("DeferredOverrideChild20") '
    '-- if ~$declaration_early(S.DECLARATIONS, porigin, PPCLASS)')

OWN = [
    'pclassdesc.PROPERTIES = [ppropertydesc]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psraw.FLAGS = 1 /\\ ~psraw.EXTRA /\\ ~psraw.BYREF /\\ ~psraw.VARIADIC',
    '$promotion_task_valid(S, porigin, 0) /\\ $call_task_valid(S, PROMOTE_PARAMETER porigin 0)',
    '$origin_source(porigin) = PORIGIN n_unit pcpath',
    'porigin_parameter = PORIGIN n_unit (pcpath ++ [PCFIELD 4, PCINDEX 0])',
    'ppropertydesc.ORIGIN = porigin_parameter',
    '$origin_node(S.SOURCES, porigin) = ' + METHOD_NODE,
    '$origin_node(S.SOURCES, porigin_parameter) = (' + PARAM + ')',
    'phpType14_param = ' + ATTRS,
    '$pslower(' + PARAM + ') = PSINPUTATTRIBUTES psraw phpType14_param',
    'ptcontext = $promotion_attribute_context(pfunction)',
    '$psattributes_supported(ptcontext, psraw, phpType14_param)',
    '$promotion_override_property(S, pclassdesc, ppropertydesc)',
    '$promotion_override_parent_layout(S, pclassdesc) = ppropertydesc_parent*',
    '$promotion_override_parent_match(ppropertydesc_parent*, psraw.NAME)',
    '~$promotion_override_parent_match(ppropertydesc_parent*, $ptascii("Value"))',
    '$promotion_override_parent_match([(ppropertydesc[.VISIBILITY = PROPERTY_PRIVATE])], psraw.NAME) = false',
    '$promotion_override_issue(S, pclassdesc, ppropertydesc_parent*, pclassdesc.PROPERTIES) = eps',
    '$psrequiredlater([(PSINPUTATTRIBUTES psraw phpType14_param)]) = (psraw.NAME)',
    '$psrequiredlater([(PSINPUTATTRIBUTES (psraw[.DEFAULT = (NScalarInt (INTEGER 1) metadata_param)]) phpType14_param)]) = eps',
    '$psrequiredlater([(PSINPUTATTRIBUTES (psraw[.VARIADIC = true]) phpType14_param)]) = eps',
    '$psrequiredlater([(PSINPUTATTRIBUTES psraw phpType14_param), (PSINPUTATTRIBUTES (psraw[.NAME = $ptascii("later")]) phpType14_param)]) = ($ptascii("later"))',
    '$psfold_start(ptcontext, [(PSINPUTATTRIBUTES (psraw[.NAME = $ptascii("this")]) ' + USER_ATTRS + ')], { PARAMETERS eps, RETURNS eps, BYREF false }, eps) = PSSDONE (PSERROR ([$psissue(ptcontext[.LINE = psraw.LINE][.POSITION = PTPARAMETER], "fatal", "parameter-this", eps)]))',
    '$pspromotion_raw(ptcontext, PSINPUT (psraw[.EXTRA = true])) = eps',
    '~$psattributes_supported(ptcontext, psraw[.FLAGS = 0], phpType14_param)',
    '~$psattributes_supported(ptcontext, psraw[.EXTRA = true], phpType14_param)',
    '~$pspromotion_override_attribute(ptcontext, ' + REPEATED + ')',
    '~$pspromotion_override_attribute(ptcontext, ' + MIXED + ')',
    '~$pspromotion_override_attribute(ptcontext, ' + WITH_ARGUMENT + ')',
    '$pslower(' + PARAM.replace('phpType37_hooks', '(SEQUENCE ([' + HOOK + ']))') + ') = PSINPUT (psraw[.EXTRA = true])',
    '~$pspromotion_override_attribute(ptcontext[.NAMESPACE = $ptascii("Local")], ' + ATTRS.replace('name_param', '(NName (BYTES "T3ZlcnJpZGU=") metadata_attribute)') + ')',
    '$pspromotion_override_attribute(ptcontext[.NAMESPACE = $ptascii("Local")], phpType14_param)',
    '~$promotion_override_property($promotion_altered(S, porigin_parameter, ' + PARAM.replace('phpType14_param', USER_ATTRS) + '), pclassdesc, ppropertydesc)',
    '~$promotion_override_property($promotion_altered(S, porigin_parameter, ' + PARAM.replace('(INTEGER flags_param)', '(INTEGER 0)') + '), pclassdesc, ppropertydesc)',
    '~$promotion_override_property($promotion_altered(S, porigin, ' + METHOD_NODE.replace('phpType14_param', USER_ATTRS) + '), pclassdesc, ppropertydesc)',
    '~$promotion_task_valid($promotion_altered(S, porigin, ' + METHOD_NODE.replace('phpType14_param', USER_ATTRS) + '), porigin, 0)',
]
for field, value in [('ORIGIN', 'porigin'), ('KEY', '$ptascii("other")'), ('TYPE', 'eps')]:
    OWN += ['ppropertydesc_' + field.lower() + ' = ppropertydesc[.' + field + ' = ' + value + ']',
        'pclassdesc_' + field.lower() + ' = pclassdesc[.PROPERTIES = [ppropertydesc_' + field.lower() + ']]',
        '~$promotion_override_property(S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_' + field.lower() + ')], pclassdesc_' + field.lower() + ', ppropertydesc_' + field.lower() + ')']
OWN += [
    '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_before*)',
    '$property_slot_at(ppropertyslot_before*, ppropertydesc.KEY) = (ppropertyslot)',
    'ppropertyslot.STATE = PROP_INITIAL /\\ ppropertyslot.DECL = (ppropertydesc.ORIGIN)',
    'S.STORE[n_cell] = DEFINED (PINT (+7))',
    'PhpStep: S ~> S_written',
    'S_written.COMPLETION = NORMAL /\\ S_written.TODO = ptask_tail*',
    'S_written.CURRENT = S.CURRENT /\\ S_written.ORIGIN = S.ORIGIN',
    'S_written.ENV = S.ENV /\\ S_written.STORE = S.STORE',
    'S_written.EVENTS = S.EVENTS /\\ S_written.DECLARATIONS = S.DECLARATIONS',
    'S_written.ALLOCATIONS = S.ALLOCATIONS /\\ S_written.CLASSES = S.CLASSES',
    '$objectprops_at(S_written.OBJECTPROPS, n_receiver) = (ppropertyslot_after*)',
    '$property_slot_at(ppropertyslot_after*, ppropertydesc.KEY) = (ppropertyslot_written)',
    'ppropertyslot_written.STATE = PROP_VALUE (DIRECT (PINT (+7)))',
    '$node_children(S_written, HOBJECT n_receiver) = eps',
    '$property_state_valid(S_written) /\\ $call_descriptors_valid(S_written)',
    '$declaration_history_valid(S_written)',
    '$heap_valid($heap_prune($heap_graph(S_written)))',
]

TRAIT = [
    '$promotion_task_valid(S, porigin, 0)',
    '$origin_source(porigin) = PORIGIN n_unit pcpath',
    '$class_method_origin(S.CLASSES, PORIGIN n_unit pcpath) = (pmethoddesc_source)',
    '$class_at(S.CLASSES, pmethoddesc_source.OWNER) = (pclassdesc_source)',
    'pclassdesc_source.KIND = "trait" /\\ pclassdesc_source.NAME = $ptascii("ImportedOverrideCtor20")',
    'porigin_parameter = PORIGIN n_unit (pcpath ++ [PCFIELD 4, PCINDEX 0])',
    'ppropertydesc.ORIGIN = porigin_parameter',
    '$origin_node(S.SOURCES, porigin_parameter) = (' + PARAM + ')',
    'phpType14_param = ' + ATTRS,
    '$ppproperty_desc_at(pclassdesc.PROPERTIES, psraw.NAME) = (ppropertydesc_effective)',
    'ppropertydesc_effective = $trait_data_property(pclassdesc, ppropertydesc)',
    '$promotion_override_property(S, pclassdesc, ppropertydesc_effective)',
    '~$promotion_override_property($promotion_altered(S, porigin_parameter, ' + PARAM.replace('phpType14_param', USER_ATTRS) + '), pclassdesc, ppropertydesc_effective)',
    'ppropertydesc_wrong = ppropertydesc_effective[.ORIGIN = TRAIT_MEMBER_ORIGIN pclassdesc_source.ORIGIN (PORIGIN n_unit (pcpath ++ [PCFIELD 4, PCINDEX 0]))]',
    'pclassdesc_wrong = pclassdesc[.PROPERTIES = [ppropertydesc_wrong]]',
    '~$promotion_override_property(S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_wrong)], pclassdesc_wrong, ppropertydesc_wrong)',
    '$promotion_override_issue(S, pclassdesc, $promotion_override_parent_layout(S, pclassdesc), pclassdesc.PROPERTIES) = eps',
    'S.STORE[n_cell] = DEFINED (PINT (+13))',
    'PhpStep: S ~> S_written',
    'S_written.COMPLETION = NORMAL /\\ S_written.TODO = ptask_tail*',
    'S_written.CLASSES = S.CLASSES /\\ S_written.EVENTS = S.EVENTS',
    '$objectprops_at(S_written.OBJECTPROPS, n_receiver) = (ppropertyslot_after*)',
    '$property_slot_at(ppropertyslot_after*, ppropertydesc_effective.KEY) = (ppropertyslot)',
    'ppropertyslot.DECL = (ppropertydesc_effective.ORIGIN) /\\ ppropertyslot.STATE = PROP_VALUE (DIRECT (PINT (+13)))',
    '$property_state_valid(S_written) /\\ $declaration_history_valid(S_written)',
    '$heap_valid($heap_prune($heap_graph(S_written)))',
]

ROLLBACK = [
    'pclassdesc.LINE = 5 /\\ pclassdesc.PARENT = ($ptascii("DeferredOverrideBase20"))',
    'S.EVENTS = [OUTPUT ($ptascii("BEFORE|"))]',
    '$class_named(S.CLASSNAMES, $ptlc(pclassdesc.NAME)) = eps',
    '$class_link_at(S.LINKEDPARENTS, porigin) = eps',
    'pclassdesc.PROPERTIES = [ppropertydesc]',
    '$promotion_override_property(S, pclassdesc, ppropertydesc)',
    '$eval_compile_fatal_current(S) = eps',
    r'ptbytes_message = pclassdesc.NAME ++ $ptascii("::$value has #[\\Override] attribute, but no matching parent property exists")',
    '$promotion_override_issue(S, pclassdesc, eps, pclassdesc.PROPERTIES) = (ptbytes_message)',
    'PhpStep: S ~> S_failed',
    'S_failed.COMPLETION = STATICBYTES ptbytes_message 5',
    '$runtime_class_rollback(S, S_failed)',
    'S_failed.CLASSSTATICS = S.CLASSSTATICS /\\ S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    'S_failed.EVENTS = S.EVENTS /\\ S_failed.DECLARATIONS = S.DECLARATIONS',
    '$iterator_notice_publication_index(S_failed.DECLARATIONS, porigin, 0) = eps',
    '$class_named(S_failed.CLASSNAMES, $ptlc(pclassdesc.NAME)) = eps',
    'S_failed.SOURCES = S.SOURCES /\\ S_failed.STORE = S.STORE',
    'S_failed.OBJECTS = S.OBJECTS /\\ S_failed.ALLOCATIONS = S.ALLOCATIONS',
    '$declaration_history_valid(S_failed)',
    '$class_links_valid(S_failed) /\\ $class_statics_valid(S_failed)',
    '$heap_valid($heap_prune($heap_graph(S_failed)))',
]

SEEK = r'''
dec $ov_stage(pstate, ptbytes) : bool
def $ov_stage(S, ptbytes) = true -- if STAGE
def $ov_stage(S, ptbytes) = false -- otherwise
dec $ov_rollback_stage(pstate) : bool
def $ov_rollback_stage(S) = true -- if ROLLBACK_STAGE
def $ov_rollback_stage(S) = false -- otherwise
dec $ov_ready(pstate, ptbytes) : bool
def $ov_ready(S, eps) = $ov_rollback_stage(S)
def $ov_ready(S, ptbytes) = $ov_stage(S, ptbytes) -- if ptbytes =/= eps
dec $ov_seek(pstate, ptbytes, nat) : pstate
def $ov_seek(S, ptbytes, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ov_seek(S, ptbytes, n) = S -- if $ov_ready(S, ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ov_seek(S, ptbytes, 0) = S -- if ~$ov_ready(S, ptbytes) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ov_seek(S, ptbytes, n) = $ov_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptbytes, $nabs($(n - 1)))
  -- if ~$ov_ready(S, ptbytes) -- if $(n > 0) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''.replace('ROLLBACK_STAGE', ROLLBACK_STAGE).replace('STAGE', STAGE)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    php, adapter, runner, bridge, worker = (ROOT / name for name in ['.tools/php/bin/php',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        '.tools/php-file.so', 'frontend/worker.php'])
    selected = {'own': (ROOT / 'tests/semantics/constructor-promotion-override-inherited.php', 'OverrideChild20', OWN),
        'trait': (ROOT / 'tests/semantics/constructor-promotion-override-trait.php', 'ImportedOverrideChild20', TRAIT),
        'rollback': (ROOT / 'tests/semantics/constructor-promotion-override-rollback.php', '', ROLLBACK)}
    watched = [Path(__file__), manifest, *modules, php, adapter, runner, bridge, worker,
        ROOT / 'tests/semantics/profile.json', ROOT / 'spec/schema.json',
        ROOT / 'tests/semantics/constructor_promotion_protocol.py',
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py',
        *(row[0] for row in selected.values())]
    catalogue = ROOT / 'tests/semantics/constructor_promotion_override_cases.json'
    retained = json.loads(catalogue.read_bytes())
    assert retained['native_profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    rows = {row['id']: row for row in retained['cases']}
    source_ids = {'own': 'inherited-promoted-override', 'trait': 'raw-trait-import',
        'rollback': 'conditional-parent-deferred'}
    for name, (source, _, _) in selected.items():
        original = rows[source_ids[name]]
        assert source.read_bytes() == original['source'].encode()
        assert sha(source) == original['source_sha256']
    watched.append(catalogue)
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    before = {str(path): sha(path) for path in watched}
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert not status and revision == args.revision, (revision, status)
    out = Path(tempfile.mkdtemp(prefix='promotion-override-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert profile['error_reporting'] == '30719'
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'mode': 'SL', 'cache': False,
        'det': True, 'evaluated': False, 'application_evaluations': 0, 'source_agreements': 0,
        'records': [], 'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC',
        'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}}
    try:
        content = PREFIX + SEEK
        for name, (source, classname, checks) in selected.items():
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / (name + '-frontend'))
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
            finally:
                frontend.close()
            adapter_worker = Worker([str(adapter), str(ROOT)], out / (name + '-adapter'))
            try:
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'], checked
            finally:
                adapter_worker.close()
            target = '$ptascii(' + json.dumps(classname) + ')' if classname else 'eps'
            stage = STAGE.replace('ptbytes', target) if classname else ROLLBACK_STAGE
            content += '\ndec $ov_' + name + '() : bool\ndef $ov_' + name + '() = true\n'
            content += '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            content += '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            content += '  -- if S_found = $ov_seek(S_initial, ' + target + ', 2000)\n'
            content += '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            content += '  -- if S = S_found[.COMPLETION = NORMAL]\n  -- if ' + stage + '\n'
            content += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks)
            content += 'def $ov_' + name + '() = false -- otherwise\n'
            report['records'].append({'id': name, 'source': str(source), 'source_sha256': sha(source),
                'reached_premises': len(checks), 'setup_premises': 6, 'evaluated': False})
        content += '\ndec $main() : bool\ndef $main() = ($ov_own() /\\ $ov_trait() /\\ $ov_rollback())\n'
        fixture = out / 'override.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), reached_premises=sum(row['reached_premises'] for row in report['records']))
        report['passed'] = True
        if not args.prepare_only:
            report['evaluated'] = True
            report['application_evaluations'] = 1
            for row in report['records']:
                row['evaluated'] = True
            report['process'] = process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'override', 120)
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
                and (out / 'override.stdout').read_bytes() == b'true\n' and not (out / 'override.stderr').read_bytes())
            print('override', report['passed'], flush=True)
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
            head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report.get('passed', False) and all(report[key] for key in ['inputs_stable', 'head_stable', 'status_stable'])
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']

if __name__ == '__main__':
    main()
