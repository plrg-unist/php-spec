"""Check virtual getter type-presence rejections and untyped inherited dispatch."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
byte_expr = lambda value: '[' + ','.join(str(byte) for byte in value) + ']'



PREFIX = 'dec $vp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\ndef $vp_replace(eps,pcpath,pcnode) = eps\ndef $vp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*\ndef $vp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $vp_replace(pcoccurrence*,pcpath,pcnode)\n  -- if pcpath_other =/= pcpath\ndec $vp_output(pevent*) : ptbytes\ndef $vp_output(eps) = eps\ndef $vp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $vp_output(pevent*)\ndec $vp_stage(pstate,nat) : bool\ndef $vp_stage(S,0) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("presencechild41")\ndef $vp_stage(S,1) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("presencegrand41")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("presenceparent41::parentread")\ndef $vp_stage(S,2) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $property_hook_context_kind(pcallcontext)\ndef $vp_stage(S,3) = true\n  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\ndef $vp_stage(S,4) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("presencechild41::answer")\ndef $vp_stage(S,n) = false -- otherwise\n\ndec $vp_seek(pstate,nat,nat) : pstate\ndef $vp_seek(S,n_stage,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $vp_stage(S,n_stage) \\/ n = 0\ndef $vp_seek(S,n_stage,n) = $vp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$vp_stage(S,n_stage) /\\ $(n > 0)\ndef $vp_seek(S,n_stage,n) = $vp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\ndef $vp_seek(S,n_stage,n) = S -- otherwise\ndec $vp_after(pstate,pstate) : pstate\ndef $vp_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\ndec $vp_guard(pstate) : bool\ndef $vp_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n'

def reach(name, previous, stage):
    return [f'{name}_found = $vp_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']

def prep(s, called, owners):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            f'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\\ ppropertydesc_{s} = ppropertydesc_child /\\ ppropertyhook_{s}.PROPERTY = ppropertydesc_child.ORIGIN /\\ pfunction_{s}.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
            f'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_child) /\\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\\ $objectprops_at({s}.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps)',
            f'$heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vp_guard({s})']

def call(s, called, owners):
    return [f'PhpStep: {s} ~> {s}_call_raw',
            f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) z_{s}), PROPERTY_HOOK_RESULT ppropertyhook_{s}] ++ ptask_{s}*',
            f'{s}_call_raw.RESULT = KNOWN PNULL /\\ {s}_call_raw.EVENTS = {s}.EVENTS /\\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS',
            f'{s}_call = $vp_after({s},{s}_call_raw)',
            f'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vp_guard({s}_call)',
            *reach(s+'_entered', s+'_call', 2),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            f'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            f'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\\ pfunction_{s}.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s})',
            f'~$property_hook_backing({s}_entered,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\\ $objectprops_at({s}_entered.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps) /\\ $heap_owners($heap_prune($heap_graph({s}_entered)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vp_guard({s}_entered)']

def answer(s, called):
    return [*reach(s+'_answer', s+'_entered', 4),
            f'{s}_answer.CURRENT = (pcallcontext_answer_{s})',
            f'pcallcontext_answer_{s}.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer_{s}.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_{s}.CALLED_CLASS = (porigin_{called}) /\\ pcallcontext_answer_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT) /\\ $call_context_valid({s}_answer,pcallcontext_answer_{s},{s}_answer.CVS)']

def returned(s, previous, value, caller):
    return [*reach(s+'_result', previous, 3),
            f'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ {s}_result.RESULT = KNOWN ({value}) /\\ {s}_result.CURRENT = {"(pcallcontext_read)" if caller else "eps"}',
            f'$objectprops_at({s}_result.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps) /\\ $heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\\ $vp_guard({s}_result)',
            f'PhpStep: {s}_result ~> {s}_base_raw',
            f'{s}_base_raw.RESULT = {s}_result.RESULT /\\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\\ {s}_base_raw.TODO = ptask_{s}* /\\ {s}_base_raw.EVENTS = {s}_result.EVENTS',
            f'{s}_base = $vp_after({s}_result,{s}_base_raw)',
            f'$vp_guard({s}_base)']

def rejected(parent_name, child_name, parent_type, child_type, message, line):
    return [
        f'S.COMPLETION = STATICBYTES ($ptascii("{message}")) {line} /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
        'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
        f'pclassdesc_parent.NAME = $ptascii("{parent_name}") /\\ pclassdesc_child.NAME = $ptascii("{child_name}") /\\ |pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1',
        'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        f'ppropertydesc_parent.TYPE = {parent_type} /\\ ppropertydesc_child.TYPE = {child_type}',
        f'ppropertydesc_parent.DEFAULT = {"PROP_NULL" if parent_type == "eps" else "PROP_UNINITIALIZED"} /\\ ppropertydesc_child.DEFAULT = {"PROP_NULL" if child_type == "eps" else "PROP_UNINITIALIZED"}',
        '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
        '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
        'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
        '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
        '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
        'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
        'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ pfunction_parent.LINE = 3 /\\ pfunction_child.LINE = 6',
        '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
        '$source_line(metadata_hook) = 6 /\\ pclassdesc_child.LINE = 5 /\\ S.ERRORORIGIN = eps /\\ n_unit = 0 /\\ pcpath_child_hook =/= eps',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
        '$property_hook_override_virtual(S,ppropertydesc_parent) /\\ $property_hook_override_virtual(S,ppropertydesc_child) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
        '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
        '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED text_presence',
        'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ $declaration_history_valid(S) /\\ $class_links_valid(S)',
    ]

REMOVE_MESSAGE = 'Declaration of PresenceMissingChild41::$value::get() must be compatible with PresenceTypedParent41::$value::get(): int'
ADD_MESSAGE = 'Type of PresenceAddedChild41::$value must be omitted to match the parent definition in class PresenceUntypedParent41'
REMOVE = rejected('PresenceTypedParent41','PresenceMissingChild41','[PTBRANCH ([PTBUILTIN "int"])]','eps',REMOVE_MESSAGE,6) + [
    '$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
    f'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = ($ptascii("{REMOVE_MESSAGE}"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{REMOVE_MESSAGE}")) = ((porigin_child_hook,6))',
    '$property_hook_get_declaration(S,ppropertydesc_child) = ($ptascii("PresenceMissingChild41::$value::get()"))',
]
ADD = rejected('PresenceUntypedParent41','PresenceAddedChild41','eps','[PTBRANCH ([PTBUILTIN "int"])]',ADD_MESSAGE,5) + [
    '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
    f'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = ($ptascii("{ADD_MESSAGE}"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{ADD_MESSAGE}")) = eps',
    '$property_hook_get_declaration(S,ppropertydesc_parent) = ($ptascii("PresenceUntypedParent41::$value::get()"))',
]

DERIVED = [
    '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) /\\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = ppropertydesc_parent.TYPE])',
    '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_UNINITIALIZED]) /\\ ~$property_hook_missing_return_parent(S,ppropertydesc_child,ppropertydesc_parent)',
    '~$property_hook_missing_return_parent(S[.SOURCES = eps],ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_missing_return_parent(S[.CLASSES = eps],ppropertydesc_parent,ppropertydesc_child)',
    'porigin_parent = pclassdesc_parent.ORIGIN',
    'porigin_child = pclassdesc_child.ORIGIN',
    '~$property_hook_missing_return_parent(S[.LINKEDPARENTS = [CLASSLINK porigin_parent (SOURCE_PARENT porigin_child)]],ppropertydesc_parent,ppropertydesc_child)',
    '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) /\\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)])',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) = ($ptascii("Cannot override final property PresenceTypedParent41::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.STATIC = true]) = ($ptascii("Cannot redeclare non static PresenceTypedParent41::$value as static PresenceMissingChild41::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) = ($ptascii("Cannot redeclare non-readonly property PresenceTypedParent41::$value as readonly PresenceMissingChild41::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED]) = ($ptascii("Access level to PresenceMissingChild41::$value must be public (as in class PresenceTypedParent41)"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{ADD_MESSAGE}")) = eps',
    '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
    'porigin_parent_hook = PORIGIN n_unit pcpath_parent_hook',
    'S.SOURCES = pcunit :: pcunit_tail*',
    'pcunit.ID = n_unit',
    'phpType38_parent_backed = NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") metadata_parent) (NIdentifier (BYTES "dmFsdWU=") metadata_parent) metadata_parent) metadata_parent',
    'S_parent_backed = S[.SOURCES = pcunit[.OCCURRENCES = $vp_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_backed)] :: pcunit_tail*]',
    '$property_hook_override_backed(S_parent_backed,ppropertydesc_parent) /\\ ~$property_hook_missing_return_parent(S_parent_backed,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_child_byref = NPropertyHook phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook',
    'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = $vp_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_byref)] :: pcunit_tail*]',
    '~$property_hook_missing_return_parent(S_child_byref,ppropertydesc_parent,ppropertydesc_child)',
]

def classes():
    clauses = []
    for suffix,name in [('Parent','parent'),('Bridge','bridge'),('Child','child'),('Grand','grand')]:
        clauses += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("Presence{suffix}41"))) = (porigin_{name})',
                    f'$class_at(S.CLASSES,porigin_{name}) = (pclassdesc_{name})']
    return clauses + [
        '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
        '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps',
        'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ ppropertydesc_parent.DEFAULT = PROP_NULL /\\ ppropertydesc_child.DEFAULT = PROP_NULL',
        '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
        '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|) /\\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
        '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps',
        '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
        '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
        '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
        'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    ]

CV = classes() + ['S_child = S'] + prep('S_child','child',1) + call('S_child','child',2) + answer('S_child','child') + returned('S_child','S_child_answer','PINT 13',False) + [
    'S_done = $drive_steps(S_child_base,10000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ $vp_output(S_done.EVENTS) = EXPECTED_OUTPUT /\\ $objectprops_at(S_done.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = (eps) /\\ $vp_guard(S_done)',
]
THIS = classes() + ['S_this = S'] + prep('S_this','grand',3) + [
    'S_this.CURRENT = (pcallcontext_read)',
    'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
] + call('S_this','grand',3) + answer('S_this','grand') + returned('S_this','S_this_answer','PINT 13',True) + [
    'S_done = $drive_steps(S_this_base,10000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ $vp_output(S_done.EVENTS) = EXPECTED_OUTPUT /\\ $objectprops_at(S_done.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = (eps) /\\ $vp_guard(S_done)',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['remove', 'add', 'cv', 'this'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'virtual_get_hook_type_presence_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'remove': (REMOVE, DERIVED, 0, None),
        'add': (ADD, [], 1, None),
        'cv': (CV, [], 2, 0),
        'this': (THIS, [], 2, 1),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('virtual-get-hook-type-presence-' + ['remove', 'add', 'control'][case_index] + '.php')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
               HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='virtual-get-hook-type-presence-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum((1 if args.group in ('remove', 'add') else 5) + len(row[1]) for row in selections)
    report = {'revision': revision, 'group': args.group, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, (source, case) in enumerate(zip(sources, cases)):
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, cases):
            name, clauses, negatives = selection
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $vp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group in ('remove', 'add'):
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $vp_' + name + '() : bool\ndef $vp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $vp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$vp_' + name + '()' for name, _, _ in selections) + ')\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
