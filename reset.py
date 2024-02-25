def runn(co,args):
    try:
        co(args)
    except Exception as e:
        print(e)
def run():
    import os
    runn(os.remove,('db.sqlite3'))
    import shutil
    runn(shutil.rmtree,('judger/migrations'))
    runn(os.system,('python manage.py makemigrations'))
    runn(os.system,('python manage.py makemigrations judger'))
    runn(os.system,('python manage.py migrate'))

    from django.contrib.auth.models import User

    # Check if superuser already exists
    if not User.objects.filter(username='admin').exists():
        # Create a superuser
        superuser = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        print("Superuser created successfully.")
    else:
        print("Superuser already exists.")