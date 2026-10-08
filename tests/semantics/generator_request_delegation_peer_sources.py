#!/usr/bin/env python3
"""Independent request-delegation originals; outputs are provisional until run."""
import generator_force_close_review as driver


CASES = {
    'peer-request-delegate-temporary-child-before-outer': (
        b'''<?php
function innerPeerRequest(){try{yield 7;}finally{echo "I";}}
function outerPeerRequest(){try{yield from innerPeerRequest();}finally{echo "O";}}
$g=outerPeerRequest();echo "C|",$g->current(),"|";
''', b'C|7|IO', 0),
    'peer-request-delegate-parameter-retains-child-through-outer': (
        b'''<?php
function innerPeerRequest(){try{yield 7;}finally{echo "I";}}
function outerPeerRequest($inner){try{yield from $inner;}finally{echo "O";}}
$inner=innerPeerRequest();$g=outerPeerRequest($inner);unset($inner);echo "C|",$g->current(),"|";
''', b'C|7|OI', 0),
    'peer-request-delegate-shared-direct-globals-reverse': (
        b'''<?php
function innerPeerRequest(){try{yield 7;}finally{echo "I";}}
function outerPeerRequest($inner,$label){try{yield from $inner;}finally{echo $label;}}
$inner=innerPeerRequest();$a=outerPeerRequest($inner,"A");$b=outerPeerRequest($inner,"B");
echo "C|",$a->current(),":",$b->current(),"|";
''', b'C|7:7|BAI', 0),
    'peer-request-delegate-shared-reference-globals-store-order': (
        b'''<?php
function innerPeerRequest(){try{yield 7;}finally{echo "I";}}
function outerPeerRequest($inner,$label){try{yield from $inner;}finally{echo $label;}}
$inner=innerPeerRequest();$innerAlias=&$inner;$a=outerPeerRequest($inner,"A");$aa=&$a;
$b=outerPeerRequest($inner,"B");$bb=&$b;echo "C|",$a->current(),":",$b->current(),"|";
''', b'C|7:7|IAB', 0),
    'peer-request-delegate-inner-handler-cache-before-outer': (
        b'''<?php
class PayloadPeerRequest{function __destruct(){echo "D";}}
function caughtPeerRequest($e){echo "H";}
set_exception_handler("caughtPeerRequest");
function innerPeerRequest(){try{yield new PayloadPeerRequest;}finally{echo "I";throw new Exception("inner");}}
function outerPeerRequest(){try{yield from innerPeerRequest();}finally{echo "O";}}
$g=outerPeerRequest();$g->current();echo "C|";
''', b'C|IHDO', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/289-generator-delegation.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'tests/semantics/generator_request_delegation_peer_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
