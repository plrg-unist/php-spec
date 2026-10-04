<?php
$a = [0=>'zero', -2=>'neg', '08'=>'eight', ''=>'empty', "\0x"=>'nul', "middle\0tail"=>'mid'];
$o = (object)$a;
foreach ($o as $k=>$v) { echo ($k === '0' ? 'str0' : ($k === '-2' ? 'strneg' : $k)), '=', $v, '|'; }
echo $o->{'0'}, ':', $o->{'-2'}, ':', $o->{'08'}, ':', $o->{''}, '|';
$name = "\0x"; echo (isset($o->{$name}) ? 'yes' : 'no'), '|';
try { echo $o->{$name}; } catch (Error $e) { echo $e->getMessage(), '|'; }
$b = (array)$o;
foreach ($b as $k=>$v) { echo ($k === 0 ? 'int0' : ($k === -2 ? 'intneg' : $k)), '=', $v, '|'; }
$b[]='append'; echo $b[1], '|END';
