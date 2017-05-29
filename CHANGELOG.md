# Change Log

## [Unreleased](https://github.com/conjure-up/conjure-up/tree/HEAD)

[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0...HEAD)

**Implemented enhancements:**

- allow user to select a model on a controller to deploy to [\#753](https://github.com/conjure-up/conjure-up/issues/753)
- look into dealing with existing credentials [\#545](https://github.com/conjure-up/conjure-up/issues/545)

**Closed issues:**

- conjure-up continue operations [\#624](https://github.com/conjure-up/conjure-up/issues/624)

**Merged pull requests:**

- WIP: First crack at asyncio tailing of step output [\#898](https://github.com/conjure-up/conjure-up/pull/898) ([battlemidget](https://github.com/battlemidget))

## [2.2.0](https://github.com/conjure-up/conjure-up/tree/2.2.0) (2017-05-25)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta4...2.2.0)

**Implemented enhancements:**

- FYI "juju login -B" is the new "juju register"... [\#891](https://github.com/conjure-up/conjure-up/issues/891)
- make sure region selection is always visible [\#883](https://github.com/conjure-up/conjure-up/issues/883)
- region selection for jaas deployment [\#882](https://github.com/conjure-up/conjure-up/issues/882)
- add prebootstrap process hook [\#863](https://github.com/conjure-up/conjure-up/issues/863)
- embed lxd [\#850](https://github.com/conjure-up/conjure-up/issues/850)
- enable oracle provider [\#833](https://github.com/conjure-up/conjure-up/issues/833)
- \[ARM64\] Need conjure-up snap in snap store [\#828](https://github.com/conjure-up/conjure-up/issues/828)
- bootstrap exception capture cloud type [\#789](https://github.com/conjure-up/conjure-up/issues/789)
- bundlewriter should place generated bundles inside their cached spell dir [\#787](https://github.com/conjure-up/conjure-up/issues/787)
- Add sudo support for spells [\#758](https://github.com/conjure-up/conjure-up/issues/758)
- support bootstrap to a region for public cloud in gui mode [\#715](https://github.com/conjure-up/conjure-up/issues/715)
- support conjure-up on vmware/vsphere [\#709](https://github.com/conjure-up/conjure-up/issues/709)
- Support juju login for JAAS support [\#708](https://github.com/conjure-up/conjure-up/issues/708)
- migrate to libjuju [\#697](https://github.com/conjure-up/conjure-up/issues/697)
- better error feedback on user input screens [\#686](https://github.com/conjure-up/conjure-up/issues/686)
- export bundle after mutations [\#621](https://github.com/conjure-up/conjure-up/issues/621)
- Add support for channels [\#556](https://github.com/conjure-up/conjure-up/issues/556)
- \[release-process\] gate bundles on successful conjure-up deploy [\#555](https://github.com/conjure-up/conjure-up/issues/555)
- Support OSX [\#549](https://github.com/conjure-up/conjure-up/issues/549)

**Fixed bugs:**

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

- Installing OpenStack from Landscape not working [\#893](https://github.com/conjure-up/conjure-up/issues/893)
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

**Implemented enhancements:**

- Provide better feedback if shutdown process takes some time [\#835](https://github.com/conjure-up/conjure-up/issues/835)

**Fixed bugs:**

- conjure-up from edge r154 nonetype exception deploying landscape on maas [\#773](https://github.com/conjure-up/conjure-up/issues/773)
- Juju Bootstrap to MAAS should not do --debug [\#742](https://github.com/conjure-up/conjure-up/issues/742)
- Continues forever but doesn't do anything. [\#729](https://github.com/conjure-up/conjure-up/issues/729)
- Openstack fails to correctly deploy when network device is not eth0 [\#728](https://github.com/conjure-up/conjure-up/issues/728)

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

**Fixed bugs:**

- Snap fails to install, with ERROR: '~ubuntu-lxc' user or team does not exist [\#818](https://github.com/conjure-up/conjure-up/issues/818)

**Closed issues:**

- Juju failed to bootstrap: maas [\#817](https://github.com/conjure-up/conjure-up/issues/817)

## [2.1.3](https://github.com/conjure-up/conjure-up/tree/2.1.3) (2017-04-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0-beta2...2.1.3)

**Implemented enhancements:**

- existing controllers filtered by type as well [\#771](https://github.com/conjure-up/conjure-up/issues/771)

**Fixed bugs:**

- The "install-dependencies" and "install" make targets don't work. [\#804](https://github.com/conjure-up/conjure-up/issues/804)
- headless maas deployments fail with 'services' error [\#757](https://github.com/conjure-up/conjure-up/issues/757)

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
- Improve handling of "cannot get user details" error during JAAS registration [\#745](https://github.com/conjure-up/conjure-up/issues/745)
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

**Implemented enhancements:**

- support bootstrap to a region for public cloud in headless mode [\#511](https://github.com/conjure-up/conjure-up/issues/511)

**Fixed bugs:**

- conjure-up shared libraries leaking out to system ldconfig [\#717](https://github.com/conjure-up/conjure-up/issues/717)
- Exception calling callback for \<Future at 0x7f4fd00db080 state=finished returned NoneType\> [\#712](https://github.com/conjure-up/conjure-up/issues/712)
- Setting lxd profile fails [\#695](https://github.com/conjure-up/conjure-up/issues/695)
- Error deploying to AWS when default region changed - conjure-up does not form correct bootstrap command when juju default aws region set [\#693](https://github.com/conjure-up/conjure-up/issues/693)
- Conjure up won't bootstrap a named LXD cloud on Zesty [\#576](https://github.com/conjure-up/conjure-up/issues/576)

**Closed issues:**

- Snap install conjure-up doesn't work if juju is installed [\#719](https://github.com/conjure-up/conjure-up/issues/719)
- conjure-up ssh connection fails to remote host [\#550](https://github.com/conjure-up/conjure-up/issues/550)
- document:  vsphere network configuration must be loosened to allow Promiscuous mode in the OpenStack management vlan [\#504](https://github.com/conjure-up/conjure-up/issues/504)

## [2.1.1](https://github.com/conjure-up/conjure-up/tree/2.1.1) (2017-03-03)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.1.0...2.1.1)

**Implemented enhancements:**

- make a decision on supporting root level modifications [\#507](https://github.com/conjure-up/conjure-up/issues/507)

**Fixed bugs:**

- failed to use 'lxd' for conjure-up [\#675](https://github.com/conjure-up/conjure-up/issues/675)
- Conjure-up bootstrapping not working on 16.04 [\#535](https://github.com/conjure-up/conjure-up/issues/535)
- openstack nova-lxd: all machined stuck in waiting state [\#526](https://github.com/conjure-up/conjure-up/issues/526)
- handle error if ipv6 is enabled and localhost was selected [\#495](https://github.com/conjure-up/conjure-up/issues/495)

**Closed issues:**

- "LookupError: Unable to list models: error: No controllers registered." [\#707](https://github.com/conjure-up/conjure-up/issues/707)
- snap won't install due to lxd-service failing to start [\#706](https://github.com/conjure-up/conjure-up/issues/706)
- Typo in Manual Docs [\#705](https://github.com/conjure-up/conjure-up/issues/705)
- Error deploying: cannot add application "ceph-osd": DB is locked | conjure-up setup [\#704](https://github.com/conjure-up/conjure-up/issues/704)
- Unable to install openstack with nova LXD on Ubuntu 16.04. Error stating IpV6 enabled even though disabled [\#703](https://github.com/conjure-up/conjure-up/issues/703)
- lxd openstack - is there a way to  have custom names or more related names for containers? [\#701](https://github.com/conjure-up/conjure-up/issues/701)
- more lxd polish necessary [\#538](https://github.com/conjure-up/conjure-up/issues/538)
- packaging: make sure openstack0 is removed [\#508](https://github.com/conjure-up/conjure-up/issues/508)
- die cleanly if github.com \(our registry\) is unavailable [\#500](https://github.com/conjure-up/conjure-up/issues/500)
- handle bootstrap error on non matching constraints [\#498](https://github.com/conjure-up/conjure-up/issues/498)
- make cancel/quit button show a dialog box giving option to kill model [\#65](https://github.com/conjure-up/conjure-up/issues/65)

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
- lxd setup hint to make sure to not set a subnet for ipv6 [\#534](https://github.com/conjure-up/conjure-up/issues/534)
- Support passing a template to LXD [\#505](https://github.com/conjure-up/conjure-up/issues/505)

**Fixed bugs:**

- Crash during the install of OpenStack with NovaLXD [\#673](https://github.com/conjure-up/conjure-up/issues/673)
- kubenetes core spell failed on localhost \(LXD\) [\#690](https://github.com/conjure-up/conjure-up/issues/690)
- Conjure Up failed on post-processing openstack-base [\#687](https://github.com/conjure-up/conjure-up/issues/687)
- snap: persists network/iptables configuration on reboot [\#685](https://github.com/conjure-up/conjure-up/issues/685)
- snap: fix network create on trusty [\#684](https://github.com/conjure-up/conjure-up/issues/684)
- Exception: Could not determine LXD version. [\#683](https://github.com/conjure-up/conjure-up/issues/683)
- headless conjure-up kubernetes-core fails, while GUI does work [\#676](https://github.com/conjure-up/conjure-up/issues/676)
- Failed to run pre deploy task: Expecting value: line 1 column 1  [\#674](https://github.com/conjure-up/conjure-up/issues/674)
- dont set perms on .cache dir if run as root [\#662](https://github.com/conjure-up/conjure-up/issues/662)
- zesty/yakkety snap conjure-up fails to load iptables rules [\#649](https://github.com/conjure-up/conjure-up/issues/649)
- conjure-up isn't properly handling a failed bootstrap [\#641](https://github.com/conjure-up/conjure-up/issues/641)
- conjure-up kubernetes crashes and doesn't run post steps but juju status looks good [\#623](https://github.com/conjure-up/conjure-up/issues/623)
- Better JSON errors during processing scripts results [\#563](https://github.com/conjure-up/conjure-up/issues/563)
- Conjure-up uses double the deployed hardware when deploying openstack-base and kubernetes-core [\#553](https://github.com/conjure-up/conjure-up/issues/553)
- Multiple conjure-up's fail to deploy because of unknown controller/cloud [\#544](https://github.com/conjure-up/conjure-up/issues/544)
- maas bootstrap errors if no existing bootstrap-config.yaml [\#539](https://github.com/conjure-up/conjure-up/issues/539)
- failing to reach google-analytics causes conjure-up to halt [\#516](https://github.com/conjure-up/conjure-up/issues/516)

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
- handle juju get\_models exception better [\#558](https://github.com/conjure-up/conjure-up/issues/558)
- add --debug to juju bootstrap if conjure-up is invoked with -d [\#536](https://github.com/conjure-up/conjure-up/issues/536)
- When using localhost/lxd, conjure-up should make sure lxd group is assigned to $USER [\#521](https://github.com/conjure-up/conjure-up/issues/521)
- Document setting locale for UTF8 [\#478](https://github.com/conjure-up/conjure-up/issues/478)
- prefix model names with conjure-up-randomname [\#463](https://github.com/conjure-up/conjure-up/issues/463)

**Merged pull requests:**

- Revert "Fixes \#615" [\#682](https://github.com/conjure-up/conjure-up/pull/682) ([battlemidget](https://github.com/battlemidget))
- Add HACKING.txt [\#681](https://github.com/conjure-up/conjure-up/pull/681) ([mikemccracken](https://github.com/mikemccracken))
- Warn on upgrading to snap lxd if deb lxd exists [\#678](https://github.com/conjure-up/conjure-up/pull/678) ([battlemidget](https://github.com/battlemidget))
- Fixes an issue on localhost deploying to nested lxd [\#677](https://github.com/conjure-up/conjure-up/pull/677) ([battlemidget](https://github.com/battlemidget))
- Snap a roo [\#559](https://github.com/conjure-up/conjure-up/pull/559) ([battlemidget](https://github.com/battlemidget))

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
- hitting \[deploy\] while bootstrap is pending freezes UI [\#541](https://github.com/conjure-up/conjure-up/issues/541)

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

**Implemented enhancements:**

- Please support deploying kubernetes-core [\#506](https://github.com/conjure-up/conjure-up/issues/506)

**Fixed bugs:**

- fails to pull down spells and fails without --notrack [\#554](https://github.com/conjure-up/conjure-up/issues/554)
- traceback during machine placement [\#540](https://github.com/conjure-up/conjure-up/issues/540)

**Closed issues:**

- deploying kubernetes-core onto LXD breaks due to nested LXDs [\#578](https://github.com/conjure-up/conjure-up/issues/578)
- misleading error when ipv6 is enabled in lxd [\#570](https://github.com/conjure-up/conjure-up/issues/570)
- Name of the kubernetes spell is wrong [\#546](https://github.com/conjure-up/conjure-up/issues/546)
- num\_units in config page persists even when 'back' is pressed instead of 'apply' [\#543](https://github.com/conjure-up/conjure-up/issues/543)
- placement: querying maas machines show empty list [\#528](https://github.com/conjure-up/conjure-up/issues/528)
- Conjure-up for hangs for a long time and eventually throws error [\#523](https://github.com/conjure-up/conjure-up/issues/523)
- error: flag provided but not defined: --upload-tools [\#518](https://github.com/conjure-up/conjure-up/issues/518)
- How to recover openstack install after reboot? [\#501](https://github.com/conjure-up/conjure-up/issues/501)
- openstack instances not getting ip's [\#494](https://github.com/conjure-up/conjure-up/issues/494)
- Console access and Object Store do not work [\#491](https://github.com/conjure-up/conjure-up/issues/491)

**Merged pull requests:**

- Left justify bootstrap wait output [\#580](https://github.com/conjure-up/conjure-up/pull/580) ([battlemidget](https://github.com/battlemidget))
- Ignore placement specs for LXD controllers [\#579](https://github.com/conjure-up/conjure-up/pull/579) ([mikemccracken](https://github.com/mikemccracken))
- Ensure that bundle placement directives are always used and shown in UI [\#564](https://github.com/conjure-up/conjure-up/pull/564) ([mikemccracken](https://github.com/mikemccracken))
- Snap sysctl increase [\#561](https://github.com/conjure-up/conjure-up/pull/561) ([battlemidget](https://github.com/battlemidget))
- fix use without access to google analytics [\#557](https://github.com/conjure-up/conjure-up/pull/557) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#540 [\#552](https://github.com/conjure-up/conjure-up/pull/552) ([mikemccracken](https://github.com/mikemccracken))
- Use a shadow copy for num\_units in options view [\#551](https://github.com/conjure-up/conjure-up/pull/551) ([mikemccracken](https://github.com/mikemccracken))
- Registry changes [\#548](https://github.com/conjure-up/conjure-up/pull/548) ([mikemccracken](https://github.com/mikemccracken))
- We dont use this any longer \(craft.py\) [\#542](https://github.com/conjure-up/conjure-up/pull/542) ([battlemidget](https://github.com/battlemidget))
- add maas fuzzy match for architecture constraint [\#533](https://github.com/conjure-up/conjure-up/pull/533) ([mikemccracken](https://github.com/mikemccracken))
- RFC: input colors and pin label [\#532](https://github.com/conjure-up/conjure-up/pull/532) ([battlemidget](https://github.com/battlemidget))
- Bump rev [\#531](https://github.com/conjure-up/conjure-up/pull/531) ([battlemidget](https://github.com/battlemidget))
- Fix 521 [\#530](https://github.com/conjure-up/conjure-up/pull/530) ([battlemidget](https://github.com/battlemidget))
- Fixes \#516 [\#529](https://github.com/conjure-up/conjure-up/pull/529) ([battlemidget](https://github.com/battlemidget))
- Improved ux for architecture view [\#527](https://github.com/conjure-up/conjure-up/pull/527) ([mikemccracken](https://github.com/mikemccracken))
- Just always cast constraints to string [\#525](https://github.com/conjure-up/conjure-up/pull/525) ([mikemccracken](https://github.com/mikemccracken))
- Deep copy machines dict [\#524](https://github.com/conjure-up/conjure-up/pull/524) ([mikemccracken](https://github.com/mikemccracken))
- Fix for new cloud creation [\#522](https://github.com/conjure-up/conjure-up/pull/522) ([mikemccracken](https://github.com/mikemccracken))
- add constraint editing to architecture screen [\#519](https://github.com/conjure-up/conjure-up/pull/519) ([mikemccracken](https://github.com/mikemccracken))
- remove vestigial old pollinate call [\#517](https://github.com/conjure-up/conjure-up/pull/517) ([mikemccracken](https://github.com/mikemccracken))
- get\_machines should return None when loading [\#515](https://github.com/conjure-up/conjure-up/pull/515) ([mikemccracken](https://github.com/mikemccracken))
- Bundle centric placement [\#514](https://github.com/conjure-up/conjure-up/pull/514) ([mikemccracken](https://github.com/mikemccracken))
- update bundleplacer for bug fix [\#513](https://github.com/conjure-up/conjure-up/pull/513) ([mikemccracken](https://github.com/mikemccracken))
- update bundleplacer [\#512](https://github.com/conjure-up/conjure-up/pull/512) ([mikemccracken](https://github.com/mikemccracken))
- fix tui code path when checking lxd [\#510](https://github.com/conjure-up/conjure-up/pull/510) ([battlemidget](https://github.com/battlemidget))
- Fix the snapcraft.yaml [\#509](https://github.com/conjure-up/conjure-up/pull/509) ([elopio](https://github.com/elopio))
- Use google analytics [\#503](https://github.com/conjure-up/conjure-up/pull/503) ([mikemccracken](https://github.com/mikemccracken))
- Return parsed apikey pieces [\#502](https://github.com/conjure-up/conjure-up/pull/502) ([mikemccracken](https://github.com/mikemccracken))
- Group additional input items [\#499](https://github.com/conjure-up/conjure-up/pull/499) ([battlemidget](https://github.com/battlemidget))
- Fix maas apiclient to work with MAASv2 api [\#496](https://github.com/conjure-up/conjure-up/pull/496) ([battlemidget](https://github.com/battlemidget))

## [2.0.2](https://github.com/conjure-up/conjure-up/tree/2.0.2) (2016-10-14)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1...2.0.2)

**Closed issues:**

- How many machines needed for OpenStack MAAS Getting Insufficient Peers [\#490](https://github.com/conjure-up/conjure-up/issues/490)
- nova-cloud-controller/0: hook failed [\#487](https://github.com/conjure-up/conjure-up/issues/487)
- conjure-up openstack fails deployment missing spell [\#484](https://github.com/conjure-up/conjure-up/issues/484)
- PPA Package not found when trying to install [\#483](https://github.com/conjure-up/conjure-up/issues/483)
- add walkthrough examples [\#193](https://github.com/conjure-up/conjure-up/issues/193)
- switch positional arguments for headless mode [\#493](https://github.com/conjure-up/conjure-up/issues/493)
- update juju bootstrap call to match cloud/controller name switch [\#492](https://github.com/conjure-up/conjure-up/issues/492)
- rabbitmq-server/0: hook failed [\#489](https://github.com/conjure-up/conjure-up/issues/489)
- fix checking lxd bridge on lxd 2.4+ [\#485](https://github.com/conjure-up/conjure-up/issues/485)

**Merged pull requests:**

- Fixes \#485 [\#486](https://github.com/conjure-up/conjure-up/pull/486) ([battlemidget](https://github.com/battlemidget))
- Add some extra options to grapher [\#482](https://github.com/conjure-up/conjure-up/pull/482) ([mikemccracken](https://github.com/mikemccracken))
- Add FLOAT type to option widget handling [\#488](https://github.com/conjure-up/conjure-up/pull/488) ([mikemccracken](https://github.com/mikemccracken))

## [2.0.1](https://github.com/conjure-up/conjure-up/tree/2.0.1) (2016-10-06)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1-beta2...2.0.1)

**Fixed bugs:**

- add support for running privileged commands [\#445](https://github.com/conjure-up/conjure-up/issues/445)
- traceback in TUI conjureing to maas [\#466](https://github.com/conjure-up/conjure-up/issues/466)
- blacklist not working for conjure-up canonical-kubernetes [\#464](https://github.com/conjure-up/conjure-up/issues/464)
- conjure-up package should depend on git-core [\#460](https://github.com/conjure-up/conjure-up/issues/460)

**Closed issues:**

- some applications wont display readme header in application list [\#458](https://github.com/conjure-up/conjure-up/issues/458)
- pull spells registry from a different git branch [\#454](https://github.com/conjure-up/conjure-up/issues/454)
- 'expose' key in bundle services dict is ignored [\#452](https://github.com/conjure-up/conjure-up/issues/452)
- headless mode: additional input environment variables not being set [\#451](https://github.com/conjure-up/conjure-up/issues/451)
- neutron-gateway/0: hook failed: "config-changed" [\#450](https://github.com/conjure-up/conjure-up/issues/450)
- hooklib should use correct model/controller [\#476](https://github.com/conjure-up/conjure-up/issues/476)
- print results in summary tui [\#474](https://github.com/conjure-up/conjure-up/issues/474)
- need a way to specify an existing controller on CLI [\#462](https://github.com/conjure-up/conjure-up/issues/462)
- newcloud maas sent me to the applications list screen [\#461](https://github.com/conjure-up/conjure-up/issues/461)
- do not allow button press on summary until all steps are complete [\#251](https://github.com/conjure-up/conjure-up/issues/251)
- unhelpful error handling when bootstrap fails in maas newcloud [\#223](https://github.com/conjure-up/conjure-up/issues/223)
- steps need basic interactive input validation [\#124](https://github.com/conjure-up/conjure-up/issues/124)

**Merged pull requests:**

- prep 2.0.1 release [\#481](https://github.com/conjure-up/conjure-up/pull/481) ([battlemidget](https://github.com/battlemidget))
- Fixes and error handling [\#479](https://github.com/conjure-up/conjure-up/pull/479) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#476 [\#477](https://github.com/conjure-up/conjure-up/pull/477) ([battlemidget](https://github.com/battlemidget))
- Fixes \#474 [\#475](https://github.com/conjure-up/conjure-up/pull/475) ([battlemidget](https://github.com/battlemidget))
- fix summary view button [\#473](https://github.com/conjure-up/conjure-up/pull/473) ([battlemidget](https://github.com/battlemidget))
- Fixes \#124 [\#472](https://github.com/conjure-up/conjure-up/pull/472) ([battlemidget](https://github.com/battlemidget))
- Show errors from bootstrap [\#471](https://github.com/conjure-up/conjure-up/pull/471) ([mikemccracken](https://github.com/mikemccracken))
- dont show result in footer [\#470](https://github.com/conjure-up/conjure-up/pull/470) ([battlemidget](https://github.com/battlemidget))
- Fixes \#466 [\#469](https://github.com/conjure-up/conjure-up/pull/469) ([battlemidget](https://github.com/battlemidget))
- Fixes \#464 [\#468](https://github.com/conjure-up/conjure-up/pull/468) ([battlemidget](https://github.com/battlemidget))
- Fix 462 [\#467](https://github.com/conjure-up/conjure-up/pull/467) ([mikemccracken](https://github.com/mikemccracken))
- fix new-cloud path [\#465](https://github.com/conjure-up/conjure-up/pull/465) ([mikemccracken](https://github.com/mikemccracken))
- Fix metadata lookup due to series being left unset. [\#459](https://github.com/conjure-up/conjure-up/pull/459) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#251 [\#457](https://github.com/conjure-up/conjure-up/pull/457) ([battlemidget](https://github.com/battlemidget))
- Fixes \#454 [\#456](https://github.com/conjure-up/conjure-up/pull/456) ([battlemidget](https://github.com/battlemidget))
- handle 'expose' keys separately in service dict [\#455](https://github.com/conjure-up/conjure-up/pull/455) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#451 [\#453](https://github.com/conjure-up/conjure-up/pull/453) ([battlemidget](https://github.com/battlemidget))
- tweak deploy message [\#449](https://github.com/conjure-up/conjure-up/pull/449) ([mikemccracken](https://github.com/mikemccracken))
- Series fixes [\#448](https://github.com/conjure-up/conjure-up/pull/448) ([mikemccracken](https://github.com/mikemccracken))
- Explicitly specify series in deploys [\#447](https://github.com/conjure-up/conjure-up/pull/447) ([mikemccracken](https://github.com/mikemccracken))
- fix bootstrap wait view when importing lxd images [\#480](https://github.com/conjure-up/conjure-up/pull/480) ([battlemidget](https://github.com/battlemidget))

## [2.0.1-beta2](https://github.com/conjure-up/conjure-up/tree/2.0.1-beta2) (2016-09-26)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.1-beta1...2.0.1-beta2)

**Fixed bugs:**

- conjure-up hangs with multiple 'Missing relation' [\#428](https://github.com/conjure-up/conjure-up/issues/428)
- non standard bridge juju failure [\#37](https://github.com/conjure-up/conjure-up/issues/37)

**Closed issues:**

- bad error for invalid path to spell [\#429](https://github.com/conjure-up/conjure-up/issues/429)
- app config screen match wireframe - fixed footer charm description [\#422](https://github.com/conjure-up/conjure-up/issues/422)
- no way to tell conjure-up where to bootstrap to [\#420](https://github.com/conjure-up/conjure-up/issues/420)
- can't edit unit count [\#418](https://github.com/conjure-up/conjure-up/issues/418)
- make conjure-up work on trusty [\#389](https://github.com/conjure-up/conjure-up/issues/389)
- support showing spell readme from the spellpicker view [\#340](https://github.com/conjure-up/conjure-up/issues/340)
- make model explicit when running juju-cli commands or API calls [\#295](https://github.com/conjure-up/conjure-up/issues/295)
- app config screen should allow showing all configs [\#241](https://github.com/conjure-up/conjure-up/issues/241)
- make -s a hidden environment variable for demos only [\#240](https://github.com/conjure-up/conjure-up/issues/240)
- display required environment variables in headless mode [\#215](https://github.com/conjure-up/conjure-up/issues/215)

**Merged pull requests:**

- Make spell readme available via 'r' in spellpicker [\#444](https://github.com/conjure-up/conjure-up/pull/444) ([mikemccracken](https://github.com/mikemccracken))
- Force default-model during bootstrap [\#443](https://github.com/conjure-up/conjure-up/pull/443) ([battlemidget](https://github.com/battlemidget))
- Fix bootstrap error in newcloud/gui [\#442](https://github.com/conjure-up/conjure-up/pull/442) ([battlemidget](https://github.com/battlemidget))
- Fixes \#295 [\#441](https://github.com/conjure-up/conjure-up/pull/441) ([battlemidget](https://github.com/battlemidget))
- Allow show/hide of non-whitelisted configs [\#440](https://github.com/conjure-up/conjure-up/pull/440) ([mikemccracken](https://github.com/mikemccracken))
- better error for directories that aren't spells. [\#439](https://github.com/conjure-up/conjure-up/pull/439) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#422 [\#438](https://github.com/conjure-up/conjure-up/pull/438) ([battlemidget](https://github.com/battlemidget))
- make logging output more consistent [\#437](https://github.com/conjure-up/conjure-up/pull/437) ([battlemidget](https://github.com/battlemidget))
- More compat changes for Trusty [\#435](https://github.com/conjure-up/conjure-up/pull/435) ([battlemidget](https://github.com/battlemidget))
- compatibility for python3.5 subprocess.run [\#434](https://github.com/conjure-up/conjure-up/pull/434) ([battlemidget](https://github.com/battlemidget))
- Fixes \#389 [\#433](https://github.com/conjure-up/conjure-up/pull/433) ([battlemidget](https://github.com/battlemidget))
- Remove charm/charm-tools dep [\#432](https://github.com/conjure-up/conjure-up/pull/432) ([battlemidget](https://github.com/battlemidget))
- Fixes \#215 [\#431](https://github.com/conjure-up/conjure-up/pull/431) ([battlemidget](https://github.com/battlemidget))
- Support editing num\_units for applications [\#430](https://github.com/conjure-up/conjure-up/pull/430) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#240 [\#427](https://github.com/conjure-up/conjure-up/pull/427) ([battlemidget](https://github.com/battlemidget))
- Fixes \#420 [\#426](https://github.com/conjure-up/conjure-up/pull/426) ([battlemidget](https://github.com/battlemidget))
- sync with macumba master [\#425](https://github.com/conjure-up/conjure-up/pull/425) ([mikemccracken](https://github.com/mikemccracken))
- sync bundleplacer [\#423](https://github.com/conjure-up/conjure-up/pull/423) ([mikemccracken](https://github.com/mikemccracken))

## [2.0.1-beta1](https://github.com/conjure-up/conjure-up/tree/2.0.1-beta1) (2016-09-20)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.9...2.0.1-beta1)

**Fixed bugs:**

- Exception: Tried to login with no current model set. [\#399](https://github.com/conjure-up/conjure-up/issues/399)
- conjure-up \<namespace\>/\<spell\> fails under snappy [\#365](https://github.com/conjure-up/conjure-up/issues/365)
- 2.0.0.7-0~526~ubuntu16.04.1 does not start bootstraping [\#310](https://github.com/conjure-up/conjure-up/issues/310)
- neutron API error using 1.0 needs 2.0 [\#288](https://github.com/conjure-up/conjure-up/issues/288)

**Closed issues:**

- applicationlist - dont show configure button if subordinate [\#415](https://github.com/conjure-up/conjure-up/issues/415)
- controllerpicker: filter blacklist/whitelist [\#413](https://github.com/conjure-up/conjure-up/issues/413)
- attributeerror with controllerpicker [\#410](https://github.com/conjure-up/conjure-up/issues/410)
- NovaLXD hook failed: "config-changed" and next steps after installation [\#361](https://github.com/conjure-up/conjure-up/issues/361)
- add hotkey to show spell readme from any screen [\#341](https://github.com/conjure-up/conjure-up/issues/341)
- No available machine matches constraints: zone=default` [\#331](https://github.com/conjure-up/conjure-up/issues/331)
- transition deb to snap only install [\#315](https://github.com/conjure-up/conjure-up/issues/315)
- display a list of current controllers or option to deploy new [\#294](https://github.com/conjure-up/conjure-up/issues/294)
- conjure-up sdks [\#248](https://github.com/conjure-up/conjure-up/issues/248)
- complete initial guides on conjure-up.io [\#166](https://github.com/conjure-up/conjure-up/issues/166)
- uncaught ConnectionClosedError in deploystatus  [\#137](https://github.com/conjure-up/conjure-up/issues/137)
- conjure-craft - add project starter [\#117](https://github.com/conjure-up/conjure-up/issues/117)
- application list view: no way to tell if charms are out of date [\#104](https://github.com/conjure-up/conjure-up/issues/104)
- add --verify for running tests after a deployment/post process complete [\#96](https://github.com/conjure-up/conjure-up/issues/96)
- allow choosing container type in service walkthrough [\#63](https://github.com/conjure-up/conjure-up/issues/63)

**Merged pull requests:**

- Submit label changed to Run [\#419](https://github.com/conjure-up/conjure-up/pull/419) ([battlemidget](https://github.com/battlemidget))
- Avoid showing config button for nothing [\#417](https://github.com/conjure-up/conjure-up/pull/417) ([mikemccracken](https://github.com/mikemccracken))
- Only show controllers matching white/blacklist [\#416](https://github.com/conjure-up/conjure-up/pull/416) ([mikemccracken](https://github.com/mikemccracken))
- Split application list to have a fixed footer description [\#414](https://github.com/conjure-up/conjure-up/pull/414) ([battlemidget](https://github.com/battlemidget))
- Fix another place where 'controllers' was used [\#412](https://github.com/conjure-up/conjure-up/pull/412) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#410 [\#411](https://github.com/conjure-up/conjure-up/pull/411) ([battlemidget](https://github.com/battlemidget))
- Fix 294 controller selection view [\#409](https://github.com/conjure-up/conjure-up/pull/409) ([mikemccracken](https://github.com/mikemccracken))
- Update add-credential view [\#408](https://github.com/conjure-up/conjure-up/pull/408) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.9](https://github.com/conjure-up/conjure-up/tree/2.0.0.9) (2016-09-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.8...2.0.0.9)

**Fixed bugs:**

- headless mode fails to deploy applications [\#402](https://github.com/conjure-up/conjure-up/issues/402)
- Told to add credentials when already done so [\#366](https://github.com/conjure-up/conjure-up/issues/366)
- look better on white backgrounds [\#283](https://github.com/conjure-up/conjure-up/issues/283)
- need to validate maas credential field in newcloud [\#224](https://github.com/conjure-up/conjure-up/issues/224)

**Closed issues:**

- split clouds view for existing public clouds and creating new clouds [\#395](https://github.com/conjure-up/conjure-up/issues/395)
- pressing deploy all should removes the \[configure\]\[deploy\] buttons [\#381](https://github.com/conjure-up/conjure-up/issues/381)
- snap install issue -- snap.conjure-up.bridge.service failed [\#376](https://github.com/conjure-up/conjure-up/issues/376)
- spells not sorted in spellpicker view [\#374](https://github.com/conjure-up/conjure-up/issues/374)
- conjure-up \<spell\> tracebacks [\#371](https://github.com/conjure-up/conjure-up/issues/371)
- remove initial readme view for spell [\#369](https://github.com/conjure-up/conjure-up/issues/369)
- rework deploy controller [\#323](https://github.com/conjure-up/conjure-up/issues/323)
- if no clouds are whitelisted \(e.g. openstack-novalxd spell\), an empty list is shown in the newcloud view [\#405](https://github.com/conjure-up/conjure-up/issues/405)
- crash in bootstrap because juju beta 16 does not allow bootstrap --upload-tools [\#367](https://github.com/conjure-up/conjure-up/issues/367)
- headless fails in a snappy environment [\#359](https://github.com/conjure-up/conjure-up/issues/359)
- show spell friendly name in spellpicker view [\#355](https://github.com/conjure-up/conjure-up/issues/355)
- separate spells and bundles.yaml [\#325](https://github.com/conjure-up/conjure-up/issues/325)
- rework keyword handling to avoid searching charm store [\#324](https://github.com/conjure-up/conjure-up/issues/324)
- clean up makefile for snappy builds [\#321](https://github.com/conjure-up/conjure-up/issues/321)
- need intro screen for showing existing controllers [\#320](https://github.com/conjure-up/conjure-up/issues/320)

**Merged pull requests:**

- Add conjureup0 network bridge [\#404](https://github.com/conjure-up/conjure-up/pull/404) ([battlemidget](https://github.com/battlemidget))
- fix log path in error view [\#403](https://github.com/conjure-up/conjure-up/pull/403) ([battlemidget](https://github.com/battlemidget))
- squash download errors if download stream length out of range [\#401](https://github.com/conjure-up/conjure-up/pull/401) ([battlemidget](https://github.com/battlemidget))
- Fixes \#283 [\#397](https://github.com/conjure-up/conjure-up/pull/397) ([battlemidget](https://github.com/battlemidget))
- update cloud list view [\#396](https://github.com/conjure-up/conjure-up/pull/396) ([battlemidget](https://github.com/battlemidget))
- add spell selector hover descriptions [\#394](https://github.com/conjure-up/conjure-up/pull/394) ([battlemidget](https://github.com/battlemidget))
- remove subheader as it is not part of the new designs [\#393](https://github.com/conjure-up/conjure-up/pull/393) ([battlemidget](https://github.com/battlemidget))
- Remove bundlereadme controller [\#392](https://github.com/conjure-up/conjure-up/pull/392) ([mikemccracken](https://github.com/mikemccracken))
- update to reflect new step paths [\#391](https://github.com/conjure-up/conjure-up/pull/391) ([battlemidget](https://github.com/battlemidget))
- fix deb packaging [\#390](https://github.com/conjure-up/conjure-up/pull/390) ([battlemidget](https://github.com/battlemidget))
- update readme to add lxd as a requirement [\#388](https://github.com/conjure-up/conjure-up/pull/388) ([battlemidget](https://github.com/battlemidget))
- Feature git spells registry [\#387](https://github.com/conjure-up/conjure-up/pull/387) ([battlemidget](https://github.com/battlemidget))
- make use of pep420 [\#386](https://github.com/conjure-up/conjure-up/pull/386) ([battlemidget](https://github.com/battlemidget))
- update travis,makefile to check isort [\#384](https://github.com/conjure-up/conjure-up/pull/384) ([battlemidget](https://github.com/battlemidget))
- Patch more dev checks [\#383](https://github.com/conjure-up/conjure-up/pull/383) ([battlemidget](https://github.com/battlemidget))
- go directly to status after deploy-all [\#382](https://github.com/conjure-up/conjure-up/pull/382) ([mikemccracken](https://github.com/mikemccracken))
- fix imports in utils [\#380](https://github.com/conjure-up/conjure-up/pull/380) ([battlemidget](https://github.com/battlemidget))
- Add openstack-base spell [\#379](https://github.com/conjure-up/conjure-up/pull/379) ([mikemccracken](https://github.com/mikemccracken))
- Do not show add-credential button until valid [\#378](https://github.com/conjure-up/conjure-up/pull/378) ([mikemccracken](https://github.com/mikemccracken))
- rework deploy screen [\#377](https://github.com/conjure-up/conjure-up/pull/377) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#374 [\#375](https://github.com/conjure-up/conjure-up/pull/375) ([battlemidget](https://github.com/battlemidget))
- add alternative install method [\#373](https://github.com/conjure-up/conjure-up/pull/373) ([battlemidget](https://github.com/battlemidget))
- Fixes \#371 [\#372](https://github.com/conjure-up/conjure-up/pull/372) ([battlemidget](https://github.com/battlemidget))
- deb packaging updates [\#370](https://github.com/conjure-up/conjure-up/pull/370) ([battlemidget](https://github.com/battlemidget))
- remove --upload-tools [\#368](https://github.com/conjure-up/conjure-up/pull/368) ([battlemidget](https://github.com/battlemidget))
- clean up makefile for snappy [\#364](https://github.com/conjure-up/conjure-up/pull/364) ([battlemidget](https://github.com/battlemidget))
- add description per spell in spells index [\#363](https://github.com/conjure-up/conjure-up/pull/363) ([battlemidget](https://github.com/battlemidget))
- Fixes \#402 [\#407](https://github.com/conjure-up/conjure-up/pull/407) ([battlemidget](https://github.com/battlemidget))
- Fixes \#405 [\#406](https://github.com/conjure-up/conjure-up/pull/406) ([battlemidget](https://github.com/battlemidget))
- add journald logging [\#398](https://github.com/conjure-up/conjure-up/pull/398) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.8](https://github.com/conjure-up/conjure-up/tree/2.0.0.8) (2016-08-22)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.6...2.0.0.8)

**Fixed bugs:**

- traceback in lxdsetup on snappy [\#346](https://github.com/conjure-up/conjure-up/issues/346)
- codec error loading spells index [\#336](https://github.com/conjure-up/conjure-up/issues/336)
- error creating directories at start [\#334](https://github.com/conjure-up/conjure-up/issues/334)
- Conjure-up - Unable to get juju version [\#296](https://github.com/conjure-up/conjure-up/issues/296)
- application "neutron-gateway" not found [\#273](https://github.com/conjure-up/conjure-up/issues/273)
- The installation does not start . I am with ppa:conjure-up/daily-git [\#252](https://github.com/conjure-up/conjure-up/issues/252)
- pre-deploy fails intermittently for LXD provider after an add-model [\#197](https://github.com/conjure-up/conjure-up/issues/197)
- conjure-up doesn't appear to work in charmbox [\#279](https://github.com/conjure-up/conjure-up/issues/279)

**Closed issues:**

- Add a hooklib function to run juju actions and wait  [\#339](https://github.com/conjure-up/conjure-up/issues/339)
- test failure if no juju found on system [\#312](https://github.com/conjure-up/conjure-up/issues/312)
- conjure-up openstack on 16.04 still not working [\#289](https://github.com/conjure-up/conjure-up/issues/289)
- AttributeError: 'NoneType' object has no attribute  [\#287](https://github.com/conjure-up/conjure-up/issues/287)
- Traceback error if a spell has no steps [\#286](https://github.com/conjure-up/conjure-up/issues/286)
- make add\_machines work in headless mode [\#280](https://github.com/conjure-up/conjure-up/issues/280)
- traceback in conjuring hadoop [\#271](https://github.com/conjure-up/conjure-up/issues/271)
- remove submit on steps after pressing [\#267](https://github.com/conjure-up/conjure-up/issues/267)
- add autopkg test [\#266](https://github.com/conjure-up/conjure-up/issues/266)
- load application metadata earlier [\#263](https://github.com/conjure-up/conjure-up/issues/263)
- traceback in service walkthrough for apache mapreduce bundle [\#260](https://github.com/conjure-up/conjure-up/issues/260)
- add asyncio subprocess to read from stdout [\#247](https://github.com/conjure-up/conjure-up/issues/247)
- add openstack upstream spell [\#243](https://github.com/conjure-up/conjure-up/issues/243)
- document enabling existing bundle to be conjure-up enabled [\#190](https://github.com/conjure-up/conjure-up/issues/190)
- conjure-up.conf blessed should be True for GA release [\#94](https://github.com/conjure-up/conjure-up/issues/94)
- switch to asyncio coroutines and Futures for async.submit [\#77](https://github.com/conjure-up/conjure-up/issues/77)
- add 'view full readme' button/overlay [\#47](https://github.com/conjure-up/conjure-up/issues/47)
- 'conjure-up' with no args should show screen with list of packaged spells [\#322](https://github.com/conjure-up/conjure-up/issues/322)
- lxdsetup view does nothing in TUI [\#309](https://github.com/conjure-up/conjure-up/issues/309)
- conjure-up supports running without a spell defined on the cli [\#293](https://github.com/conjure-up/conjure-up/issues/293)
- make it snap installable [\#290](https://github.com/conjure-up/conjure-up/issues/290)
- conjure-up bigdata:  wget failure [\#285](https://github.com/conjure-up/conjure-up/issues/285)
- Support logging to flatfile [\#282](https://github.com/conjure-up/conjure-up/issues/282)
- check user group for lxd [\#262](https://github.com/conjure-up/conjure-up/issues/262)
- handle post-deploy failures better [\#204](https://github.com/conjure-up/conjure-up/issues/204)
- conjure-list to query registry [\#116](https://github.com/conjure-up/conjure-up/issues/116)

**Merged pull requests:**

- Display friendly spell names [\#362](https://github.com/conjure-up/conjure-up/pull/362) ([battlemidget](https://github.com/battlemidget))
- re-add common lib to openstack spell, more cleanups [\#360](https://github.com/conjure-up/conjure-up/pull/360) ([battlemidget](https://github.com/battlemidget))
- update to add network bridge [\#358](https://github.com/conjure-up/conjure-up/pull/358) ([battlemidget](https://github.com/battlemidget))
- make lxd configuration a user task [\#357](https://github.com/conjure-up/conjure-up/pull/357) ([battlemidget](https://github.com/battlemidget))
- fix parse-whitelist and parse-blacklist [\#354](https://github.com/conjure-up/conjure-up/pull/354) ([battlemidget](https://github.com/battlemidget))
- use dump plugin for snapcraft [\#353](https://github.com/conjure-up/conjure-up/pull/353) ([battlemidget](https://github.com/battlemidget))
- Fix shortcut when keyword search matches one spell [\#352](https://github.com/conjure-up/conjure-up/pull/352) ([mikemccracken](https://github.com/mikemccracken))
- reduce snap to ~56M [\#351](https://github.com/conjure-up/conjure-up/pull/351) ([battlemidget](https://github.com/battlemidget))
- remove lxd stage-package [\#350](https://github.com/conjure-up/conjure-up/pull/350) ([battlemidget](https://github.com/battlemidget))
- strip out unused files from snap build [\#349](https://github.com/conjure-up/conjure-up/pull/349) ([battlemidget](https://github.com/battlemidget))
- update readme [\#348](https://github.com/conjure-up/conjure-up/pull/348) ([battlemidget](https://github.com/battlemidget))
- remove incorrect license from tests headers [\#345](https://github.com/conjure-up/conjure-up/pull/345) ([battlemidget](https://github.com/battlemidget))
- Fix application deploy [\#344](https://github.com/conjure-up/conjure-up/pull/344) ([battlemidget](https://github.com/battlemidget))
- synergize tasteful, crisp, effective solutions [\#343](https://github.com/conjure-up/conjure-up/pull/343) ([tych0](https://github.com/tych0))
- make setuptools find pep420 style packages [\#342](https://github.com/conjure-up/conjure-up/pull/342) ([battlemidget](https://github.com/battlemidget))
- add wireframe doc [\#338](https://github.com/conjure-up/conjure-up/pull/338) ([battlemidget](https://github.com/battlemidget))
- Fixes \#336 [\#337](https://github.com/conjure-up/conjure-up/pull/337) ([battlemidget](https://github.com/battlemidget))
- Fixes \#334 [\#335](https://github.com/conjure-up/conjure-up/pull/335) ([battlemidget](https://github.com/battlemidget))
- Fix tox flake command and fix lint that got thru [\#333](https://github.com/conjure-up/conjure-up/pull/333) ([mikemccracken](https://github.com/mikemccracken))
- Misc fixes for new spell organization [\#332](https://github.com/conjure-up/conjure-up/pull/332) ([mikemccracken](https://github.com/mikemccracken))
- Overhaul spell finding and searching [\#330](https://github.com/conjure-up/conjure-up/pull/330) ([mikemccracken](https://github.com/mikemccracken))
- remove 'to' subparser to allow optional spell name [\#329](https://github.com/conjure-up/conjure-up/pull/329) ([mikemccracken](https://github.com/mikemccracken))
- remove apt install for additional packages [\#328](https://github.com/conjure-up/conjure-up/pull/328) ([battlemidget](https://github.com/battlemidget))
- keep cli options naming consistent [\#327](https://github.com/conjure-up/conjure-up/pull/327) ([battlemidget](https://github.com/battlemidget))
- Several related initial view / snappy / charmstore search removal changes [\#326](https://github.com/conjure-up/conjure-up/pull/326) ([mikemccracken](https://github.com/mikemccracken))
- bring spells into the project [\#316](https://github.com/conjure-up/conjure-up/pull/316) ([battlemidget](https://github.com/battlemidget))
- Avoid calling out to juju in tests [\#314](https://github.com/conjure-up/conjure-up/pull/314) ([mikemccracken](https://github.com/mikemccracken))
- Add lots of test scaffolding [\#311](https://github.com/conjure-up/conjure-up/pull/311) ([mikemccracken](https://github.com/mikemccracken))
- do not rely on wget [\#308](https://github.com/conjure-up/conjure-up/pull/308) ([battlemidget](https://github.com/battlemidget))
- move bootstrap output up to top-level of cache dir [\#307](https://github.com/conjure-up/conjure-up/pull/307) ([mikemccracken](https://github.com/mikemccracken))
- squelch stderr from tail [\#306](https://github.com/conjure-up/conjure-up/pull/306) ([mikemccracken](https://github.com/mikemccracken))
- Don't call set\_text with undefined out [\#305](https://github.com/conjure-up/conjure-up/pull/305) ([mikemccracken](https://github.com/mikemccracken))
- Avoid dying if stderr output file isn't there yet [\#304](https://github.com/conjure-up/conjure-up/pull/304) ([mikemccracken](https://github.com/mikemccracken))
- Fix \#286 [\#303](https://github.com/conjure-up/conjure-up/pull/303) ([mikemccracken](https://github.com/mikemccracken))
- Step feedback [\#302](https://github.com/conjure-up/conjure-up/pull/302) ([mikemccracken](https://github.com/mikemccracken))
- show bootstrap output and save it to a file [\#299](https://github.com/conjure-up/conjure-up/pull/299) ([mikemccracken](https://github.com/mikemccracken))
- sync version in snap [\#298](https://github.com/conjure-up/conjure-up/pull/298) ([battlemidget](https://github.com/battlemidget))
- pull in wget/juju for snappy snap snap [\#297](https://github.com/conjure-up/conjure-up/pull/297) ([battlemidget](https://github.com/battlemidget))
- more conjure -\> conjureup renames [\#292](https://github.com/conjure-up/conjure-up/pull/292) ([battlemidget](https://github.com/battlemidget))
- fix typo in call to handle\_exception [\#284](https://github.com/conjure-up/conjure-up/pull/284) ([battlemidget](https://github.com/battlemidget))
- remove superfluous async submit for add\_machines [\#281](https://github.com/conjure-up/conjure-up/pull/281) ([mikemccracken](https://github.com/mikemccracken))
- Fix automatically running steps in TUI [\#278](https://github.com/conjure-up/conjure-up/pull/278) ([battlemidget](https://github.com/battlemidget))
- Fixes \#266 [\#277](https://github.com/conjure-up/conjure-up/pull/277) ([battlemidget](https://github.com/battlemidget))
- refactor tui controllers [\#276](https://github.com/conjure-up/conjure-up/pull/276) ([battlemidget](https://github.com/battlemidget))
- Make service deploy in TUI great again [\#275](https://github.com/conjure-up/conjure-up/pull/275) ([battlemidget](https://github.com/battlemidget))
- Make checkbox conform [\#274](https://github.com/conjure-up/conjure-up/pull/274) ([battlemidget](https://github.com/battlemidget))
- load metadata after spell is chosen [\#272](https://github.com/conjure-up/conjure-up/pull/272) ([mikemccracken](https://github.com/mikemccracken))
- set is\_predeploy\_queued immediately after queueing [\#270](https://github.com/conjure-up/conjure-up/pull/270) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#267 [\#269](https://github.com/conjure-up/conjure-up/pull/269) ([battlemidget](https://github.com/battlemidget))
- Move metadata controller init earlier [\#268](https://github.com/conjure-up/conjure-up/pull/268) ([mikemccracken](https://github.com/mikemccracken))
- Add tests for deploycontroller.finish [\#265](https://github.com/conjure-up/conjure-up/pull/265) ([mikemccracken](https://github.com/mikemccracken))
- Bump rev in master [\#264](https://github.com/conjure-up/conjure-up/pull/264) ([battlemidget](https://github.com/battlemidget))
- Fixes \#260 [\#261](https://github.com/conjure-up/conjure-up/pull/261) ([battlemidget](https://github.com/battlemidget))
- Refactor controllers [\#259](https://github.com/conjure-up/conjure-up/pull/259) ([battlemidget](https://github.com/battlemidget))
- Unit test deploy controller [\#258](https://github.com/conjure-up/conjure-up/pull/258) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#282 [\#318](https://github.com/conjure-up/conjure-up/pull/318) ([battlemidget](https://github.com/battlemidget))
- re-organization with steps hooklib [\#317](https://github.com/conjure-up/conjure-up/pull/317) ([battlemidget](https://github.com/battlemidget))
- more snappy fixes [\#313](https://github.com/conjure-up/conjure-up/pull/313) ([battlemidget](https://github.com/battlemidget))
- make it snappy [\#291](https://github.com/conjure-up/conjure-up/pull/291) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.6](https://github.com/conjure-up/conjure-up/tree/2.0.0.6) (2016-07-18)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.5...2.0.0.6)

**Fixed bugs:**

- conjure-up openstack fails with "Machine creation errors: 0: Failed to get device attributes: no such file or directory" [\#227](https://github.com/conjure-up/conjure-up/issues/227)
- traceback during services list view [\#231](https://github.com/conjure-up/conjure-up/issues/231)
- Ungraceful exception [\#214](https://github.com/conjure-up/conjure-up/issues/214)
- Barfs when using an edited bundle.yaml for machine placement with MAAS [\#211](https://github.com/conjure-up/conjure-up/issues/211)

**Closed issues:**

- Failure in deploy-done \(\#012glannce/0: hook failed: "install"\) [\#233](https://github.com/conjure-up/conjure-up/issues/233)
- options-whitelist showing duplicate entries [\#256](https://github.com/conjure-up/conjure-up/issues/256)
- make charmstore tag search for `conjure-up-\<spell\>` [\#245](https://github.com/conjure-up/conjure-up/issues/245)
- better formatting in summary page [\#242](https://github.com/conjure-up/conjure-up/issues/242)
- make deploy\_done wait until all services have been allocated [\#238](https://github.com/conjure-up/conjure-up/issues/238)
- readme screen should accept TAB to go back to continue button [\#226](https://github.com/conjure-up/conjure-up/issues/226)
- more feedback prior to displaying the service status screen [\#205](https://github.com/conjure-up/conjure-up/issues/205)
- make sure steps can not be run out of order [\#135](https://github.com/conjure-up/conjure-up/issues/135)

**Merged pull requests:**

- Avoid adding options twice [\#257](https://github.com/conjure-up/conjure-up/pull/257) ([mikemccracken](https://github.com/mikemccracken))
- add tab loop to bundle readme view [\#255](https://github.com/conjure-up/conjure-up/pull/255) ([mikemccracken](https://github.com/mikemccracken))
- Remove unnecessary wait for deploy status view [\#237](https://github.com/conjure-up/conjure-up/pull/237) ([mikemccracken](https://github.com/mikemccracken))
- update deploystatusview on main thread [\#235](https://github.com/conjure-up/conjure-up/pull/235) ([mikemccracken](https://github.com/mikemccracken))
- Fix prepare constraints [\#234](https://github.com/conjure-up/conjure-up/pull/234) ([battlemidget](https://github.com/battlemidget))
- cleanup summary [\#254](https://github.com/conjure-up/conjure-up/pull/254) ([battlemidget](https://github.com/battlemidget))
- fix beta12 change in accounts [\#253](https://github.com/conjure-up/conjure-up/pull/253) ([battlemidget](https://github.com/battlemidget))
- Patch gh 135 [\#250](https://github.com/conjure-up/conjure-up/pull/250) ([battlemidget](https://github.com/battlemidget))
- Search for `conjure-up` rather than `conjure` [\#246](https://github.com/conjure-up/conjure-up/pull/246) ([battlemidget](https://github.com/battlemidget))
- Patch step ui refinements [\#244](https://github.com/conjure-up/conjure-up/pull/244) ([battlemidget](https://github.com/battlemidget))
- Add wait for applications to deploy q [\#239](https://github.com/conjure-up/conjure-up/pull/239) ([battlemidget](https://github.com/battlemidget))
- Patch gh 205 [\#236](https://github.com/conjure-up/conjure-up/pull/236) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.5](https://github.com/conjure-up/conjure-up/tree/2.0.0.5) (2016-07-12)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.4...2.0.0.5)

**Fixed bugs:**

- Need to add machines prior to deploying applications with placements [\#216](https://github.com/conjure-up/conjure-up/issues/216)
- --status-only fails on missing positional arg to deploy render [\#212](https://github.com/conjure-up/conjure-up/issues/212)
- Doesn't work with Juju 2.0 and MAAS 2.0 [\#199](https://github.com/conjure-up/conjure-up/issues/199)
- slow charmstore search can delay initial UI [\#172](https://github.com/conjure-up/conjure-up/issues/172)

**Closed issues:**

- traceback in applications list view [\#232](https://github.com/conjure-up/conjure-up/issues/232)
- Not accepting MAAS credentials in input field [\#220](https://github.com/conjure-up/conjure-up/issues/220)
- doesn't work again, with juju 2 beta11, MAAS 2 rc1... [\#218](https://github.com/conjure-up/conjure-up/issues/218)
- failure to bootstrap into maas [\#225](https://github.com/conjure-up/conjure-up/issues/225)
- Add information on where to file bugs in exception view [\#203](https://github.com/conjure-up/conjure-up/issues/203)
- change bootstrapping environment text [\#202](https://github.com/conjure-up/conjure-up/issues/202)
- 'openstack' curated spell does not include a low-machine-count bundle [\#176](https://github.com/conjure-up/conjure-up/issues/176)
- No available machine matches constraints: zone=default [\#175](https://github.com/conjure-up/conjure-up/issues/175)
- new: bundle overview screen for showing bundle README before service walkthru [\#169](https://github.com/conjure-up/conjure-up/issues/169)

**Merged pull requests:**

- Add machines if specified in bundle [\#228](https://github.com/conjure-up/conjure-up/pull/228) ([mikemccracken](https://github.com/mikemccracken))
- Make TUI flow exit on all script errors [\#222](https://github.com/conjure-up/conjure-up/pull/222) ([mikemccracken](https://github.com/mikemccracken))
- allow apt update on bootstrap [\#221](https://github.com/conjure-up/conjure-up/pull/221) ([mikemccracken](https://github.com/mikemccracken))
- Add new bundle readme screen to gui path [\#219](https://github.com/conjure-up/conjure-up/pull/219) ([mikemccracken](https://github.com/mikemccracken))
- avoid traceback when running via -s [\#213](https://github.com/conjure-up/conjure-up/pull/213) ([mikemccracken](https://github.com/mikemccracken))
- Add extra info to error screen [\#210](https://github.com/conjure-up/conjure-up/pull/210) ([mikemccracken](https://github.com/mikemccracken))
- Improve feedback for initial charmstore search [\#209](https://github.com/conjure-up/conjure-up/pull/209) ([mikemccracken](https://github.com/mikemccracken))
- add authors [\#208](https://github.com/conjure-up/conjure-up/pull/208) ([battlemidget](https://github.com/battlemidget))
- Fix 202 [\#207](https://github.com/conjure-up/conjure-up/pull/207) ([mikemccracken](https://github.com/mikemccracken))
- change login check [\#206](https://github.com/conjure-up/conjure-up/pull/206) ([mikemccracken](https://github.com/mikemccracken))
- fix constraints for add machines [\#230](https://github.com/conjure-up/conjure-up/pull/230) ([battlemidget](https://github.com/battlemidget))
- Handle macumba server error during add machines [\#229](https://github.com/conjure-up/conjure-up/pull/229) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.4](https://github.com/conjure-up/conjure-up/tree/2.0.0.4) (2016-07-01)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.3...2.0.0.4)

**Closed issues:**

- Deployment without success. no issue to import key key ssh.  [\#178](https://github.com/conjure-up/conjure-up/issues/178)
- blocking the recovery of the ssh key [\#177](https://github.com/conjure-up/conjure-up/issues/177)
- Doesn't work ootb for OpenStack [\#167](https://github.com/conjure-up/conjure-up/issues/167)
- sometimes last applications deployed are ending up in error state [\#115](https://github.com/conjure-up/conjure-up/issues/115)
- doesn't work again, with juju 2 beta11, MAAS 2 rc1... [\#201](https://github.com/conjure-up/conjure-up/issues/201)
- deploying services do not include resources [\#195](https://github.com/conjure-up/conjure-up/issues/195)
- metadata spec update to include required apt packages [\#179](https://github.com/conjure-up/conjure-up/issues/179)
- post-bootstrap is not run when controller exists [\#174](https://github.com/conjure-up/conjure-up/issues/174)
- Possibility to provide \(or propagate\) proxy settings and bootstrap timeout [\#171](https://github.com/conjure-up/conjure-up/issues/171)
- ui freezes after last deployment until all deploy and relation api calls are done [\#170](https://github.com/conjure-up/conjure-up/issues/170)
- ability to deploy spells from filesystem [\#158](https://github.com/conjure-up/conjure-up/issues/158)
- documentation - add info about how to "stop" or "delete" openstack [\#155](https://github.com/conjure-up/conjure-up/issues/155)
- document running steps in headless mode [\#144](https://github.com/conjure-up/conjure-up/issues/144)
- add 'conjure' transitional package to debian packaging [\#133](https://github.com/conjure-up/conjure-up/issues/133)

**Merged pull requests:**

- Compat fix for juju2 beta11 [\#200](https://github.com/conjure-up/conjure-up/pull/200) ([battlemidget](https://github.com/battlemidget))
- fix common-sh hooklib [\#198](https://github.com/conjure-up/conjure-up/pull/198) ([battlemidget](https://github.com/battlemidget))
- Patch add resources to deploy [\#196](https://github.com/conjure-up/conjure-up/pull/196) ([battlemidget](https://github.com/battlemidget))
- dont fail on unknown workload status message [\#194](https://github.com/conjure-up/conjure-up/pull/194) ([battlemidget](https://github.com/battlemidget))
- Patch pre deploy fixes [\#192](https://github.com/conjure-up/conjure-up/pull/192) ([battlemidget](https://github.com/battlemidget))
- Only run pre-deploy once and return proper json [\#191](https://github.com/conjure-up/conjure-up/pull/191) ([battlemidget](https://github.com/battlemidget))
- Fixes \#174 [\#188](https://github.com/conjure-up/conjure-up/pull/188) ([battlemidget](https://github.com/battlemidget))
- fix logname [\#187](https://github.com/conjure-up/conjure-up/pull/187) ([battlemidget](https://github.com/battlemidget))
- Fixes \#171 [\#186](https://github.com/conjure-up/conjure-up/pull/186) ([battlemidget](https://github.com/battlemidget))
- Fixes \#158 [\#185](https://github.com/conjure-up/conjure-up/pull/185) ([battlemidget](https://github.com/battlemidget))
- Fixes \#133 [\#184](https://github.com/conjure-up/conjure-up/pull/184) ([battlemidget](https://github.com/battlemidget))
- Fix deploy via juju api [\#183](https://github.com/conjure-up/conjure-up/pull/183) ([battlemidget](https://github.com/battlemidget))
- fixes more juju beta10 api changes [\#182](https://github.com/conjure-up/conjure-up/pull/182) ([battlemidget](https://github.com/battlemidget))
- Patch raise min juju [\#181](https://github.com/conjure-up/conjure-up/pull/181) ([battlemidget](https://github.com/battlemidget))
- Patch gh 179 [\#180](https://github.com/conjure-up/conjure-up/pull/180) ([battlemidget](https://github.com/battlemidget))
- Show deploystatus view immediately after deploys [\#173](https://github.com/conjure-up/conjure-up/pull/173) ([mikemccracken](https://github.com/mikemccracken))

## [2.0.0.3](https://github.com/conjure-up/conjure-up/tree/2.0.0.3) (2016-06-17)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.2...2.0.0.3)

**Closed issues:**

- Distro error openstack/autopilot [\#154](https://github.com/conjure-up/conjure-up/issues/154)
- traceback with http proxy code [\#134](https://github.com/conjure-up/conjure-up/issues/134)
- conjure-up openstack presents no cloud choices to choose from?? [\#127](https://github.com/conjure-up/conjure-up/issues/127)
- ceph-osd blocked with "No block devices detected using current configuration" [\#125](https://github.com/conjure-up/conjure-up/issues/125)
- make table heading row fixed in services status view [\#21](https://github.com/conjure-up/conjure-up/issues/21)
- traceback during tui deploy [\#164](https://github.com/conjure-up/conjure-up/issues/164)
- Invalid markup element ServerError\(ServerError\(…\), ‘unknown version \(1\) of interface “Application”’\) [\#163](https://github.com/conjure-up/conjure-up/issues/163)
- error when deploying application is not shown to user [\#159](https://github.com/conjure-up/conjure-up/issues/159)
- make steps work in headless mode [\#141](https://github.com/conjure-up/conjure-up/issues/141)
- juju add-model call should use juju async queue [\#139](https://github.com/conjure-up/conjure-up/issues/139)
- traceback when deploying a bundle without revnos too fast [\#138](https://github.com/conjure-up/conjure-up/issues/138)
- update icon states in steps [\#136](https://github.com/conjure-up/conjure-up/issues/136)
- deploy-done,postbootstrap, steps no filename extensions [\#129](https://github.com/conjure-up/conjure-up/issues/129)
- check for appropriate beta version of juju [\#128](https://github.com/conjure-up/conjure-up/issues/128)
- non captured traceback during add relations [\#126](https://github.com/conjure-up/conjure-up/issues/126)
- need friendlier error messages when using -s on a non-bootstrapped or non-deployed system [\#83](https://github.com/conjure-up/conjure-up/issues/83)
- hang after pressing 'q' from deploy status screen [\#73](https://github.com/conjure-up/conjure-up/issues/73)
- add a fallback description for spells that aren't in keyword-definitions.yaml [\#55](https://github.com/conjure-up/conjure-up/issues/55)
- add http/s proxy support [\#22](https://github.com/conjure-up/conjure-up/issues/22)

**Merged pull requests:**

- TUI and async fixes [\#165](https://github.com/conjure-up/conjure-up/pull/165) ([mikemccracken](https://github.com/mikemccracken))
- Fix 159 [\#162](https://github.com/conjure-up/conjure-up/pull/162) ([mikemccracken](https://github.com/mikemccracken))
- Fix deploy issues [\#161](https://github.com/conjure-up/conjure-up/pull/161) ([mikemccracken](https://github.com/mikemccracken))
- deploy in callback to get\_info for unpinned apps [\#160](https://github.com/conjure-up/conjure-up/pull/160) ([mikemccracken](https://github.com/mikemccracken))
- juju.switch -\> switch\_controller and switch\_model [\#157](https://github.com/conjure-up/conjure-up/pull/157) ([mikemccracken](https://github.com/mikemccracken))
- Juju Beta 9 api compat changes [\#156](https://github.com/conjure-up/conjure-up/pull/156) ([battlemidget](https://github.com/battlemidget))
- poll bootstrap subprocess so we can kill on quit [\#153](https://github.com/conjure-up/conjure-up/pull/153) ([mikemccracken](https://github.com/mikemccracken))
- Improve finding existing controller & adding model [\#152](https://github.com/conjure-up/conjure-up/pull/152) ([mikemccracken](https://github.com/mikemccracken))
- Add hooklib symlink during development [\#151](https://github.com/conjure-up/conjure-up/pull/151) ([battlemidget](https://github.com/battlemidget))
- pin ws4py to version working in xenial [\#150](https://github.com/conjure-up/conjure-up/pull/150) ([mikemccracken](https://github.com/mikemccracken))
- Improve error handling in wait script [\#149](https://github.com/conjure-up/conjure-up/pull/149) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#83 [\#148](https://github.com/conjure-up/conjure-up/pull/148) ([battlemidget](https://github.com/battlemidget))
- Fixes \#141 [\#145](https://github.com/conjure-up/conjure-up/pull/145) ([battlemidget](https://github.com/battlemidget))
- Fixes \#55 [\#143](https://github.com/conjure-up/conjure-up/pull/143) ([battlemidget](https://github.com/battlemidget))
- Update status icon states for steps [\#142](https://github.com/conjure-up/conjure-up/pull/142) ([battlemidget](https://github.com/battlemidget))
- Rework step findings [\#140](https://github.com/conjure-up/conjure-up/pull/140) ([battlemidget](https://github.com/battlemidget))
- Fixes \#22 [\#132](https://github.com/conjure-up/conjure-up/pull/132) ([battlemidget](https://github.com/battlemidget))
- check for at least juju beta 9 [\#131](https://github.com/conjure-up/conjure-up/pull/131) ([battlemidget](https://github.com/battlemidget))
- Fixes \#129 [\#130](https://github.com/conjure-up/conjure-up/pull/130) ([battlemidget](https://github.com/battlemidget))
- Feature python hooklib [\#147](https://github.com/conjure-up/conjure-up/pull/147) ([battlemidget](https://github.com/battlemidget))

## [2.0.0.2](https://github.com/conjure-up/conjure-up/tree/2.0.0.2) (2016-06-13)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.0.0.1...2.0.0.2)

**Closed issues:**

- PPA Install resulting in no spell found [\#54](https://github.com/conjure-up/conjure-up/issues/54)
- log the juju commands that we run [\#23](https://github.com/conjure-up/conjure-up/issues/23)
- walkthru: subordinate charms should not show num\_units [\#118](https://github.com/conjure-up/conjure-up/issues/118)
- prefix steps filenames [\#113](https://github.com/conjure-up/conjure-up/issues/113)
- syncing latest bundleplacement changes fails to load initial readme [\#110](https://github.com/conjure-up/conjure-up/issues/110)
- address juju 2.0 beta9 internal changes [\#107](https://github.com/conjure-up/conjure-up/issues/107)
- walkthrough: initial unit count is not correct [\#102](https://github.com/conjure-up/conjure-up/issues/102)
- indexerror when updating readme  [\#100](https://github.com/conjure-up/conjure-up/issues/100)
- each deploy button press should indicate something is being deployed [\#99](https://github.com/conjure-up/conjure-up/issues/99)
- charm IDs with no revno do not deploy correctly [\#93](https://github.com/conjure-up/conjure-up/issues/93)
- spell download does not check staleness of cached spell [\#92](https://github.com/conjure-up/conjure-up/issues/92)
- steps view should be interactive [\#91](https://github.com/conjure-up/conjure-up/issues/91)
- last service in walkthru needs different button labels [\#90](https://github.com/conjure-up/conjure-up/issues/90)
- errors in machine bringup during deploy are not shown to user [\#72](https://github.com/conjure-up/conjure-up/issues/72)
- ui tweaks [\#51](https://github.com/conjure-up/conjure-up/issues/51)
- conjure-up openstack landscape deploy failure [\#43](https://github.com/conjure-up/conjure-up/issues/43)
- bsdtar is required but not installed by install-dependencies [\#41](https://github.com/conjure-up/conjure-up/issues/41)
- support maas 2.0 [\#38](https://github.com/conjure-up/conjure-up/issues/38)
- service walkthrough: deploy services one at a time [\#26](https://github.com/conjure-up/conjure-up/issues/26)
- Openstack LXD Single installation failing [\#8](https://github.com/conjure-up/conjure-up/issues/8)

**Merged pull requests:**

- Feature interactive steps [\#123](https://github.com/conjure-up/conjure-up/pull/123) ([battlemidget](https://github.com/battlemidget))
- Ensure local spell dir is empty before downloading [\#122](https://github.com/conjure-up/conjure-up/pull/122) ([mikemccracken](https://github.com/mikemccracken))
- don't show num\_units for subs [\#121](https://github.com/conjure-up/conjure-up/pull/121) ([mikemccracken](https://github.com/mikemccracken))
- sync bundleplacer cleanups [\#120](https://github.com/conjure-up/conjure-up/pull/120) ([mikemccracken](https://github.com/mikemccracken))
- support maas 2.0 [\#114](https://github.com/conjure-up/conjure-up/pull/114) ([battlemidget](https://github.com/battlemidget))
- sync bundleplacer to fix readmes again [\#112](https://github.com/conjure-up/conjure-up/pull/112) ([mikemccracken](https://github.com/mikemccracken))
- issue message callback for deploy/relation [\#111](https://github.com/conjure-up/conjure-up/pull/111) ([battlemidget](https://github.com/battlemidget))
- juju 9 internal changes [\#109](https://github.com/conjure-up/conjure-up/pull/109) ([battlemidget](https://github.com/battlemidget))
- Patch better step queue [\#108](https://github.com/conjure-up/conjure-up/pull/108) ([battlemidget](https://github.com/battlemidget))
- walkthru: Show just one button for last service [\#105](https://github.com/conjure-up/conjure-up/pull/105) ([mikemccracken](https://github.com/mikemccracken))
- Fix fetching readmes for user-scoped charms [\#103](https://github.com/conjure-up/conjure-up/pull/103) ([mikemccracken](https://github.com/mikemccracken))
- install additional deps with make install-dependencies [\#101](https://github.com/conjure-up/conjure-up/pull/101) ([battlemidget](https://github.com/battlemidget))
- return properly on deploy service exception [\#97](https://github.com/conjure-up/conjure-up/pull/97) ([battlemidget](https://github.com/battlemidget))
- fix post-bootstrap location [\#95](https://github.com/conjure-up/conjure-up/pull/95) ([battlemidget](https://github.com/battlemidget))
- Deploy: Use latest revno if not set [\#119](https://github.com/conjure-up/conjure-up/pull/119) ([mikemccracken](https://github.com/mikemccracken))
- actually use the service's num\_units [\#106](https://github.com/conjure-up/conjure-up/pull/106) ([mikemccracken](https://github.com/mikemccracken))

## [2.0.0.1](https://github.com/conjure-up/conjure-up/tree/2.0.0.1) (2016-06-08)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.1.2...2.0.0.1)

**Fixed bugs:**

- Can't get the console of a LXD container. [\#14](https://github.com/conjure-up/conjure-up/issues/14)
- Stack Trace on conjure-up bigdata [\#40](https://github.com/conjure-up/conjure-up/issues/40)

**Closed issues:**

- headless mode [\#98](https://github.com/conjure-up/conjure-up/issues/98)
- relation setting failure [\#86](https://github.com/conjure-up/conjure-up/issues/86)
- add global queue for managing juju commands [\#69](https://github.com/conjure-up/conjure-up/issues/69)
- cleanup service status view [\#66](https://github.com/conjure-up/conjure-up/issues/66)
- keyword definition for openstack starts with "Juju" [\#57](https://github.com/conjure-up/conjure-up/issues/57)
- allow use of GUI for non-keyword spells [\#56](https://github.com/conjure-up/conjure-up/issues/56)
- traceback when getting spell from charm store [\#42](https://github.com/conjure-up/conjure-up/issues/42)
- show status info line after background bootstrap  [\#39](https://github.com/conjure-up/conjure-up/issues/39)
- traceback after choosing 'localhost' as a cloud [\#36](https://github.com/conjure-up/conjure-up/issues/36)
- crash when choosing 'lxd' cloud [\#35](https://github.com/conjure-up/conjure-up/issues/35)
- set up travis for unit tests [\#31](https://github.com/conjure-up/conjure-up/issues/31)
- add charm store download for spell-enabled bundles [\#30](https://github.com/conjure-up/conjure-up/issues/30)
- post-deploy actions view MVP [\#29](https://github.com/conjure-up/conjure-up/issues/29)
- service walkthrough view MVP [\#28](https://github.com/conjure-up/conjure-up/issues/28)
- add summary view after post-deploy actions view [\#27](https://github.com/conjure-up/conjure-up/issues/27)
- start bootstrap early [\#25](https://github.com/conjure-up/conjure-up/issues/25)
- service walkthrough view - show only some options [\#24](https://github.com/conjure-up/conjure-up/issues/24)
- add conjure-craft tool [\#20](https://github.com/conjure-up/conjure-up/issues/20)

**Merged pull requests:**

- async handle deploystatus [\#89](https://github.com/conjure-up/conjure-up/pull/89) ([battlemidget](https://github.com/battlemidget))
- uniquify relations before setting [\#88](https://github.com/conjure-up/conjure-up/pull/88) ([mikemccracken](https://github.com/mikemccracken))
- dont assume unknown means active [\#87](https://github.com/conjure-up/conjure-up/pull/87) ([battlemidget](https://github.com/battlemidget))
- no more pre deploy scripts, no second deploy bundle [\#85](https://github.com/conjure-up/conjure-up/pull/85) ([battlemidget](https://github.com/battlemidget))
- Add juju event queue and finish service walkthru [\#84](https://github.com/conjure-up/conjure-up/pull/84) ([mikemccracken](https://github.com/mikemccracken))
- pass credentials in headless mode bootstrap [\#82](https://github.com/conjure-up/conjure-up/pull/82) ([battlemidget](https://github.com/battlemidget))
- Add additional unit function checks [\#81](https://github.com/conjure-up/conjure-up/pull/81) ([battlemidget](https://github.com/battlemidget))
- Make sure to switch to the most current model [\#80](https://github.com/conjure-up/conjure-up/pull/80) ([battlemidget](https://github.com/battlemidget))
- drive-by shell fix [\#79](https://github.com/conjure-up/conjure-up/pull/79) ([battlemidget](https://github.com/battlemidget))
- Add results view [\#78](https://github.com/conjure-up/conjure-up/pull/78) ([battlemidget](https://github.com/battlemidget))
- invalidate widget caches when changing size [\#76](https://github.com/conjure-up/conjure-up/pull/76) ([mikemccracken](https://github.com/mikemccracken))
- Add option whitelist to spell metadata. [\#75](https://github.com/conjure-up/conjure-up/pull/75) ([mikemccracken](https://github.com/mikemccracken))
- add steps logic, few drive by fixes [\#71](https://github.com/conjure-up/conjure-up/pull/71) ([battlemidget](https://github.com/battlemidget))
- point lxdsetup at right next controller [\#70](https://github.com/conjure-up/conjure-up/pull/70) ([mikemccracken](https://github.com/mikemccracken))
- add util script to graph controller code paths [\#68](https://github.com/conjure-up/conjure-up/pull/68) ([mikemccracken](https://github.com/mikemccracken))
- Fixes \#66 [\#67](https://github.com/conjure-up/conjure-up/pull/67) ([battlemidget](https://github.com/battlemidget))
- Fixes \#57 [\#64](https://github.com/conjure-up/conjure-up/pull/64) ([battlemidget](https://github.com/battlemidget))
- Patch charmstore to search var [\#62](https://github.com/conjure-up/conjure-up/pull/62) ([battlemidget](https://github.com/battlemidget))
- Load gui for single spells [\#61](https://github.com/conjure-up/conjure-up/pull/61) ([battlemidget](https://github.com/battlemidget))
- fix keyerror if friendly-name not in metadata [\#60](https://github.com/conjure-up/conjure-up/pull/60) ([battlemidget](https://github.com/battlemidget))
- Add option editing to service walkthru view [\#59](https://github.com/conjure-up/conjure-up/pull/59) ([mikemccracken](https://github.com/mikemccracken))
- Chiz [\#58](https://github.com/conjure-up/conjure-up/pull/58) ([battlemidget](https://github.com/battlemidget))
- Improve readme parsing and fix crash on last svc [\#53](https://github.com/conjure-up/conjure-up/pull/53) ([mikemccracken](https://github.com/mikemccracken))
- \[WIP\] ui tweaks [\#52](https://github.com/conjure-up/conjure-up/pull/52) ([battlemidget](https://github.com/battlemidget))
- move finish controller to steps controller [\#50](https://github.com/conjure-up/conjure-up/pull/50) ([battlemidget](https://github.com/battlemidget))
- Patch post process fix [\#49](https://github.com/conjure-up/conjure-up/pull/49) ([battlemidget](https://github.com/battlemidget))
- Patch ui tweaks [\#48](https://github.com/conjure-up/conjure-up/pull/48) ([battlemidget](https://github.com/battlemidget))
- Only display first 20 lines of readme [\#46](https://github.com/conjure-up/conjure-up/pull/46) ([mikemccracken](https://github.com/mikemccracken))
- Controller cleanup [\#45](https://github.com/conjure-up/conjure-up/pull/45) ([battlemidget](https://github.com/battlemidget))
- Walkthrough view 2 [\#44](https://github.com/conjure-up/conjure-up/pull/44) ([mikemccracken](https://github.com/mikemccracken))
- Give deploy done control to the bundle authors [\#74](https://github.com/conjure-up/conjure-up/pull/74) ([battlemidget](https://github.com/battlemidget))

## [0.1.2](https://github.com/conjure-up/conjure-up/tree/0.1.2) (2016-05-26)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.2.0...0.1.2)

**Fixed bugs:**

- conjure-up install keeps running even after install fails [\#13](https://github.com/conjure-up/conjure-up/issues/13)
- launching VM via horizon:  No Valid host was found.  There are not enough Hosts available  [\#11](https://github.com/conjure-up/conjure-up/issues/11)

**Closed issues:**

- conjure-up still not working [\#12](https://github.com/conjure-up/conjure-up/issues/12)
- ERROR loading credentials: credentials.maas.ryker.maas-oauth: expected string, got nothing [\#10](https://github.com/conjure-up/conjure-up/issues/10)

**Merged pull requests:**

- log full exceptions [\#34](https://github.com/conjure-up/conjure-up/pull/34) ([mikemccracken](https://github.com/mikemccracken))
- fix config hack to work with tox devmode [\#33](https://github.com/conjure-up/conjure-up/pull/33) ([mikemccracken](https://github.com/mikemccracken))
- Add travis [\#32](https://github.com/conjure-up/conjure-up/pull/32) ([mikemccracken](https://github.com/mikemccracken))
- use conf file from source dir if not installed [\#19](https://github.com/conjure-up/conjure-up/pull/19) ([mikemccracken](https://github.com/mikemccracken))
- tweaks [\#18](https://github.com/conjure-up/conjure-up/pull/18) ([battlemidget](https://github.com/battlemidget))
- Check multiple locations to download spells [\#17](https://github.com/conjure-up/conjure-up/pull/17) ([battlemidget](https://github.com/battlemidget))
- Patch headless [\#16](https://github.com/conjure-up/conjure-up/pull/16) ([battlemidget](https://github.com/battlemidget))

## [0.2.0](https://github.com/conjure-up/conjure-up/tree/0.2.0) (2016-04-27)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.8...0.2.0)

**Merged pull requests:**

- Hide stderr on pre and postproc scripts [\#7](https://github.com/conjure-up/conjure-up/pull/7) ([mikemccracken](https://github.com/mikemccracken))
- retry on json errors [\#6](https://github.com/conjure-up/conjure-up/pull/6) ([mikemccracken](https://github.com/mikemccracken))

## [0.0.8](https://github.com/conjure-up/conjure-up/tree/0.0.8) (2016-04-16)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.7...0.0.8)

## [0.0.7](https://github.com/conjure-up/conjure-up/tree/0.0.7) (2016-04-11)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/0.0.6...0.0.7)

**Merged pull requests:**

- send more detailed status about deploys [\#5](https://github.com/conjure-up/conjure-up/pull/5) ([mikemccracken](https://github.com/mikemccracken))

## [0.0.6](https://github.com/conjure-up/conjure-up/tree/0.0.6) (2016-03-24)
**Merged pull requests:**

- add ackrc to make searching better [\#3](https://github.com/conjure-up/conjure-up/pull/3) ([mikemccracken](https://github.com/mikemccracken))
- make pollinate calls asynchronous [\#2](https://github.com/conjure-up/conjure-up/pull/2) ([mikemccracken](https://github.com/mikemccracken))
- Add calls to pollinate [\#1](https://github.com/conjure-up/conjure-up/pull/1) ([mikemccracken](https://github.com/mikemccracken))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*