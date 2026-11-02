"""Two copied array arguments retain separate COW snapshots."""

CASES = {
    'config-generator-two-owning-array-cow-typeerror': b'''<?php
function a80ArrayBody() {
  $row=[13]; echo "Y0;"; yield 0=>$row;
  $row[0]=31; echo "M0:",$row[0],";"; yield 1=>$row;
  $row[0]=42; echo "M1:",$row[0],";";
}
function a80ArrayFactory() {
  $g=a80ArrayBody(); $GLOBALS["gw"]=WeakReference::create($g); echo "P;"; return $g;
}
$gw=null; echo "B;";
try { ini_set(...a80ArrayFactory()); echo "BAD;"; }
catch (TypeError $e) {
  $a=$e->getTrace()[0]["args"];
  echo "T:",$a[0][0],":",$a[1][0],":",(int)($gw->get()===null),";";
}
''',
}

EXPECTED = b'B;P;Y0;M0:31;M1:42;T:13:31:1;'
