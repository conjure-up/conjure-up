# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from jinja2 import FileSystemLoader, Environment, exceptions
from .utils import FS
from tempfile import NamedTemporaryFile
import logging
import os
import yaml

log = logging.getLogger('template')


def render_charm_conf(name, options):
    """ Render a yaml config suitable for charm deployment

    Arguments:
    name: service/charm name
    options: dictionary of config options and their values

    Returns:
    Path to charm config file
    """
    ctx = dict(name=options)
    with NamedTemporaryFile(mode='w+', encoding='utf-8') as tempf:
        tempf.write(yaml.dump(ctx, default_flow_style=False))
        return tempf.name


def render(source, target, context, owner='root', group='root',
           perms=0o444, templates_dir=None, encoding='UTF-8',
           template_loader=None):
    """
    Render a template.

    The `source` path, if not absolute, is relative to the `templates_dir`.

    The `target` path should be absolute.

    The context should be a dict containing the values to be replaced in the
    template.

    The `owner`, `group`, and `perms` options will be passed to `write_file`.

    If omitted, `templates_dir` defaults to the `templates` folder in the
    charm.

    Note: Using this requires python-jinja2; if it is not installed, calling
    this will attempt to use charmhelpers.fetch.apt_install to install it.
    """

    if template_loader:
        template_env = Environment(loader=template_loader)
    else:
        if templates_dir is None:
            templates_dir = 'templates'
        template_env = Environment(loader=FileSystemLoader(templates_dir))
    try:
        source = source
        template = template_env.get_template(source)
    except exceptions.TemplateNotFound as e:
        log.error('Could not load template {} from {}.'.format(source,
                                                               templates_dir))
        raise e
    content = template.render(context)
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        # This is a terrible default directory permission, as the file
        # or its siblings will often contain secrets.
        os.makedirs(os.path.dirname(target))
    FS.spew(target, content)
