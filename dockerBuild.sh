#!/bin/sh

apk add bash

pip install --upgrade pip
pip install -r requirements.txt

mkdir /static
mkdir /db
