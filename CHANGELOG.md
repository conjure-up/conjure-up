# Change Log

## [2.2.1](https://github.com/conjure-up/conjure-up/tree/2.2.1) (2017-06-20)
[Full Changelog](https://github.com/conjure-up/conjure-up/compare/2.2.0...2.2.1)

**Implemented enhancements:**

- make use of lxd preseed init data [\#949](https://github.com/conjure-up/conjure-up/issues/949)
- Add Sentry support for tracking errors [\#931](https://github.com/conjure-up/conjure-up/issues/931)

**Fixed bugs:**

- can not select existing controller to deploy to [\#950](https://github.com/conjure-up/conjure-up/issues/950)
- TypeError 'NoneType' object is not subscriptable [\#946](https://github.com/conjure-up/conjure-up/issues/946)
- failed to set lxc config [\#943](https://github.com/conjure-up/conjure-up/issues/943)
- Failed to create LXD conjureup1 network bridge: error: Failed to run: dnsmasq --strict-order --bind-interfaces [\#942](https://github.com/conjure-up/conjure-up/issues/942)
- hooklib.writer log needs update [\#938](https://github.com/conjure-up/conjure-up/issues/938)
- Exception: Unable to determine controller: ERROR controller conjure-up-controller not found [\#937](https://github.com/conjure-up/conjure-up/issues/937)
- JSONDecodeError: Expecting value: line 1 column 2 \(char 1\) [\#935](https://github.com/conjure-up/conjure-up/issues/935)
- Error Deploying Openstack: Could not find a suitable network interface... with NovaLXD in a nested LXD  [\#916](https://github.com/conjure-up/conjure-up/issues/916)
- Stuck on "Waiting For Applications To Start" with NovaLXD in a nested LXD [\#915](https://github.com/conjure-up/conjure-up/issues/915)

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
- use state server for handling step results [\#910](https://github.com/conjure-up/conjure-up/issues/910)
- add redis for state caching and step-2-step intercommunication [\#901](https://github.com/conjure-up/conjure-up/issues/901)
- Update screen selection/ordering [\#897](https://github.com/conjure-up/conjure-up/issues/897)
- allow user to select a model on a controller to deploy to [\#753](https://github.com/conjure-up/conjure-up/issues/753)
- should spell steps have conditions based on cloud provider [\#633](https://github.com/conjure-up/conjure-up/issues/633)
- look into dealing with existing credentials [\#545](https://github.com/conjure-up/conjure-up/issues/545)
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
- Add support for channels [\#556](https://github.com/conjure-up/conjure-up/issues/556)
- \[release-process\] gate bundles on successful conjure-up deploy [\#555](https://github.com/conjure-up/conjure-up/issues/555)
- Support OSX [\#549](https://github.com/conjure-up/conjure-up/issues/549)

**Fixed bugs:**

- MAAS provider line asks for URL http:IP:port/MAAS but inserts the /MAAS into that URL  [\#925](https://github.com/conjure-up/conjure-up/issues/925)
- traceback with application facade [\#924](https://github.com/conjure-up/conjure-up/issues/924)
- Hadoop-spark bundle calls a charm version not available \(hadoop-plugin-21\) [\#918](https://github.com/conjure-up/conjure-up/issues/918)
- make sure MTU 1500 is set for lxd profiles [\#904](https://github.com/conjure-up/conjure-up/issues/904)
- syncing spell repository: handle git related conflicts better [\#813](https://github.com/conjure-up/conjure-up/issues/813)
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
- Snap install conjure-up doesn't work if juju is installed [\#719](https://github.com/conjure-up/conjure-up/issues/719)
- conjure-up continue operations [\#624](https://github.com/conjure-up/conjure-up/issues/624)
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
- Feature/910 enable redis state server [\#911](https://github.com/conjure-up/conjure-up/pull/911) ([battlemidget](https://github.com/battlemidget))
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

**Closed issues:**

- bad error for invalid path to spell [\#429](https://github.com/conjure-up/conjure-up/issues/429)
- app config screen match wireframe - fixed footer charm description [\#422](https://github.com/conjure-up/conjure-up/issues/422)
- no way to tell conjure-up where to bootstrap to [\#420](https://github.com/conjure-up/conjure-up/issues/420)
- can't edit unit count [\#418](https://github.com/conjure-up/conjure-up/issues/418)
- make conjure-up work on trusty [\#389](https://github.com/conjure-up/conjure-up/issues/389)

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

**Closed issues:**

- applicationlist - dont show configure button if subordinate [\#415](https://github.com/conjure-up/conjure-up/issues/415)
- controllerpicker: filter blacklist/whitelist [\#413](https://github.com/conjure-up/conjure-up/issues/413)
- attributeerror with controllerpicker [\#410](https://github.com/conjure-up/conjure-up/issues/410)

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

**Closed issues:**

- split clouds view for existing public clouds and creating new clouds [\#395](https://github.com/conjure-up/conjure-up/issues/395)
- pressing deploy all should removes the \[configure\]\[deploy\] buttons [\#381](https://github.com/conjure-up/conjure-up/issues/381)
- snap install issue -- snap.conjure-up.bridge.service failed [\#376](https://github.com/conjure-up/conjure-up/issues/376)
- spells not sorted in spellpicker view [\#374](https://github.com/conjure-up/conjure-up/issues/374)
- conjure-up \<spell\> tracebacks [\#371](https://github.com/conjure-up/conjure-up/issues/371)
- if no clouds are whitelisted \(e.g. openstack-novalxd spell\), an empty list is shown in the newcloud view [\#405](https://github.com/conjure-up/conjure-up/issues/405)

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
- Fixes \#402 [\#407](https://github.com/conjure-up/conjure-up/pull/407) ([battlemidget](https://github.com/battlemidget))
- Fixes \#405 [\#406](https://github.com/conjure-up/conjure-up/pull/406) ([battlemidget](https://github.com/battlemidget))
- add journald logging [\#398](https://github.com/conjure-up/conjure-up/pull/398) ([battlemidget](https://github.com/battlemidget))

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