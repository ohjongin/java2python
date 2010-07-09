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


modulePrologueHandlers = [
    'java2python.mod.simpleShebang',
    'java2python.mod.simpleDocString',
    'java2python.mod.configImports',
    'java2python.mod.commentedImports',
    'java2python.mod.commentedPackageName',
]


moduleEpilogueHandlers = [
    'java2python.mod.scriptMainStanza',
]


moduleOutputHandlers = [
    'java2python.mod.outputSubs',
]





methodDocStringHandlers = [
    'java2python.mod.simpleDocString',
]


moduleStringImports = []

moduleOutputSubs = [
#    (r'(\.self\.)', '.'),
#    (r'String\.valueOf\((.*?)\)', r'str(\1)'),
    (r'System\.out\.println\((.*)\)', r'print \1'),
    (r'System\.out\.print_\((.*?)\)', r'print \1,'),
    (r'(.*?)\.equals\((.*?)\)', r'\1 == \2'),
    (r'(.*?)\.equalsIgnoreCase\((.*?)\)', r'\1.lower() == \2.lower()'),
    (r'([\w.]+)\.size\(\)', r'len(\1)'),
    (r'(\w+)\.get\((.*?)\)', r'\1[\2]'),
#    (r'(\s)(\S*?)(\.toString\(\))', r'\1str(\2)'),
    (r'(\s)(\S*?)(\.toString\(\))', r'\1\2.__str__()'),
    (r'(\s)(\S*?)(\.toLowerCase\(\))', r'\1\2.lower()'),
    (r'(\s)(\S*?)(\.length\(\))', r'\1len(\2)'),
    (r'(.*?)IndexOutOfBoundsException\((.*?)\)', r'\1IndexError(\2)'),
    (r'\.__class__\.getName\(\)', '.__class__.__name__'),
]


modulePostParseHandlers = [
    ## update top level classes, interfaces for overloaded methods.
    'java2python.mod.overloadedClassMethods',

    ## You only need one of these:
    'java2python.mod.simpleInterfaces',
    #'java2python.mod.abcInterfaces',
    #'java2python.mod.zopeInterfaces',
]


methodExtraDecoratorHandlers = [
    'java2python.mod.maybeClassMethod',
    'java2python.mod.overloadedClassMethods',
]


classSomething = [
    ## You only need one of the following:
    'java2python.mod.simpleInterfaces',
    #'java2python.mod.abcInterfaces',
    #'java2python.mod.zopeInterfaces',
    ]

classDocStringHandlers = [
    'java2python.mod.simpleDocString',
]


classBaseHandler = 'java2python.mod.mapClassType'
enumBaseHandler = 'java2python.mod.mapClassType'
interfaceBaseHandler = 'java2python.mod.mapClassType'

enumDocStringHandlers = [
    'java2python.mod.simpleDocString',
]


enumValueHandler = 'java2python.mod.enumConstInts'
## or this one:
# enumValueHandler = 'java2python.mod.enumConstStrings'


exceptionSubMap = {
    'IndexOutOfBoundsException' : 'IndexError',
    }


typeSubstitutionMap = {
    'Boolean'          : 'bool',
    'Object'           : 'object',
    'String'           : 'str',
    'char'             : 'str',
    'double'           : 'float',
    'java.lang.String' : 'str',
}


## This enum constant handler inspects the enum block and determines
## the best handler to call.  If the enum constant contains a
## constructor, it defers to the enumConstantInstances, otherwise it
## uses the enumConstantStrings:
enumEpilogueHandler = 'java2python.mod.enumConstantSelector'


## This handler generates enum constants as instances of the enum
## class (as class attributes):
# enumEpilogueHandler = 'java2python.mod.enumConstantInstances'

## This handler generates enum constants as integers:
# enumEpilogueHandler = 'java2python.mod.enumConstantInts'

## This handler generates enum constants as strings:
# enumEpilogueHandler = 'java2python.mod.enumConstantStrings'



inputSubs = [
]

outputSubs = [
    (r'(\.self\.)', '.'),
    (r'String\.valueOf\((.*?)\)', r'str(\1)'),
    (r'System\.out\.println\((.*)\)', r'print \1'),
    (r'System\.out\.print_\((.*?)\)', r'print \1,'),
    (r'(.*?)\.equals\((.*?)\)', r'\1 == \2'),
    (r'(.*?)\.equalsIgnoreCase\((.*?)\)', r'\1.lower() == \2.lower()'),
    (r'([\w.]+)\.size\(\)', r'len(\1)'),
    (r'(\w+)\.get\((.*?)\)', r'\1[\2]'),
    (r'(\s)(\S*?)(\.toString\(\))', r'\1str(\2)'),
    (r'(\s)(\S*?)(\.toLowerCase\(\))', r'\1\2.lower()'),
    (r'(\s)(\S*?)(\.length\(\))', r'\1len(\2)'),
    (r'(.*?)IndexOutOfBoundsException\((.*?)\)', r'\1IndexError(\2)'),
    (r'\.__class__\.getName\(\)', '.__class__.__name__'),
]

## mapping of java type names to python type names.  user-defined
## configuration modules can replace and/or augment this mapping.
typeRenames = {
    'String'  : 'str',
    'Integer' : 'int',
    'Object'  : 'object',
    'Date'    : 'datetime.date',
    'int'     : 'int',
    'double'  : 'float',
    'Vector'  : 'list',
    'boolean' : 'bool',
    'char'    : 'str',
    '['       : 'list',
}


## mapping of java type values to python type values.  user-defined
## configuration modules can replace and/or augment this mapping.
typeValueMap = {
    'String'  : '""',
    'int'     : '0',
    'double'  : '0.0',
    'Vector'  : '[]',
    'boolean' : 'False',
    'str'     : '""',
    '['       : 'None',
}


## not implemented:
## move inner class definitions to the top of their outer class.
## allows the outer class to reference the inner class definition
#bubbleInnerClasses = True

## minimum parameter count to trigger indentation of parameter names
## in method declarations.  set to 0 to disable.
#minIndentParams = 5

## these handle shift right and bit shift right assignments.
#bsrHandler = 'java2python.mod.functionBsr'
#bsrHandlerAssign = 'java2python.mod.functionBsrAssign'

# etc.,
