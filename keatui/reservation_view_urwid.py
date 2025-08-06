
"""
reservation_view_urwid.py — Manage DHCPv4 and DHCPv6 reservations with subnet selection and editing support
"""

import urwid
import requests

def fetch_reservations(host, port, subnet_id):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "subnet4-get-reservations",
            "service": "dhcp4",
            "arguments": {"subnet-id": subnet_id}
        })
        return response.json().get("arguments", {}).get("reservations", [])
    except Exception as e:
        return [f"Error fetching reservations: {e}"]

def submit_reservation(host, port, subnet_id, ip, mac):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "reservation-add",
            "service": "dhcp4",
            "arguments": {
                "reservation": {
                    "ip-address": ip,
                    "hw-address": mac,
                    "subnet-id": subnet_id
                }
            }
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def delete_reservation(host, port, subnet_id, ip):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "reservation-del",
            "service": "dhcp4",
            "arguments": {
                "ip-address": ip,
                "subnet-id": subnet_id
            }
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_subnets(host, port):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={"command": "subnet4-list", "service": "dhcp4"})
        return response.json().get("arguments", {}).get("subnets", [])
    except Exception:
        return []

class ReservationView:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.subnets = fetch_subnets(context['kea_host'], context['kea_port'])
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("", wrap='clip')
        self.ip_field = urwid.Edit("IP Address: ")
        self.mac_field = urwid.Edit("MAC Address: ")
        self.subnet_choices = [(f"{s['id']} ({s['subnet']})", str(s['id'])) for s in self.subnets]
        self.subnet_history = []
        self.subnet_dropdown = urwid.ListBox(urwid.SimpleFocusListWalker([
            urwid.RadioButton(self.subnet_history, label, state=(i == 0), user_data=val)
            for i, (label, val) in enumerate(self.subnet_choices)
        ])) if self.subnet_choices else urwid.Text("No subnets available")

        fetch_btn = urwid.Button("Fetch Reservations", on_press=self.fetch_and_display)
        add_btn = urwid.Button("Add/Edit Reservation", on_press=self.add_edit_reservation)
        del_btn = urwid.Button("Delete Reservation", on_press=self.delete_reservation_by_ip)
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Returned from reservation viewer."))
        to_lease_btn = urwid.Button("View Leases", on_press=lambda _: self.return_cb("show_lease_view"))

        return urwid.LineBox(
            urwid.Pile([
                urwid.Columns([fetch_btn, add_btn, del_btn, back_btn, to_lease_btn]),
                self.ip_field,
                self.mac_field,
                urwid.Text("Select Subnet ID:"),
                self.subnet_dropdown,
                urwid.Divider(),
                self.output
            ]),
            title="DHCP Reservations (IPv4)"
        )

    def get_selected_subnet_id(self):
        for widget in self.subnet_dropdown.body:
            if isinstance(widget, urwid.RadioButton) and widget.state:
                return int(widget.user_data)
        return None

    def fetch_and_display(self, _):
        subnet_id = self.get_selected_subnet_id()
        if subnet_id is None:
            self.output.set_text("Please select a subnet.")
            return

        reservations = fetch_reservations(self.context['kea_host'], self.context['kea_port'], subnet_id)
        if isinstance(reservations, list):
            lines = [f"IP: {r['ip-address']}  MAC: {r['hw-address']}" for r in reservations]
            self.output.set_text("\n".join(lines) if lines else "No reservations found.")
        else:
            self.output.set_text(str(reservations))

    def add_edit_reservation(self, _):
        subnet_id = self.get_selected_subnet_id()
        ip = self.ip_field.get_edit_text().strip()
        mac = self.mac_field.get_edit_text().strip()
        if not subnet_id or not ip or not mac:
            self.output.set_text("All fields and subnet must be selected.")
            return

        result = submit_reservation(self.context['kea_host'], self.context['kea_port'], subnet_id, ip, mac)
        self.output.set_text(str(result))
        self.fetch_and_display(None)

    def delete_reservation_by_ip(self, _):
        subnet_id = self.get_selected_subnet_id()
        ip = self.ip_field.get_edit_text().strip()
        if not subnet_id or not ip:
            self.output.set_text("Subnet and IP must be provided.")
            return

        result = delete_reservation(self.context['kea_host'], self.context['kea_port'], subnet_id, ip)
        self.output.set_text(str(result))
        self.fetch_and_display(None)
