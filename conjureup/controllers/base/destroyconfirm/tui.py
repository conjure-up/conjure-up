from conjureup import events, utils


class DestroyConfirm:

    def render(self):
        utils.error("You should not have gotten here, "
                    "please file a bug at "
                    "https://github.com/conjure-up/conjure-up/issues/new")
        events.Shutdown.set(1)


_controller_class = DestroyConfirm
