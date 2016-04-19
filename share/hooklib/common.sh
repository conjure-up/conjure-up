# common.sh - common utility functions for conjure processing tasks

# Path to executing script
SCRIPT=$(realpath $0)

# Directory housing script
SCRIPTPATH=$(dirname $SCRIPT)

# loggers
#
# Arguments:
# $1: logger name, ie. openstack, bigdata
# $@: rest of log message
debug() {
    name=$1
    shift 1
    logger -t "$name" "[DEBUG] $@"
}

info() {
    name=$1
    shift 1
    logger -t "$name" "[INFO] $@"
}

# Gets current juju state for machine
#
# Arguments:
# $1: service name
#
# Returns:
# machine status
agentState()
{
    juju status --format json | jq ".machines[\"$1\"][\"juju-status\"][\"current\"]"
}

# Gets current workload state for service
#
# Arguments:
# $1: service name
# $2: unit number
#
# Returns:
# unit status
agentStateUnit()
{
    juju status --format json | jq ".services[\"$1\"][\"units\"][\"$1/$2\"][\"workload-status\"][\"current\"]"
}

# Exports the variables required for communicating with your cloud.
#
# Arguments:
# $1: username
# $2: password
# $3: tenant name
# $4: keystone auth url
# $5: region name
configOpenrc()
{
    export OS_USERNAME=$1
    export OS_PASSWORD=$2
    export OS_TENANT_NAME=$3
    export OS_AUTH_URL=$4
    export OS_REGION_NAME=$5
}

# Get public address of unit
#
# Arguments:
# $1: service
# $2: unit number
#
# Returns:
# IP Address of unit
unitAddress()
{
    juju status --format json | jq -r ".services[\"$1\"][\"units\"][\"$1/$2\"][\"public-address\"]"
}

# Get status of unit
#
# Arguments:
# $1: service
# $2: unit number
#
# Returns:
# String of status
unitStatus()
{
    juju status --format json | jq -r ".services[\"$1\"][\"units\"][\"$1/$2\"][\"workload-status\"][\"current\"]"
}

# Get machine for unit, ie 0/lxc/1
#
# Arguments:
# 1: service
# 2: unit number
#
# Returns:
# machine identifier
unitMachine()
{
    juju status --format json | jq -r ".services[\"$1\"][\"units\"][\"$1/$2\"][\"machine\"]"
}

# Waits for machine to start
#
# Arguments:
# machine: machine number
waitForMachine()
{
    for machine; do
        while [ "$(agentState $machine)" != started ]; do
            sleep 5
        done
    done
}

# Waits for service to start
#
# Arguments:
# service: service name
waitForService()
{

    for service; do
        while [ "$(agentStateUnit "$service" 0)" != active ]; do
            sleep 5
        done
    done
}

# Parses result into json output
#
# Arguments:
# $1: return message
# $2: return code
# $3: true/false
exposeResult()
{
    printf '{"message": "%s", "returnCode": %d, "isComplete": %s}' "$1" $2 "$3"
}
