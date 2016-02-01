# Copyright 2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Represents a Juju service """


class JujuUnitNotFoundException(Exception):

    """ Unable to find a matching Unit """


class Unit:

    """ Unit class """

    def __init__(self, unit_name, unit):
        self.unit_name = unit_name
        self.unit = unit

    @property
    def agent_state(self):
        """ Unit's agent state

        :returns: agent state
        :rtype: str
        """
        return self.unit.get('AgentState', 'unknown')

    @property
    def workload_state(self):
        return self.unit.get('Workload', {}).get('Status', '')

    @property
    def extended_agent_state(self):
        return self.unit.get('UnitAgent', {}).get('Status', '')

    @property
    def workload_info(self):
        return self.unit.get('Workload', {}).get('Info', '')

    @property
    def machine_id(self):
        """ Associate machine for unit

        :returns: machine id
        :rtype: str
        """
        return self.unit.get('Machine', '-1')

    @property
    def public_address(self):
        """ Public address of unit

        :returns: address of unit
        :rtype: str
        """
        return self.unit.get('PublicAddress', None)

    @property
    def agent_state_info(self):
        """ Gets unit state info

        Usually prints a error message if unit failed to deploy
        :returns: error
        :rtype: str
        """
        return self.unit.get('AgentStateInfo', None)

    @property
    def is_cloud_controller(self):
        """ Is machine housing the cloud-controller?

        :returns: True/False
        :rtype: bool
        """
        return 'nova-cloud-controller' in self.unit_name

    def __repr__(self):
        return "<Unit: {name}, Machine: {machine}, State: {state}>".format(
            name=self.unit_name,
            machine=self.machine_id,
            state=self.agent_state)


class Relation:

    """ Relation class """

    def __init__(self, relation_name, charms):
        self.relation_name = relation_name
        self.charms = charms

    def is_relation(self, charm):
        """ Is a charm already related? """
        return charm in self.charms

    def __repr__(self):
        return "<Relation: {name}, {charms}>".format(name=self.relation_name,
                                                     charms=self.charms)


class Service:

    """ Service class """

    def __init__(self, service_name, service):
        self.service_name = service_name
        self.service = service
        self.charm = self.service.get('Charm')
        self.exposed = self.service.get('Exposed')
        self.networks = self.service.get('Networks')
        self.life = self.service.get('Life')

    def unit(self, name):
        """ Single unit entry

        :params str name: name of unit
        :returns: a Unit entry
        :rtype: Unit()
        """
        def _match(unit):
            if name in unit.unit_name:
                return True
            return False
        try:
            return next(filter(_match, self.units))
        except:
            raise JujuUnitNotFoundException("Could not find matching "
                                            "unit: {}".format(name))

    @property
    def units(self):
        """ Service units

        :returns: iterator of associated units for service
        :rtype: Unit()
        """
        units_list = []
        units_dict = self.service.get('Units', {})
        if units_dict is None:
            return units_list

        for unit_name, units in units_dict.items():
            units_list.append(Unit(unit_name, units))
        return units_list

    def relation(self, name):
        """ Single relation entry

        :params str name: name of relation
        :returns: a Relation entry
        :rtype: Relation()
        """
        r = next(filter(lambda r: r.relation_name == name,
                        self.relations),
                 Relation('unknown', []))
        return r

    @property
    def relations(self):
        """ Service relations

        :returns: iterator of relations for service
        :rtype: Relation()
        """
        relations = self.service.get('Relations', {})
        for relation_name, relation in relations.items():
            yield Relation(relation_name, relation)

    def __repr__(self):
        return "<Service: {name} " \
            "Units: {units}>".format(name=self.service_name,
                                     units=list(self.units))
