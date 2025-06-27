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
from datetime import datetime, timedelta


# Owned
from common import ProgressBar, TXsession

class BenchmarkSyncSessionsImplicit():
    @staticmethod
    def run(number_tests: int, cypher: str, url: str, usr: str, pwd:str, db, http2: bool = False ):
        """
         Repeats a cypher statement, neo4j_cyper, for the number of times set by num_tests to the Neo4j Query API
         at neo4j_url.  The total time is returned.

         Uses Sessions so that requests share a TCP connection vs creating a connection for each request

         :param cypher - the cypher statement to run
         :param number_tests  - the number of times to execute the test
         :param url - the URL of the Neo4j Query API
         :param usr - the user account to use
         :param pwd  - the password of the user account
         :param http2 - request to use http2
         :return: total time taken
         """

        # Create an instance of TXSession as this triggers
        # the use of httpx client to allow us to re-use connections
        tx_session = TXsession(url, usr, pwd, db, http2)

        # Progress bar
        tx_progress_bar = ProgressBar("TXSyncSessions", number_tests)

        # Set the start time
        start_time = datetime.now()

        for _ in range(number_tests):

            tx_session.tx_session_implicit(cypher)

            # Update progress bar
            tx_progress_bar.add_progress_entry()

        # Destroy progress bar object
        # Make sure to do this to avoid the console
        # output showing the progress bar more than once
        # when something else is printed to the screen
        del tx_progress_bar


        # Destroy tx_session so we can free up the connection
        del tx_session

        # Set the end time
        end_time = datetime.now()

        # Work out how long the test took
        total_time: timedelta = end_time - start_time


        return total_time.total_seconds()



