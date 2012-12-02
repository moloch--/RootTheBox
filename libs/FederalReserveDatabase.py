# -*- coding: utf-8 *-*


import sqlite3

from models import Team
from libs.Singleton import Singleton


@Singleton
class FederalReserveDatabase(object):

    def __init__(self):
        self.dbs = {}
        for team in Team.all():
            self.create_team_table(team)

    def create_team_table(self, team):
        self.dbs[team.name] = sqlite3.connect(':memory:')
        cursor = self.dbs[team.name].cursor()
        cursor.execute("""CREATE TABLE users(id INTEGER PRIMARY KEY,
            username TEXT, password TEXT, algorithm TEXT)
        """)
        for create_team in Team.all():
            if create_team == team:
                continue
            for user in create_team.members:
                cursor.execute("""INSERT INTO users VALUES (NULL, ?, ?, ?) """,
                    (user.handle, user.password, user.algorithm,)
                )

    def select(self, user, query):
        db = self.dbs[user.team.name]
        cursor = db.cursor()
        results = cursor.execute(query)
        return results
