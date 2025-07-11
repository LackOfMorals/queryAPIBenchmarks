# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Jonathan Giffard'
__copyright__ = 'Copyright 2025, Neo4j'
__credits__ = ['Jonathan Giffard']
__license__ = 'MIT License'
__version__ = '0.0.1'
__maintainer__ = 'Jonathan Giffard'
__email__ = 'jon.giffard@neo4j.com'
__status__ = 'Alpha'

# Generic / built in
import sys

# Owned
from .customExceptions import APIException


def query_api_errors(response_errors: dict):
    """
    Handles and prints error messages from a Neo4j Query API response.

    Args:
        response_errors (dict): A list of error entries returned by the API, 
                                where each entry is expected to be a dictionary 
                                containing at least 'code' and 'message' keys.

    Raises:
        ConnectionError: If there are any connection-related errors.
    """

    try:
        for error_entry in response_errors:
            error_code = error_entry['code']
            match error_code:
                case "Neo.ClientError.Database.DatabaseNotFound":
                    print(f"{error_entry['message']}")
                    sys.exit(1)

                case "Neo.ClientError.Security.Unauthorized":
                    print(f"{error_entry['message']}")
                    sys.exit(1)

                case "Neo.ClientError.Request.Invalid":
                    print(f"{error_entry['message']}")
                    sys.exit(1)

                case "Neo.TransientError.Request.ResourceExhaustion":
                    print(f"{error_entry['message']}")
                    sys.exit(1)

                case "Neo.ClientError.Security.AuthenticationRateLimit":
                    print(f"{error_entry['message']}")
                    sys.exit(1)

                case _:
                    print(f"Error from Query API: {error_entry}")
                    sys.exit(1)

            raise APIException(error_entry['message'])
    
    
    except Exception as e:
            raise APIException(e) from e
    

