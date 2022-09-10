# Para correr la aplicacion


## Docker

- install docker

[Docker](https://docs.docker.com/get-docker/)

$ docker-compose build

$ docker-compose up -d

$ docker-compose down --remove-orphans


## Windows

### instalar python

[python for windows](https://www.python.org/downloads/windows/)

[using python on windows](https://docs.python.org/3/using/windows.html)

instalar version 3.9

Añadir Python 3.9 a PATH


## Linux

## instalar python

## crear un entorno virtual

cd webapp

python3 -m venv ./webappenv

## activar el entorno virtual creado

source ./webappenv/bin/activate

## instalar las dependencias

pip install -r requirements.txt

## poner en modo ejecutable el server

$>chmod +x runserver.sh

## correr el server

$>./runserver.sh

## ejecutar la aplicación

### luego en un tab del browser poner

localhost:8000/docs
