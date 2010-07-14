#!/usr/bin/env python
# -*- coding: utf-8 -*-
from keyword import kwlist

from antlr3 import Parser
from antlr3.tree import CommonTreeAdaptor

from java2python.blocks import BlockFactory
from java2python.config import Config

from java2python.parser.JavaLexer import (
    Ident as IdentType, FloatingPointLiteral, NullLiteral, BooleanLiteral
    )


class Scope(object):
    def __init__(self):
	self.stack = []

    def __len__(self):
	return len(self.stack)

    def push(self, v):
	self.stack.append(v)
	return v

    def pop(self, index=-1, default=None):
	try:
	    return self.stack.pop(index)
	except (IndexError, ):
	    return default

    @property
    def top(self):
	return self.stack[-1]


class Scopes(object):
    def __init__(self):
	self.module = Scope()
	self.block = Scope()
	self.expr = Scope()


class LocalParser(Parser):
    """ Antlr parser subclass with block factory and comment handling.

    """
    renameIdents = kwlist + ['None', 'str', ]

    def __init__(self, input, state=None):
	Parser.__init__(self, input, state=state)
	# makes instance usable when run as a script
	self.comments = []
        self.factory = BlockFactory(Config([]))
	self.nodeHandlerMap = {
	    IdentType            : self.xformIdent,
	    FloatingPointLiteral : self.xformFloat,
	    NullLiteral          : self.xformNull,
	    BooleanLiteral       : self.xformBool,
        }
	self.scope = Scopes()

    def handleNode(self, node):
	""" Special treatments for various types of nodes

	"""
	self.xformComments(node)
	xform = self.nodeHandlerMap.get(node.token.type, lambda n:None)
	xform(node)

    def xformBool(self, node):
	node.token.text = node.token.text.title()

    def xformComments(self, node):
	""" Called by the tree adapter below after each token is made

	"""
	start = node.token.start if hasattr(node, 'token') else node
	target = self.selectCommentsTarget()
	if target is None:
	    return
	for comment in self.popComments(start):
	    target.addComment(comment)

    def xformFloat(self, node):
	value = node.token.text
	node.token.text = self.fixFloatLiteral(value)

    def xformIdent(self, node):
	ident = node.token.text
	if ident in self.renameIdents:
	    node.token.text = '%s_' % (ident, )

    def xformNull(self, node):
	node.token.text = 'None'

    def selectCommentsTarget(self):
	""" Feeble attempt to locate the most appropriate block for comments

	"""
	stacks = ('expr', 'method', 'klass', 'module')
	for name in stacks:
	    stack = getattr(self, 'py_%s_stack' % name, None)
	    if stack:
		return getattr(stack[-1], name)

    def popComments(self, start):
	""" Pops and returns comments before given starting point

	"""
	comments = []
	for item in self.comments:
	    if item[0] < start:
		comments.append(item)
	    else:
		break
	for comment in comments:
	    self.comments.remove(comment)
	return comments

    def checkCommentsLeading(self, token):
	""" Handles any leading comments.

	"""
	self.xformComments(token.start)

    def checkCommentsTrailing(self):
	""" Handles any trailing comments.

	"""
	if self.comments:
	    self.xformComments(self.comments[-1][1]+1)

    def fixFloatLiteral(self, value):
        """ Turns a java float into a syntactically correct python float.

        This could be a regular function, but having it here makes it
        easily callable within the grammar.
        """
        if value.startswith('.'):
            value = '0' + value
        if value.endswith(('f', 'd')):
            value = value[:-1]
        elif value.endswith(('l', 'L')):
            value = value[:-1] + 'L'
        return value


class LocalTreeAdaptor(CommonTreeAdaptor):
    """ Antlr tree subclass with hook for checking comments.

    """
    def __init__(self, callback):
	CommonTreeAdaptor.__init__(self)
	self.callback = callback

    def createWithPayload(self, payload):
	""" Invokes commentCallback to check for comments as each node is created

	"""
        node = CommonTreeAdaptor.createWithPayload(self, payload)
	if node.token:
	    self.callback(node)
        return node
