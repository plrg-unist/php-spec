"""Check backed getter type-presence rejections, inherited reads and backing writes."""
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



PREFIX = 'dec $bp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\ndef $bp_replace(eps,pcpath,pcnode) = eps\ndef $bp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*\ndef $bp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $bp_replace(pcoccurrence*,pcpath,pcnode)\n  -- if pcpath_other =/= pcpath\ndec $bp_output(pevent*) : ptbytes\ndef $bp_output(eps) = eps\ndef $bp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $bp_output(pevent*)\ndec $bp_stage(pstate,nat) : bool\ndef $bp_stage(S,0) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("backedpresencechild42")\ndef $bp_stage(S,1) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("backedpresencegrand42")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("backedpresenceparent42::parentread")\ndef $bp_stage(S,2) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $property_hook_context_kind(pcallcontext)\ndef $bp_stage(S,3) = true\n  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\ndef $bp_stage(S,4) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("backedpresencechild42::answer")\ndef $bp_stage(S,5) = true\n  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n  -- if S.RESULT = KNOWN (PINT 300)\ndef $bp_stage(S,6) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("backedpresencegrand42")\ndef $bp_stage(S,n) = false -- otherwise\n\ndec $bp_seek(pstate,nat,nat) : pstate\ndef $bp_seek(S,n_stage,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $bp_stage(S,n_stage) \\/ n = 0\ndef $bp_seek(S,n_stage,n) = $bp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$bp_stage(S,n_stage) /\\ $(n > 0)\ndef $bp_seek(S,n_stage,n) = $bp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\ndef $bp_seek(S,n_stage,n) = S -- otherwise\ndec $bp_after(pstate,pstate) : pstate\ndef $bp_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\ndec $bp_guard(pstate) : bool\ndef $bp_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n'

def reach(name, previous, stage):
    return [f'{name}_found = $bp_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


def slot(s, receiver, value):
    return f'$objectprops_at({s}.OBJECTPROPS,{receiver}) = ([{{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT {value})) }}])'


def prep(s, called, owners, value=200):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            fr'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\ ppropertydesc_{s} = ppropertydesc_child /\ ppropertyhook_{s}.PROPERTY = ppropertydesc_child.ORIGIN /\ pfunction_{s}.SIGNATURE.RETURNS = eps',
            fr'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_child) /\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\ ~$property_hook_backing({s},ppropertyhook_{s}.OBJECT,ppropertydesc_child)',
            slot(s, f'ppropertyhook_{s}.OBJECT', value),
            fr'$heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $bp_guard({s})']


def call(s, called, owners, value=200):
    return [f'PhpStep: {s} ~> {s}_call_raw',
            f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) z_{s}), PROPERTY_HOOK_RESULT ppropertyhook_{s}] ++ ptask_{s}*',
            fr'{s}_call_raw.RESULT = KNOWN PNULL /\ {s}_call_raw.EVENTS = {s}.EVENTS /\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS',
            f'{s}_call = $bp_after({s},{s}_call_raw)',
            fr'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $bp_guard({s}_call)',
            *reach(s+'_entered', s+'_call', 2),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            fr'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            fr'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_child) /\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\ pfunction_{s}.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s})',
            fr'$property_hook_backing({s}_entered,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\ $heap_owners($heap_prune($heap_graph({s}_entered)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $bp_guard({s}_entered)',
            slot(s+'_entered', f'ppropertyhook_{s}.OBJECT', value)]


def answer(s, called, value=200):
    return [*reach(s+'_answer', s+'_entered', 4),
            f'{s}_answer.CURRENT = (pcallcontext_answer_{s})',
            fr'pcallcontext_answer_{s}.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\ pcallcontext_answer_{s}.LEXICAL_CLASS = (porigin_child) /\ pcallcontext_answer_{s}.CALLED_CLASS = (porigin_{called}) /\ pcallcontext_answer_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT) /\ $call_context_valid({s}_answer,pcallcontext_answer_{s},{s}_answer.CVS)',
            slot(s+'_answer', f'ppropertyhook_{s}.OBJECT', value)]


def returned(s, previous, result, slot_value, caller=False):
    return [*reach(s+'_result', previous, 3),
            fr'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\ {s}_result.RESULT = KNOWN (PINT {result}) /\ {s}_result.CURRENT = {"(pcallcontext_read)" if caller else "eps"}',
            slot(s+'_result', f'ppropertyhook_{s}.OBJECT', slot_value),
            fr'$heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\ ~$property_hook_backing({s}_result,ppropertyhook_{s}.OBJECT,ppropertydesc_child) /\ $bp_guard({s}_result)',
            f'PhpStep: {s}_result ~> {s}_base_raw',
            fr'{s}_base_raw.RESULT = {s}_result.RESULT /\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\ {s}_base_raw.TODO = ptask_{s}* /\ {s}_base_raw.EVENTS = {s}_result.EVENTS /\ {s}_base_raw.OBJECTPROPS = {s}_result.OBJECTPROPS',
            f'{s}_base = $bp_after({s}_result,{s}_base_raw)',
            f'$bp_guard({s}_base)']


def rejected(parent_name, child_name, parent_type, child_type, message, line):
    return [
        fr'S.COMPLETION = STATICBYTES ($ptascii("{message}")) {line} /\ S.EVENTS = eps /\ S.OBJECTS = eps /\ S.OBJECTPROPS = eps',
        'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
        fr'pclassdesc_parent.NAME = $ptascii("{parent_name}") /\ pclassdesc_child.NAME = $ptascii("{child_name}") /\ |pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1',
        'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        fr'ppropertydesc_parent.TYPE = {parent_type} /\ ppropertydesc_child.TYPE = {child_type}',
        r'$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
        '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
        '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
        'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
        '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
        '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
        r'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\ pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
        r'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\ pfunction_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\ pfunction_parent.LINE = 3 /\ pfunction_child.LINE = 6',
        '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
        r'$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\ $source_line(metadata_hook) = 6 /\ pclassdesc_child.LINE = 5 /\ S.ERRORORIGIN = eps /\ n_unit = 0 /\ pcpath_child_hook =/= eps',
        r'$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\ $class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
        r'$property_hook_override_backed(S,ppropertydesc_parent) /\ $property_hook_override_backed(S,ppropertydesc_child) /\ ~$property_hook_virtual(S,ppropertydesc_parent) /\ ~$property_hook_virtual(S,ppropertydesc_child)',
        r'~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
        '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED text_presence',
        r'S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps /\ S.ENV = eps /\ $declaration_history_valid(S) /\ $class_links_valid(S)',
    ]


REMOVE_MESSAGE = 'Declaration of BackedMissingChild42::$value::get() must be compatible with BackedTypedParent42::$value::get(): int'
ADD_MESSAGE = 'Type of BackedAddedChild42::$value must be omitted to match the parent definition in class BackedUntypedParent42'
REMOVE = rejected('BackedTypedParent42','BackedMissingChild42','[PTBRANCH ([PTBUILTIN "int"])]','eps',REMOVE_MESSAGE,6) + [
    '$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
    f'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = ($ptascii("{REMOVE_MESSAGE}"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{REMOVE_MESSAGE}")) = ((porigin_child_hook,6))',
    '$property_hook_get_declaration(S,ppropertydesc_child) = ($ptascii("BackedMissingChild42::$value::get()"))',
]
ADD = rejected('BackedUntypedParent42','BackedAddedChild42','eps','[PTBRANCH ([PTBUILTIN "int"])]',ADD_MESSAGE,5) + [
    '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
    f'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = ($ptascii("{ADD_MESSAGE}"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{ADD_MESSAGE}")) = eps',
    '$property_hook_get_declaration(S,ppropertydesc_parent) = ($ptascii("BackedUntypedParent42::$value::get()"))',
]


DERIVED = [
    r'~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = ppropertydesc_parent.TYPE]) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_child,ppropertydesc_parent)',
    r'~$property_hook_missing_return_parent(S,ppropertydesc_parent[.DEFAULT = PROP_NULL],ppropertydesc_child) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL]) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = ppropertydesc_parent.DEFAULT])',
    r'~$property_hook_missing_return_parent(S[.SOURCES = eps],ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_missing_return_parent(S[.CLASSES = eps],ppropertydesc_parent,ppropertydesc_child)',
    r'~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.ORIGIN = ppropertydesc_parent.ORIGIN]) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.NAME = $ptascii("wrong")])',
    r'~$property_hook_missing_return_parent(S,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) /\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)])',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) = ($ptascii("Cannot override final property BackedTypedParent42::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.STATIC = true]) = ($ptascii("Cannot redeclare non static BackedTypedParent42::$value as static BackedMissingChild42::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) = ($ptascii("Cannot redeclare non-readonly property BackedTypedParent42::$value as readonly BackedMissingChild42::$value"))',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED]) = ($ptascii("Access level to BackedMissingChild42::$value must be public (as in class BackedTypedParent42)"))',
    f'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("{ADD_MESSAGE}")) = eps',
    '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
    'porigin_parent_hook = PORIGIN n_unit pcpath_parent_hook',
    'S.SOURCES = pcunit :: pcunit_tail*',
    'pcunit.ID = n_unit',
    'phpType38_parent_virtual = NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent (NScalarInt (INTEGER 7) metadata_parent) metadata_parent',
    'S_parent_virtual = S[.SOURCES = pcunit[.OCCURRENCES = $bp_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_virtual)] :: pcunit_tail*]',
    r'~$property_hook_override_backed(S_parent_virtual,ppropertydesc_parent) /\ ~$property_hook_missing_return_parent(S_parent_virtual,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_child_virtual = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook (NScalarInt (INTEGER 7) metadata_hook) metadata_hook',
    'S_child_virtual = S[.SOURCES = pcunit[.OCCURRENCES = $bp_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_virtual)] :: pcunit_tail*]',
    r'~$property_hook_override_backed(S_child_virtual,ppropertydesc_child) /\ ~$property_hook_missing_return_parent(S_child_virtual,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_child_byref = NPropertyHook phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook',
    'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = $bp_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_byref)] :: pcunit_tail*]',
    '~$property_hook_missing_return_parent(S_child_byref,ppropertydesc_parent,ppropertydesc_child)',
]


def classes():
    clauses = []
    for suffix,name in [('Parent','parent'),('Bridge','bridge'),('Child','child'),('Grand','grand')]:
        clauses += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedPresence{suffix}42"))) = (porigin_{name})',
                    f'$class_at(S.CLASSES,porigin_{name}) = (pclassdesc_{name})']
    return clauses + [
        r'$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
        r'|pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1 /\ pclassdesc_bridge.PROPERTIES = eps /\ pclassdesc_grand.PROPERTIES = eps',
        'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        r'ppropertydesc_parent.TYPE = eps /\ ppropertydesc_child.TYPE = eps /\ $property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
        r'$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
        r'$property_hook_override_backed(S,ppropertydesc_parent) /\ $property_hook_override_backed(S,ppropertydesc_child) /\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_virtual(S,ppropertydesc_parent) /\ ~$property_hook_virtual(S,ppropertydesc_child)',
        r'~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\ $trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps',
        '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
        '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
        '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
        '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
        r'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.OWNER = porigin_child /\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    ]


CV = classes() + ['S_child = S'] + prep('S_child','child',1) + call('S_child','child',2) + answer('S_child','child') + returned('S_child','S_child_answer',213,200)
THIS = classes() + ['S_this = S'] + prep('S_this','grand',3) + [
    'S_this.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
] + call('S_this','grand',3) + answer('S_this','grand') + returned('S_this','S_this_answer',213,200,True)
WRITE = classes() + [
    'S_write = S',
    'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
    '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
    'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
    r'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
    slot('S_write','n_grand',200),
    r'$property_pending_base(pbase_write) /\ S_write.RESULT = KNOWN (PINT 300) /\ z_write = 39 /\ $call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\ $heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\ $bp_guard(S_write)',
    'PhpStep: S_write ~> S_write_raw',
    r'S_write_raw.COMPLETION = NORMAL /\ S_write_raw.RESULT = KNOWN (PINT 300) /\ S_write_raw.EVENTS = S_write.EVENTS /\ S_write_raw.TODO = ptask_write*',
    slot('S_write_raw','n_grand',300),
    'S_written = $bp_after(S_write,S_write_raw)',
    '$bp_guard(S_written)',
    *reach('S_after_write','S_written',6),
] + prep('S_after_write','grand',1,300) + returned('S_after_write','S_after_write',313,300) + [
    'ppropertyhook_S_after_write.OBJECT = n_grand',
    'S_done = $drive_steps(S_after_write_base,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $bp_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $bp_guard(S_done)',
    slot('S_done','n_grand',300),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['remove', 'add', 'cv', 'this', 'write'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_get_hook_type_presence_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'remove': (REMOVE, DERIVED, 0, None),
        'add': (ADD, [], 1, None),
        'cv': (CV, [], 2, 0),
        'this': (THIS, [], 2, 1),
        'write': (WRITE, [], 2, 5),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('backed-get-hook-type-presence-' + ['remove', 'add', 'control'][case_index] + '.php')]
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
    out = Path(tempfile.mkdtemp(prefix='backed-get-hook-type-presence-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $bp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group in ('remove', 'add'):
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $bp_' + name + '() : bool\ndef $bp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $bp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$bp_' + name + '()' for name, _, _ in selections) + ')\n'
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
