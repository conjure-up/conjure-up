from jinja2 import FileSystemLoader, Environment
from conjureup.utils import spew
from tempfile import NamedTemporaryFile
import yaml


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


def load(name, path):
    """ load template file
    :param str name: name of template file
    :param str path: directory location of templates
    """
    env = Environment(
        loader=FileSystemLoader(path))
    return env.get_template(name)


def save(template, opts):
    """ Saves template to temporary file

    Arguments:
    template: loaded jinja template
    opts: dictionary of items to be passed into template
    """
    modified = template.render(**opts)
    with NamedTemporaryFile(mode='w', encoding='utf-8',
                            delete=False) as tempf:
        spew(tempf.name, modified)
        return tempf.name
