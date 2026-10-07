#!/usr/bin/env python3
"""Paused Generator last-owner close on the active ordinary Fiber stack."""
import generator_force_close_review as driver

ROOT = driver.ROOT
run = driver.run
CASES = {
    'active-current-local': (b'<?php\nfunction seq(){try{yield 1;echo "X";}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"F":"X";echo Fiber::getCurrent()->isRunning()?"R":"X";}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A";return 7;});$f->start();echo $f->isTerminated()?"T":"X";echo $f->getReturn(),"Z";\n', b'1FRAT7Z', 0),
    'active-current-global': (b'<?php\nfunction seq(){try{yield 1;}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"F":"X";}}$g=seq();echo $g->current();$f=new Fiber(function(){unset($GLOBALS["g"]);echo "A";});$f->start();echo "Z";\n', b'1FAZ', 0),
    'active-resumed-close': (b'<?php\nfunction seq(){try{yield 1;}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"F":"X";}}$f=new Fiber(function(){$g=seq();echo $g->current();echo Fiber::suspend("S");unset($g);echo "A";return 7;});echo $f->start(),"M";$f->resume("R");echo $f->getReturn(),"Z";\n', b'1SMRFA7Z', 0),
    'active-nested-finally': (b'<?php\nfunction seq(){try{try{yield 1;echo "X";}catch(Throwable $e){echo "C";}finally{echo "I";}}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"O":"X";}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'1IOAZ', 0),
    'active-temporary-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function seq(){try{yield from inner();}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"O":"X";}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'1IOAZ', 0),
    'active-parameter-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function seq($i){try{yield from $i;}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"O":"X";}}$f=new Fiber(function(){$i=inner();$g=seq($i);echo $g->current();unset($i);unset($g);echo "A";});$f->start();echo "Z";\n', b'1OIAZ', 0),
    'active-paused-return-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function payload(){$i=inner();$i->current();return $i;}function seq(){try{try{return payload();yield 0;}finally{echo "B";yield 1;echo "X";}}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"O":"X";}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'B1IOAZ', 0),
    'active-finally-throw-caught': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";throw new Exception("new");}}$f=new Fiber(function(){$g=seq();echo $g->current();try{unset($g);}catch(Exception $e){echo $e->getMessage(),":";echo $e->getPrevious()===null?"N":"X";echo Fiber::getCurrent()===$GLOBALS["f"]?"C":"X";}echo "A";});$f->start();echo "Z";\n', b'1Fnew:NCAZ', 0),
    'active-caller-pending': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";throw new Exception("new");}}function work(){$g=seq();echo $g->current();throw new Exception("old");}$f=new Fiber(function(){try{work();}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()->getMessage();echo Fiber::getCurrent()===$GLOBALS["f"]?"C":"X";}echo "A";});$f->start();echo "Z";\n', b'1Fnew:oldCAZ', 0),
    'active-private-scope': (b'<?php\nclass Owner {private $v=7;private function mark(){echo "M",$this->v;}function seq(){try{yield 1;}finally{$this->mark();echo self::class,":",static::class;echo Fiber::getCurrent()===$GLOBALS["f"]?"F":"X";}}}class Child extends Owner {}$f=new Fiber(function(){$c=new Child;$g=$c->seq();unset($c);echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'1M7Owner:ChildFAZ', 0),
    'active-forbidden-yield': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";yield 2;}}$f=new Fiber(function(){$g=seq();echo $g->current();try{unset($g);}catch(Error $e){echo $e->getMessage();}echo "A";});$f->start();echo "Z";\n', b'1FCannot yield from finally in a force-closed generatorAZ', 0),
    'active-from-warning': (b'<?php\nfunction notice($l,$m,$f,$n){echo Fiber::getCurrent()===$GLOBALS["f"]?"W":"X";throw new Exception("handler");}function seq(){try{yield 1;}finally{yield from $missing;}}$f=new Fiber(function(){set_error_handler("notice");$g=seq();echo $g->current();try{unset($g);}catch(Error $e){echo $e->getMessage(),":",$e->getPrevious()->getMessage();}restore_error_handler();echo "A";});$f->start();echo "Z";\n', b'1WCannot use "yield from" in a force-closed generator:handlerAZ', 0),
    'waiting-main-argument-owner': (b'<?php\nfunction seq(){try{yield 1;}finally{echo Fiber::getCurrent()===null?"N":"X";}}function hold($g){$GLOBALS["f"]->start();echo $g->current(),"H";}$g=seq();echo $g->current();$f=new Fiber(function(){unset($GLOBALS["g"]);echo "A";});hold($g);echo "Z";\n', b'1A1HNZ', 0),
    'active-array-cache-child': (b'<?php\nfunction inner(){try{yield 1;}finally{echo "I";}}function payload(){$g=inner();$g->current();return [&$g];}function seq(){try{yield from payload();}finally{echo Fiber::getCurrent()===$GLOBALS["f"]?"O":"X";}}$f=new Fiber(function(){$g=seq();$g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'OIAZ', 0),
}
DECLARATIONS = {}
UNSUPPORTED = {
    'finalizer-suspends': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";echo Fiber::suspend("S");echo "E";}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "A";});echo $f->start(),"M";$f->resume("R");echo "Z";\n', b'1FSMREAZ', 'Fiber switch during an initializer, source loader or Generator continuation', 0),
    'parked-running-generator': (b'<?php\nfunction seq(){try{echo "B";Fiber::suspend("S");yield 1;}finally{echo "F";}}$g=seq();$f=new Fiber(function(){echo $GLOBALS["g"]->current();});echo $f->start();$f->resume();unset($g);echo "Z";\n', b'BS1FZ', 'Fiber switch during an initializer, source loader or Generator continuation', 0),
    'active-user-destructor': (b'<?php\nclass Box {function __destruct(){echo "D";}}function seq($b){try{yield 1;}finally{echo "F";}}$f=new Fiber(function(){$g=seq(new Box);echo $g->current();unset($g);echo "A";});$f->start();echo "Z";\n', b'1FDAZ', 'ordinary destructor release before request stage', 0),
    'active-terminal-close': (b'<?php\nfunction seq(){try{yield 1;}finally{echo "F";exit(3);}}$f=new Fiber(function(){$g=seq();echo $g->current();unset($g);echo "X";});$f->start();echo "Z";\n', b'1F', 'Generator force-close terminal cleanup', 3),
}
WATCHED = driver.WATCHED + [
    'spec/semantics/281-fibers.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'tests/semantics/generator_fiber_close_prepare.py',
]


def main():
    driver.CASES = CASES
    driver.DECLARATIONS = DECLARATIONS
    driver.UNSUPPORTED = UNSUPPORTED
    driver.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
