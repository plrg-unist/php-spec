#!/usr/bin/env python3
"""Check object/mixed masks, bounded DIRECT values and physical release edges."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_object_mixed')
sources = {'single': SOURCE / 'literal-singleton.php', 'vector': SOURCE / 'mixed-vector.php'}
NAMESPACES = {'single':'Ns259ObjectMixedSingle', 'vector':'Ns259ObjectMixedVector'}
PRIMITIVES = ('int','float','string','bool','false','true','null','object','mixed')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
atom = lambda name, value: 'PTBUILTIN ' + json.dumps(value) if value in PRIMITIVES else 'PTCLASS ' + named(name,value)
union = lambda name, values: '[' + ','.join('PTBRANCH ([' + atom(name,v) + '])' for v in values) + ']'
FIELDS = {
    'single': [('edge', ('mixed',), 'POBJECT n_child_single_edge')],
    'vector': [('first', ('object',), 'POBJECT n_child_vector_first'),
        ('middle', ('object','int'), 'POBJECT n_child_vector_middle'),
        ('last', ('null','object'), 'POBJECT n_child_vector_last'),
        ('nothing', ('mixed',), 'PNULL'), ('integer', ('mixed',), 'PINT 17'),
        ('floating', ('mixed',), 'PFLOAT 4609434218613702656'),
        ('request', ('mixed',), 'PSTRING_CARRIER (REQUEST_STRING n_request) $ptascii("req259")'),
        ('onlyFalse', ('mixed',), 'PBOOL false'), ('onlyTrue', ('mixed',), 'PBOOL true'),
        ('nullable', ('object','null'), 'PNULL'),
        ('selectedPrim', ('bool','float','int','string','null','object'), 'PINT 23')]}



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
            desc+'.NAME = '+named(name,'Selected259' if name=='single' else 'Wide259'),
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
                slot+'.DECL = ('+prop+'.ORIGIN)',prop+'.KEY = $ptascii("'+field+'")',prop+'.TYPE = '+union(name,names),
                prop+'.DEFAULT = PROP_UNINITIALIZED',prop+'.VISIBILITY = PROPERTY_PUBLIC',prop+'.SETVISIBILITY = eps',
                '~'+prop+'.STATIC','~'+prop+'.READONLY','~$property_hook_source_declared('+raw+','+prop+')',
                '~$property_hook_declared('+raw+','+obj+','+slot+'.NAME)',
                '$class_constant_reference_object_object_mixed_type('+prop+'.TYPE)',
                '$class_constant_reference_object_object_mixed_field_type('+raw+','+prop+','+slot+')',
                '$class_constant_reference_object_field_type('+raw+','+prop+','+slot+')']
            if expected.startswith('POBJECT'):
                child=expected.split()[1]
                actual='Middle259' if field=='middle' else 'Leaf259'
                checks += ['(HOBJECT '+child+') <- '+raw+'.ALLOCATIONS',
                    raw+'.OBJECTS['+child+'] = INSTANCE porigin_child_'+name+'_'+field,
                    '$class_at('+raw+'.CLASSES,porigin_child_'+name+'_'+field+') = (pclassdesc_child_'+name+'_'+field+')',
                    'pclassdesc_child_'+name+'_'+field+'.NAME = '+named(name,actual),
                    '$objectprops_at('+raw+'.OBJECTPROPS,'+child+') = (eps)',
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
        '~$class_constant_reference_object_scalar_value(pvalue_single_edge)',
        'n_child_vector_first = n_child_vector_last','n_child_vector_first =/= n_child_vector_middle',
        '$node_children(S_raw_vector,HOBJECT n_object_vector) = [HOBJECT n_child_vector_first,HOBJECT n_child_vector_middle,HOBJECT n_child_vector_last]',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_first) = 2',
        '$heap_owners($heap_graph(S_raw_vector),HOBJECT n_child_vector_middle) = 1',
        'pclassdesc_vector.PROPERTIES = eps',
        '$class_link_at(S_raw_vector.LINKEDPARENTS,porigin_vector) = (SOURCE_PARENT porigin_fields)',
        '$class_at(S_raw_vector.CLASSES,porigin_fields) = (pclassdesc_fields)',
        'pclassdesc_fields.PROPERTIES = ['+','.join('ppropertydesc_vector_'+f for f,_,_ in FIELDS['vector'])+']',
        'n_request = 0','S_raw_vector.STRINGDATA[n_request] = $ptascii("req259")',
        '$string_carrier_valid(S_raw_vector,pvalue_vector_request)']
    return checks


def boundaries():
    checks = []
    values = [('object','pvalue_single_edge'),('int','PINT 17'),('float','PFLOAT 4609434218613702656'),
        ('string','PSTRING_CARRIER INTERNED_STRING $ptascii("matrix259")'),
        ('false','PBOOL false'),('true','PBOOL true'),('null','PNULL')]
    groups = [('object',),('mixed',),('object','null'),('int','object'),('object','float'),
        ('string','object'),('object','bool'),('true','object'),('object','false'),
        ('bool','float','int','string','null','object')]
    for names in groups:
        type_value=union('single',names); desc='ppropertydesc_single_edge[.TYPE = '+type_value+']'
        checks += ['$class_constant_reference_object_object_mixed_type('+type_value+')']
        for tag,value in values:
            accepted='mixed' in names or tag in names or (tag in ('false','true') and 'bool' in names)
            slot='ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
            for helper in ['object_mixed_field_type','field_type']:
                checks += [('' if accepted else '~')+'$class_constant_reference_object_'+helper+'(S_class_single,'+desc+','+slot+')']
    invalid = [union('single',names) for names in [('mixed','null'),('object','mixed'),('int','mixed'),
        ('object','object'),('object','int','int'),('object','bool','false'),
        ('object','true','bool'),('object','false','true'),('object','null','null')]]
    for bad in ['array','callable','void','never','Object']:
        invalid += ['[PTBRANCH ([PTBUILTIN "object"]),PTBRANCH ([PTBUILTIN '+json.dumps(bad)+'])]']
    invalid += ['[PTBRANCH ([PTBUILTIN "object"]),PTBRANCH ([PTCLASS '+named('single','LeafBase259')+'])]',
        '[PTBRANCH ([PTBUILTIN "object"]),PTBRANCH ([PTSELF])]',
        '[PTBRANCH ([PTBUILTIN "object"]),PTBRANCH ([PTPARENT])]',
        '[PTBRANCH ([PTBUILTIN "object"]),PTBRANCH ([PTSTATIC])]',
        '[PTBRANCH ([PTBUILTIN "object",PTBUILTIN "int"])]',
        '[PTBRANCH eps,PTBRANCH ([PTBUILTIN "object"])]']
    for type_value in invalid:
        desc='ppropertydesc_single_edge[.TYPE = '+type_value+']'
        checks += ['~$class_constant_reference_object_object_mixed_type('+type_value+')',
            '~$class_constant_reference_object_object_mixed_field_type(S_class_single,'+desc+',ppropertyslot_single_edge)',
            '~$class_constant_reference_object_field_type(S_class_single,'+desc+',ppropertyslot_single_edge)']
    for type_value in ['eps',union('single',('int',)),union('single',('int','float')),
        union('single',('LeafBase259','null'))]:
        checks += ['~$class_constant_reference_object_object_mixed_type('+type_value+')']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT (PARRAY 0))','PROP_VALUE (DIRECT (POBJECT (|S_class_single.OBJECTS|)))']:
        slot='ppropertyslot_single_edge[.STATE = '+state+']'
        for helper in ['object_mixed_field_type','field_type']:
            checks += ['~$class_constant_reference_object_'+helper+'(S_class_single,ppropertydesc_single_edge,'+slot+')']
    checks += ['$typed_exact(ppropertydesc_single_edge.TYPE,PARRAY 0)',
        'S_cycle = S_class_single[.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_object_single,[ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (POBJECT n_object_single))]])]',
        '$class_constant_reference_object_object_mixed_field_type(S_cycle,ppropertydesc_single_edge,ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (POBJECT n_object_single))])',
        '~$class_constant_reference_object_graph(S_cycle,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_cycle,S_raw_single.RESULT) = eps']
    for type_value in [union('vector',('mixed',)),union('vector',('object','string'))]:
        desc='ppropertydesc_vector_request[.TYPE = '+type_value+']'
        checks += ['$class_constant_reference_object_object_mixed_field_type(S_class_vector,'+desc+',ppropertyslot_vector_request)']
        for value in ['PSTRING $ptascii("req259")',
            'PSTRING_CARRIER (REQUEST_STRING (|S_class_vector.STRINGDATA|)) $ptascii("req259")',
            'PSTRING_CARRIER INTERNED_STRING $base64("cmVxADI1OQ==")']:
            slot='ppropertyslot_vector_request[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
            for helper in ['object_mixed_field_type','field_type']:
                checks += ['~$class_constant_reference_object_'+helper+'(S_class_vector,'+desc+','+slot+')']
    checks += ['S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_object_mixed_field_type(S_retired,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        '$class_at(S_class_single.CLASSES,porigin_child_single_edge) = (pclassdesc_child)',
        'S_interface = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_child[.KIND = "interface"])]',
        '$typed_exact(ppropertydesc_single_edge.TYPE,pvalue_single_edge)',
        '~$class_constant_reference_object_object_mixed_field_type(S_interface,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        'n_invalid_owner = |S_class_single.OBJECTS|',
        'S_invalid_owner = S_class_single[.STORE = $set_cell(S_class_single.STORE,n_reference_single,DEFINED (POBJECT n_invalid_owner))][.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_invalid_owner,[ppropertyslot_single_edge])]',
        '$call_reference_operand_valid(S_invalid_owner,S_raw_single.RESULT)',
        '$class_constant_reference_object_selector(S_invalid_owner,S_raw_single.RESULT) = eps']
    return checks


def lifecycle():
    old=quoted(b'Ns257TypedClassVector\\Wide257'); new=named('vector','Wide259')
    extra=','.join('ppropertyslot_vector_'+f for f,_,_ in FIELDS['vector'][3:])
    return [c.replace(old,new).replace('257','259').replace('B|W|D|','B|W|D|N|I|F|S|F|T|N|U|')
        .replace('ppropertyslot_vector_last])','ppropertyslot_vector_last,'+extra+'])') for c in class_lifecycle()]


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
