#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" java2python.sourcetypes.block -> basic building block of output source code.

"""
from cStringIO import StringIO
from itertools import dropwhile
from operator import not_
from re import sub as rxsub

from java2python.config import Config

def maybeAttr(obj, name, default=None):
    return getattr(obj, name, default)


class Block:
    """ Block -> base class for source code types.

    Instances have methods to create new child instances, e.g., newClass
    to create a new class.

    This class contains some attributes only used by subclasses; their
    creation in this base type is strictly from laziness.

    """
    anonymousClassCount = 0
    classmethodLiteral = '@classmethod'
    config = None
    emptyAssign = ('%s', '<empty>')
    missingValue = ('%s', '<missing>')
    staticmethodLiteral = '@staticmethod'
    unknownExpression = ('%s', '<unknown>')

    def __init__(self, parent=None, name=None):
        self.parent = parent
        self.name = name
        self.bases = []
        self.modifiers = []
        self.preamble = []
        self.epilogue = []
        self.lines = []
        self.type = None
        self.variables = []
        self.methods = []
        ## ug.
        self.postIncDecInExprFixed = False
        self.postIncDecVars = []
        self.postIncDecCount= 0
        self.externalComments = []

    def __iter__(self):
        for line in self.lines:
            yield line

    @classmethod
    def setConfigs(cls, configs):
        ## always place it on the root so all instances of all Block
        ## types get the same object.  also means any instance of any
        ## Block type can set the config for all other instances of
        ## all Block types.  dr. seuss would have loved oop and its
        ## goop.
        Block.config = Config(*configs)

    def asString(self):
        """ asString() -> source code defined in obj

        """
        out = StringIO()
        self.dump(out, 0)
        source = out.getvalue()
        for subs in self.config.all('outputSubs', []):
            for sub in subs:
                source = rxsub(sub[0], sub[1], source)
        return source

    def dump(self, output, indent):
        """ Serialize this object to stream output.

        @param output any writable file-like object
        @param indent indentation level of this block
        @return None
        """
        offset = self.I(indent)
        for line in self:
            if isinstance(line, tuple):
                line = self.formatExpression(line)
            if hasattr(line, 'dump'):
                line.dump(output, indent)
            elif line:
                output.write('%s%s\n' % (offset, line))

    # The next set of functions are for configuring and filling the
    # block.

    def addComment(self, text, prefix='##', end=True):
        """ add a comment to this source block

        @param text value of comment
        @keyparam prefix='##' value of comment prefix
        @return None
        """
        prefix = self.config.last('commentPrefix', prefix)
        self.addSource('%s %s' % (prefix, text), end=end)

    def addModifier(self, name):
        """ add a modifier to this source block

        @param name value of modifier, as a string
        @return None
        """
        self.modifiers.append(name)

    def addSource(self, src, end=True):
        """ add source code to the end of this block

        @param src string, instance of Block (or subclass), or two-tuple
        @return None
        """
        if len(self.lines) == 1 and self.lines[0] == 'pass':
            self.lines.pop()
        if end:
            self.lines.append(src)
        else:
            self.lines.insert(0, src)

    def addSourceBefore(self, src, stat=None):
        """ add source code to the end of this block, before the last line
        or the specified statement

        @param src string, instance of Block (or subclass), or two-tuple
        @param stat Statement, insert source before this statement
        @return None
        """
        if len(self.lines):
            if isinstance(stat, int):
                idx = stat
            else:
                idx = 0 if stat == None else self.lines.index(stat)
            self.lines.insert(idx, src)
        else:
            self.lines.append(src)

    def addVariable(self, var, force=False):
        """ add variable name to set for tracking

        Variables are only added to Class instances unless the force
        parameter True.

        @param name variable as string
        @keyparam force=False, if True, always add to set
        @return None
        """
        from java2python.sourcetypes import Variable
        if not isinstance(var, Variable):
            var = Variable(var)
        if force or (var.name and self.isClass):
            self.variables.append(var)

    def addMethod(self, meth):
        self.methods.append(meth)

    # The next set of property methods are sugar for various queries
    # on a block.  Some subclasses of Block override these.

    @property
    def allParents(self):
        """ generator to provide each ancestor of this instance

        @return yields individual ancestors of this instance one at a time
        """
        previous = self.parent
        while previous:
            yield previous
            previous = previous.parent

    @property
    def allVars(self):
        """ all variables in this instance and its ancestors

        @return yields variable names from this instance and all ancestors
        """
        for obj in [self, ] + list(self.allParents):
            for v in obj.variables:
                yield v.name
            for v in obj.methods:
                yield v.name
            for v in obj.extraVars:
                yield v

    @property
    def methodVars(self):
        """ all vars declared in the current method

        @return yeilds all vars declared in the method
        """

        for obj in [self, ] + list(self.allParents):
            for v in obj.variables:
                yield v.name
            if obj.isMethod:
		break

    @property
    def instanceMembers(self):
        """ all instance members in this class

        @return yields all instance member names from this class
        """
        for obj in [self, ] + list(self.allParents):
	    if obj.isClass:
                for v in obj.variables:
                    if not v.isStatic:
                        yield v.name
                for v in obj.extraVars:
                    yield v

    @property
    def instanceMethods(self):
        """ all instance methods in this class

        @return yields all instance method names from this class
        """
        for obj in [self, ] + list(self.allParents):
	    if obj.isClass:
                for v in obj.methods:
                    if not v.isStatic:
                        yield v.name

    @property
    def staticMembers(self):
        """ all static members in this class

        @return yields static member names from this class
        """
        for obj in [self, ] + list(self.allParents):
	    if obj.isClass:
                for v in obj.variables:
                    if v.isStatic:
                        yield v.name

    @property
    def staticMethods(self):
        """ all static methods in this class

        @return yields static method names from this class
        """
        for obj in [self, ] + list(self.allParents):
	    if obj.isClass:
                for v in obj.methods:
                    if v.isStatic:
                        yield v.name

    @property
    def extraVars(self):
        """ extra variable names; subclasses can and should reimplement

        @return sequence of variable names
        """
        return []

    @property
    def blockMethods(self):
        """ all source objects that are methods

        @return generator expression with all methods in this block
        """
        return (m for m in self.lines if getattr(m, 'isMethod', False))

    @property
    def isClass(self):
        """ True if this instance is a Class

        """
	return False

    @property
    def isMethod(self):
        """ True if this instance is a Method

        """
	return False

    @property
    def isStatic(self):
        """ True if this instance is static

        @return if the variable is static return True
        """
        return 'static' in self.modifiers

    @property
    def isVariable(self):
        """ True if this instance is static

        @return if the variable is static return True
        """
        return False

    @property
    def declFormat(self):
        """ string format for variable names in this block

        """
        # seriously, wtf.
        for parent in [self, ] + list(self.allParents):
            if parent.isMethod:
                preamble = parent.preamble
                if self.staticmethodLiteral in preamble:
                    return '%s'
                elif self.classmethodLiteral in preamble:
                    return '%s'
                else:
                    return 'self.%s'
        return '%s ## ERROR'

    @property
    def nameOrClassName(self):
        return self.name if self.isClass else self.className

    @property
    def className(self):
        """

        """
        if self.parent is not None:
            return self.parent.className
	else:
            return None

    def newClass(self, name=None):
        """ creates a new Class object as a child of this block

        @keyparam name=None name of new method
        @return Class instance
        """
        from java2python.sourcetypes import Class
        c = Class(parent=self, name=name)
        self.addSource(c)
        return c

    def newForEach(self):
        s = Block(self)
        f = Statement(self, 'for')
        self.addSource(s)
        self.addSource(f)
        return s, f

    def newFor(self):
        """ creates a new 'for' Statement as a child of this block

        @return two-tuple of initializer Statement and block Statement
        """
        s = Block(self)
        f = Statement(self, 'while')
        self.addSource(s)
        self.addSource(f)
        return s, f

    def newMethod(self, name=None):
        """ creates a new Method object as a child of this block

        @keyparam name=None name of new method
        @return Method instance
        """
        from java2python.sourcetypes import Method
        m = Method(parent=self, name=name)
        self.addMethod(m)
        self.addSource(m)
        return m

    def newSwitch(self):
        """ creates a new 'if' Statement as a child of this block

        @return Statement instance
        """
        from java2python.sourcetypes import Statement
        while_stat = Statement(self, 'while')
        while_stat.setExpression('True')
        self.addSource(while_stat)
        return while_stat

    def newStatement(self, name):
        """ creates a new Statement as a child of this block

        @param name name of statement
        @return Statement instance
        """
        from java2python.sourcetypes import Statement
        s = Statement(parent=self, name=name)
        self.addSource(s)
        return s

    def newStatementAbove(self, name, stat=None):
        """ creates a new Statement as a child of this block before the last
        or the specified statement.

        @param name name of statement
        @param stat add statement before this one
        @return Statement instance
        """
        from java2python.sourcetypes import Statement
        s = Statement(parent=self, name=name)
        self.addSourceBefore(s, stat)
        return s

    def newVariable(self, name=None, force=True):
        """ creates a new Variable for the block

        @param name name of the variable
        @return Variable instance
        """
        from java2python.sourcetypes import Variable
        var = Variable(self)
        self.addVariable(var, force)
        return var

    def removeStatement(self, stat):
        """ remove a statement from source.

        @param stat Statement to be removed.
        @return None
        """
        idx = self.lines.index(stat)
        del self.lines[idx]

    ## Useful utilities.

    def trimLines(self):
        """ removes empty lines from the end of this block

        @return None
        """
        self.lines = list(reversed(list(dropwhile(not_, reversed(self.lines)))))

    def I(self, indent):
        """ calculated indentation string

        @param indent integer indentation level
        @return string of spaces
        """
        return (' ' * self.config.last('indent', 4)) * indent


    # Here are the dragons.  They are crisp and dreadful.  I wish they
    # were gone.

    def fixDecl(self, *args):
        """ fixes variable names that are class members

        @varparam args names to fix
        @return fixed name or names
        """
        fixed = list(args)
        methodvars = list(self.methodVars)
        membervars = list(self.instanceMembers) + list(self.instanceMethods)
        staticvars = list(self.staticMembers) + list(self.staticMethods)
        mapping = self.config.combined('variableNameMapping')
        format = self.declFormat
        for i, arg in enumerate(args):
            if arg in methodvars:
                arg = mapping.get(arg, arg)
                fixed[i] = arg
            elif arg in staticvars:
                arg = mapping.get(arg, arg)
                fixed[i] = "%s.%s" % (self.nameOrClassName, arg)
            elif arg in membervars:
                arg = mapping.get(arg, arg)
                fixed[i] = format % (arg, )
            else:
                fixed[i] = mapping.get(arg, arg)
        if len(fixed) == 1:
            return fixed[0]
        else:
            return tuple(fixed)

    def formatExpression(self, expr):
        """ format an expression set by the tree walker

        Expressions are either strings or nested two-tuples of
        format strings and their arguments.

        @param expr string or two-tuple
        @return interpolated, fixed expression as string
        """
        fixdecl = self.fixDecl
        if isinstance(expr, basestring):
            return expr # fixdecl(expr)
        format = self.formatExpression
        first, second = expr
        if isinstance(first, basestring) and isinstance(second, basestring):
            return fixdecl(first) % fixdecl(second)
        elif isinstance(first, basestring) and isinstance(second, tuple):
            return fixdecl(first) % format(second)
        elif isinstance(first, tuple) and isinstance(second, basestring):
            return format(first) % fixdecl(second)
        elif isinstance(first, tuple) and isinstance(second, tuple):
            return (format(first), format(second))
        else:
	    return str(expr)
            raise NotImplementedError('Unhandled expression type:  %s' % expr)

    def alternateName(self, name, key='renameAnyMap'):
        """ returns an alternate for given name

        @param name any string
        @return alternate for name if found; if not found, returns name
        """
        mapping = self.config.combined(key)
        try:
            return mapping[name]
        except (KeyError, ):
            return name


    def fixAssignInExpr(self, needFix, expr, left):
        if not needFix: return expr
        if self.name == 'if':
            self.parent.addSourceBefore(expr, self)
        elif self.name == 'while':
            self.addSource(expr)
        elif isinstance(self, Method):
            self.addSource(expr)
        return left

    def fixPostIncDecInExpr(self, needFix, expr, left, op):
        if not needFix: return expr
        if self.name == 'if':
            avar = "_%s0" % left[1]
            self.postIncDecVars.append((avar, left, op))
            self.postIncDecInExprFixed = True
            return '%s', avar
        else:
            self.postIncDecVars.append((left, op))
            self.postIncDecInExprFixed = True
            return '%s', left

    def fixPostIncDecInExprAfter(self, expr):
        if not self.postIncDecInExprFixed: return expr
        if self.name == 'if':
            for var in self.postIncDecVars:
                self.parent.addSourceBefore((var[0] + ' = %s', var[1]), self)
            for var in self.postIncDecVars:
                self.parent.addSourceBefore(('%s ' + var[2] + '= 1', var[1]), self)
        else:
            for var in self.postIncDecVars:
                left, op = var
                self.addSource(('%s ' + op + "= 1", left))
        self.postIncDecVars = []
        self.postIncDecInExprFixed = False
        return expr

    def hasAssignInExpr(self, expr):
        from lexer import ASSIGN, INC, DEC, POST_INC, POST_DEC, BAND_ASSIGN, SL_ASSIGN, BSR_ASSIGN, SR_ASSIGN, MOD_ASSIGN, DIV_ASSIGN, STAR_ASSIGN, MINUS_ASSIGN, PLUS_ASSIGN
        if expr.getType() in (ASSIGN, INC, DEC, POST_INC, POST_DEC, BAND_ASSIGN, SL_ASSIGN, BSR_ASSIGN, SR_ASSIGN, MOD_ASSIGN, DIV_ASSIGN, STAR_ASSIGN, MINUS_ASSIGN, PLUS_ASSIGN):
            return True
        child = expr.getFirstChild()
        while child:
            ret = self.hasAssignInExpr(child)
            if ret: return True
            child = child.getNextSibling()
        return False
