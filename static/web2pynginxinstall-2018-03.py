#!/bin/env python2.7

"""
Web2py install/uninstall script for WebFaction using the latest stable source
code from http://www.web2py.com/examples/static/web2py_src.zip.

This installs web2py for Python 2.7, served via Nginx 1.8.0 and uWSGI 2.0.10.

The web2py files are found in ~/webapps/<app_name>/web2py.

IMPORTANT: Remember to set the Admin password in the extra_info field.

Caveats
-------

* Web2py won't work properly if it is mounted to a sub-URL like
http://domain.com/web2py/. Instead, it must be mounted to the website root,
e.g. http://domain.com/

* For the administrative interface to work, the web2py app must be mounted to and
accessed through an HTTPS-enabled site. You would usually mount the app to two
websites - HTTPS-disabled one for normal access, and HTTPS-enabled one for admin
logins.

"autostart": not applicable
"extra info": Password for administrative interface
"""

import sys
import xmlrpclib

def hash_password(plaintext):
    """Standardized method for hashing password"""
    from hashlib import md5
    return md5(plaintext).hexdigest()

def create(server, session_id, account, username, app_name, autostart, extra_info, password):
    # Make sure there is the last stable versions
    nginx = 'nginx-1.12.2'
    uwsgi = 'uwsgi-2.0.15'

    # Create application.
    app = server.create_app(session_id, app_name, 'custom_app_with_port')
    appname = app['name']
    port = app['port']

    # install Nginx
    cmd = """
    mkdir -p {bin,nginx,src,tmp,lib/python2.7}
    cd /home/%(username)s/webapps/%(appname)s/src
    wget -q 'http://nginx.org/download/%(nginx)s.tar.gz'
    tar -xzf %(nginx)s.tar.gz
    rm %(nginx)s.tar.gz
    cd %(nginx)s
    ./configure \
      --prefix=/home/%(username)s/webapps/%(appname)s/nginx \
      --error-log-path=/home/%(username)s/logs/user/error_%(appname)s.log \
      --http-log-path=/home/%(username)s/logs/user/access_%(appname)s.log \
      > /dev/null
    make > /dev/null
    make install > /dev/null
    """ % locals()
    server.system(session_id, cmd)

    # install uwsgi
    cmd = """
    cd /home/%(username)s/webapps/%(appname)s/src
    wget -q 'http://projects.unbit.it/downloads/%(uwsgi)s.tar.gz'
    tar -xzf %(uwsgi)s.tar.gz
    rm %(uwsgi)s.tar.gz
    cd %(uwsgi)s
    python2.7 uwsgiconfig.py --build > /dev/null
    mv ./uwsgi /home/%(username)s/webapps/%(appname)s/bin
    ln -s /home/%(username)s/webapps/%(appname)s/nginx/sbin/nginx /home/%(username)s/webapps/%(appname)s/bin

    mkdir -p /home/%(username)s/webapps/%(appname)s/nginx/tmp/nginx/client

    cat << EOF > /home/%(username)s/webapps/%(appname)s/nginx/conf/nginx.conf
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    access_log  /home/%(username)s/logs/user/access_%(appname)s.log combined;
    error_log   /home/%(username)s/logs/user/error_%(appname)s.log  crit;

    include mime.types;
    sendfile on;

    server {
        listen 127.0.0.1:%(port)d;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:///home/%(username)s/webapps/%(appname)s/uwsgi.sock;
        }
    }
}
EOF
    """ % locals()
    server.system(session_id, cmd)

    # install web2py
    cmd = """
    cd /home/%(username)s/webapps/%(appname)s/src
    wget -q 'http://www.web2py.com/examples/static/web2py_src.zip'
    cd ..
    unzip -qq src/web2py_src.zip
    rm src/web2py_src.zip
    cp ./web2py/handlers/./wsgihandler.py ./web2py/
    """ % locals()
    server.system(session_id, cmd)

    # create paramaters_80.py
    assert extra_info
    server.system(session_id, "echo 'password=\"%s\"' > web2py/parameters_%s.py" % (hash_password(extra_info), port))

    # make the start, stop, and restart scripts
    cmd = """
    cat << EOF > /home/%(username)s/webapps/%(appname)s/bin/start
#!/bin/bash

# Start uwsgi
/home/%(username)s/webapps/%(appname)s/bin/uwsgi \\
  --uwsgi-socket "/home/%(username)s/webapps/%(appname)s/uwsgi.sock" \\
  --master \\
  --workers 2 \\
  --max-requests 10000 \\
  --harakiri 60 \\
  --daemonize /home/%(username)s/logs/user/uwsgi_%(appname)s.log \\
  --pidfile /home/%(username)s/webapps/%(appname)s/uwsgi.pid \\
  --vacuum \\
  --chdir /home/%(username)s/webapps/%(appname)s \\
  --python-path /home/%(username)s/webapps/%(appname)s/lib/python2.7 \\
  --wsgi-file /home/%(username)s/webapps/%(appname)s/web2py/wsgihandler.py \\

# Start nginx
/home/%(username)s/webapps/%(appname)s/bin/nginx
EOF

    cat << EOF > /home/%(username)s/webapps/%(appname)s/bin/stop
#!/bin/bash

APPNAME=%(appname)s

# stop uwsgi
/home/%(username)s/webapps/%(appname)s/bin/uwsgi --stop \/home/%(username)s/webapps/%(appname)s/uwsgi.pid

# stop nginx
/home/%(username)s/webapps/%(appname)s/bin/nginx -s stop
EOF

    cat << EOF > /home/%(username)s/webapps/%(appname)s/bin/restart
#!/bin/bash

APPNAME=%(appname)s

/home/%(username)s/webapps/%(appname)s/bin/stop
sleep 5
/home/%(username)s/webapps/%(appname)s/bin/start
EOF

    chmod 755 /home/%(username)s/webapps/%(appname)s/bin/{start,stop,restart}
    """ % locals()
    server.system(session_id, cmd)



    # TODO start the app
    cmd = "/home/%(username)s/webapps/%(appname)s/bin/start 2>&1 >/dev/null" % locals()
    server.system(session_id, cmd)

    print app['id']


def delete(server, session_id, account, username, app_name, autostart, extra_info, password):
    # TODO stop the app
    cmd = "/home/%(username)s/webapps/%(app_name)s/bin/stop 2>&1 >/dev/null" % locals()
    server.system(session_id, cmd)
    # Delete the application
    server.delete_app(session_id, app_name)


if __name__ == '__main__':
    command, username, password, machine, app_name, autostart, extra_info = sys.argv[1:]

    # Connect to API server and login
    url = 'https://api.webfaction.com/'
    server = xmlrpclib.ServerProxy(url)
    session_id, account = server.login(username, password, machine)

    # Call create or delete method
    method = locals()[command] # create or delete
    method(server, session_id, account, username, app_name, autostart, extra_info, password)
