# intermix.io Python Plugin

## Introduction

The intermix.io Python plugin is a set of code that inline annotates running SQL queries. It does this by prepending 
the query with a SQL comment containing metadata about the query itself. Our service currently supports Redshift, 
support for other databases is coming. This does not slow down query execution or affect the logical execution of the
code. It is used to provide data inside our analytics service. For more information: 
[documentation site](http://docs.intermix.io/plugins)

## Installation

Run `pip install intermix` and add the package to your requirements.txt. Or you can install from source by cloning and
running `python setup.py install`.

## Getting Started

Lets say you have a query `select count(*) from users;` that you execute in a batch process. To use the annotation
feature you would do the following:

```python
# Top of file
import intermix

# A bunch of your code
sql = "select count(*) from users;"
# The line below does the annotation.
sql = intermix.annotate(sql, app='my_app', app_ver='my_app_version1', dag='batch', task='user_count')
# Code that executes the SQL
# More of your code
```

## Questions

For questions and support please contact support@intermix.io.

## Contributing

If you're looking to contribute, please contact us at support@intermix.io.

## About Intermix

intermix.io ([http://intermix.io](http://intermix.io)) is a product that instruments Amazon Redshift to provide 
performance analytics. It helps Redshift adminstrators to:

- optimize WLM to maximize throughput and memory utilization
- monitor user behavior (ad hoc queries, batch jobs, etc.)
- root cause analysis of issues impacting your cluster
- predict storage growth and deep visilibty into storage utilization
- optimize dist and sort keys

We offer a free trial and procurement via [AWS Marketplace](https://aws.amazon.com/marketplace/pp/B0764JGX86?qid=1513291438437&sr=0-2&ref_=srh_res_product_title).

## License

This software is published under the MIT license.  For full license see the [LICENSE file](https://github.com/intermix/python-plugin/master/LICENSE.txt).
