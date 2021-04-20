#!/usr/bin/env python
"""Squal Kubernetes Plugin"""
import re
import sys
import argparse
import json
from benchmarks import Benchmarks
from squall_api import SquallAPI

VALID_COMPONENTS = ['benchmarks', 'api']
VALID_BENCHMARK_ACTIONS = ['version', 'run']
VALID_BENCHMARK_ARGS = ['format']
VALID_API_ACTIONS = ['get', 'update']
UID_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"


def usage():
    usage = f"""
    Squal Kubernetes Plugin
    
    Usage:
    kubectl squall [component] [action] [args]
    
    Components:
    {VALID_COMPONENTS}
    
    Benchmarks:
        Actions:
        {VALID_BENCHMARK_ACTIONS}
        Arguments:
        {VALID_BENCHMARK_ARGS}

        Example:
            kubectl squall benchmarks run
    API:
        Actions:
        {VALID_API_ACTIONS}
        Arguments:
        UID v4 JSON String

        Examples:
            kubectl squall api get 31c357c1-9e80-4ff0-bfe5-5b7319d20438
            kubectl squall api update 31c357c1-9e80-4ff0-bfe5-5b7319d20438 {{\"uid\":\"c224f46e-d258-4818-a1bb-4361ceaf849c\"\,\"frequency\":60}}

    optional arguments:
    -h, --help, help  show this help message and exit
    """
    return usage


def print_usage():
    print(usage())
    sys.exit(1)


def main(args):
    component = args.arguments.pop(0)
    if component not in VALID_COMPONENTS:
        print_usage()

    if component == 'benchmarks':
        benchmarks = Benchmarks()
        try:
            action = args.arguments.pop(0)
            if action not in VALID_BENCHMARK_ACTIONS:
                print_usage()
            if action == 'version':
                print(f"CIS Kubernetes Benchmark version: {benchmarks.get_version()}")
            if action == 'run':
                benchmarks.run()
        except IndexError:
            print_usage()
    elif component == 'api':
        try:
            import requests
        except ImportError:
            print("The Squall API client depends on requests")
            print("please install requests by running:")
            print("pip install requests")

        api = SquallAPI()
        try:
            action = args.arguments.pop(0)
            if action not in VALID_API_ACTIONS:
                print_usage()
            if action == 'get':
                uid = None
                if len(args.arguments) == 1:
                    uid = args.arguments.pop(0)
                    if not re.match(UID_REGEX, uid):
                        print("The uid is not valid")
                        sys.exit()
                api.get(uid)
            if action == 'update':
                uid = None
                print(args.arguments)
                if len(args.arguments) == 2:
                    uid = args.arguments.pop(0)
                    data = args.arguments.pop(0)
                    print(data)
                    if not re.match(UID_REGEX, uid):
                        print("The uid is not valid")
                        sys.exit()
                    try:
                        json.dumps(data)
                    except json.JSONDecodeError:
                        print("The data is not valid")
                        sys.exit()
                else:
                    print_usage()
                    sys.exit(1)
                api.update(uid, data)

        except IndexError:
            print_usage()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Squall Kubernetes Controller.',
        usage=usage(),
        add_help=False
    )
    parser.add_argument('arguments', type=str, nargs='+')
    args = parser.parse_args()
    main(args)
