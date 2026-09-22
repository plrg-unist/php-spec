"""State assertions preserving legacy diagnostic checks through owned Throwables."""

import re


def uncaught_assertions(state, kind, message, line):
    suffix = state.lower()
    obj = 'n_uncaught_' + suffix
    payload = 'pthrowable_' + suffix
    return [
        f'{state}.COMPLETION = UNCAUGHT {obj}',
        f'{state}.OBJECTS[{obj}] = THROWABLE {payload}',
        f'{payload}.KIND = {kind}',
        f'{payload}.MESSAGE = PSTRING {message}',
        f'{payload}.LINE = {line}',
        f'{state}.TRACE = {payload}.TRACE',
        f'{state}.ERRORORIGIN = {payload}.ORIGIN',
        f'$heap_valid($heap_graph({state}))',
        f'$($heap_owners($heap_graph({state}), HOBJECT {obj}) > 0)',
    ]


def completion_assertions(state, completion):
    """Translate only the retained suites' NORMAL or literal THROWN forms."""
    if completion == 'NORMAL':
        return [f'{state}.COMPLETION = NORMAL']
    match = re.fullmatch(
        r'THROWN ("[A-Za-z][A-Za-z0-9]*") (\(\[(?:[0-9]+(?:,[0-9]+)*)?\]\)|n_message\*) ([0-9]+)',
        completion,
    )
    if match is None:
        raise ValueError('Unknown test completion: ' + completion)
    kind, message, line = match.groups()
    if message.startswith('(['):
        values = message[2:-2]
        if values and any(int(value) > 255 for value in values.split(',')):
            raise ValueError('Non-byte test diagnostic: ' + completion)
    return uncaught_assertions(state, kind, message, line)
