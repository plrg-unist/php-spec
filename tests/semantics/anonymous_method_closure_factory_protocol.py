#!/usr/bin/env python3
"""Method-owned factory scopes, real receivers, failed owners and resumption."""
import argparse
import base64
import json
from pathlib import Path

import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_method_closure_factory_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
FRONT = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_closure')
PREFIX = r'''
dec $factory182_output_one(pevent) : ptbytes
def $factory182_output_one(OUTPUT ptbytes) = ptbytes
def $factory182_output_one(pevent) = eps -- otherwise
dec $factory182_output(pevent*) : ptbytes
def $factory182_output(eps) = eps
def $factory182_output(pevent :: pevent_tail*) = $factory182_output_one(pevent) ++ $factory182_output(pevent_tail*)
dec $factory182_front(pstate) : bool
def $factory182_front(S) = true -- if FRONT
def $factory182_front(S) = false -- otherwise
dec $factory182_seek(pstate, nat) : pstate
def $factory182_seek(S, 0) = S
def $factory182_seek(S, n) = S -- if $(n > 0) /\ $factory182_front(S)
def $factory182_seek(S, n) = $factory182_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$factory182_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $factory182_seek(S, n) = S -- otherwise
'''.replace('FRONT', FRONT)


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def runtime(row, fixture, filename):
    failed = row['id'] == 'anonymous-ctor-closure-escape'
    out = ['S_initial = $php_run(' + fixture + ',0,' + filename + ')',
           r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
           'S_found = $factory182_seek(S_initial,2048)',
           'S_found.COMPLETION = BUDGET',
           'S = S_found[.COMPLETION = NORMAL]', FRONT,
           'S.CLASSES = [pclassdesc_child,pclassdesc_owner]' if not failed else
           'S.CLASSES = [pclassdesc_owner,pclassdesc_child]',
           'pcallcontext.LEXICAL_CLASS = (pclassdesc_owner.ORIGIN)',
           'pcallcontext.CALLED_CLASS = (pclassdesc_owner.ORIGIN)',
           '$target_function(S,CLOSURE_TARGET n_closure) = (pfunction)',
           'pfunction.ORIGIN = pcallcontext.FUNCTION',
           '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
           '$call_current_valid(S)', '$call_descriptors_valid(S)',
           '$closure_state_valid(S)', '$declaration_history_valid(S)',
           '$heap_valid($heap_graph(S))']
    if failed:
        out += ['pclosurescope.RECEIVER = eps',
                'pcallcontext.RECEIVER = eps',
                'S.OBJECTS[0] = INSTANCE pclassdesc_owner.ORIGIN',
                '~((HOBJECT 0) <- S.ALLOCATIONS)',
                '$factory182_output(S.EVENTS) = $ptascii("caught;")']
    else:
        out += ['pclosurescope.RECEIVER = (n_receiver)',
                'pcallcontext.RECEIVER = (n_receiver)',
                'S.OBJECTS[n_receiver] = INSTANCE pclassdesc_owner.ORIGIN',
                '(HOBJECT n_receiver) <- S.ALLOCATIONS',
                '(HOBJECT n_receiver) <- $node_children(S,HOBJECT n_closure)',
                '$lookup($global_table_view(S).ENV,$ptascii("owner")) = eps',
                '$factory182_output(S.EVENTS) = $ptascii("9;R182Default;3;")']
    expected = base64.b64decode(row['stdout_template_base64'])
    out += ['S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
            'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$factory182_output(S_done.EVENTS) = ' + template(expected, filename),
            'S_full = $drive_steps(S,4097)', 'S_full = S_done',
            '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
            '$class_state_valid(S_done)', '$declaration_history_valid(S_done)',
            '$heap_valid($heap_graph(S_done))']
    return out


def template(data, filename):
    return (' ++ $base64(' + filename + ') ++ ').join(term(part) for part in data.split(b'{FILE}'))


def pure(fixture, filename):
    return ['P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
            r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
            'P.CLOSURETEMPLATES = [pfunction]',
            'P.CLASSES = [pclassdesc_before,pclassdesc_child,pclassdesc_owner,pclassdesc_after]',
            '$method_named(pclassdesc_owner.METHODS,$ptascii("make")) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = PORIGIN 0 pcpath_method',
            'pfunction.ORIGIN = PORIGIN 0 pcpath_closure',
            'pclassdesc_child.ORIGIN = PORIGIN 0 pcpath_child',
            'pcpath_new = pcpath_child[0:$nabs($(|pcpath_child| - 1))]',
            'pclassdesc_owner.ORIGIN = PORIGIN 0 pcpath_owner',
            '$origin_node([P.FOLD.SOURCE],pclassdesc_owner.ORIGIN) = (pcnode_owner)',
            '$plclasscontext(P.FOLD.SOURCE,pcpath_owner,$base64(' + filename + '),pclassdesc_owner.LINE) = (ptcontext_source)',
            '$anonymous_named_header(pcnode_owner,ptcontext_source) = ((pchheader,z_owner))',
            'ptcontext = $ppmethod_context(P,pchheader,$ptascii("make"),3)',
            'P_scope = P[.GOTOROOT = pcpath_closure][.CLOSURE = true][.RETURNREF = false][.CLASSCONTEXT = (ptcontext)][.FOLD = P.FOLD[.CLOSURE = true][.FUNCTION = pfunction.NAME][.CLASSCONTEXT = (ptcontext)]]',
            '$anonymous_method_scope(P.FOLD.SOURCE,pcpath_closure,pclassdesc_owner.NAME) = ((pcpath_closure,pcpath_method,pfunction.NAME,6))',
            '$anonymous_factory_context(P_scope,pcpath_new)',
            '~$anonymous_factory_context(P_scope[.GOTOROOT = pcpath_method],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.FUNCTION = $ptascii("forged")],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.CLASSCONTEXT = (ptcontext[.OWNER = $ptascii("Other")])],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.CLASSCONTEXT = eps],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.CLOSURE = false],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.RETURNREF = true],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.DEFAULT = true],pcpath_new)',
            '~$anonymous_factory_context(P_scope[.FOLD.CONSTANT = true],pcpath_new)',
            'pclassdesc_before.ORIGIN = PORIGIN 0 pcpath_before',
            '~$anonymous_factory_context(P_scope,pcpath_before)',
            '~$anonymous_rejected_constructor_factory(P_scope)']


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = pure(fixture, filename) if case['id'] == 'named-static-closure-reuse' else runtime(row, fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or ['named-static-closure-reuse', 'named-instance-closure-self-default', 'anonymous-ctor-closure-escape']
    cases = {name: {'id': name, 'source': ROWS[name]['source']} for name in selected}
    protocol.run(cases, (Path(__file__), CATALOGUE), fixture_renderer=render, runner_flags=('--sl',))


if __name__ == '__main__':
    main()
