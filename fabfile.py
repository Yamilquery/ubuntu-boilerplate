from fabric.api import *
from fabric.contrib.console import confirm



@task
def build(flavor=None):
    if flavor == 'app':
        postgres = False
        nginx = True
        memcached = True
        redis = False
        rabbitmq = True
        supervisor = True
    elif flavor == 'db':
        postgres = True
        nginx = False
        memcached = False
        redis = True
        rabbitmq = False
        supervisor = False
    elif flavor == 'web':
        postgres = False
        nginx = True
        memcached = False
        redis = False
        rabbitmq = False
        supervisor = False
    else:
        postgres = confirm("Install PostgreSQL?", default=False)
        nginx = confirm("Install NGINX?", default=False)
        memcached = confirm("Install Memcached?", default=False)
        redis = confirm("Install Redis?", default=False)
        rabbitmq = confirm("Install RabbitMQ?", default=False)
        supervisor = confirm("Install Supervisor?", default=False)

    run('apt-get update -q')
    run('apt-get upgrade -qy')
    run('apt-get install git-core vim -qy')
    run('update-alternatives --set editor /usr/bin/vim.basic')

    put('./sudoers', '/etc/sudoers', mode=0440)

    run('locale-gen en_US.UTF-8')
    run('update-locale LANG=en_US.UTF-8')
    run('ln -sfn /usr/share/zoneinfo/America/New_York /etc/localtime')

    put('./bash.bashrc', '/etc/bash.bashrc', mode=0644)
    put('./root.bashrc', '/root/.bashrc', mode=0644)
    put('./skel.bashrc', '/etc/skel/.bashrc', mode=0644)
    run('touch /etc/skel/.hushlogin')

    put('./iptables', '/etc/network/iptables', mode=0644)
    put('./iptables-start', '/etc/network/if-pre-up.d/iptables', mode=0755)
    run('iptables-restore < /etc/network/iptables')

    put('./sshd_config', '/etc/ssh/sshd_config', mode=0644)

    # Create admin user
    import string
    import random
    import crypt

    characters = string.letters + string.digits + '!@#$%^&*()-_=+~{[}],.<>?'
    password_size = 30
    # A possible 10,838,109,570,573,913,960,623,703,697,505,423,039,374,700,588,527,754,674,176
    # variations with this algorithm
    admin_password = ''.join((random.choice(characters) for x in range(password_size)))

    salt_characters = string.letters + string.digits
    salt = ''.join((random.choice(salt_characters) for x in range(3)))

    admin_crypt = crypt.crypt(admin_password, salt)

    run('useradd admin -Um -s /bin/bash -p %s' % admin_crypt)

    # Python 3.x stuff
    run('apt-get install build-essential gcc python3-dev python3-setuptools bash-completion htop ipython3 -qy')
    run('easy_install3 pip')
    run('pip install ipdb virtualenv')
    run('apt-get install git-core mercurial subversion -qy')
    run('apt-get install python3-imaging libpq-dev -qy')

    if postgres:
        run('apt-get install postgresql-server-dev-9.1 postgresql-9.1 -qy')

    if nginx:
        run('apt-get install nginx -qy')
        put('./nginx.conf', '/etc/nginx/nginx.conf', mode=0644)
        put('./proxy_params', '/etc/nginx/proxy_params', mode=0644)

    if memcached:
        run('apt-get install memcached -qy')

    if redis:
        run('apt-get install redis-server -qy')

    if rabbitmq:
        run('apt-get install rabbitmq-server -qy')

    if supervisor:
        run('apt-get install supervisor -qy')

    print "\n\nADMIN PASSWORD\n\n%s\n\n" % admin_password