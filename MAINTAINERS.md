# Maintainers

This document describes our release process

## New major releases

Each new major release will be tagged from master and named
`<major.minor.patch>` version. For example, we release a new major version of
`2.4.0` we would tag master with `2.4.0`.

### Prepare

Prepare the necessary files for a new release.

1. Update the `VERSION` file to reflect the new version.

2. Update the `JUJU_VERSION` file with the branch or tag name to use for Juju.
   Generally, this should be the latest stable release tag from https://github.com/juju/juju/releases
   but conjure-up master always tracks the `develop` branch.

3. Run `make update-version`. This will update all the necessary files to reflect the new versions.

### Tagging

Once preparation is done tag the commit with the new release: `git tag 2.4.0 && git push --tags`

### Packaging

Launchpad is where packages are built, and a git remote exists as well:

```
git remote add lp git+ssh://git.launchpad.net/conjure-up
```

Once the remote is added, you'll want to `git push lp master` so that Launchpad
will have the release tags.

A build will automatically start and once finished it will automatically upload
the snap package to the edge channel in the snap store.

### Testing and Releasing

Once the tagged release is built in the snap store we promote it to 'beta' and
'candidate' channels.

Then our QA team needs to be notified that a new release is available in the
`candidate` channel so they can perform their validation tests.

Once QA gives the OK, go to the snap store page for `conjure-up`
https://dashboard.snapcraft.io/dev/snaps/5479/ and select the upload of the
candidate snap, for example,
https://dashboard.snapcraft.io/dev/snaps/5479/rev/719/.

From there, click the **Release** link beside **Channels** and select the
**Stable** channel. The snap store will publish conjure-up to the stable channel
for the rest of the world to consume.
