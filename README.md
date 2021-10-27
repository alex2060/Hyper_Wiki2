# Dockerized App: Hyper Wiki
#Thanks a thanks to https://github.com/Alejandroacho/DockerizedAppTemplate for the docker template

All we be in one Docker container that will be already setted up to just start With ths hyper wiki

## Requirements
  - Docker
  - Docker-Compose

## Nice to have
  - Python3
  - Django

## Nice to take a look to
- [Docker documentation.](https://docs.celeryproject.org/en/stable/index.html#)
- [Django documentation.](https://www.djangoproject.com/)
- [DjangoREST documentation.](https://www.django-rest-framework.org/)
- [Celery documentation.](https://docs.celeryproject.org/)



## Instructions

1. Go to root content folder.
2. Bring up the docker container running:  
    ```docker-compose up```

3. go to http://localhost:8000/ the rest of the documention can be found there
4. go to http://localhost:5000/ please give time for it to connfiger and load
5. go to add a database named app1 by clicking new
6. import into that database the app1 sql file
7. open test.html and look at the console log



## Notes for deployment in industry settings
The best way to scail is to go horizontally
Redirect each request to for a newpage to random server all pointing to same sql database cluster.
When scailing the DB Note that the underling data stuchture is a hash table.






