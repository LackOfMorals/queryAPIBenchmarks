# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__ = 'Jonathan Giffard'
__copyright__ = 'Copyright 2025, Neo4j'
__credits__ = ['Jonathan Giffard']
__license__ = 'MIT License'
__version__ = '0.0.1'
__maintainer__ = 'Jonathan Giffard'
__email__ = 'jon.giffard@neo4j.com'
__status__ = 'Dev'

# Generic/Built-in
import concurrent.futures
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Owned
from common import ProgressBar, TXrequest


class BenchmarkThreadsImplicit:
    """
    Provides methods to execute Cypher statement against the Neo4j Query API using threads and implicit transations for benchmarking.
    """
    @staticmethod
    def _TXThreads(tx_request: TXrequest, cypher: str):
        """
        PRIVATE

        Executes the supplied Cypher statement in a managed TX

        :param tx_request - an instance of the TXRequest class
        :param cypher - the cypher statement to run

        :return: - Nothing is returned
        """
     
        # In our transaction context, run the cypher statement
        tx_request.tx_request_implicit(cypher)

        pass


    @staticmethod
    def run(number_tests: int, cypher: str, url: str, usr: str, pwd:str, db: str, t_out: int, workers:int = 0, http2: bool = False ):
        """
         Repeats a cypher statement, neo4j_cyper, for the number of times set by num_tests to the Neo4j Query API
         at neo4j_url using Threads. The total time is returned.

         :param cypher - the cypher statement to run
         :param number_tests  - the number of times to execute the test
         :param url - the URL of the Neo4j Query API
         :param usr - the user account to use
         :param pwd  - the password of the user account
         :return: total time taken
         """

        # Progress bar
        tx_progress_bar = ProgressBar("TXThreads", number_tests)

        # Object to handle our requests
        tx_request = TXrequest(url, usr, pwd, db, t_out)

        start_time = datetime.now()

        # Be careful with the number of workers - bad things happen if this is too high
        # looks like we exhaust the number of connections, showing as hitting max retries
        # you'll need to tweak this to reach a table value.
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:

            futures = [executor.submit(BenchmarkThreadsImplicit._TXThreads, tx_request, cypher) for i in range(number_tests)]

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Retrieve result from a thread or raise an exception
                    tx_progress_bar.add_progress_entry() # thread has finished, so increment the progress bar
                except Exception as e:
                    print(f"Task raised an exception: {e}")
                    raise

        # Destroy progress bar object
        # Make sure to do this to avoid the console
        # output showing the progress bar more than once
        # when something else is printed to the screen
        del tx_progress_bar

        # Desstroy our object that was doing the request work
        del tx_request

        end_time = datetime.now()

        total_time: timedelta = end_time - start_time

        return total_time.total_seconds()
