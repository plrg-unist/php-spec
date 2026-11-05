#!/usr/bin/env python3
"""Trait source authority, consumer scope, shared templates and abrupt images."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/trait_source_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
FRONT = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext)')
PREFIX = names.PREFIX.replace(names.FRONT, FRONT)


def source_context(fixture, filename):
    return ['P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
            r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
            'P.CLASSES = [pclassdesc_child,pclassdesc_trait,pclassdesc_a,pclassdesc_b,pclassdesc_after]',
            'pclassdesc_trait.ORIGIN = PORIGIN 0 pcpath_trait',
            '$origin_node([P.FOLD.SOURCE],pclassdesc_trait.ORIGIN) = (pcnode_trait)',
            '$anonymous_named_method_owner(pcnode_trait) = (2)',
            '$method_named(pclassdesc_trait.METHODS,$ptascii("make")) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
            'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
            'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
            '$plclasscontext(P.FOLD.SOURCE,pcpath_trait,$base64(' + filename + '),pclassdesc_trait.LINE) = (ptcontext_source)',
            '$anonymous_named_header(pcnode_trait,ptcontext_source) = ((pchheader,z_trait))',
            'pchheader.KIND = "trait"',
            'ptcontext = $ppmethod_context(P,pchheader,$ptascii("make"),2)',
            'ptcontext.SCOPE = PTTRAIT pclassdesc_trait.NAME',
            'P_scope = P[.GOTOROOT = pcpath_method][.CLOSURE = false][.RETURNREF = false][.CLASSCONTEXT = (ptcontext)][.FOLD = P.FOLD[.CLOSURE = false][.FUNCTION = pclassdesc_trait.NAME ++ $ptascii("::make")][.CLASSCONTEXT = (ptcontext)]]',
            '$anonymous_factory_context(P_scope,pcpath_new)',
            'ptcontext_bad = ptcontext[.SCOPE = PTKNOWN pclassdesc_trait.NAME eps]',
            '~$anonymous_factory_context(P_scope[.CLASSCONTEXT = (ptcontext_bad)][.FOLD.CLASSCONTEXT = (ptcontext_bad)],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.GOTOROOT = pcpath_trait ++ [PCFIELD 5,PCINDEX 0]],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.FUNCTION = $ptascii("T184Shared::alias")],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.SOURCE = $pcsource(1,P.FOLD.SOURCE.AST)],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.CLASSCONTEXT = eps],pcpath_new)',
            '$anonymous_compiled_class_count(P.FOLD.SOURCE,$base64(' + filename + '),P.CLASSES,eps,eps,0) = (4)',
            '$anonymous_class_name($base64(' + filename + '),2,0) = (pclassdesc_child.NAME)',
            '$anonymous_class_name($base64(' + filename + '),4,3) = (pclassdesc_after.NAME)']


def consumer(fixture, filename):
    expected = base64.b64decode(ROWS['trait-lexical-parent-self-static']['stdout_template_base64'])
    return ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
            r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
            'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
            'S = S_found[.COMPLETION = NORMAL]', FRONT,
            '$class_named(S.CLASSNAMES,$ptascii("a184scope")) = (porigin_a)',
            '$class_named(S.CLASSNAMES,$ptascii("c184scope")) = (porigin_c)',
            '$class_at(S.CLASSES,porigin_a) = (pclassdesc_a)',
            '$method_named(pclassdesc_a.METHODS,$ptascii("make")) = (pmethoddesc)',
            'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
            'pcallcontext.LEXICAL_CLASS = (porigin_a)',
            'pcallcontext.CALLED_CLASS = (porigin_c)',
            'pcallcontext.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_c',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$call_current_valid(S)', '$call_descriptors_valid(S)',
            '$class_state_valid(S)', '$declaration_history_valid(S)', '$heap_valid($heap_graph(S))',
            'S_split = $drive_steps(S,7)', 'S_split.COMPLETION = BUDGET',
            'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],8192)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$factory182_output(S_done.EVENTS) = ' + names.template(expected, filename),
            'S_full = $drive_steps(S,8199)', 'S_full = S_done',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$class_state_valid(S_done)', '$property_state_valid(S_done)',
            '$declaration_history_valid(S_done)', '$heap_valid($heap_graph(S_done))']


def abrupt(fixture, filename):
    return ['P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
            'P.COMPLETION = PPCABRUPT pcompletion', '~$declaration_unsupported(pcompletion)',
            'P.CLASSES = [pclassdesc_child]', 'P.INSTALLED.CLASSES = eps',
            'P.PUBLICATIONS = [PPCP pclassdesc_child.ORIGIN 1 PPCLASS]',
            '$anonymous_failed_owner_child_checkpoint(P,pclassdesc_child.ORIGIN)',
            'porigin_trait = PORIGIN 0 ([PCINDEX 0])',
            '~$anonymous_failed_owner_child_checkpoint(P,porigin_trait)',
            'pclassdesc_trait = { ORIGIN porigin_trait, KIND "trait", NAME $ptascii("T184Constant"), PARENT eps, INTERFACES eps, PROPERTIES eps, METHODS eps, CONSTANTS eps, ABSTRACT false, FINAL false, READONLY false, EARLY true, LINE 2 }',
            '~$anonymous_failed_owner_child_checkpoint(P[.INSTALLED.CLASSES = [pclassdesc_trait]],pclassdesc_child.ORIGIN)',
            '~$anonymous_failed_owner_child_checkpoint(P[.INSTALLED.CLASSES = [pclassdesc_child]],pclassdesc_child.ORIGIN)',
            '~$anonymous_failed_owner_child_checkpoint(P[.COMPLETION = PPCNORMAL],pclassdesc_child.ORIGIN)',
            '~$anonymous_failed_owner_child_checkpoint(P[.COMPLETION = PPCABRUPT (UNSUPPORTED "other")],pclassdesc_child.ORIGIN)',
            'S = $php_run(' + fixture + ',0,' + filename + ')',
            'S.COMPLETION = pcompletion', 'S.CLASSES = eps', 'S.CLASSNAMES = eps',
            'S.OBJECTS = eps', '$declaration_history_valid(S)']


def render(case, fixture, filename):
    make = source_context if case['id'] == 'trait-shared-template-alias' else consumer if case['id'] == 'trait-lexical-parent-self-static' else abrupt
    checks = make(fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or ['trait-shared-template-alias','trait-lexical-parent-self-static','trait-child-warning-before-constant-fatal']
    cases = {name: {'id': name, 'source': ROWS[name]['source']} for name in selected}
    protocol.run(cases, (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))


if __name__ == '__main__':
    main()
