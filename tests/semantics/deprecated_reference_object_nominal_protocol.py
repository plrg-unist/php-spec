#!/usr/bin/env python3
"""Check nominal constraints, primitive alternatives and physical release edges."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_nominal')
sources = {'single': SOURCE / 'interface-singleton.php', 'vector': SOURCE / 'dnf-vector.php'}
NAMESPACES = {'single':'Ns260NominalSingle', 'vector':'Ns260NominalVector'}
PRIMITIVES = ('int','float','string','bool','false','true','null')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda b: '$base64(' + json.dumps(base64.b64encode(b).decode()) + ')'
named = lambda name, cls: quoted((NAMESPACES[name] + chr(92) + cls).encode())
atom = lambda name, value: 'PTBUILTIN ' + json.dumps(value) if value in PRIMITIVES else 'PTCLASS ' + named(name,value)
branch = lambda name, value: 'PTBRANCH ([' + ','.join(atom(name,v) for v in (value if isinstance(value,tuple) else (value,))) + '])'
union = lambda name, values: '[' + ','.join(branch(name,v) for v in values) + ']'
FIELDS = {
    'single': [('edge', ('RootI260',), 'POBJECT n_child_single_edge')],
    'vector': [('first', (('I260','J260'),), 'POBJECT n_child_vector_first'),
        ('middle', (('MiddleBase260','I260'),), 'POBJECT n_child_vector_middle'),
        ('last', (('I260','J260'),'Absent260'), 'POBJECT n_child_vector_last'),
        ('nothing', (('I260','J260'),'null'), 'PNULL'),
        ('integer', (('Missing260','I260'),'int'), 'PINT 17'),
        ('floating', ('float',('I260','J260')), 'PFLOAT 4609434218613702656'),
        ('request', (('I260','J260'),'string'), 'PSTRING_CARRIER (REQUEST_STRING n_request) $ptascii("req260")'),
        ('onlyFalse', ('false',('I260','J260')), 'PBOOL false'),
        ('onlyTrue', (('I260','J260'),'true'), 'PBOOL true')]}


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
            desc+'.NAME = '+named(name,'Selected260' if name=='single' else 'Wide260'),
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
                '$class_constant_reference_object_nominal_type('+prop+'.TYPE)',
                '$class_constant_reference_object_nominal_field_type('+raw+','+prop+','+slot+')',
                '$class_constant_reference_object_field_type('+raw+','+prop+','+slot+')']
            if expected.startswith('POBJECT'):
                child=expected.split()[1]
                actual='Middle260' if field=='middle' else 'Leaf260'
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
        'n_request = 0','S_raw_vector.STRINGDATA[n_request] = $ptascii("req260")',
        '$string_carrier_valid(S_raw_vector,pvalue_vector_request)']
    return checks


def boundaries():
    checks = []
    cases = [(('I260',), True), (('J260',), True), (('MiddleBase260',), False),
        ((('I260','J260'),), True), ((('J260','I260'),), True),
        ((('LeafBase260','J260'),), True), ((('I260','MiddleBase260'),), False),
        ((('I260','Missing260'),), False),
        ((('Missing260','I260'),('J260','I260')), True),
        ((('I260','MiddleBase260'),('J260','I260')), True),
        (('Missing260',('I260','J260')), True),
        ((('I260','J260'),'Missing260','int'), True)]
    for names, accepted in cases:
        type_value = union('vector',names)
        desc = 'ppropertydesc_vector_first[.TYPE = '+type_value+']'
        checks += ['$class_constant_reference_object_nominal_type('+type_value+')',
            ('' if accepted else '~')+'$class_constant_reference_object_field_type(S_class_vector,'+desc+',ppropertyslot_vector_first)']
    values = [('int','PINT 17'),('float','PFLOAT 4609434218613702656'),
        ('string','PSTRING_CARRIER INTERNED_STRING $ptascii("matrix260")'),
        ('false','PBOOL false'),('true','PBOOL true'),('null','PNULL')]
    for primitive in PRIMITIVES:
        type_value = union('vector',(('Missing260','I260'),primitive))
        desc = 'ppropertydesc_vector_integer[.TYPE = '+type_value+']'
        checks += ['$class_constant_reference_object_nominal_type('+type_value+')']
        for tag, value in values:
            accepted = primitive == tag or (primitive == 'bool' and tag in ('false','true'))
            slot = 'ppropertyslot_vector_integer[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
            for helper in ['nominal_field_type','field_type']:
                checks += [('' if accepted else '~')+'$class_constant_reference_object_'+helper+'(S_class_vector,'+desc+','+slot+')']
    valid = union('vector',('bool','float','int','string','null',('I260','J260')))
    checks += ['$class_constant_reference_object_nominal_type('+valid+')',
        '$class_constant_reference_object_nominal_field_type(S_class_vector,ppropertydesc_vector_integer[.TYPE = '+valid+'],ppropertyslot_vector_integer)',
        'S_nonominal = S_class_vector[.CLASSES = eps][.CLASSNAMES = eps]',
        '$class_constant_reference_object_nominal_field_type(S_nonominal,ppropertydesc_vector_integer,ppropertyslot_vector_integer)']
    invalid = [union('vector',names) for names in [
        (('I260','I260'),'int'), (('I260','i260'),'int'),
        (('I260','J260'),'I260','int'), ('J260',('I260','J260'),'int'),
        (('I260','J260'),('J260','I260'),'int'),
        (('I260','J260','Missing260'),('J260','I260'),'int'),
        (('I260','J260'),'int','int'), (('I260','J260'),'bool','false'),
        (('I260','J260'),'true','bool'), (('I260','J260'),'false','true'),
        (('I260','int'),'int')]]
    for name in [b'',b'9Bad',b'bad\x00name',b'Bad\\',b'Bad\\\\Name',b'self',b'Bad\\int']:
        invalid += ['[PTBRANCH ([PTCLASS '+quoted(name)+',PTCLASS '+named('vector','I260')+']),PTBRANCH ([PTBUILTIN "int"])]']
    for builtin in ['object','mixed','array','callable','void','never','String']:
        invalid += ['['+branch('vector',('I260','J260'))+',PTBRANCH ([PTBUILTIN '+json.dumps(builtin)+']),PTBRANCH ([PTBUILTIN "int"])]']
    invalid += ['[PTBRANCH eps,PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTSELF,PTCLASS '+named('vector','I260')+']),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTPARENT]),PTBRANCH ([PTBUILTIN "int"])]',
        '[PTBRANCH ([PTSTATIC]),PTBRANCH ([PTBUILTIN "int"])]']
    for type_value in invalid:
        desc = 'ppropertydesc_vector_integer[.TYPE = '+type_value+']'
        checks += ['~$class_constant_reference_object_nominal_type('+type_value+')',
            '~$class_constant_reference_object_nominal_field_type(S_class_vector,'+desc+',ppropertyslot_vector_integer)',
            '~$class_constant_reference_object_field_type(S_class_vector,'+desc+',ppropertyslot_vector_integer)']
    for type_value in ['eps',union('vector',('int',)),union('vector',('int','float'))]:
        checks += ['~$class_constant_reference_object_nominal_type('+type_value+')']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference_single)',
        'PROP_VALUE (DIRECT PNULL)','PROP_VALUE (DIRECT (PINT 17))','PROP_VALUE (DIRECT (PARRAY 0))',
        'PROP_VALUE (DIRECT (POBJECT (|S_class_single.OBJECTS|)))']:
        slot = 'ppropertyslot_single_edge[.STATE = '+state+']'
        for helper in ['nominal_field_type','field_type']:
            checks += ['~$class_constant_reference_object_'+helper+'(S_class_single,ppropertydesc_single_edge,'+slot+')']
    for value in ['PSTRING $ptascii("req260")',
        'PSTRING_CARRIER (REQUEST_STRING (|S_class_vector.STRINGDATA|)) $ptascii("req260")',
        'PSTRING_CARRIER INTERNED_STRING $base64("cmVxADI2MA==")']:
        slot = 'ppropertyslot_vector_request[.STATE = PROP_VALUE (DIRECT ('+value+'))]'
        checks += ['~$class_constant_reference_object_nominal_field_type(S_class_vector,ppropertydesc_vector_request,'+slot+')']
    checks += ['S_retired = S_class_single[.ALLOCATIONS = $native_remove_one(S_class_single.ALLOCATIONS,HOBJECT n_child_single_edge)]',
        '~$class_constant_reference_object_nominal_field_type(S_retired,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '~$class_constant_reference_object_graph(S_retired,n_object_single,eps)',
        '$class_constant_reference_object_selector(S_retired,S_raw_single.RESULT) = eps',
        '$class_named(S_class_single.CLASSNAMES,$ptlc('+named('single','RootI260')+')) = (porigin_target)',
        '$class_at(S_class_single.CLASSES,porigin_target) = (pclassdesc_target)',
        'S_trait_target = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_target[.KIND = "trait"])]',
        '~$typed_object_exact(S_trait_target,ppropertydesc_single_edge.TYPE,pvalue_single_edge)',
        '~$class_constant_reference_object_nominal_field_type(S_trait_target,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        '$class_at(S_class_single.CLASSES,porigin_child_single_edge) = (pclassdesc_child)',
        'S_interface_child = S_class_single[.CLASSES = $trait_class_set(S_class_single.CLASSES,pclassdesc_child[.KIND = "interface"])]',
        '$typed_object_exact(S_interface_child,ppropertydesc_single_edge.TYPE,pvalue_single_edge)',
        '~$class_constant_reference_object_nominal_field_type(S_interface_child,ppropertydesc_single_edge,ppropertyslot_single_edge)',
        'n_invalid_owner = |S_class_single.OBJECTS|',
        'S_invalid_owner = S_class_single[.STORE = $set_cell(S_class_single.STORE,n_reference_single,DEFINED (POBJECT n_invalid_owner))][.OBJECTPROPS = $objectprops_set(S_class_single.OBJECTPROPS,n_invalid_owner,[ppropertyslot_single_edge])]',
        '$call_reference_operand_valid(S_invalid_owner,S_raw_single.RESULT)',
        '$class_constant_reference_object_selector(S_invalid_owner,S_raw_single.RESULT) = eps']
    slots = ['ppropertyslot_vector_'+f for f,_,_ in FIELDS['vector']]
    swapped = '['+','.join([slots[1],slots[0],*slots[2:]])+']'
    props = ['ppropertydesc_vector_'+f for f,_,_ in FIELDS['vector']]
    changed_props = '['+','.join([props[0]+'[.TYPE = '+union('vector',(('J260','I260'),))+']',*props[1:]])+']'
    checks += ['S_order = S_class_vector[.OBJECTPROPS = $objectprops_set(S_class_vector.OBJECTPROPS,n_object_vector,'+swapped+')]',
        '$class_constant_reference_object_graph(S_order,n_object_vector,eps)',
        '~$call_descriptors_valid(S_order)',
        '~$class_constant_reference_object_capture_entry(S_order,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)',
        'S_type = S_class_vector[.CLASSES = $trait_class_set(S_class_vector.CLASSES,pclassdesc_fields[.PROPERTIES = '+changed_props+'])]',
        '$class_constant_reference_object_graph(S_type,n_object_vector,eps)',
        '~$call_descriptors_valid(S_type)',
        '~$class_constant_reference_object_capture_entry(S_type,S_raw_vector.RESULT,expression_class_vector,expression_member_vector,z_vector,ptask_tail_vector*)']
    return checks


def lifecycle():
    old = quoted(b'Ns257TypedClassVector\\Wide257'); new = named('vector','Wide260')
    extra = ','.join('ppropertyslot_vector_'+f for f,_,_ in FIELDS['vector'][3:])
    return [c.replace(old,new).replace('257','260').replace('B|W|D|','B|W|D|N|I|F|S|F|T|')
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
