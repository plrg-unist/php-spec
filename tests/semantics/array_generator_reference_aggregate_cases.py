"""Aggregate promotion to a Generator with a scalar-reference array cache."""

CASES = {
    'array-generator-reference-aggregate-alias-retained': b'''<?php
function reference_cache_returned() {
    echo "B;";unset($GLOBALS["cursor"]);
    try {
        yield "ref"=>$GLOBALS["row"];
        echo "N;";$GLOBALS["leaf"]=3;
    } finally {echo "F;";}
}
class ReferenceCacheAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$row=[&$leaf,7];$cursor=reference_cache_returned();
$watch=WeakReference::create($cursor);$it=new ReferenceCacheAggregate;
echo "P:",$watch->get()===$cursor,";";
$out=[4=>8,...$it,9];
echo "D:",$watch->get()===null,":",isset($cursor),";";
echo "B:",$out["ref"][0],":",$row[0],":",$leaf,";";
$out["ref"][1]=88;$leaf=44;
echo "R:",$out["ref"][0],":",$row[0],":",$leaf,":",$out["ref"][1],":",$row[1],";";
unset($out,$row,$leaf,$watch,$it);
echo "U:",isset($cursor),":",isset($it),":",isset($out),":",isset($row),":",isset($leaf),";";
''',
}
