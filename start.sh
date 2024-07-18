#!/bin/bash

exec python3 --version | python --version

NAME=pruebas
DIR=$PWD

cd $DIR

ls

exec uvicorn main:app --host 0.0.0.0 --port  8000 --reload
