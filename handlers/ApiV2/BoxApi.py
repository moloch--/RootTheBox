import json
from ..BaseHandlers import BaseHandler
from libs.SecurityDecorators import apikey, restrict_ip_address
from models.Box import Box
from models.Corporation import Corporation
from models.GameLevel import GameLevel
import logging
from models import dbsession

logger = logging.getLogger()


class BoxApiHandler(BaseHandler):

    @apikey
    @restrict_ip_address
    def get(self, id=None):
        if id is None or id == "":
            data = {"boxes": [box.to_dict() for box in Box.all()]}
        else:
            box = Box.by_id(id)
            if box is not None:
                data = {"box": box.to_dict()}
            else:
                data = {"message": "Box not found"}
        self.write(json.dumps(data))

    @apikey
    @restrict_ip_address
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        logger.info(f"Posted data : {data}")
        if "corporation" not in data:
            data = {"corporation": None, "message": "Corporation is required"}
            self.write(json.dumps(data))
            return
        if "name" not in data:
            data = {"box": None, "message": "Name is required"}
            self.write(json.dumps(data))
            return

        if Box.by_name(data["name"]) is not None:
            data = {"box": None, "message": "This box already exists"}
            self.write(json.dumps(data))
            return

        if Corporation.by_name(data["corporation"]) is None:
            data = {
                "corporation": data["corporation"],
                "message": "This corporation does not exist",
            }
            self.write(json.dumps(data))
            return

        new_box = Box()
        new_box.name = data["name"]
        new_box.description = data["description"] if "description" in data else ""
        new_box.corporation_id = (
            Corporation.by_name(data["corporation"]).id
            if "corporation" in data
            else None
        )

        flag_submission_type = (
            data["flag_submission_type"]
            if "flag_submission_type" in data
            else "CLASSIC"
        )
        if flag_submission_type not in ["CLASSIC", "TOKEN"]:
            new_box.flag_submission_type = "CLASSIC"
        else:
            new_box.flag_submission_type = flag_submission_type

        new_box.game_level_id = GameLevel.by_number(0).id

        dbsession.add(new_box)
        dbsession.commit()
        data = {"box": new_box.to_dict(), "message": "This box has been created"}
        self.write(json.dumps(data))

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
