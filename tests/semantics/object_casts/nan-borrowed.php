<?php
set_error_handler(function($level,$message) {
    global $v,$mode; echo 'W:', $mode, '|';
    if ($mode==='null') { $v=null; }
    elseif ($mode==='array') { $v=[9]; }
    elseif ($mode==='object') { $v=new stdClass; $v->tag='made'; }
    elseif ($mode==='unset') { unset($GLOBALS['v']); }
    else { $v='changed'; }
    return true;
});
$mode='string'; $v=NAN; $o=(object)$v; echo $o->scalar, '|';
$mode='null'; $v=NAN; $o=(object)$v; echo ($o->scalar===null ? 'null' : 'bad'), '|';
$mode='array'; $v=NAN; $o=(object)$v; echo $o->scalar[0], '|';
$mode='object'; $v=NAN; $o=(object)$v; echo $o->scalar->tag, '|';
$mode='unset'; $v=NAN; $o=(object)$v; echo (isset($o->scalar) ? 'set' : 'absent'), '|'; foreach ($o as $k=>$item) { echo 'unexpected', $k, '|'; }
$mode='captured'; $v=NAN; $o=(object)($v+0.0); echo ($o->scalar!==$o->scalar ? 'nan' : 'bad'), ':', $v, '|END';
