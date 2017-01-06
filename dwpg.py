#!/usr/bin/env python2

import os, json, argparse, random, time

import dwave_sapi2 as dw
from dwave_sapi2.remote import RemoteConnection


CONFIG_FILE_DEFAULT = '_config'


def main(args):
    if not args.seed is None:
        random.seed(args.seed)

    if args.dw_proxy is None: 
        remote_connection = RemoteConnection(args.dw_url, args.dw_token)
    else:
        remote_connection = RemoteConnection(args.dw_url, args.dw_token, args.dw_proxy)

    solver = remote_connection.get_solver(args.solver_name)

    edges = solver.properties['couplers']
    nodes = solver.properties['qubits']

    print(len(edges))
    print(len(nodes))

    edges = set([tuple(edge) for edge in edges])

    #c_count = [ int(math.floor(i / 8)) for i in all_nodes]
    #c_row = [ int(math.floor(c_count[i] / 12)) for i in all_nodes]
    #c_col = [ c_count[i] % 12 for i in all_nodes]

    H = ran_generator(edges, steps = 1)

    print(H)



def ran_generator(edges, steps = 1):
    H = {edge : -1.0 if random.random() <= 0.5 else 1.0 for edge in edges}
    return H



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
        if config_file_path != CONFIG_FILE_DEFAULT:
            print('unable to open conifguration file: %s' % config_file_path)
            quit()


def build_cli_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-cf', '--config-file', help='a configuration file for specifing common parameters', default=CONFIG_FILE_DEFAULT)

    parser.add_argument('-url', '--dw-url', help='url of the d-wave machine')
    parser.add_argument('-token', '--dw-token', help='token for accessing the d-wave machine')
    parser.add_argument('-proxy', '--dw-proxy', help='proxy for accessing the d-wave machine')
    parser.add_argument('-solver', '--solver-name', help='d-wave solver to use', type=int)

    parser.add_argument('-cd', '--chimera-degree', help='the degree of the square chimera graph', type=int)
    #parser.add_argument('-o', '--output', help='the output file name')
    parser.add_argument('-rs', '--seed', help='seed for the random number generator', type=int)
    #parser.add_argument('-dqp', '--display-qaudratic-program', help='prints the qaudratic program to stdout', action='store_true', default=False)
    #parser.add_argument('-rtl', '--runtime-limit', help='gurobi runtime limit (sec.)', type=int)

    #parser.add_argument('-g', '--generator', choices=['ran1', 'negative', 'checker', 'frustrated-checker'], default='ran1')
    subparsers = parser.add_subparsers()

    parser_ran = subparsers.add_parser('ran', help='builds a ran-n problem')
    parser_ran.set_defaults(generator='ran')
    parser_ran.add_argument('-s', '--steps', help='the number of steps in random numbers', type=int, default=1)

    return parser


if __name__ == '__main__':
    parser = build_cli_parser()
    args = parser.parse_args()
    load_config(args)
    main(args)
