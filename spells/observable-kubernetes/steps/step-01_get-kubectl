#!/bin/bash

. /usr/share/conjure-up/hooklib/common.sh

KUBECTL_PATH=$HOME/conjure-up/kubernetes
mkdir -p $KUBECTL_PATH || true

# TODO: Convert to an actionable item
leaderUnit=$(getLeader kubernetes)
debug "Found leader: $leaderUnit"
juju scp $leaderUnit:kubectl_package.tar.gz $KUBECTL_PATH/.
cd $KUBECTL_PATH && tar zxf kubectl_package.tar.gz

exposeResult "Cluster can now be accessed with $KUBECTL_PATH/kubectl application" 0 "true"
