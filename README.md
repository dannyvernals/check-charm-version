# Tools to analyse juju charms

# check-charm-version
Compare the commit hashes of Contrail charm versions to infer compatibility.  
The script queries the juju charm store for Contrail component charms.  
It captures the referenced git commit hash for each component and compares them.  
It then queries Github for metadata about the relevant commit.

```
usage: check_charm_versions.py [-h]
                               agent analytics analyticsdb controller keystone
                               openstack

compare charm commit hashes

positional arguments:
  agent        contrail-agent charm version
  analytics    contrail-analytics charm version
  analyticsdb  contrail-analyticsdb charm version
  controller   contrail-controller charm version
  keystone     contrail-keystone-auth charm version
  openstack    contrail-openstack charm version

optional arguments:
  -h, --help   show this help message and exit
```

For example:
```
python check-charm-versions.py contrail-agent-18 contrail-analytics-16 contrail-analyticsdb-16 \
                               contrail-controller-17 contrail-keystone-auth-16 contrail-openstack-19
Or
python check-charm-versions.py `juju export-bundle | grep juniper-os-software |awk -F \/ '{print $2}' | xargs`
```


## diff-charm-versions
Find the github commit hashes of Contrail components in the juju charm store.
Diff these commits and output the code differences between them. 

Usage:

```
python ./diff_charm_versions.py --help
usage: diff_charm_versions.py [-h] charm_1 charm_2

diff charm commit hashes.

positional arguments:
  charm_1     charm version 1 e.g. contrail-agent-21
  charm_2     charm version 2 e.g. contrail-agent-22

optional arguments:
  -h, --help  show this help message and exit
```

For example:

