## Purpose

Add ability to customize charm deployments through a post processing mechanism.

### Directory Layout

```
/usr/share/openstack/
   - landscape-dense-maas(bundle)
      - pre.sh
      - post.sh
```

### Files

Each directory will be defined by a bundle key found in `config.json` beneath
that will contain each known charm as defined by an existing bundle. Beneath
those charm directories will contain files to alter the state of deployment and
customize the charm being deployed.

* `pre.sh` - Runs regardless, passing in the controller type. Useful if you need to
apply an updated profile to the LXD type.

* `post.sh` - Perform post actions after the charm(s) have been deployed. Useful for
configuring things like registering against Autopilot and returning a URL to
the user for further installation. The script can be re-run several times in
instances where services may not be fully up at the same time.

The script can do things like the following (by no means limited to just these tasks):
* Set config items via juju get/set
* copy files into machines housing the services
* run scripts inside machines for additional configuration needs

The post processing script should follow these guidelines:
* should be run many times without fail
* skips whatever is done
* Returns json output from stdout to be parsed and reported back to the UI

The output returned from the script should be in the format of:

```json
{
    "message": "A success/fail message",
    "postStatus": "Unfinished",
    "returnCode": $?
}
```

Definitions:
* message: A typical string describing the outcome of the script
* postStatus: A conjure specific return letting the queue know if the script needs to run again or has finished.
* returnCode: Return code of the processes exit code from within the script

### Communicating with the UI

The UI will display any relevant messages from the return output of the `post.sh` script.
