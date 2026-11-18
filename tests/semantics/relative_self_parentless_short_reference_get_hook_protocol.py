#!/usr/bin/env python3
"""Check namespace-relative self through the existing same-class protocol."""
import self_parentless_short_reference_get_hook_protocol as protocol

if __name__ == '__main__':
    protocol.main('relative_self_parentless_short_reference_get_hook')
