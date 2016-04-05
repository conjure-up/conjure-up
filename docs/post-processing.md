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

* `pre.sh` - This is a special case where you will be deploying to a LXD
  controller and need to do alterations to the controllers for things like
  adding additional network interfaces for neutron, or loading specific kernel
  modules, etc. Basic checks are in place to not run the lxd script on
  controllers that aren't lxd, however, anything other than that is up to the
  user. **Note**: this will apply to all containers.
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
    "returnCode": 127
}
```

### Communicating with the UI

The UI will display any relevant messages from the return output of the `post.sh` script.
