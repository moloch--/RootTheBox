import json
from ..BaseHandlers import BaseHandler
from libs.SecurityDecorators import apikey, restrict_ip_address
from models.Corporation import Corporation
import logging
from models import Team, dbsession

logger = logging.getLogger()


class CorporationApiHandler(BaseHandler):

    @apikey
    @restrict_ip_address
    def get(self, id: str = None):
        if id is None or id == "":
            data = {
                "data": [corporation.to_dict() for corporation in Corporation.all()]
            }
        else:
            corporation = Corporation.by_id(id)
            if corporation is not None:
                data = {"data": corporation.to_dict()}
            else:
                data = {"message": "Corporation not found"}
        self.write(json.dumps(data))

    @apikey
    @restrict_ip_address
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        logger.info(f"Post data : {data}")

        if Corporation.by_name(data["name"]) is not None:
            data = {
                "data": {"corporation": data["name"]},
                "message": "This corporation already exists",
            }
            self.write(json.dumps(data))
            return

        new_corporation = Corporation()
        new_corporation.name = data["name"]
        new_corporation.locked = data["locked"] if "locked" in data else False
        new_corporation.description = (
            data["description"] if "description" in data else ""
        )

        dbsession.add(new_corporation)
        dbsession.commit()
        data = {
            "data": {
                "corporation": new_corporation.to_dict(),
            },
            "message": "This corporation has been created",
        }
        self.write(json.dumps(data))

    @apikey
    @restrict_ip_address
    def delete(self, id: str):
        corporation = Corporation.by_id(id)
        if corporation is not None:
            dbsession.delete(corporation)
            dbsession.commit()
            self.write(
                json.dumps(
                    {
                        "data": {"corporation": corporation.to_dict()},
                        "message": "Corporation deleted",
                    }
                )
            )
        else:
            self.write(
                json.dumps(
                    {
                        "data": {"corporation": None},
                        "message": "Corporation not found",
                    }
                )
            )

    @apikey
    @restrict_ip_address
    def put(self, *args, **kwargs):
        raise NotImplementedError()

    def check_xsrf_cookie(self):
        pass
