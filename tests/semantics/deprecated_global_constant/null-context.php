<?php
namespace Ns;
#[\Deprecated(message:\null,since:null)]
const X=7;
\set_error_handler(function($n,$m){echo $m,"|";return true;});echo X;
