#!/usr/bin/env python3
"""Check class/primitive union correlation, whole-type guards and physical edges."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_class_union')
sources = {'single': SOURCE / 'literal-singleton.php', 'vector': SOURCE / 'mixed-vector.php'}
NAMESPACES = {'single':'Ns258ClassUnionSingle', 'vector':'Ns258ClassUnionVector'}
PRIMITIVES = ('int','float','string','bool','false','true','null')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
atom = lambda name, value: 'PTBUILTIN ' + json.dumps(value) if value in PRIMITIVES else 'PTCLASS ' + named(name,value)
union = lambda name, values: '[' + ','.join('PTBRANCH ([' + atom(name,v) + '])' for v in values) + ']'
FIELDS = {
    'single': [('edge', ('LeafBase258','null'), 'POBJECT n_child_single_edge')],
    'vector': [('first', ('Middle258','LeafBase258'), 'POBJECT n_child_vector_first'),
        ('middle', ('LeafBase258','Middle258','int'), 'POBJECT n_child_vector_middle'),
        ('last', ('null','Middle258','LeafBase258'), 'POBJECT n_child_vector_last'),
        ('nothing', ('LeafBase258','null'), 'PNULL'),
        ('integer', ('LeafBase258','int'), 'PINT 17'),
        ('floating', ('float','LeafBase258'), 'PFLOAT 4609434218613702656'),
        ('request', ('LeafBase258','string'), 'PSTRING_CARRIER (REQUEST_STRING n_request) $ptascii("req258")'),
        ('onlyFalse', ('LeafBase258','false'), 'PBOOL false'),
        ('onlyTrue', ('true','LeafBase258'), 'PBOOL true'),
        ('boolean', ('LeafBase258','bool'), 'PBOOL false'),
        ('unknown', ('Unknown258','int'), 'PINT 23')]}


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
            desc+'.NAME = '+named(name,'Selected258' if name=='single' else 'Wide258'),
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
                '$class_constant_reference_object_class_union_type('+prop+'.TYPE)',
                '$class_constant_reference_object_class_union_field_type('+raw+','+prop+','+slot+')',
                '$class_constant_reference_object_field_type('+raw+','+prop+','+slot+')']
            if expected.startswith('POBJECT'):
                child=expected.split()[1]
                actual='Middle258' if field=='middle' else 'Leaf258'
                checks += ['(HOBJECT '+child+') <- '+raw+'.ALLOCATIONS',
                    raw+'.OBJECTS['+child+'] = INSTANCE porigin_child_'+name+'_'+field,
                    '$class_at('+raw+'.CLASSES,porigin_child_'+name+'_'+field+') = (pclassdesc_child_'+name+'_'+field+')',
                    'pclassdesc_child_'+name+'_'+field+'.NAME = '+named(name,actual),
                    '$objectprops_at('+raw+'.OBJECTPROPS,'+child+') = (eps)',
                    '$typed_object_exact('+raw+','+prop+'.TYPE,'+value+')',
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
        'n_request = 0','S_raw_vector.STRINGDATA[n_request] = $ptascii("req258")',
        '$string_carrier_valid(S_raw_vector,pvalue_vector_request)',
        '$class_named(S_raw_vector.CLASSNAMES,$ptlc('+named('vector','Unknown258')+')) = eps']
    return checks


def boundaries():
    checks = []
    values = [('int','PINT 17'),('float','PFLOAT 4609434218613702656'),
        ('string','PSTRING_CARRIER INTERNED_STRING $ptascii("matrix258")'),
        ('false','PBOOL false'),('true','PBOOL true'),('null','PNULL')]
    for kind in PRIMITIVES:
        type_value=union('single',('NotLoaded258',kind))
        desc='ppropertydesc_single_edge[.TYPE = '+type_value+']'
        checks += ['$class_constant_reference_object_class_union_type('+type_value+')']
        for tag,value in values:
            accepted=tag==kind or (tag in ('false','true') and kind=='bool')
            slot='ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
            for helper in ['class_union_field_type','field_type']:
                checks += [('' if accepted else '~')+'$class_constant_reference_object_'+helper+'(S_class_single,'+desc+','+slot+')']
    invalid = [union('single',names) for names in [
        ('LeafBase258','LeafBase258'),('LeafBase258','leafbase258','int'),
        ('LeafBase258','int','int'),('LeafBase258','bool','false'),
        ('LeafBase258','true','bool'),('LeafBase258','false','true'),
        ('LeafBase258','null','null')]]
    for bad in ['object','mixed','array','callable','void','never','String']:
        invalid += ['[PTBRANCH (['+atom('single','LeafBase258')+']),PTBRANCH ([PTBUILTIN '+json.dumps(bad)+']),PTBRANCH ([PTBUILTIN "int"])]']
    for bad_name in [b'',b'bad\x00name',b'9Bad',b'Bad\\',b'Bad\\\\Name',b'self',b'Bad\\int']:
        invalid += ['[PTBRANCH ([PTCLASS '+quoted(bad_name)+']),PTBRANCH ([PTBUILTIN "int"])]']
    invalid += ['[PTBRANCH ([PTSELF]),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTPARENT]),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTSTATIC]),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH (['+atom('single','LeafBase258')+','+atom('single','Selected258')+']),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH eps,PTBRANCH ([PTBUILTIN "int"])]']
    for type_value in invalid:
        desc='ppropertydesc_vector_integer[.TYPE = '+type_value+']'
        checks += ['~$class_constant_reference_object_class_union_type('+type_value+')',
            '~$class_constant_reference_object_class_union_field_type(S_class_vector,'+desc+',ppropertyslot_vector_integer)',
            '~$class_constant_reference_object_field_type(S_class_vector,'+desc+',ppropertyslot_vector_integer)']
    for type_value in ['eps',union('single',('LeafBase258',)),union('single',('int','float'))]:
        checks += ['~$class_constant_reference_object_class_union_type('+type_value+')']
    for names,accepted in [(('LeafBase258','null'),True),(('NotLoaded258','LeafBase258'),True),
        (('Leaf258','NotLoaded258','int'),True),(('NotLoaded258','Selected258','int'),False)]:
        desc='ppropertydesc_single_edge[.TYPE = '+union('single',names)+']'
        checks += [('' if accepted else '~')+'$class_constant_reference_object_class_union_field_type(S_class_single,'+desc+',ppropertyslot_single_edge)']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT (PBOOL false))','PROP_VALUE (DIRECT (PINT 17))','PROP_VALUE (DIRECT (PARRAY 0))',
        'PROP_VALUE (DIRECT (POBJECT n_object_single))','PROP_VALUE (DIRECT (POBJECT (|S_class_single.OBJECTS|)))']:
        slot='ppropertyslot_single_edge[.STATE = '+state+']'
        for helper in ['class_union_field_type','field_type']:
            checks += ['~$class_constant_reference_object_'+helper+'(S_class_single,ppropertydesc_single_edge,'+slot+')']
    for value in ['PSTRING $ptascii("req258")',
        'PSTRING_CARRIER (REQUEST_STRING (|S_class_vector.STRINGDATA|)) $ptascii("req258")',
        'PSTRING_CARRIER INTERNED_STRING $base64("cmVxADI1OA==")']:
        slot='ppropertyslot_vector_request[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
        for helper in ['class_union_field_type','field_type']:
            checks += ['~$class_constant_reference_object_'+helper+'(S_class_vector,ppropertydesc_vector_request,'+slot+')']
    checks += ['$class_constant_reference_object_class_union_field_type(S_class_single,ppropertydesc_single_edge,ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT PNULL)])',
        'S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_class_union_field_type(S_retired,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        '$class_named(S_class_single.CLASSNAMES,$ptlc('+named('single','LeafBase258')+')) = (porigin_target)',
        '$class_at(S_class_single.CLASSES,porigin_target) = (pclassdesc_target)',
        'S_interface = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_target[.KIND = "interface"])]',
        '$typed_object_exact(S_interface,ppropertydesc_single_edge.TYPE,pvalue_single_edge)',
        '~$class_constant_reference_object_class_union_field_type(S_interface,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '$class_constant_reference_object_class_union_field_type(S_interface,ppropertydesc_single_edge[.TYPE = '+union('single',('LeafBase258','int'))+'],ppropertyslot_single_edge[.STATE = PROP_VALUE (DIRECT (PINT 17))])',
        'n_invalid_owner = |S_class_single.OBJECTS|',
        'S_invalid_owner = S_class_single[.STORE = $set_cell(S_class_single.STORE,n_reference_single,DEFINED (POBJECT n_invalid_owner))][.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_invalid_owner,[ppropertyslot_single_edge])]',
        '$call_reference_operand_valid(S_invalid_owner,S_raw_single.RESULT)',
        '$class_constant_reference_object_selector(S_invalid_owner,S_raw_single.RESULT) = eps']
    return checks


def lifecycle():
    old=quoted(b'Ns257TypedClassVector\\Wide257'); new=named('vector','Wide258')
    extra=','.join('ppropertyslot_vector_'+f for f,_,_ in FIELDS['vector'][3:])
    return [c.replace(old,new).replace('257','258').replace('B|W|D|','B|W|D|N|I|F|S|F|T|B|U|')
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
