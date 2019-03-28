# Change Log

## [2.6.7](https://github.com/conjure-up/conjure-up/tree/2.6.7) (2019-03-28)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.6...2.6.7)

**Closed issues:**

- ValueError: not enough values to unpack \(expected 4, got 3\) [\#1591](https://github.com/conjure-up/conjure-up/issues/1591)
- Imrpove docs and message: !! This should \_not\_ be run as root or with sudo. !! [\#1589](https://github.com/conjure-up/conjure-up/issues/1589)
- Error bootstrapping controller: \['ERROR Get https://10.218.116.1:8443/1.0: Service Unavailable'\] [\#1570](https://github.com/conjure-up/conjure-up/issues/1570)
- deploy error with conjure-up kubernetes [\#1537](https://github.com/conjure-up/conjure-up/issues/1537)

## [2.6.6](https://github.com/conjure-up/conjure-up/tree/2.6.6) (2019-02-04)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.5...2.6.6)

**Merged pull requests:**

- Fix unable to select new controller [\#1581](https://github.com/conjure-up/conjure-up/pull/1581) ([johnsca](https://github.com/johnsca))

## [2.6.5](https://github.com/conjure-up/conjure-up/tree/2.6.5) (2019-01-31)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.4...2.6.5)

**Closed issues:**

- conjure-up Unable to bootstrap \(cloud type: maas\) [\#1567](https://github.com/conjure-up/conjure-up/issues/1567)
- kubernetes-core bootstrap \(localhost\) hangs on "Waiting for deployment to settle." [\#1565](https://github.com/conjure-up/conjure-up/issues/1565)
- Waiting for 5 kube-system pods to start [\#1562](https://github.com/conjure-up/conjure-up/issues/1562)
- subordinate application must be deployed without units [\#1561](https://github.com/conjure-up/conjure-up/issues/1561)
- Re-deploy failed after cancel a deploy task [\#1515](https://github.com/conjure-up/conjure-up/issues/1515)

**Merged pull requests:**

- Fix value of controller widget [\#1579](https://github.com/conjure-up/conjure-up/pull/1579) ([johnsca](https://github.com/johnsca))
- Update snapcraft.yaml to use new Juju deps mechanism [\#1578](https://github.com/conjure-up/conjure-up/pull/1578) ([johnsca](https://github.com/johnsca))
- bump libjuju \(needed for 2.5\) [\#1577](https://github.com/conjure-up/conjure-up/pull/1577) ([kwmonroe](https://github.com/kwmonroe))
- Disable controllers which have no endpoints [\#1575](https://github.com/conjure-up/conjure-up/pull/1575) ([johnsca](https://github.com/johnsca))

## [2.6.4](https://github.com/conjure-up/conjure-up/tree/2.6.4) (2018-12-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.3...2.6.4)

**Fixed bugs:**

- Failure to bootstrap Juju [\#1556](https://github.com/conjure-up/conjure-up/issues/1556)

**Merged pull requests:**

- Bump libjuju version to pick up subordinate fix [\#1560](https://github.com/conjure-up/conjure-up/pull/1560) ([johnsca](https://github.com/johnsca))

## [2.6.3](https://github.com/conjure-up/conjure-up/tree/2.6.3) (2018-12-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.2...2.6.3)

**Merged pull requests:**

- Fix KeyError if bootstrap-series not set [\#1558](https://github.com/conjure-up/conjure-up/pull/1558) ([johnsca](https://github.com/johnsca))

## [2.6.2](https://github.com/conjure-up/conjure-up/tree/2.6.2) (2018-12-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.1...2.6.2)

**Implemented enhancements:**

- Failure to bootstrap maas - apparent distribution mismatch - conjure-up sees xenial but system is bionic [\#1516](https://github.com/conjure-up/conjure-up/issues/1516)

**Fixed bugs:**

- conjure-up openstack with NovaLXD   fails on Ubuntu 18.04 LTS  ---\>  [\#1475](https://github.com/conjure-up/conjure-up/issues/1475)
- Doesn't support OpenStack Queens on Ubuntu 18.04 LTS [\#1428](https://github.com/conjure-up/conjure-up/issues/1428)
- Cannot deploy Openstack+LXD using localhost on 16.04 \(AWS\) [\#1418](https://github.com/conjure-up/conjure-up/issues/1418)

**Closed issues:**

- Not able to create an Image, Ubuntu 18.04 Juju OpenStack Config and Installation on LXD [\#1551](https://github.com/conjure-up/conjure-up/issues/1551)
-  exception: 'BundleApplicationFragment' object has no attribute 'fragment' [\#1549](https://github.com/conjure-up/conjure-up/issues/1549)
- Flannel hook failed: "install" [\#1546](https://github.com/conjure-up/conjure-up/issues/1546)
- Conjure-Up k8s core install fails on flannel setup with error: hook failed: "install" [\#1545](https://github.com/conjure-up/conjure-up/issues/1545)
- connection refused error [\#1542](https://github.com/conjure-up/conjure-up/issues/1542)
- can't deploy instance in conjure'd openstack-novalxd localhost [\#1540](https://github.com/conjure-up/conjure-up/issues/1540)
- conjure-up does not detect my manual cloud [\#1539](https://github.com/conjure-up/conjure-up/issues/1539)
- Openstack NovaKVM Dashboard cannot login with the given credential [\#1534](https://github.com/conjure-up/conjure-up/issues/1534)
- Reason: [\#1526](https://github.com/conjure-up/conjure-up/issues/1526)
- OpenStack-LXD on Ubuntu 18.04 Failure [\#1511](https://github.com/conjure-up/conjure-up/issues/1511)
- Can't Install OpenStack-LXD on Ubuntu 18.04 [\#1504](https://github.com/conjure-up/conjure-up/issues/1504)

**Merged pull requests:**

- Update libjuju and version + changelog [\#1557](https://github.com/conjure-up/conjure-up/pull/1557) ([johnsca](https://github.com/johnsca))
- Add bootstrap series override to Conjurefile [\#1555](https://github.com/conjure-up/conjure-up/pull/1555) ([johnsca](https://github.com/johnsca))
- Fix error handling for invalid bundles [\#1554](https://github.com/conjure-up/conjure-up/pull/1554) ([johnsca](https://github.com/johnsca))

## [2.6.1](https://github.com/conjure-up/conjure-up/tree/2.6.1) (2018-10-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.6.0...2.6.1)

**Fixed bugs:**

- Conjure up fails with Exception: Could not determine Juju version [\#1514](https://github.com/conjure-up/conjure-up/issues/1514)

**Closed issues:**

- Unhandled exception in \<Task finished coro=\<DeployController.\_wait\_for\_applications\(\) done [\#1509](https://github.com/conjure-up/conjure-up/issues/1509)
- ipv6 [\#1506](https://github.com/conjure-up/conjure-up/issues/1506)
- conjure-up kubernetes-core hangs on master Waiting for kube-system pods to start [\#1499](https://github.com/conjure-up/conjure-up/issues/1499)
- LocalhostJSONError: Unable to parse JSON output from LXD, does `/snap/bin/lxc query --wait -X GET /1.0` return info a... [\#1451](https://github.com/conjure-up/conjure-up/issues/1451)

**Merged pull requests:**

- Use dict literal [\#1520](https://github.com/conjure-up/conjure-up/pull/1520) ([sieben](https://github.com/sieben))
- Use list literal [\#1519](https://github.com/conjure-up/conjure-up/pull/1519) ([sieben](https://github.com/sieben))
- Replace use of a deprecated attributes [\#1518](https://github.com/conjure-up/conjure-up/pull/1518) ([sieben](https://github.com/sieben))
- Update libjuju 0.10.2 [\#1512](https://github.com/conjure-up/conjure-up/pull/1512) ([johnsca](https://github.com/johnsca))
- Bump Juju 2.4.1 [\#1502](https://github.com/conjure-up/conjure-up/pull/1502) ([battlemidget](https://github.com/battlemidget))

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

**Fixed bugs:**

- Error setting up microk8s on Azure [\#1478](https://github.com/conjure-up/conjure-up/issues/1478)

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

**Closed issues:**

- Spell data for aliases not synced properly [\#1280](https://github.com/conjure-up/conjure-up/issues/1280)
- Openstack Autopilot with Landscape [\#1266](https://github.com/conjure-up/conjure-up/issues/1266)

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

**Fixed bugs:**

- conjure-up was never notified regarding ec2 API error [\#1249](https://github.com/conjure-up/conjure-up/issues/1249)
- AttributeError: 'KV' object has no attribute 'set' [\#1243](https://github.com/conjure-up/conjure-up/issues/1243)
- Headless conjure up failed at juju\_wait [\#1242](https://github.com/conjure-up/conjure-up/issues/1242)

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

**Merged pull requests:**

- Replace charmhelpers with kv [\#1234](https://github.com/conjure-up/conjure-up/pull/1234) ([johnsca](https://github.com/johnsca))
- Be more explicit in what path to use for LXD/LXC error messages [\#1233](https://github.com/conjure-up/conjure-up/pull/1233) ([battlemidget](https://github.com/battlemidget))

## [2.4.0](https://github.com/conjure-up/conjure-up/tree/2.4.0) (2017-11-02)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.3.1...2.4.0)

## [2.3.1](https://github.com/conjure-up/conjure-up/tree/2.3.1) (2017-09-19)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.3.0...2.3.1)

## [2.3.0](https://github.com/conjure-up/conjure-up/tree/2.3.0) (2017-09-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.2...2.3.0)

## [2.2.2](https://github.com/conjure-up/conjure-up/tree/2.2.2) (2017-06-23)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.1...2.2.2)

## [2.2.1](https://github.com/conjure-up/conjure-up/tree/2.2.1) (2017-06-20)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0...2.2.1)

## [2.2.0](https://github.com/conjure-up/conjure-up/tree/2.2.0) (2017-06-15)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta4...2.2.0)

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