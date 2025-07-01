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
import os
import dotenv
import logging
import httpx

# Owned
from . import query_api_errors


class TXrequest:
    """
    Handles transaction-based requests to the Neo4j Query API, including transaction creation,
    cypher execution within a transaction, and transaction commit, with support for cluster affinity.
    """

    def __init__(self, url: str, usr: str, pwd: str, db: str, t_out:int ):
        dotenv.load_dotenv()
        # Configure logging
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(__name__)
        self._query_api = f"{url}/db/{db}/query/v2"
        self._query_auth = httpx.BasicAuth(usr, pwd)
        self._query_db = db
        self._timeout = t_out


    def _make_request(self, url_path: str ="", cluster_affinity: str = "", cypher: str = "") -> httpx.Response:
        # Makesd the request to Query API , send response back and deals with any errors

        query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        if len(cypher) > 0:
            query_cypher = {'statement': cypher}
        else:
            query_cypher = {}

        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}

        try:
            # Make request to query api at url
            response = httpx.post(f"{self._query_api}{url_path}", headers=query_headers, auth=self._query_auth, json=query_cypher, timeout=self._timeout)
            
            # If this key is present in the response headers
            # we are talking to aura and need to use this in further TX requests
            # to ensure the TX stays with the initial server in a cluster
            # Similar to sticky sessions
            # Save as a property of the object

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

        except httpx.RequestError as e:
            self._logger.error(f"Request error: {str(e)}")
            print(f"Connection error {e.request.url}")
            exit()

        except httpx.HTTPError as e:
            self._logger.error(f"HTTP error: {str(e)}")
            print(f"HTTP Error  {e.request.url}")
            exit()

        except httpx.ConnectTimeout as e:
            self._logger.error(f"Connection timed out error: {str(e)}")
            print(f"Connection timed out {e.request.url}")
            exit()

        except ConnectionError as e:
            self._logger.error(f"Connection error: {str(e)}")
            print(f"Connection error")
            exit()

        return response


    def tx_request_id(self) -> tuple[str, str]:
        """
        Obtains a TX id from a neo4j server query api.  TX id is valid for 30 seconds
        Also returns neo4j-cluster-affinity value when used with Aura
        Both of these must be used with the transaction

        :return: str - tx id as a string
        """

        tx_id: str = ""
        tx_cluster_affinity: str = ""

        try:
            
            # Make request to query api at url
            response = self._make_request("/tx")
            
            # If this key is present in the response headers
            # we are talking to aura and need to use this in further TX requests
            # to ensure the TX stays with the initial server in a cluster
            # Similar to sticky sessions
            # Save as a property of the object

            # Extract the transaction id.  This will be added to the end of the URI
            # to associate database operations with the transaction
            if 'transaction' in response.json():
                tx_id = response.json()['transaction']['id']
            else:
                tx_id = ""

            # Add tx_id and it's associated cluster affinity to our map to track them
            # for when an instance of this class is being shared amongst multiple threads
            # This allows us to use them as a matched pair in the correct transaction
            # We only need to do this for Aura
            if 'neo4j-cluster-affinity' in response.headers:
                tx_cluster_affinity = response.headers['neo4j-cluster-affinity']

        except Exception as e:
            print(f"Exception when obtaining a tx id  {e}")

        return tx_id, tx_cluster_affinity

    
    def tx_request_cypher(self, tx_id: str, cypher: str, cluster_affinity: str = ""):
        """
        Runs the cypher statement within the transaction, tx_id

        :param tx_id -  the transaction id
        :param cluster_affinity - ( optional ) the cluster affinity to use with Aura DBs
        :param cypher -  the cypher statement to execute in the transaction

        :return: None
        """

        try:
            # Make request to query api at url
            response = self._make_request(f"/tx/{tx_id}", cluster_affinity, cypher)

        except Exception as e:
            print(f"Error with Cypher request {e}")
            exit()

        pass


    def tx_request_commit(self, tx_id: str, cluster_affinity: str = ""):
        """
        Commits the transaction identified by tx_id
        :param tx_id -  the transaction id
        :param cluster_affinity - ( optional ) the cluster affinity to use with an Aura DB
        :return: None
        """

        try:
            # Make request to query api at url
            esponse = self._make_request(f"/tx/{tx_id}/commit", cluster_affinity)

        except Exception as e:
            print(f"Error commiting tx {tx_id}:  {e}")
            exit()

    pass

    def tx_request_implicit(self, cypher: str):
        """
   
        :param cypher -  the cypher statement to execute
        :return: str - tx id as a string
        """

        try:
            # Make request to query api at url
            response = self._make_request("","",cypher)

        except Exception as e:
            print(f"Error with implicit tx {e}")

        pass




class TXsession:
    """
    Manages session-based transactions with the Neo4j Query API, supporting transaction creation,
    cypher execution, and commit operations, with optional HTTP/2 and cluster affinity support.
    """
     
    def __init__(self, url: str, usr: str, pwd: str, db: str, t_out: int, http2_support: bool = False):
        # Configure logging
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(__name__)
        self._session = httpx.Client(http2=http2_support)
        self._query_api = f"{url}/db/{db}/query/v2"
        self._query_auth = httpx.BasicAuth(usr, pwd)
        self._timeout = t_out
 

    def __del__(self):
        self._session.close()
        

    def _make_session_request(self, url_path: str ="", cluster_affinity: str = "", cypher: str = "") -> httpx.Response:
        """
        Makes a session based request , handles any erorrs and returns the response
        """

        query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        if len(cypher) > 0:
            query_cypher = {'statement': cypher}
        else:
            query_cypher = {}
        
        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}

        try:
            # Make request to query api at url
            response = self._session.post(f"{self._query_api}{url_path}", headers=query_headers, auth=self._query_auth, json=query_cypher, timeout=self._timeout)

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])


        except httpx.RequestError as e:
            self._logger.error(f"Request error: {str(e)}")
            print(f"Connection error {e.request.url}")
            exit()

        except httpx.HTTPError as e:
            self._logger.error(f"HTTP error: {str(e)}")
            print(f"HTTP Error  {e.request.url}")
            exit()

        except httpx.ConnectTimeout as e:
            self._logger.error(f"Connection timed out error: {str(e)}")
            print(f"Connection timed out {e.request.url}")
            exit()

        except ConnectionError as e:
            self._logger.error(f"Connection error: {str(e)}")
            print(f"Connection error")
            exit()


        return response
     
    def tx_session_id(self) -> tuple[str, str]:
        """
        Obtains a TX id from a neo4j server query api.  TX id is valid for 30 seconds

        :return: str - tx id as a string
        :return: str - cluster affinity as a string
        """

        tx_id = ""
        tx_cluster_affinity = ""

        try:
            # Make request to query api at url
            response = self._make_session_request("/tx")

            # Extract the transaction id from the response.  This will be added to the end of the URI
            # to associate database operations with the transaction
            if 'transaction' in response.json():
                tx_id = response.json()['transaction']['id']
            else:
                tx_id = None

            # Add tx_id and it's associated cluster affinity to our map to track them
            # for when an instance of this class is being shared amongst multiple threads
            # This allows us to use them as a matched pair in the correct transaction
            # We only need to do this for Aura
            if 'neo4j-cluster-affinity' in response.headers:
                tx_cluster_affinity = response.headers['neo4j-cluster-affinity']

        except Exception as e:
            print(f"Exception when obtaining a tx id  {e}")  
            exit()

        return tx_id, tx_cluster_affinity

     
    def tx_session_cypher(self, tx_id: str, cypher: str, cluster_affinity: str = ""):
        """
        Runs the cypher statement within the transaction, tx_id

        :param tx_id -  the transaction id
        :param cypher -  the cypher statement to execute in the transaction
        :return None
        """
       
        try:
            # Make request to query api
            response = self._make_session_request(f"/tx/{tx_id}", cluster_affinity, cypher)
            
        except Exception as e:
            print(f"Error with Cypher request {e}")
            exit()

        pass

     
    def tx_session_commit(self, tx_id: str, cluster_affinity: str = ""):
        """
        Commits the transaction identified by tx_id
        :param tx_id -  the transaction id
        :param cluster_affinity - (optional)

        :return: None
        """
             

        try:
            # Make request to query api at url
            response = self._make_session_request(f"/tx/{tx_id}/commit", cluster_affinity)
            

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

        except Exception as e:
            print(f"Error commiting tx {tx_id}:  {e}")
            exit()

        pass

    def __delete__(self):
        self._session.close()

    def tx_session_implicit(self, cypher: str):
            """
            Runs the cypher statement within an implicit transaction

            :param cypher -  the cypher statement to execute in the transaction
            :return None
            """

            try:
                # Make request to query api
                response = self._make_session_request("","",cypher)

            except Exception as e:
                print(f"Error with implicit tx {e}")
                exit()

            pass