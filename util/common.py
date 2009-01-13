"""
Commonly used utilities
"""

import os, sys, re
from arguments import isIterable as _isIterable
from re import escape 

#-----------------------------------------------
#  Pymel Internals
#-----------------------------------------------


def capitalize(s):
    """
    Python's string 'capitalize' method is NOT equiv. to mel's capitalize, which preserves
    capital letters.
        >>> capitalize( 'fooBAR' )
        'FooBAR'
        >>> 'fooBAR'.capitalize()
        'Foobar'
    
    :rtype: string
    """
    return s[0].upper() + s[1:]

def uncapitalize(s, preserveAcronymns=False):
    """preserveAcronymns enabled ensures that 'NTSC' does not become 'nTSC'
    :rtype: string
    
    """
    try:
        if preserveAcronymns and s[0:2].isupper():
            return s
    except IndexError: pass
    
    return s[0].lower() + s[1:]
                        
def unescape( s ):
    """
    :rtype: string
    """
    chars = [ r'"', r"'" ]
    for char in chars:
        tokens = re.split( r'(\\*)' + char,  s )
        for i in range(1,len(tokens),2 ):
            if tokens[i]:
                tokens[i] = tokens[i][:-1]+'"'
        s = ''.join(tokens)
    return s

def cacheProperty(getter, attr_name, fdel=None, doc=None):
    """a property type for getattr functions that only need to be called once per instance.
        future calls to getattr for this property will return the previous non-null value.
        attr_name is the name of an attribute in which to store the cached values"""
    def fget(obj):
        val = None
    
        if hasattr(obj,attr_name):            
            val = getattr(obj, attr_name)
            #print "cacheProperty: retrieving cache: %s.%s = %s" % (obj, attr_name, val)
            
        if val is None:
            #print "cacheProperty: running getter: %s.%s" %  (obj, attr_name)
            val = getter(obj)
            #print "cacheProperty: caching: %s.%s = %s" % (obj, attr_name, val)
            setattr(obj, attr_name, val )
        return val
                
    def fset(obj, val):
        #print "cacheProperty: setting attr %s.%s=%s" % (obj, attr_name, val)
        setattr(obj, attr_name, val)

    return property( fget, fset, fdel, doc)

def moduleDir():
    """
    Returns the base pymel directory.
    :rtype: string
    """
    return os.path.dirname( os.path.dirname( sys.modules[__name__].__file__ ) )
    
def timer( command='pass', number=10, setup='import pymel' ):
    import timeit
    t = timeit.Timer(command, setup)
    time = t.timeit(number=number)
    print "command took %.2f sec to execute" % time
    return time
    
def toZip( directory, zipFile ):
    """Sample for storing directory to a ZipFile"""
    import zipfile

    zipFile = path(zipFile)
    if zipFile.exists(): zipFile.remove()
    
    z = zipfile.ZipFile(
        zipFile, 'w', compression=zipfile.ZIP_DEFLATED
    )
    if not directory.endswith(os.sep):
        directory += os.sep
        
    directory = path(directory)
    
    for subdir in directory.dirs('[a-z]*') + [directory]: 
        print "adding ", subdir
        for fname in subdir.files('[a-z]*'):
            archiveName = fname.replace( directory, '' )            
            z.write( fname, archiveName, zipfile.ZIP_DEFLATED )
    z.close()
    return zipFile



# TODO : expand environment variables when testing if it already exists in the list
def appendEnv( env, value ):
    """append the value to the environment variable list ( separated by ':' on osx and linux and ';' on windows).
    skips if it already exists in the list"""
    sep = os.path.pathsep
    if env not in os.environ:
        #print "adding", env, value
        os.environ[env] = value
    else:
        splitEnv = os.environ[env].split(sep)
        if value not in splitEnv:
            splitEnv.append(value)
            #print "adding", env, value
            os.environ[env] = sep.join( splitEnv )   
    # i believe os.putenv is triggered by modifying os.environ, so this should not be necessary ?
    #if put :
    #    os.putenv(env, os.environ[env])

def prependEnv( env, value ):
    """prepend the value to the environment variable list (separated by ':' on osx and linux and ';' on windows). 
    skips if it already exists in the list"""
    sep = os.path.pathsep
    if env not in os.environ:
        #print "adding", env, value
        os.environ[env] = value
    else:
        splitEnv = os.environ[env].split(sep)
        if value not in splitEnv:
            splitEnv.insert(0,value)
            #print "adding", env, value
            os.environ[env] = sep.join( splitEnv ) 
              
def getEnv( env, default=None ):
    "get the value of an environment variable.  returns default (None) if the variable has not been previously set."
    return os.environ.get(env, default)

def getEnvs( env, default = None ):
    "get the value of an environment variable split into a list.  returns default ([]) if the variable has not been previously set."
    try:
        return os.environ[env].split(os.path.pathsep)
    except KeyError:
        if default is None:
            return list()
        else:
            return default


def putEnv( env, value ):
    """set the value of an environment variable.  overwrites any pre-existing value for this variable. If value is a non-string
    iterable (aka a list or tuple), it will be joined into a string with the separator appropriate for the current system."""
    if _isIterable(value):
        value = os.path.pathsep.join(value)
    os.environ[env] = value
