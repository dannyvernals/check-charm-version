# Tools to analyse contrail juju charms

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
  -t, --terse  Show only differences in config.yaml. Good for checking if new
               configuration is needed or new features are available between
               versions
```

### Examples

1. Using terse option.

Contrail charms use a 'Documentation as Code' methodology.  Therefore features are often explained in the 
code itself, rather than in separate documents.  So it's useful to compare the code changes
between charm versions for release management purposes.  Any external configuration for charms are
exposed in the 'config.yaml' file within the charms so the terse option filters the diff to only that file.
```
python3 diff_charm_versions.py contrail-agent-18 contrail-agent-20 -t

Outputing difference between:
4e0a0a9174ddab2b6c641e0e84ddc35d95b4deea & 1e64438a96b3e43cc4f90ff379ad1648be5e06ed
Only showing diffs of files relating to the component: 'contrail-agent'
==========================================================================================
diff of 'contrail-agent/config.yaml':
@@ -36,16 +36,76 @@ options:
       instances.
       Value can be specified as percentage of system memory e.g. 70% or as
       number of huge pages e.g. 1434.
+  kernel-hugepages-1g:
+    type: string
+    description: |
+      Number of 1 GB huge pages to reserve for use with vRouter in kernel mode  and OpenStack instances.
+      Value can be specified as number of huge pages e.g. 10.
+      To turn off HP suppor completely kernel-hugepages-1g and kernel-hugepages-2m must be set as '0' both.
+      Supported from Contrail release 2005.
+  kernel-hugepages-2m:
+    type: string
+    default: '1024'
+    description: |
+      Number of 2 MB huge pages to reserve for use with vRouter in kernel mode  and OpenStack
+      instances.
+      Value can be specified as number of huge pages e.g. '1024'.
+      To turn off HP suppor completely kernel-hugepages-1g and kernel-hugepages-2m must be set as '0' both.
+      Supported from Contrail release 2005.
   dpdk-coremask:
     type: string
     default: "1"
     description: |
-      vRouter CPU affinity mask. Determines on which CPUs DPDK vRouter will run.
+      vRouter CPU affinity mask for dpdk forwarding threads.
+      Value can be specified as either a hexidecimal bitmask e.g. 0xF or
+      as a numbered list separated by commas e.g. 0,1 (ranges are also supported
+      using '-' e.g. 0-2).
+      It must specify only real cores cause contrail-vrouter-dpdk service will
+      fail if specified core number is not present in the system.
+  dpdk-service-coremask:
+    type: string
+    default: "1"
+    description: |
+      vRouter DPDK CPU affinity mask for dpdk service threads.
       Value can be specified as either a hexidecimal bitmask e.g. 0xF or
       as a numbered list separated by commas e.g. 0,1 (ranges are also supported
       using '-' e.g. 0-2).
       It must specify only real cores cause contrail-vrouter-dpdk service will
       fail if specified core number is not present in the system.
+      Supported from Contrail release 2003 and R1912.L2.
+  dpdk-ctrl-thread-coremask:
+    type: string
+    default: "1"
+    description: |
+      vRouter DPDK CPU affinity mask for dpdk ctrl threads.
+      Value can be specified as either a hexidecimal bitmask e.g. 0xF or
+      as a numbered list separated by commas e.g. 0,1 (ranges are also supported
+      using '-' e.g. 0-2).
+      It must specify only real cores cause contrail-vrouter-dpdk service will
+      fail if specified core number is not present in the system.
+      Supported from Contrail release 2003 and R1912.L2.
+  dpdk-rx-ring-sz:
+    type: string
+    default: ""
+    description: |
+      vRouter DPDK option to configure for forwarding lcores rx ring buffer size.
+      If not there is default in dpdk bin is used which is 1024.
+      Supported from Contrail release 2003 and R1912.L2.
+  dpdk-tx-ring-sz:
+    type: string
+    default: ""
+    description: |
+      vRouter DPDK option to configure for forwarding lcores tx ring buffer size.
+      If not there is default in dpdk bin is used which is 1024.
+      Supported from Contrail release 2003 and R1912.L2.
+  dpdk-yield-option:
+    type: string
+    default: ""
+    description: |
+      vRouter DPDK option to disable/enable yield on forwarding lcores.
+      Allowed values 0 / 1.
+      If not set the default behaviour is enalbed (1).
+      Supported from Contrail release 2003 and R1912.L2.
   dpdk-main-mempool-size:
     type: string
     description: |
@@ -68,6 +128,11 @@ options:
     description: |
       NumVFS for specified device. This parameter and sriov-physical-interface
       will be passed into agent container that will configure SR-IOV.
+  csn-mode:
+    type: string
+    description: |
+      The vrouter agent mode. The valid values are 'tor'/'tsn'/'tsn-no-forwarding' or empty.
+    default: ''
   log-level:
     type: string
     default: SYS_NOTICE
@@ -180,3 +245,8 @@ options:
     description: |
       A comma-separated list of nagios servicegroups.
       If left empty, the nagios_context will be used as the servicegroup
+  max-vm-flows:
+    default: ""
+    type: string
+    description: |
+      Maximum flows allowed per VM (given as % of maximum system flows) 
```

2. Full diff 

If you omit the terse flag, you will get a diff of all changes for that particular charm.
This is useful if you need a deep understanding of functional differences between charm versions.
For example, to validate bug fixes.

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
# find_common_charms
Find the charm versions for Contrail components that were commited to 'tf-charms' github repo at the same time.  
The script gets the commit hash to compare from 'repo-info' text file in each Contrail charm in the charm store.  
From this we can infer compatibility.  
Usage:
```
python3 find_common_charms.py -h
usage: find_common_charms.py [-h] charm_version

Find Contrail charm versions that were commited at the same time

positional arguments:
  charm_version  Charm version e.g. contrail-agent-21

optional arguments:
  -h, --help     show this help message and exit
```

Example:
```
danny@ubuntu:~/git_clones/check-charm-version$ python3 find_common_charms.py contrail-openstack-18
['contrail-openstack-18', 'contrail-agent-17', 'contrail-analytics-15', 'contrail-analyticsdb-15']

```

# check-charm-version
Compare the commit hashes of Contrail charm versions to infer compatibility.  
It also queries Github for metadata about the relevant commit.

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
