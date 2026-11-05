#!/usr/bin/env python3
"""Raw anonymous owner reservation and composed trait/Stringable runtime state."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_owner_declaration_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
FRONT = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext)')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)


def reservation(fixture, filename):
    return ['P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
            r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
            'P.CLASSES = [pclassdesc_interface,pclassdesc_owner,pclassdesc_child,pclassdesc_after]',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            'pclassdesc_owner.INTERFACES = [$ptascii("R183Factory")]',
            '~pclassdesc_owner.EARLY',
            '$origin_node([P.FOLD.SOURCE],pclassdesc_owner.ORIGIN) = (NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE name*) (SEQUENCE statement*) metadata)',
            '$pchlower(NStmtClass (SEQUENCE eps) (INTEGER flags) ABSENT ABSENT (SEQUENCE name*) (SEQUENCE statement*) metadata) = PCHRAW pchraw',
            'pchheader = { KIND "class", NAME pclassdesc_owner.NAME, ABSTRACT false, FINAL false, READONLY false, PARENT eps, INTERFACES pclassdesc_owner.INTERFACES, BODY pchraw.BODY }',
            'P_before = P[.CLASSES = [pclassdesc_interface]][.EARLY = eps][.LOCATION = P.LOCATION[.PATH = pcpath_owner][.LINE = pclassdesc_owner.LINE]]',
            '$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader)',
            'P_reserved = $anonymous_owner_reserve(P_before,pcpath_owner,pchheader)',
            'P_reserved.CLASSES = [pclassdesc_interface,pclassdesc_provisional]',
            'pclassdesc_provisional.INTERFACES = pchheader.INTERFACES',
            '~pclassdesc_provisional.EARLY',
            'pclassdesc_provisional.METHODS = eps /\\ pclassdesc_provisional.PROPERTIES = eps /\\ pclassdesc_provisional.CONSTANTS = eps',
            '$anonymous_compiled_class_count(P.FOLD.SOURCE,$base64(' + filename + '),P_reserved.CLASSES,eps,eps,0) = (1)',
            '~$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader[.INTERFACES = eps])',
            '~$anonymous_owner_factory_header(P_before[.EARLY = (pcpath_owner)],pcpath_owner,pchheader)',
            '~$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader[.READONLY = true])',
            '$anonymous_class_name($base64(' + filename + '),pclassdesc_owner.LINE,0) = (ptbytes_wrong)',
            '~$anonymous_owner_factory_header(P_before,pcpath_owner,pchheader[.NAME = ptbytes_wrong])',
            '~$anonymous_owner_factory_header(P_reserved,pcpath_owner,pchheader)',
            '$anonymous_compiled_class_count(P.FOLD.SOURCE,$base64(' + filename + '),[pclassdesc_interface,pclassdesc_provisional[.INTERFACES = eps]],eps,eps,0) = eps',
            '$anonymous_compiled_class_count(P.FOLD.SOURCE,$base64(' + filename + '),[pclassdesc_interface,pclassdesc_provisional[.EARLY = true]],eps,eps,0) = eps',
            'P_finished = $anonymous_owner_finish(P_reserved,pcpath_owner,pchheader,pclassdesc_owner.PROPERTIES,pclassdesc_owner.METHODS)',
            'P_finished.CLASSES = [pclassdesc_interface,pclassdesc_owner]']


def runtime(fixture, filename):
    expected = base64.b64decode(ROWS['owner-trait-stringable']['stdout_template_base64'])
    return ['P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
            'P.COMPLETION = PPCNORMAL',
            'P.CLASSES = [pclassdesc_trait,pclassdesc_raw,pclassdesc_child]',
            'pclassdesc_raw.INTERFACES = eps /\\ ~pclassdesc_raw.EARLY',
            'pclassdesc_raw.ORIGIN = PORIGIN 0 pcpath_owner',
            '$origin_node([P.FOLD.SOURCE],pclassdesc_raw.ORIGIN) = (pcnode_owner)',
            '$anonymous_owner_factory_node(pcnode_owner)',
            'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
            r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
            'S_initial.OBJECTS = eps',
            'S_found = $factory182_seek(S_initial,2048)',
            'S_found.COMPLETION = BUDGET',
            'S = S_found[.COMPLETION = NORMAL]', FRONT,
            '$class_at(S.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
            'pclassdesc_live.INTERFACES = [$ptascii("Stringable")]',
            '~pclassdesc_live.EARLY',
            '$method_named(pclassdesc_live.METHODS,$ptascii("make")) = (pmethoddesc_make)',
            '$method_named(pclassdesc_live.METHODS,$ptascii("__toString")) = (pmethoddesc_string)',
            'pcallcontext.FUNCTION = pmethoddesc_make.FUNCTION.ORIGIN',
            'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN)',
            'pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
            'pcallcontext.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_live.ORIGIN',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$anonymous_compiled_class_count(P.FOLD.SOURCE,$base64(' + filename + '),S.CLASSES,eps,eps,0) = (2)',
            '$call_current_valid(S)', '$call_descriptors_valid(S)',
            '$class_state_valid(S)', '$declaration_history_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_split = $drive_steps(S,7)', 'S_split.COMPLETION = BUDGET',
            'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$factory182_output(S_done.EVENTS) = ' + names.template(expected, filename),
            'S_full = $drive_steps(S,8199)', 'S_full = S_done',
            '$class_state_valid(S_done)', '$property_state_valid(S_done)',
            '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))']


def render(case, fixture, filename):
    checks = reservation(fixture, filename) if case['id'] == 'owner-interface-prefix' else runtime(fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or ['owner-interface-prefix', 'owner-trait-stringable']
    cases = {name: {'id': name, 'source': ROWS[name]['source']} for name in selected}
    protocol.run(cases, (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))


if __name__ == '__main__':
    main()
