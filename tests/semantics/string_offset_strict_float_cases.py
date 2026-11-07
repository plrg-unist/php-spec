"""Strict terminal float-offset diagnostics differ from quiet BP_VAR_IS."""

CASES = {
    'string-offset-strict-float-infinite': b"<?php\n$s='ab';$k=INF; echo (int)isset($s[$k]),'|',(int)empty($s[$k]),'|',($s[$k]??'F');\n",
}
