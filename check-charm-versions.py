"""
check-charm-versions.py
Compare the commit hashes of Contrail charm versions to infer compatibility based on whether or not they were
committed at the same time.

Usage e.g. python check-charm-versions.py contrail-agent-18 contrail-analytics-16 contrail-analyticsdb-16 \
                                          contrail-controller-17 contrail-keystone-auth-16 contrail-openstack-19
Or
python check-charm-versions.py `juju export-bundle | grep juniper-os-software |awk -F \/ '{print $2}' | xargs`
"""
import requests
import re
import argparse

MASTER_URL= 'https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info'

def cli_grab():
    """take stuff from cli, output it in a dict"""
    parser = argparse.ArgumentParser(description='compare charm commit hashes. Arguments = all the versions to check')
    parser.add_argument("agent", help="contrail-agent charm version")
    parser.add_argument("analytics", help="contrail-analytics charm version")
    parser.add_argument("analyticsdb", help="contrail-analyticsdb charm version")
    parser.add_argument("controller", help="contrail-controller charm version")
    parser.add_argument("keystone", help="contrail-keystone-auth charm version")
    parser.add_argument("openstack", help="contrail-openstack charm version")
    args = vars(parser.parse_args())
    return args


def get_hashes(args):
    charms = list()
    for charm, version in args.items():
        page = requests.get(MASTER_URL.format(version))
        sha_text = re.search(r"commit-sha-1[^\w]+(.+)\n", page.text)
        if sha_text:
            sha_text = sha_text.group(1)
        else:
            sha_text = "."
        charms.append((charm, version, sha_text))
    return charms


def compare_hashes(hashes):
    hash_set = set([line[2] for line in hashes])
    if len(hash_set) == 1:
        print("\nHashes are equal, charms were committed at the same time, we can assume they are compatible\n")
    else:
        print("\nWARNING: Hashes are NOT equal\n")
        for line in hashes:
            print(line)


if __name__ == '__main__':
    args = cli_grab()
    hashes = get_hashes(args)
    compare_hashes(hashes)
