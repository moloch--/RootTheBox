# -*- coding: utf-8 -*-
"""
Created on Apr 2, 2021

@author: anthturner

    Copyright 2021 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# pylint: disable=unused-variable

import logging
import requests
from tornado.options import options


def send_game_start_webhook():
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "game_start",
        }
    )


def send_game_stop_webhook():
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "game_stop",
        }
    )


def send_capture_webhook(user, flag, reward):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "capture_flag",
            "flag": {"name": flag.name, "original_value": flag.value, "value": reward},
            "user": get_user_info(user),
            "team": get_team_info(user.team),
        }
    )


def send_capture_failed_webhook(user, flag):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "capture_failed",
            "flag": {"name": flag.name, "original_value": flag.value},
            "user": get_user_info(user),
            "team": get_team_info(user.team),
        }
    )


def send_level_complete_webhook(user, level):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "level_complete",
            "level": {
                "name": level.name,
                "number": level.number,
                "type": level.type,
                "reward": level.reward,
            },
            "user": get_user_info(user),
            "team": get_team_info(user.team),
        }
    )


def send_box_complete_webhook(user, box):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "box_complete",
            "box": {
                "name": box.name,
                "value": box.value,
                "operating_system": box.operating_system,
                "difficulty": box.difficulty,
            },
            "user": get_user_info(user),
            "team": get_team_info(user.team),
        }
    )


def send_hint_taken_webhook(user, hint):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "hint_taken",
            "flag": {"name": hint.flag.name},
            "user": get_user_info(user),
            "team": get_team_info(user.team),
            "cost": hint.price,
        }
    )

def send_user_registered_webhook(user):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "user_registered",
            "user": get_user_info(user),
        }
    )

def send_user_validated_webhook(user):
    send_webhook(
        {
            "game": options.game_name,
            "game_version": options.game_version,
            "origin": options.origin.replace("wss://", "").replace("ws://", ""),
            "action": "user_validated",
            "user": get_user_info(user),
        }
    )


def get_user_info(user):
    return {
        "handle": user.handle,
        "email": user.email,
        "name": user.name,
    }


def get_team_info(team):
    return {
        "name": team.name,
        "money": team.get_score("money"),
        "flags": team.get_score("flag"),
        "hints": team.get_score("hint"),
        "bots": team.get_score("bot"),
        "members": get_team_members(team),
    }


def get_team_members(team):
    team_members = []
    for team_member in team.members:
        team_members.append(get_user_info(team_member))
    return team_members


def send_webhook(data):
    if options.webhook_url:
        logging.info(
            "Sending webhook for '" + data["action"] + "' to " + options.webhook_url
        )
        try:
            requests.post(options.webhook_url, json=data)
        except requests.exceptions.RequestException:
            logging.exception("error sending webhook")
