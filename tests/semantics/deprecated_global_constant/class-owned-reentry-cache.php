<?php
namespace {
#[Deprecated] const X = [];
function notice194() { echo 'H|'; define('Ns194\\X', 9); echo \Ns194\Box194::VALUE === 9 ? 'N|' : 'E|'; return true; }
}
namespace Ns194 {
class Box194 { const VALUE = X; }
set_error_handler('notice194');
echo Box194::VALUE === [] ? 'E|' : 'N|';
echo Box194::VALUE === [] ? 'E|' : 'N|';
}
