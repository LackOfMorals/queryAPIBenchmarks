# -*- coding: utf-8 -*-

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
from common import ProgressBar, TXrequest


class BenchmarkSync:
    """
    Class to run a benchmark by executing a Cypher statement multiple times in explicit transactions using the Neo4j Query API.
    """
    @staticmethod
    def run(number_tests: int, cypher: str, url: str, usr: str, pwd:str, db: str, http2: bool = False  ):
        """
         Repeats a cypher statement, neo4j_cyper, for the number of times set by num_tests to the Neo4j Query API
         at neo4j_url.  The total time is returned.

         :param cypher - the cypher statement to run
         :param number_tests  - the number of times to execute the test
         :param url - the URL of the Neo4j Query API
         :param usr - the user account to use
         :param pwd  - the password of the user account
         :param http2 - ( optional ) request to use http2 protocol.
         :return: total time taken
         """

        # Progress bar
        tx_progress_bar = ProgressBar("TXSync", number_tests)

        # Object to handle our requests
        tx_request = TXrequest(url, usr, pwd, db)

        # Set the start time
        start_time = datetime.now()

        tx_id: str = ""
        tx_affinity: str = ""

        for _ in range(number_tests):
            # Begin our transaction
            tx_id, tx_affinity = tx_request.tx_request_id()
            
            # In our transaction context, run the cypher statement
            tx_request.tx_request_cypher(tx_id, cypher, tx_affinity)

            # Commit the transaction
    
            tx_request.tx_request_commit(tx_id, tx_affinity)

            # Update progress bar
            tx_progress_bar.add_progress_entry()

        # Destroy progress bar object
        # Make sure to do this to avoid the console
        # output showing the progress bar more than once
        # when something else is printed to the screen
        del tx_progress_bar


        # destory the object we used to handle requests
        del tx_request

        # Set the end time
        end_time = datetime.now()

        # Work out how long the test took
        total_time: timedelta = end_time - start_time


        return total_time.total_seconds()
