#!/usr/bin/env python3
"""Plain-CV compound ADD late-alias originals through the checked source recorder."""
import addassign_cv_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
