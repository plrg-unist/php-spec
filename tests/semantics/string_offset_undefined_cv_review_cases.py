"""An accepting handler leaves the initially undefined key CV undefined."""

CASES = [{
    'id': 'undefined-cv-accepting-no-write-review',
    'source': '''<?php
function undefinedStringReview($level, $message) {
    echo "H:", $message, ";";
    return true;
}
set_error_handler('undefinedStringReview', 2);
$result = 'abc'[$missing];
echo "R:", $result, ";Z;";
''',
    'expected_stdout': 'H:Undefined variable $missing;H:String offset cast occurred;R:a;Z;',
}]
