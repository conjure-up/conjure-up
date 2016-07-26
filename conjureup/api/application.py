""" application api
"""

from conjureup import juju
from .models import model_status


@juju.requires_login
def get_workload_statuses():
    """ gather application workload statuses from all agents

    Returns:
    List of all units status
    """
    apps = model_status()['applications']
    units = []
    for k, v in apps.items():
        if v['units'] is None:
            continue
        for a, b in v['units'].items():
            units.append(b['workload-status']['status'])
    return units
