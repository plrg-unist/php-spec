#!/usr/bin/env python3
"""Fresh request close keeps a retired typed slot until its actual decrement."""
import generator_force_close_review as driver

CASES = {
    'fresh-store-child-before-typed-slot': (
        b'''<?php
class FreshTypedHolder349 { public $child; public int $number; }
class FreshTypedChild349 { function __destruct() {
    echo "A|";
    try { $GLOBALS['r'] = 'bad'; echo "free|"; }
    catch (TypeError $error) { echo "type|"; }
} }
class FreshTypedObserver349 { function __destruct() {
    global $r, $g;
    $r = 'after';
    echo $r, "|", (int)$g->valid(), ":", (int)($g->current() === null);
} }
function fresh_typed349(&$holder) { echo "body|"; yield 1; }
$r = 7; $holder = null; $g = fresh_typed349($holder); $ga =& $g;
$observer = new FreshTypedObserver349; $oa =& $observer;
$holder = new FreshTypedHolder349;
$holder->number =& $r; $holder->child = new FreshTypedChild349;
unset($holder); echo "C|";
''', b'C|A|type|after|0:1', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/346-typed-property-slot-retirement.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_fresh_typed_slot_join_sources.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
