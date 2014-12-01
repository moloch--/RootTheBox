# -*- coding: utf-8 -*-
'''
Created on Nov 24, 2014

@author: moloch

    Copyright 2014 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


Handlers related to controlling and configuring the overall game.


'''

import os
import logging
import defusedxml.minidom
import xml.etree.cElementTree as ET

from tempfile import NamedTemporaryFile
from libs.SecurityDecorators import *
from models.User import ADMIN_PERMISSION
from handlers.BaseHandlers import BaseHandler, BaseWebSocketHandler


class AdminGameHandler(BaseHandler):

    ''' Start or stop the game '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        if self.get_argument('start_game') == 'true':
            self.start_game()
        else:
            self.stop_game()
        self.redirect('/user')

    def start_game(self):
        ''' Start the game and any related callbacks '''
        if not self.application.settings['game_started']:
            logging.info("The game is about to begin, good hunting!")
            self.application.settings['game_started'] = True
            self.application.settings['history_callback'].start()
            if self.config.use_bots:
                self.application.settings['score_bots_callback'].start()

    def stop_game(self):
        ''' Stop the game and all callbacks '''
        logging.info("The game is stopping ...")
        self.application.settings['game_started'] = False
        if self.application.settings['history_callback']._running:
            self.application.settings['history_callback'].stop()
        if self.application.settings['score_bots_callback']._running:
            self.application.settings['score_bots_callback'].stop()
        for user in User.all_users():
            user.locked = True
            self.dbsession.add(user)
        self.dbsession.commit()


class AdminRegTokenHandler(BaseHandler):

    ''' Manages registration tokens '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Call method based on URI '''
        uri = {
            'create': self.create,
            'view': self.view,
        }
        if len(args) == 1 and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Used to delete regtokens '''
        token_value = self.get_argument('token_value', '')
        reg_token = RegistrationToken.by_value(token_value)
        if reg_token is not None:
            self.dbsession.delete(reg_token)
            self.dbsession.commit()
            self.redirect('/admin/regtoken/view')
        else:
            self.render('admin/view/token.html',
                        errors=["Token does not exist"]
                        )

    def create(self):
        ''' Adds a registration token to the db and displays the value '''
        token = RegistrationToken()
        self.dbsession.add(token)
        self.dbsession.commit()
        self.render('admin/create/token.html', token=token)

    def view(self):
        ''' View all reg tokens '''
        self.render('admin/view/token.html', errors=None)


class AdminSourceCodeMarketHandler(BaseHandler):

    ''' Add source code files to the source code market '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render('admin/upgrades/source_code_market.html', errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        uri = {
            '/add': self.add_source_code,
            '/delete': self.delete_source_code,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render("public/404.html")

    def add_source_code(self):
        box = Box.by_uuid(self.get_argument('box_uuid'))
        if box is not None:
            if not 'source_archive' in self.request.files and 0 < len(self.request.files['source_archive']):
                self.render('admin/upgrades/source_code_market.html',
                            errors=["No file data"]
                            )
            else:
                try:
                    price = abs(int(self.get_argument('price', 'NaN')))
                    self.create_source_code(box, price)
                    self.render('admin/upgrades/source_code_market.html',
                                errors=None
                                )
                except ValueError:
                    self.render('admin/upgrades/source_code_market.html',
                                errors=["Price must be an integer"]
                                )
        else:
            self.render('admin/upgrades/source_code_market.html',
                        errors=["The selected box does not exist"]
                        )

    def create_source_code(self, box, price):
        ''' Save file data and create object in database '''
        description = unicode(self.get_argument('description', ''))
        file_name = unicode(
            self.request.files['source_archive'][0]['filename']
        )
        source_code = SourceCode(
            file_name=file_name,
            box_id=box.id,
            price=price,
            description=description,
        )
        self.dbsession.add(source_code)
        self.dbsession.flush()
        file_data = self.request.files['source_archive'][0]['body']
        root = self.application.settings['source_code_market_dir']
        save_file = open(str(root + '/' + source_code.uuid), 'w')
        source_code.checksum = self.get_checksum(file_data)
        save_file.write(file_data.encode('base64'))
        save_file.close()
        self.dbsession.add(source_code)
        self.dbsession.commit()

    def get_checksum(self, data):
        ''' Calculate checksum of file data '''
        return sha1(data).hexdigest()

    def delete_source_code(self):
        ''' Delete source code file '''
        uuid = self.get_argument('box_uuid', '')
        box = Box.by_uuid(uuid)
        if box is not None and box.source_code is not None:
            source_code_uuid = box.source_code.uuid
            self.dbsession.delete(box.source_code)
            self.dbsession.commit()
            root = self.application.settings['source_code_market_dir']
            source_code_path = root + '/' + source_code_uuid
            logging.info("Delete souce code market file: %s (box: %s)" %
                        (source_code_path, box.name,)
                         )
            if os.path.exists(source_code_path):
                os.unlink(source_code_path)
            errors = None
        else:
            errors = ["Box does not exist, or contains no source code"]
        self.render('admin/upgrades/source_code_market.html', errors=errors)


class AdminSwatHandler(BaseHandler):

    ''' Manage SWAT requests '''

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render_page()

    def render_page(self, errors=None):
        ''' Render page with extra arguments '''
        if errors is not None and not isinstance(errors, list):
            errors = [str(errors), ]
        self.render('admin/upgrades/swat.html',
                    pending_bribes=Swat.all_pending(),
                    in_progress_bribes=Swat.all_in_progress(),
                    completed_bribes=Swat.all_completed(),
                    errors=errors,
                    )

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Accept/Complete bribes '''
        uri = {
            '/accept': self.accept_bribe,
            '/complete': self.complete_bribe,
        }
        if len(args) and args[0] in uri:
            uri[args[0]]()
        else:
            self.render('public/404.html')

    def accept_bribe(self):
        ''' Accept bribe, and lock user's account '''
        swat = Swat.by_uuid(self.get_argument('uuid', ''))
        if swat is not None and not swat.completed:
            logging.info("Accepted SWAT with uuid: %s", swat.uuid)
            swat.accepted = True
            swat.target.locked = True
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warn("Invalid request to accept bribe with uuid: %r" %
                        (self.get_argument('uuid', ''),)
                         )
            self.render_page('Requested SWAT object does not exist')

    def complete_bribe(self):
        ''' Complete bribe and unlock user's account '''
        swat = Swat.by_uuid(self.get_argument('uuid', ''))
        if swat is not None and not swat.completed:
            logging.info("Completed SWAT with uuid: %s", swat.uuid)
            swat.completed = True
            swat.target.locked = False
            self.dbsession.add(swat)
            self.dbsession.add(swat.target)
            self.dbsession.commit()
            self.render_page()
        else:
            logging.warn("Invalid request to complete bribe with uuid: %r" %
                        (self.get_argument('uuid', ''),)
                         )
            self.render_page('Requested SWAT object does not exist')


class AdminConfigurationHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        self.render('admin/configuration.html',
                    errors=[],
                    config=self.config
                    )

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        '''
        Update configuration
        Disabled fields will not be send in the POST, so check for blank values
        '''
        try:
            config = ConfigManager.instance()
            config.game_name = self.get_argument('game_name', '')
            config.restrict_registration = self.get_argument(
                'restrict_registration', '') == 'true'
            config.public_teams = self.get_argument(
                'public_teams', '') == 'true'
            config.max_team_size = self.get_argument('max_team_size', '')
            config.max_password_length = self.get_argument(
                'max_password_length', '')
            self.config_bots(config)
            reward = self.get_argument('bot_reward', '')
            if reward != '':
                config.bot_reward = reward
            config.use_black_market = self.get_argument(
                'use_black_market', '') == 'true'
            upgrade_cost = self.get_argument('password_upgrade_cost', '')
            if upgrade_cost != '':
                config.password_upgrade_cost = upgrade_cost
            bribe_cost = self.get_argument('bribe_cost', '')
            if bribe_cost != '':
                config.bribe_cost = bribe_cost
            config.save()
            self.render(
                'admin/configuration.html', errors=None, config=self.config)
        except ValidationError as error:
            logging.exception("Configuration update threw an exception")
            self.render('admin/configuration.html',
                        errors=[str(error)], config=self.config)

    def config_bots(self, config):
        ''' Updates bot config, and starts/stops the botnet callback '''
        config.use_bots = self.get_argument('use_bots') == 'true'
        if config.use_bots and not self.application.settings['score_bots_callback']._running:
            logging.info("Starting botnet callback function")
            self.application.settings['score_bots_callback'].start()
        elif self.application.settings['score_bots_callback']._running:
            logging.info("Stopping botnet callback function")
            self.application.settings['score_bots_callback'].stop()


class AdminGarbageCfgHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Download a Box's garbage file '''
        box = Box.by_uuid(self.get_argument('uuid', ''))
        if box is not None:
            data = box.get_garbage_cfg()
            self.set_header('Content-Type', 'text/plain')
            self.set_header(
                "Content-disposition", "attachment; filename=%s.garbage" % (
                    filter(lambda char: char in printable[:-38], box.name),
                ))
            self.set_header('Content-Length', len(data))
            self.write(data)


class AdminExportHandler(BaseHandler):

    API_VERSION = "1"

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Export to document formats '''
        self.render('admin/export.html', errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        ''' Include the requests exports in the xml dom '''
        root = ET.Element("rootthebox")
        root.set("api", self.API_VERSION)
        if self.get_argument('game_objects', '') == 'true':
            self.export_game_objects(root)
        if self.get_argument('users', '') == 'true':
            self.export_users(root)
        xml_dom = defusedxml.minidom.parseString(ET.tostring(root))
        self.write_xml(xml_dom.toprettyxml())

    def write_xml(self, xml_doc):
        ''' Write XML document to page '''
        self.set_header('Content-Type', 'text/xml')
        self.set_header(
            "Content-disposition", "attachment; filename=%s.xml" % (
                filter(lambda char: char in printable[
                       :-38], self.config.game_name),
            ))
        self.set_header('Content-Length', len(xml_doc.encode('utf-8')))
        self.write(xml_doc.encode('utf-8'))
        self.finish()

    def export_game_objects(self, root):
        '''
        Exports the game objects to an XML doc.
        For the record, I hate XML with a passion.
        '''
        levels_elem = ET.SubElement(root, "gamelevels")
        levels_elem.set("count", str(GameLevel.count()))
        for level in GameLevel.all()[1:]:
            level.to_xml(levels_elem)
        corps_elem = ET.SubElement(root, "corporations")
        corps_elem.set("count", str(Corporation.count()))
        for corp in Corporation.all():
            corp.to_xml(corps_elem)

    def export_users(self, root):
        teams_elem = ET.SubElement(root, "teams")
        teams_elem.set("count", str(Team.count()))
        for team in Team.all():
            team.to_xml(teams_elem)


class AdminImportXmlHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Import setup files '''
        self.render('admin/import.html', success=None, errors=None)

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def post(self, *args, **kwargs):
        '''
        Import XML file uploaded by the admin.
        '''
        if 'xml_file' in self.request.files:
            fxml = self._get_tmp()
            errors = []
            success = None
            if import_xml(fxml):
                success = "Successfully imported XML objects"
            else:
                errors.append("Failed to parse file correctly.")
            os.unlink(fxml)
            self.render('admin/import.html', success=success, errors=errors)
        else:
            self.render(
                'admin/import.html', success=None, errors=["No file data."])

    def _get_tmp(self):
        ''' Creates a tmp file with the file data '''
        data = self.request.files['xml_file'][0]['body']
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.write(data)
        tmp_file.close()
        return tmp_file.name


class AdminLogViewerHandler(BaseHandler):

    @restrict_ip_address
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def get(self, *args, **kwargs):
        ''' Import setup files '''
        if self.config.enable_logviewer:
            self.render('admin/logviewer.html')
        else:
            self.render('public/404.html')


class AdminLogViewerSocketHandler(BaseWebSocketHandler):

    @restrict_ip_address
    @restrict_origin
    @authenticated
    @authorized(ADMIN_PERMISSION)
    def open(self):
        ''' Add this object as an observer '''
        self.observerable_log = None
        if self.config.enable_logviewer:
            self.observerable_log = ObservableLoggingHandler.instance()
            self.observerable_log.add_observer(self)
        else:
            self.close()

    def update(self, messages):
        ''' Write logging messages to wsocket '''
        self.write_message({'messages': messages})

    def on_close(self):
        ''' Remove the ref to this object '''
        if self.observerable_log is not None:
            self.observerable_log.remove_observer(self)
