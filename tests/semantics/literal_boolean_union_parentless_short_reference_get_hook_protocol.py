#!/usr/bin/env python3
"""Check literal-Boolean union headers with actual COW, aliases and owner detach."""
import builtin_union_parentless_short_reference_get_hook_protocol as prior

raw = prior.prior.raw
mask = prior.prior.mask
ORDERS = []
for literal in ('true', 'false'):
    domain = ('array', 'object', 'int', 'float', 'string', 'null', literal)
    for other in domain[:-1]:
        ORDERS.extend(((literal, other), (other, literal)))
    for length in range(3, 8):
        for start in range(7):
            order = (domain[start:] + domain[:start])[:length]
            if literal in order:
                ORDERS.extend((order, tuple(reversed(order))))
ORDERS = list(dict.fromkeys(ORDERS))


def header_fields():
    checks = []
    for members in ORDERS:
        checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')',
                   '$hook_short_reference_header(' + raw([part.upper() for part in members]) + ',' + mask(members) + ')',
                   '~$hook_short_reference_header(' + raw(list(reversed(members))) + ',' + mask(members) + ')',
                   '~$hook_short_reference_header(' + raw(members) + ',' + mask(list(reversed(members))) + ')',
                   '~$hook_short_reference_header(' + raw(members) + ',' + mask(members[:-1]) + ')']
    for length in range(2, 8):
        middle = ['array', 'object', 'int', 'float', 'string', 'null'][:length - 2]
        for left, right in (('true', 'false'), ('false', 'true'), ('bool', 'true'), ('true', 'bool'),
                            ('bool', 'false'), ('false', 'bool'), ('true', 'true'), ('false', 'false')):
            members = [left, *middle, right]
            checks += ['~$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')',
                       '~$hook_short_reference_header(' + raw([part.upper() for part in members]) + ',' + mask(members) + ')']
    for kind in ('mixed', 'iterable', 'callable', 'void', 'never', 'integer', 'resource', 'static'):
        members = ['true', kind]
        checks += ['~$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    ordinary = raw(['array', 'true', 'null'])
    for node in ('NName', 'NNameFullyQualified'):
        checks += ['~$hook_short_reference_header(' + ordinary.replace('NIdentifier', node, 1) + ',' + mask(['array', 'true', 'null']) + ')']
    for branches in ('eps', '[(PTBRANCH ([PTBUILTIN "array",PTBUILTIN "true"])),(PTBRANCH ([PTBUILTIN "true"])),(PTBRANCH ([PTBUILTIN "null"]))]',
                     '[(PTBRANCH ([PTBUILTIN "array"])),(PTBRANCH ([PTCLASS ($ptascii("true"))])),(PTBRANCH ([PTBUILTIN "null"]))]',
                     mask(['array', 'TRUE', 'null'])):
        checks += ['~$hook_short_reference_header(' + ordinary + ',' + branches + ')']
    for members in ([], ['true'], ['array', 'object', 'int', 'float', 'string', 'null', 'true', 'false']):
        checks += ['~$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    for members in (['array', 'object', 'int', 'float', 'bool', 'string'],
                    ['null', 'string', 'bool', 'float', 'int', 'object', 'array']):
        checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    # Retain each exact affected legacy expression as a positive assertion.
    for literal in ('true', 'false'):
        for members in (['int', literal, 'null'], ['string', literal]):
            checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
        for length in range(2, 6):
            members = ['array', 'object', 'int', 'float', 'bool', 'string', 'null'][:length - 1] + [literal]
            checks += ['$hook_short_reference_header(' + raw(members) + ',' + mask(members) + ')']
    return checks


if __name__ == '__main__':
    prior.STEM = 'literal_boolean_union_parentless_short_reference_get_hook'
    prior.header_fields = header_fields
    prior.main(header_report={'literal_boolean_header_tuples': len(ORDERS),
                              'promoted_prior_header_assertions': 12})
