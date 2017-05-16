from conjureup.ui.views.base import SchemaFormView


class LXDSetupView(SchemaFormView):
    title = "LXD Setup"
    subtitle = "LXD Network Setup"
    header = "Select a physical network device for your LXD bridge:"
