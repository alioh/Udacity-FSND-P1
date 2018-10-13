# Project One: PLogs Analysis


## SQL
Before answering the questions, lets know more about the tables

Schema |   Name   | Type  |
-------|---------|--------|
public | articles | table |
public | authors  | table |
public | log      | table |
--------------------------


#### Log Table
Column |           Type           |
-------|--------------------------|
path   | text                     |
ip     | inet                     |
method | text                     |
time   | timestamp with time zone |
status | text                     |
id     | integer                  |

An example of three rows from the log table:
```
('/', '192.0.2.194',  'GET',  '200 OK', datetime.datetime(2016, 7, 1, 7, 0, 5, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 1678928)
('/article/candidate-is-jerk', '198.51.100.195', 'GET', '200 OK', datetime.datetime(2016, 7,1, 7, 0, 47, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 1678924)
('/article/goats-eat-googles', '198.51.100.195', 'GET', '200 OK', datetime.datetime(2016, 7,1, 7, 0, 34, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 1678925)
```

#### Articles Table
Column |           Type           |
-------|--------------------------|
author | integer                  |
title  | text                     |
slug   | text                     |
lead   | text                     |
body   | text                     |
time   | timestamp with time zone |
id     | integer                  |

An example of three rows from the articles table:
```
(3, 'Bad things gone, say good people', 'bad-things-gone', 'All bad things have gone....', 'Bad things are a thing of the bad, ...', datetime.datetime(2016, 8, 15, 18, 55, 10, 814316, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 23)
(4, 'Balloon goons doomed', 'balloon-goons-doomed', 'The doom of balloon goons is....', datetime.datetime(2016, 8, 15, 18, 55, 10, 814316, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 24)
(1, 'Bears love berries, alleges bear', 'bears-love-berries', 'Rumors that bears...', 'Bear specified thatraspberries...', datetime.datetime(2016, 8, 15, 18, 55, 10, 814316, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)), 25)
```

### Authors Table
Column |  Type   |
-------|---------|
name   | text    |
bio    | text    |
id     | integer |

An example of three rows from the authors table:
```
('Ursula La Multa', 'Ursula La Multa is an expert on bears, bear abundance, and bear accessories.', 1)
('Rudolf von Treppenwitz', 'Rudolf von Treppenwitz is a nonprofitable disorganizer specializing in procrastinatory operations.', 2)
('Anonymous Contributor', "Anonymous Contributor's parents had unusual taste in names.", 3)
```

And this is how I got the results given before:
```
cur.execute("""SELECT * from authors""")
rows = cur.fetchall()
for i in range(3):  
    print(rows[i])
```
-----------------------------------

##### Popular Articles

Q1: What are the most popular three articles of all time?
to find that we need to check the logs of how many visitors to each article,
to find which are the most popular articles we need to find the logs and group them by the the path
in my query I put "where path <> '/'", because '/' is the home page of the news page and we only want to know the visits to articles.

Final query:
```
SELECT path, count(*) as total_visits from log where path <> '/' group by path order by total_visits desc limit 3;
```
-----------------------------------

##### Popular Authors
Q2: Who are the most popular article authors of all time?
to answer this question, I created 2 views. First one will have the path/slug after fixing it to match the one in the slug column in the article table
The where statement checks if the path have the word article at the beginning because I saw some paths like: '/spam-spam-spam-humbug' '/%20%20%20''/+++ATH0',
which (i think) are not articles. I used SUBSTR to get the slug from the full path.
here is the view creation statement:
```
create view article_total_views as SELECT SUBSTR(path,10) as slug, count(*) as total_visits from log where path <> '/' and path like '/article/%' group by path order by total_visits desc;
```
The second view is to group all article authors and sum all their views, creation statement:
```
create view article_views as select author, sum(total_views) as total_reads from (SELECT articles.author as author, cast(article_total_views.total_visits as integer) as total_views from article_total_views left join articles on article_total_views.slug= articles.slug)as authors_views group by author order by total_reads desc;
```
after this I can now get the authors and their total articles visits using inner join between authors
reference:
- [SUBSTR](https://webfocusinfocenter.informationbuilders.com/wfappent/TLs/TL_srv_dm/source/sql_char21.htm)
- [CAST- to convert string to intger](https://stackoverflow.com/questions/10518258/typecast-string-to-integer-postgres) 

Final query to get the results:
```
select  authors.name, article_views.total_reads from authors left join article_views on article_views.author = authors.id;
```

-----------------------------------

##### Errors more than 1%
Q3: On which days did more than 1% of requests lead to errors? 
The answer is by checking the status and time columns in log table. But first we need to find the total amount of logs whe have, I created view for that:
```
create view total_logs as select count(*) as total_logs from log;
```
Now all we have to do is do some math with python and answer this question.
- [Convert time to date format](http://www.postgresqltutorial.com/postgresql-date/) (MON dd,yyyy)

First query used to store the total:
```
select * from total_logs;
```
Second query to get logs grouped by date and status 404:
```
select status, TO_CHAR(time :: DATE, 'MON dd, yyyy') as date, count(*) as total_visits from log where status = '404 NOT FOUND' group by date, status;
```
