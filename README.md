# accuknox-assignment
It is a test assignment given by Accuknox for their hiring.

### Requirements
1. Docker, if you don't have docker, download and install it from https://www.docker.com/products/docker-desktop

### Steps to Run it:
1. Create a build with docker-compose
```
$ docker-compose build
```
3. Migrate the changes to database
```
$ docker-compose run web python manage.py migrate
``` 
5. run the docker
```
$ docker-compose up
```
