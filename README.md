# D-Wave Instance Generator (D-WIG)
================

The D-WIG toolset is used to generate binary quadratic programs based on a specific D-Wave QPU.  A significant advantage of generating problems on a specific QPU is that the a problem does not require embedding onto the hardware graph.  The D-WIG problem generator assumes that the QPU has a chimera topology.

The D-WIG toolset includes,
* bqp-schema.json - a JSON-Schema for encoding Binary Quadratic Programs (B-QP) problems
* dwig.py - a command line tool for generating B-QP problems in the bqp-json format
* spin2bool.py - a command line tool for converting a bqp-json data files between the spin and boolean variable spaces
* bqp2qh.py - a command line tool for converting a bqp-json data files into a qubist compatible Hamiltonians

The remainder of this documentation assumes that,
1. You have access to a D-Wave QPU and the SAPI binaries
2. You are familiar with the D-Wave Qubist interface
3. You are using a bash-like terminal


## Installation

The D-WIG toolset requires `dwave-sapi2` and `jsonschema` to run and `pytest` for testing.
To install these requirements first make sure that the `dwave-sapi2` library is installed by running,
```
python <path to sapi>/install.py
```
Then the remaining dependencies can be installed via,
```
pip install -r requirements.txt
```

The installation can be tested by running,
```
./test.it
```

## Introduction

### Basic Usage

The primary entry point of the D-WIG toolset is `dwig.py` this script is used to generate a variety of B-QP problems, which have been studied in the literature.

For example, the following command will generate a RAN1 problem for a full yield QPU of chimera degree 12 and send it to standard output,
```
./dwig.py ran
```
Bash stream redirection can be used to save the standard output to a file, for example,
```
./dwig.py ran > ran1.json
```
The `ran1.json` file is a json document in the bqp-json format.  A detailed description of this format can be found in the `BQP.md` file.

A helpful feature of D-WIG is to reduce the size of the QPU that you are working with.  The _chimera degree_ argument `-cd n` can be used to reduce D-WIG's view of the full QPU to a smaller the first n-by-n unit cells.  For example try,
```
./dwig.py -cd 2 ran
```
A detailed list of all command line options can be reviewed via,
```
./dwig.py --help
```


### Problem Types

The D-Wig toolset currently supports three types of problem generation,

1. ran - the QPU fields are couplers are set uniformly at random
2. fl - frustrated loops
3. wscn - weak-strong cluster networks

See the doc strings inside of `generator.py` for further details on each of these problem types.


### Connecting to a QPU

Without any connection details, D-WIG will assume a full yield QPU of chimera degree 12.  Connection details are required to build B-QPs from a specific QPU.  The simplest way to add connection details is via the following command line arguments,
```
./dwig.py 
    -url <d-wave endpoint url>
    -token <sapi token>
    -solver <solver name>
    ran
```

Alternatively, a `_config` file can be placed in the D-WIG directory of the following form,
```
{
    "dw_url":"<d-wave endpoint url>",
    "dw_token":"<sapi token>",
    "solver_name":"<solver name>"
}
```
The configuration file is a json document that can be use to set default values for all command line parameters.


### Viewing a B-QP

The Qubist Solver Visualization tool is very helpful in understanding complex B-QP datasets.  The `bqp2qh.py` script can be used to convert a B-QP problem into the Qubist Hamiltonian format so that it can be viewed in the Solver Visualization tool.  For example, the following command will generate a 2-by-2 RAN1 problem in the qubist format and then print it to standard output,
```
./dwig.py -cd 2 ran | ./bqp2qh.py
```
To view this problem paste the output data into the Data tab of the Qubist Solver Visualization tool.


### Spin vs Boolean Variables

The B-QP format supports problems with spin variables (i.e. {-1,1}) and boolean variables (i.e. {0,1}).  However, the D-WIG toolset generates problems only using spin variables.  The `spin2bool.py` tool can be used to make the transformation after the problem is generated.  For example, the following  command will generate 2-by-2 RAN1 problem and convert it to a boolean variable space,
```
./dwig.py -cd 1 ran | ./spin2bool.py
```

## Known Issues

The json schema validation library `jsonschema` is designed for python 3 while the `dwave-sapi2` library requires python 2.  Consequently, it takes about 2 seconds to load the compatibility libraries to use jsonschema in python 2.


## Acknowledgments

The D-WIG development team would like to thank Denny Dahl for suggesting the D-WIG name.


## Citations

The D-WIG development team would like to thank Denny Dahl for suggesting the D-WIG name.
