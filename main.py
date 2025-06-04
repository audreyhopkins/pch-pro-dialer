import threading
from gui import run_gui
from webhook_server import run_webhook

if __name__ == '__main__':
    threading.Thread(target=run_webhook, daemon=True).start()
    run_gui()
