<?php
try{try{throw new Exception("a");}finally{echo "F";throw new Error("b");}}catch(Error $e){echo "E";}catch(Exception $e){echo "X";}
