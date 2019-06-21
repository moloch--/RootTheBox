from handlers.BaseHandlers import BaseHandler
from libs.SecurityDecorators import authenticated


class ChefHandler(BaseHandler):
    @authenticated
    def get(self):
        with open("cyberchef/CyberChef.html", "r") as myfile:
            data = myfile.read()
        self.write(data)
