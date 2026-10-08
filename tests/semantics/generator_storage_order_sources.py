#!/usr/bin/env python3
"""Closure and raw cache retirement at genuine closed Generator storage free."""
import generator_force_close_review as driver
import generator_request_fresh_peer_sources as peer

CASES = {
    'peer-reacquired-generator-releases-closure-before-cache': peer.CASES['peer-reacquired-generator-releases-closure-before-cache'],
    'closed-generator-ordinary-release-closure-before-cache': (
        b'''<?php
class Capture349{function __destruct(){echo "C";}}
class Value349{function __destruct(){echo "V";}}
$capture=new Capture349;$value=new Value349;
$fn=function(&$value)use(&$capture){yield 1;return $value;};
$g=$fn($value);unset($fn);$g->current();$g->next();
unset($capture,$value);echo "C|";unset($g);
''', b'C|CV', 0),
    'closed-generator-cache-throw-replaces-capture-throw': (
        b'''<?php
class Capture349{function __destruct(){echo "C";throw new Exception("capture");}}
class Value349{function __destruct(){echo "V";throw new Exception("value");}}
$capture=new Capture349;$value=new Value349;
$fn=function(&$value)use(&$capture){yield 1;return $value;};
$g=$fn($value);unset($fn);$g->current();$g->next();unset($capture,$value);
echo "C|";try{unset($g);}catch(Exception $e){echo "E",$e->getMessage(),":",$e->getPrevious()->getMessage();}
''', b'C|CVEvalue:capture', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_request_fresh_peer_sources.py',
        'tests/semantics/generator_storage_order_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
