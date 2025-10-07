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
import seaborn as sns
import matplotlib.pyplot as plt
import texttable as tt
import uuid



def generate_graph(test_results:dict):

    names = []
    values = []
    for k, v in test_results.items():
        names.append(k)
        values.append(v)

    ax = sns.barplot(x=names, y=values)
    ax.set(ylabel='seconds')
    bar_container = ax.containers[0]
    ax.bar_label(
        bar_container, fmt=lambda x: f"{round(x, 2)}s"
    )
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the image file and inform user of the filename
    image_filename = f"{uuid.uuid4().hex}.png"

    # Using bbox_inches='tight' makes sure that there is a min
    # of whitespace around the image
    plt.savefig(image_filename, bbox_inches='tight')
    
    print(f"\n Results graph saved as {image_filename}\n\n")

    pass


def generate_table(test_results:dict, num_requests: int):
    # This creates a formatted table using texttable

    pretty_table = ''

    results_table = tt.Texttable(900)

    # Set alignment for our 3 columns
    results_table.set_cols_align(["l","l","l"])

    # Characters used for horizontal & vertical lines
    # You can have different horizontal line for the header if wanted
    results_table.set_chars(['-', '|', '-', '-'])

    table_heading = ["Test","Time taken (s)","Requests/sec"]

    table_rows = []

    for name, value in test_results.items():
        request_per_second = num_requests / value
        table_rows.append([name, f"{value:.2f}", f"{request_per_second:.0f}"])

    results_table.add_rows([table_heading] + table_rows)

    print (results_table.draw())

    pass

