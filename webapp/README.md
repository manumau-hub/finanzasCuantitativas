# Para correr la aplicacion

## Linux

## instalar python

## crear un entorno virtual

$ cd webapp


$ python3 -m venv ./webappenv

## activar el entorno virtual creado

$ source ./webappenv/bin/activate

## instalar las dependencias

$ pip install -r requirements.txt

## poner en modo ejecutable el server

$ chmod +x runserver.sh

## correr el server

$ ./runserver.sh

## ejecutar la aplicación

### luego en un tab del browser poner

localhost:8000/docs


## Windows

### instalar python version 3.9

[python for windows](https://www.python.org/downloads/windows/)

[using python on windows](https://docs.python.org/3/using/windows.html)


Añadir Python 3.9 a PATH

Para tener un entorno similar a linux


- [instalar git bash](https://dev.to/mailingdelgadomedina/como-instalar-gitbash-en-windows-10-4o0e)


- abrir una terminal git bash


## crear un entorno virtual

$ cd webapp

$ python3 -m venv ./webappenv

## activar el entorno virtual creado

$ source ./webappenv/Scripts/activate

## instalar las dependencias

$ pip install -r requirements.txt

## poner en modo ejecutable el server

$ chmod +x runserver.sh

## correr el server

$ ./runserver.sh

## ejecutar la aplicación

### luego en un tab del browser poner

localhost:8000/docs



## Docker

- install docker

(puede no ser trivial)

[Docker](https://docs.docker.com/get-docker/)

[install docker](https://docs.docker.com/desktop/install/windows-install/)

$ cd webapp

$ docker-compose build

$ docker-compose up -d

$ docker-compose down --remove-orphans

