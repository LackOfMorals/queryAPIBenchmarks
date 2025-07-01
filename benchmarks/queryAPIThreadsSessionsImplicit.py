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

import concurrent.futures
import os
# Generic / built in
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Owned
from common import ProgressBar, TXsession


class BenchmarkThreadsSessionsImplicit:
    """
    Provides methods to benchmark Neo4j Query API performance using threads and sessions.
    """
    @staticmethod
    def _TXThreadsSessions(tx_session: TXsession, cypher: str):
        """
          PRIVATE

          Executes the supplied Cypher statement. Uses Sessions

          :param cypher - the cypher statement to run
          :param url - the URL of the Neo4j Query API
          :param usr - the user account to use
          :param pwd  - the password of the user account
          :return: - Nothing is returned
        """

        # run the transaction 
        tx_session.tx_session_implicit(cypher)


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

        # Create an instance of TXSession as this triggers
        # the use of httpx client to allow us to re-use connections
        # We can use the same session across all of the threads
        tx_session = TXsession(url, usr, pwd, db, t_out)


        # Progress bar
        tx_progress_bar = ProgressBar("TXThreadsSessions", number_tests)

        # Starting time
        start_time = datetime.now()

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(BenchmarkThreadsSessionsImplicit._TXThreadsSessions, tx_session, cypher) for i in range(number_tests)]
            #concurrent.futures.wait(futures)
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()  # Retrieve result or raise an exception
                    tx_progress_bar.add_progress_entry()  # thread has finished, so increment the progress bar
                except Exception as e:
                    print(f"Task raised an exception: {e}")
                    raise 

        # Destroy progress bar object
        # Make sure to do this to avoid the console
        # output showing the progress bar more than once
        # when something else is printed to the screen
        del tx_progress_bar

        # Destroy the session object
        del tx_session

        end_time = datetime.now()
        total_time: timedelta = end_time - start_time

        return total_time.total_seconds()
