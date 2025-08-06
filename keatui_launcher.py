import urwid
from keatui.reservation_view_urwid import ReservationView
from keatui.lease_view_urwid import LeaseView
from keatui.subnet_editor_urwid import SubnetEditor
from keatui.global_options_urwid import GlobalOptionsView
from keatui.control_agent_urwid import ControlAgentView

class KeaTUILauncher:
    def __init__(self):
        self.context = {
            'kea_host': 'localhost',
            'kea_port': 8000
        }
        self.main_menu()

    def main_menu(self):
        options = [
            ('Reservations', self.show_reservations),
            ('Leases', self.show_leases),
            ('Subnet Editor', self.show_subnets),
            ('Global Options', self.show_globals),
            ('Control Agent Tools', self.show_agent_tools),
            ('Quit', self.exit_app),
        ]
        menu_items = [urwid.Button(label, on_press=lambda btn, cb=cb: cb()) for label, cb in options]
        self.menu = urwid.LineBox(urwid.ListBox(urwid.SimpleFocusListWalker(menu_items)), title="KeaTUI Main Menu")
        self.loop = urwid.MainLoop(self.menu, unhandled_input=self.handle_keys)
        self.loop.run()

    def handle_keys(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def show_view(self, view_cls):
        view = view_cls(self.context, self.return_to_menu)
        self.loop.widget = view.body

    def return_to_menu(self, msg):
        self.loop.widget = self.menu

    def show_reservations(self):
        self.show_view(ReservationView)

    def show_leases(self):
        self.show_view(LeaseView)

    def show_subnets(self):
        self.show_view(SubnetEditor)

    def show_globals(self):
        self.show_view(GlobalOptionsView)

    def show_agent_tools(self):
        self.show_view(ControlAgentView)

    def exit_app(self):
        raise urwid.ExitMainLoop()

if __name__ == "__main__":
    KeaTUILauncher()
