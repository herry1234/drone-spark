# drone-spark

This is a plugin for [drone.io](http://drone.io), a Continuous Integration and Deployment server.

***This plugin currently only supports Drone 0.4***

This plugin will allow you to send notifications using [Cisco Spark](http://ciscospark.com).

# Usage Examples

## .drone.yml

See [DOCS.md](DOCS.md) for how to configure and use the plugin.

## Python

```
python send_message.py
```

## Docker

```
docker run -rm  
-e PLUGIN_REPO_OWNER=herry \
-e PLUGIN_REPO_NAME=drs \
-e PLUGIN_REPO_FULL_NAME=drs \
-e PLUGIN_BUILD_NUMBER=1 \
-e PLUGIN_BUILD_BRANCH=master \
-e PLUGIN_BUILD_AUTHOR=HERRY \
-e PLUGIN_BUILD_AUTHOR_EMAIL=herry@gmail.com \
-e PLUGIN_BUILD_MESSAGE=Testing... \
-e PLUGIN_BUILD_STATUS=sucess \
-e PLUGIN_MESSAGE=# Sending Spark Message \n Using Markdown!!! \
-e PLUGIN_AUTH_TOKEN=N2ZjYWNjNDgtMGJjOS00ZWNjLThiN2EtZGJiMjVjYmU4NWRmOTU2ZWNiY2ItYjRk \
-e PLUGIN_roomName=herrytest \
drone-spark

```

# Roadmap and Plans

This plugin is in active development and has the following features planned

* Support for Drone 0.5
* Support for handlebar templating like other notification templates
* Support for referencing the environment variables used by Drone