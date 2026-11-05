#!/usr/bin/env python3
"""Saved source/receiver and closed-Generator ownership of a real Closure."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol
import generator_method_factory_protocol as methods

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_generator_closure_factory_cases.json'
ROW = next(row for row in json.loads(CATALOGUE.read_text())['cases']
           if row['id'] == 'generator-closure-closed-owner')
CLOSED = ('S.TODO = (GENERATOR_RESUME pgeneratorop_closed) :: ptask_closed* '
          '-- if S.OBJECTS[pgeneratorop_closed.OBJECT] = GENERATOR pgenerator_closed '
          '-- if pgenerator_closed.PHASE = GENERATOR_CLOSED')
PREFIX = methods.PREFIX + r'''
dec $factory186_closed(pstate) : bool
def $factory186_closed(S) = true -- if CLOSED
def $factory186_closed(S) = false -- otherwise
dec $factory186_seek_closed(pstate, nat) : pstate
def $factory186_seek_closed(S, 0) = S
def $factory186_seek_closed(S, n) = S -- if $(n > 0) /\ $factory186_closed(S)
def $factory186_seek_closed(S, n) = $factory186_seek_closed($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$factory186_closed(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $factory186_seek_closed(S, n) = S -- otherwise
'''.replace('CLOSED', CLOSED)


def at(stage, state):
    return stage.replace('S.', state + '.').replace('(S,', '(' + state + ',')


def render(case, fixture, filename):
    expected = base64.b64decode(ROW['stdout_template_base64'])
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_base,pclassdesc_child,pclassdesc_owner,pclassdesc_derived]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        'pfunction_closure.ORIGIN = PORIGIN 0 pcpath_closure',
        '$origin_node([P.FOLD.SOURCE],pfunction_closure.ORIGIN) = (pcnode_closure)',
        '$anonymous_method_closure_body(pcnode_closure) = (6)',
        '$anonymous_method_scope(P.FOLD.SOURCE,pcpath_closure,pclassdesc_owner.NAME) = ((pcpath_closure,pcpath_method,pfunction_closure.NAME,6))',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory185_seek_paused(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', methods.PAUSED,
        'pgeneratorop_paused.OBJECT = n_generator',
        'pgenerator.CLOSURE = (n_closure)',
        'pgenerator.FRAME = (pframe_generator)',
        'pframe_generator.CONTEXT = (pcallcontext_saved)',
        'pgenerator.FUNCTION = pfunction_closure.ORIGIN',
        'pcallcontext_saved.FUNCTION = pgenerator.FUNCTION',
        'pcallcontext_saved.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext_saved.INSTANCE = (n_closure)',
        'pcallcontext_saved.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
        'pcallcontext_saved.CALLED_CLASS = (pclassdesc_derived.ORIGIN)',
        'pcallcontext_saved.RECEIVER = (n_receiver)',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.RECEIVER = (n_receiver)',
        'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_derived.ORIGIN',
        '(HOBJECT n_closure) <- S.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S.ALLOCATIONS',
        '(HOBJECT n_closure) <- $node_children(S,HOBJECT n_generator)',
        '(HOBJECT n_receiver) <- $node_children(S,HOBJECT n_closure)',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("factory")) = eps',
        '$generator_frame_valid(S,pgenerator,pframe_generator)',
        '$generator_state_valid(S)', '$closure_state_valid(S)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.RECEIVER = eps])])',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.LEXICAL_CLASS = (pclassdesc_derived.ORIGIN)])])',
        '~$generator_frame_valid(S,pgenerator,pframe_generator[.CONTEXT = (pcallcontext_saved[.CALLED_CLASS = (pclassdesc_owner.ORIGIN)])])',
        '~$generator_frame_valid(S,pgenerator[.FUNCTION = pclassdesc_child.ORIGIN],pframe_generator)',
        'S_new_found = $factory182_seek(S,2048)',
        'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', at(methods.FRONT, 'S_new'),
        'pgeneratorop.OBJECT = n_generator', 'pcallcontext = pcallcontext_saved',
        'S_new.ORIGIN = (porigin_new)',
        '$anonymous_new_descriptor(S_new,porigin_new) = (pclassdesc_child)',
        '$call_current_valid(S_new)', '$generator_state_valid(S_new)',
        'S_closed_found = $factory186_seek_closed(S_new,4096)',
        'S_closed_found.COMPLETION = BUDGET',
        'S_closed = S_closed_found[.COMPLETION = NORMAL]', at(CLOSED, 'S_closed'),
        'pgeneratorop_closed.OBJECT = n_generator',
        'pgenerator_closed.CLOSURE = (n_closure)', 'pgenerator_closed.FRAME = eps',
        '(HOBJECT n_closure) <- S_closed.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_closed.ALLOCATIONS',
        '(HOBJECT n_closure) <- $node_children(S_closed,HOBJECT n_generator)',
        '(HOBJECT n_receiver) <- $node_children(S_closed,HOBJECT n_closure)',
        '$heap_owners($heap_graph(S_closed),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_closed),HOBJECT n_receiver) = 1',
        '$generator_state_valid(S_closed)', '$closure_state_valid(S_closed)',
        '$heap_valid($heap_graph(S_closed))',
        'S_split = $drive_steps(S_new,7)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(expected, filename),
        'S_full = $drive_steps(S_new,8199)', 'S_full = S_done',
        '~((HOBJECT n_generator) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$generator_state_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$declaration_history_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({ROW['id']: {'id': ROW['id'], 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(methods.__file__), methods.CATALOGUE,
                  Path(names.__file__)), fixture_renderer=render, runner_flags=('--sl',))
