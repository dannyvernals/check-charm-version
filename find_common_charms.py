"""
Return a list all the Contrail charms with the same commit hash.
From this we can infer compatibility as they will have been QAed together.
"""
import argparse
import requests
import re


CHARMS_URL = "https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info"
CHARM_LIST = ['contrail-agent', 'contrail-analytics', 'contrail-analyticsdb', 'contrail-openstack']


def get_hash(version):
    """query the Canonical juju charms repo to find the github commit hash of the passed charm"""
    page = requests.get(CHARMS_URL.format(version))
    sha_text = re.search(r"commit-sha-1[^\w]+(.+)\n", page.text)
    if sha_text:
        return sha_text.group(1)
    else:
        return "Not Found"

def compare_hash(queried_hash, version, component):
    """Test hashes for equality"""
    querying_hash = get_hash(component + '-' + str(version))
    if queried_hash == querying_hash:
        return True
    return False


def find_matching_hash(search_tuple):
    """recurse through charm versions looking for a commit hash match.
    move 1 version away up and down each pass. Stop recursing when no more
    charm versions are found"""
    #print(search_tuple)
    component, queried_hash, left, right = search_tuple
    if left == 'not found' and right == 'not found':
        return component + ': match not found'
    elif isinstance(left, str):
        if 'match' in left:
            return component + '-' + left.split('-')[1]
    elif isinstance(right, str):
        if 'match' in right:
            return component + '-' + right.split('-')[1]
    else:
        if left != 'not found':
            if compare_hash(queried_hash, left, component):
                left = 'match-' + str(left)
            else:
                left = left - 1
        if right != 'not found':
            if compare_hash(queried_hash, right, component):
                right = 'match-' + str(right)
            else:
                right = right + 1
        return find_matching_hash((component, queried_hash, left, right))


def cli_grab():
    """take stuff from cli, output it in a dict"""
    parser = argparse.ArgumentParser(description="Find Contrail charm versions that were commited at the same time")
    parser.add_argument("charm_version", help="Charm version e.g. contrail-agent-21")
    args = vars(parser.parse_args())
    return args

    
def main():
    args = cli_grab()
    queried_charm = args['charm_version']
    component = '-'.join(queried_charm.split('-')[0:2])
    queried_version = int(queried_charm.split('-')[2])
    CHARM_LIST.remove(component)
    queried_hash = get_hash(queried_charm)
    compatible_charms = [queried_charm]
    for component in CHARM_LIST:
        search_tuple = (component, queried_hash, queried_version, queried_version) 
        matching_charm = find_matching_hash(search_tuple)
        compatible_charms.append(matching_charm)
    print(compatible_charms)


if __name__ == "__main__":
    main()