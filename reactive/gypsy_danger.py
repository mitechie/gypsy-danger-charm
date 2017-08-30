import configparser
import os

from charms.reactive import (
    set_state,
    when,
    when_not,
)

from charmhelpers.core import hookenv as env

GRAFANA = 'grafana.ini'


@when_not('gypsy-danger.installed')
def install_gypsy_danger():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    env.log('Install gypsy-danger')
    set_state('gypsy-danger.installed')


@when('gypsy-danger.installed')
@when('db.available')
@when('grafana-source.available')
def is_running(*args):
    env.status_set('active', 'Ready')


@when('db.available')
def setup_mysql(mysql):
    env.log('Into setup mysql')
    env.log('Data Available')
    env.log(mysql.host())
    write_mysql_config(
        source_type='mysql',
        url="{}:{}/{}".format(mysql.host(), mysql.port(), mysql.database()),
        username=mysql.user(),
        password=mysql.password()
    )


@when_not('db.available')
def remove_mysql():
    """If the relation is broken remove the db connection info."""
    if os.path.isfile(GRAFANA):
        env.log('Removing {}'.format(GRAFANA))
        os.remove(GRAFANA)
    else:
        env.log('{} does not exist'.format(GRAFANA))

    env.status_set('blocked',
                   'Missing required relation to MySQL')


@when('grafana-source.available')
def setup_grafana(grafana):
    env.log('Into setup grafana')
    env.log('Data Available')
    env.log(grafana)
    dbconfig = read_mysql_config()
    if dbconfig:
        env.log('Sending Grafana all the datas')
        grafana.provide(
            dbconfig['source_type'],
            dbconfig['url'],
            'Gypsy Danger Data Source',
            username=dbconfig['username'],
            password=dbconfig['password']
            )
    else:
        env.log('No mysql config to use')


@when_not('grafana-source.available')
def remove_grafana():
    env.status_set('blocked',
                   'Missing required relation to Grafana')


def write_mysql_config(**kwargs):
    env.log('Writing ini for connecting to Grafana')
    config = configparser.ConfigParser()
    config['GRAFANA'] = {}
    for k, v in kwargs.items():
        config['GRAFANA'][k] = v

    # Writing our configuration file to 'example.cfg'
    with open(GRAFANA, 'w') as configfile:
        config.write(configfile)

    env.log('{} written'.format(GRAFANA))


def read_mysql_config():
    """Read the written ini file for Grafana data."""
    if os.path.isfile(GRAFANA):
        env.log('Found {} to read'.format(GRAFANA))

        config = configparser.ConfigParser()
        config.read(GRAFANA)
        return config['GRAFANA']
    else:
        env.log('{} not available to read'.format(GRAFANA))
        return None
