#!/usr/bin/env python3
"""Anonymous NEW after a real method Generator restores its suspended frame."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/generator_method_factory_cases.json'
ROW = next(row for row in json.loads(CATALOGUE.read_text())['cases']
           if row['id'] == 'named-generator-resumed-receiver')
FRONT = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if $generator_context_operation(S,pcallcontext) = (pgeneratorop)')
PAUSED = ('S.TODO = (GENERATOR_RESUME pgeneratorop_paused) :: ptask_paused* '
          '-- if S.OBJECTS[pgeneratorop_paused.OBJECT] = GENERATOR pgenerator '
          '-- if pgenerator.PHASE = GENERATOR_PAUSED')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT) + r'''
dec $factory185_paused(pstate) : bool
def $factory185_paused(S) = true -- if PAUSED
def $factory185_paused(S) = false -- otherwise
dec $factory185_seek_paused(pstate, nat) : pstate
def $factory185_seek_paused(S, 0) = S
def $factory185_seek_paused(S, n) = S -- if $(n > 0) /\ $factory185_paused(S)
def $factory185_seek_paused(S, n) = $factory185_seek_paused($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$factory185_paused(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $factory185_seek_paused(S, n) = S -- otherwise
'''.replace('PAUSED', PAUSED)


def render(case, fixture, filename):
    expected = base64.b64decode(ROW['stdout_template_base64'])
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_base,pclassdesc_child,pclassdesc_owner,pclassdesc_derived]',
        '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc)',
        '$origin_node([P.FOLD.SOURCE],pmethoddesc.FUNCTION.ORIGIN) = (pcnode_method)',
        '$anonymous_method_factory_node(pcnode_method)',
        'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory185_seek_paused(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PAUSED,
        'pgeneratorop_paused.OBJECT = n_generator',
        'pgenerator.VALUE = (pvalue_cached)',
        '$string_bytes(pvalue_cached) = ($ptascii("PAUSE"))',
        'S.CURRENT = eps', 'S.FRAMES = eps',
        'pgenerator.FRAME = (pframe_generator)',
        'pframe_generator.CONTEXT = (pcallcontext_saved)',
        'pgenerator.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_saved.FUNCTION = pgenerator.FUNCTION',
        'pcallcontext_saved.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
        'pcallcontext_saved.CALLED_CLASS = (pclassdesc_derived.ORIGIN)',
        'pcallcontext_saved.RECEIVER = (n_receiver)',
        'pcallcontext_saved.TARGET = METHOD_TARGET n_receiver pgenerator.FUNCTION',
        'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_derived.ORIGIN',
        '(HOBJECT n_receiver) <- S.ALLOCATIONS',
        '(HOBJECT n_receiver) <- $node_children(S,HOBJECT n_generator)',
        '$lookup(S.ENV,$ptascii("owner")) = eps',
        '$generator_frame_valid(S,pgenerator,pframe_generator)',
        '$generator_state_valid(S)', '$call_descriptors_valid(S)',
        '$class_state_valid(S)', '$declaration_history_valid(S)',
        '$heap_valid($heap_graph(S))',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.RECEIVER = eps])])',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.LEXICAL_CLASS = (pclassdesc_derived.ORIGIN)])])',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.CALLED_CLASS = (pclassdesc_owner.ORIGIN)])])',
        '~$generator_frame_valid(S,pgenerator[.FUNCTION = pclassdesc_child.ORIGIN],pframe_generator)',
        'S_new_found = $factory182_seek(S,2048)',
        'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]',
        FRONT.replace('S.', 'S_new.').replace('(S,', '(S_new,'),
        'pgeneratorop.OBJECT = n_generator',
        'pcallcontext = pcallcontext_saved',
        'S_new.OBJECTS[n_generator] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING',
        'pgenerator_running.FRAME = eps',
        'S_new.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_new,porigin_new) = (pclassdesc_child)',
        '$function_generator(S_new,pmethoddesc.FUNCTION)',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$generator_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_split = $drive_steps(S_new,7)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(expected, filename),
        'S_full = $drive_steps(S_new,8199)', 'S_full = S_done',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_generator) <- S_done.ALLOCATIONS)',
        '$generator_state_valid(S_done)', '$class_state_valid(S_done)',
        '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({ROW['id']: {'id': ROW['id'], 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
