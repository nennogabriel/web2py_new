#!/usr/bin/env bash
if [ -f "./web2py/web2py.py" ]
    then
        echo "web2py already downloded"
    else
        wget http://www.web2py.com/examples/static/web2py_src.zip
        unzip -o web2py_src.zip
        rm web2py_src.zip
fi

#if [ -d "node_modules" ]
#    then
#        echo "node modules already downloded"
#    else
#        npm install
#        npm i -g npm
#        npm i npm
#fi
#
#if [ -d "./web2py/applications/init/00_local" ]
#    then
#        echo "init/00_local folder already exists"
#    else
#        cp -rf "./web2py/applications/init/00_local.example" "./web2py/applications/init/00_local"
#fi
#
#if [ -d "./web2py/applications/init/static" ]
#    then
#        echo "init/static folder already exists"
#    else
#        cp -rf "./web2py/applications/init/static.example" "./web2py/applications/init/static"
#fi
#
#if [ -d "./web2py/app.yaml" ]
#    then
#        echo "app.yaml already exists"
#    else
#        cp "./web2py/app.example.yaml" "./web2py/app.yaml"
#fi
#
#
#
## Gulp is always good
#gulp sass
#gulp uglify
