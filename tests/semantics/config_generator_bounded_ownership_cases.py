"""Crossed factory aliases and repeated-cell snapshots from pinned PHP."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_FILES = {
    'config-generator-bounded-factory-alias-normal': HERE / 'config_generator_bounded_factory_alias_normal.php',
    'config-generator-bounded-factory-alias-terminal-throw': HERE / 'config_generator_bounded_factory_alias_terminal_throw.php',
    'config-generator-bounded-same-cell-arrays': HERE / 'config_generator_bounded_same_cell_arrays.php',
    'config-generator-bounded-effectful-first-cell': HERE / 'config_generator_bounded_effectful_first_cell.php',
}
CASES = {name: path.read_bytes() for name, path in SOURCE_FILES.items()}
EXPECTED = {
    'config-generator-bounded-factory-alias-normal': b'B;P;Y0;Y1;M:8;T;E:1:1:99:6;A:1:8:8;L:1;U0:1;U1:0;',
    'config-generator-bounded-factory-alias-terminal-throw': b'B;P;Y0;Y1;M:8;T;S:1:1:1;L:1;U0:1;U1:0;',
    'config-generator-bounded-same-cell-arrays': b'B;Y0;Y1;T:42;A:13:31:6;',
    'config-generator-bounded-effectful-first-cell': b'B;Y0;Y1;T;D;E:4:8:6;',
}
