#! /bin/sh

# This is a modified version of the osm2po demo that comes with the JAR file.
#
# I just changed the reference to refer to the Minnesota PBF which I had already downloaded.
#

java -Xmx1g -jar osm2po-core-5.1.0-signed.jar prefix=hh tileSize=x ../minnesota-latest.osm.pbf postp.0.class=de.cm.osm2po.plugins.postp.PgRoutingWriter
