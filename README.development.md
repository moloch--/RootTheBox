# First time we start developing with visual studio
-Clone repo
`git clone https://github.com/pedcremo/RootTheBox.git`
-Install dependencies
`sudo ./setup/depends.sh`
-Create config file (PATH files/rootthebox.cfg)
`./rootthebox.py --update`
Edit files/rootthebox.cfg to set locale (i18n) and database. Sqlite to develop
sql_dialect = "sqlite"
-Create database schema
`./rootthebox.py --setup=prod`

# Every time we start to develop
`./rootthebox.py --start`



Cal fer còpia de:
files/game_materials
files/rootthebox.cfg
files/botnet.db
rootthebox.db


MORE INFO: https://github.com/moloch--/RootTheBox/wiki/Installation