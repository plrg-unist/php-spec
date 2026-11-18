#!/usr/bin/env python3
"""Check exact Relative class bytes, flat folds and source NULL reception."""
import base64
import json

import global_relative_case_stdclass_producer_reference_notice_state as driver

author_controls=driver.controls


def independent_controls(case):
    env,signature='pfunction_producer.ENV','pfunction_producer.SIGNATURE'
    formal=case['side']=='formal'
    role=case.get('role_index',0) if formal else 0
    parameter='psparam' if role==0 else 'psparam_last'
    def param(typename,byref=None):
        flag=str(role==1).lower() if byref is None else byref
        return 'NParam (SEQUENCE eps) (INTEGER 0) ('+typename+') (BOOLEAN '+flag+') (BOOLEAN false) '+('phpType10' if role==0 else 'phpType10_last')+' ABSENT (SEQUENCE eps) '+('metadata_parameter' if role==0 else 'metadata_parameter_last')
    def proof(typename,normalized,context=env,byref=None):
        checked=signature
        if formal:
            checked+='[.PARAMETERS = ['+('' if role==0 else 'psparam, ')+parameter+'[.TYPE = '+normalized+']'+('' if byref is None else '[.BYREF = '+byref+']')+']]'
            arguments='SEQUENCE (['+('' if role==0 else 'phpType17, ')+param(typename,byref)+'])'
            returns='phpType18'
        else:
            checked+='[.RETURNS = '+normalized+']'
            arguments,returns='phpType16',typename
        return '$reference_notice_producer_scoped_header('+context+', phpType6_producer, '+arguments+', '+returns+', '+checked+')'
    actual=driver.raw_type(case)
    lines=['~'+proof(actual,driver.normalized(case,'stdClass')),
        proof(actual,driver.normalized(case,case['relative_class'])),
        '~'+proof(actual,driver.normalized(case,case['relative_class']),env+'[.NAMESPACE = $ptascii("Other")]')]
    if case.get('nullable_first'):
        lines+=['$pfn_receive_seek(S_received_first, 1, 5000)[.COMPLETION = NORMAL] = S_receive',
            'S_received_first.OBJECTPROPS = S_receive_first.OBJECTPROPS',
            'n_first =/= n_receive']
    if formal and case['shape']=='bare':
        # A source-bound single-CV BYREF variant subsumes the old peer bare header.
        lines.append(proof(actual,driver.normalized(case,case['relative_class']),byref='true'))
    if case['shape']!='union':
        return lines

    encoded=lambda text:json.dumps(base64.b64encode(text.encode()).decode())
    def atoms(members,name,tag='NNameRelative'):
        return '['+', '.join((tag+' (BYTES '+encoded(name)+') eps') if kind=='class' else 'NIdentifier (BYTES '+encoded(kind)+') eps' for kind in members)+']'
    raw=lambda members,name: 'NUnionType (SEQUENCE ('+atoms(members,name)+')) eps'
    normalized=lambda members,name:driver.ordered.ordered.normalized(members,name)
    valid=[['class','array'],['array','class'],['class','iterable'],['iterable','class'],
        ['class','null'],['null','class'],['class','int'],['int','class'],
        ['class','array','int','float','string','null','false','callable'],
        ['iterable','int','float','class','string','null','true','callable']]
    name=case['relative_class']
    for members in valid:
        lines += [proof(raw(members,name),normalized(members,name)),
            '~'+proof(raw(members,name),normalized(members[::-1],name)),
            '~'+proof(raw(members,name),normalized(members,name.swapcase()))]
    for members in ([],['class'],['class','class'],['class','int','int'],
            ['class','bool','true'],['class','false','true'],['class','array','iterable'],
            ['class','object'],['class','mixed'],['class','void'],['class','never'],
            ['class','array','int','float','string','null','false','callable','iterable']):
        if not members and not formal:
            continue  # An empty RETURN descriptor selects the old untyped route.
        lines.append('~'+proof(raw(members,name),normalized(members,name)))
    helper='$reference_notice_producer_relative_'+('parameter' if formal else 'return')+'_union_view('
    view=lambda items,context=env,seen='false':helper+context+', '+items+', '+seen+')'
    members=case['formal_members'] if formal else case['return_members']
    for spelling in ('stdClass','STDCLASS','sTdClAsS','StDcLaSs'):
        original=atoms(members,spelling)
        canonical=atoms(members,spelling,'NNameFullyQualified')
        lines += [view(original)+' = ('+canonical+')',
            proof(raw(members,spelling),normalized(members,spelling)),
            '~'+proof(raw(members,spelling),normalized(members,spelling.swapcase()))]
    source=atoms(members,name)
    lines += [view('eps')+' = eps',
        view(source,env+'[.NAMESPACE = $ptascii("Other")]')+' = eps',
        view(source,seen='true')+' = eps',
        view(atoms(['class','class'],name))+' = eps']
    for tag in ('NName','NNameFullyQualified','NIdentifier'):
        lines.append(view(atoms(members,name,tag))+' = eps')
    relative='NNameRelative (BYTES '+encoded(name)+') eps'
    lines += [view('['+relative+', '+relative.replace('NNameRelative','NName')+']')+' = eps',
        view('['+relative+', NIntersectionType (SEQUENCE (['+relative+'])) eps]')+' = eps']
    return lines


def controls(case):
    return author_controls(case)+independent_controls(case)


if __name__=='__main__':
    driver.controls=controls
    driver.__doc__=__doc__
    raise SystemExit(0 if driver.main() else 1)
