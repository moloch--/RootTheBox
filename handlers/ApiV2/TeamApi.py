import json
from ..BaseHandlers import BaseHandler
from libs.SecurityDecorators import apikey, restrict_ip_address
from models.Corporation import Corporation
import logging
from models import Team, dbsession

logger = logging.getLogger()


class TeamApiHandler(BaseHandler):

    @apikey
    @restrict_ip_address
    def get(self, id: str = None):
        with_flags = self.get_argument("with_flags", "false").lower() == "true"
        if id is None or id == "":
            data = {"data": [team.to_dict(with_flags) for team in Team.all()]}
        else:
            team = Team.by_uuid(id)
            if team is not None:
                data = {"data": team.to_dict(with_flags)}
            else:
                data = {"message": "Team not found"}
        self.write(json.dumps(data))

    @apikey
    @restrict_ip_address
    def post(self, *args, **kwargs):
        raise NotImplementedError()

    @apikey
    @restrict_ip_address
    def delete(self, id: str):
        raise NotImplementedError()

    @apikey
    @restrict_ip_address
    def put(self, *args, **kwargs):
        raise NotImplementedError()

    def check_xsrf_cookie(self):
        pass
