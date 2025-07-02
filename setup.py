from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Load the version
version = {}
with open("queryAPIBenchmarks/version.py") as f:
    exec(f.read(), version)

setup(
    name="queryAPIBenchmarks",
    version=version["__version__"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        queryAPIBenchmarks=queryAPIBenchmarks.queryAPIBenchmarks:run_benchmark_tests
    """,
)