"""Strict terminal float-offset diagnostics differ from quiet BP_VAR_IS."""

CASES = {
    'string-offset-strict-float-infinite': b"<?php\n$s='ab';$k=INF; echo (int)isset($s[$k]),'|',(int)empty($s[$k]),'|',($s[$k]??'F');\n",
    'string-offset-strict-float-out-of-range': b"<?php\n$s='a0';$k=9223372036854775808.0; echo (int)isset($s[$k]),'|',(int)empty($s[$k]),'|',($s[$k]??'F'),';';\n$k=18446744073709551616.0; echo (int)isset($s[$k]),'|',(int)empty($s[$k]),'|',($s[$k]??'F');\n",
}
