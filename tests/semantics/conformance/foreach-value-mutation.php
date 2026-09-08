<?php
$a=[1,2]; foreach($a as $k=>$v) {echo $v; if($k===0){$a[1]=8; $a[]=9;}} echo ":"; foreach($a as $v)echo $v;
