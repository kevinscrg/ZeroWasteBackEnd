# ZeroWasteBackEnd
Before stating the API, run the following commands:<br>
<b>pip install django<br>
pip install djangorestframework<br>
pip install environs<br>
pip install celery<br>
pip install redis<br>
</b>

You will need to install also Redis server from: https://github.com/microsoftarchive/redis/releases

In order to start the API, run the following commands:<br>

<b>python --version<br>
python manage.py runserver<br></b>

for uploading receipts you will need to
<b>
execute redis-derver.exe<br>
run in another terminal the comand: celery -A zerowaste.celery_app worker -l info --pool=solo<br>
</b>

Then open a web browser and go to http://127.0.0.1:8000/user/

If you want to make any changes in the source code and then test in the web browser, please run the following coomands:<br>
<b>python manage.py makemigrations<br>
python manage.py migrate</b>

If errors occur, try to run:<br>
<b>pip install -r ./requirements.txt</b>



PRODUCT - ENDPOINTS

GET, CREATE
http://127.0.0.1:8000/products/

DELETE, PUT
http://127.0.0.1:8000/products/id/


UPLOAD A RECEIPE:



