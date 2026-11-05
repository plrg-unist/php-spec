<?php
#[Deprecated]
const B=true;
#[Deprecated]
const N=null;
#[Deprecated]
const F=1.5;
set_error_handler(function($n){echo $n,"|";return true;});echo B?"bool|":"bad|",constant("N")===null?"null|":"bad|",F,"|";
