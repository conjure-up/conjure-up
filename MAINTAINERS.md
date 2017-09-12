# Maintainers

This document describes our release process

## New major releases

Each new major release will be branched from master and named
`<major.minor.patch>` version. For example, we release a new major version of
`2.4.0` we would branch off master and name it `2.4`. We don't include the patch
version here as we will push those patch release version to this same branch.

### Prepare

Prepare the necessary files for a new release.

1. Update the `VERSION` file to reflect the new version.

2. Update the `JUJU_VERSION` file with the branch or tag name to use for Juju.
   Generally, this should be the latest stable release tag from https://github.com/juju/juju/releases
   but conjure-up master always tracks the `develop` branch.

3. Run `make update-version`. This will update all the necessary files to reflect the new versions.

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
2. The `VERSION` file should reflect the next patch release (ie 2.4.1)
3. Update `JUJU_VERSION` file if a new stable release is available.
4. `make update-version` to reflect the patch version change
5. Apply a git tag `git tag 2.4.1`
6. Then push to Launchpad release branch `git push lp 2.4`

Launchpad will then kick off a build and upload to the candidate channel in the
snap store. Proceed through the QA process and release as outlined above.
