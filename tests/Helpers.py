from models import dbsession
from models.Team import Team
from models.User import User
from models.Corporation import Corporation
from models.Box import Box
from models.GameLevel import GameLevel
from tornado.options import options


def create_team():
    team = Team()
    team.name = "TestTeam"
    team.motto = "TestMotto"
    dbsession.add(team)
    dbsession.commit()
    return team


def create_user():
    user = User.by_handle("HacKer")
    if user is None:
        options.banking = True
        user = User()
        user.handle = "HacKer"
        user.password = "TestPassword"
        user.bank_password = "Test123"
        dbsession.add(user)
        dbsession.commit()
    return user


def create_corp():
    corp = Corporation()
    corp.name = "TestCorp"
    dbsession.add(corp)
    dbsession.commit()
    return corp


def create_box(corp=None):
    if corp is None:
        corp = create_corp()
    game_level = GameLevel.all()[0]
    box = Box(corporation_id=corp.id, game_level_id=game_level.id)
    box.name = "TestBox"
    box.description = "Some description"
    box.difficuly = "Easy"
    corp.boxes.append(box)
    dbsession.add(box)
    dbsession.commit()
    return box, corp
