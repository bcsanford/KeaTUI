import urwid
import requests

def fetch_subnets(host, port):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={"command": "subnet4-list", "service": "dhcp4"})
        return response.json().get("arguments", {}).get("subnets", [])
    except Exception as e:
        return [f"Error: {e}"]

def add_subnet(host, port, subnet):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "subnet4-add",
            "service": "dhcp4",
            "arguments": {"subnet": subnet}
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def del_subnet(host, port, subnet_id):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "subnet4-del",
            "service": "dhcp4",
            "arguments": {"id": subnet_id}
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

class SubnetEditor:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("")
        self.subnet_input = urwid.Edit("New Subnet (CIDR): ")

        fetch_btn = urwid.Button("Fetch Subnets", on_press=self.fetch_and_display)
        add_btn = urwid.Button("Add Subnet", on_press=self.add_subnet)
        del_btn = urwid.Button("Delete Subnet by ID", on_press=self.delete_subnet_prompt)
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Returned from subnet editor."))

        self.subnet_list = urwid.Text("No subnets loaded.")

        pile = urwid.Pile([
            urwid.Columns([fetch_btn, add_btn, del_btn, back_btn]),
            self.subnet_input,
            urwid.Divider(),
            self.subnet_list,
            urwid.Divider(),
            self.output
        ])
        return urwid.LineBox(pile, title="Subnet Editor")

    def fetch_and_display(self, _):
        subnets = fetch_subnets(self.context['kea_host'], self.context['kea_port'])
        if isinstance(subnets, list):
            lines = [f"{s['id']}: {s['subnet']}" for s in subnets]
            self.subnet_list.set_text("\n".join(lines) if lines else "No subnets.")
        else:
            self.subnet_list.set_text(str(subnets))

    def add_subnet(self, _):
        new_subnet = self.subnet_input.get_edit_text().strip()
        if not new_subnet:
            self.output.set_text("Subnet field is empty.")
            return
        result = add_subnet(self.context['kea_host'], self.context['kea_port'], new_subnet)
        self.output.set_text(str(result))
        self.fetch_and_display(None)

    def delete_subnet_prompt(self, _):
        def on_done(edit, text):
            if not text.strip().isdigit():
                self.output.set_text("Invalid subnet ID.")
                return
            result = del_subnet(self.context['kea_host'], self.context['kea_port'], int(text.strip()))
            self.output.set_text(str(result))
            self.fetch_and_display(None)
            self.loop.widget = self.body

        prompt = urwid.Edit("Enter Subnet ID to delete: ")
        fill = urwid.Filler(urwid.Pile([
            prompt,
            urwid.Button("Delete", on_press=lambda _: on_done(prompt, prompt.get_edit_text())),
            urwid.Button("Cancel", on_press=lambda _: setattr(self.loop, 'widget', self.body))
        ]))
        self.loop.widget = urwid.LineBox(fill, title="Delete Subnet")
    
    def run_in_loop(self, loop):
        self.loop = loop
