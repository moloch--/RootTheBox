 Root the Box
-------------------
* Based on teaspoon


 Setup
-------------------
* install these packages: tornado, sqlalchemy, nose, pycco (virtualenv is always recommended)
* download and extract  
* cd teaspoon  
* type 'python .' - will print out options available to you from the __\_\_main\_\_.py__ file  
* set up the db connection string at __models/\_\_init\_\_.py__
* 'python . create'. it'll create the tables (it wont fill em with data)
* 'pyhon -c "import setup.auth" inorder to fill with basic User/Group/Permission data
* 'python . test' - will test the application. should pass.
* 'python . serve' - will serve the application. open your browser at http://localhost:8888, for more configuration checkout __handlers/\_\_init\_\_.py__


