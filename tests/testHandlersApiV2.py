# -*- coding: utf-8 -*-
"""
Unit tests for everything in handlers/
"""
import requests
import unittest
import string
import random

URL = "https://rtb.docker.localhost"  # The RTB URL
APIKEY = "TheApiKey"  # The Api Key


class TestApiV2(unittest.TestCase):

    url = None

    @classmethod
    def setUpClass(cls):
        print("setUpClass")
        cls.url = URL
        cls.headers = {"Content-Type": "application/json", "apikey": APIKEY}
        corps = cls.get_all_corporations(cls)
        corps = [
            x
            for x in corps.json()["corporations"]
            if "testUT" in x["name"] or "TU_" in x["name"]
        ]
        for x in corps:
            requests.delete(
                f"{cls.url}/api/v2/corporation/{x['id']}",
                headers=cls.headers,
                verify=False,
            )

    def test_1_create_corp(self):
        data = {"name": "testUT", "description": "Nothing as test", "locked": False}
        rsp = requests.post(
            f"{self.url}/api/v2/corporation",
            json=data,
            headers=self.headers,
            verify=False,
        )
        self.assertEqual(rsp.status_code, 200)
        json_d = rsp.json()
        self.assertEqual(json_d["corporation"]["name"], "testUT")
        self.assertEqual(json_d["corporation"]["locked"], False)
        self.assertEqual(json_d["corporation"]["description"], "Nothing as test")

    def test_2_get_corporation(self):
        all = self.get_all_corporations()
        corp = [x for x in all.json()["corporations"] if "testUT" in x["name"]]
        self.assertEqual(len(corp), 1)
        res = requests.get(
            f"{self.url}/api/v2/corporation/{corp[0]['id']}",
            headers=self.headers,
            verify=False,
        )
        self.assertEqual(res.status_code, 200)
        json_d = res.json()
        self.assertEqual(json_d["corporation"]["name"], "testUT")
        self.assertEqual(json_d["corporation"]["locked"], False)
        self.assertEqual(json_d["corporation"]["description"], "Nothing as test")

    def test_3_delete_corporation(self):
        all = self.get_all_corporations()
        corp = [x for x in all.json()["corporations"] if "testUT" in x["name"]]
        res = requests.delete(
            f"{self.url}/api/v2/corporation/{corp[0]['id']}",
            headers=self.headers,
            verify=False,
        )
        self.assertEqual(res.status_code, 200)

    def test_4_complex(self):
        self.test_1_create_corp()

        self.get_all_corporations()
        data = {
            "name": "testUTBox",
            "description": "Nothing as a box test",
            "corporation": "testUT",
        }
        rsp_box = requests.post(
            f"{self.url}/api/v2/box", json=data, headers=self.headers, verify=False
        )
        self.assertEqual(rsp_box.status_code, 200)
        json_box = rsp_box.json()

        self.assertEqual(json_box["box"]["name"], "testUTBox")
        self.assertEqual(json_box["box"]["description"], "Nothing as a box test")

        data = {
            "box": "testUTBox",
            "name": "testUTFlag",
            "value": 10,
            "token": "testUTToken",
            "description": "Nothing as a flag test",
        }
        rsp_flag = requests.post(
            f"{self.url}/api/v2/flag", json=data, headers=self.headers, verify=False
        )
        self.assertEqual(rsp_flag.status_code, 200)
        json_flag = rsp_flag.json()

        self.assertEqual(json_flag["flag"]["name"], "testUTFlag")
        self.assertEqual(json_flag["flag"]["token"], "testUTToken")
        self.assertEqual(json_flag["flag"]["description"], "Nothing as a flag test")

        self.assertEqual(json_flag["flag"]["value"], 10)

        data = {
            "box": "testUTBox",
            "name": "testUTFlag2",
            "value": 20,
            "token": "testUTToken2",
            "description": "Nothing as a flag2 test",
        }
        rsp_flag = requests.post(
            f"{self.url}/api/v2/flag", json=data, headers=self.headers, verify=False
        )
        self.assertEqual(rsp_flag.status_code, 200)
        json_flag = rsp_flag.json()

        self.assertEqual(json_flag["flag"]["name"], "testUTFlag2")
        self.assertEqual(json_flag["flag"]["token"], "testUTToken2")
        self.assertEqual(json_flag["flag"]["description"], "Nothing as a flag2 test")
        self.assertEqual(json_flag["flag"]["value"], 20)

    def get_all_corporations(self):
        corps = requests.get(
            f"{self.url}/api/v2/corporation", headers=self.headers, verify=False
        )
        return corps

    def get_all_boxes(self):
        boxes = requests.get(
            f"{self.url}/api/v2/box", headers=self.headers, verify=False
        )
        return boxes

    def get_all_flags(self):
        flags = requests.get(
            f"{self.url}/api/v2/flag", headers=self.headers, verify=False
        )
        return flags

    def test_5_complex(self):

        corporations = {
            "TU_007": {
                "description": "Corporation 007",
                "boxes": {
                    "DECOUVERTE": "Box DECOUVERTE",
                    "ZONE_EDF": "Box ZONE_EDF",
                    "ZONE_THALES": "Box ZONE_THALES",
                    "ZONE_LES_ECHOS": "Box ZONE_LES_ECHOS",
                    "ZONE_FREE": "Box ZONE_FREE",
                },
            },
            "TU_CORP_12": {
                "description": "Corp 12",
                "boxes": {
                    "DECOUVERTE": "Box DECOUVERTE",
                    "ZONE_TOTAL": "Box ZONE_TOTAL",
                    "ZONE_MBDA": "Box ZONE_MBDA",
                    "ZONE_LE_MONDE": "Box ZONE_LE_MONDE",
                    "ZONE_SFR": "Box ZONE_SFR",
                },
            },
            "TU_OTHER_CORP": {
                "description": "Other corp",
                "boxes": {
                    "DECOUVERTE": "Box DECOUVERTE",
                    "ZONE_WEB": "Box ZONE_WEB",
                    "ZONE_PHYSIQUE": "Box ZONE_PHYSIQUE",
                },
            },
        }

        letters = string.ascii_lowercase

        for k, v in corporations.items():
            self.create_corp(k, v["description"], False)

            for k_box, v_box in v["boxes"].items():
                self.create_box(k_box, v_box, k)
                for i in range(random.randint(1, 10)):
                    self.create_flag(
                        f"flag_{''.join(random.choices(letters, k=5))}",
                        "Une fake description",
                        random.randint(1, 100),
                        f"CHE-{''.join(random.choices(letters, k=15))}",
                        k_box,
                    )

    def create_corp(self, name, description, locked):
        data = {"name": name, "description": description, "locked": locked}
        rsp = requests.post(
            f"{self.url}/api/v2/corporation",
            json=data,
            headers=self.headers,
            verify=False,
        )
        return rsp

    def create_box(self, name, description, corporation):
        data = {
            "name": name,
            "description": description,
            "corporation": corporation,
        }
        rsp = requests.post(
            f"{self.url}/api/v2/box", json=data, headers=self.headers, verify=False
        )

        return rsp

    def create_flag(self, name, description, value, token, box):
        data = {
            "name": name,
            "description": description,
            "value": value,
            "token": token,
            "box": box,
        }
        rsp = requests.post(
            f"{self.url}/api/v2/flag",
            json=data,
            headers=self.headers,
            verify=False,
        )
        return rsp
