"""
Find the github commit hashes of Contrail components in the juju charms store.
Diff these commits and output the code differences between them. 

diff charm commit hashes.

positional arguments:
  charm_1      Charm version 1 e.g. contrail-agent-21
  charm_2      Charm version 2 e.g. contrail-agent-22

optional arguments:
  -h, --help   show this help message and exit
  -t, --terse  Show only differences in config.yaml. Good for checking if new
               configuration is needed or new features are available between
               versions
"""
import argparse
import check_charm_versions


CHARMS_URL = "https://api.jujucharms.com/charmstore/v5/~juniper-os-software/{}/archive/repo-info"
GITHUB_SEARCH_URL = "https://api.github.com/search/commits?q=repo:tungstenfabric/tf-charms+"
GITHUB_DIFF_URL = "https://api.github.com/repos/tungstenfabric/tf-charms/compare/{}...{}"

def cli_grab():
    """take stuff from cli, output it in a dict"""
    parser = argparse.ArgumentParser(description="diff charm commit hashes. ")
    parser.add_argument("charm_1", help="Charm version 1 e.g. contrail-agent-21")
    parser.add_argument("charm_2", help="Charm version 2 e.g. contrail-agent-22")
    parser.add_argument("-t", "--terse", action="store_true", help="Show only differences in config.yaml."
                                                                    " Good for checking if new configuration is needed"
                                                                    " or new features are available between versions"
                                                                    )
    args = vars(parser.parse_args())
    return args



def main():
    args = list(cli_grab().values())
    terse = args.pop()
    hash_1, hash_2, component = check_charm_versions.process_versions(args)
    print("\nOutputing difference between:\n{} & {}".format(hash_1, hash_2))
    print("Only showing diffs of files relating to the component: '{}'".format(component))
    check_charm_versions.output_diff(hash_1, hash_2, component, terse)


if __name__ == "__main__":
    main()

    

