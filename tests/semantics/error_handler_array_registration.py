"""Callback-array shape errors use the API wording and leave registration intact."""
SOURCE = b'''<?php
function eh13array($n,$m,$f,$l) {}
function reject13($c) {try {set_error_handler($c);} catch (TypeError $e) {echo $e->getMessage(),'|';}}
set_error_handler('eh13array',512);
reject13([]);
reject13(['a'=>'MissingShape13','b'=>'method']);
reject13([1,2]);
reject13(['MissingShape13',2]);
echo get_error_handler()==='eh13array';
restore_error_handler();
'''
PREFIX = b'set_error_handler(): Argument #1 ($callback) must be a valid callback or null, '
EXPECTED = b''.join(PREFIX + reason + b'|' for reason in (
    b'array callback must have exactly two members',
    b'array callback has to contain indices 0 and 1',
    b'first array member is not a valid class name or object',
    b'second array member is not a valid method',
)) + b'1'
