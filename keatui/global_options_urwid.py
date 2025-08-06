import urwid
import requests

def fetch_global_options(host, port):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={"command": "config-get", "service": "dhcp4"})
        return response.json().get("arguments", {}).get("Dhcp4", {}).get("option-data", [])
    except Exception as e:
        return [{"error": str(e)}]

def submit_global_option(host, port, option):
    url = f"http://{host}:{port}/"
    try:
        response = requests.post(url, json={
            "command": "config-set",
            "service": "dhcp4",
            "arguments": {
                "Dhcp4": {
                    "option-data": [option]
                }
            }
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

class GlobalOptionsView:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("")
        self.name_field = urwid.Edit("Option Name: ")
        self.code_field = urwid.Edit("Option Code: ")
        self.value_field = urwid.Edit("Option Value: ")

        fetch_btn = urwid.Button("Fetch Options", on_press=self.fetch_and_display)
        submit_btn = urwid.Button("Set Option", on_press=self.submit_option)
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Back"))

        self.options_list = urwid.Text("")

        return urwid.LineBox(
            urwid.Pile([
                urwid.Columns([fetch_btn, submit_btn, back_btn]),
                self.name_field,
                self.code_field,
                self.value_field,
                urwid.Divider(),
                self.options_list,
                urwid.Divider(),
                self.output
            ]),
            title="Global DHCP Options"
        )

    def fetch_and_display(self, _):
        options = fetch_global_options(self.context['kea_host'], self.context['kea_port'])
        if isinstance(options, list):
            lines = [f"Code: {o.get('code')} | Name: {o.get('name')} | Value: {o.get('data')}" for o in options]
            self.options_list.set_text("\n".join(lines) if lines else "No options found.")
        else:
            self.options_list.set_text(str(options))

    def submit_option(self, _):
        name = self.name_field.get_edit_text().strip()
        code = self.code_field.get_edit_text().strip()
        value = self.value_field.get_edit_text().strip()

        if not name or not code.isdigit() or not value:
            self.output.set_text("Invalid input: all fields must be filled, code must be a number.")
            return

        result = submit_global_option(self.context['kea_host'], self.context['kea_port'], {
            "name": name,
            "code": int(code),
            "data": value,
            "space": "dhcp4"
        })
        self.output.set_text(str(result))
        self.fetch_and_display(None)
