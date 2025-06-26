# A benchmark tool for Neo4j Query API

## Requirements

- Python 3.13 or better
- neo4j 5.x / 202x.y or Aura

## Installation

Clone repo

```Text
git clone https://github.com/LackOfMorals/queryAPIBenchmarks.git
```

change directory

```
cd queryAPIBenchmarks
```

There are several Python libraries that will need to be installed and these are listed in _requirements.txt_. Blindy adding these could cause conflict with any existing libaries used by other Python applications that you may have. It is recommended that you setup a virtual Python environment which will keep the libaries used by aura API samples in isolation

```
python3 -m venv /path_to_virtual_environment

```

Once created you then need to activate it to use it. This varies between Windows and Linux / Mac

Windows

```
.\path_to_virtual_environment\Scripts\activate
```

Linux / Mac

```
source path_to_virtual_environment/bin/activate
```

They can be automatically loaded using the _pip_ command:

```
pip install -r requirements.txt
```

Depending on how you have Python installed, you may need to call pip for Python3 like this

```
pip3 install -r requirements.txt
```

## Configuration

You can set many of values using environmental values rather than entering them on the command line

```Text

# Number of requests to make in each benchmark
NUM_REQUESTS=5

# The cypher statement to run in the benchmarks
NEO4J_CYPHER='RETURN 1'

# Show a graph at the end.  If multiple tests are run, the graph will include all tests to make
# comparison easier.
OUTPUT_GRAPH=0

# By default, the benchmarks will output a table of results to the console.
OUTPUT_TABLE=1

# Tests SyncSessions and ThreadsSessions can use HTTP/2 .
# All other test use HTTP/1.1 and ignore this setting.
HTTP2_SUPPORT=0

# Noej4 connection details
NEO4J_URL=http://mydb.example.com:7474
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j


# Number of threads to use with Threads and ThreadsSessions benchmarks
# Too many threads can cause issues with the Neo4j server when num_request is set to medium -> large quantities
# You will see errors "Connection error: " and
# even "Error from Query API: {'code': 'Neo.TransientError.Request.ResourceExhaustion'} "
MAX_WORKERS=4

```

_Note:_ When using an Aura DB, set the URL to use https and without the port number at the end. e.g `https://9957dik7.databases.neo4j.io`

You can set these individually e.g `export NUM_REQUESTS=5` or copy and paste the above into a file called '.env' and save in the root of the installation folder, queryAPIBenchmarks

## Usage

Make sure you are the root of the installation folder, queryAPIBenchmarks

To see what command line options can be used, type

```
python queryAPIBenchmarks.py --help
```

If you have previously configured the .env file with values for your environment, you can run a test with

```
python queryAPIBenchmarks.py -t Sync
```

Each test will display a progress bar. When test have finished,the results are shown in a table. A graph is also available for showing results by using -output-graph e.g

```
python queryAPIBenchmarks.py -t Sync --output-graph True
```

## Tests

The current set of tests execute a single Cypher statement as a _managed transaction_.

- Obtain a transaction ID
- Using the transaction ID, execute the Cypher statement
- Commit the transaction

_Note:_ Managed transactions are better suited for when multiple Cypher statements must be executed together to achieve an outcome. The Query API also supports unmanaged transactions for single Cypher statements. These are still executed as a transaction with the Query API managing them.

### Sync

Repeatedly sends the Cypher statements one by one in a sequential fashion to Neo4j system with a new network connection being used for each. The slowest performing test.

### SyncSessions

The difference between this test and the Sync one is with the network connection. SyncSessions re-uses the same network connection which elminates the overheard of establishing a connection for each test cycle. This should be quicker than Sync, particulary with a larger number of test runs.

### Threads

Uses a new connection for each test run but does many at the sametime using Python threads. The max number at once is determined by the MAX_WORKER environment variable which is set at 4. Should be quicker than SyncSessions.

### ThreadsSessions

Combines the use of Threads and SyncSessions in a single test. Number of threads is set by the MAX_WORKER environment. Depending on circumstances, this can give the highest number of transactions per second.

## FAQS

### Can I avoid entering lots of command line options?

Yes, copy .env_example to .env and save in the folder root. Change the values to match your environment.

You can override whatever is set in that file by using command line parameters.

### Error handling

There is some but it's not extensive...

### When using Threads or ThreadsSessions, I see error messages

Likely caused when you use large values for the total number of test cycles. Lower the value of MAX_WORKERS which you can find in .env file at folder root. The default value is 4
