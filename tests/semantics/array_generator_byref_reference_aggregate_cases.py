"""Aggregate promotion of a by-reference Generator with a retargeted array cache."""

CASES = {
    'array-generator-byref-reference-aggregate-rebound': b'''<?php
function &byref_cache_returned() {
    global $row;
    echo "B;";unset($GLOBALS["cursor"]);
    try {
        yield "ref"=>$row;
        echo "N;";$GLOBALS["leaf"]=3;
        $GLOBALS["row"]=[&$GLOBALS["other"],19];$GLOBALS["other"]=11;
    } finally {echo "F;";}
}
class ByrefCacheAggregate implements IteratorAggregate {
    public function getIterator():Traversable {echo "G;";return $GLOBALS["cursor"];}
}
$leaf=2;$other=9;$row=[&$leaf,7];$cursor=byref_cache_returned();
$watch=WeakReference::create($cursor);$it=new ByrefCacheAggregate;
echo "P:",$watch->get()===$cursor,";";
$out=[4=>8,...$it,9];
echo "D:",$watch->get()===null,":",isset($cursor),";";
echo "S:",$out["ref"][0],":",$row[0],":",$leaf,":",$other,";";
$out["ref"][1]=88;$leaf=44;$other=66;
echo "R:",$out["ref"][0],":",$row[0],":",$leaf,":",$other,":",$out["ref"][1],":",$row[1],";";
unset($out,$row,$leaf,$other,$watch,$it);
echo "U:",isset($cursor),":",isset($it),":",isset($out),":",isset($row),":",isset($leaf),";";
''',
}
