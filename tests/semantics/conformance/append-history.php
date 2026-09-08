<?php
$a=[5=>1]; unset($a[5]); $a[]=2; foreach($a as $k=>$v) echo $k,":",$v;
