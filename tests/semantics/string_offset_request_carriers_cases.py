"""Ordinary concatenation creates request-local quiet string-offset carriers."""

CASES = {
    'string-offset-quiet-request-base': b"<?php\n$head='a';$s=$head.'0'; echo (int)isset($s[0]),'|',(int)empty($s[0]),'|',($s[0]??'F'),'|',$s[0];\n",
    'string-offset-quiet-request-key': b"<?php\n$head='a';$s=$head.'0';$sign='-';$key=$sign.'1'; echo (int)isset($s[$key]),'|',(int)empty($s[$key]),'|',($s[$key]??'F'),'|',$s[$key];\n",
}
