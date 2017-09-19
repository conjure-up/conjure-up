# Testing

This document describes our current testing process.

> Currently this covers deploying of spells via conjure-up which includes making
> sure all applications relate and are in a ready state. Further documentation is
> needed to outline how further testing is done to validate those deployments.

# GitHub Pull Requests

Each PR is both unit tested and functionally tested using https://travis-ci.org.
`conjure-up` is ran against a localhost(LXD) provider and the ghost spell.

Versions of underlying software used:

- Juju alpha (from their develop branch)
- LXD stable (from snap store stable channel)

# Nightly CI Runs

Nightly spell deployments using `conjure-up` snap and the localhost provider.
These deployments cover canonical-kubernetes, openstack-novalxd, hadoop-kafka,
and hadoop-spark.

Versions of underlying software used:

- Juju alpha (from their develop branch, bundled with conjure-up)
- LXD stable (from snap store stable channel)

# Canonical Solutions QA Engineering

The QA engineering team handles the final vetting of `conjure-up` just before a
stable release is cut. Currently, their tests include:

## MAAS

- kubernetes-core
- canonical-kubernetes
- hadoop-spark

## Localhost

- openstack-novalxd

## VSphere

- canonical-kubernetes

Versions of underlying software used:

- conjure-up from candidate snap channel
- Juju stable (bundled with conjure-up)
- LXD stable (from snap store stable channel)

# Manual Maintainer Runs

Current developers and maintainers will also run through all spells but
openstack-novalxd on AWS.

Versions of underlying software used:

- conjure-up from edge and stable
- Juju edge/stable releases (bundled with conjure-up)

# Automation

We have a few scripts written that help facilitate the deployment tests found in
https://github.com/conjure-up/conjure-up-tests.
