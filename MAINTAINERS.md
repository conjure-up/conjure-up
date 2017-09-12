# Maintainers

This document describes our release process

## New major releases

Each new major release will be branched from master and named
`<major.minor.patch>` version. For example, we release a new major version of
`2.4.0` we would branch off master and name it `2.4`. We don't include the patch
version here as we will push those patch release version to this same branch.

### Prepare

Prepare the necessary files for a new release.

1. Update `Makefile` and change the `VERSION` variable to reflect the new version.

```
#
# Makefile for conjure
#
NAME = conjure-up
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)

# Update the VERSION number here
VERSION := 2.4.0

CHANNEL := edge
```

2. Run `make update-version`. This will update all the necessary files to reflect the new version.

3. Prepare `snap/snapcraft.yaml`.

Our build process includes external sources such as Juju and a spells
repository. conjure-up master branch always tracks Juju's `develop` branch,
however, when cutting a new release we want to make sure we're using one of
Juju's stable releases. To determine this go to https://github.com/juju/juju/releases and pick the
latest release (2.2.3 at the time of this writing).

Once a release is selected update `snap/snapcraft.yaml` to reflect that:

```
  juju:
    source: https://github.com/juju/juju.git
    source-type: git
    source-tag: "juju-2.2.3"
    source-depth: 1
    plugin: godeps
    go-importpath: github.com/juju/juju
    go-packages:
      - github.com/juju/juju/cmd/juju
      - github.com/juju/juju/cmd/jujud
    install: |
      mkdir -p $SNAPCRAFT_PART_INSTALL/bash_completions
      cp -a etc/bash_completion.d/juju* $SNAPCRAFT_PART_INSTALL/bash_completions/.
    build-packages: [lsb-release]
    after: [conjure-up, go]
```

### Tagging

Once preparation is done tag the branch with the new release: `git tag 2.4 && git push --tags`

### Packaging

Launchpad is where packages are built, and a git remote exists as well:

```
git remote add lp git+ssh://git.launchpad.net/conjure-up
```

Once the remote is added, you'll want to `git push lp 2.4` so that Launchpad
will have the release branch.

Next, we map the Launchpad snap builders with the release branch, so for a
`2.4.0` release we want to create a snap package with this link
https://code.launchpad.net/~conjure-up/conjure-up/+git/conjure-up/+ref/2.4/+new-snap.
You can set it to automatically build when the repo changes and the channel
should be `candidate`.

Once the build is finished it will automatically upload the snap package to the
candidate channel in the snap store.

### Testing and Releasing

Our QA team needs to be notified that a new release is available in the
`candidate` channel so they can perform their validation tests.

Once QA gives the OK, go to the snap store page for `conjure-up`
https://dashboard.snapcraft.io/dev/snaps/5479/ and select the upload of the
candidate snap, for example,
https://dashboard.snapcraft.io/dev/snaps/5479/rev/719/.

From there, click the **Release** link beside **Channels** and select the
**Stable** channel. The snap store will publish conjure-up to the stable channel
for the rest of the world to consume.

## Patch releases

For patch release the above applies with the following differences.

1. Code is cherry picked from master into the release branch.
2. The `Makefile` version should reflect the next patch release (ie 2.4.1)
3. `make update-version` to reflect the patch version change
4. Update Juju version in `snap/snapcraft.yaml` if a new stable release is available.
5. Apply a git tag `git tag 2.4.1`
6. Then push to Launchpad release branch `git push lp 2.4`

Launchpad will then kick off a build and upload to the candidate channel in the
snap store. Proceed through the QA process and release as outlined above.
