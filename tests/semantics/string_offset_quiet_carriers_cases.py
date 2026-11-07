"""Ordinary interned string-offset bases and scalar string keys in quiet queries."""

CASES = {
    'string-offset-quiet-interned-base': b"<?php\n$s='a0'; echo (int)isset($s[0]),'|',(int)empty($s[0]),'|',($s[0]??'F'),'|',$s[0];\n",
    'string-offset-quiet-interned-key': b"<?php\n$s='a0';$key='0'; echo (int)isset($s[$key]),'|',(int)empty($s[$key]),'|',($s[$key]??'F'),'|',$s[$key];\n",
}
