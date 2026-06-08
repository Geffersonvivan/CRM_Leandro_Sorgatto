web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py load_sc && python manage.py create_admin && gunicorn crm_sorgatto.wsgi --bind 0.0.0.0:$PORT
