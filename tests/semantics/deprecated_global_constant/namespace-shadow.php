<?php
namespace{#[\Deprecated("global")]const X=7;}namespace Ns{\set_error_handler(function(){\define("Ns\\X",9);echo "H|",X,"|";return true;});echo X,"|",X,"|";}
