from conjureup import events, utils


class Destroy:
    def render(self):
        utils.error("Please run `conjure-down` without any arguments.")
        events.Shutdown.set(0)


_controller_class = Destroy
