# -*- coding: utf-8 -*-

__author__ = 'Jonathan Giffard'
__copyright__ = 'Copyright 2025, Neo4j'
__credits__ = ['Jonathan Giffard']
__license__ = 'MIT License'
__version__ = '0.0.1'
__maintainer__ = 'Jonathan Giffard'
__email__ = 'jon.giffard@neo4j.com'
__status__ = 'Alpha'


import inspect
# Generic/Built-in
import sys

# Other Libs


# Owned



class APIException(Exception):
    """
    Base exception for API errors that suppresses traceback information.
    """
    # Extends Exception class 
    # to stops the traceback information being shown
    def __init__(self, msg):
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__} : {1}".format(type(self), msg),
        sys.exit(self)


class MissingAccessKeyError(APIException):
    # Raised when there is a problem with the environmental variable that defines the access key for the Public API
    pass


class MissingSecretKeyError(APIException):
    # Raised when there is a problem with the environmental variable that defines the secret key for the Public API
    pass


class MissingBaseURLError(APIException):
    #Raised when there is a problem with the environmental variable that defines the URL for the Public API
    pass


class AllowlistRuleError(APIException):
    #Allow list is wrong
    pass


class UserBucketAccessListError(APIException):
    #Raised when invalid list of buckets & access is given for a cluster user
    pass


class InvalidUuidError(APIException):
    #Raised when an invalid uuid is given
    pass

class GenericHTTPError(APIException):
    # Raised for generic http errors resulting
    # from calling the API
    pass