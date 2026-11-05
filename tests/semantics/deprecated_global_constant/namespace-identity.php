<?php
namespace Ns;
#[\Deprecated('old')]
const X=7;
\set_error_handler(function($n,$m){echo $n,"|",$m,"|";return true;});echo \NS\X,"|",\constant("\\nS\\X"),"|";
