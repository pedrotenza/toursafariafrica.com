# toursafariafrica.com
Discover Botswana and its wildlife. Book your unforgettable safari adventure today at TourSafariAfrica.com!

cd "E:\Visual Studio Code\toursafariafrica.com"
.\safari-site-env\Scripts\Activate.ps1
cd "E:\Visual Studio Code\toursafariafrica.com\root"

python manage.py runserver



cd "E:\Visual Studio Code\toursafariafrica.com\root"
python manage.py makemigrations
python manage.py migrate




python manage.py runserver

http://localhost:8000/admin