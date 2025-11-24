import logging

from flask import Flask

# custom imports
from components.print import vPrint
from components.hostInfo import isHostValid,getHostType

# api blueprints
from api.test import testBlueprint

debug = True

if __name__ == "__main__":
    vPrint("Server starting.")

    if not isHostValid() or debug == True:
        Debug = True
        vPrint("Development environment detected.")
    
        api = Flask(__name__)
        api.register_blueprint(testBlueprint)
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        api.run(port=80,debug=False)
