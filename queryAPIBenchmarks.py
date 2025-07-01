# -*- coding: utf-8 -*-
# Generic/Built-in
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
from datetime import datetime, timedelta
import logging
import click
from dotenv import load_dotenv


# Owned
from benchmarks import (BenchmarkSync, BenchmarkSyncImplicit,
                        BenchmarkSyncSessions, BenchmarkSyncSessionsImplicit,
                        BenchmarkThreads, BenchmarkThreadsImplicit,
                        BenchmarkThreadsSessions,
                        BenchmarkThreadsSessionsImplicit)
from common.showResults import generate_graph, generate_table


# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()

NUM_REQUESTS = int(os.getenv('NUM_REQUESTS', 5))
NEO4J_URL = os.getenv('NEO4J_URL')
NEO4J_USR = os.getenv('NEO4J_USERNAME')
NEO4J_PWD = os.getenv('NEO4J_PASSWORD')
NEO4J_DB = os.getenv('NEO4J_DATABASE')
NEO4J_CYPHER = os.getenv('NEO4J_CYPHER')
OUTPUT_GRAPH = int(os.getenv('OUTPUT_GRAPH',0))
OUTPUT_TABLE = int(os.getenv('OUTPUT_TABLE',1))
NETWORK_TIMEOUT = int(os.getenv('NETWORK_TIMEOUT',30))
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 5))
NETWORK_HTTP2 = bool(os.getenv('NETWORK_HTTP2',0))

benchmark_test_map = {
    "Sync": BenchmarkSync,
    "SyncSessions": BenchmarkSyncSessions,
    "Threads": BenchmarkThreads,
    "ThreadsSessions": BenchmarkThreadsSessions,
    "SyncImplicit": BenchmarkSyncImplicit,
    "SyncSessionsImplicit": BenchmarkSyncSessionsImplicit,
    "ThreadsImplicit": BenchmarkThreadsImplicit,
    "ThreadsSessionsImplicit": BenchmarkThreadsSessionsImplicit
}

@click.command()
@click.option("--tests", "-t", required=True, type=click.Choice(list(benchmark_test_map.keys())), multiple=True)
@click.option("--num-requests", "-n", default=NUM_REQUESTS, type=int)
@click.option("--neo4j-url", "-url", default=NEO4J_URL, type=str)
@click.option("--neo4j-usr", "-usr", default=NEO4J_USR, type=str)
@click.option("--neo4j-pwd", "-pwd", default=NEO4J_PWD, type=str)
@click.option("--neo4j-db", "-db", default=NEO4J_DB, type=str)
@click.option("--neo4j-cypher", "-cypher", default=NEO4J_CYPHER, type=str)
@click.option("--output-graph", "-graph", default=OUTPUT_GRAPH, type=bool)
@click.option("--output-table", "-table", default=OUTPUT_TABLE, type=bool)
@click.option("--network-timeout", "-timeout", default=NETWORK_TIMEOUT, type=int)
@click.option("--max-workers", "-workers", default=MAX_WORKERS, type=int)
@click.option("--network-http2", "-http2", default=NETWORK_HTTP2, type=bool)
def run_benchmark_tests(tests: dict, num_requests: int, neo4j_url: str, neo4j_usr: str, neo4j_pwd: str, neo4j_cypher: str, neo4j_db: str, output_graph: bool, output_table: bool, max_workers: int, network_timeout, network_http2: bool) -> None:

    results = {}
    total_time: timedelta

    for test_name in tests:
        test = benchmark_test_map[test_name]
  
        total_time = test.run(num_requests, neo4j_cypher, neo4j_url, neo4j_usr, neo4j_pwd, neo4j_db, network_timeout, max_workers, network_http2)

        results[test_name] = total_time

    # Generate a graph
    if output_graph:
        generate_graph(results)

    # Generate a table
    if output_table:
        generate_table(results, num_requests)



if __name__ == "__main__":
    run_benchmark_tests()