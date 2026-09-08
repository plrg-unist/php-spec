"""Bounded-depth JSON wire representation for deep, otherwise unchanged ASTs."""
import json

TAG = 'php-flat-1'

def deep(value, limit=256):
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        if depth > limit:
            return True
        if isinstance(item, dict):
            pending.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            pending.extend((child, depth + 1) for child in item)
    return False

def flatten(value):
    values = [value]
    index = 0
    while index < len(values):
        item = values[index]
        if isinstance(item, (list, dict)):
            children = list(item.values()) if isinstance(item, dict) else item
            refs = list(range(len(values), len(values) + len(children)))
            values.extend(children)
            values[index] = [2, list(map(list, zip(item, refs)))] if isinstance(item, dict) else [1, refs]
        else:
            values[index] = [0, item]
        index += 1
    return {'wire': TAG, 'root': 0, 'values': values}

def inflate(value):
    if not isinstance(value, dict) or value.get('wire') != TAG:
        return value
    if set(value) != {'wire', 'root', 'values'} or type(value['root']) is not int or value['root'] != 0:
        raise ValueError('invalid flat wire header')
    rows = value['values']
    if not isinstance(rows, list) or not rows:
        raise ValueError('invalid flat wire rows')
    result = [None] * len(rows)
    def child(ref, index):
        if type(ref) is not int or not index < ref < len(rows):
            raise ValueError('invalid flat wire reference')
        return result[ref]
    for index in range(len(rows) - 1, -1, -1):
        row = rows[index]
        if not isinstance(row, list) or len(row) != 2 or type(row[0]) is not int:
            raise ValueError('invalid flat wire row')
        kind, payload = row
        if kind == 0 and not isinstance(payload, (dict, list)):
            result[index] = payload
        elif kind == 1 and isinstance(payload, list):
            result[index] = [child(ref, index) for ref in payload]
        elif kind == 2 and isinstance(payload, list):
            if any(not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not str for pair in payload):
                raise ValueError('invalid flat object field')
            if len({key for key, _ in payload}) != len(payload):
                raise ValueError('duplicate flat object key')
            result[index] = {key: child(ref, index) for key, ref in payload}
        else:
            raise ValueError('invalid flat wire row')
    return result[0]

def dumps(value):
    return json.dumps(flatten(value) if deep(value) else value, separators=(',', ':'))

def loads(text):
    return inflate(json.loads(text))

def equal(left, right):
    pending = [(left, right)]
    while pending:
        left, right = pending.pop()
        if type(left) is not type(right):
            return False
        if isinstance(left, dict):
            if left.keys() != right.keys():
                return False
            pending.extend((value, right[key]) for key, value in left.items())
        elif isinstance(left, list):
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif left != right:
            return False
    return True
