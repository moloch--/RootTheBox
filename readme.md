Teaspoon - (TSN<>P)
-------------------

a template+suggestion on how to create a web app using Tornado, SqlAlchemy, testing it using Nose and documentation using Pycco  
intended to give ya just the things you need (more likely to say, I needed), nothing more, WYSIWYG...  
no 'magical' 'project' generation... just download and start using the template


how to:   

* install these packages: tornado, sqlalchemy, nose, pycco (virtualenv is always recommended)
* download and extract  
* cd teaspoon  
* type 'python .' - will print out options available to you from the __\_\_main\_\_.py__ file  
* set up the db connection string at __models/\_\_init\_\_.py__
* 'python . create'. it'll create the tables (it wont fill em with data)
* 'pyhon -c "import setup.auth" inorder to fill with basic User/Group/Permission data
* 'python . test' - will test the application. should pass.
* 'python . serve' - will serve the application. open your browser at http://localhost:8888, for more configuration checkout __handlers/\_\_init\_\_.py__


after all that. RTFC. (docs directory for your convenience) and start modifing the supplied code and apply it to your needs.

marxus@gmail.com  
@_marxus -> @twitter