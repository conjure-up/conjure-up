#!/bin/bash

. /usr/share/conjure-up/hooklib/common.sh

dashboard_address() {
    unitAddress openstack-dashboard 0
}

exposeResult "Login to Horizon: http://$(dashboard_address)/horizon l: admin p: openstack" 0 "true"
