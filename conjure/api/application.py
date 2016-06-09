""" application api
"""

from conjure import juju
from .models import model_status


@juju.requires_login
def get_workload_statuses():
    """ gather application workload statuses from all agents

    Returns:
    List of all units status
    """
    apps = model_status()['Applications']
    units = []
    for k, v in apps.items():
        if v['Units'] is None:
            continue
        for a, b in v['Units'].items():
            units.append(b['WorkloadStatus']['Status'])
    return units
