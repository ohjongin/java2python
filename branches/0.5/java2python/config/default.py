#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
#
# This is the default configuration file for java2python.  Unless
# explicity disabled with the '-n' or '--nodefaults' options, the j2py
# script will reference this file for runtime configuration.
#
# The j2py script accepts additional configuration modules with the
# '-c' or '--config' arguments.  These arguments may be repeated.
#
# There are three flavors of options: every, last, and combined.  The
# semantics are:
#
#  * every means the value is loaded from each configuration module and
#    returned as a sequence.
#
#  * last means the value is selected from the last configuration
#    module specified.  if no configuration modules are specified (and
#    if the default is not disabled), the last value will be the value
#    in this module.
#
#  * combined means that the values (dictionaries) will be merged in
#    order and returned as a single dictionary.
#
# In some cases, noted below, the value or values may be a dotted path
# to a python value.  In these cases, the value is imported as needed.


## leading indent characters (or character).  this is a "last" option.
leadingIndent = '    '


## prefix for comments.  this is a "last" option.
commentPrefix = '## '


## this is an 'every' handler sequence
modulePrologueHandlers = [
    'java2python.mod.simpleShebang',
    'java2python.mod.simpleDocString',
    'java2python.mod.configImports',
    'java2python.mod.commentedImports',
    'java2python.mod.commentedPackageName',
]

## this is an 'every' handler sequence
moduleEpilogueHandlers = [
    'java2python.mod.scriptMainStanza',
]

## ???
moduleOutputHandlers = [
    'java2python.mod.outputSubs',
]

## handlers for doc strings.
classDocStringHandlers = [
    'java2python.mod.simpleDocString',
]
enumDocStringHandlers = [
    'java2python.mod.simpleDocString',
]
methodDocStringHandlers = [
    'java2python.mod.simpleDocString',
]


## extra decorator methods
methodExtraDecoratorHandlers = [
    'java2python.mod.maybeClassMethod',
    'java2python.mod.overloadedClassMethods',
]





## these next 4 handler values should get morphed into lists.

classBaseHandler = 'java2python.mod.mapClassType'
enumBaseHandler = 'java2python.mod.mapClassType'
interfaceBaseHandler = 'java2python.mod.mapClassType'

##
# Note that the following two enum value handlers are only called for
# basic enumerations, not enumerations that take arguments in a
# constructor.  When those kinds of enum values are detected, the
# package will create the enum values as instance of the enum class,
# and these handlers will not be invoked.

# This handler creates enum values on enum classes after they've been
# defined.  The handler matches Java semantics fairly closely by using
# strings.
enumValueHandler = 'java2python.mod.enumConstStrings'

# Alternatively, you can use this handler to construct enum values as
# integers.
#enumValueHandler = 'java2python.mod.enumConstInts'



## not implemented:

## interfaceWhateverHandlers = []
## move inner class definitions to the top of their outer class.
## allows the outer class to reference the inner class definition
#bubbleInnerClasses = True

## minimum parameter count to trigger indentation of parameter names
## in method declarations.  set to 0 to disable.
#minIndentParams = 5

## these handle shift right and bit shift right assignments.
#bsrHandler = 'java2python.mod.functionBsr'
#bsrHandlerAssign = 'java2python.mod.functionBsrAssign'


##
# Below are values used by the handlers.  They're here for
# convenience.


## module output subs.
moduleOutputSubs = [
    (r'System\.out\.println\((.*)\)', r'print \1'),
    (r'System\.out\.print_\((.*?)\)', r'print \1,'),
    (r'(.*?)\.equals\((.*?)\)', r'\1 == \2'),
    (r'(.*?)\.equalsIgnoreCase\((.*?)\)', r'\1.lower() == \2.lower()'),
    (r'([\w.]+)\.size\(\)', r'len(\1)'),
    (r'(\w+)\.get\((.*?)\)', r'\1[\2]'),
    (r'(\s)(\S*?)(\.toString\(\))', r'\1\2.__str__()'),
    (r'(\s)(\S*?)(\.toLowerCase\(\))', r'\1\2.lower()'),
    (r'(\s)(\S*?)(\.length\(\))', r'\1len(\2)'),
    (r'(.*?)IndexOutOfBoundsException\((.*?)\)', r'\1IndexError(\2)'),
    (r'\.__class__\.getName\(\)', '.__class__.__name__'),
    (r'\.getClass\(\)', '.__class__'),
    (r'\.getName\(\)', '.__name__'),
    (r'\.getInterfaces\(\)', '.__bases__'),
    #(r'(\.self\.)', '.'),
    #(r'String\.valueOf\((.*?)\)', r'str(\1)'),
    #(r'(\s)(\S*?)(\.toString\(\))', r'\1str(\2)'),
]


## TODO:  stop using 'combined' to define this.
exceptionSubMap = {
    'IndexOutOfBoundsException' : 'IndexError',
}

## TODO: stop using 'combined' to define this.
typeSubstitutionMap = {
    'Boolean'          : 'bool',
    'Object'           : 'object',
    'String'           : 'str',
    'char'             : 'str',
    'double'           : 'float',
    'java.lang.String' : 'str',
}
