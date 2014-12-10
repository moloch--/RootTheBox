# -*- coding: utf-8 -*-
'''
Created on Sep 12, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


from models.BaseModels import DatabaseObject
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.types import Integer


team_to_box = Table('team_to_box', DatabaseObject.metadata,
                    Column(
                        'team_id', Integer, ForeignKey('team.id'), nullable=False),
                    Column(
                        'box_id', Integer, ForeignKey('box.id'), nullable=False)
                    )

team_to_item = Table('team_to_item', DatabaseObject.metadata,
                     Column(
                         'team_id', Integer, ForeignKey('team.id'), nullable=False),
                     Column(
                         'item_id', Integer, ForeignKey('market_item.id'), nullable=False)
                     )

team_to_source_code = Table('team_to_source_code', DatabaseObject.metadata,
                            Column(
                                'team_id', Integer, ForeignKey('team.id'), nullable=False),
                            Column('source_code_id', Integer, ForeignKey(
                                'source_code.id'), nullable=False)
                            )

team_to_hint = Table('team_to_hint', DatabaseObject.metadata,
                     Column(
                         'team_id', Integer, ForeignKey('team.id'), nullable=False),
                     Column(
                         'hint_id', Integer, ForeignKey('hint.id'), nullable=False)
                     )

team_to_flag = Table('team_to_flag', DatabaseObject.metadata,
                     Column(
                         'team_id', Integer, ForeignKey('team.id'), nullable=False),
                     Column(
                         'flag_id', Integer, ForeignKey('flag.id'), nullable=False)
                     )

team_to_game_level = Table('team_to_game_level', DatabaseObject.metadata,
                           Column(
                               'team_id', Integer, ForeignKey('team.id'), nullable=False),
                           Column('game_level_id', Integer, ForeignKey(
                               'game_level.id'), nullable=False)
                           )

snapshot_to_snapshot_team = Table('snapshot_to_snapshot_team', DatabaseObject.metadata,
                                  Column(
                                      'snapshot_id', Integer, ForeignKey('snapshot.id'), nullable=False),
                                  Column('snapshot_team_id', Integer, ForeignKey(
                                      'snapshot_team.id'), nullable=False)
                                  )

snapshot_team_to_flag = Table('snapshot_team_to_flag', DatabaseObject.metadata,
                              Column('snapshot_team_id', Integer, ForeignKey(
                                  'snapshot_team.id'), nullable=False),
                              Column(
                                  'flag_id', Integer, ForeignKey('flag.id'), nullable=False)
                              )

snapshot_team_to_game_level = Table('snapshot_team_to_game_level', DatabaseObject.metadata,
                                    Column('snapshot_team_id', Integer, ForeignKey(
                                        'snapshot_team.id'), nullable=False),
                                    Column('gam_level_id', Integer, ForeignKey(
                                        'game_level.id'), nullable=False)
                                    )
