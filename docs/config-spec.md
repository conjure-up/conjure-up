# Config Specification

```json
{
    "name": "bigdata",
    "version": "1.0.0",
    "summary": "Juju solutions for Big Data",
    "excerpt": "Choose your big data solution for the most streamlined approach to utilizing these tools to further bolster your business.",
    "maintainer": "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>",
    "bundles": [{
        "key": "apache-core-batch-processing",
        "name": "Apache MapReduce",
        "summary": "MapReduce is a software framework for easily writing applications which process vast amounts of data in-parallel on large clusters of machines."
    }, {
        "key": "apache-hadoop-spark",
        "name": "Apache Spark",
        "summary": "Extend the core MapReduce model to include the Apache Spark execution engine and take advantage of a fast general engine for large-scale data processing."
    }, {
        "key": "realtime-syslog-analytics",
        "name": "Apache Flume/Spark/Zeppelin",
        "summary": "An end-to-end Big Data solution that enables ingestion, processing, and visualization of log data"
    }, {
        "key": "apache-hadoop-spark-zeppelin",
        "name": "Apache Spark Streaming",
        "summary": "Leverage Spark's built-in ingestion support for twitter, local data and more.",
        "additionalQuestions": [
            {
                "key": "spark-username",
                "type": "string"
            },
            {
                "key": "spark-password",
                "type": "password"
            },
            {
                "key": "enable-admin",
                "type": "boolean"
            }
        ]
    }, {
        "key": "apache-analytics-pig",
        "name": "Data analytics with Apache Pig Latin",
        "summary": "Use Pig Latin to run analytics on your data by connecting Pig to Hadoop Core.",
        "blacklist": ["maas"]
    }, {
        "key": "apache-analytics-sql",
        "name": "Data analytics with SQL-like",
        "summary": "Connect Hive to Hadoop Core for SQL-like data analysis with a MySQL data warehouse.",
        "whitelist": ["maas"],
        "recommendedCharms": [
            "kibana"
        ]
    }],
    "bin":  "bigdata-install"
}
```

* `name, version, summary, excerpt, maintainer` are pretty self explanatory
* `bundles`: A list of key/value items describing what bundles are available for the installed package.
  * `key`: **required** This references the key name of the bundle usually found at the end of the charmstore URL
  * `name`: **required** Friendly name to display in selection view
  * `summary`: **required** Short summary of what the bundle does
  * `blacklist`: **optional** A list of providers to blacklist, if defined it will show all providers but those specified here.
  * `whitelist`: **optional** Opposite of `blacklist` if defined will only show these providers and hide the others.
  * `recommendedCharms`: **optional** A list of of recommended charms that would be useful for the bundle.
  * `additionalQuestions`: **optional** List of additional questions a bundle would require for deployment.
* `bin`: Mostly used in packaging the application for telling conjure what script to execute.

## Additional Questions

In order to define specific questions that should be answered for a particular bundle to work out of the box this section
allows you to define those and their types.

A list of supported types are:

* boolean - true/false input
* string - basic string input
* password - masked password string input
* integer - integer input

The *key* is what will be displayed to the user during input requests. Each key will then be exposed via enviroment variables
to be used in pre, post-bootstrap, and post processing tasks.

There are transformations on the key that will take place before being exported to the environment:

* Any keys with a hyphen '-' in its name will be replaced with an underscore '_'.
* All keys will be converted to UPPERCASE when exposed in the environment.

For example, a key with the name 'i-am-a-test' will be converted to 'I_AM_A_TEST' when exported.
