<?php
namespace { const X = 9; class Scope190 {} }
namespace Ns190 {
$shared = function($value = X, $tag = 0) { echo $value === 9 ? 'N|' : 'E|'; };
$scoped = $shared->bindTo(null, \Scope190::class);
$private = $scoped->bindTo(null, null); $scoped = null;
$private(tag: 1);
#[\Deprecated] const X = [];
set_error_handler(function() { echo 'H|'; return true; });
$shared(tag: 2); $private(tag: 3);
}
