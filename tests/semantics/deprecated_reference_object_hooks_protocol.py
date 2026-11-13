#!/usr/bin/env python3
"""Check backed getter/setter storage and physical release without hook invocation."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_hooks')
sources = {'single': SOURCE / 'backed-get-singleton.php', 'vector': SOURCE / 'backed-hook-vector.php'}
NAMESPACES = {'single':'Ns264HookSingle', 'vector':'Ns264HookVector'}
PRIMITIVES = ('int','float','string','bool','false','true','null','object','mixed')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
atom = lambda name, value: 'PTBUILTIN ' + json.dumps(value) if value in PRIMITIVES else 'PTCLASS ' + named(name,value)
union = lambda name, values: '[' + ','.join('PTBRANCH ([' + atom(name,v) + '])' for v in values) + ']'
FIELDS = {'single': [('edge',('LeafBase264',),'POBJECT n_child_single_edge')],
    'vector': [('first',('LeafBase264',),'POBJECT n_child_vector_first'),
        ('tag',('int',),'PINT 17'), ('middle',('Middle264',),'POBJECT n_child_vector_middle'),
        ('last',('LeafBase264',),'POBJECT n_child_vector_last')]}


def inventory(fixtures):
    checks = []
    for name, source in sources.items():
        raw='S_raw_'+name; cls='S_class_'+name; obj='n_object_'+name; ref='n_reference_'+name
        desc='pclassdesc_'+name; exp='expression_class_'+name; mem='expression_member_'+name
        line='z_'+name; tail='ptask_tail_'+name+'*'
        slots='['+','.join('ppropertyslot_'+name+'_'+f for f,_,_ in FIELDS[name])+']'
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
            desc+'.NAME = '+named(name,'Selected264' if name=='single' else 'Wide264'),
            '$objectprops_at('+raw+'.OBJECTPROPS,'+obj+') = ('+slots+')',
            '$object_table_at('+raw+'.OBJECTTABLES,'+obj+') = eps',
            '$node_children('+raw+',HCELL '+ref+') = [HOBJECT '+obj+']',
            '$heap_owners($heap_graph('+raw+'),HCELL '+ref+') = 1',
            '$heap_owners($heap_graph('+raw+'),HOBJECT '+obj+') = 1',
            '$call_descriptors_valid('+raw+')',
            '$ccn_output('+raw+'.EVENTS) = $ptascii("B|'+('C' if name=='single' else 'W')+'|")']
        for field, names, expected in FIELDS[name]:
            slot='ppropertyslot_'+name+'_'+field; prop='ppropertydesc_'+name+'_'+field; value='pvalue_'+name+'_'+field
            checks += [slot+'.STATE = PROP_VALUE (DIRECT '+value+')',value+' = '+expected,
                '$property_slot_descriptor('+raw+','+obj+','+slot+') = ('+prop+')',
                slot+'.DECL = ('+prop+'.ORIGIN)',slot+'.NAME = '+prop+'.KEY',
                prop+'.NAME = $ptascii("'+field+'")',prop+'.KEY = '+prop+'.NAME',prop+'.TYPE = '+union(name,names),
                prop+'.DEFAULT = '+('PROP_STORED porigin_tag_default' if field=='tag' else 'PROP_UNINITIALIZED'),
                prop+'.VISIBILITY = PROPERTY_PUBLIC',prop+'.SETVISIBILITY = eps',
                '~'+prop+'.STATIC','~'+prop+'.READONLY','~'+prop+'.FINAL',
                '$class_constant_reference_object_field_type('+raw+','+prop+','+slot+')']
            if field!='middle':
                origin='porigin_hook_'+name+'_'+field; body='phpType39_'+name+'_'+field
                setter=field=='tag'
                checks += ['$property_hook_source_declared('+raw+','+prop+')',
                    '$property_hook_declared('+raw+','+obj+','+slot+'.NAME)',
                    '$property_hook_origin('+raw+','+prop+') = '+('eps' if setter else '('+origin+')'),
                    '$property_set_origin('+raw+','+prop+') = '+('('+origin+')' if setter else 'eps'),
                    ('~' if setter else '')+'$property_hook_override_backed('+raw+','+prop+')',
                    '~$property_hook_virtual('+raw+','+prop+')',
                    '~$property_hook_backing('+raw+','+obj+','+prop+')',
                    '$origin_node('+raw+'.SOURCES,'+origin+') = (NPropertyHook phpType14_'+name+'_'+field+' phpType24_'+name+'_'+field+' phpType4_'+name+'_'+field+' phpType11_'+name+'_'+field+' phpType16_'+name+'_'+field+' '+body+' metadata_'+name+'_'+field+')',
                    '$hook_body_backed('+body+','+prop+'.NAME)',
                    '$class_constant_reference_object_hook_backed('+raw+','+prop+')',
                    '$class_constant_reference_object_hook_field('+raw+','+obj+','+prop+','+slot+')']
            else:
                checks += ['~$property_hook_source_declared('+raw+','+prop+')',
                    '~$property_hook_declared('+raw+','+obj+','+slot+'.NAME)',
                    '~$class_constant_reference_object_hook_backed('+raw+','+prop+')',
                    '~$class_constant_reference_object_hook_field('+raw+','+obj+','+prop+','+slot+')']
            if expected.startswith('POBJECT'):
                child=expected.split()[1]
                actual='Middle264' if field=='middle' else 'Leaf264'
                checks += ['(HOBJECT '+child+') <- '+raw+'.ALLOCATIONS',
                    raw+'.OBJECTS['+child+'] = INSTANCE porigin_child_'+name+'_'+field,
                    '$class_at('+raw+'.CLASSES,porigin_child_'+name+'_'+field+') = (pclassdesc_child_'+name+'_'+field+')',
                    'pclassdesc_child_'+name+'_'+field+'.NAME = '+named(name,actual),
                    '$objectprops_at('+raw+'.OBJECTPROPS,'+child+') = (eps)',
                    '$typed_object_exact('+raw+','+prop+'.TYPE,'+value+')',
                    '~$typed_exact('+prop+'.TYPE,'+value+')',
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
        '~$class_constant_reference_object_scalar_value(pvalue_single_edge)',
        'n_child_vector_first = n_child_vector_last','n_child_vector_first =/= n_child_vector_middle',
        '$node_children(S_raw_vector,HOBJECT n_object_vector) = [HOBJECT n_child_vector_first,HOBJECT n_child_vector_middle,HOBJECT n_child_vector_last]',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_first) = 2',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_middle) = 1',
        'pclassdesc_vector.PROPERTIES = eps',
        '$class_link_at(S_raw_vector.LINKEDPARENTS,porigin_vector) = (SOURCE_PARENT porigin_fields)',
        '$class_at(S_raw_vector.CLASSES,porigin_fields) = (pclassdesc_fields)',
        'pclassdesc_fields.PROPERTIES = ['+','.join('ppropertydesc_vector_'+f for f,_,_ in FIELDS['vector'])+']',
        '~pclassdesc_single.READONLY','~pclassdesc_vector.READONLY','~pclassdesc_fields.READONLY']
    return checks


def boundaries():
    checks = []
    for change in ['[.VISIBILITY = PROPERTY_PRIVATE]', '[.SETVISIBILITY = (PROPERTY_PRIVATE)]',
        '[.TYPE = eps]', '[.STATIC = true]', '[.READONLY = true]', '[.FINAL = true]']:
        checks += ['~$class_constant_reference_object_hook_field(S_class_single,n_object_single,ppropertydesc_single_edge'+change+',ppropertyslot_single_edge)']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT PNULL)','PROP_VALUE (DIRECT (PBOOL false))','PROP_VALUE (DIRECT (PINT 17))',
        'PROP_VALUE (DIRECT (PARRAY 0))','PROP_VALUE (DIRECT (POBJECT n_object_single))']:
        slot='ppropertyslot_single_edge[.STATE = '+state+']'
        checks += ['~$class_constant_reference_object_hook_field(S_class_single,n_object_single,ppropertydesc_single_edge,'+slot+')']
    checks += ['~$class_constant_reference_object_hook_field(S_class_single,|S_class_single.OBJECTS|,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        'S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        'ppropertydesc_cycle = ppropertydesc_single_edge[.TYPE = '+union('single',('Selected264',))+']',
        'ppropertyslot_cycle = ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (POBJECT n_object_single))]',
        'S_cycle = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_single[.PROPERTIES = [ppropertydesc_cycle]])][.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_object_single,[ppropertyslot_cycle])]',
        '$class_constant_reference_object_hook_field(S_cycle,n_object_single,ppropertydesc_cycle,ppropertyslot_cycle)',
        '~$class_constant_reference_object_graph(S_cycle,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_cycle,S_raw_single.RESULT) = eps',
        'S_class_single.SOURCES = [pcunit_single]',
        '$origin_source(porigin_hook_single_edge) = PORIGIN n_source_single pcpath_hook_single',
        'pcnode_virtual = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (NScalarInt (INTEGER 17) eps) eps',
        'S_virtual = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_hook_single pcnode_virtual) :: pcunit_single.OCCURRENCES]]]',
        '$property_hook_virtual(S_virtual,ppropertydesc_single_edge)',
        '~$class_constant_reference_object_hook_backed(S_virtual,ppropertydesc_single_edge)',
        '~$class_constant_reference_object_graph(S_virtual,n_object_single,eps)',
        '~$class_constant_reference_object_capture_entry(S_virtual,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'ppropertydesc_single_edge.ORIGIN = PORIGIN n_source_single pcpath_property_single',
        'pcpath_group_single = pcpath_property_single[0:$nabs($( |pcpath_property_single| - 2))]',
        '$origin_node(S_class_single.SOURCES,PORIGIN n_source_single pcpath_group_single) = (NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([phpType38_get])) metadata_property)',
        'phpType38_get = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_single_edge metadata_single_edge',
        'pcnode_static = NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([NPropertyHook phpType14_hook (INTEGER 8) phpType4_hook phpType11_hook phpType16_hook phpType39_single_edge metadata_single_edge])) metadata_property',
        'S_static = S_class_single[.SOURCES = [pcunit_single[.OCCURRENCES = (PCOCCURRENCE pcpath_group_single pcnode_static) :: pcunit_single.OCCURRENCES]]]',
        '~$class_constant_reference_object_hook_backed(S_static,ppropertydesc_single_edge)',
        '~$class_constant_reference_object_graph(S_static,n_object_single,eps)',
        'S_class_vector.SOURCES = [pcunit_vector]',
        '$origin_source(porigin_hook_vector_tag) = PORIGIN n_source_vector pcpath_hook_set',
        'pcnode_empty_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "c2V0") eps) (SEQUENCE eps) (SEQUENCE eps) eps',
        'S_unbacked_set = S_class_vector[.SOURCES = [pcunit_vector[.OCCURRENCES = (PCOCCURRENCE pcpath_hook_set pcnode_empty_set) :: pcunit_vector.OCCURRENCES]]]',
        '~$class_constant_reference_object_hook_backed(S_unbacked_set,ppropertydesc_vector_tag)',
        '~$class_constant_reference_object_graph(S_unbacked_set,n_object_vector,eps)',
        'S_type = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_single[.PROPERTIES = [ppropertydesc_single_edge[.TYPE = '+union('single',('LeafBase264','null'))+']]])]',
        '$class_constant_reference_object_graph(S_type,n_object_single,eps)', '~$call_descriptors_valid(S_type)',
        '~$class_constant_reference_object_capture_entry(S_type,S_raw_single.RESULT,expression_class_single,expression_member_single,z_single,ptask_tail_single*)',
        'S_default = S_class_vector[.CLASSES = $trait_class_set(S_class_vector.CLASSES,pclassdesc_fields[.PROPERTIES = [ppropertydesc_vector_first,ppropertydesc_vector_tag[.DEFAULT = PROP_UNINITIALIZED],ppropertydesc_vector_middle,ppropertydesc_vector_last]])]',
        '$class_constant_reference_object_graph(S_default,n_object_vector,eps)', '~$call_descriptors_valid(S_default)',
        '~$class_constant_reference_object_capture_entry(S_default,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)']
    slots='[ppropertyslot_vector_last,ppropertyslot_vector_tag,ppropertyslot_vector_middle,ppropertyslot_vector_first]'
    checks += ['S_order = S_class_vector[.OBJECTPROPS = $objectprops_set(S_class_vector.OBJECTPROPS,n_object_vector,'+slots+')]',
        '$class_constant_reference_object_graph(S_order,n_object_vector,eps)', '~$call_descriptors_valid(S_order)',
        '~$class_constant_reference_object_capture_entry(S_order,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)',
        'S_decl = S_class_vector[.OBJECTPROPS = $objectprops_set(S_class_vector.OBJECTPROPS,n_object_vector,[ppropertyslot_vector_first[.DECL = ppropertyslot_vector_last.DECL],ppropertyslot_vector_tag,ppropertyslot_vector_middle,ppropertyslot_vector_last])]',
        '~$class_constant_reference_object_graph(S_decl,n_object_vector,eps)']
    return checks


def lifecycle():
    old = quoted(b'Ns257TypedClassVector\\Wide257'); new = named('vector','Wide264')
    return [c.replace(old,new).replace('257','264').replace('B|W|D|','B|W|D|I|')
        .replace('pinstancestorage.NEXT = 2','pinstancestorage.NEXT = 3')
        .replace('ppropertyslot_vector_first[.STATE = PROP_UNSET],ppropertyslot_vector_middle',
            'ppropertyslot_vector_first[.STATE = PROP_UNSET],ppropertyslot_vector_tag[.STATE = PROP_UNSET],ppropertyslot_vector_middle')
        for c in class_lifecycle()]




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
