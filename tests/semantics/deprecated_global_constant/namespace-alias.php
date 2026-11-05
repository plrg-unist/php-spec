<?php
namespace Ns{#[\Deprecated("old")]const X=7;}namespace Other{use const Ns\X as A;\set_error_handler(function($n,$m){echo "H|",$m,"|",\ns\X,"|";return true;});echo A,"|";}
