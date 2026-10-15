#!/usr/bin/env python3
"""Compound ADD warning/store originals through the checked source recorder."""
import addassign_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
