<?php
namespace {
#[Deprecated] const X = [];
function notice194() { echo 'H|'; define('Ns194\\X', 9); return true; }
}
namespace Ns194 {
class First194 { const VALUE = X; }
class Second194 { const VALUE = X; }
set_error_handler('notice194');
echo First194::VALUE === [] ? 'E|' : 'N|';
echo First194::VALUE === [] ? 'E|' : 'N|';
echo Second194::VALUE === 9 ? 'N|' : 'E|';
}
