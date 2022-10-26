# OpenSearch SQL

Using the Query Workbench in OpenSearch Dashboards (ie. Kibana) we can use SQL to perform queries.

In the OpenSearch Dashboards go to `OpenSearch Plugins > Query Workbench` and then you can type SQL queries like the following:

```
SHOW TABLES LIKE 'mov%';

DESCRIBE TABLES LIKE movies-tuned;

SELECT * FROM movies-tuned LIMIT 10;

SELECT year, title FROM movies-tuned ORDER BY year LIMIT 10;

SELECT year, title FROM movies-tuned ORDER BY year DESC LIMIT 10;

SELECT year, title FROM movies-tuned WHERE year=1995 LIMIT 5;

SELECT year, title FROM movies-tuned WHERE year>=2000 AND year<=2005 LIMIT 5;

SELECT title, year FROM movies-tuned WHERE title LIKE 'harry';
```

WARNING: Keep in mind that this is much more limitted than using the Elasticsearch Query DSL language, but it is an option that we have since elasticsearch version 7.

## Exercises
- Lab: open the Query Workbench and run some queries like the above.

## References
- [Basic Queries](https://opensearch.org/docs/latest/search-plugins/sql/sql/basic/)
- [Metadata queries](https://opensearch.org/docs/latest/search-plugins/sql/sql/metadata/)
