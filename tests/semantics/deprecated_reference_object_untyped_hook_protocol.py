#!/usr/bin/env python3
"""Check untyped GET backing, EPS payload fences and physical release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_reference_object_fields_protocol import SELECTED
from deprecated_reference_object_typed_class_protocol import lifecycle as class_lifecycle
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook')
sources = {'single': SOURCE / 'untyped-get-singleton.php', 'vector': SOURCE / 'untyped-get-vector.php'}
NAMESPACES = {'single':'Ns266UntypedHookSingle', 'vector':'Ns266UntypedHookVector'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
class_type = lambda name, cls: '[PTBRANCH ([PTCLASS ' + named(name,cls) + '])]'
FIELDS = {'single': [('edge','POBJECT n_child_single_edge')],
    'vector': [('first','POBJECT n_child_vector_first'),
        ('tag','PINT 17'), ('middle','POBJECT n_child_vector_middle'),
        ('last','POBJECT n_child_vector_last')]}


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        raw='S_raw_'+name; cls='S_class_'+name; obj='n_object_'+name; ref='n_reference_'+name
        desc='pclassdesc_'+name; exp='expression_class_'+name; mem='expression_member_'+name
        line='z_'+name; tail='ptask_tail_'+name+'*'
        slots='['+','.join('ppropertyslot_'+name+'_'+f for f,_ in FIELDS[name])+']'
        checks += ['U_'+name+' = '+fixtures[name],
            'S_start_'+name+' = $php_run(U_'+name+',0,'+json.dumps(base64.b64encode(bytes(source)).decode())+')',
            raw+' = $reference_fields_pause(S_start_'+name+'[.COMPLETION = NORMAL],0,eps,30000)',
            '$reference_fields_ready('+raw+',0,eps)',
            raw+'.TODO = (CLASS_CONST_CLASS '+exp+' '+mem+' '+line+') :: '+tail,
            raw+'.ORIGIN = (porigin_site_'+name+')',raw+'.RESULT = REFERENCE '+ref,
            '$call_reference_operand_valid('+raw+','+raw+'.RESULT)',
            raw+'.STORE['+ref+'] = DEFINED (POBJECT '+obj+')',
            '(HCELL '+ref+') <- '+raw+'.ALLOCATIONS','(HOBJECT '+obj+') <- '+raw+'.ALLOCATIONS',
            raw+'.CURRENT = eps',raw+'.FRAMES = eps',raw+'.HELD = eps',raw+'.PROPREFS = eps',
            raw+'.OBJECTS['+obj+'] = INSTANCE porigin_'+name,
            '$class_at('+raw+'.CLASSES,porigin_'+name+') = ('+desc+')',
            desc+'.NAME = '+named(name,'Selected266' if name=='single' else 'Wide266'),
            '$objectprops_at('+raw+'.OBJECTPROPS,'+obj+') = ('+slots+')',
            '$object_table_at('+raw+'.OBJECTTABLES,'+obj+') = eps',
            '$node_children('+raw+',HCELL '+ref+') = [HOBJECT '+obj+']',
            '$heap_owners($heap_graph('+raw+'),HCELL '+ref+') = 1',
            '$heap_owners($heap_graph('+raw+'),HOBJECT '+obj+') = 1',
            '$call_descriptors_valid('+raw+')',
            '$ccn_output('+raw+'.EVENTS) = $ptascii("B|'+('C' if name=='single' else 'W')+'|")',
            'S_global_raw_'+name+' = $global_table_view('+raw+')',
            '$lookup(S_global_raw_'+name+'.ENV,$ptascii("called266'+name+'")) = (n_called_'+name+')',
            'S_global_raw_'+name+'.STORE[n_called_'+name+'] = DEFINED (PBOOL false)']
        for field, expected in FIELDS[name]:
            slot='ppropertyslot_'+name+'_'+field; prop='ppropertydesc_'+name+'_'+field; value='pvalue_'+name+'_'+field
            checks += [slot+'.STATE = PROP_VALUE (DIRECT '+value+')',value+' = '+expected,
                '$property_slot_descriptor('+raw+','+obj+','+slot+') = ('+prop+')',
                slot+'.DECL = ('+prop+'.ORIGIN)',slot+'.NAME = '+prop+'.KEY',
                prop+'.NAME = $ptascii("'+field+'")',prop+'.KEY = '+prop+'.NAME',prop+'.TYPE = eps',
                prop+'.DEFAULT = '+('PROP_STORED porigin_tag_default' if field=='tag' else 'PROP_NULL'),
                prop+'.VISIBILITY = PROPERTY_PUBLIC',prop+'.SETVISIBILITY = eps',
                '~'+prop+'.STATIC','~'+prop+'.READONLY','~'+prop+'.FINAL',
                '$class_constant_reference_object_field_type('+raw+','+prop+','+slot+')']
            origin='porigin_hook_'+name+'_'+field; body='phpType39_'+name+'_'+field
            checks += ['$property_hook_source_declared('+raw+','+prop+')',
                '$property_hook_declared('+raw+','+obj+','+slot+'.NAME)',
                '$property_hook_origin('+raw+','+prop+') = '+'('+origin+')',
                '$property_set_origin('+raw+','+prop+') = '+'eps',
                '$property_hook_override_backed('+raw+','+prop+')',
                '~$property_hook_virtual('+raw+','+prop+')',
                '~$property_hook_backing('+raw+','+obj+','+prop+')',
                '$origin_node('+raw+'.SOURCES,'+origin+') = (NPropertyHook phpType14_'+name+'_'+field+' phpType24_'+name+'_'+field+' phpType4_'+name+'_'+field+' phpType11_'+name+'_'+field+' phpType16_'+name+'_'+field+' '+body+' metadata_'+name+'_'+field+')',
                '$hook_body_backed('+body+','+prop+'.NAME)',
                '$class_constant_reference_object_hook_backed('+raw+','+prop+')',
                '~$class_constant_reference_object_hook_field('+raw+','+obj+','+prop+','+slot+')',
                '$class_constant_reference_object_untyped_hook_field('+raw+','+obj+','+prop+','+slot+')']
            if expected.startswith('POBJECT'):
                child=expected.split()[1]
                actual='Middle266' if field=='middle' else 'Leaf266'
                checks += ['(HOBJECT '+child+') <- '+raw+'.ALLOCATIONS',
                    raw+'.OBJECTS['+child+'] = INSTANCE porigin_child_'+name+'_'+field,
                    '$class_at('+raw+'.CLASSES,porigin_child_'+name+'_'+field+') = (pclassdesc_child_'+name+'_'+field+')',
                    'pclassdesc_child_'+name+'_'+field+'.NAME = '+named(name,actual),
                    '$objectprops_at('+raw+'.OBJECTPROPS,'+child+') = (eps)',
                    '~$typed_object_exact('+raw+','+prop+'.TYPE,'+value+')',
                    '$typed_exact('+prop+'.TYPE,'+value+')',
                    '$value_nodes('+value+') = [HOBJECT '+child+']',
                    '$property_slot_release_job('+raw+','+obj+','+slot+') = [DESTRUCTION_VALUE (HOBJECT '+child+')]']
            else:
                checks += ['$typed_exact('+prop+'.TYPE,'+value+')','$value_nodes('+value+') = eps',
                    '$property_slot_release_job('+raw+','+obj+','+slot+') = eps']
        checks += [cls+' = $class_constant_selector('+raw+','+exp+','+line+')',
            cls+'.COMPLETION = NORMAL',cls+'.RESULT = KNOWN (PSTRING '+desc+'.NAME)',
            cls+'.STORE = '+raw+'.STORE',cls+'.OBJECTPROPS = '+raw+'.OBJECTPROPS',
            '$class_constant_reference_object_graph('+cls+','+obj+',eps)',
            '$class_constant_reference_object_fields('+cls+','+obj+','+slots+')',
            '$class_constant_reference_object_selector('+cls+','+raw+'.RESULT) = ('+desc+')',
            '$class_constant_reference_object_capture_entry('+cls+','+raw+'.RESULT,'+exp+','+mem+','+line+','+tail+')']
    checks += ['$node_children(S_raw_single,HOBJECT n_object_single) = [HOBJECT n_child_single_edge]',
        '$heap_owners($heap_graph(S_raw_single),HOBJECT n_child_single_edge) = 1',
        'n_child_vector_first = n_child_vector_last','n_child_vector_first =/= n_child_vector_middle',
        '$node_children(S_raw_vector,HOBJECT n_object_vector) = [HOBJECT n_child_vector_first,HOBJECT n_child_vector_middle,HOBJECT n_child_vector_last]',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_first) = 2',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_middle) = 1',
        'pclassdesc_vector.PROPERTIES = eps',
        '$class_link_at(S_raw_vector.LINKEDPARENTS,porigin_vector) = (SOURCE_PARENT porigin_fields)',
        '$class_at(S_raw_vector.CLASSES,porigin_fields) = (pclassdesc_fields)',
        'pclassdesc_fields.PROPERTIES = ['+','.join('ppropertydesc_vector_'+f for f,_ in FIELDS['vector'])+']',
        '~pclassdesc_single.READONLY','~pclassdesc_vector.READONLY','~pclassdesc_fields.READONLY']
    return checks


def boundaries():
    checks = []
    for change in ['[.VISIBILITY = PROPERTY_PRIVATE]', '[.SETVISIBILITY = (PROPERTY_PRIVATE)]',
        '[.TYPE = '+class_type('single','LeafBase266')+']', '[.STATIC = true]', '[.READONLY = true]', '[.FINAL = true]']:
        checks += ['~$class_constant_reference_object_untyped_hook_field(S_class_single,n_object_single,ppropertydesc_single_edge'+change+',ppropertyslot_single_edge)']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)']:
        checks += ['~$class_constant_reference_object_untyped_hook_field(S_class_single,n_object_single,ppropertydesc_single_edge,ppropertyslot_single_edge[.STATE = '+state+'])']
    for value in ['PNULL','PINT 17','PBOOL false']:
        slot='ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
        view='S_class_single[.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_object_single,['+slot+'])]'
        checks += ['$class_constant_reference_object_untyped_hook_field('+view+',n_object_single,ppropertydesc_single_edge,'+slot+')',
            '$class_constant_reference_object_graph('+view+',n_object_single,eps)']
    checks += ['~$class_constant_reference_object_untyped_hook_field(S_class_single,|S_class_single.OBJECTS|,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        'ppropertyslot_array = ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (PARRAY 0))]',
        'S_array = S_class_single[.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_object_single,[ppropertyslot_array])]',
        '$class_constant_reference_object_field_type(S_array,ppropertydesc_single_edge,ppropertyslot_array)',
        '$class_constant_reference_object_untyped_hook_field(S_array,n_object_single,ppropertydesc_single_edge,ppropertyslot_array)',
        '~$class_constant_reference_object_graph(S_array,n_object_single,eps)',
        '~$class_constant_reference_object_capture_entry(S_array,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'ppropertyslot_cycle = ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (POBJECT n_object_single))]',
        'S_cycle = S_class_single[.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_object_single,[ppropertyslot_cycle])]',
        '$class_constant_reference_object_untyped_hook_field(S_cycle,n_object_single,ppropertydesc_single_edge,ppropertyslot_cycle)',
        '~$class_constant_reference_object_graph(S_cycle,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_cycle,S_raw_single.RESULT) = eps',
        'S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        'ppropertydesc_typed = ppropertydesc_single_edge[.TYPE = '+class_type('single','LeafBase266')+']',
        '$class_constant_reference_object_hook_field(S_class_single,n_object_single,ppropertydesc_typed,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_untyped_hook_field(S_class_single,n_object_single,ppropertydesc_typed,ppropertyslot_single_edge)',
        'S_type = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_single[.PROPERTIES = [ppropertydesc_typed]])]',
        '$class_constant_reference_object_graph(S_type,n_object_single,eps)', '~$call_descriptors_valid(S_type)',
        '~$class_constant_reference_object_capture_entry(S_type,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'S_default = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_single[.PROPERTIES = [ppropertydesc_single_edge[.DEFAULT = PROP_UNINITIALIZED]]])]',
        '$class_constant_reference_object_graph(S_default,n_object_single,eps)', '~$call_descriptors_valid(S_default)',
        '~$class_constant_reference_object_capture_entry(S_default,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'S_class_single.SOURCES = [pcunit_single]',
        '$origin_source(porigin_hook_single_edge) = PORIGIN n_source_single pcpath_hook_single',
        'pcnode_virtual = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (NScalarInt (INTEGER 17) eps) eps',
        'S_virtual = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_hook_single pcnode_virtual) :: pcunit_single.OCCURRENCES]]]',
        '$property_hook_virtual(S_virtual,ppropertydesc_single_edge)',
        '~$class_constant_reference_object_untyped_hook_field(S_virtual,n_object_single,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_virtual,n_object_single,eps)',
        'ppropertydesc_single_edge.ORIGIN = PORIGIN n_source_single pcpath_property_single',
        'pcpath_group_single = pcpath_property_single[0:$nabs($( |pcpath_property_single| - 2))]',
        '$origin_node(S_class_single.SOURCES,PORIGIN n_source_single pcpath_group_single) = (NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([phpType38_get])) metadata_property)',
        'phpType38_get = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_single_edge metadata_single_edge',
        'pcnode_static = NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([NPropertyHook phpType14_hook (INTEGER 8) phpType4_hook phpType11_hook phpType16_hook phpType39_single_edge metadata_single_edge])) metadata_property',
        'S_static = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_group_single pcnode_static) :: pcunit_single.OCCURRENCES]]]',
        '~$class_constant_reference_object_untyped_hook_field(S_static,n_object_single,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_static,n_object_single,eps)']
    slots='[ppropertyslot_vector_last,ppropertyslot_vector_tag,ppropertyslot_vector_middle,ppropertyslot_vector_first]'
    checks += ['S_order = S_class_vector[.OBJECTPROPS = $objectprops_set(S_class_vector.OBJECTPROPS,n_object_vector,'+slots+')]',
        '$class_constant_reference_object_graph(S_order,n_object_vector,eps)', '~$call_descriptors_valid(S_order)',
        '~$class_constant_reference_object_capture_entry(S_order,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)',
        'S_decl = S_class_vector[.OBJECTPROPS = $objectprops_set(S_class_vector.OBJECTPROPS,n_object_vector,[ppropertyslot_vector_first[.DECL = ppropertyslot_vector_last.DECL],ppropertyslot_vector_tag,ppropertyslot_vector_middle,ppropertyslot_vector_last])]',
        '~$class_constant_reference_object_graph(S_decl,n_object_vector,eps)']
    return checks


def lifecycle():
    old = quoted(b'Ns257TypedClassVector\\Wide257'); new = named('vector','Wide266')
    return [c.replace(old,new).replace('257','266').replace('H|10|Z|','H|10|N|Z|')
        .replace('pinstancestorage.NEXT = 2','pinstancestorage.NEXT = 3')
        .replace('ppropertyslot_vector_first[.STATE = PROP_UNSET],ppropertyslot_vector_middle',
            'ppropertyslot_vector_first[.STATE = PROP_UNSET],ppropertyslot_vector_tag[.STATE = PROP_UNSET],ppropertyslot_vector_middle')
        for c in class_lifecycle()] + [
        'S_global_mid.STORE[n_called_vector] = DEFINED (PBOOL false)',
        'S_global_done.STORE[n_called_vector] = DEFINED (PBOOL false)']




def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),*sources.values(),*modules,*(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_reference_object_typed_class_protocol.py',
        'tests/semantics/deprecated_reference_object_fields_protocol.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py','tests/semantics/static_types.py','tests/semantics/profile.json',
        '.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report={'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'passed':False}
    try:
        frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter=Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        fixtures={}
        try:
            for name,source in sources.items():
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'] and not parsed['diagnostics']
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
                fixtures[name]=checked['fixture']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks=inventory(fixtures)+boundaries()+lifecycle(); report['premises']=len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
        (out / 'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
        report['process']=recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout']=(out / 'check.stdout').read_text(); report['stderr']=(out / 'check.stderr').read_text()
        report['head_stable']=head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable']=before=={str(p.relative_to(ROOT)):sha(p) for p in paths}
        report['passed']=(report['process']['exit']==0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout']=='true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']: print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed']; print('pass',report['premises'])


if __name__ == '__main__': main()
