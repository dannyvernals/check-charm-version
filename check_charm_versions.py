"""
'check-charm-versions.py'
Compare the commit hashes of Contrail charm versions to infer compatibility.
Based on whether or not they were committed at the same time.

Usage e.g. python check-charm-versions.py contrail-agent-18 contrail-analytics-16 \
                                          contrail-analyticsdb-16 contrail-controller-17 \
                                          contrail-keystone-auth-16 contrail-openstack-19
Or something like:
check-charm-versions.py `juju export-bundle | grep juniper-os- |awk -F \/ '{print $2}' | xargs`
"""
import re
import argparse
import itertools
import requests


CHARMS_URL = "https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info"
GITHUB_SEARCH_URL = "https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+"
GITHUB_DIFF_URL = "https://api.github.com/repos/tungstenfabric/tf-charms/compare/{}...{}"

# Example web commit search query:
# https://github.com/tungstenfabric/tf-charms/search?q=hash%3Acc1474f70b5bbfb6abeab009b4acab704f525bf2&type=commits
# example API search query:
# curl -H "Accept: application/vnd.github.cloak-preview" \
# https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+cc1474f70b5bbfb6abeab009b4acab704f525bf2

def cli_grab():
    """take stuff from cli, output it in a dict"""
    parser = argparse.ArgumentParser(description="compare charm commit hashes. "
                                                 "Arguments = all the versions to check")
    parser.add_argument("agent", help="contrail-agent charm version")
    parser.add_argument("analytics", help="contrail-analytics charm version")
    parser.add_argument("analyticsdb", help="contrail-analyticsdb charm version")
    parser.add_argument("controller", help="contrail-controller charm version")
    parser.add_argument("keystone", help="contrail-keystone-auth charm version")
    parser.add_argument("openstack", help="contrail-openstack charm version")
    args = vars(parser.parse_args())
    return args


def get_hashes(args):
    """query the Canonical juju charms repo to find the github commit hashes of the passed charms"""
    charms = list()
    for version in args:
        page = requests.get(CHARMS_URL.format(version))
        sha_text = re.search(r"commit-sha-1[^\w]+(.+)\n", page.text)
        if sha_text:
            sha_text = sha_text.group(1)
        else:
            sha_text = "Not Found"
        charms.append((version, sha_text))
    return charms


def find_commit(commit_hash):
    """query github to search for metadata about the specified commit"""
    if commit_hash != "Not Found":
        github_query_url = GITHUB_SEARCH_URL + commit_hash
        commit_details = requests.get(github_query_url,
                                      headers={"Accept": "application/vnd.github.cloak-preview"})
        return commit_details.json()
    else:
        return {}


def get_diff(com_hash_1, com_hash_2):
    """query github to search for metadata about the specified commit"""
    github_query_url = GITHUB_DIFF_URL.format(com_hash_1, com_hash_2)
    diff_details = requests.get(github_query_url,
                                      headers={"Accept": "application/vnd.github.cloak-preview"})
    return diff_details.json()


def parse_commit(commit_hash):
    """extract data from the json blob we grab from github"""
    try:
        commit_data = find_commit(commit_hash)
        commit_date = commit_data["items"][0]["commit"]["committer"]["date"]
        commit_message = commit_data["items"][0]["commit"]["message"]
    except (IndexError, KeyError):
        commit_message = "'Commit not found'"
        commit_date = "'Not Known'"
    return commit_date, commit_message


def iterate_hashes(hashes):
    """For a list of non-equal hashes, sort and group them and output metadata"""
    hashes = sorted(hashes, key=lambda x: x[1])
    num = 1
    for commit_hash, grouped_hashes in itertools.groupby(hashes, key=lambda x: x[1]):
        commit_date, commit_message = parse_commit(commit_hash)
        print('-' * 80)
        print("\nGroup {}: commit-date: {}".format(num, commit_date))
        print("commit details: \n===\n{}\n===".format(commit_message))
        for line in grouped_hashes:
            print(line)
        num += 1


def compare_hashes(hashes):
    """Find if all commit hashes are equal"""
    hash_set = set([line[1] for line in hashes])
    if len(hash_set) == 1:
        print("\nHashes are equal, charms versions are from the same commit "
              "so we can assume compatibility.\n")
        commit_date, commit_message = parse_commit(hash_set.pop())
        print("commit-date: {}".format(commit_date))
        print("commit details: \n===\n{}\n===".format(commit_message))
    else:
        print("\nWARNING: Not all hashes are equal\n")
        iterate_hashes(hashes)


if __name__ == "__main__":
    ARGS = cli_grab().values()
    COMMIT_HASHES = get_hashes(ARGS)
    compare_hashes(COMMIT_HASHES)