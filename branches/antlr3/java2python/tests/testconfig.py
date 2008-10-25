#!/usr/bin/env python
# -*- coding: utf-8 -*-


## lines written at the beginning of each generated module.  this value
## is cumulative, so when user-defined configuration modules specify
## this value, those lines are written after these.
modulePreamble = [
    'import unittest',
    'from unittest import TestCase',
    'from overloading import overloaded',
    ]

## lines written at the end of each generated module.  this value is
## cumulative, so user-defined configuration modules may specify
## additional values.
moduleEpilogue = [
    'if __name__ == "__main__":\n'
    '    unittest.main()',
    ]

variableNameMapping = {
    'Assert':'self',
    }

fixPropMethods = False