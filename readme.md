 Root the Box
-------------------
* Based on teaspoon
* http://rootthebox.com/
* GPL v3

 Setup
-------------------
* install these packages: tornado (2.2), sqlalchemy (0.7.5), nose (1.0.0), pycco (virtualenv is always recommended)
* set up the db connection string at __models/\_\_init\_\_.py__
* 'python . create'. it will ONLY create the tables 
* 'python -c "import setup.auth" to initialize database
* 'python . test' - will test the application.
* 'python . serve' - will serve the application. open your browser at http://localhost:8888, for more configuration checkout __handlers/\_\_init\_\_.py__


