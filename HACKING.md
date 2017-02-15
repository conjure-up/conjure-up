# Getting a development environment started

0. clone the repo
1. `make git-sync-requirements`
2. `make dev`
3. `source conjure-dev/bin/activate`
3. `make test`

# Check tests before submitting a PR

While the unit test suite coverage is low enough that most changes
won't affect the test results (yes this is bad), the Travis test suite
checks lint, so it's a good idea to run the tests anyway before submitting:

```
% make test
```

If you see isort or pep8 errors, e.g. due to imports being out of
order, fix it automatically with this:

```
% make auto-format
```

# Release procedures
TODO - need more details on version updates, etc.

## Building the snap

```
% make release-snap
```
