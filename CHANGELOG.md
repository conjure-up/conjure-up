# Change Log

## [2.6.6](https://github.com/conjure-up/conjure-up/tree/2.6.6) (2019-02-04)

**Fixed bugs:**

- Fix unable to select new controller (#1581)

## [2.6.5](https://github.com/conjure-up/conjure-up/tree/2.6.5) (2019-01-31)

**Implemented enhancements:**

- Update Juju to 2.5.0
- Update libjuju

**Fixed bugs:**

- Disable controllers which have no endpoints

## [2.6.4](https://github.com/conjure-up/conjure-up/tree/2.6.4) (2018-12-13)

**Fixed bugs:**

- Bump libjuju version to pick up subordinate fix (juju/python-libjuju#277) (#1560)

## [2.6.3](https://github.com/conjure-up/conjure-up/tree/2.6.3) (2018-12-13)

**Fixed bugs:**

- Fix bootstrap-series KeyError (#1558)

**Closed issues:**

- Fix error handling for invalid bundles (#1554)
- Update spells to fix CDK with Calico (conjure-up/spells#239)

## [2.6.2](https://github.com/conjure-up/conjure-up/tree/2.6.2) (2018-12-12)

**Implemented enhancements:**

- Update libjuju to support Juju 2.5 (#1557)
- Add bootstrap series override to Conjurefile (#1555)

**Closed issues:**

- Fix error handling for invalid bundles (#1554)
- Update spells to fix CDK with Calico (conjure-up/spells#239)

## [2.6.1](https://github.com/conjure-up/conjure-up/tree/2.6.1) (2018-9-20)

**Implemented enhancements:**

- Update libjuju to improve charm store query performance (#1512)
- Update bundled Juju version to 2.4.3

## [2.6.0](https://github.com/conjure-up/conjure-up/tree/2.6.0) (2018-07-16)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.9...2.6.0)

**Implemented enhancements:**

- Feature Request: support custom model config [\#1241](https://github.com/conjure-up/conjure-up/issues/1241)

**Closed issues:**

- Some applications failed to start successfully [\#1493](https://github.com/conjure-up/conjure-up/issues/1493)
- 'set' object does not support indexing [\#1491](https://github.com/conjure-up/conjure-up/issues/1491)
- Error when running conjure-up and choosing Openstack with NovaKVM : 'set' object does not support indexing                           [\#1487](https://github.com/conjure-up/conjure-up/issues/1487)

**Merged pull requests:**

- Update libjuju 0.9.1 [\#1497](https://github.com/conjure-up/conjure-up/pull/1497) ([battlemidget](https://github.com/battlemidget))
- Uses pyyaml 3.13 proper [\#1496](https://github.com/conjure-up/conjure-up/pull/1496) ([battlemidget](https://github.com/battlemidget))
- Fix case where no whitelisted clouds are enabled [\#1492](https://github.com/conjure-up/conjure-up/pull/1492) ([johnsca](https://github.com/johnsca))
- Send cloud name to steps [\#1490](https://github.com/conjure-up/conjure-up/pull/1490) ([johnsca](https://github.com/johnsca))
- Add option for branch and force sync [\#1489](https://github.com/conjure-up/conjure-up/pull/1489) ([johnsca](https://github.com/johnsca))
- Test multiple pythons, fix lint [\#1488](https://github.com/conjure-up/conjure-up/pull/1488) ([battlemidget](https://github.com/battlemidget))

## [2.5.9](https://github.com/conjure-up/conjure-up/tree/2.5.9) (2018-07-01)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.8...2.5.9)

**Closed issues:**

- Python 3.7 support [\#1484](https://github.com/conjure-up/conjure-up/issues/1484)
- Unable to find a storage pool for LXD [\#1483](https://github.com/conjure-up/conjure-up/issues/1483)

## [2.5.8](https://github.com/conjure-up/conjure-up/tree/2.5.8) (2018-06-29)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.7...2.5.8)

**Implemented enhancements:**

- MAAS introspection [\#896](https://github.com/conjure-up/conjure-up/issues/896)

**Fixed bugs:**

- Error setting up microk8s on Azure [\#1478](https://github.com/conjure-up/conjure-up/issues/1478)
- unable to attach aws ebs as persistent volume for kubernetes [\#1195](https://github.com/conjure-up/conjure-up/issues/1195)
- make sure conjure-up uses localcharms from a custom bundle [\#1032](https://github.com/conjure-up/conjure-up/issues/1032)

**Closed issues:**

- LXDBinaryNotFound when install Kubernetes via conjure-up [\#1477](https://github.com/conjure-up/conjure-up/issues/1477)
- AttributeError: 'Localhost' object has no attribute 'lxd\_bin' [\#1464](https://github.com/conjure-up/conjure-up/issues/1464)
- juju add-worker kubernetes-worker stuck on 'Waiting for kubelet to start' [\#1462](https://github.com/conjure-up/conjure-up/issues/1462)
- Localhost cluster fails after restart [\#1448](https://github.com/conjure-up/conjure-up/issues/1448)

**Merged pull requests:**

- Python 3.7 compatibility [\#1486](https://github.com/conjure-up/conjure-up/pull/1486) ([battlemidget](https://github.com/battlemidget))
- Fix incorrect exception name for LXDBinaryNotFoundError [\#1485](https://github.com/conjure-up/conjure-up/pull/1485) ([johnsca](https://github.com/johnsca))
- Dont allow snap spell types on macos [\#1480](https://github.com/conjure-up/conjure-up/pull/1480) ([battlemidget](https://github.com/battlemidget))
- Log actual data for LXDParseError [\#1473](https://github.com/conjure-up/conjure-up/pull/1473) ([johnsca](https://github.com/johnsca))
- Fix unable to select cloud when only public clouds are whitelisted [\#1471](https://github.com/conjure-up/conjure-up/pull/1471) ([johnsca](https://github.com/johnsca))
- Cleanup unused python deps [\#1469](https://github.com/conjure-up/conjure-up/pull/1469) ([battlemidget](https://github.com/battlemidget))
- Update controllers for spell-type snap [\#1467](https://github.com/conjure-up/conjure-up/pull/1467) ([battlemidget](https://github.com/battlemidget))
- File/Directory restructure for handling spell types [\#1466](https://github.com/conjure-up/conjure-up/pull/1466) ([battlemidget](https://github.com/battlemidget))
- Fixes 1464 [\#1465](https://github.com/conjure-up/conjure-up/pull/1465) ([battlemidget](https://github.com/battlemidget))
- Adds support for bypassing juju and performing custom deploys [\#1463](https://github.com/conjure-up/conjure-up/pull/1463) ([battlemidget](https://github.com/battlemidget))

## [2.5.7](https://github.com/conjure-up/conjure-up/tree/2.5.7) (2018-06-06)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.6...2.5.7)

**Fixed bugs:**

- No clear instruction why LXD\(localhost\) provider is not available with localhost-only spells [\#1441](https://github.com/conjure-up/conjure-up/issues/1441)
- Rackspace: image-stream=daily causes error [\#1398](https://github.com/conjure-up/conjure-up/issues/1398)
- Unable to list controllers: /bin/sh: 1: None: not found  [\#1352](https://github.com/conjure-up/conjure-up/issues/1352)
- conjure-down app.env\['PATH'\] -- NoneType object is not subscriptable [\#1338](https://github.com/conjure-up/conjure-up/issues/1338)
- Conjure-up fails while creating juju model with the following. exception: json: cannot unmarshal string into Go struct field Value.tags of type \[\]string [\#1301](https://github.com/conjure-up/conjure-up/issues/1301)
- conjure-down of localhost lxd openstack fails with AttributeError: 'NoneType' object has no attribute 'controller' [\#1182](https://github.com/conjure-up/conjure-up/issues/1182)

**Closed issues:**

- LXDSetupControllerError: Unable to determine ip address of lxdbr0, please double check `lxc network edit lxdbr0` and make ... [\#1454](https://github.com/conjure-up/conjure-up/issues/1454)
- LocalhostError: Unable to find a lxd binary. Make sure `snap info lxd` shows as installed, otherwise, run `sudo s... [\#1449](https://github.com/conjure-up/conjure-up/issues/1449)
- Can we use conjure-up for NovaLXD or NovaKVM without internet ? [\#1446](https://github.com/conjure-up/conjure-up/issues/1446)
- Too many placement specifications after config change [\#1435](https://github.com/conjure-up/conjure-up/issues/1435)
- Check lxd storage and networking earlier [\#1431](https://github.com/conjure-up/conjure-up/issues/1431)
- Conjure-up fails while "Juju Model is initializing" [\#1429](https://github.com/conjure-up/conjure-up/issues/1429)
- trying to deploy kubernetes: LXD Server or LXC client not compatible [\#1427](https://github.com/conjure-up/conjure-up/issues/1427)
- NTP not supported in containers: please configure on host [\#1417](https://github.com/conjure-up/conjure-up/issues/1417)
- Unable to boot strap \(cloud type: localhost\)  [\#1416](https://github.com/conjure-up/conjure-up/issues/1416)
- fix travis-ci [\#1414](https://github.com/conjure-up/conjure-up/issues/1414)
-  Waiting for kube-system pods to start [\#1412](https://github.com/conjure-up/conjure-up/issues/1412)
- Update website - http://webchat.freenode.net/ [\#1411](https://github.com/conjure-up/conjure-up/issues/1411)
- No attribute ControllerNotFound [\#1405](https://github.com/conjure-up/conjure-up/issues/1405)
- why not installed? [\#1400](https://github.com/conjure-up/conjure-up/issues/1400)
- cannot change profile for the next exec call: No such file or directory [\#1392](https://github.com/conjure-up/conjure-up/issues/1392)

**Merged pull requests:**

- Retry deploy on ConnectionClosed [\#1460](https://github.com/conjure-up/conjure-up/pull/1460) ([johnsca](https://github.com/johnsca))
- Add network and storage check for LXD to cloud screen [\#1459](https://github.com/conjure-up/conjure-up/pull/1459) ([johnsca](https://github.com/johnsca))
- Dont track LXD network errors [\#1455](https://github.com/conjure-up/conjure-up/pull/1455) ([battlemidget](https://github.com/battlemidget))
- Bump to Juju 2.3.8 [\#1453](https://github.com/conjure-up/conjure-up/pull/1453) ([battlemidget](https://github.com/battlemidget))
- Updates the raven python lib to latest stable [\#1452](https://github.com/conjure-up/conjure-up/pull/1452) ([battlemidget](https://github.com/battlemidget))
- Add LXD no binary found to sentry exception list [\#1450](https://github.com/conjure-up/conjure-up/pull/1450) ([battlemidget](https://github.com/battlemidget))
- Put color as an option [\#1447](https://github.com/conjure-up/conjure-up/pull/1447) ([gonfva](https://github.com/gonfva))
- Pass model-config options from conjurefile to juju [\#1444](https://github.com/conjure-up/conjure-up/pull/1444) ([battlemidget](https://github.com/battlemidget))
- Update libjuju [\#1439](https://github.com/conjure-up/conjure-up/pull/1439) ([johnsca](https://github.com/johnsca))
- Replace app data after configure rather than merge [\#1436](https://github.com/conjure-up/conjure-up/pull/1436) ([johnsca](https://github.com/johnsca))
- Update deps and make use of conjurefile for testing [\#1415](https://github.com/conjure-up/conjure-up/pull/1415) ([battlemidget](https://github.com/battlemidget))
- conjure-down fixes [\#1408](https://github.com/conjure-up/conjure-up/pull/1408) ([battlemidget](https://github.com/battlemidget))
- Process addons/steps in conjurefile [\#1407](https://github.com/conjure-up/conjure-up/pull/1407) ([battlemidget](https://github.com/battlemidget))
- Fix AttributeError: ControllerNotFoundException [\#1406](https://github.com/conjure-up/conjure-up/pull/1406) ([johnsca](https://github.com/johnsca))
- Fix missed usages of argv/opts values to Conjurefile [\#1403](https://github.com/conjure-up/conjure-up/pull/1403) ([johnsca](https://github.com/johnsca))
- Fix Conjurefile opts not being used in some places [\#1401](https://github.com/conjure-up/conjure-up/pull/1401) ([johnsca](https://github.com/johnsca))
- Bump Juju version [\#1395](https://github.com/conjure-up/conjure-up/pull/1395) ([battlemidget](https://github.com/battlemidget))
- Update Conjurefile templating [\#1394](https://github.com/conjure-up/conjure-up/pull/1394) ([battlemidget](https://github.com/battlemidget))

## [2.5.6](https://github.com/conjure-up/conjure-up/tree/2.5.6) (2018-04-04)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.5...2.5.6)

**Implemented enhancements:**

- use juju native bundle deploy [\#1329](https://github.com/conjure-up/conjure-up/issues/1329)

**Fixed bugs:**

- "Architect" kubernetes-worker unsupported operand type\(s\) for /: 'str' and 'int' [\#1365](https://github.com/conjure-up/conjure-up/issues/1365)
- after-input doesnt run on steps with no viewable additional-input metadata [\#1364](https://github.com/conjure-up/conjure-up/issues/1364)
- Conjure-up fails if unnecessary network endpoints are unavailable [\#1358](https://github.com/conjure-up/conjure-up/issues/1358)
- TypeError on configapps [\#1345](https://github.com/conjure-up/conjure-up/issues/1345)
- Conjure-up crashes upon using the "Architect" screen [\#1333](https://github.com/conjure-up/conjure-up/issues/1333)
- conjure-up Kubernetes not detecting LXD [\#1331](https://github.com/conjure-up/conjure-up/issues/1331)
- --add-bundle doesn't support local charms [\#1317](https://github.com/conjure-up/conjure-up/issues/1317)

**Closed issues:**

- No available deployment options Openstack\(even cannot deploy localhost\) [\#1382](https://github.com/conjure-up/conjure-up/issues/1382)
- Horizon default username and password with snap —classic —edge [\#1378](https://github.com/conjure-up/conjure-up/issues/1378)
- Automate the debug info gathering process? [\#1360](https://github.com/conjure-up/conjure-up/issues/1360)
- juju 2.4 credentials changed format [\#1355](https://github.com/conjure-up/conjure-up/issues/1355)
- conjure-up doesn't work on a freshly installed ubuntu server system unless apt update && apt upgrade actions are performed [\#1332](https://github.com/conjure-up/conjure-up/issues/1332)

**Merged pull requests:**

- Dont fail hard on incompatible LXD since it's an optional component [\#1391](https://github.com/conjure-up/conjure-up/pull/1391) ([battlemidget](https://github.com/battlemidget))
- Fail with a error message on incompatible lxd versions [\#1390](https://github.com/conjure-up/conjure-up/pull/1390) ([battlemidget](https://github.com/battlemidget))
- Fix lxc query defaults [\#1389](https://github.com/conjure-up/conjure-up/pull/1389) ([battlemidget](https://github.com/battlemidget))
- Allow reading from a Conjurefile [\#1388](https://github.com/conjure-up/conjure-up/pull/1388) ([battlemidget](https://github.com/battlemidget))
- Create metadata model [\#1383](https://github.com/conjure-up/conjure-up/pull/1383) ([battlemidget](https://github.com/battlemidget))
- Use namespace ghost spell for testing [\#1381](https://github.com/conjure-up/conjure-up/pull/1381) ([battlemidget](https://github.com/battlemidget))
- Handle Juju returning null from list-clouds [\#1380](https://github.com/conjure-up/conjure-up/pull/1380) ([johnsca](https://github.com/johnsca))
- Handle errors loading README [\#1376](https://github.com/conjure-up/conjure-up/pull/1376) ([johnsca](https://github.com/johnsca))
- Fix configapps.gui test broken by merge conflict [\#1375](https://github.com/conjure-up/conjure-up/pull/1375) ([johnsca](https://github.com/johnsca))
- Feature/juju deploy native [\#1373](https://github.com/conjure-up/conjure-up/pull/1373) ([battlemidget](https://github.com/battlemidget))
- add docstrings, simple validator for constraints [\#1372](https://github.com/conjure-up/conjure-up/pull/1372) ([battlemidget](https://github.com/battlemidget))
- Support constraints input in configure [\#1371](https://github.com/conjure-up/conjure-up/pull/1371) ([battlemidget](https://github.com/battlemidget))
- Fix accessing advanced options [\#1370](https://github.com/conjure-up/conjure-up/pull/1370) ([battlemidget](https://github.com/battlemidget))
- Add before-config step phase [\#1368](https://github.com/conjure-up/conjure-up/pull/1368) ([johnsca](https://github.com/johnsca))
- Remove architect code \o/ [\#1367](https://github.com/conjure-up/conjure-up/pull/1367) ([battlemidget](https://github.com/battlemidget))
- Apply same fix to diskval that was applied to memval [\#1366](https://github.com/conjure-up/conjure-up/pull/1366) ([johnsca](https://github.com/johnsca))
- Explicitly ignore errors posting telemetry [\#1362](https://github.com/conjure-up/conjure-up/pull/1362) ([johnsca](https://github.com/johnsca))
- Clean up application list view [\#1361](https://github.com/conjure-up/conjure-up/pull/1361) ([battlemidget](https://github.com/battlemidget))
- Switch to libjuju's FileJujuData for loading credentials [\#1357](https://github.com/conjure-up/conjure-up/pull/1357) ([johnsca](https://github.com/johnsca))
- Fix placement sometimes not being populated [\#1353](https://github.com/conjure-up/conjure-up/pull/1353) ([johnsca](https://github.com/johnsca))
- Put charmstore in app\_config, update application configure view [\#1349](https://github.com/conjure-up/conjure-up/pull/1349) ([battlemidget](https://github.com/battlemidget))
- Add bundle-fragment container [\#1348](https://github.com/conjure-up/conjure-up/pull/1348) ([battlemidget](https://github.com/battlemidget))
- Fix JAAS controller selection when token auth succeeds [\#1344](https://github.com/conjure-up/conjure-up/pull/1344) ([johnsca](https://github.com/johnsca))

## [2.5.5](https://github.com/conjure-up/conjure-up/tree/2.5.5) (2018-02-26)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.4...2.5.5)

## [2.5.4](https://github.com/conjure-up/conjure-up/tree/2.5.4) (2018-02-25)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.3...2.5.4)

**Fixed bugs:**

- Error Installing Kubernetes on AWS using Conjure-up [\#1311](https://github.com/conjure-up/conjure-up/issues/1311)

**Closed issues:**

- Handle type mismatches between input field and default values better [\#1339](https://github.com/conjure-up/conjure-up/issues/1339)
- Unable to bootstrap \(cloud type:localhost\) [\#1328](https://github.com/conjure-up/conjure-up/issues/1328)

**Merged pull requests:**

- Deploy from a bundle file [\#1347](https://github.com/conjure-up/conjure-up/pull/1347) ([battlemidget](https://github.com/battlemidget))
- Check type of default value for step fields [\#1342](https://github.com/conjure-up/conjure-up/pull/1342) ([johnsca](https://github.com/johnsca))
- Pass session ID to steps [\#1340](https://github.com/conjure-up/conjure-up/pull/1340) ([johnsca](https://github.com/johnsca))
- Deploy from a bundle file [\#1337](https://github.com/conjure-up/conjure-up/pull/1337) ([battlemidget](https://github.com/battlemidget))
- Remove some dependencies on Juju CLI now that libjuju supports macaroon auth [\#1334](https://github.com/conjure-up/conjure-up/pull/1334) ([johnsca](https://github.com/johnsca))
- Retry juju-status + login after creating model [\#1330](https://github.com/conjure-up/conjure-up/pull/1330) ([johnsca](https://github.com/johnsca))

## [2.5.3](https://github.com/conjure-up/conjure-up/tree/2.5.3) (2018-02-08)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.2...2.5.3)

**Fixed bugs:**

- AttributeError: 'Text' object has no attribute 'enabled' [\#1324](https://github.com/conjure-up/conjure-up/issues/1324)
- conjure-down fails with `LookupError: Unable to list controllers: /bin/sh: 1: None: not found` [\#1269](https://github.com/conjure-up/conjure-up/issues/1269)

**Closed issues:**

- Architect option throws operand error [\#1309](https://github.com/conjure-up/conjure-up/issues/1309)
- Update Juju to 2.3.2 [\#1307](https://github.com/conjure-up/conjure-up/issues/1307)
- OpenStack Installer fails on Ubuntu 16.04.3 LTS with WORKLOAD\_ERROR\_STATES,  IndexError: list index out of range [\#1306](https://github.com/conjure-up/conjure-up/issues/1306)
- Unable to read add-on selection screen on small windows [\#1305](https://github.com/conjure-up/conjure-up/issues/1305)
- confirm quit [\#1291](https://github.com/conjure-up/conjure-up/issues/1291)
- Master hangout -  \(update-status\) Waiting for kube-system pods to start [\#1247](https://github.com/conjure-up/conjure-up/issues/1247)
- base class for keyboard navigation [\#1226](https://github.com/conjure-up/conjure-up/issues/1226)

**Merged pull requests:**

- Update juju-wait to get fix for IndexError [\#1327](https://github.com/conjure-up/conjure-up/pull/1327) ([johnsca](https://github.com/johnsca))
- Fix 'NoneType' has no attr 'value' [\#1326](https://github.com/conjure-up/conjure-up/pull/1326) ([johnsca](https://github.com/johnsca))
- Fix 'has no attribute enabled' error on cloud selection [\#1325](https://github.com/conjure-up/conjure-up/pull/1325) ([johnsca](https://github.com/johnsca))
- Convert Deploy Status screen to BaseView to enable scrolling [\#1318](https://github.com/conjure-up/conjure-up/pull/1318) ([johnsca](https://github.com/johnsca))
- Fix a few issues with enhanced keyboard navigation [\#1316](https://github.com/conjure-up/conjure-up/pull/1316) ([johnsca](https://github.com/johnsca))
- Bug/1309 operand error [\#1314](https://github.com/conjure-up/conjure-up/pull/1314) ([battlemidget](https://github.com/battlemidget))
- Bug/1269 fix bin path [\#1313](https://github.com/conjure-up/conjure-up/pull/1313) ([battlemidget](https://github.com/battlemidget))
- Fixes \#1307 [\#1312](https://github.com/conjure-up/conjure-up/pull/1312) ([battlemidget](https://github.com/battlemidget))
- Make it explicit that JaaS is free [\#1310](https://github.com/conjure-up/conjure-up/pull/1310) ([johnsca](https://github.com/johnsca))
- Prompt to confirm before quit [\#1304](https://github.com/conjure-up/conjure-up/pull/1304) ([johnsca](https://github.com/johnsca))
- Add indicator for help and page up/down support [\#1302](https://github.com/conjure-up/conjure-up/pull/1302) ([johnsca](https://github.com/johnsca))
- Make keyboard navigation consistent [\#1290](https://github.com/conjure-up/conjure-up/pull/1290) ([johnsca](https://github.com/johnsca))

## [2.5.2](https://github.com/conjure-up/conjure-up/tree/2.5.2) (2018-01-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.1...2.5.2)

**Fixed bugs:**

- addon steps dont seem to be executing [\#1295](https://github.com/conjure-up/conjure-up/issues/1295)

**Closed issues:**

- Information on the final screen is gone once you quit [\#1294](https://github.com/conjure-up/conjure-up/issues/1294)
- Unable to do a clean install via conjure-up: ERROR "Could not determine Juju version." [\#1289](https://github.com/conjure-up/conjure-up/issues/1289)

**Merged pull requests:**

- Remove attribute duplicating property [\#1297](https://github.com/conjure-up/conjure-up/pull/1297) ([johnsca](https://github.com/johnsca))
- Fix addon steps not being run [\#1296](https://github.com/conjure-up/conjure-up/pull/1296) ([johnsca](https://github.com/johnsca))

## [2.5.1](https://github.com/conjure-up/conjure-up/tree/2.5.1) (2018-01-06)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.5.0...2.5.1)

**Fixed bugs:**

- Fix constraints not being parsed properly [\#1283](https://github.com/conjure-up/conjure-up/issues/1283)
- conjure-up cannot find storage or network bridge? [\#1279](https://github.com/conjure-up/conjure-up/issues/1279)
- Applications failed to start successfully reported but juju status shows all units ready [\#1218](https://github.com/conjure-up/conjure-up/issues/1218)
- OpenStack NovaLXD using old version of LXD inside the controller node [\#1194](https://github.com/conjure-up/conjure-up/issues/1194)
- lxd default profile inserts lxdbr0 as network device even if custom bridge selected [\#1159](https://github.com/conjure-up/conjure-up/issues/1159)
- too many machines  [\#1140](https://github.com/conjure-up/conjure-up/issues/1140)
- Error bootstrapping controller: \['ERROR unknown cloud "vsphere", please try "juju update-clouds"'\] [\#1097](https://github.com/conjure-up/conjure-up/issues/1097)

**Closed issues:**

- Spell data for aliases not synced properly [\#1280](https://github.com/conjure-up/conjure-up/issues/1280)
- Openstack Autopilot with Landscape [\#1266](https://github.com/conjure-up/conjure-up/issues/1266)
- The 'conjure-up==2.4a1' distribution was not found and is required by the application [\#1210](https://github.com/conjure-up/conjure-up/issues/1210)

**Merged pull requests:**

- Update default lxd profile with selected network bridge [\#1288](https://github.com/conjure-up/conjure-up/pull/1288) ([battlemidget](https://github.com/battlemidget))
- Remove placement restrictions on localhost [\#1285](https://github.com/conjure-up/conjure-up/pull/1285) ([battlemidget](https://github.com/battlemidget))
- Fix constraints parsing [\#1284](https://github.com/conjure-up/conjure-up/pull/1284) ([battlemidget](https://github.com/battlemidget))
- Update maintainers for a simplified release process [\#1282](https://github.com/conjure-up/conjure-up/pull/1282) ([battlemidget](https://github.com/battlemidget))
- Fix \#1280: Spell not synced for aliases [\#1281](https://github.com/conjure-up/conjure-up/pull/1281) ([johnsca](https://github.com/johnsca))
- Pass along the constraint to juju and let it handle the conversions [\#1278](https://github.com/conjure-up/conjure-up/pull/1278) ([battlemidget](https://github.com/battlemidget))

## [2.5.0](https://github.com/conjure-up/conjure-up/tree/2.5.0) (2017-12-19)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.4.2...2.5.0)

**Fixed bugs:**

- Application constraints are ignored [\#1272](https://github.com/conjure-up/conjure-up/issues/1272)
- bundle-add fragment hides remainder of applications [\#1270](https://github.com/conjure-up/conjure-up/issues/1270)
- Deploy getting stuck on setting relations [\#1264](https://github.com/conjure-up/conjure-up/issues/1264)
- boolean step type failure \(expected str, bytes or os.PathLike object, not bool\) [\#1261](https://github.com/conjure-up/conjure-up/issues/1261)
- boolean step type failure \(no attribute 'required'\) [\#1255](https://github.com/conjure-up/conjure-up/issues/1255)
- conjure-up tells me the wrong log location when i specify --cache-dir [\#1254](https://github.com/conjure-up/conjure-up/issues/1254)

**Merged pull requests:**

- Fix placement spec not being honored [\#1277](https://github.com/conjure-up/conjure-up/pull/1277) ([battlemidget](https://github.com/battlemidget))
- Copy app constraints to conjure-up created machines [\#1276](https://github.com/conjure-up/conjure-up/pull/1276) ([johnsca](https://github.com/johnsca))
- Update libjuju to 0.7.0 [\#1273](https://github.com/conjure-up/conjure-up/pull/1273) ([battlemidget](https://github.com/battlemidget))
- Normalize bundle top level keys for application/services [\#1271](https://github.com/conjure-up/conjure-up/pull/1271) ([battlemidget](https://github.com/battlemidget))
- Add's libsodium for libjuju updates [\#1268](https://github.com/conjure-up/conjure-up/pull/1268) ([battlemidget](https://github.com/battlemidget))
- Add test branch for libjuju relation updates [\#1267](https://github.com/conjure-up/conjure-up/pull/1267) ([battlemidget](https://github.com/battlemidget))
- \[debug\] Add additional debug logging for \#1264 [\#1265](https://github.com/conjure-up/conjure-up/pull/1265) ([johnsca](https://github.com/johnsca))
- Ensure step field values are always strings [\#1262](https://github.com/conjure-up/conjure-up/pull/1262) ([johnsca](https://github.com/johnsca))
- skip field input validate if boolean [\#1259](https://github.com/conjure-up/conjure-up/pull/1259) ([battlemidget](https://github.com/battlemidget))
- Add required attribute to step model [\#1258](https://github.com/conjure-up/conjure-up/pull/1258) ([battlemidget](https://github.com/battlemidget))
- Use proper cache directory in error view [\#1256](https://github.com/conjure-up/conjure-up/pull/1256) ([battlemidget](https://github.com/battlemidget))

## [2.4.2](https://github.com/conjure-up/conjure-up/tree/2.4.2) (2017-11-30)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.4.1...2.4.2)

**Implemented enhancements:**

- direct user to run `lxd init` and walk through the guided setup process [\#1252](https://github.com/conjure-up/conjure-up/issues/1252)
- Show disabled clouds, with indication as to why they're disabled [\#1222](https://github.com/conjure-up/conjure-up/issues/1222)

**Fixed bugs:**

- conjure-up was never notified regarding ec2 API error [\#1249](https://github.com/conjure-up/conjure-up/issues/1249)
- AttributeError: 'KV' object has no attribute 'set' [\#1243](https://github.com/conjure-up/conjure-up/issues/1243)
- Headless conjure up failed at juju\_wait [\#1242](https://github.com/conjure-up/conjure-up/issues/1242)
- add pwgen as a dep in conjure-up brew formula [\#1215](https://github.com/conjure-up/conjure-up/issues/1215)

**Closed issues:**

- add hook between bundle deploy and built-in juju-wait [\#1238](https://github.com/conjure-up/conjure-up/issues/1238)
- Unable to bootstrap Openstack NovaKVM [\#1237](https://github.com/conjure-up/conjure-up/issues/1237)

**Merged pull requests:**

- Update lxd init message to remove auto setup [\#1253](https://github.com/conjure-up/conjure-up/pull/1253) ([battlemidget](https://github.com/battlemidget))
- bump ubuntui version to support defaults in boolean widgets [\#1251](https://github.com/conjure-up/conjure-up/pull/1251) ([battlemidget](https://github.com/battlemidget))
- Better handling of determining which juju/juju-wait binaries to use [\#1246](https://github.com/conjure-up/conjure-up/pull/1246) ([battlemidget](https://github.com/battlemidget))
- Fix AttributeError when saving state [\#1244](https://github.com/conjure-up/conjure-up/pull/1244) ([johnsca](https://github.com/johnsca))
- Add spell hook for before-wait [\#1239](https://github.com/conjure-up/conjure-up/pull/1239) ([johnsca](https://github.com/johnsca))
- Show disabled clouds and why they're disabled [\#1235](https://github.com/conjure-up/conjure-up/pull/1235) ([johnsca](https://github.com/johnsca))

## [2.4.1](https://github.com/conjure-up/conjure-up/tree/2.4.1) (2017-11-17)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.4.0...2.4.1)

**Fixed bugs:**

- AttributeError: 'NoneType' object has no attribute 'strip' when looking for lxd server version [\#1229](https://github.com/conjure-up/conjure-up/issues/1229)

**Closed issues:**

- Replace charmhelpers with kv [\#1231](https://github.com/conjure-up/conjure-up/issues/1231)
- attributeerror nonetype object has no attribute 'splitlines' [\#1223](https://github.com/conjure-up/conjure-up/issues/1223)
- Bootstrap, deploy-wait, and step log files empty in snap [\#1220](https://github.com/conjure-up/conjure-up/issues/1220)
- Error on post-deploy of kubernete add-ons deis workflow!​ [\#1214](https://github.com/conjure-up/conjure-up/issues/1214)

**Merged pull requests:**

- Replace charmhelpers with kv [\#1234](https://github.com/conjure-up/conjure-up/pull/1234) ([johnsca](https://github.com/johnsca))
- Be more explicit in what path to use for LXD/LXC error messages [\#1233](https://github.com/conjure-up/conjure-up/pull/1233) ([battlemidget](https://github.com/battlemidget))
- Fix NoneType has no attribute splitlines [\#1227](https://github.com/conjure-up/conjure-up/pull/1227) ([johnsca](https://github.com/johnsca))
- Fix detail log files not being written to [\#1221](https://github.com/conjure-up/conjure-up/pull/1221) ([johnsca](https://github.com/johnsca))
- Differentiate DeploymentFailure error [\#1217](https://github.com/conjure-up/conjure-up/pull/1217) ([johnsca](https://github.com/johnsca))

## [2.4.0](https://github.com/conjure-up/conjure-up/tree/2.4.0) (2017-11-02)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.3.1...2.4.0)

**Implemented enhancements:**

- support selection input type in steps [\#1167](https://github.com/conjure-up/conjure-up/issues/1167)
- expand steps to allow bundle modification [\#1156](https://github.com/conjure-up/conjure-up/issues/1156)

**Fixed bugs:**

- Conjure-up cannot detect the local installed lxd [\#1200](https://github.com/conjure-up/conjure-up/issues/1200)
- lxd not found \(Ubuntu 16.04 vm\) [\#1190](https://github.com/conjure-up/conjure-up/issues/1190)
- doesn't detect LXD even with snap lxd 2.18 installed [\#1187](https://github.com/conjure-up/conjure-up/issues/1187)
- AWS file not found [\#1184](https://github.com/conjure-up/conjure-up/issues/1184)
- AddressValueError: Expected 4 octets in 'None' [\#1152](https://github.com/conjure-up/conjure-up/issues/1152)

**Closed issues:**

- Failed AWS Integration [\#1197](https://github.com/conjure-up/conjure-up/issues/1197)
- design doc: placement and application configure [\#1193](https://github.com/conjure-up/conjure-up/issues/1193)
- Selecting BACK from Add-ons if spell given on CLI breaks [\#1180](https://github.com/conjure-up/conjure-up/issues/1180)
- Mouse clicking CONTINUE on add-ons goes BACK [\#1179](https://github.com/conjure-up/conjure-up/issues/1179)
- TypeError: 'dict\_values' object does not support indexing [\#1176](https://github.com/conjure-up/conjure-up/issues/1176)
- Add ability to add new OpenStack cloud via conjure-up [\#1171](https://github.com/conjure-up/conjure-up/issues/1171)
- openstack installation using conjure-up issue [\#1169](https://github.com/conjure-up/conjure-up/issues/1169)
- juju.py bootstrap fn uses incorrect parameter --model-default instead of --model-defaults [\#1164](https://github.com/conjure-up/conjure-up/issues/1164)
- lxd didnt store correct allocation pool [\#1162](https://github.com/conjure-up/conjure-up/issues/1162)
- install kubernetes , no localhost to select [\#1161](https://github.com/conjure-up/conjure-up/issues/1161)
- Error running conjure-up \(openstack novalxd\) on a clean install of Ubuntu Server 17.04 [\#1160](https://github.com/conjure-up/conjure-up/issues/1160)
- document what tests are being run [\#1157](https://github.com/conjure-up/conjure-up/issues/1157)

**Merged pull requests:**

- Fix issue where non localhost headless clouds werent calling finish [\#1211](https://github.com/conjure-up/conjure-up/pull/1211) ([battlemidget](https://github.com/battlemidget))
- Add logging and retries back to deploy wait [\#1209](https://github.com/conjure-up/conjure-up/pull/1209) ([johnsca](https://github.com/johnsca))
- Address some of the lxd issues [\#1205](https://github.com/conjure-up/conjure-up/pull/1205) ([battlemidget](https://github.com/battlemidget))
- Handle unknown ipaddress in lxd setup [\#1203](https://github.com/conjure-up/conjure-up/pull/1203) ([battlemidget](https://github.com/battlemidget))
- Disable BACK when spell specified on CLI [\#1186](https://github.com/conjure-up/conjure-up/pull/1186) ([johnsca](https://github.com/johnsca))
- Disable mouse clicks [\#1185](https://github.com/conjure-up/conjure-up/pull/1185) ([battlemidget](https://github.com/battlemidget))
- Re-add openstack as a provider option [\#1183](https://github.com/conjure-up/conjure-up/pull/1183) ([battlemidget](https://github.com/battlemidget))
- Add support for bundle overrides from CLI for testing [\#1181](https://github.com/conjure-up/conjure-up/pull/1181) ([johnsca](https://github.com/johnsca))
- Fixes for vSphere network / datastore selection [\#1178](https://github.com/conjure-up/conjure-up/pull/1178) ([johnsca](https://github.com/johnsca))
- Fix "dict\_values object does not support indexing" [\#1177](https://github.com/conjure-up/conjure-up/pull/1177) ([johnsca](https://github.com/johnsca))
- Add after-input phase with bundle modification [\#1172](https://github.com/conjure-up/conjure-up/pull/1172) ([johnsca](https://github.com/johnsca))
- Add support for choices in steps [\#1168](https://github.com/conjure-up/conjure-up/pull/1168) ([battlemidget](https://github.com/battlemidget))
- expand steps to process phases [\#1166](https://github.com/conjure-up/conjure-up/pull/1166) ([battlemidget](https://github.com/battlemidget))
- Move deploy-done script into conjure-up [\#1165](https://github.com/conjure-up/conjure-up/pull/1165) ([battlemidget](https://github.com/battlemidget))
- Correct localhost dhcp ranges [\#1163](https://github.com/conjure-up/conjure-up/pull/1163) ([battlemidget](https://github.com/battlemidget))
- Add testing overview doc [\#1158](https://github.com/conjure-up/conjure-up/pull/1158) ([battlemidget](https://github.com/battlemidget))

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
- document extending sudo timeout [\#1104](https://github.com/conjure-up/conjure-up/issues/1104)
- remove status icon in steps view and keep only in runsteps [\#1102](https://github.com/conjure-up/conjure-up/issues/1102)
- Error on macOS trying to deploy using local controller with MAAS [\#1083](https://github.com/conjure-up/conjure-up/issues/1083)

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

**Fixed bugs:**

- lxdbr0 set as default for localhost cloud [\#921](https://github.com/conjure-up/conjure-up/issues/921)
- credentials being populated incorrectly [\#907](https://github.com/conjure-up/conjure-up/issues/907)
- unexpected keyword argument 'agent-version' [\#903](https://github.com/conjure-up/conjure-up/issues/903)

**Closed issues:**

- Invalid signature when conjure-up juju [\#914](https://github.com/conjure-up/conjure-up/issues/914)

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

## [2.2.0-beta4](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta4) (2017-05-11)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta3...2.2.0-beta4)

## [2.2.0-beta3](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta3) (2017-05-09)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.5...2.2.0-beta3)

## [2.1.5](https://github.com/conjure-up/conjure-up/tree/2.1.5) (2017-04-15)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.4...2.1.5)

## [2.1.4](https://github.com/conjure-up/conjure-up/tree/2.1.4) (2017-04-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.3...2.1.4)

## [2.1.3](https://github.com/conjure-up/conjure-up/tree/2.1.3) (2017-04-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta2...2.1.3)

## [2.2.0-beta2](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta2) (2017-03-30)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta1...2.2.0-beta2)

## [2.2.0-beta1](https://github.com/conjure-up/conjure-up/tree/2.2.0-beta1) (2017-03-23)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.2...2.2.0-beta1)

## [2.1.2](https://github.com/conjure-up/conjure-up/tree/2.1.2) (2017-03-10)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.1...2.1.2)

## [2.1.1](https://github.com/conjure-up/conjure-up/tree/2.1.1) (2017-03-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0...2.1.1)

## [2.1.0](https://github.com/conjure-up/conjure-up/tree/2.1.0) (2017-02-22)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-rc1...2.1.0)

## [2.1.0-rc1](https://github.com/conjure-up/conjure-up/tree/2.1.0-rc1) (2017-02-10)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-beta5...2.1.0-rc1)

## [2.1.0-beta5](https://github.com/conjure-up/conjure-up/tree/2.1.0-beta5) (2017-02-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0-pre-snappy...2.1.0-beta5)

## [2.1.0-pre-snappy](https://github.com/conjure-up/conjure-up/tree/2.1.0-pre-snappy) (2017-01-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.2...2.1.0-pre-snappy)

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
