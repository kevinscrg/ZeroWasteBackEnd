# ZeroWasteBackEnd

ZeroWasteFrontend: <a>https://github.com/kriss1809/ZeroWasteFrontEnd</a>
<br>
ZeroWasteAI: <a>https://github.com/kriss1809/ZeroWasteAI</a>

Before stating the API, run the following commands:<br>
<b>pip install django<br>
pip install djangorestframework<br>
pip install environs<br>
pip install celery<br>
pip install redis<br>
pip install chanells<br>
pip install daphne<br>
python -m spacy download en_core_web_md<br>
</br>

You should install the Redis server from https://github.com/microsoftarchive/redis/releases, or alternatively, install it on WSL (or any Linux-based operating system) using the command `sudo apt install redis-server`.<br>
(I recommend using WSL to install Redis and starting the Redis server from WSL since the Windows port is not up-to-date.)

In order to start the API, run the following commands:<br>

<b>python --version<br>
python manage.py runserver<br></b>

for uploading receipts you will need to
<b>
Run `redis-server.exe` if you've installed it on Windows, or use `sudo service redis-server start` if you're on a Linux OS. <br>
run in another terminal the comand: `celery -A zerowaste.celery_app worker -l info --pool=solo`<br>
</b>

Then open a web browser and go to http://127.0.0.1:8000/user/

If you want to make any changes in the source code and then test in the web browser, please run the following coomands:<br>
<b>python manage.py makemigrations<br>
python manage.py migrate</b>

If errors occur, try to run:<br>
<b>pip install -r ./requirements.txt</b>


In order to start the API with Websockets, run the following commands:<br>
<b>
daphne -p 8000 zerowaste.asgi:application (instead of pyhton manage.py runserver)<br>
you will also nead to run the redis-server 


PRODUCT - ENDPOINTS

GET, CREATE
http://127.0.0.1:8000/products/

DELETE, PUT
http://127.0.0.1:8000/products/id/


UPLOAD A RECEIPE:



