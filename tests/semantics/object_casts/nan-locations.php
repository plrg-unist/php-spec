<?php
set_error_handler(function() { $GLOBALS['v']='made'; return true; });
$v=NAN; $o=(object)$v; $v='later'; echo 'plain:', $o->scalar, '|';
set_error_handler(function() { global $v; $v='made'; return true; });
$v=NAN; $o=(object)$v; $v='later'; echo 'introduced:', $o->scalar, '|'; $o->scalar='object-write'; echo $v, '|';
$v=NAN; $w=&$v; $o=(object)$v; $v='later'; echo 'oldref:', $o->scalar, ':', $w, '|'; unset($w,$v);
set_error_handler(function() { unset($GLOBALS['v']); echo (isset($GLOBALS['v']) ? 'still' : 'gone'), '|'; return true; });
$v=NAN; $o=(object)$v; echo 'unsetplain:', (isset($v) ? 'vset' : 'vabsent'), ':', (isset($o->scalar) ? 'oset' : 'oabsent'), '|'; foreach ($o as $k=>$item) { echo $k, '=', $item, '|'; }
set_error_handler(function() { global $v; unset($GLOBALS['v']); echo (isset($GLOBALS['v']) ? 'still' : 'gone'), '|'; return true; });
$v=NAN; $o=(object)$v; echo 'unsetintroduced:', (isset($v) ? 'vset' : 'vabsent'), ':', (isset($o->scalar) ? 'oset' : 'oabsent'), '|'; foreach ($o as $k=>$item) { echo $k, '=', $item, '|'; }
echo 'END';
