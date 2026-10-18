"""Historical dynamic ancestor keys, detached child tables and nested COW."""

CASES = {
    'list-recursive-cv-review-detached-child-key-retire': b'''<?php
function list_recursive_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key 0"),":",$l,";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;$GLOBALS["outer_alias"]=9;
    unset($GLOBALS["outer"],$GLOBALS["outer_alias"]);
    $GLOBALS["outer"]=&$GLOBALS["replacement"];
    $GLOBALS["key"]=1.5;$GLOBALS["next"]=1;
    $GLOBALS["row"]=[0=>22,1=>66];$GLOBALS["a"]=[[88],9];
    unset($GLOBALS["q"]);
    return true;
}
$outer=0;$outer_alias=&$outer;$replacement=7;$key=false;$next=2;
$q=2;$row=[1=>&$q,2=>6];$a=[0=>&$row,1=>4];
$x=7;$y=8;$tail=9;$dest=100;$calls=0;
set_error_handler("list_recursive_cv_peer");
$dest=([
$outer=>[
$key=>$x,
$next=>$y
],
1=>$tail
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$tail,":",$dest[0][1],":",$dest[1],":",$a[0][0],":",$a[1],":",$row[1],":",isset($q),":",$key,":",$outer,":",$calls,";";
$y=55;$row[1]=77;
echo "A:",$y,":",$dest[0][1],":",$row[1],":",$tail,";";
unset($dest,$a,$row,$outer,$replacement);
echo "U:",isset($dest),":",isset($a),":",isset($row),":",isset($outer_alias),";";
''',
    'list-recursive-cv-review-dynamic-ancestor-prior-reference': b'''<?php
function list_recursive_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",($m==="Undefined array key 1"),":",$GLOBALS["early"],":",$GLOBALS["missing"],":",$GLOBALS["late"],";";
    $GLOBALS["outer"]="gone";$GLOBALS["middle"]="gone";
    $GLOBALS["early"]=21;$GLOBALS["missing"]=99;$GLOBALS["q"]=33;
    $GLOBALS["a"]["branch"]["deep"][1]=77;
    return false;
}
error_reporting(0);$calls=0;$outer="branch";$middle="deep";$q=2;
$leaf=[0=>5,2=>&$q];$mid=["deep"=>$leaf,1=>7];$a=["branch"=>$mid,2=>8];$copy=$a;unset($leaf,$mid);
$early=11;$missing=12;$late=13;$near=14;$tail=15;$dest=100;
set_error_handler("list_recursive_cv_peer",E_WARNING);
$dest=(list(
$outer=>list(
$middle=>list(
&$early,
$missing,
&$late
),
1=>$near
),
2=>$tail
)=
$a);
restore_error_handler();
echo "R:",$early,":",($missing===null),":",$late,":",$near,":",$tail,":",$dest["branch"]["deep"][0],":",$dest["branch"]["deep"][1],":",$copy["branch"]["deep"][0],":",isset($copy["branch"]["deep"][1]),":",$copy["branch"]["deep"][2],":",$outer,":",$middle,":",$calls,";";
$early=55;$late=44;
echo "A:",$a["branch"]["deep"][0],":",$dest["branch"]["deep"][0],":",$copy["branch"]["deep"][0],":",$a["branch"]["deep"][2],":",$dest["branch"]["deep"][2],":",$copy["branch"]["deep"][2],":",$q,";";
unset($dest,$a,$copy,$q,$early,$late);
echo "U:",isset($dest),":",isset($a),":",isset($copy),":",isset($late),";";
''',
}
