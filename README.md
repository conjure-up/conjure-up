# conjure-up [![Build Status](https://travis-ci.org/conjure-up/conjure-up.svg?branch=master)](https://travis-ci.org/conjure-up/conjure-up)
> Installing big software like whoa.

# what it is

Ever wanted to get started with Kubernetes, Deep Learning, Big Data but didn't want
to go through pages and pages of "Getting Started" documentation?

Then **conjure-up** is for you!

This is the runtime application for processing spells to get those **big software**
solutions up and going with as little hindrance as possible.

# installation

> Ubuntu and macOS

## Ubuntu

```
$ sudo snap install conjure-up --classic
```

## macOS

```
$ brew install conjure-up
```

# how to use

## Run the installer interactively

You may want to learn a little bit about what you're installing, right? This
method provides you with a tutorial like approach without being overburdening.

You can read through descriptions of the software along with ability to set a
few config options before deploying. Or, just hold down the enter button and
it'll choose sensible defaults for you.

```
$ conjure-up
```

## Run the installer non-interactively (headless mode)

Already been through the guided tour? Not keen on holding down the enter button
on your keyboard? Not a problem, easily get your **big software** up and running
with all the sensible defaults in place.

```
$ conjure-up canonical-kubernetes localhost
```

Note that some spells require sudo for certain steps.  When running in headless
mode, conjure-up should be run with a user with passwordless sudo enabled (or
sudo should be pre-authorized before invoking conjure-up).

## Destroying deployments

```
$ conjure-down
```

# authors

* Adam Stokes <adam.stokes@ubuntu.com>
* Mike McCracken <mike.mccracken@canonical.com>
* Cory Johns <cory.johns@canonical.com>

# license

The MIT License (MIT)

* Copyright (c) 2015-2019 Canonical Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
