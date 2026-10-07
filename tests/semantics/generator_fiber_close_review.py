#!/usr/bin/env python3
"""Independent original-source ownership and context checks for module310."""
import generator_force_close_review as driver

ROOT = driver.ROOT
run = driver.run
CASES = {
    'active-current': (b'<?php\nfunction seq(){try{yield 1;}finally{global $f;echo "F",(int)(Fiber::getCurrent()===$f),(int)$f->isRunning(),"|";}}\n$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A|";return 9;});\n$f->start();echo "M",$f->getReturn(),(int)(Fiber::getCurrent()===null);\n', b'1F11|A|M91', 0),
    'resumed-current': (b'<?php\nfunction seq(){try{yield 2;}finally{global $f;echo "F",(int)(Fiber::getCurrent()===$f),(int)$f->isRunning(),"|";}}\n$f=new Fiber(function(){$g=seq();echo $g->current();Fiber::suspend("S");unset($g);echo "A|";return 8;});\necho $f->start(),"|",(int)$f->isSuspended(),"|";$f->resume();echo "M",$f->getReturn();\n', b'2S|1|F11|A|M8', 0),
    'container-copies': (b'<?php\nfunction seq(){try{yield 3;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";}}\n$f=new Fiber(function(){$g=seq();echo $g->current();$a=[$g];$b=$a;unset($g,$a);echo "A|";unset($b);echo "B|";return 7;});\n$f->start();echo $f->getReturn();\n', b'3A|F1|B|7', 0),
    'aliased-received-cell': (b'<?php\nfunction seq(&$x){try{yield $x;}finally{$x=9;echo "F",(int)(Fiber::getCurrent()!==null),"|";}}\n$x=4;$f=new Fiber(function(){global $x;$g=seq($x);echo $g->current();$a=$g;unset($g);echo $x,"|";unset($a);echo $x,"|";return 6;});\n$f->start();echo $x,$f->getReturn();\n', b'44|F1|9|96', 0),
    'parked-caller-owner': (b'<?php\nfunction seq(){try{yield 5;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";}}\n$g=seq();echo $g->current();$f=new Fiber(function(){unset($GLOBALS["g"]);echo "A|";return 9;});\nfunction hold($held){global $f;$f->start();echo $held->current(),"H|";}hold($g);echo "Z",$f->getReturn();\n', b'5A|5H|F0|Z9', 0),
    'parked-fiber-owner': (b'<?php\nfunction seq(){try{yield 6;}finally{global $keep;echo "F",(int)(Fiber::getCurrent()!==null),(int)(Fiber::getCurrent()===$keep),"|";}}\n$g=seq();echo $g->current();$keep=new Fiber(function($held){Fiber::suspend("S");echo $held->current(),"K|";unset($held);echo "C|";return 4;});\necho $keep->start($g),"|";$drop=new Fiber(function(){unset($GLOBALS["g"]);echo "D|";return 3;});\n$drop->start();echo "M|";$keep->resume();echo "Z",$keep->getReturn(),$drop->getReturn();\n', b'6S|D|M|6K|F11|C|Z43', 0),
    'pending-throw-chain': (b'<?php\nfunction seq(){try{yield 7;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";throw new Exception("close");}}\nfunction body(){$g=seq();echo $g->current();throw new Exception("body");}\n$f=new Fiber(function(){try{body();}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()->getMessage(),"|";}return 5;});\n$f->start();echo "M",$f->getReturn();\n', b'7F1|close:body|M5', 0),
    'uncaught-close-to-caller': (b'<?php\nfunction seq(){try{yield 8;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";throw new Exception("close");}}\n$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "BAD";});\ntry{$f->start();}catch(Exception $e){echo $e->getMessage(),"|",(int)$f->isTerminated(),(int)(Fiber::getCurrent()===null);}\n', b'8F1|close|11', 0),
    'nested-active-fibers': (b'<?php\nfunction seq(){try{yield 9;}finally{global $inner,$outer;echo "F",(int)(Fiber::getCurrent()===$inner),(int)$outer->isRunning(),"|";}}\n$inner=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "I|";return 2;});\n$outer=new Fiber(function(){global $inner,$outer;echo "O|";$inner->start();echo "A",(int)(Fiber::getCurrent()===$outer),$inner->getReturn(),"|";return 3;});\n$outer->start();echo "M",$outer->getReturn();\n', b'O|9F11|I|A12|M3', 0),
    'shared-delegation': (b'<?php\nfunction leaf(){try{yield 1;}finally{echo "L",(int)(Fiber::getCurrent()!==null),"|";}}\nfunction wrap($leaf,$name){try{yield from $leaf;}finally{echo $name,(int)(Fiber::getCurrent()!==null),"|";}}\n$f=new Fiber(function(){$l=leaf();$a=wrap($l,"A");$b=wrap($l,"B");echo $a->current(),$b->current();unset($l,$a);echo "X|";unset($b);echo "Y|";return 4;});\n$f->start();echo $f->getReturn();\n', b'11A1|X|B1|L1|Y|4', 0),
    'unrelated-running-generator': (b'<?php\nfunction seq(){try{yield 2;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";}}\nfunction drive(){$g=seq();echo $g->current();unset($g);echo "D|";yield 3;return 4;}\n$f=new Fiber(function(){$d=drive();echo $d->current(),"|";$d->next();echo $d->getReturn(),"|";return 5;});\n$f->start();echo "M",$f->getReturn();\n', b'2F1|D|3|4|M5', 0),
    'forbidden-yield-keeps-fiber': (b'<?php\nfunction seq(){try{yield 4;}finally{echo "F",(int)(Fiber::getCurrent()!==null),"|";yield 5;}}\n$f=new Fiber(function(){$g=seq();echo $g->current();try{unset($g);}catch(Error $e){echo $e->getMessage(),"|",(int)(Fiber::getCurrent()!==null),"|";}return 6;});\n$f->start();echo "M",$f->getReturn();\n', b'4F1|Cannot yield from finally in a force-closed generator|1|M6', 0),
}
DECLARATIONS = {}
UNSUPPORTED = {}
WATCHED = driver.WATCHED + [
    'spec/semantics/281-fibers.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'tests/semantics/generator_fiber_close_review.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = DECLARATIONS
    driver.UNSUPPORTED = UNSUPPORTED
    driver.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
