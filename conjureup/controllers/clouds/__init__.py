""" clouds controller

This is the public cloud selection and the entrypoint into conjure-up.

This view presents the user with a list of available clouds that have been
whitelisted by the spell and then can be deployed.

Once a cloud is selected, credentials for that cloud will be queried and if not
found a credentials view will be presented. If credentials already exist for
that cloud then the view will go directly to the next view.

This should also check to see if any existing controllers are available that
satisfy the selected cloud. If so then those controllers are used instead of
doing a bootstrap to a new cloud/controller.
"""
