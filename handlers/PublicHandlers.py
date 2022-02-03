# -*- coding: utf-8 -*-
"""
Created on Mar 13, 2012

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
----------------------------------------------------------------------------

This file holds publicly exposed handlers (handlers that to not require
any authentication) with the exception of error handlers and the scoreboard

"""


import logging
import re
import smtplib
import secrets
import string

from os import urandom
from netaddr import IPAddress
from libs.Identicon import identicon
from libs.SecurityDecorators import blacklist_ips
from libs.ValidationError import ValidationError
from libs.XSSImageCheck import filter_avatars
from libs.StringCoding import encode, decode
from base64 import urlsafe_b64encode, urlsafe_b64decode, b64encode
from builtins import str
from models import azuread_app
from models.Team import Team
from models.Theme import Theme
from models.PasswordToken import PasswordToken
from models.RegistrationToken import RegistrationToken
from models.EmailToken import EmailToken
from models.GameLevel import GameLevel
from models.User import User, ADMIN_PERMISSION
from models.Permission import Permission
from handlers.BaseHandlers import BaseHandler
from hashlib import sha256
from datetime import datetime
from pbkdf2 import PBKDF2
from tornado.options import options
from msal import ConfidentialClientApplication


class HomePageHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """ Renders the main page """
        if self.session is not None:
            self.redirect("/user")
        else:
            self.render("public/home.html")


class CodeFlowHandler(BaseHandler):

    """ Handles the OIDC code flow response, when using Azure AD authentication """

    azuread_app = azuread_app

    def get(self, *args, **kwargs):
        state = args = self.get_argument("state")
        code = self.get_argument("code")
        code_flow = self.memcached.get(state)
        self.memcached.delete(state)
        args = {"code": code, "state": state}
        result = azuread_app.acquire_token_by_auth_code_flow(code_flow, args)
        if "error" in result:
            self.redirect("/403")
            return

        claims = result.get("id_token_claims")

        # Admin is defined by the Azure AD AppRole "Admin"
        hasAdminRole = self.is_admin(claims)

        # Get the team code (if set) would have come from the Join Team page.
        team_code = None
        if "teamcode" in code_flow:
            team_code = code_flow["teamcode"]

        # Look up user the Azure AD object id (Guid)
        user = User.by_uuid(claims["oid"])

        # If user is not admin and not part of a team or new, they need to join a team.
        # Redirect to the join team page here, if needed, before the user is created in the db.
        if self.needs_team(hasAdminRole, user, team_code):
            self.redirect("/jointeam?upn=" + claims["upn"])
            return

        # New user
        if user is None:
            user = self.add_user(claims, team_code)

        self.update_permissions(user, hasAdminRole)

        self.dbsession.commit()

        self.create_login_session(user)

        self.redirect("/user")

    def create_login_session(self, user):
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        if user.team is not None:
            self.session["team_id"] = int(user.team.id)
        self.session["user_id"] = int(user.id)
        self.session["user_uuid"] = user.uuid
        self.session["handle"] = user.handle
        self.session["theme"] = [str(f) for f in theme.files]
        self.session["theme_id"] = int(theme.id)
        if user.is_admin():
            self.session["menu"] = "admin"
        else:
            self.session["menu"] = "user"
        self.session.save()

    # Admin is defined by the Azure AD AppRole "Admin"
    def is_admin(self, claims):
        if "roles" in claims:
            roles = claims["roles"]
            if "Admin" in roles:
                return True
        return False

    # Figure out whether the user should be presented with the join team page.
    def needs_team(self, hasAdminRole, user, team_code):
        needsateam = False
        # Is the a member of a team, if not admin?
        if not hasAdminRole:
            if user is not None:
                if user.team is None:
                    # Have they entered a joining code from the join team page?
                    if team_code is not None and len(team_code) > 0:
                        team = Team.by_code(team_code)
                        user.team = team
                    else:
                        needsateam = True
            # New user must have teamcode for joining a team.
            elif team_code is None or len(team_code) == 0:
                needsateam = True
        return needsateam

    def add_user(self, claims, team_code):
        user = User()
        user.uuid = claims["oid"]
        user.handle = claims["preferred_username"].split("@")[0]
        # Generate a long random password that the user will never know or use.
        user.password = "".join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for i in range(30)
        )
        user.bank_password = ""
        user.name = claims["name"]
        user.email = claims["email"]
        user.theme = options.default_theme
        user.last_login = datetime.now()
        user.logins = 1
        if not self.is_admin(claims):
            user.team = Team.by_code(team_code)
        self.dbsession.add(user)
        return user

    def update_permissions(self, user, isAdmin):
        # Update permissions, in-case the user has been added to or removed from the
        # admin role in Azure AD.
        if isAdmin and not user.is_admin():
            permission = Permission()
            permission.name = ADMIN_PERMISSION
            permission.user_id = user.id
            self.dbsession.add(permission)
            user.team_id = None  # Admins aren't part of a team.
        elif not isAdmin and user.is_admin():
            permissions = Permission.by_user_id(user.id)
            for permission in permissions:
                if permission.name == ADMIN_PERMISSION:
                    self.dbsession.delete(permission)


class LoginHandler(BaseHandler):

    """ Takes care of the login process """

    azuread_app = azuread_app

    def get(self, *args, **kwargs):
        """ Display the login page """
        if self.session is not None:
            self.redirect("/user")
        else:
            if options.auth == "azuread":
                code_flow = self.build_auth_code_flow()
                self.memcached.add(code_flow["state"], code_flow)
                self.redirect(code_flow["auth_uri"])
            else:
                self.render("public/login.html", info=None, errors=None)

    @blacklist_ips
    def post(self, *args, **kwargs):
        """ Checks submitted username and password """
        user = User.by_handle(self.get_argument("account", ""))
        password_attempt = self.get_argument("password", "")
        if user is None:
            user = User.by_email(self.get_argument("account", ""))
        if user is not None:
            if user.validate_password(password_attempt):
                self.valid_login(user)
            else:
                self.failed_login()
        else:
            if password_attempt is not None:
                PBKDF2.crypt(password_attempt, "BurnTheHashTime")
            self.failed_login()

    def build_auth_code_flow(self):
        codeflow = azuread_app.initiate_auth_code_flow(
            ["email"], redirect_uri=options.redirect_url
        )
        return codeflow

    def allowed_ip(self):
        return (
            len(options.admin_ips) == 0 or self.request.remote_ip in options.admin_ips
        )

    def valid_login(self, user):
        if user.is_admin() and not self.allowed_ip():
            self.render(
                "public/login.html",
                info=[
                    "Successful credentials, but administration is restriceted via IP.  See 'admin_ips' in configuration."
                ],
                errors=None,
            )
            logging.warning(
                "Admin login - invalid IP %s.  Valid: %s"
                % (self.request.remote_ip, ",".join(options.admin_ips))
            )
        elif (
            options.require_email
            and options.validate_email
            and not user.is_admin()
            and not user.is_email_valid()
        ):
            self.render(
                "public/login.html",
                info=None,
                errors=["Your email account must be validated before login"],
            )
        elif user.locked:
            self.render(
                "public/login.html", info=None, errors=["Your account has been locked"]
            )
        elif user.is_expired():
            self.render(
                "public/login.html", info=None, errors=["Your account is expired"]
            )
        else:
            self.successful_login(user)
            if self.config.story_mode and user.logins == 1 and not user.is_admin():
                self.redirect("/user/missions/firstlogin")
            else:
                self.redirect("/user")

    def successful_login(self, user):
        """ Called when a user successfully logs in """
        logging.info(
            "Successful login: %s from %s" % (user.handle, self.request.remote_ip)
        )
        user.last_login = datetime.now()
        user.logins += 1
        self.dbsession.add(user)
        self.dbsession.commit()
        self.start_session()
        theme = Theme.by_id(user.theme_id)
        if user.team is not None:
            self.session["team_id"] = int(user.team.id)
        self.session["user_id"] = int(user.id)
        self.session["user_uuid"] = user.uuid
        self.session["handle"] = user.handle
        self.session["theme"] = [str(f) for f in theme.files]
        self.session["theme_id"] = int(theme.id)
        if user.is_admin():
            self.session["menu"] = "admin"
        else:
            self.session["menu"] = "user"
        self.session.save()

    def failed_login(self):
        """ Called if username/password is invalid """
        ip = self.request.remote_ip
        logging.info("*** Failed login attempt from: %s" % ip)
        failed_logins = self.application.settings["failed_logins"]
        if ip in failed_logins:
            failed_logins[ip] += 1
        else:
            failed_logins[ip] = 1
        threshold = self.application.settings["blacklist_threshold"]
        if (
            self.application.settings["automatic_ban"]
            and threshold <= failed_logins[ip]
        ):
            logging.info("[BAN HAMMER] Automatically banned IP: %s" % ip)
            try:
                if not IPAddress(ip).is_loopback():
                    self.application.settings["blacklisted_ips"].append(ip)
                else:
                    logging.warning("[BAN HAMMER] Cannot blacklist loopback address")
            except:
                logging.exception("Error while attempting to ban ip address")
        self.render(
            "public/login.html",
            info=None,
            errors=["Bad username and/or password, try again"],
        )


class RegistrationHandler(BaseHandler):

    """ Registration Code """

    def get(self, *args, **kwargs):
        """ Renders the registration page """
        if self.session is not None:
            self.redirect("/user")
        else:
            self.render(
                "public/registration.html",
                errors=None,
                suspend=self.application.settings["suspend_registration"],
            )

    def post(self, *args, **kwargs):
        """ Attempts to create an account, with shitty form validation """
        try:
            if self.application.settings["suspend_registration"]:
                self.render("public/registration.html", errors=None, suspend=True)
            else:
                self.form_validation()
                if self.config.restrict_registration:
                    self.check_regtoken()
                user = self.create_user()
                validate = options.require_email and options.validate_email
                self.render(
                    "public/successful_reg.html", account=user.handle, validate=validate
                )
        except ValidationError as error:
            self.render(
                "public/registration.html",
                errors=[str(error)],
                suspend=self.application.settings["suspend_registration"],
            )

    def check_regtoken(self):
        regtoken = self.get_argument("token", "")
        token = RegistrationToken.by_value(regtoken)
        if token is not None and not token.used:
            token.used = True
            self.dbsession.add(token)
            self.dbsession.commit()
        else:
            raise ValidationError("Invalid registration token")

    def form_validation(self):
        unicodewd = "ªµºÀ-ÖØ-öø-ˁˆ-ˑˠ-ˤˬˮͰ-ʹͶͷͺ-ͽͿΆΈ-ΊΌΎ-ΡΣ-ϵϷ-ҁҊ-ԯԱ-Ֆՙՠ-ֈא-תׯ-ײؠ-يٮٯٱ-ۓەۥۦۮۯۺ-ۼۿܐܒ-ܯݍ-ޥޱߊ-ߪߴߵߺࠀ-ࠕࠚࠤࠨࡀ-ࡘࡠ-ࡪࡰ-ࢇࢉ-ࢎࢠ-ࣉऄ-हऽॐक़-ॡॱ-ঀঅ-ঌএঐও-নপ-রলশ-হঽৎড়ঢ়য়-ৡৰৱৼਅ-ਊਏਐਓ-ਨਪ-ਰਲਲ਼ਵਸ਼ਸਹਖ਼-ੜਫ਼ੲ-ੴઅ-ઍએ-ઑઓ-નપ-રલળવ-હઽૐૠૡૹଅ-ଌଏଐଓ-ନପ-ରଲଳଵ-ହଽଡ଼ଢ଼ୟ-ୡୱஃஅ-ஊஎ-ஐஒ-கஙசஜஞடணதந-பம-ஹௐఅ-ఌఎ-ఐఒ-నప-హఽౘ-ౚౝౠౡಀಅ-ಌಎ-ಐಒ-ನಪ-ಳವ-ಹಽೝೞೠೡೱೲഄ-ഌഎ-ഐഒ-ഺഽൎൔ-ൖൟ-ൡൺ-ൿඅ-ඖක-නඳ-රලව-ෆก-ะาำเ-ๆກຂຄຆ-ຊຌ-ຣລວ-ະາຳຽເ-ໄໆໜ-ໟༀཀ-ཇཉ-ཬྈ-ྌက-ဪဿၐ-ၕၚ-ၝၡၥၦၮ-ၰၵ-ႁႎႠ-ჅჇჍა-ჺჼ-ቈቊ-ቍቐ-ቖቘቚ-ቝበ-ኈኊ-ኍነ-ኰኲ-ኵኸ-ኾዀዂ-ዅወ-ዖዘ-ጐጒ-ጕጘ-ፚᎀ-ᎏᎠ-Ᏽᏸ-ᏽᐁ-ᙬᙯ-ᙿᚁ-ᚚᚠ-ᛪᛱ-ᛸᜀ-ᜑᜟ-ᜱᝀ-ᝑᝠ-ᝬᝮ-ᝰក-ឳៗៜᠠ-ᡸᢀ-ᢄᢇ-ᢨᢪᢰ-ᣵᤀ-ᤞᥐ-ᥭᥰ-ᥴᦀ-ᦫᦰ-ᧉᨀ-ᨖᨠ-ᩔᪧᬅ-ᬳᭅ-ᭌᮃ-ᮠᮮᮯᮺ-ᯥᰀ-ᰣᱍ-ᱏᱚ-ᱽᲀ-ᲈᲐ-ᲺᲽ-Ჿᳩ-ᳬᳮ-ᳳᳵᳶᳺᴀ-ᶿḀ-ἕἘ-Ἕἠ-ὅὈ-Ὅὐ-ὗὙὛὝὟ-ώᾀ-ᾴᾶ-ᾼιῂ-ῄῆ-ῌῐ-ΐῖ-Ίῠ-Ῥῲ-ῴῶ-ῼⁱⁿₐ-ₜℂℇℊ-ℓℕℙ-ℝℤΩℨK-ℭℯ-ℹℼ-ℿⅅ-ⅉⅎↃↄⰀ-ⳤⳫ-ⳮⳲⳳⴀ-ⴥⴧⴭⴰ-ⵧⵯⶀ-ⶖⶠ-ⶦⶨ-ⶮⶰ-ⶶⶸ-ⶾⷀ-ⷆⷈ-ⷎⷐ-ⷖⷘ-ⷞⸯ々〆〱-〵〻〼ぁ-ゖゝ-ゟァ-ヺー-ヿㄅ-ㄯㄱ-ㆎㆠ-ㆿㇰ-ㇿ㐀-䶿一-ꒌꓐ-ꓽꔀ-ꘌꘐ-ꘟꘪꘫꙀ-ꙮꙿ-ꚝꚠ-ꛥꜗ-ꜟꜢ-ꞈꞋ-ꟊꟐꟑꟓꟕ-ꟙꟲ-ꠁꠃ-ꠅꠇ-ꠊꠌ-ꠢꡀ-ꡳꢂ-ꢳꣲ-ꣷꣻꣽꣾꤊ-ꤥꤰ-ꥆꥠ-ꥼꦄ-ꦲꧏꧠ-ꧤꧦ-ꧯꧺ-ꧾꨀ-ꨨꩀ-ꩂꩄ-ꩋꩠ-ꩶꩺꩾ-ꪯꪱꪵꪶꪹ-ꪽꫀꫂꫛ-ꫝꫠ-ꫪꫲ-ꫴꬁ-ꬆꬉ-ꬎꬑ-ꬖꬠ-ꬦꬨ-ꬮꬰ-ꭚꭜ-ꭩꭰ-ꯢ가-힣ힰ-ퟆퟋ-ퟻ豈-舘並-龎ﬀ-ﬆﬓ-ﬗיִײַ-ﬨשׁ-זּטּ-לּמּנּסּףּפּצּ-ﮱﯓ-ﴽﵐ-ﶏﶒ-ﷇﷰ-ﷻﹰ-ﹴﹶ-ﻼＡ-Ｚａ-ｚｦ-ﾾￂ-ￇￊ-ￏￒ-ￗￚ-ￜ"
        if (
            bool(re.match(r"^[a-zA-Z0-9_\-\.]{3,16}$", self.get_argument("handle", "")))
            is False
        ):
            raise ValidationError("Invalid handle format")
        email = self.get_argument("email", None)
        if options.require_email and (not email or not len(email) > 0):
            raise ValidationError("Email address is required")
        if (
            email
            and bool(
                re.match(
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    self.get_argument("email", ""),
                )
            )
            is False
        ):
            raise ValidationError("Invalid email format")
        if (
            self.get_argument("playername", None)
            and bool(
                re.match(
                    r"^[0-9A-Za-z %s]{3,64}$" % unicodewd,
                    self.get_argument("playername", ""),
                    re.UNICODE,
                )
            )
            is False
        ):
            raise ValidationError("Invalid playername format")
        if (
            self.get_argument("team-name", None)
            and bool(
                re.match(
                    r"^[0-9A-Za-z _\-\.]{3,24}$", self.get_argument("team-name", "")
                )
            )
            is False
        ):
            raise ValidationError("Invalid Team Name format")
        if (
            self.get_argument("motto", None)
            and bool(
                re.match(
                    r"^[0-9A-Za-z _\-\.%s]{,32}$" % unicodewd,
                    self.get_argument("motto", ""),
                    re.UNICODE,
                )
            )
            is False
        ):
            raise ValidationError("Invalid Team Motto format")
        if (
            User.by_handle(self.get_argument("handle", ""), case_sensitive=False)
            is not None
        ):
            raise ValidationError("This handle is already registered")
        if (
            options.require_email
            and User.by_email(self.get_argument("email", None)) is not None
        ):
            raise ValidationError("This email address is already registered")
        if self.get_argument("pass1", "") != self.get_argument("pass2", ""):
            raise ValidationError("Passwords do not match")

    def create_user(self):
        """ Add user to the database """
        user = User()
        user.handle = self.get_argument("handle", "")
        user.password = self.get_argument("pass1", "")
        user.bank_password = self.get_argument("bpass", "")
        user.name = self.get_argument("playername", "")
        user.email = self.get_argument("email", "")
        user.theme = options.default_theme
        team = self.get_team()
        self.dbsession.add(user)
        self.dbsession.add(team)
        self.dbsession.commit()

        # Avatar
        avatar_select = self.get_argument("user_avatar_select", "")
        if avatar_select and len(avatar_select) > 0:
            user._avatar = avatar_select
        elif hasattr(self.request, "files") and "avatar" in self.request.files:
            user.avatar = self.request.files["avatar"][0]["body"]
        else:
            user._avatar = identicon(user.handle, 6)
        team.members.append(user)
        if not options.teams:
            if avatar_select and len(avatar_select) > 0:
                team._avatar = avatar_select
            elif hasattr(self.request, "files") and "avatar" in self.request.files:
                team.avatar = self.request.files["avatar"][0]["body"]
            else:
                team._avatar = identicon(user.handle, 6)
        self.dbsession.add(user)
        self.dbsession.add(team)
        self.dbsession.commit()
        if (
            options.require_email
            and options.validate_email
            and len(options.mail_host) > 0
        ):
            self.send_validate_message(user)
            user.locked = True
            self.dbsession.add(user)
            self.dbsession.commit()
        else:
            self.event_manager.user_joined_team(user)

        # Chat
        if self.chatsession:
            self.chatsession.create_user(user, self.get_argument("pass1", ""))

        return user

    def get_team(self):
        """ Create a team object, or pull the existing one """
        code = self.get_argument("team-code", "")
        if len(code) > 0:
            team = Team.by_code(code)
            if not team:
                raise ValidationError("Invalid team code")
            elif self.config.max_team_size <= len(team.members):
                raise ValidationError("Team %s is already full" % team.name)
            return team
        return self.create_team()

    def create_team(self):
        """ Create a new team """
        if not self.config.teams:
            team = Team.by_name(self.get_argument("handle", ""))
            if team is None:
                team = Team()
                team.name = self.get_argument("handle", "")
            else:
                logging.info(
                    "Team %s already exists - Player Mode: reset team." % team.name
                )
                team.flags = []
                team.hints = []
                team.boxes = []
                team.items = []
                team.game_levels = []
                team.purchased_source_code = []
            team.motto = self.get_argument("motto", "")
            team._avatar = identicon(team.name, 6)
            if self.config.banking:
                team.money = self.config.starting_team_money
            else:
                team.money = 0
            levels = GameLevel.all()
            for level in levels:
                if level.type == "none":
                    team.game_levels.append(level)
                elif level.type != "hidden" and level.buyout == 0:
                    team.game_levels.append(level)
            return team
        elif self.config.public_teams:
            if Team.by_name(self.get_argument("team_name", "")) is not None:
                raise ValidationError(
                    "This team name is already registered.  Use team code to join that team."
                )
            team = Team()
            team.name = self.get_argument("team_name", "")
            team.motto = self.get_argument("motto", "")
            if len(filter_avatars("team")) == 0:
                team._avatar = identicon(team.name, 6)
            if not self.config.banking:
                team.money = 0
            level_0 = GameLevel.by_number(0)
            if not level_0:
                level_0 = GameLevel.all()[0]
            team.game_levels.append(level_0)
            return team
        else:
            raise ValidationError("Public teams are not enabled")

    def send_validate_message(self, user):
        if user is not None and len(user.email) > 0:
            email_token = encode(urandom(16), "hex")
            emailtoken = EmailToken()
            emailtoken.user_id = user.id
            emailtoken.value = sha256(email_token).hexdigest()
            receivers = [user.email]
            message = self.create_validate_message(user, email_token)
            smtpObj = smtplib.SMTP(options.mail_host, port=options.mail_port)
            smtpObj.set_debuglevel(False)
            try:
                smtpObj.starttls()
                try:
                    smtpObj.login(options.mail_username, options.mail_password)
                except smtplib.SMTPNotSupportedError as e:
                    logging.warning(
                        "SMTP Auth issue (%s). Attempting to send anyway." % e
                    )
                smtpObj.sendmail(options.mail_sender, receivers, message)
            finally:
                smtpObj.quit()
            if not len(options.mail_host) > 0:
                logging.info(
                    "Email validation failed: No Mail Host in Configuration. Skipping Validation."
                )
                emailtoken.valid = True
            else:
                logging.info("Email Validation sent for %s" % user.email)
            self.dbsession.add(emailtoken)
            self.dbsession.commit()
        elif (
            user is not None
            and options.require_email
            and options.validate_email
            and not len(user.email) > 0
        ):
            logging.info(
                "Email validation failed: No Email Address for user %s.  Deleting User"
                % user.handle
            )
            self.dbsession.delete(user)
            self.dbsession.commit()

    def create_validate_message(self, user, token):
        account = encode(user.uuid)
        try:
            account = decode(urlsafe_b64encode(account))
            token = decode(urlsafe_b64encode(token))
        except:
            account = urlsafe_b64encode(account)
            token = urlsafe_b64encode(token)
        if options.ssl:
            origin = options.origin.replace("ws://", "https://").replace(
                "wss://", "https://"
            )
        else:
            origin = options.origin.replace("ws://", "http://")
        validate_url = "%s/registration/token?u=%s&t=%s" % (origin, account, token)
        remote_ip = (
            self.request.headers.get("X-Real-IP")
            or self.request.headers.get("X-Forwarded-For")
            or self.request.remote_ip
        )
        header = []
        header.append("Subject: %s Email Validation" % options.game_name)
        header.append("From: %s <%s>" % (options.game_name, options.mail_sender))
        header.append("To: %s <%s>" % (user.name, user.email))
        header.append("MIME-Version: 1.0")
        header.append('Content-Type: text/html; charset="UTF-8"')
        header.append("Content-Transfer-Encoding: BASE64")
        header.append("")
        f = open("templates/public/valid_email.html", "r")
        template = (
            f.read()
            .replace("\n", "")
            .replace("[Product Name]", options.game_name)
            .replace("{{name}}", user.name)
            .replace("{{action_url}}", validate_url)
            .replace("{{remote_ip}}", remote_ip)
            .replace("https://example.com", origin)
        )
        f.close()
        try:
            email_msg = "\n".join(header) + b64encode(template)
        except:
            email_msg = "\n".join(header) + decode(b64encode(encode(template)))
        return email_msg


class JoinTeamHandler(BaseHandler):

    azuread_app = azuread_app

    def get(self, *args, **kwargs):
        if self.session is not None:
            self.redirect("/user")
        else:
            login_hint = self.get_argument("upn", "")
            self.render(
                "public/jointeam.html",
                errors=None,
                suspend=self.application.settings["suspend_registration"],
                login_hint=login_hint,
            )

    def post(self, *args, **kwargs):
        login_hint = None
        try:
            if self.application.settings["suspend_registration"]:
                self.render("public/jointeam.html", errors=None, suspend=True)
            else:
                code = self.get_argument("team-code", "")
                code = self.validate_teamcode(code)
                login_hint = self.get_argument("login-hint", None)
                if len(login_hint) == 0:
                    login_hint = None
                code_flow = azuread_app.initiate_auth_code_flow(
                    ["email"], redirect_uri=options.redirect_url, login_hint=login_hint
                )
                code_flow["teamcode"] = code
                self.memcached.add(code_flow["state"], code_flow)
                self.redirect(code_flow["auth_uri"])

        except ValidationError as error:
            self.render(
                "public/jointeam.html",
                errors=[str(error)],
                suspend=self.application.settings["suspend_registration"],
                login_hint=login_hint,
            )

    def validate_teamcode(self, teamcode):
        if len(teamcode) == 0:
            raise ValidationError("Invalid team code")
        team = Team.by_code(teamcode)
        if not team:
            raise ValidationError("Invalid team code")
        elif self.config.max_team_size <= len(team.members):
            raise ValidationError("Team %s is already full" % team.name)
        return teamcode


class FakeRobotsHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """
        Troll time :P - TODO: Add BeEF to these pages
        """
        self.set_header("Content-Type", "text/plain")
        self.write("# Block access to admin stuff\n\n")
        self.write("User-agent: *\n\n")
        self.write("/admin/create/sql_query\n")
        self.write("/admin/create/flag_capture\n")
        self.write("/admin/view/db_users.txt\n")
        self.write("/admin/view/passwords.txt\n")
        self.write("/admin/manager/c99.php\n")
        self.finish()


class AboutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """ Renders the about page """
        self.render("public/about.html")


class ForgotPasswordHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """ Renders the Forgot Password Reset page """
        if len(options.mail_host) > 0:
            self.render("public/forgot.html", errors=None, info=None)
        else:
            self.redirect("public/404")

    def post(self, *args, **kwargs):
        """ Sends the password reset to email """
        user = User.by_email(self.get_argument("email", ""))
        if user is not None and len(options.mail_host) > 0 and len(user.email) > 0:
            reset_token = encode(urandom(16), "hex")
            passtoken = PasswordToken()
            passtoken.user_id = user.id
            passtoken.value = sha256(reset_token).hexdigest()
            self.dbsession.add(passtoken)
            self.dbsession.commit()
            receivers = [user.email]
            message = self.create_reset_message(user, reset_token)
            smtpObj = smtplib.SMTP(options.mail_host, port=options.mail_port)
            smtpObj.set_debuglevel(False)
            try:
                smtpObj.starttls()
                try:
                    smtpObj.login(options.mail_username, options.mail_password)
                except smtplib.SMTPNotSupportedError as e:
                    logging.warning(
                        "SMTP Auth issue (%s). Attempting to send anyway." % e
                    )
                smtpObj.sendmail(options.mail_sender, receivers, message)
            finally:
                smtpObj.quit()
            logging.info("Password Reset sent for %s" % user.email)
        elif not len(options.mail_host) > 0:
            logging.info("Password Reset request failed: No Mail Host in Settings.")
        elif user is None or not len(user.email) > 0:
            logging.info("Password Reset request failed: Email does not exist.")
        self.render(
            "public/forgot.html",
            errors=None,
            info=["If the email exists, a password reset has been sent."],
        )

    def create_reset_message(self, user, token):
        account = encode(user.uuid)
        try:
            account = decode(urlsafe_b64encode(account))
            token = decode(urlsafe_b64encode(token))
        except:
            account = urlsafe_b64encode(account)
            token = urlsafe_b64encode(token)
        if options.ssl:
            origin = options.origin.replace("ws://", "https://").replace(
                "wss://", "https://"
            )
        else:
            origin = options.origin.replace("ws://", "http://")
        reset_url = "%s/reset/token?u=%s&p=%s" % (origin, account, token)
        remote_ip = (
            self.request.headers.get("X-Real-IP")
            or self.request.headers.get("X-Forwarded-For")
            or self.request.remote_ip
        )
        header = []
        header.append("Subject: %s Password Reset" % options.game_name)
        header.append("From: %s <%s>" % (options.game_name, options.mail_sender))
        header.append("To: %s <%s>" % (user.name, user.email))
        header.append("MIME-Version: 1.0")
        header.append('Content-Type: text/html; charset="UTF-8"')
        header.append("Content-Transfer-Encoding: BASE64")
        header.append("")
        f = open("templates/public/reset_email.html", "r")
        template = (
            f.read()
            .replace("\n", "")
            .replace("[Product Name]", options.game_name)
            .replace("{{name}}", user.name)
            .replace("{{action_url}}", reset_url)
            .replace("{{remote_ip}}", remote_ip)
            .replace("https://example.com", origin)
        )
        f.close()
        try:
            email_msg = "\n".join(header) + b64encode(template)
        except:
            email_msg = "\n".join(header) + decode(b64encode(encode(template)))
        return email_msg


class ResetPasswordHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """ Renders the Token Reset page """
        if len(options.mail_host) > 0:
            try:
                uuid = decode(urlsafe_b64decode(self.get_argument("u", "")))
                token = sha256(
                    urlsafe_b64decode(self.get_argument("p", ""))
                ).hexdigest()
            except:
                uuid = urlsafe_b64decode(encode(self.get_argument("u", "")))
                token = sha256(
                    urlsafe_b64decode(encode(self.get_argument("p", "")))
                ).hexdigest()
            if self.valid_pass_token(token, uuid):
                self.render(
                    "public/reset.html", errors=None, info=None, token=token, uuid=uuid
                )
        else:
            self.redirect("public/404")

    def post(self, *args, **kwargs):
        token = self.get_argument("token", "")
        uuid = self.get_argument("uuid", "")
        if self.valid_pass_token(token, uuid):
            if self.get_argument("pass1", "") != self.get_argument("pass2", ""):
                self.render(
                    "public/reset.html",
                    errors=None,
                    info=["Passwords do not match."],
                    token=token,
                    uuid=uuid,
                )
            else:
                pass_token = PasswordToken.by_value(token)
                user = User.by_id(pass_token.user_id)
                user.password = self.get_argument("pass1", "")
                pass_token.used = True
                self.dbsession.add(pass_token)
                self.dbsession.commit()
                self.render(
                    "public/reset.html",
                    errors=None,
                    info=["Successfully updated password."],
                    uuid=uuid,
                    token=token,
                )

    def valid_pass_token(self, token, uuid):
        pass_token = PasswordToken.by_value(token)
        if pass_token:
            user = User.by_id(pass_token.user_id)
            if (
                user
                and user.uuid == uuid
                and not pass_token.is_expired()
                and not pass_token.used
            ):
                return True
        self.render(
            "public/reset.html",
            errors=["The password reset token does not exist, is invalid or expired."],
            info=None,
            token="",
            uuid="",
        )
        return False


class ValidEmailHandler(BaseHandler):
    def get(self, *args, **kwargs):
        """ Validates Email and renders login page """
        if len(options.mail_host) > 0:
            error = None
            info = None
            try:
                user_uuid = decode(urlsafe_b64decode(self.get_argument("u", "")))
                token = sha256(
                    urlsafe_b64decode(self.get_argument("t", ""))
                ).hexdigest()
            except:
                user_uuid = urlsafe_b64decode(encode(self.get_argument("u", "")))
                token = sha256(
                    urlsafe_b64decode(encode(self.get_argument("t", "")))
                ).hexdigest()
            user = User.by_uuid(user_uuid)
            if user:
                if user.is_email_valid() is True:
                    pass
                elif user.validate_email(token) is True:
                    info = ["Successfully validated email for %s" % user.handle]
                    user.locked = False
                    self.dbsession.add(user)
                    self.dbsession.commit()
                    self.event_manager.user_joined_team(user)
                else:
                    error = ["Failed to validate email for %s" % user.handle]
            elif len(user_uuid) > 0 and not user:
                error = ["Invalid user for email validation"]
            self.render("public/login.html", info=info, errors=error)
        else:
            self.redirect("public/404")
