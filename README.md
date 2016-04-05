# conjure
> Installing cloud packages like whoa.

# what it is

This is the runtime application for processing juju bundles/charms for easier
installation via `apt-get install` and an install wizard.

# how to use

## Xenial and above

It is included in the archive.

## Wily and below

Packages are currently built for *Trusty* and *Wily*.
```
$ sudo apt-add-repository ppa:conjure/ppa
```

### Install the packages
```
$ sudo apt-get update
$ sudo apt-get install bigdata
```

### Run the installer
```
$ bigdata-install
```

# license

The MIT License (MIT)

* Copyright (c) 2015-2016 Canonical Ltd.
* Copyright (c) 2015-2016 Adam Stokes <adam.stokes@ubuntu.com>

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
