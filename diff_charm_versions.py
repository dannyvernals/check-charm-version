"""
Find the github commit hashes of Contrail components in the juju charms store.
Diff these commits and output the code differences between them. 
"""
import re
import argparse
import itertools
import json
import requests
import check_charm_versions


CHARMS_URL = "https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info"
GITHUB_SEARCH_URL = "https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+"
GITHUB_DIFF_URL = "https://api.github.com/repos/tungstenfabric/tf-charms/compare/{}...{}"

def cli_grab():
    """take stuff from cli, output it in a dict"""
    parser = argparse.ArgumentParser(description="diff charm commit hashes. ")
    parser.add_argument("charm_1", help="charm version 1 e.g. contrail-agent-21")
    parser.add_argument("charm_2", help="charm version 2 e.g. contrail-agent-22")
    args = vars(parser.parse_args())
    return args



def main():
    args = cli_grab().values()
    hash_1, hash_2, component = check_charm_versions.process_versions(args)
    check_charm_versions.output_diff(hash_1, hash_2, component)


if __name__ == "__main__":
    main()

    

