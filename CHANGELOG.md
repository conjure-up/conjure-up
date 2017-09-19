# Change Log

## [2.3.1](https://github.com/conjure-up/conjure-up/tree/2.3.1) (2017-09-19)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.3.0...2.3.1)

**Fixed bugs:**

- Bootstrap fails if ipv6 enabled on LXD [\#1151](https://github.com/conjure-up/conjure-up/issues/1151)

**Merged pull requests:**

- Improves on LXD error handling and reporting [\#1153](https://github.com/conjure-up/conjure-up/pull/1153) ([battlemidget](https://github.com/battlemidget))
- Add maintainers doc [\#1149](https://github.com/conjure-up/conjure-up/pull/1149) ([battlemidget](https://github.com/battlemidget))

## [2.3.0](https://github.com/conjure-up/conjure-up/tree/2.3.0) (2017-09-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.2...2.3.0)

**Implemented enhancements:**

- update bundled lxd to handle things like reboots [\#1020](https://github.com/conjure-up/conjure-up/issues/1020)
- use aioredis [\#1015](https://github.com/conjure-up/conjure-up/issues/1015)
- How to get conjure-up with packaged LXD to use lxdbr0 [\#1023](https://github.com/conjure-up/conjure-up/issues/1023)
- make use of lxd preseed init data [\#949](https://github.com/conjure-up/conjure-up/issues/949)
- start/stop redis during execution of conjure-up [\#923](https://github.com/conjure-up/conjure-up/issues/923)
- use state server for handling step results [\#910](https://github.com/conjure-up/conjure-up/issues/910)
- add redis for state caching and step-2-step intercommunication [\#901](https://github.com/conjure-up/conjure-up/issues/901)
- Update screen selection/ordering [\#897](https://github.com/conjure-up/conjure-up/issues/897)
- Provide better feedback if shutdown process takes some time [\#835](https://github.com/conjure-up/conjure-up/issues/835)
- existing controllers filtered by type as well [\#771](https://github.com/conjure-up/conjure-up/issues/771)
- allow user to select a model on a controller to deploy to [\#753](https://github.com/conjure-up/conjure-up/issues/753)

**Fixed bugs:**

- MAAS bootstrap fails when default-credential is set [\#1141](https://github.com/conjure-up/conjure-up/issues/1141)
- hangs on master - Waiting for kube-system pods to start [\#1134](https://github.com/conjure-up/conjure-up/issues/1134)
- GUI: JaaS controller already exists error [\#1131](https://github.com/conjure-up/conjure-up/issues/1131)
- Object of type 'IPv4Network' is not JSON serializable [\#1127](https://github.com/conjure-up/conjure-up/issues/1127)
- Unable to use conjure-up to deploy helm and kubernetes on fresh ubuntu 16.04.03-LTS-x64 [\#1125](https://github.com/conjure-up/conjure-up/issues/1125)
- Constraints not met when deploying CDK [\#1123](https://github.com/conjure-up/conjure-up/issues/1123)
- Error bootstrapping controller: \['ERROR Get https://10.0.116.1:46783/1.0: unexpected EOF'\] [\#1073](https://github.com/conjure-up/conjure-up/issues/1073)
- Failed to create LXD conjureup1 network bridge: error: Failed to run: dnsmasq - Address already in use [\#1064](https://github.com/conjure-up/conjure-up/issues/1064)
- conjure-up does not work out-of-the-box in a minimal virtual machine installation - Could not determine LXD version [\#1062](https://github.com/conjure-up/conjure-up/issues/1062)
- AttributeError: module 'requests' has no attribute 'RequestsHTTPTransport' [\#1029](https://github.com/conjure-up/conjure-up/issues/1029)
- unable to parse snap versions like 2.25~14.04 [\#1027](https://github.com/conjure-up/conjure-up/issues/1027)
- better handling of managing app\_config global state data [\#1019](https://github.com/conjure-up/conjure-up/issues/1019)
- azure provider, tenant-id no longer needed [\#1013](https://github.com/conjure-up/conjure-up/issues/1013)
- Retry step 00\_deploy-done [\#1003](https://github.com/conjure-up/conjure-up/issues/1003)
- Retry creating LXD conjureup network bridges [\#998](https://github.com/conjure-up/conjure-up/issues/998)
- permission denied accessing ~/.local/share/juju [\#991](https://github.com/conjure-up/conjure-up/issues/991)
- Exception: Could not find a suitable physical network interface to create a LXD bridge on. Please check your... [\#990](https://github.com/conjure-up/conjure-up/issues/990)
- Exception: Unable to get info for controller conjure-up-localhost-0a7:  [\#987](https://github.com/conjure-up/conjure-up/issues/987)
- make sure localhost deployments survive reboots [\#985](https://github.com/conjure-up/conjure-up/issues/985)
- timeout in sentry code [\#970](https://github.com/conjure-up/conjure-up/issues/970)
- Exception: Problem setting default profile: CompletedProcess\(args='cat /tmp/tmpcpcb753i |conjure-up.lxc prof... [\#967](https://github.com/conjure-up/conjure-up/issues/967)
- Stuck in "waiting for applications to start" [\#890](https://github.com/conjure-up/conjure-up/issues/890)
- Unable to add machine, db locked [\#886](https://github.com/conjure-up/conjure-up/issues/886)
- Exception: Could not determine LXD version. [\#683](https://github.com/conjure-up/conjure-up/issues/683)
- Exception: Failure in step 00\_deploy-done [\#1025](https://github.com/conjure-up/conjure-up/issues/1025)
- ConnectionRefusedError: \[Errno 111\] Connect call failed \('10.218.149.192', 17070\) [\#995](https://github.com/conjure-up/conjure-up/issues/995)
- Exception: Unable to create model: ERROR failed to open environ: Get https://10.159.252.1:12001/1.0: Unable ... [\#989](https://github.com/conjure-up/conjure-up/issues/989)
- Exception: Unable to determine controller: ERROR opening API connection: unable to connect to API: dial tcp ... [\#988](https://github.com/conjure-up/conjure-up/issues/988)
- KeyError: 'details' [\#966](https://github.com/conjure-up/conjure-up/issues/966)
- can not select existing controller to deploy to [\#950](https://github.com/conjure-up/conjure-up/issues/950)
- TypeError 'NoneType' object is not subscriptable [\#946](https://github.com/conjure-up/conjure-up/issues/946)
- failed to set lxc config [\#943](https://github.com/conjure-up/conjure-up/issues/943)
- Failed to create LXD conjureup1 network bridge: error: Failed to run: dnsmasq --strict-order --bind-interfaces [\#942](https://github.com/conjure-up/conjure-up/issues/942)
- hooklib.writer log needs update [\#938](https://github.com/conjure-up/conjure-up/issues/938)
- Exception: Unable to determine controller: ERROR controller conjure-up-controller not found [\#937](https://github.com/conjure-up/conjure-up/issues/937)
- Conjure-up is not able to use existing maas provider after snap remove and re-install [\#927](https://github.com/conjure-up/conjure-up/issues/927)
- MAAS provider line asks for URL http:IP:port/MAAS but inserts the /MAAS into that URL  [\#925](https://github.com/conjure-up/conjure-up/issues/925)
- traceback with application facade [\#924](https://github.com/conjure-up/conjure-up/issues/924)
- Hadoop-spark bundle calls a charm version not available \(hadoop-plugin-21\) [\#918](https://github.com/conjure-up/conjure-up/issues/918)
- Error Deploying Openstack: Could not find a suitable network interface... with NovaLXD in a nested LXD  [\#916](https://github.com/conjure-up/conjure-up/issues/916)
- Stuck on "Waiting For Applications To Start" with NovaLXD in a nested LXD [\#915](https://github.com/conjure-up/conjure-up/issues/915)
- make sure MTU 1500 is set for lxd profiles [\#904](https://github.com/conjure-up/conjure-up/issues/904)
- better error handling in steps [\#889](https://github.com/conjure-up/conjure-up/issues/889)
- Problem with container IPs - Juju can't reach them [\#865](https://github.com/conjure-up/conjure-up/issues/865)
- Unable to install OpenStack on single node with conjure-up [\#858](https://github.com/conjure-up/conjure-up/issues/858)
- Snap fails to install, with ERROR: '~ubuntu-lxc' user or team does not exist [\#818](https://github.com/conjure-up/conjure-up/issues/818)
- syncing spell repository: handle git related conflicts better [\#813](https://github.com/conjure-up/conjure-up/issues/813)
- headless maas deployments fail with 'services' error [\#757](https://github.com/conjure-up/conjure-up/issues/757)
- Juju Bootstrap to MAAS should not do --debug [\#742](https://github.com/conjure-up/conjure-up/issues/742)
- Continues forever but doesn't do anything. [\#729](https://github.com/conjure-up/conjure-up/issues/729)
- Openstack fails to correctly deploy when network device is not eth0 [\#728](https://github.com/conjure-up/conjure-up/issues/728)
- Openstack spell fails on next steps [\#711](https://github.com/conjure-up/conjure-up/issues/711)

**Closed issues:**

- Can't Access Services Outside Cluster Network \(LXD installation\) [\#1144](https://github.com/conjure-up/conjure-up/issues/1144)
- conjure-up $ADDON [\#1139](https://github.com/conjure-up/conjure-up/issues/1139)
- fix form field querying in provider [\#1137](https://github.com/conjure-up/conjure-up/issues/1137)
- setting conjure-up.lxd waitready --timeout=X [\#1133](https://github.com/conjure-up/conjure-up/issues/1133)
- The Canonical Distribution \(kube on Ubuntu\) cannot find apiserver config file [\#1130](https://github.com/conjure-up/conjure-up/issues/1130)
- conjure-up failed to initiate containers: Error : ERROR juju.provisioner provisioner\_task.go:707 cannot start instance for machine "0/lxd/2": failed to bridge devices: bridge activaction error: bridge activation failed: Killed old client process [\#1128](https://github.com/conjure-up/conjure-up/issues/1128)
- Document how to custom openstack deployed with Autopilot [\#1118](https://github.com/conjure-up/conjure-up/issues/1118)
- addon's should pull step metadata from providertype if exists [\#1110](https://github.com/conjure-up/conjure-up/issues/1110)
- show addon description in addon list [\#1105](https://github.com/conjure-up/conjure-up/issues/1105)
- support bundle fragments for addons [\#1103](https://github.com/conjure-up/conjure-up/issues/1103)
- Openstack NovaLXD stuck at Bootstrapping Juju controller [\#1098](https://github.com/conjure-up/conjure-up/issues/1098)
- unmounted /dev/.lxc causing problems to hosted storage providers \(rook and quartermasters\) via CDK [\#1096](https://github.com/conjure-up/conjure-up/issues/1096)
- set default radio on vsphere setup screen [\#1086](https://github.com/conjure-up/conjure-up/issues/1086)
- shim cloud credentials [\#1084](https://github.com/conjure-up/conjure-up/issues/1084)
- Implement initial add-on screen for cdk spell - Deis only [\#1082](https://github.com/conjure-up/conjure-up/issues/1082)
- Define "unbundle lxd" tasks [\#1081](https://github.com/conjure-up/conjure-up/issues/1081)
- Test EBS on AWS cloud-native [\#1080](https://github.com/conjure-up/conjure-up/issues/1080)
- Update docs for cloud-native stuff [\#1079](https://github.com/conjure-up/conjure-up/issues/1079)
- Update docs for vsphere [\#1078](https://github.com/conjure-up/conjure-up/issues/1078)
- error in ubuntu 16.04 while installing the openstack using conjure-up parameter [\#1077](https://github.com/conjure-up/conjure-up/issues/1077)
- Unable to bootstrap \(Cloud type: maas\) [\#1076](https://github.com/conjure-up/conjure-up/issues/1076)
- LXC Shows nothing after fresh install and 1 instance running [\#1074](https://github.com/conjure-up/conjure-up/issues/1074)
- Pass vsphere network parameters through to bootstrap [\#1058](https://github.com/conjure-up/conjure-up/issues/1058)
- Add screen that lists network switch, external network, and data sources [\#1057](https://github.com/conjure-up/conjure-up/issues/1057)
- Include client to query vsphere [\#1056](https://github.com/conjure-up/conjure-up/issues/1056)
- Do aws-specific stuff in spell - create StorageClass, PVCs, etc [\#1055](https://github.com/conjure-up/conjure-up/issues/1055)
- Set --cloud-provider on master and worker and restart snap services [\#1054](https://github.com/conjure-up/conjure-up/issues/1054)
- Create IAM roles for cluster nodes \(pre-deploy\) [\#1053](https://github.com/conjure-up/conjure-up/issues/1053)
- Bundle AWS cli with conjure-up [\#1052](https://github.com/conjure-up/conjure-up/issues/1052)
- LXD give user to select lxc network bridge [\#1051](https://github.com/conjure-up/conjure-up/issues/1051)
- LXD give user ability to select storage pool [\#1050](https://github.com/conjure-up/conjure-up/issues/1050)
- Add check for LXD presence [\#1049](https://github.com/conjure-up/conjure-up/issues/1049)
- make LXD optional [\#1048](https://github.com/conjure-up/conjure-up/issues/1048)
- VSphere: Query API to gather network switches, ext network, datasources [\#1047](https://github.com/conjure-up/conjure-up/issues/1047)
- conjure-up unable to bootstrap lxd juju on zesty [\#1046](https://github.com/conjure-up/conjure-up/issues/1046)
- conjure-up on bonded network interface could not find a suitable physical network interface to create a LXD bridge on. [\#1044](https://github.com/conjure-up/conjure-up/issues/1044)
- Problem running lxd init: error: Unable to talk to LXD [\#1043](https://github.com/conjure-up/conjure-up/issues/1043)
- switch from redis to sqlite [\#1039](https://github.com/conjure-up/conjure-up/issues/1039)
- included juju wait missing -r argument [\#1035](https://github.com/conjure-up/conjure-up/issues/1035)
- Unrecoverable error when application has an empty readme [\#1034](https://github.com/conjure-up/conjure-up/issues/1034)
- TagMarkupException [\#1026](https://github.com/conjure-up/conjure-up/issues/1026)
- error occurs when run the installer non-interactively \(headless mode\)  in MacOS [\#1018](https://github.com/conjure-up/conjure-up/issues/1018)
- Delay bootstrap, jaas login, add-model until after configuration is done [\#1012](https://github.com/conjure-up/conjure-up/issues/1012)
- Record last known deploy state [\#1010](https://github.com/conjure-up/conjure-up/issues/1010)
- Move steps view before deploy status [\#1009](https://github.com/conjure-up/conjure-up/issues/1009)
- KeyError: 'getgrnam\(\): name not found: lxd' [\#1007](https://github.com/conjure-up/conjure-up/issues/1007)
- AttributeError: 'NoneType' object has no attribute 'keys' [\#1006](https://github.com/conjure-up/conjure-up/issues/1006)
- cloud native support [\#895](https://github.com/conjure-up/conjure-up/issues/895)
- Document how to access containers deployed with Autopilot [\#881](https://github.com/conjure-up/conjure-up/issues/881)
- Kubectl not finding the "config" file after deployment with error "The connection to the server localhost:8080 was refused" [\#790](https://github.com/conjure-up/conjure-up/issues/790)
- Adding machines with kvm causes conjure-up Oops \(localhost controller\) [\#610](https://github.com/conjure-up/conjure-up/issues/610)
- Architecture view lets you add machines without making it clear there won't be any units assigned. [\#604](https://github.com/conjure-up/conjure-up/issues/604)
- spells need to be able to specify what hw architecture they support [\#594](https://github.com/conjure-up/conjure-up/issues/594)
- Registered DNS names don't reflect same names specified in configuration Edit [\#593](https://github.com/conjure-up/conjure-up/issues/593)
- fails to deploy on s390x [\#592](https://github.com/conjure-up/conjure-up/issues/592)
- document extending sudo timeout [\#1104](https://github.com/conjure-up/conjure-up/issues/1104)
- remove status icon in steps view and keep only in runsteps [\#1102](https://github.com/conjure-up/conjure-up/issues/1102)
- Error on macOS trying to deploy using local controller with MAAS [\#1083](https://github.com/conjure-up/conjure-up/issues/1083)
- conjure-up unable to obtain a node from MAAS [\#876](https://github.com/conjure-up/conjure-up/issues/876)
- Juju failed to bootstrap: maas [\#817](https://github.com/conjure-up/conjure-up/issues/817)
- Add details about spells/deployments on the website [\#791](https://github.com/conjure-up/conjure-up/issues/791)
- Improve handling of "cannot get user details" error during JAAS registration [\#745](https://github.com/conjure-up/conjure-up/issues/745)
- Snap install conjure-up doesn't work if juju is installed [\#719](https://github.com/conjure-up/conjure-up/issues/719)
- conjure-up continue operations [\#624](https://github.com/conjure-up/conjure-up/issues/624)
- on error, conjure-up presents 'quit' option that doesn't quit  [\#607](https://github.com/conjure-up/conjure-up/issues/607)

**Merged pull requests:**

- Flush output and improve color control in headless [\#1148](https://github.com/conjure-up/conjure-up/pull/1148) ([johnsca](https://github.com/johnsca))
- Skip logging Sentry errors [\#1147](https://github.com/conjure-up/conjure-up/pull/1147) ([johnsca](https://github.com/johnsca))
- Add support for `conjure-up $ADDON` [\#1146](https://github.com/conjure-up/conjure-up/pull/1146) ([battlemidget](https://github.com/battlemidget))
- Fix default-credential and default-region handling in setup\_maas [\#1143](https://github.com/conjure-up/conjure-up/pull/1143) ([johnsca](https://github.com/johnsca))
- Add ability to query provider input prior to save\_form [\#1138](https://github.com/conjure-up/conjure-up/pull/1138) ([battlemidget](https://github.com/battlemidget))
- Use cloud white/blacklist from selected addons only [\#1136](https://github.com/conjure-up/conjure-up/pull/1136) ([johnsca](https://github.com/johnsca))
- Fix allow JaaS controller not named 'jaas' in GUI [\#1132](https://github.com/conjure-up/conjure-up/pull/1132) ([simonklb](https://github.com/simonklb))
- Make sure we are storing IPv4Networks as strings in state db [\#1129](https://github.com/conjure-up/conjure-up/pull/1129) ([battlemidget](https://github.com/battlemidget))
- tracks addon selections [\#1126](https://github.com/conjure-up/conjure-up/pull/1126) ([battlemidget](https://github.com/battlemidget))
- properly associates constraints [\#1124](https://github.com/conjure-up/conjure-up/pull/1124) ([battlemidget](https://github.com/battlemidget))
- Add line padding between spell list and description [\#1122](https://github.com/conjure-up/conjure-up/pull/1122) ([battlemidget](https://github.com/battlemidget))
- Switch to sqlite backend [\#1121](https://github.com/conjure-up/conjure-up/pull/1121) ([battlemidget](https://github.com/battlemidget))
- Add ability to show steps per provider type [\#1120](https://github.com/conjure-up/conjure-up/pull/1120) ([battlemidget](https://github.com/battlemidget))
- Fix subordinates not showing on Deploy Status [\#1119](https://github.com/conjure-up/conjure-up/pull/1119) ([johnsca](https://github.com/johnsca))
- Use ordereddict for lxd devices, push default to front of dict [\#1117](https://github.com/conjure-up/conjure-up/pull/1117) ([battlemidget](https://github.com/battlemidget))
- Fix order of steps provided by addons [\#1116](https://github.com/conjure-up/conjure-up/pull/1116) ([johnsca](https://github.com/johnsca))
- Add lxd network/storage selector view [\#1115](https://github.com/conjure-up/conjure-up/pull/1115) ([battlemidget](https://github.com/battlemidget))
- Refactor Addon to have a proper model [\#1114](https://github.com/conjure-up/conjure-up/pull/1114) ([johnsca](https://github.com/johnsca))
- Checks for availability of LXD [\#1112](https://github.com/conjure-up/conjure-up/pull/1112) ([battlemidget](https://github.com/battlemidget))
- Removes lxd from snap [\#1111](https://github.com/conjure-up/conjure-up/pull/1111) ([battlemidget](https://github.com/battlemidget))
- Adds the addon's description in the view [\#1109](https://github.com/conjure-up/conjure-up/pull/1109) ([battlemidget](https://github.com/battlemidget))
- Add-ons improvements [\#1108](https://github.com/conjure-up/conjure-up/pull/1108) ([johnsca](https://github.com/johnsca))
- Refactor cloud type handling to fix errors [\#1107](https://github.com/conjure-up/conjure-up/pull/1107) ([johnsca](https://github.com/johnsca))
- Export known environment vars to make it easier to re-run steps [\#1106](https://github.com/conjure-up/conjure-up/pull/1106) ([battlemidget](https://github.com/battlemidget))
- Support add-ons in spells [\#1100](https://github.com/conjure-up/conjure-up/pull/1100) ([johnsca](https://github.com/johnsca))
- Fix region not being passed to JAAS [\#1095](https://github.com/conjure-up/conjure-up/pull/1095) ([johnsca](https://github.com/johnsca))
- Remove disabling of os-upgrade during juju bootstrap [\#1094](https://github.com/conjure-up/conjure-up/pull/1094) ([battlemidget](https://github.com/battlemidget))
- Use short-name from juju status [\#1093](https://github.com/conjure-up/conjure-up/pull/1093) ([battlemidget](https://github.com/battlemidget))
- Set radio defaults in vspheresetup [\#1092](https://github.com/conjure-up/conjure-up/pull/1092) ([battlemidget](https://github.com/battlemidget))
- Refactor how steps are run [\#1091](https://github.com/conjure-up/conjure-up/pull/1091) ([johnsca](https://github.com/johnsca))
- Do not overwrite existing AWS cred if already configured [\#1090](https://github.com/conjure-up/conjure-up/pull/1090) ([johnsca](https://github.com/johnsca))
- We were return access-key twice in credential manager [\#1089](https://github.com/conjure-up/conjure-up/pull/1089) ([battlemidget](https://github.com/battlemidget))
- Set auth-type for localhost provider [\#1088](https://github.com/conjure-up/conjure-up/pull/1088) ([battlemidget](https://github.com/battlemidget))
- Fix error in shutdown\_watcher [\#1087](https://github.com/conjure-up/conjure-up/pull/1087) ([johnsca](https://github.com/johnsca))
- Fix CredentialManagerInvalidCloudType [\#1085](https://github.com/conjure-up/conjure-up/pull/1085) ([johnsca](https://github.com/johnsca))
- Provider refactor and add enhanced VSphere support [\#1075](https://github.com/conjure-up/conjure-up/pull/1075) ([battlemidget](https://github.com/battlemidget))
- Include pwgen in snap [\#1072](https://github.com/conjure-up/conjure-up/pull/1072) ([johnsca](https://github.com/johnsca))
- Add symlink for conjure-up.lxc [\#1071](https://github.com/conjure-up/conjure-up/pull/1071) ([mpontillo](https://github.com/mpontillo))
- Minor initial dev env cleanup [\#1069](https://github.com/conjure-up/conjure-up/pull/1069) ([mpontillo](https://github.com/mpontillo))
- Small improvements to shutdown and error handling [\#1068](https://github.com/conjure-up/conjure-up/pull/1068) ([johnsca](https://github.com/johnsca))
- Fix Next button on Show Steps screen not working with enter key [\#1065](https://github.com/conjure-up/conjure-up/pull/1065) ([johnsca](https://github.com/johnsca))
- Fix credential not being applied to add\_model or passed to pre-deploy [\#1063](https://github.com/conjure-up/conjure-up/pull/1063) ([johnsca](https://github.com/johnsca))
- Enable configuration of provider tools [\#1061](https://github.com/conjure-up/conjure-up/pull/1061) ([johnsca](https://github.com/johnsca))
- Add VMWare python bindings for VSphere [\#1060](https://github.com/conjure-up/conjure-up/pull/1060) ([battlemidget](https://github.com/battlemidget))
- Add awscli to pip requirements [\#1059](https://github.com/conjure-up/conjure-up/pull/1059) ([battlemidget](https://github.com/battlemidget))
- Delay bootstrap/add-model until after steps/deploy is done [\#1042](https://github.com/conjure-up/conjure-up/pull/1042) ([battlemidget](https://github.com/battlemidget))
- Add mockup scripts for add-ons [\#1040](https://github.com/conjure-up/conjure-up/pull/1040) ([johnsca](https://github.com/johnsca))
- Move Steps view before Deploy [\#1037](https://github.com/conjure-up/conjure-up/pull/1037) ([johnsca](https://github.com/johnsca))
- Temporarily use branch of juju-wait until fix is released [\#1033](https://github.com/conjure-up/conjure-up/pull/1033) ([johnsca](https://github.com/johnsca))
- Enhance travis-ci [\#1031](https://github.com/conjure-up/conjure-up/pull/1031) ([battlemidget](https://github.com/battlemidget))
- Add test for sentry\_report and fix it being accidentally blocking [\#1030](https://github.com/conjure-up/conjure-up/pull/1030) ([johnsca](https://github.com/johnsca))
- Improve Sentry reporting and update juju-wait for --retry\_errors option [\#1028](https://github.com/conjure-up/conjure-up/pull/1028) ([johnsca](https://github.com/johnsca))
- Latest LXD wrappers solve issues we were facing with lxcfs [\#1022](https://github.com/conjure-up/conjure-up/pull/1022) ([battlemidget](https://github.com/battlemidget))
- State storage for Application config [\#1017](https://github.com/conjure-up/conjure-up/pull/1017) ([battlemidget](https://github.com/battlemidget))
- Azure tenant id no longer required [\#1014](https://github.com/conjure-up/conjure-up/pull/1014) ([battlemidget](https://github.com/battlemidget))
- Using wrong test flag for checking unix.socket [\#1008](https://github.com/conjure-up/conjure-up/pull/1008) ([battlemidget](https://github.com/battlemidget))
- Do not track incompatible snapd versions [\#1005](https://github.com/conjure-up/conjure-up/pull/1005) ([battlemidget](https://github.com/battlemidget))
- Validate ~/.local/share/juju is accessible [\#1002](https://github.com/conjure-up/conjure-up/pull/1002) ([battlemidget](https://github.com/battlemidget))
- Create CODE\_OF\_CONDUCT.md [\#996](https://github.com/conjure-up/conjure-up/pull/996) ([battlemidget](https://github.com/battlemidget))
- Temporarily disable interface selection [\#993](https://github.com/conjure-up/conjure-up/pull/993) ([johnsca](https://github.com/johnsca))
- Dont retry setting current\_cloud [\#992](https://github.com/conjure-up/conjure-up/pull/992) ([battlemidget](https://github.com/battlemidget))
- Feature/910 enable redis state server [\#911](https://github.com/conjure-up/conjure-up/pull/911) ([battlemidget](https://github.com/battlemidget))

## [2.2.2](https://github.com/conjure-up/conjure-up/tree/2.2.2) (2017-06-23)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.1...2.2.2)

**Fixed bugs:**

- jaas login failures [\#983](https://github.com/conjure-up/conjure-up/issues/983)
- port 12001 collides with nomachine users [\#975](https://github.com/conjure-up/conjure-up/issues/975)
- Warn user if not part of LXD group when deploying localhost [\#973](https://github.com/conjure-up/conjure-up/issues/973)
- conjure-up doesn't handle "This should \_not\_ be run as root or with sudo." messaging correctly anymore. [\#969](https://github.com/conjure-up/conjure-up/issues/969)
- JujuAPIError: watcher was stopped [\#965](https://github.com/conjure-up/conjure-up/issues/965)
- OSError: \[Errno 28\] No space left on device [\#963](https://github.com/conjure-up/conjure-up/issues/963)
- ValueError: Unknown format code 'd' for object of type 'str' [\#962](https://github.com/conjure-up/conjure-up/issues/962)
- OSError: \[Errno 28\] No space left on device: '/home/ubuntu/.cache/conjure-up/canonical-kubernetes' [\#959](https://github.com/conjure-up/conjure-up/issues/959)
- permission denied accessing lxd unix.socket [\#956](https://github.com/conjure-up/conjure-up/issues/956)
- conjure-up localhost unable to locate liblxc.so.1 [\#955](https://github.com/conjure-up/conjure-up/issues/955)
- AttributeError: 'str' object has no attribute 'keys' [\#954](https://github.com/conjure-up/conjure-up/issues/954)
- ValueError list.remove\(x\): x not in list [\#948](https://github.com/conjure-up/conjure-up/issues/948)

**Merged pull requests:**

- Fix JAAS registration [\#984](https://github.com/conjure-up/conjure-up/pull/984) ([johnsca](https://github.com/johnsca))
- Ignore error attempting to deploy unknown application [\#981](https://github.com/conjure-up/conjure-up/pull/981) ([johnsca](https://github.com/johnsca))
- Fix "Unknown format code" error [\#980](https://github.com/conjure-up/conjure-up/pull/980) ([johnsca](https://github.com/johnsca))
- Pick unused port for bundled lxd to listen on [\#978](https://github.com/conjure-up/conjure-up/pull/978) ([battlemidget](https://github.com/battlemidget))
- Verify running user can access LXD daemon [\#976](https://github.com/conjure-up/conjure-up/pull/976) ([battlemidget](https://github.com/battlemidget))
- Dont track certain exceptions [\#974](https://github.com/conjure-up/conjure-up/pull/974) ([battlemidget](https://github.com/battlemidget))
- This prepends the $SNAP/lib to ld\_library\_path [\#972](https://github.com/conjure-up/conjure-up/pull/972) ([battlemidget](https://github.com/battlemidget))
- Handle clouds with no regions [\#971](https://github.com/conjure-up/conjure-up/pull/971) ([johnsca](https://github.com/johnsca))
- Make sure LD\_LIBRARY\_PATH is set for our lxd/lxc/redis wrappers [\#968](https://github.com/conjure-up/conjure-up/pull/968) ([battlemidget](https://github.com/battlemidget))
- Ensures correct permissions on lxd unix.socket [\#958](https://github.com/conjure-up/conjure-up/pull/958) ([battlemidget](https://github.com/battlemidget))
- Sanitize data sent in automated error reporting [\#979](https://github.com/conjure-up/conjure-up/pull/979) ([johnsca](https://github.com/johnsca))

## [2.2.1](https://github.com/conjure-up/conjure-up/tree/2.2.1) (2017-06-20)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0...2.2.1)

**Implemented enhancements:**

- Add Sentry support for tracking errors [\#931](https://github.com/conjure-up/conjure-up/issues/931)

**Fixed bugs:**

- JSONDecodeError: Expecting value: line 1 column 2 \(char 1\) [\#935](https://github.com/conjure-up/conjure-up/issues/935)

**Merged pull requests:**

- Improve error handling when getting controller info [\#953](https://github.com/conjure-up/conjure-up/pull/953) ([johnsca](https://github.com/johnsca))
- Remove dnsmasq hold on an interface during network creation [\#952](https://github.com/conjure-up/conjure-up/pull/952) ([battlemidget](https://github.com/battlemidget))
- Fix existing controller detection [\#951](https://github.com/conjure-up/conjure-up/pull/951) ([johnsca](https://github.com/johnsca))
- Bootstrap given controller if not found [\#947](https://github.com/conjure-up/conjure-up/pull/947) ([johnsca](https://github.com/johnsca))
- Include more info in failed step reports [\#945](https://github.com/conjure-up/conjure-up/pull/945) ([johnsca](https://github.com/johnsca))
- More lxd retries for times when socket isn't completely ready [\#944](https://github.com/conjure-up/conjure-up/pull/944) ([battlemidget](https://github.com/battlemidget))
- Fix NoneType error from no step result [\#941](https://github.com/conjure-up/conjure-up/pull/941) ([johnsca](https://github.com/johnsca))
- fix logger and print output in hooklib writer [\#939](https://github.com/conjure-up/conjure-up/pull/939) ([battlemidget](https://github.com/battlemidget))
- No longer parsing json data from step output [\#936](https://github.com/conjure-up/conjure-up/pull/936) ([battlemidget](https://github.com/battlemidget))
- Do not filter out interfaces if run inside a container [\#934](https://github.com/conjure-up/conjure-up/pull/934) ([battlemidget](https://github.com/battlemidget))
- Add Sentry automatic error reporting [\#933](https://github.com/conjure-up/conjure-up/pull/933) ([johnsca](https://github.com/johnsca))

## [2.2.0](https://github.com/conjure-up/conjure-up/tree/2.2.0) (2017-06-15)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta4...2.2.0)

**Implemented enhancements:**

- decide on top level juju alias [\#917](https://github.com/conjure-up/conjure-up/issues/917)
- should spell steps have conditions based on cloud provider [\#633](https://github.com/conjure-up/conjure-up/issues/633)
- FYI "juju login -B" is the new "juju register"... [\#891](https://github.com/conjure-up/conjure-up/issues/891)
- make sure region selection is always visible [\#883](https://github.com/conjure-up/conjure-up/issues/883)
- region selection for jaas deployment [\#882](https://github.com/conjure-up/conjure-up/issues/882)
- add prebootstrap process hook [\#863](https://github.com/conjure-up/conjure-up/issues/863)
- embed lxd [\#850](https://github.com/conjure-up/conjure-up/issues/850)
- enable oracle provider [\#833](https://github.com/conjure-up/conjure-up/issues/833)
- \[ARM64\] Need conjure-up snap in snap store [\#828](https://github.com/conjure-up/conjure-up/issues/828)
- bootstrap exception capture cloud type [\#789](https://github.com/conjure-up/conjure-up/issues/789)
- bundlewriter should place generated bundles inside their cached spell dir [\#787](https://github.com/conjure-up/conjure-up/issues/787)
- push localhost requirements to the cloud picker [\#772](https://github.com/conjure-up/conjure-up/issues/772)
- Add sudo support for spells [\#758](https://github.com/conjure-up/conjure-up/issues/758)
- support bootstrap to a region for public cloud in gui mode [\#715](https://github.com/conjure-up/conjure-up/issues/715)
- support conjure-up on vmware/vsphere [\#709](https://github.com/conjure-up/conjure-up/issues/709)
- Support juju login for JAAS support [\#708](https://github.com/conjure-up/conjure-up/issues/708)
- migrate to libjuju [\#697](https://github.com/conjure-up/conjure-up/issues/697)
- better error feedback on user input screens [\#686](https://github.com/conjure-up/conjure-up/issues/686)
- export bundle after mutations [\#621](https://github.com/conjure-up/conjure-up/issues/621)

**Fixed bugs:**

- lxdbr0 set as default for localhost cloud [\#921](https://github.com/conjure-up/conjure-up/issues/921)
- credentials being populated incorrectly [\#907](https://github.com/conjure-up/conjure-up/issues/907)
- unexpected keyword argument 'agent-version' [\#903](https://github.com/conjure-up/conjure-up/issues/903)
- Unable to deploy kubernetes-core using --edge and MAAS Version 2.1.5+bzr5596-0ubuntu1 \(16.04.1\) [\#894](https://github.com/conjure-up/conjure-up/issues/894)
- selecting existing maas controller bootstraps a new machine [\#892](https://github.com/conjure-up/conjure-up/issues/892)
- saving of credentials happens prior to a current\_controller being set [\#888](https://github.com/conjure-up/conjure-up/issues/888)
- Cannot retrieve charm "cs:haproxy-41"  [\#874](https://github.com/conjure-up/conjure-up/issues/874)
- snap configure hook could just run `lxc version` to determine if installation needed [\#873](https://github.com/conjure-up/conjure-up/issues/873)
- snap configure hook shouldn't use just "zesty" to determine archive lxd suitability [\#872](https://github.com/conjure-up/conjure-up/issues/872)
- snap install fails with spurious `apt-get` errors [\#871](https://github.com/conjure-up/conjure-up/issues/871)
- ubuntui version in requirements.txt [\#868](https://github.com/conjure-up/conjure-up/issues/868)
- charm not found error when deploying spell from an edge channel [\#862](https://github.com/conjure-up/conjure-up/issues/862)
- Duplicate machines \(co-location\) not properly handled by "deploy all" [\#857](https://github.com/conjure-up/conjure-up/issues/857)
- Failures in automated tests [\#854](https://github.com/conjure-up/conjure-up/issues/854)
- conjure-down failed with “login\(\) got an unexpected keyword arument ‘force’ “ [\#845](https://github.com/conjure-up/conjure-up/issues/845)
- conjure-up crashes on macos [\#839](https://github.com/conjure-up/conjure-up/issues/839)
- conjure-down stacktraces [\#832](https://github.com/conjure-up/conjure-up/issues/832)
- libjuju: headless failure to add machines [\#829](https://github.com/conjure-up/conjure-up/issues/829)
- There was an error during the pre deploy processing phase, failure to set profile [\#825](https://github.com/conjure-up/conjure-up/issues/825)
- \_\_init\_\_\(\) got an unexpected keyword argument 'default' [\#821](https://github.com/conjure-up/conjure-up/issues/821)
- Conjure-up screen does not get past adding machine\['0'\] [\#819](https://github.com/conjure-up/conjure-up/issues/819)
- entering sudo password fails to allow a snap to install [\#816](https://github.com/conjure-up/conjure-up/issues/816)
- error during conjure-up landscape to an existing maas controller [\#814](https://github.com/conjure-up/conjure-up/issues/814)
- Conjure up isn't bootstraping juju [\#810](https://github.com/conjure-up/conjure-up/issues/810)
- conjure-up error: Unable to find credentials for cloud looking for local-host [\#807](https://github.com/conjure-up/conjure-up/issues/807)
- Deployment of kubernetes-core crashes on 2.2-beta3 [\#806](https://github.com/conjure-up/conjure-up/issues/806)
- azure: need to make sure generated model names are less than 80 char [\#795](https://github.com/conjure-up/conjure-up/issues/795)
- Calling incorrect ensure\_machines when cloud name != maas [\#794](https://github.com/conjure-up/conjure-up/issues/794)
- Deploying with Juju 2.2 beta1 and vsphere provider - Conjure-up errors with: Application did not start successfully [\#785](https://github.com/conjure-up/conjure-up/issues/785)
- on OSX conjure-up openstack throws traceback [\#779](https://github.com/conjure-up/conjure-up/issues/779)
- OS X "Unable to find model" [\#778](https://github.com/conjure-up/conjure-up/issues/778)
- conjure-up errors on the kubernetes-core spell on OSX [\#776](https://github.com/conjure-up/conjure-up/issues/776)
- maas deploy error in get\_models [\#774](https://github.com/conjure-up/conjure-up/issues/774)
- conjure-up breaks bsdtar \(& possibly others\) due to lib install hook [\#770](https://github.com/conjure-up/conjure-up/issues/770)
- can\_sudo always fails [\#764](https://github.com/conjure-up/conjure-up/issues/764)
- macOS: steps don't require sudo [\#763](https://github.com/conjure-up/conjure-up/issues/763)
- KeyError: KeyError\('CONJURE\_UP\_CACHEDIR',\) [\#747](https://github.com/conjure-up/conjure-up/issues/747)
- output truncated in summary view if current view is filled [\#738](https://github.com/conjure-up/conjure-up/issues/738)
- confusing error if step00-\* are not executable [\#736](https://github.com/conjure-up/conjure-up/issues/736)
- password fields - inputs are shown in clear text [\#735](https://github.com/conjure-up/conjure-up/issues/735)
- not able to use boolean values in steps [\#734](https://github.com/conjure-up/conjure-up/issues/734)
- strings that don't have a default specified -  didn't show an input box [\#733](https://github.com/conjure-up/conjure-up/issues/733)
- Conjure-up Openstack-novalxd fails to multiple errors [\#726](https://github.com/conjure-up/conjure-up/issues/726)

**Closed issues:**

- Invalid signature when conjure-up juju [\#914](https://github.com/conjure-up/conjure-up/issues/914)
- Installing OpenStack from Landscape not working [\#893](https://github.com/conjure-up/conjure-up/issues/893)
- Conjure-up openstack deployment stuck at last step "additional-application-tasks"  [\#885](https://github.com/conjure-up/conjure-up/issues/885)
- Can not attach volume to an instance [\#884](https://github.com/conjure-up/conjure-up/issues/884)
- Landscape install waiting status 16.04 conjure-up [\#844](https://github.com/conjure-up/conjure-up/issues/844)
- MAAS is not completing a successful node deployment [\#843](https://github.com/conjure-up/conjure-up/issues/843)
- Failing to connect to LXD server when deploying spells [\#841](https://github.com/conjure-up/conjure-up/issues/841)
- Conjure-up --bootstrap-to \<hostname\> no progress  'fetching juju agent version 2.1.2 for amd64' [\#824](https://github.com/conjure-up/conjure-up/issues/824)
- Reason: Juju failed to bootstrap: maas [\#822](https://github.com/conjure-up/conjure-up/issues/822)
- conjure-up doesn't set terminal title [\#775](https://github.com/conjure-up/conjure-up/issues/775)
- Unable to install via: brew install conjure-up --HEAD [\#762](https://github.com/conjure-up/conjure-up/issues/762)
- rework logging wording for tracking exceptions [\#714](https://github.com/conjure-up/conjure-up/issues/714)

**Merged pull requests:**

- Validates that a snap version is compatible with our localhost deployments [\#928](https://github.com/conjure-up/conjure-up/pull/928) ([battlemidget](https://github.com/battlemidget))
- Revert "Make sure lxd profile is correct for our bridges" [\#926](https://github.com/conjure-up/conjure-up/pull/926) ([battlemidget](https://github.com/battlemidget))
- Make sure lxd profile is correct for our bridges [\#922](https://github.com/conjure-up/conjure-up/pull/922) ([battlemidget](https://github.com/battlemidget))
- Prevent snap alias collisions [\#920](https://github.com/conjure-up/conjure-up/pull/920) ([johnsca](https://github.com/johnsca))
- Fix problem syncing registry [\#912](https://github.com/conjure-up/conjure-up/pull/912) ([battlemidget](https://github.com/battlemidget))
- Use a auto generated name for credentials user key [\#909](https://github.com/conjure-up/conjure-up/pull/909) ([battlemidget](https://github.com/battlemidget))
- Flip the default value for allow\_exists on add\_model [\#906](https://github.com/conjure-up/conjure-up/pull/906) ([johnsca](https://github.com/johnsca))
- Adds redis-server to snap [\#902](https://github.com/conjure-up/conjure-up/pull/902) ([battlemidget](https://github.com/battlemidget))
- Move cloud selection screen forward [\#900](https://github.com/conjure-up/conjure-up/pull/900) ([johnsca](https://github.com/johnsca))
- WIP: First crack at asyncio tailing of step output [\#898](https://github.com/conjure-up/conjure-up/pull/898) ([battlemidget](https://github.com/battlemidget))
- Add screens for selecting region and credential [\#887](https://github.com/conjure-up/conjure-up/pull/887) ([johnsca](https://github.com/johnsca))
- Include our own LXD to not conflict with rest of users system. \(\#852\) [\#880](https://github.com/conjure-up/conjure-up/pull/880) ([battlemidget](https://github.com/battlemidget))

## [2.2.0-beta4](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta4) (2017-05-11)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta3...2.2.0-beta4)

**Closed issues:**

- Juju beta4 breaks auth [\#878](https://github.com/conjure-up/conjure-up/issues/878)

**Merged pull requests:**

- Fix JAAS registration for 2.2-beta4 [\#879](https://github.com/conjure-up/conjure-up/pull/879) ([johnsca](https://github.com/johnsca))
- Allow to run without installation [\#870](https://github.com/conjure-up/conjure-up/pull/870) ([techtonik](https://github.com/techtonik))

## [2.2.0-beta3](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta3) (2017-05-09)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.5...2.2.0-beta3)

**Fixed bugs:**

- conjure-up from edge r154 nonetype exception deploying landscape on maas [\#773](https://github.com/conjure-up/conjure-up/issues/773)

**Closed issues:**

- Incompatibility with LXD 2.13 [\#866](https://github.com/conjure-up/conjure-up/issues/866)
- Openstack Autopilot deployment on Ubuntu 16.04 LTS [\#851](https://github.com/conjure-up/conjure-up/issues/851)
- Failed to set profile [\#849](https://github.com/conjure-up/conjure-up/issues/849)
- Openstack with NovaLXD installation failure [\#724](https://github.com/conjure-up/conjure-up/issues/724)

**Merged pull requests:**

- Update HACKING.md [\#869](https://github.com/conjure-up/conjure-up/pull/869) ([techtonik](https://github.com/techtonik))
- Adds pre-bootstrap hook [\#864](https://github.com/conjure-up/conjure-up/pull/864) ([battlemidget](https://github.com/battlemidget))
- Fix headless deploy blocking indefinitely [\#861](https://github.com/conjure-up/conjure-up/pull/861) ([johnsca](https://github.com/johnsca))
- Fix extra machines being created [\#860](https://github.com/conjure-up/conjure-up/pull/860) ([johnsca](https://github.com/johnsca))
- Revert "Include our own LXD to not conflict with rest of users system." [\#853](https://github.com/conjure-up/conjure-up/pull/853) ([battlemidget](https://github.com/battlemidget))
- Include our own LXD to not conflict with rest of users system. [\#852](https://github.com/conjure-up/conjure-up/pull/852) ([battlemidget](https://github.com/battlemidget))
- integrate region selection in credentials view [\#847](https://github.com/conjure-up/conjure-up/pull/847) ([battlemidget](https://github.com/battlemidget))
- Fix conjure-down [\#846](https://github.com/conjure-up/conjure-up/pull/846) ([johnsca](https://github.com/johnsca))
- Add better add cloud [\#840](https://github.com/conjure-up/conjure-up/pull/840) ([battlemidget](https://github.com/battlemidget))
- Add message to indicate shutdown [\#838](https://github.com/conjure-up/conjure-up/pull/838) ([johnsca](https://github.com/johnsca))
- oracle provider [\#837](https://github.com/conjure-up/conjure-up/pull/837) ([battlemidget](https://github.com/battlemidget))
- Fix error handling and logging in conjure-down [\#834](https://github.com/conjure-up/conjure-up/pull/834) ([johnsca](https://github.com/johnsca))
- Fix add\_machines failure in headless [\#830](https://github.com/conjure-up/conjure-up/pull/830) ([johnsca](https://github.com/johnsca))
- Switch to libjuju and asyncio [\#713](https://github.com/conjure-up/conjure-up/pull/713) ([johnsca](https://github.com/johnsca))

## [2.1.5](https://github.com/conjure-up/conjure-up/tree/2.1.5) (2017-04-15)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.4...2.1.5)

## [2.1.4](https://github.com/conjure-up/conjure-up/tree/2.1.4) (2017-04-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.3...2.1.4)

## [2.1.3](https://github.com/conjure-up/conjure-up/tree/2.1.3) (2017-04-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta2...2.1.3)

**Fixed bugs:**

- The "install-dependencies" and "install" make targets don't work. [\#804](https://github.com/conjure-up/conjure-up/issues/804)

**Closed issues:**

- error to build Openstack Cloud  [\#812](https://github.com/conjure-up/conjure-up/issues/812)
- deploy of Landscape in Openstack Autopilot is in permanent pending status [\#805](https://github.com/conjure-up/conjure-up/issues/805)
- Expired timestamp [\#803](https://github.com/conjure-up/conjure-up/issues/803)
- Error while conjuring up kubernetes-core "Applications did not start successfully" [\#802](https://github.com/conjure-up/conjure-up/issues/802)
- Upgrade to Ocata breaks openstack-novaxld [\#801](https://github.com/conjure-up/conjure-up/issues/801)

**Merged pull requests:**

- Feature/better input validation/686 [\#809](https://github.com/conjure-up/conjure-up/pull/809) ([battlemidget](https://github.com/battlemidget))
- Fix error with normalization of lxd / localhost [\#808](https://github.com/conjure-up/conjure-up/pull/808) ([johnsca](https://github.com/johnsca))
- Bug/738/scroll results summary [\#800](https://github.com/conjure-up/conjure-up/pull/800) ([battlemidget](https://github.com/battlemidget))
- Fix normalization of lxd / localhost cloud type [\#799](https://github.com/conjure-up/conjure-up/pull/799) ([johnsca](https://github.com/johnsca))
- More cloud type checks [\#798](https://github.com/conjure-up/conjure-up/pull/798) ([battlemidget](https://github.com/battlemidget))
- Fixes \#794 - checks correct cloud type for maas/enable default series [\#797](https://github.com/conjure-up/conjure-up/pull/797) ([battlemidget](https://github.com/battlemidget))
- Fixes \#795 shorten model name to max 28 characters [\#796](https://github.com/conjure-up/conjure-up/pull/796) ([battlemidget](https://github.com/battlemidget))
- Filter controllers by cloud by type instead of name [\#793](https://github.com/conjure-up/conjure-up/pull/793) ([johnsca](https://github.com/johnsca))
- Fix "invalid file" error when reading spell bundle [\#792](https://github.com/conjure-up/conjure-up/pull/792) ([johnsca](https://github.com/johnsca))

## [2.2.0-beta2](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta2) (2017-03-30)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta1...2.2.0-beta2)

**Merged pull requests:**

- Fixes \#775 [\#786](https://github.com/conjure-up/conjure-up/pull/786) ([battlemidget](https://github.com/battlemidget))
- Fixes \#556 [\#783](https://github.com/conjure-up/conjure-up/pull/783) ([battlemidget](https://github.com/battlemidget))
- Fix trace from sudo check if no steps [\#769](https://github.com/conjure-up/conjure-up/pull/769) ([johnsca](https://github.com/johnsca))
- Improve error handling for sudo in GUI flow [\#768](https://github.com/conjure-up/conjure-up/pull/768) ([johnsca](https://github.com/johnsca))
- Improve can\_sudo check [\#767](https://github.com/conjure-up/conjure-up/pull/767) ([johnsca](https://github.com/johnsca))
- Fixes \#763 [\#766](https://github.com/conjure-up/conjure-up/pull/766) ([battlemidget](https://github.com/battlemidget))
- Fixes \#764 [\#765](https://github.com/conjure-up/conjure-up/pull/765) ([battlemidget](https://github.com/battlemidget))

## [2.2.0-beta1](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta1) (2017-03-23)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.2...2.2.0-beta1)

**Fixed bugs:**

- "not redirected" error on deploy screen for localhost [\#746](https://github.com/conjure-up/conjure-up/issues/746)

**Closed issues:**

- MAAS registration in Landscape requires a URI, not an IP [\#756](https://github.com/conjure-up/conjure-up/issues/756)
- "architecture" option to select maas node didn't work [\#755](https://github.com/conjure-up/conjure-up/issues/755)
- Snap install fails [\#750](https://github.com/conjure-up/conjure-up/issues/750)
- conjure-up kubernetes gives stacktrace  [\#727](https://github.com/conjure-up/conjure-up/issues/727)
- Snap conjure-up fails to start [\#718](https://github.com/conjure-up/conjure-up/issues/718)

**Merged pull requests:**

- Add sudo support for spells [\#761](https://github.com/conjure-up/conjure-up/pull/761) ([johnsca](https://github.com/johnsca))
- Proposal: Allow re-use of an existing model in headless mode. [\#760](https://github.com/conjure-up/conjure-up/pull/760) ([petevg](https://github.com/petevg))
- Fix handling of boolean step inputs [\#754](https://github.com/conjure-up/conjure-up/pull/754) ([johnsca](https://github.com/johnsca))
- Drops global config, simplifies registry remote [\#752](https://github.com/conjure-up/conjure-up/pull/752) ([battlemidget](https://github.com/battlemidget))
- Improve error handling around JaaS registration [\#751](https://github.com/conjure-up/conjure-up/pull/751) ([johnsca](https://github.com/johnsca))
- Fixes \#747 [\#749](https://github.com/conjure-up/conjure-up/pull/749) ([battlemidget](https://github.com/battlemidget))
- Merge with bug fix in bundleplacer upstream [\#748](https://github.com/conjure-up/conjure-up/pull/748) ([mikemccracken](https://github.com/mikemccracken))
- Add support for JAAS [\#743](https://github.com/conjure-up/conjure-up/pull/743) ([johnsca](https://github.com/johnsca))
- Fixes \#736 [\#741](https://github.com/conjure-up/conjure-up/pull/741) ([battlemidget](https://github.com/battlemidget))
- Save bundle file with modifications [\#739](https://github.com/conjure-up/conjure-up/pull/739) ([mikemccracken](https://github.com/mikemccracken))
- Fix issues with deploying some charms [\#732](https://github.com/conjure-up/conjure-up/pull/732) ([mikemccracken](https://github.com/mikemccracken))
- s/deployment/model [\#731](https://github.com/conjure-up/conjure-up/pull/731) ([mikemccracken](https://github.com/mikemccracken))

## [2.1.2](https://github.com/conjure-up/conjure-up/tree/2.1.2) (2017-03-10)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.1...2.1.2)

**Fixed bugs:**

- conjure-up shared libraries leaking out to system ldconfig [\#717](https://github.com/conjure-up/conjure-up/issues/717)
- Exception calling callback for \<Future at 0x7f4fd00db080 state=finished returned NoneType\> [\#712](https://github.com/conjure-up/conjure-up/issues/712)
- Setting lxd profile fails [\#695](https://github.com/conjure-up/conjure-up/issues/695)
- Error deploying to AWS when default region changed - conjure-up does not form correct bootstrap command when juju default aws region set [\#693](https://github.com/conjure-up/conjure-up/issues/693)
- Conjure up won't bootstrap a named LXD cloud on Zesty [\#576](https://github.com/conjure-up/conjure-up/issues/576)

## [2.1.1](https://github.com/conjure-up/conjure-up/tree/2.1.1) (2017-03-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0...2.1.1)

**Fixed bugs:**

- failed to use 'lxd' for conjure-up [\#675](https://github.com/conjure-up/conjure-up/issues/675)

**Closed issues:**

- "LookupError: Unable to list models: error: No controllers registered." [\#707](https://github.com/conjure-up/conjure-up/issues/707)
- snap won't install due to lxd-service failing to start [\#706](https://github.com/conjure-up/conjure-up/issues/706)
- Typo in Manual Docs [\#705](https://github.com/conjure-up/conjure-up/issues/705)
- Error deploying: cannot add application "ceph-osd": DB is locked | conjure-up setup [\#704](https://github.com/conjure-up/conjure-up/issues/704)
- Unable to install openstack with nova LXD on Ubuntu 16.04. Error stating IpV6 enabled even though disabled [\#703](https://github.com/conjure-up/conjure-up/issues/703)
- lxd openstack - is there a way to  have custom names or more related names for containers? [\#701](https://github.com/conjure-up/conjure-up/issues/701)

**Merged pull requests:**

- Allow for 'side-loading' additional charm options for applications [\#700](https://github.com/conjure-up/conjure-up/pull/700) ([battlemidget](https://github.com/battlemidget))

## [2.1.0](https://github.com/conjure-up/conjure-up/tree/2.1.0) (2017-02-22)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-rc1...2.1.0)

**Implemented enhancements:**

- LXD openstack: installation failure [\#688](https://github.com/conjure-up/conjure-up/issues/688)
- track OS [\#661](https://github.com/conjure-up/conjure-up/issues/661)
- Allow specifying model name in headless [\#635](https://github.com/conjure-up/conjure-up/issues/635)
- provide way to de-conjure-up a spell [\#596](https://github.com/conjure-up/conjure-up/issues/596)
- Need warning about small terminal sizes affecting usability [\#585](https://github.com/conjure-up/conjure-up/issues/585)
- using localhost with lxd init has confusing instructions [\#565](https://github.com/conjure-up/conjure-up/issues/565)
- Better JSON errors during processing scripts results [\#563](https://github.com/conjure-up/conjure-up/issues/563)

**Fixed bugs:**

- Crash during the install of OpenStack with NovaLXD [\#673](https://github.com/conjure-up/conjure-up/issues/673)
- kubenetes core spell failed on localhost \(LXD\) [\#690](https://github.com/conjure-up/conjure-up/issues/690)
- Conjure Up failed on post-processing openstack-base [\#687](https://github.com/conjure-up/conjure-up/issues/687)
- snap: persists network/iptables configuration on reboot [\#685](https://github.com/conjure-up/conjure-up/issues/685)
- snap: fix network create on trusty [\#684](https://github.com/conjure-up/conjure-up/issues/684)
- headless conjure-up kubernetes-core fails, while GUI does work [\#676](https://github.com/conjure-up/conjure-up/issues/676)
- Failed to run pre deploy task: Expecting value: line 1 column 1  [\#674](https://github.com/conjure-up/conjure-up/issues/674)
- dont set perms on .cache dir if run as root [\#662](https://github.com/conjure-up/conjure-up/issues/662)
- zesty/yakkety snap conjure-up fails to load iptables rules [\#649](https://github.com/conjure-up/conjure-up/issues/649)
- conjure-up isn't properly handling a failed bootstrap [\#641](https://github.com/conjure-up/conjure-up/issues/641)
- conjure-up kubernetes crashes and doesn't run post steps but juju status looks good [\#623](https://github.com/conjure-up/conjure-up/issues/623)
- Better JSON errors during processing scripts results [\#563](https://github.com/conjure-up/conjure-up/issues/563)

**Closed issues:**

- Snap based installation fails [\#691](https://github.com/conjure-up/conjure-up/issues/691)
- snap install conjure-up --classic --stable fails in lxd privileged container [\#689](https://github.com/conjure-up/conjure-up/issues/689)
- conjure-up openstack crash [\#671](https://github.com/conjure-up/conjure-up/issues/671)
- Unable to conjure-up kubernetes with OpenStack [\#617](https://github.com/conjure-up/conjure-up/issues/617)
- document running localhost provided spells on remote systems [\#672](https://github.com/conjure-up/conjure-up/issues/672)
- Document Allow specifying model name in headless [\#670](https://github.com/conjure-up/conjure-up/issues/670)
- log lxd and juju versions [\#668](https://github.com/conjure-up/conjure-up/issues/668)
- Documentation: need to install snapd manually [\#658](https://github.com/conjure-up/conjure-up/issues/658)
- add machine count to destroy confirmation page [\#627](https://github.com/conjure-up/conjure-up/issues/627)
- track cloud selections [\#622](https://github.com/conjure-up/conjure-up/issues/622)
- num\_units is not necessary with the architecture view [\#615](https://github.com/conjure-up/conjure-up/issues/615)
- docs: developer documentation for step writing needs to cover stdout being JSON only [\#614](https://github.com/conjure-up/conjure-up/issues/614)
- sometimes the bootstrap output is way too wide [\#590](https://github.com/conjure-up/conjure-up/issues/590)
- Should warn on smaller terminal geometry [\#584](https://github.com/conjure-up/conjure-up/issues/584)
- bootstrap wait output should be left justified [\#577](https://github.com/conjure-up/conjure-up/issues/577)
- download kubectl and put it in ~/bin/kubectl [\#568](https://github.com/conjure-up/conjure-up/issues/568)
- add custom systctl options to the deb packaging [\#562](https://github.com/conjure-up/conjure-up/issues/562)
- handle inclusion of lxd snap [\#560](https://github.com/conjure-up/conjure-up/issues/560)

**Merged pull requests:**

- Revert "Fixes \#615" [\#682](https://github.com/conjure-up/conjure-up/pull/682) ([battlemidget](https://github.com/battlemidget))
- Add HACKING.txt [\#681](https://github.com/conjure-up/conjure-up/pull/681) ([mikemccracken](https://github.com/mikemccracken))
- Warn on upgrading to snap lxd if deb lxd exists [\#678](https://github.com/conjure-up/conjure-up/pull/678) ([battlemidget](https://github.com/battlemidget))
- Fixes an issue on localhost deploying to nested lxd [\#677](https://github.com/conjure-up/conjure-up/pull/677) ([battlemidget](https://github.com/battlemidget))

## [2.1.0-rc1](https://github.com/conjure-up/conjure-up/tree/2.1.0-rc1) (2017-02-10)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-beta5...2.1.0-rc1)

**Implemented enhancements:**

- use juju-wait deprecate 00-deploy\_done script [\#651](https://github.com/conjure-up/conjure-up/issues/651)

**Fixed bugs:**

- conjure-up for openstack lxd fails: "No controllers registered." [\#659](https://github.com/conjure-up/conjure-up/issues/659)
- traceback in conjure-up [\#653](https://github.com/conjure-up/conjure-up/issues/653)

**Closed issues:**

- Conjure-up openstack on Ubuntu 16.10 Crash [\#656](https://github.com/conjure-up/conjure-up/issues/656)
- non-integer constraints not handled correctly for add-machines API  [\#654](https://github.com/conjure-up/conjure-up/issues/654)
- Fresh install of conjure-up fails [\#652](https://github.com/conjure-up/conjure-up/issues/652)
- "Unable to list models: {}".format\(sh.stderr.decode\('utf8'\)\)\) [\#574](https://github.com/conjure-up/conjure-up/issues/574)
- First run on new system gets stack trace [\#566](https://github.com/conjure-up/conjure-up/issues/566)

**Merged pull requests:**

- Better error dialog handling, especially for bootstrap failures [\#667](https://github.com/conjure-up/conjure-up/pull/667) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#661 [\#665](https://github.com/conjure-up/conjure-up/pull/665) ([battlemidget](https://github.com/battlemidget))
- Fixes \#662 [\#664](https://github.com/conjure-up/conjure-up/pull/664) ([battlemidget](https://github.com/battlemidget))
- Fixes \#615 [\#660](https://github.com/conjure-up/conjure-up/pull/660) ([battlemidget](https://github.com/battlemidget))
- Expose MAAS endpoint and api\_key for use in steps [\#657](https://github.com/conjure-up/conjure-up/pull/657) ([battlemidget](https://github.com/battlemidget))
- Always store constraint values as ints, MiB units [\#655](https://github.com/conjure-up/conjure-up/pull/655) ([mikemccracken](https://github.com/mikemccracken))
- Allow specifying model in headless mode [\#638](https://github.com/conjure-up/conjure-up/pull/638) ([battlemidget](https://github.com/battlemidget))

## [2.1.0-beta5](https://github.com/conjure-up/conjure-up/tree/2.1.0-beta5) (2017-02-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-pre-snappy...2.1.0-beta5)

**Implemented enhancements:**

- allow specifying custom controller in headless mode [\#639](https://github.com/conjure-up/conjure-up/issues/639)
- add ability to customize model name in UI [\#637](https://github.com/conjure-up/conjure-up/issues/637)

**Closed issues:**

- Remove juju from snap now that's it's classic [\#646](https://github.com/conjure-up/conjure-up/issues/646)
- Spells-dir expects git repo and public internet access [\#645](https://github.com/conjure-up/conjure-up/issues/645)
- Crash when running conjure-down [\#644](https://github.com/conjure-up/conjure-up/issues/644)
- gnome-terminal colors get brighter after exiting conjure-up [\#632](https://github.com/conjure-up/conjure-up/issues/632)
- Support deploying to other regions in a cloud [\#630](https://github.com/conjure-up/conjure-up/issues/630)
- Conjure-up fails on egress-filtered network due to GA unavailability [\#629](https://github.com/conjure-up/conjure-up/issues/629)
- Oops when running false for required in a step [\#611](https://github.com/conjure-up/conjure-up/issues/611)
- conjure-up quits if a charm hook error happens [\#609](https://github.com/conjure-up/conjure-up/issues/609)
- conjure-up ui does not work on 80x24 terminal [\#605](https://github.com/conjure-up/conjure-up/issues/605)
- running pre-deployment tasks non-responsive [\#602](https://github.com/conjure-up/conjure-up/issues/602)
- conjure up stops on hook error even though juju retries [\#601](https://github.com/conjure-up/conjure-up/issues/601)
- Spell selection doesn't highlight requirements \(or any other spell+bundle details\) [\#599](https://github.com/conjure-up/conjure-up/issues/599)
- Not obvious how to report a bug [\#598](https://github.com/conjure-up/conjure-up/issues/598)
- conjure-up uses petname for model name [\#595](https://github.com/conjure-up/conjure-up/issues/595)
- show list of existing credentials to use instead of entering new ones [\#589](https://github.com/conjure-up/conjure-up/issues/589)
- If lxc is used, conjure-up needs to deal with lxc problems too [\#587](https://github.com/conjure-up/conjure-up/issues/587)
- It's not clear whether I should use the mouse or keyboard [\#583](https://github.com/conjure-up/conjure-up/issues/583)
- Button name changes [\#573](https://github.com/conjure-up/conjure-up/issues/573)
- juju bootstrap progress [\#571](https://github.com/conjure-up/conjure-up/issues/571)

**Merged pull requests:**

- Adds optional ability to use an existing spell dir [\#647](https://github.com/conjure-up/conjure-up/pull/647) ([battlemidget](https://github.com/battlemidget))
- Warn if terminal geometry is to small [\#642](https://github.com/conjure-up/conjure-up/pull/642) ([battlemidget](https://github.com/battlemidget))
- Fixes \#627 [\#640](https://github.com/conjure-up/conjure-up/pull/640) ([battlemidget](https://github.com/battlemidget))
- Indicate the distribution switch from deb to snap [\#634](https://github.com/conjure-up/conjure-up/pull/634) ([battlemidget](https://github.com/battlemidget))
- Add conjure-down [\#625](https://github.com/conjure-up/conjure-up/pull/625) ([battlemidget](https://github.com/battlemidget))
- Re-adds percentage and pads the logging a bit [\#620](https://github.com/conjure-up/conjure-up/pull/620) ([battlemidget](https://github.com/battlemidget))
- Fixes \#595 [\#619](https://github.com/conjure-up/conjure-up/pull/619) ([battlemidget](https://github.com/battlemidget))
- Fix 541 [\#618](https://github.com/conjure-up/conjure-up/pull/618) ([mikemccracken](https://github.com/mikemccracken))
- bson python library no longer needed [\#616](https://github.com/conjure-up/conjure-up/pull/616) ([battlemidget](https://github.com/battlemidget))
- Fixes \#495 [\#613](https://github.com/conjure-up/conjure-up/pull/613) ([battlemidget](https://github.com/battlemidget))
- Point to upstream bug url for reporting bugs [\#612](https://github.com/conjure-up/conjure-up/pull/612) ([battlemidget](https://github.com/battlemidget))
- Snappy updates [\#581](https://github.com/conjure-up/conjure-up/pull/581) ([battlemidget](https://github.com/battlemidget))

## [2.1.0-pre-snappy](https://github.com/conjure-up/conjure-up/tree/2.1.0-pre-snappy) (2017-01-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.2...2.1.0-pre-snappy)

**Closed issues:**

- deploying kubernetes-core onto LXD breaks due to nested LXDs [\#578](https://github.com/conjure-up/conjure-up/issues/578)
- misleading error when ipv6 is enabled in lxd [\#570](https://github.com/conjure-up/conjure-up/issues/570)

**Merged pull requests:**

- Left justify bootstrap wait output [\#580](https://github.com/conjure-up/conjure-up/pull/580) ([battlemidget](https://github.com/battlemidget))
- Ignore placement specs for LXD controllers [\#579](https://github.com/conjure-up/conjure-up/pull/579) ([mikemccracken](https://github.com/mikemccracken))
- Ensure that bundle placement directives are always used and shown in UI [\#564](https://github.com/conjure-up/conjure-up/pull/564) ([mikemccracken](https://github.com/mikemccracken))
- Snap sysctl increase [\#561](https://github.com/conjure-up/conjure-up/pull/561) ([battlemidget](https://github.com/battlemidget))

## [2.0.2](https://github.com/conjure-up/conjure-up/tree/2.0.2) (2016-10-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1...2.0.2)

## [2.0.1](https://github.com/conjure-up/conjure-up/tree/2.0.1) (2016-10-06)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1-beta2...2.0.1)

## [2.0.1-beta2](https://github.com/conjure-up/conjure-up/tree/2.0.1-beta2) (2016-09-26)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1-beta1...2.0.1-beta2)

## [2.0.1-beta1](https://github.com/conjure-up/conjure-up/tree/2.0.1-beta1) (2016-09-20)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.9...2.0.1-beta1)

## [2.0.0.9](https://github.com/conjure-up/conjure-up/tree/2.0.0.9) (2016-09-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.8...2.0.0.9)

## [2.0.0.8](https://github.com/conjure-up/conjure-up/tree/2.0.0.8) (2016-08-22)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.6...2.0.0.8)

## [2.0.0.6](https://github.com/conjure-up/conjure-up/tree/2.0.0.6) (2016-07-18)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.5...2.0.0.6)

## [2.0.0.5](https://github.com/conjure-up/conjure-up/tree/2.0.0.5) (2016-07-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.4...2.0.0.5)

## [2.0.0.4](https://github.com/conjure-up/conjure-up/tree/2.0.0.4) (2016-07-01)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.3...2.0.0.4)

## [2.0.0.3](https://github.com/conjure-up/conjure-up/tree/2.0.0.3) (2016-06-17)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.2...2.0.0.3)

## [2.0.0.2](https://github.com/conjure-up/conjure-up/tree/2.0.0.2) (2016-06-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.1...2.0.0.2)

## [2.0.0.1](https://github.com/conjure-up/conjure-up/tree/2.0.0.1) (2016-06-08)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.1.2...2.0.0.1)

## [0.1.2](https://github.com/conjure-up/conjure-up/tree/0.1.2) (2016-05-26)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.2.0...0.1.2)

## [0.2.0](https://github.com/conjure-up/conjure-up/tree/0.2.0) (2016-04-27)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.8...0.2.0)

## [0.0.8](https://github.com/conjure-up/conjure-up/tree/0.0.8) (2016-04-16)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.7...0.0.8)

## [0.0.7](https://github.com/conjure-up/conjure-up/tree/0.0.7) (2016-04-11)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.6...0.0.7)

## [0.0.6](https://github.com/conjure-up/conjure-up/tree/0.0.6) (2016-03-24)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*