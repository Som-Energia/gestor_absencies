pip install ipython

pip install -r requirements.txt

python manage.py makemigrations gestor_absencies
python manage.py migrate --settings=config.settings.develop
python manage.py runserver 0.0.0.0:8000 --settings=config.settings.develop