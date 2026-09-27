import json
from ..BaseHandlers import BaseHandler
from libs.SecurityDecorators import apikey, restrict_ip_address
from models.Box import Box
from models.Flag import Flag
import logging
from models import dbsession


logger = logging.getLogger()


class FlagApiHandler(BaseHandler):

    @apikey
    @restrict_ip_address
    def get(self, id=None):
        if id is None or id == "":
            data = {"data": [flag.to_dict() for flag in Flag.all()]}
        else:
            flag = Flag.by_id(id)
            if flag is not None:
                data = {"data": flag.to_dict()}
            else:
                data = {"message": "Flag not found"}
        self.write(json.dumps(data))

    @apikey
    @restrict_ip_address
    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        logger.info(f"Post data : {data}")

        if "box" not in data:
            data = {
                "data": {"box": None},
                "message": "Box is required",
            }
            self.write(json.dumps(data))
            return

        if Box.by_name(data["box"]) is None:
            data = {
                "data": {"box": data["box"]},
                "message": "This box does not exist",
            }
            self.write(json.dumps(data))
            return
        box = Box.by_name(data["box"])

        if Flag.by_token_and_box_id(data["token"], box.id) is not None:
            data = {
                "data": {
                    "flag": data["token"],
                    "box": data["box"],
                },
                "message": "This flag already exists",
            }
            self.write(json.dumps(data))
            return

        new_flag = Flag()
        new_flag.name = data["name"]
        new_flag.token = data["token"]
        new_flag.value = int(data["value"]) if "value" in data else 1
        new_flag.box_id = box.id
        new_flag.type = "static"
        new_flag.description = data["description"] if "description" in data else ""

        dbsession.add(new_flag)
        dbsession.commit()
        data = {"data": new_flag.to_dict(), "message": "This flag has been created"}
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
