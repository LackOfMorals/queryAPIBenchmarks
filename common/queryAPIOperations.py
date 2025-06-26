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
import httpx

# Owned
from . import query_api_errors


class TXrequest:
    """
    Handles transaction-based requests to the Neo4j Query API, including transaction creation,
    cypher execution within a transaction, and transaction commit, with support for cluster affinity.
    """

    def __init__(self, url: str, usr: str, pwd: str, db: str):
        self._query_api = f"{url}/db/{db}/query/v2"
        self._query_auth = httpx.BasicAuth(usr, pwd)
        self._query_db = db


    def tx_request_id(self) -> tuple[str, str]:
        """
        Obtains a TX id from a neo4j server query api.  TX id is valid for 30 seconds
        Also returns neo4j-cluster-affinity value when used with Aura
        Both of these must be used with the transaction

        :return: str - tx id as a string
        """

        tx_id: str = ""
        tx_cluster_affinity: str = ""

        query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            # Make request to query api at url
            response = httpx.post(f"{self._query_api}/tx", headers=query_headers, auth=self._query_auth, timeout=5)

            # If this key is present in the response headers
            # we are talking to aura and need to use this in further TX requests
            # to ensure the TX stays with the initial server in a cluster
            # Similar to sticky sessions
            # Save as a property of the object

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

            # Extract the transaction id.  This will be added to the end of the URI
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


        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print(f"Connection error")
            exit()

        return tx_id, tx_cluster_affinity

    
    def tx_request_cypher(self, tx_id: str, cypher: str, cluster_affinity: str = ""):
        """
        Runs the cypher statement within the transaction, tx_id

        :param tx_id -  the transaction id
        :param cluster_affinity - ( optional ) the cluster affinity to use with Aura DBs
        :param cypher -  the cypher statement to execute in the transaction

        :return: None
        """

        query_cypher = {'statement': cypher }

        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}
        else: 
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            # Make request to query api at url
            response = httpx.post(f"{self._query_api}/tx/{tx_id}", headers=query_headers, auth=self._query_auth, json=query_cypher, timeout=5)

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print(f"Connection error")
            exit()

        pass


    def tx_request_commit(self, tx_id: str, cluster_affinity: str = ""):
        """
        Commits the transaction identified by tx_id
        :param tx_id -  the transaction id
        :param cluster_affinity - ( optional ) the cluster affinity to use with an Aura DB
        :return: None
        """

        query_headers = {}

        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}
        else: 
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            # Make request to query api at url
            response = httpx.post(f"{self._query_api}/tx/{tx_id}/commit", headers=query_headers, auth=self._query_auth, timeout=5)

            # We need to check for errors in the response
            #if 'errors' in response.json():
            #    query_api_errors(response.json()['errors'])

        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print("Connection error")
            exit()

    pass


class TXsession:
    """
    Manages session-based transactions with the Neo4j Query API, supporting transaction creation,
    cypher execution, and commit operations, with optional HTTP/2 and cluster affinity support.
    """
     
    def __init__(self, url: str, usr: str, pwd: str, db: str, http2_support:bool = False):
        self._session = httpx.Client(http2=http2_support)
        self._aura_cluster_affinity = ""
        self._query_api = f"{url}/db/{db}/query/v2"
        self._query_auth = httpx.BasicAuth(usr, pwd)
     

    def __del__(self):
        self._session.close()

     
    def tx_session_id(self) -> tuple[str, str]:
        """
        Obtains a TX id from a neo4j server query api.  TX id is valid for 30 seconds

        :return: str - tx id as a string
        :return: str - cluster affinity as a string
        """

        tx_id = ""
        tx_cluster_affinity = ""


        query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            # Make request to query api at url
            response = self._session.post(f"{self._query_api}/tx", headers=query_headers, auth=self._query_auth, timeout=5)

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

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

        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print(f"Connection error")
            exit()

        return tx_id, tx_cluster_affinity

     
    def tx_session_cypher(self, tx_id: str, cypher: str, cluster_affinity: str = ""):
        """
        Runs the cypher statement within the transaction, tx_id

        :param tx_id -  the transaction id
        :param cypher -  the cypher statement to execute in the transaction
        :return None
        """

        query_cypher = {'statement': cypher }

        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}
        else: 
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}


        try:
            # Make request to query api
            response = self._session.post(f"{self._query_api}/tx/{tx_id}", headers=query_headers, json=query_cypher, auth=self._query_auth, timeout=5)

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print(f"Connection error")
            exit()

        pass

     
    def tx_session_commit(self, tx_id: str, cluster_affinity: str = ""):
        """
        Commits the transaction identified by tx_id
        :param tx_id -  the transaction id
        :param cluster_affinity - (optional)

        :return: None
        """

        query_headers = {}

        if len(cluster_affinity) > 0:
            # If we have a cluster affinity, we need to add it to the headers
            # This is used with Aura DBs to ensure the transaction stays with the same server
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json", "neo4j-cluster-affinity": cluster_affinity}
        else: 
            query_headers =  {"Content-Type": "application/json", "Accept": "application/json"}
             

        try:
            # Make request to query api at url
            response = self._session.post(f"{self._query_api}/tx/{tx_id}/commit", headers=query_headers, auth=self._query_auth, timeout=5)

            # We need to check for errors in the response
            if 'errors' in response.json():
                query_api_errors(response.json()['errors'])

        except httpx.RequestError as exc:
            print(f"Connection error {exc.request.url}")
            exit()

        except httpx.HTTPError as exc:
            print(f"HTTP Error  {exc.request.url}")
            exit()

        except httpx.ConnectTimeout as exc:
            print(f"Connection timed out {exc.request.url}")
            exit()

        except ConnectionError as exc:
            print(f"Connection error")
            exit()

        pass

    def __delete__(self):
        self._session.close()
