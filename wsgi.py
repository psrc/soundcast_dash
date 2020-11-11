import sys
sys.path.insert(0, "/var/www/html/soundcast_dash")
from main import app
from werkzeug.debug import DebuggedApplication

application = app.server
#application = DebuggedApplication(app.server, True)

