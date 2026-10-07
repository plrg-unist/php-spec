#!/usr/bin/env python3
"""Arrow Generator/default/Fiber/dynamic-source interaction on the current parent."""
import generator_force_close_review as driver

CASES = {
    'default-fiber-eval-entry-and-child-close': (
        b'''<?php
class Default311 {
    function __construct(){echo "D",(int)(Fiber::getCurrent()!==null),"|";}
}
class Source311 {
    function __toString():string {
        echo "S|";
        return "function ready311(){echo 'R|';}\\n\\necho\\n \\$x;";
    }
    function __destruct(){ready311();throw new Exception("released");}
}
function source311(){return new Source311;}
function leaf311($default,$x){
    try {
        try {eval(source311());}
        catch(Exception $error){$trace=$error->getTrace();echo "E",$trace[0]["line"],"|";}
        yield $x;
    } finally {echo "L",(int)(Fiber::getCurrent()!==null),"|";}
}
$fiber=new Fiber(function(){
    $arrow=fn($default=new Default311):iterable=>yield from leaf311($default,5);
    echo "A|";$generator=$arrow();unset($arrow);echo "C|";
    echo $generator->current(),"|";unset($generator);echo "F|";return 9;
});
$fiber->start();echo "M",$fiber->getReturn();
''',
        b'A|D1|C|S|R|E4|5|L1|F|M9', 0),
}


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        'spec/semantics/84-call-integrity.watsup',
        'spec/semantics/95-typed-calls.watsup',
        'spec/semantics/117-arrow-compiler.watsup',
        'spec/semantics/118-arrows.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/285-default-new-autoload.watsup',
        'spec/semantics/291-fiber-lifecycle.watsup',
        'spec/semantics/298-source-stringable-lifetime.watsup',
        'spec/semantics/302-fiber-callback-retirement.watsup',
        'spec/semantics/308-fiber-protected-completion.watsup',
        'spec/semantics/310-generator-fiber-close.watsup',
        'spec/semantics/311-arrow-generators.watsup',
        'spec/semantics/314-source-expression-emission.watsup',
        'tests/semantics/arrow_generator_integration.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
