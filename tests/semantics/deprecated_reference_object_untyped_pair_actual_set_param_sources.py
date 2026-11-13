#!/usr/bin/env python3
"""Compare genuine required untyped SET Params across paired hook bodies."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_actual_set_param')

if __name__ == '__main__':
    sources.main()
