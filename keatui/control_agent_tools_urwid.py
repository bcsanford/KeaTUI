import urwid
import requests

def fetch_control_agent_info(host, port):
    url = f"http://{host}:{port}/"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

class ControlAgentToolsView:
    def __init__(self, context, return_cb):
        self.context = context
        self.return_cb = return_cb
        self.body = self.build_interface()

    def build_interface(self):
        self.output = urwid.Text("Press 'Fetch Info' to test Control Agent")

        fetch_btn = urwid.Button("Fetch Info", on_press=self.fetch_agent_info)
        back_btn = urwid.Button("Back", on_press=lambda _: self.return_cb("Back"))

        return urwid.LineBox(
            urwid.Pile([
                urwid.Columns([fetch_btn, back_btn]),
                urwid.Divider(),
                self.output
            ]),
            title="Control Agent Tools"
        )

    def fetch_agent_info(self, _):
        result = fetch_control_agent_info(self.context['kea_host'], self.context['kea_port'])
        self.output.set_text(str(result))
