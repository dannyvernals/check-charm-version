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
import itertools

MASTER_URL= 'https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info'
# Example web commit search query:
# https://github.com/tungstenfabric/tf-charms/search?q=hash%3Acc1474f70b5bbfb6abeab009b4acab704f525bf2&type=commits
# example API search query:
# curl -H "Accept: application/vnd.github.cloak-preview" \
# https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+cc1474f70b5bbfb6abeab009b4acab704f525bf2

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
            sha_text = "Not Found"
        charms.append((charm, version, sha_text))
    return charms


def find_commit(hash):
    github_query_url = "https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+" + hash
    commit_details = requests.get(github_query_url,
                                  headers={'Accept': 'application/vnd.github.cloak-preview'})
    return commit_details.json()


def iterate_hashes(hashes):
    hashes = sorted(hashes, key=lambda x: x[2])
    n = 1
    for hash, grouped_hashes in itertools.groupby(hashes, key=lambda x: x[2]):
        try:
            commit_message = "\n" + find_commit(hash)['items'][0]['commit']['message']
        except IndexError:
            commit_message = "'Commit not found'"
        print("\nGroup {}: commit details: \n===\n{}\n===".format(n, commit_message))
        for line in grouped_hashes:
            print(line)
        n += 1

def compare_hashes(hashes):
    hash_set = set([line[2] for line in hashes])
    if len(hash_set) == 1:
        print("\nHashes are equal, charms are from the same commit, so we can assume compatibility. Commit details:\n")
        try:
            commit_message = "===\n" + find_commit(hash_set.pop())['items'][0]['commit']['message'] + "\n==="
        except IndexError:
            commit_message = "'Commit not found'"
        print(commit_message)
    else:
        print("\nWARNING: Not all hashes are equal\n")
        iterate_hashes(hashes)



if __name__ == '__main__':
    arguments = cli_grab()
    hash_out = get_hashes(arguments)
    compare_hashes(hash_out)
