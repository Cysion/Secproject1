# 12stepsapp
An app built for the [e-llipse](e-llipse.com) project team for studying suicide prevention systems. Built as a web app using the django framework, 12stepsapp aims to help people struggling with suicidal ideation. 12stepsapp was built with the integrity and security of the user at its focus, providing a robust security framework to keep user data strictly confidential. Although secure in its own right the 12steps development team strongly advices AGAINST deploying this on a large scale as it was only built for a research study, not final deployment. 12stepsapp was developed by a team of students as a project at Blekinge institute of technology (Sweden).

### Prerequisites
A mySQL compliant database is required to run the code unmodified, however all databases supported by django are indirectly supported by 12stepsapp

### Installation and deployment
Installation instructions written for a Linux/UNIX system, installation on other systems might be similar, but will require some autonomy.
After cloning this code repository, you chould set up the database and enter the details of the database into the **conf/db.cnf** file
```
[client]
database = database_name
user = database_user
password = database_user_password
default-character-set = utf8
```
After this is done, you should [generate a new django secret key](https://djecrety.ir/) which you should paste into **conf/secret_key**.  
  
After having setup surrounding dependencies, you should set up the virtual environment for the app. make sure you use python 3.8, or a later compatible version, as well as pip installed. Install python virtual environment manager with your package manager or with pip  
`pip install virutalenv`  
then use virtualenv to set up a virtual environment for the app
`python -m venv env`  
now, and in the future when launching the app, to use the environment  
`source env/bin/activate`
now being all set you can either use the **makefile** to set up the project (recommended)  
`make -f makefile all`  
or follow this step by step guide (not recommended):  
  
update to the latest version of the repository and pip  
`git pull`  
`pip install --upgrade pip`
then install the required python libraries 
**NOTE:** the version on most python libraries have been **FROZEN**, you will have to upgrade them **MANUALLY**  
`pip install -r requirements.txt`  
then you have to use the built in django database construction feature  
`python manage.py migrate`  
if the command succeds you can start the server by executing  
`python manage.py runserver`  

## Built With
* [Python](https://www.python.org/doc/) - Language and dependency management
* [Django](https://docs.djangoproject.com/en/3.1/) - The web framework used
* [MariaDB](https://mariadb.org/) - Database used in development

## Authors
### Development team
* **Robin Lenz** - *Database designer and crypto system integrator* - [RobinLenz](https://github.com/RobinLenz)
* **Ludwig Wideskär** - *Designer and frontend developer* - [buggewe](https://github.com/buggewe)
* **Kevin Engström** - *Full stack developer and Django expert* - [kevinen98](https://github.com/kevinen98)
* **Wilhelm Wickström** - *Code tester* - [willzone0](https://github.com/willzone0)
* **Joakim Karlsson** - *Tools and plugins developer and deployment manager* - [cysion](https://github.com/Cysion)

### Project lead
* **Anna Baran** - *e-llipse project coordinator and contact person between the e-llipse team and development team*

## License
This project is licensed under the GNU General Public License version 3 - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments
* We are not software developers nor security engineers, only students and the quality of the code will reflect that.
* Inspiration
* etc