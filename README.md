# Track and Trace

## Setup 

1. Setup PostgreSQL and create "track_and_trace_db" database.
2. Setup Redis.
3. Run 
`pip install -r requirements.txt`
4. Run
`python manage.py migrate`
5. Run
`python manage.py createsuperuser`
6. Run
`python manage.py import_shipment_data`
7. Set the following env vars:
 - `DB_USER`, `DB_PASSWORD` (for PostgreSQL)
 - `REDIS_URL` (for caching)
 - `WEATHER_API_KEY` (for weather integration -> get it from here: https://www.weatherapi.com/)
[Optional] Run `python manage.py test`


## Run
Run
`python manage.py runserver`


## TODO's:
 ** Add REST API tests
1. Create Dockerfile
2. Implement a proper Authentication (JWT)
3. more
