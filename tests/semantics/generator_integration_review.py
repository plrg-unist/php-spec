#!/usr/bin/env python3
"""Introduced Generator/call/ArrayAccess/Fiber integration counterexamples."""
import generator_force_close_review as driver

CASES = {'arrayaccess-private-finalizer-active-fiber': (b'<?php\nclass Cell implements ArrayAccess{public $'
                                                b'v=1;function offsetExists($k):bool{return true;}'
                                                b'function offsetGet($k):mixed{echo "G",(int)(Fibe'
                                                b'r::getCurrent()===$GLOBALS["f"]),"|";return $thi'
                                                b's->v;}function offsetSet($k,$v):void{echo $k===n'
                                                b'ull?"S":"BAD",(int)(Fiber::getCurrent()===$GLOBA'
                                                b'LS["f"]),"|";$this->v=$v;}function offsetUnset($'
                                                b'k):void{}}\nclass Holder implements ArrayAccess{p'
                                                b'ublic $child;function __construct(){$this->child'
                                                b'=new Cell;}function offsetExists($k):bool{return'
                                                b' true;}function offsetGet($k):mixed{echo "A",(in'
                                                b't)(Fiber::getCurrent()===$GLOBALS["f"]),"|";retu'
                                                b'rn $this->child;}function offsetSet($k,$v):void{'
                                                b'}function offsetUnset($k):void{}}\nclass Owner{pr'
                                                b'ivate function tag(){return self::class;}functio'
                                                b'n seq($h){try{yield 1;}finally{$h[0][]+=2;echo $'
                                                b'this->tag(),":",static::class,":",$h[0]->v,"|",('
                                                b'int)(Fiber::getCurrent()===$GLOBALS["f"]),"|";}}'
                                                b'}class Child extends Owner{public function tag()'
                                                b'{return "BAD";}}\n$f=new Fiber(function(){$o=new '
                                                b'Child;$h=new Holder;$g=$o->seq($h);unset($o,$h);'
                                                b'echo $g->current(),"|";unset($g);echo "Z|";retur'
                                                b'n 5;});$f->start();echo "M",$f->getReturn();\n',
                                                b'1|A1|G1|S1|Owner:Child:A1|3|1|Z|M5',
                                                0),
 'received-first-argument-keeps-generator': (b'<?php\nfunction seq(){try{yield 2;}finally{echo "'
                                             b'F",(int)(Fiber::getCurrent()!==null),"|";}}function '
                                             b'dropGlobal(){unset($GLOBALS["g"]);echo "D|";return 0'
                                             b';}function hold($held,$done){echo $held->current(),"'
                                             b'H|";unset($held);echo "K|";}$g=seq();echo $g->curren'
                                             b't();$f=new Fiber(function(){hold($GLOBALS["g"],dropG'
                                             b'lobal());return 7;});$f->start();echo "M",$f->getRet'
                                             b'urn();\n',
                                             b'2D|2H|F1|K|M7',
                                             0),
 'delegation-close-handler-previous-chain': (b'<?php\nfunction warn($n,$m,$f,$l){echo "H",(int)('
                                             b'Fiber::getCurrent()!==null),"|";return true;}set_err'
                                             b'or_handler("warn");function leaf(){try{yield 3;}fina'
                                             b'lly{echo $missing;echo "L",(int)(Fiber::getCurrent()'
                                             b'!==null),"|";throw new Exception("leaf");}}function '
                                             b'outer(){try{yield from leaf();}finally{echo "O",(int'
                                             b')(Fiber::getCurrent()!==null),"|";throw new Exceptio'
                                             b'n("outer");}}$f=new Fiber(function(){$g=outer();echo'
                                             b' $g->current();try{unset($g);}catch(Exception $e){ec'
                                             b'ho $e->getMessage(),":",$e->getPrevious()->getMessag'
                                             b'e(),"|";}return 8;});$f->start();echo "M",$f->getRet'
                                             b'urn();\n',
                                             b'3H1|L1|O1|outer:leaf|M8',
                                             0)}

CASES['pending-call-argument-release'] = (b'<?php\nfunction seq(){try{yield 1;}finally{echo "G|";throw new Exception("new");}}function make(){$g=seq();echo $g->current(),"|";return $g;}function fail(){throw new Exception("old");}function take($g,$v){echo "BAD";}$f=new Fiber(function(){try{take(make(),fail());}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()?$e->getPrevious()->getMessage():"none";}});$f->start();\n', b'1|G|new:old', 0)
CASES['pending-frame-array-release'] = (b'<?php\nfunction seq($tag){try{yield 1;}finally{echo $tag,"|";if($tag==="A"){throw new Exception("new");}}}\nfunction makePair(){$a=seq("A");$b=seq("B");$a->current();$b->current();return [$a,$b];}\nfunction drop(){$owned=makePair();throw new Exception("old");}\n$f=new Fiber(function(){try{drop();}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()?$e->getPrevious()->getMessage():"none","|";}return 9;});$f->start();echo "M",$f->getReturn();\n', b'A|B|new:old|M9', 0)

def main():
    driver.CASES = CASES
    driver.DECLARATIONS = {}
    driver.UNSUPPORTED = {}
    driver.WATCHED += [
        "spec/semantics/84-call-integrity.watsup", "spec/semantics/99-reference-returns.watsup",
        "spec/semantics/270-eager-destructors.watsup", "spec/semantics/291-fiber-lifecycle.watsup",
        "spec/semantics/292-arrayaccess-write-dimensions.watsup", "spec/semantics/296-weak-references.watsup",
        "spec/semantics/302-fiber-callback-retirement.watsup", "spec/semantics/304-arrayaccess-append-dimensions.watsup",
        "spec/semantics/310-generator-fiber-close.watsup", "tests/semantics/generator_integration_review.py",
    ]
    return driver.main()


if __name__ == "__main__":
    raise SystemExit(main())
