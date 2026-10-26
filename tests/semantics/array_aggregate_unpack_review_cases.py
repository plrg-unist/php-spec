"""Aggregate acquisition rejection, borrowed getter throw and closed return."""

CASES = {
    'array-aggregate-unpack-review-self-return': b'''<?php
class ArrayAggregateSelf implements IteratorAggregate {
    public function getIterator(): Traversable {
        $GLOBALS["calls"]=$GLOBALS["calls"]+1;echo "G;";
        return $this;
    }
}
$agg=new ArrayAggregateSelf();$hold=$agg;$calls=0;$dest=99;$later=7;
echo "P;";
try {
    $dest=[8,...$agg,$later++];echo "L;";
} catch (Exception $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],";";
}
echo "R:",$calls,":",$dest===99,":",$later,":",$agg===$hold,";";
unset($e,$agg,$hold,$calls,$dest,$later);
echo "U:",isset($agg),":",isset($hold),":",isset($e),";";
''',
    'array-aggregate-unpack-review-getter-supplied-throw': b'''<?php
class ArrayAggregateThrow implements IteratorAggregate {
    public function getIterator(): Traversable {
        echo "G;";unset($GLOBALS["agg"]);
        $GLOBALS["row"][0]=44;
        throw $GLOBALS["second"];
    }
}
$seed=2;$row=[$seed++];$before=$row;$agg=new ArrayAggregateThrow();$hold=$agg;
$watch=WeakReference::create($agg);$dest=99;$later=7;$second=new Exception("supplied");
echo "P;";
try {
    $dest=[$row,...$agg,$later++];echo "L;";
} catch (Exception $e) {
    echo "C:",$e===$second,":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$row[0],":",$before[0],":",$dest===99,":",$later,":",isset($agg),":",$watch->get()===$hold,";";
}
unset($e,$hold);
echo "D:",$watch->get()===null,":",$row[0],":",$before[0],":",$seed,";";
unset($seed,$row,$before,$watch,$dest,$later,$second);
echo "U:",isset($agg),":",isset($hold),":",isset($second),";";
''',
    'array-aggregate-unpack-review-closed-owning-return': b'''<?php
function array_aggregate_closed_value() {
    echo "B;";yield [$GLOBALS["seed"]++];echo "F;";
}
class ArrayAggregateClosed implements IteratorAggregate {
    public function getIterator(): Traversable {
        echo "G;";$ret=$GLOBALS["generator"];unset($GLOBALS["generator"]);
        return $ret;
    }
}
$seed=2;$generator=array_aggregate_closed_value();$watch=WeakReference::create($generator);
$generator->current();$generator->next();
$before=[$seed];$agg=new ArrayAggregateClosed();$hold=$agg;$dest=99;$later=7;
echo "P;";
try {
    $dest=[$before,...$agg,$later++];echo "L;";
} catch (Exception $e) {
    echo "E:",$e->getMessage(),":",$e->getLine(),":",$e->getPrevious()===null,":",$e->getTrace()===[],":",$watch->get()===null,";";
}
echo "R:",$dest===99,":",$later,":",$before[0],":",$seed,":",isset($generator),":",$watch->get()===null,":",$agg===$hold,";";
$before[0]=44;echo "W:",$before[0],";";
unset($e,$seed,$before,$agg,$hold,$dest,$later,$watch);
echo "U:",isset($generator),":",isset($agg),":",isset($watch),";";
''',
}
