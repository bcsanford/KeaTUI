import urwid
import requests

def fetch_leases(host, port, subnet_id=None):
    url = f"http://{host}:{port}/"
    try:
        args = {} if subnet_id is None else {"subnet-id": subnet_id}
        response = requests.post(url, json={
            "command": "lease4-get-all",
            "service": "dhcp4",
            "arguments": args
        })
        return response.json().get("arguments", {}).get("leases", [])
    except Exception as e:
        return [f"Error: {e}"]

class LeaseView:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("")
        self.subnet_field = urwid.Edit("Optional Subnet ID: ")

        fetch_btn = urwid.Button("Fetch Leases", on_press=self.fetch_and_display)
        to_res_btn = urwid.Button("Reservations", on_press=lambda _: self.return_cb("show_reservations"))
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Back"))

        return urwid.LineBox(
            urwid.Pile([
                urwid.Columns([fetch_btn, to_res_btn, back_btn]),
                self.subnet_field,
                urwid.Divider(),
                self.output
            ]),
            title="DHCP Leases"
        )

    def fetch_and_display(self, _):
        subnet_input = self.subnet_field.get_edit_text().strip()
        subnet_id = int(subnet_input) if subnet_input.isdigit() else None

        leases = fetch_leases(self.context['kea_host'], self.context['kea_port'], subnet_id)
        if isinstance(leases, list):
            lines = [f"IP: {l['ip-address']} | MAC: {l['hw-address']} | State: {l['state']}" for l in leases]
            self.output.set_text("\n".join(lines) if lines else "No leases found.")
        else:
            self.output.set_text(str(leases))
