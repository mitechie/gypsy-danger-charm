import configparser
import os

from charms.reactive import (
    set_state,
    when,
    when_not,
)

from charmhelpers.core import hookenv

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
    hookenv.log('Install gypsy-danger')
    set_state('gypsy-danger.installed')


@when('db.available')
def setup_mysql(mysql):
    hookenv.log('Into setup mysql')
    hookenv.log('Data Available')
    hookenv.log(mysql.host())
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
        hookenv.log('Removing {}'.format(GRAFANA))
        os.remove(GRAFANA)
    else:
        hookenv.log('{} does not exist'.format(GRAFANA))


@when('grafana-source.available')
def setup_grafana(grafana):
    hookenv.log('Into setup grafana')
    hookenv.log('Data Available')
    hookenv.log(grafana)
    dbconfig = read_mysql_config()
    if dbconfig:
        hookenv.log('Sending Grafana all the datas')
        grafana.provide(
            dbconfig['source_type'],
            dbconfig['url'],
            'Gypsy Danger Data Source',
            username=dbconfig['username'],
            password=dbconfig['password']
            )
    else:
        hookenv.log('No mysql config to use')


@when_not('grafana-source.available')
def remove_grafana():
    pass


def write_mysql_config(**kwargs):
    hookenv.log('Writing ini for connecting to Grafana')
    config = configparser.ConfigParser()
    config['GRAFANA'] = {}
    for k, v in kwargs.items():
        config['GRAFANA'][k] = v

    # Writing our configuration file to 'example.cfg'
    with open(GRAFANA, 'w') as configfile:
        config.write(configfile)

    hookenv.log('{} written'.format(GRAFANA))


def read_mysql_config():
    """Read the written ini file for Grafana data."""
    if os.path.isfile(GRAFANA):
        hookenv.log('Found {} to read'.format(GRAFANA))

        config = configparser.ConfigParser()
        config.read(GRAFANA)
        return config['GRAFANA']
    else:
        hookenv.log('{} not available to read'.format(GRAFANA))
        return None
