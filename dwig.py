#!/usr/bin/env python2

import sys, os, json, argparse, random, math, datetime

from dwave_sapi2.util import get_chimera_adjacency
from dwave_sapi2.remote import RemoteConnection

from structure import ChimeraQPU

import generator
from common import print_err
from common import validate_bqp_data
from common import json_dumps_kwargs

DEFAULT_CONFIG_FILE = '_config'


def main(args):
    if not args.seed is None:
        print_err('setting random seed to: %d' % args.seed)
        random.seed(args.seed)

    qpu = get_qpu(args.dw_url, args.dw_token, args.dw_proxy, args.solver_name, args.hardware_chimera_degree)
    #print_err(qpu)

    if args.chimera_degree != None:
        print_err('filtering QPU to chimera of degree %d' % args.chimera_degree)
        qpu = qpu.chimera_degree_filter(args.chimera_degree)

    if args.generator == 'ran':
        qpu_config = generator.generate_ran(qpu, args.steps, args.field)
    elif args.generator == 'clq':
        qpu_config = generator.generate_clq(qpu)
    elif args.generator == 'fl':
        qpu_config = generator.generate_fl(qpu, args.steps, args.alpha, args.min_loop_length, args.loop_reject_limit, args.loop_sample_limit)
    elif args.generator == 'wscn':
        if qpu.chimera_degree_view < 6:
            print_err('weak-strong cluster networks require a qpu with chimera degree of at least 6, the given degree is %d.' % qpu.chimera_degree_view)
            quit()

        effective_chimera_degree = 3*int(math.floor(qpu.chimera_degree_view/3))
        if effective_chimera_degree != qpu.chimera_degree_view:
            print_err('the weak-strong cluster network will occupy a space of chimera degree %d.' % effective_chimera_degree)
        qpu = qpu.chimera_degree_filter(effective_chimera_degree)

        qpu_config = generator.generate_wscn(qpu, args.weak_field, args.strong_field)
    else:
        assert(False) # CLI failed

    #print_err(qpu_config)

    data = qpu_config.build_dict()
    data['metadata'] = build_metadata(args)
    validate_bqp_data(data)
    data_string = json.dumps(data, **json_dumps_kwargs)
    print(data_string)


def build_metadata(args):
    metadata = {}
    if not args.dw_url is None:
        metadata['dw_url'] = args.dw_url
    if not args.solver_name is None:
        metadata['solver_name'] = args.solver_name
    
    metadata['generator'] = args.generator
    metadata['generated'] = str(datetime.datetime.utcnow())
    return metadata


def get_qpu(url, token, proxy, solver_name, hardware_chimera_degree):

    if not url is None and not token is None and not solver_name is None:
        print_err('QPU connection details found, accessing "%s" at "%s"' % (solver_name, url))
        if proxy is None: 
            remote_connection = RemoteConnection(url, token)
        else:
            remote_connection = RemoteConnection(url, token, proxy)

        solver = remote_connection.get_solver(solver_name)

        couplers = solver.properties['couplers']

        couplers = set([tuple(coupler) for coupler in couplers])

        sites = solver.properties['qubits']

        solver_chimera_degree = int(math.ceil(math.sqrt(len(sites)/8.0)))
        if hardware_chimera_degree != solver_chimera_degree:
            print_err('Warning: the hardware chimera degree was specified as %d, while the solver %s has a degree of %d' % (hardware_chimera_degree, solver_name, solver_chimera_degree))

        site_range = tuple(solver.properties['h_range'])
        coupler_range = tuple(solver.properties['j_range'])

    else:
        print_err('QPU connection details not found, assuming full yield square chimera of degree %d' % hardware_chimera_degree)

        site_range = (-2.0, 2.0)
        coupler_range = (-1.0, 1.0)

        # the hard coded 4 here assumes an 4x2 unit cell
        arcs = get_chimera_adjacency(hardware_chimera_degree, hardware_chimera_degree, 4)

        # turn arcs into couplers
        couplers = []
        for i,j in arcs:
            assert(i != j)
            if i < j:
                couplers.append((i,j))
            else:
                couplers.append((j,i))
        couplers = set(couplers)


        sites = set([coupler[0] for coupler in couplers]+[coupler[1] for coupler in couplers])

    # sanity check on couplers
    for i,j in couplers:
        assert(i < j)

    return ChimeraQPU(sites, couplers, hardware_chimera_degree, site_range, coupler_range)


# loads a configuration file and sets up undefined CLI arguments
def load_config(args):
    config_file_path = args.config_file

    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            try:
                config_data = json.load(config_file)
                for key, value in config_data.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        print('invalid value for configuration key "%s", only single values are allowed' % config_file_path)
                        quit()
                    if not hasattr(args, key) or getattr(args, key) == None:
                        if isinstance(value, unicode):
                            value = value.encode('ascii','ignore')
                        setattr(args, key, value)
                    else:
                        print('skipping the configuration key "%s", it already has a value of %s' % (key, str(getattr(args, key))))
                    #print(key, value)
            except ValueError:
                print('the config file does not appear to be a valid json document: %s' % config_file_path)
                quit()
    else:
        if config_file_path != DEFAULT_CONFIG_FILE:
            print('unable to open conifguration file: %s' % config_file_path)
            quit()

    return args


def build_cli_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-cf', '--config-file', help='a configuration file for specifing common parameters', default=DEFAULT_CONFIG_FILE)

    parser.add_argument('-url', '--dw-url', help='url of the d-wave machine')
    parser.add_argument('-token', '--dw-token', help='token for accessing the d-wave machine')
    parser.add_argument('-proxy', '--dw-proxy', help='proxy for accessing the d-wave machine')
    parser.add_argument('-solver', '--solver-name', help='d-wave solver to use', type=int)

    parser.add_argument('-rs', '--seed', help='seed for the random number generator', type=int)
    parser.add_argument('-cd', '--chimera-degree', help='the size of a square chimera graph to utilize', type=int)
    parser.add_argument('-hcd', '--hardware-chimera-degree', help='the size of the square chimera graph on the hardware', type=int, default=12)


    subparsers = parser.add_subparsers()

    parser_ran = subparsers.add_parser('ran', help='generates a RAN-n problem')
    parser_ran.set_defaults(generator='ran')
    parser_ran.add_argument('-s', '--steps', help='the number of steps in random numbers', type=int, default=1)
    parser_ran.add_argument('-f', '--field', help='include a random field', action='store_true', default=False)

    parser_clq = subparsers.add_parser('clq', help='generates a max clique problem')
    parser_clq.set_defaults(generator='clq')

    parser_fl = subparsers.add_parser('fl', help='generates a frustrated loop problem')
    parser_fl.set_defaults(generator='fl')
    parser_fl.add_argument('-s', '--steps', help='the number of allowed steps in output Hamiltonian', type=int, default=2)
    parser_fl.add_argument('-a', '--alpha', help='site-to-loop ratio', type=float, default=0.2)
    parser_fl.add_argument('-mll', '--min-loop-length', help='the minimum length of a loop', type=int, default=7)
    parser_fl.add_argument('-lrl', '--loop-reject-limit', help='the maximum amount of loops to be reject', type=int, default=1000)
    parser_fl.add_argument('-lsl', '--loop-sample-limit', help='the maximum amount of random walk samples', type=int, default=10000)

    parser_wscn = subparsers.add_parser('wscn', help='generates a weak-strong cluster network problem')
    parser_wscn.set_defaults(generator='wscn')
    parser_wscn.add_argument('-wf', '--weak-field', help='strength of the weak field', type=float, default=0.44)
    parser_wscn.add_argument('-sf', '--strong-field', help='strength of the weak field', type=float, default=-1)

    return parser


if __name__ == '__main__':
    parser = build_cli_parser()
    main(load_config(parser.parse_args()))
