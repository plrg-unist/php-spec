#!/usr/bin/env python3
"""Check reached anonymous typed slots, reference sources and first linking."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import anonymous_parent_protocol as parent
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_typed_property_cases.json'
CASES = {
    'inherited': 'anonymous-typed-inherited-uninitialized',
    'redeclared': 'anonymous-typed-redeclared-alias',
    'private': 'anonymous-typed-private-shadow',
    'sources': 'anonymous-typed-live-reference-sources',
    'context': 'anonymous-typed-class-type-context',
    'own': 'anonymous-typed-parentless-own-uninitialized',
    'retry': 'anonymous-typed-linked-before-throwing-argument',
}
assert parent.PREFIX.count('  -- if phpType7* =/= eps\n') == 1
PREFIX = parent.PREFIX.replace('  -- if phpType7* =/= eps\n', '')
PREFIX += r'''
dec $anon_typed_phase(pstate,nat,nat) : bool
def $anon_typed_phase(S,n_object,2) = true
  -- if $objectprops_at(S.OBJECTPROPS,n_object) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,$ptascii("left")) = (ppropertyslot_left)
  -- if $property_slot_at(ppropertyslot*,$ptascii("right")) = (ppropertyslot_right)
  -- if ppropertyslot_left.STATE = PROP_VALUE (ALIAS n_cell)
  -- if ppropertyslot_right.STATE = PROP_VALUE (ALIAS n_cell)
  -- if $propref_at(S.PROPREFS,n_cell) = (ppropref)
  -- if |ppropref.SOURCES| = 2
def $anon_typed_phase(S,n_object,1) = true
  -- if $objectprops_at(S.OBJECTPROPS,n_object) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,$ptascii("left")) = (ppropertyslot_left)
  -- if $property_slot_at(ppropertyslot*,$ptascii("right")) = (ppropertyslot_right)
  -- if ppropertyslot_left.STATE = PROP_UNSET
  -- if ppropertyslot_right.STATE = PROP_VALUE (ALIAS n_cell)
  -- if $propref_at(S.PROPREFS,n_cell) = (ppropref)
  -- if |ppropref.SOURCES| = 1
def $anon_typed_phase(S,n_object,n_phase) = false -- otherwise
dec $anon_typed_seek(pstate,nat,nat,nat) : pstate
def $anon_typed_seek(S,n_object,n_phase,n) = S -- if $anon_typed_phase(S,n_object,n_phase)
def $anon_typed_seek(S,n_object,n_phase,0) = S -- if ~$anon_typed_phase(S,n_object,n_phase)
def $anon_typed_seek(S,n_object,n_phase,n) = $anon_typed_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_object,n_phase,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_typed_phase(S,n_object,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $anon_typed_seek(S,n_object,n_phase,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descriptor(key, stem):
    return ['$property_desc_at(ppropertydesc_layout*,$ptascii(' + json.dumps(key) +
            ')) = (ppropertydesc_' + stem + ')']


def slot(state, key, stem):
    return ['$property_slot_at(ppropertyslot_' + state +
            '*,$ptascii(' + json.dumps(key) + ')) = (ppropertyslot_' + stem + ')']


def assertions(case, fixture, filename, stdout):
    checks = [
        'program_source = ' + fixture,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_front_raw = $anon_parent_seek(S_initial,4096)',
        r'S_front_raw.COMPLETION = NORMAL \/ S_front_raw.COMPLETION = BUDGET',
        'S_front = S_front_raw[.COMPLETION = NORMAL]',
        '$anon_parent_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 0 pcpath)',
        'S_front.TODO = (EVAL expression_new) :: ptask_tail*',
        '$anonymous_new_task_valid(S_front,expression_new)',
        'expression_new = NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata_new',
        'expression_wrong = NExprNew (NStmtClass (SEQUENCE eps) (INTEGER 0) ABSENT ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_class) (SEQUENCE phpType7*) metadata_new',
        '~$anonymous_new_task_valid(S_front,expression_wrong)',
        '$anonymous_new_descriptor(S_front,PORIGIN 0 pcpath) = (pclassdesc)',
        'porigin_class = pclassdesc.ORIGIN',
        'porigin_class = PORIGIN 0 (pcpath ++ [PCFIELD 0])',
        'ptbytes_class = pclassdesc.NAME',
        '$call_descriptors_valid(S_front)',
        '$class_state_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
    ]
    if case == 'own':
        checks += [
            'pclassdesc.PARENT = eps',
            'pclassdesc.EARLY',
            '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_class)',
            '$declaration_early(S_front.DECLARATIONS,porigin_class,PPCLASS)',
            '$anonymous_new_pending(S_front,PORIGIN 0 pcpath) = eps',
            '$anon_parent_publications(S_front.DECLARATIONS,porigin_class) = 0',
            'S_ready = S_front',
        ]
    else:
        checks += [
            '~pclassdesc.EARLY',
            'pclassdesc.PARENT = (ptbytes_parent)',
            '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
            '$class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)',
            '$anonymous_new_pending(S_front,PORIGIN 0 pcpath) = (pclassdesc)',
            '$anonymous_new_name(S_front,PORIGIN 0 pcpath) = eps',
            '$class_named(S_front.CLASSNAMES,$ptlc(ptbytes_class)) = eps',
            '$class_link_at(S_front.LINKEDPARENTS,porigin_class) = eps',
            '$anon_parent_publications(S_front.DECLARATIONS,porigin_class) = 0',
            'S_linked_raw = $drive_steps(S_front,1)',
            r'S_linked_raw.COMPLETION = NORMAL \/ S_linked_raw.COMPLETION = BUDGET',
            'S_ready = S_linked_raw[.COMPLETION = NORMAL]',
            'S_ready.TODO = S_front.TODO',
            'S_ready.ORIGIN = S_front.ORIGIN',
            'S_ready.OBJECTS = S_front.OBJECTS',
            'S_ready.ALLOCATIONS = S_front.ALLOCATIONS',
            'S_ready.EVENTS = S_front.EVENTS',
            '$class_named(S_ready.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_class)',
            '$class_link_at(S_ready.LINKEDPARENTS,porigin_class) = (SOURCE_PARENT porigin_parent)',
            '$anon_parent_publications(S_ready.DECLARATIONS,porigin_class) = 1',
            '~$declaration_early(S_ready.DECLARATIONS,porigin_class,PPCLASS)',
            '$anonymous_new_name(S_ready,PORIGIN 0 pcpath) = (ptbytes_class)',
            '$anonymous_new_pending(S_ready,PORIGIN 0 pcpath) = eps',
            'S_bad_receipt = S_ready[.DECLARATIONS = S_front.DECLARATIONS]',
            '~$anonymous_new_available(S_bad_receipt,pclassdesc)',
            'S_bad_link = S_ready[.LINKEDPARENTS = S_front.LINKEDPARENTS]',
            '~$anonymous_new_available(S_bad_link,pclassdesc)',
            '$class_state_valid(S_ready)',
            '$heap_valid($heap_graph(S_ready))',
        ]
    checks += [
        'S_alloc_raw = $drive_steps(S_ready,1)',
        r'S_alloc_raw.COMPLETION = NORMAL \/ S_alloc_raw.COMPLETION = BUDGET',
        'S_alloc = S_alloc_raw[.COMPLETION = NORMAL]',
    ]
    if case == 'retry':
        checks.append('S_alloc.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7_send* 0 eps (porigin_site) z_call) :: (CTOR_RESULT n_object) :: ptask_selected*')
    else:
        checks.append('S_alloc.RESULT = KNOWN (POBJECT n_object)')
    checks += [
        'S_alloc.OBJECTS[n_object] = INSTANCE porigin_class',
        '(HOBJECT n_object) <- S_alloc.ALLOCATIONS',
        '$($heap_owners($heap_graph(S_alloc),HOBJECT n_object) > 0)',
        'ppropertydesc_layout* = $property_layout(S_alloc,porigin_class,|S_alloc.CLASSES|)',
        '$objectprops_at(S_alloc.OBJECTPROPS,n_object) = (ppropertyslot_alloc*)',
        '$call_descriptors_valid(S_alloc)',
        '$class_state_valid(S_alloc)',
        '$heap_valid($heap_graph(S_alloc))',
    ]
    if case in ('inherited', 'redeclared', 'own'):
        checks += descriptor('value', 'value') + slot('alloc', 'value', 'value')
        checks += [
            'ppropertyslot_value.DECL = (ppropertydesc_value.ORIGIN)',
            'ppropertydesc_value.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        ]
        if case in ('inherited', 'own'):
            checks += [
                'ppropertydesc_value.DEFAULT = PROP_UNINITIALIZED',
                'ppropertyslot_value.STATE = PROP_INITIAL',
            ]
        else:
            checks += [
                '$ppproperty_desc_at(pclassdesc_parent.PROPERTIES,$ptascii("value")) = (ppropertydesc_parent)',
                'ppropertydesc_value.ORIGIN =/= ppropertydesc_parent.ORIGIN',
                '|ppropertydesc_layout*| = 1',
                'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
            ]
    if case == 'inherited':
        checks += descriptor('maybe', 'maybe') + slot('alloc', 'maybe', 'maybe')
        checks += [
            '"int" <- $ptmasks(ppropertydesc_maybe.TYPE)',
            '"null" <- $ptmasks(ppropertydesc_maybe.TYPE)',
            'ppropertyslot_maybe.DECL = (ppropertydesc_maybe.ORIGIN)',
            'ppropertyslot_maybe.STATE = PROP_INITIAL',
            '$property_declared_at(pclassdesc_parent.PROPERTIES,ppropertydesc_value.ORIGIN)',
            '$property_declared_at(pclassdesc_parent.PROPERTIES,ppropertydesc_maybe.ORIGIN)',
        ]
    if case == 'private':
        checks += descriptor('token', 'token')
        checks += [
            '$ppproperty_desc_at(pclassdesc_parent.PROPERTIES,$ptascii("token")) = (ppropertydesc_private)',
            'ppropertydesc_private.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_token.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_private.KEY =/= ppropertydesc_token.KEY',
            'ppropertydesc_private.ORIGIN =/= ppropertydesc_token.ORIGIN',
            'ppropertydesc_private.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            'ppropertydesc_token.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
            '$property_slot_at(ppropertyslot_alloc*,ppropertydesc_private.KEY) = (ppropertyslot_private)',
            'ppropertyslot_private.DECL = (ppropertydesc_private.ORIGIN)',
            'ppropertyslot_private.STATE = PROP_VALUE (DIRECT (PINT 3))',
        ]
    if case == 'sources':
        checks += descriptor('left', 'left') + descriptor('right', 'right')
        checks += [
            '$property_declared_at(pclassdesc_parent.PROPERTIES,ppropertydesc_left.ORIGIN)',
            '$property_declared_at(pclassdesc.PROPERTIES,ppropertydesc_right.ORIGIN)',
            'ppropertydesc_left.ORIGIN =/= ppropertydesc_right.ORIGIN',
        ]
    if case == 'context':
        checks += descriptor('owner', 'owner') + descriptor('seen', 'seen') + descriptor('same', 'same')
        checks += [
            '(PTBRANCH ([PTCLASS ptbytes_parent])) <- ppropertydesc_owner.TYPE',
            '(PTBRANCH ([PTCLASS ptbytes_parent])) <- ppropertydesc_seen.TYPE',
            '(PTBRANCH ([PTCLASS ptbytes_class])) <- ppropertydesc_same.TYPE',
            '0 <- ptbytes_class',
            '$property_declaring_name(S_alloc.CLASSES,ppropertydesc_same.ORIGIN) = ptbytes_class',
            '$property_display_name(S_alloc.CLASSES,ppropertydesc_same.ORIGIN) = $ptascii("Base144G@anonymous")',
            '$typed_given(S_alloc,POBJECT n_object) = $ptascii("Base144G@anonymous")',
            '$property_type_name(S_alloc,ppropertydesc_owner) = $ptascii("?self")',
            '$property_type_name(S_alloc,ppropertydesc_seen) = $ptascii("?parent")',
            '$property_type_name(S_alloc,ppropertydesc_same) = $ptascii("?self")',
        ]
    if case == 'sources':
        checks += [
            'S_two_raw = $anon_typed_seek(S_alloc,n_object,2,4096)',
            r'S_two_raw.COMPLETION = NORMAL \/ S_two_raw.COMPLETION = BUDGET',
            'S_two = S_two_raw[.COMPLETION = NORMAL]',
            '$anon_typed_phase(S_two,n_object,2)',
            '$objectprops_at(S_two.OBJECTPROPS,n_object) = (ppropertyslot_two*)',
            '$property_slot_at(ppropertyslot_two*,$ptascii("left")) = (ppropertyslot_left_two)',
            '$property_slot_at(ppropertyslot_two*,$ptascii("right")) = (ppropertyslot_right_two)',
            'ppropertyslot_left_two.STATE = PROP_VALUE (ALIAS n_shared)',
            'ppropertyslot_right_two.STATE = PROP_VALUE (ALIAS n_shared)',
            '$propref_at(S_two.PROPREFS,n_shared) = (ppropref_two)',
            'ppropref_two.SOURCES = [OBJECT_PROP_SOURCE n_object ppropertydesc_left.KEY ppropertydesc_left.ORIGIN, OBJECT_PROP_SOURCE n_object ppropertydesc_right.KEY ppropertydesc_right.ORIGIN]',
            'S_two.STORE[n_shared] = DEFINED (PINT 1)',
            '$($heap_owners($heap_graph(S_two),HCELL n_shared) >= 2)',
            '$call_descriptors_valid(S_two)',
            '$class_state_valid(S_two)',
            '$heap_valid($heap_graph(S_two))',
            'S_one_raw = $anon_typed_seek(S_two,n_object,1,4096)',
            r'S_one_raw.COMPLETION = NORMAL \/ S_one_raw.COMPLETION = BUDGET',
            'S_one = S_one_raw[.COMPLETION = NORMAL]',
            '$anon_typed_phase(S_one,n_object,1)',
            '$lookup(S_one.ENV,$ptascii("r")) = (n_shared)',
            '$propref_at(S_one.PROPREFS,n_shared) = (ppropref_one)',
            'ppropref_one.SOURCES = [OBJECT_PROP_SOURCE n_object ppropertydesc_right.KEY ppropertydesc_right.ORIGIN]',
            'S_one.STORE[n_shared] = DEFINED (PINT 7)',
            '$call_descriptors_valid(S_one)',
            '$class_state_valid(S_one)',
            '$heap_valid($heap_graph(S_one))',
            'S_resume = S_one',
        ]
    else:
        checks.append('S_resume = S_alloc')
    checks += [
        'S_done = $drive_steps(S_resume,8192)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$anon_parent_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$call_descriptors_valid(S_done)',
        '$class_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    if case != 'own':
        checks.append('$anon_parent_publications(S_done.DECLARATIONS,porigin_class) = 1')
    if case == 'retry':
        checks += [
            'S_done.DECLARATIONS = S_ready.DECLARATIONS',
            '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            '$lookup(S_done.ENV,$ptascii("a")) = (n_a)',
            '$lookup(S_done.ENV,$ptascii("b")) = (n_b)',
            'S_done.STORE[n_a] = DEFINED (POBJECT n_object_a)',
            'S_done.STORE[n_b] = DEFINED (POBJECT n_object_b)',
            'n_object_a =/= n_object_b',
            'S_done.OBJECTS[n_object_a] = INSTANCE porigin_class',
            'S_done.OBJECTS[n_object_b] = INSTANCE porigin_class',
            '$anonymous_new_available(S_done,pclassdesc)',
        ]
        return checks
    checks += [
        '$objectprops_at(S_done.OBJECTPROPS,n_object) = (ppropertyslot_done*)',
    ]
    if case in ('inherited', 'redeclared', 'private', 'sources', 'own'):
        checks.append('$lookup(S_done.ENV,$ptascii("r")) = (n_r)')
    if case in ('inherited', 'private', 'own'):
        key, stem, value = {
            'inherited': ('maybe', 'maybe', 'PINT 12'),
            'private': ('token', 'token', 'pvalue_r'),
            'own': ('value', 'value', 'PINT 9'),
        }[case]
        checks += slot('done', key, 'final')
        checks += [
            'S_done.STORE[n_r] = DEFINED (' + value + ')',
            'ppropertyslot_final.STATE = PROP_VALUE (ALIAS n_r)',
            'ppropertyslot_final.DECL = (ppropertydesc_' + stem + '.ORIGIN)',
            '$propref_at(S_done.PROPREFS,n_r) = (ppropref)',
            'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ppropertydesc_' + stem + '.KEY ppropertydesc_' + stem + '.ORIGIN]',
        ]
        if case == 'private':
            checks += [
                '$typed_string_value(pvalue_r)',
                '$string_bytes(pvalue_r) = ($ptascii("8"))',
            ]
    if case == 'private':
        checks += [
            '$property_slot_at(ppropertyslot_done*,ppropertydesc_private.KEY) = (ppropertyslot_base_final)',
            'ppropertyslot_base_final.STATE = PROP_VALUE (DIRECT (PINT 3))',
        ]
    if case in ('redeclared', 'sources'):
        checks += [
            'S_done.STORE[n_r] = DEFINED pvalue_r',
            '$typed_string_value(pvalue_r)',
            '$string_bytes(pvalue_r) = ($ptascii("free"))',
            '$propref_at(S_done.PROPREFS,n_r) = eps',
        ]
        if case == 'redeclared':
            checks += slot('done', 'value', 'final')
            checks += [
                'ppropertyslot_final.DECL = (ppropertydesc_value.ORIGIN)',
                'ppropertyslot_final.STATE = PROP_VALUE (DIRECT (PINT 4))',
            ]
        else:
            checks += slot('done', 'left', 'left_final') + slot('done', 'right', 'right_final')
            checks += [
                'ppropertyslot_left_final.STATE = PROP_UNSET',
                'ppropertyslot_right_final.STATE = PROP_UNSET',
            ]
    if case == 'context':
        checks += slot('done', 'same', 'same_final')
        checks.append('ppropertyslot_same_final.STATE = PROP_VALUE (DIRECT (POBJECT n_object))')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=sorted(CASES), required=True)
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == CASES[args.case])
    out = Path(tempfile.mkdtemp(prefix='anonymous-typed-' + args.case + '-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    watched = [ROOT / 'spec/semantics' / name for name in (
        '30-storage.watsup', '53-incdec.watsup', '95-type-values.watsup',
        '135-property-compiler.watsup', '136-property-runtime.watsup',
        '138-property-references.watsup', '238-trait-data.watsup',
        '359-instance-storage-pin.watsup', '383-anonymous-classes.watsup', 'modules.json')]
    watched += [CATALOGUE, Path(__file__), ROOT / '_build/default/adapter/main.exe',
                ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'passed': False, 'case': args.case, 'source_sha256': sha(source),
              'inputs_before': before, 'raw': str(out)}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        filename = base64.b64encode(os.fsencode(source)).decode()
        stdout = base64.b64decode(row.get('stdout_template_base64', row['stdout_base64'])).replace(b'{FILE}', os.fsencode(source))
        checks = assertions(args.case, checked['fixture'], filename, stdout)
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *[str(ROOT / module) for module in modules], str(fixture)],
                                      out / 'numeric', 240, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(checks), fixture_sha256=sha(fixture))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['inputs_after'] = {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
