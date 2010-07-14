#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Various enum handlers.  See the java2python.config.default for usage.

"""
from collections import defaultdict
from itertools import count

intmap = defaultdict(lambda: count(0).next)


def minJava(self, decl):
    if 'klass' in decl:
        #self.top.parent.lines.remove(self.top)
        #del(decl['klass'])
        decl['klass'].parent.lines.remove(decl['klass'])
        #print decl['klass'].name

    print decl
    return
    vf = self.top.makeMethod('values')
    vf.addModifier('static')
    vf.addSource('return [v for v in cls.__dict__.values() if isinstance(v, type)]')

    vf = self.top.makeMethod('valueOf')
    vf.addModifier('static')
    vf.addParameter('string', 'key')
    vf.addComment('propegate AttributeError (not IllegalArgumentExcption)')
    vf.addSource('return getattr(cls, key)')


def pyStrings(self, decl):
    """ string enums, e.g., A, B, C; becomes A, B, C = ('A', 'B', 'C')

    """
    const = decl['id']
    self.top.addSource("%s = '%s'" % (const, const))


def pyInts(self, decl):
    """ range enums, e.g,. A, B, C; becomes A, B, C = (0, 1, 2)

    """
    const = decl['id']
    next = intmap[self.top.name]
    self.top.addSource('%s = %s' % (const, next()))


def subClass(classname):
    """

    """
    def subclassAdder(self, decl):
        pass
    return subclassAdder