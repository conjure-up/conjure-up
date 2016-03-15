# Copyright 2015 Canonical, Ltd.
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

import argparse
import logging
import os
import sys
import urwid

from bundleplacer import async
from bundleplacer.maas import connect_to_maas

from bundleplacer.config import Config
from bundleplacer.controller import BundleWriter, PlacementController
from bundleplacer.log import setup_logger
from bundleplacer.placerview import PlacerView
from bundleplacer.fixtures.maas import FakeMaasState
from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
from ubuntui.anchors import Header, Footer

log = None


class PlacerUI(urwid.Frame):
    def __init__(self, placerview):
        super().__init__(body=placerview, header=Header(), footer=Footer())


def parse_options(argv):
    parser = argparse.ArgumentParser(description='Juju Bundle Placer',
                                     prog='placer',
                                     argument_default=argparse.SUPPRESS)
    parser.add_argument("bundle_filename", metavar='bundle',
                        help="Bundle file to edit")
    parser.add_argument("--metadata", dest="metadata_filename",
                        metavar='metadatafile',
                        help="Optional metadata file describing constraints "
                        "on services in bundle")
    parser.add_argument("--fake-maas", dest="fake_maas",
                        action="store_true", default=False)
    parser.add_argument("--maas-ip", dest="maas_ip", default=None)
    parser.add_argument("--maas-cred", dest="maas_cred", default=None)
    parser.add_argument("-o", dest="out_filename", default=None)
    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    config = Config('bundle-placer', opts.__dict__)
    config.save()

    setup_logger(cfg_path=config.cfg_path)
    log = logging.getLogger('bundleplacer')
    log.debug(opts.__dict__)

    log.info("Editing file: {}".format(opts.bundle_filename))

    if opts.maas_ip and opts.maas_cred:
        creds = dict(api_host=opts.maas_ip,
                     api_key=opts.maas_cred)
        maas, maas_state = connect_to_maas(creds)
    elif opts.fake_maas:
            maas = None
            maas_state = FakeMaasState()
    else:
        maas = None
        maas_state = None

    placement_controller = PlacementController(config=config,
                                               maas_state=maas_state)

    def cb():
        if maas:
            maas.tag_name(maas.nodes)

        bw = BundleWriter(placement_controller)
        if opts.out_filename:
            outfn = opts.out_filename
        else:
            path, ext = os.path.splitext(opts.bundle_filename)
            outfn = "{}-out{}".format(path, ext)
        bw.write_bundle(outfn)
        async.shutdown()
        raise urwid.ExitMainLoop()

    has_maas = (maas_state is not None)
    mainview = PlacerView(placement_controller, config, cb, has_maas=has_maas)
    ui = PlacerUI(mainview)

    def unhandled_input(key):
        if key in ['q', 'Q']:
            async.shutdown()
            raise urwid.ExitMainLoop()
    EventLoop.build_loop(ui, STYLES, unhandled_input=unhandled_input)
    mainview.loop = EventLoop.loop
    mainview.update()
    EventLoop.run()
