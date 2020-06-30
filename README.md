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
```
danny@ubuntu:python diff_charm_versions.py contrail-agent-22 contrail-agent-21
Outputing difference between:
395491c2a0efb1a60fca9c6629ee410e233b15de & 44a88096178ef7525a9e274673ffb206619d3f45

Only showing diffs of files relating to the component: 'contrail-agent'
================================================================================
diff of 'contrail-agent/hooks/common_utils.py':
@@ -143,8 +143,8 @@ def update_services_status(module, services):
     status_set("active", "Unit is ready")
     try:
         tag = config.get('image-tag')
-        docker_utils.pull("contrail-base", tag)
-        version = docker_utils.get_contrail_version("contrail-base", tag)
+        docker_utils.pull("contrail-node-init", tag)
+        version = docker_utils.get_contrail_version("contrail-node-init", tag)
         application_version_set(version)
     except CalledProcessError as e:
         log("Couldn't detect installed application version: " + str(e))
================================================================================
diff of 'contrail-agent/templates/vrouter.env':
@@ -68,7 +68,7 @@ VROUTER_ENCRYPTION=FALSE
 VROUTER_HOSTNAME={{ hostname }}
 
 {%- if sriov_physical_interface and sriov_numvfs %}
-{%- if contrail_version|int < 2008 %}
+{%- if contrail_version < 2008 %}
 SRIOV_PHYSICAL_INTERFACE={{ sriov_physical_interface.split(',')[0] }}
 SRIOV_VF={{ sriov_numvfs.split(',')[0] }}
 {%- else %}

```
