import urwid

def launch_ui(api_url):
    body = [urwid.Text(f"Connected to: {api_url}"), urwid.Divider()]
    body.append(urwid.Button("Exit", on_press=lambda btn: raise_exit()))
    main_loop = urwid.MainLoop(urwid.ListBox(urwid.SimpleFocusListWalker(body)), handle_mouse=True)
    main_loop.run()

def raise_exit():
    raise urwid.ExitMainLoop()
