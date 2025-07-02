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
from tqdm import tqdm

# Owned



class ProgressBar:
    """
    A progress bar wrapper using tqdm for tracking the progress of test executions.
    """
    def __init__(self, test_name:str, num_tests: int):
        self._progress_bar = tqdm(total=num_tests, desc=test_name, unit=" transactions", position=0, leave=True)

    def add_progress_entry(self):
        self._progress_bar.update(1)

    def __del__(self):
        self._progress_bar.close()

