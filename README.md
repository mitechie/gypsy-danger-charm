# Overview

Gypsy Danger will process Apache log data into a MySQL server for querying of
data. It will then enable wiring up to Grafana to create dashboards based on
queries into MySQL.


# Usage

juju deploy gypsy-danger
juju deploy mysql
juju deploy grafana
juju relate mysql:db gypsy-danger
juju relate grafana:grafana-source gypsy-danger


## Known Limitations and Issues

Doesn't currently install the Gypsy Danger python package automatically. It
only connect to the relations and works to try to get MySQL info into Grafana
for querying.

# Configuration

No current config.


# Contact Information

Hit me up Rick Harding <rick.harding@canonical.com>
