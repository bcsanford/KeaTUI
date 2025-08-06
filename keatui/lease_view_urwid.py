import urwid
import requests

def fetch_leases(host, port, service='dhcp4'):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={"command": "lease4-get-all", "service": service})
        return response.json().get("arguments", {}).get("leases", [])
    except Exception as e:
        return [{"error": str(e)}]

class LeaseView:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.service = 'dhcp4'
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("Press 'Fetch Leases' to load data")
        self.service_toggle = urwid.RadioButton([], "IPv4", state=True, on_state_change=self.set_service, user_data='dhcp4')
        self.service_toggle_v6 = urwid.RadioButton([self.service_toggle], "IPv6", on_state_change=self.set_service, user_data='dhcp6')

        fetch_btn = urwid.Button("Fetch Leases", on_press=self.fetch_and_display)
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Back"))

        return urwid.LineBox(
            urwid.Pile([
                urwid.Columns([self.service_toggle, self.service_toggle_v6]),
                urwid.Columns([fetch_btn, back_btn]),
                urwid.Divider(),
                self.output
            ]),
            title="DHCP Leases"
        )

    def set_service(self, button, new_state, user_data):
        if new_state:
            self.service = user_data

    def fetch_and_display(self, _):
        leases = fetch_leases(self.context['kea_host'], self.context['kea_port'], self.service)
        if isinstance(leases, list):
            lines = []
            for lease in leases:
                line = f"IP: {lease.get('ip-address')} | MAC: {lease.get('hw-address', 'N/A')} | State: {lease.get('state', '')}"
                lines.append(line)
            self.output.set_text("\n".join(lines) if lines else "No leases found.")
        else:
            self.output.set_text(str(leases))
