#!/usr/bin/env python3
"""Closure::call interactions with installed reference-return/finally semantics."""
from pathlib import Path
import copy
import closure_call_protocol as protocol

SOURCE = '<?php class A {} $x=1; $c=function &()use (&$x){try{return $x;}finally{echo "F";}}; $c->call(new A); echo $x;'
CASES = {}
for name, base in [('call-current-unused-finally-demand', 'call-reference-return-used'),
                   ('call-current-unused-finally-result', 'call-reference-result-unwrapped')]:
    CASES[name] = copy.deepcopy(protocol.CASES[base])
    CASES[name]['source'] = SOURCE

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__),))
