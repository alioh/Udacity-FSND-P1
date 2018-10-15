# Project One: Logs Analysis
This is part of the Fullstack Nanodegree Udacity course. The project sets up a PostgreSQL database for a news website.
I have to find answers for three questions. I have three tables that I can find answers from: Authors, Log, Articles.
For this project I have to apply what I learn in the previous lessons with a real-world data.

## Requirements
Tools used in this project are:
- [Python 3.7](https://www.python.org/downloads/)
- [Vagrant](https://www.vagrantup.com/downloads.html)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 
- [Newsdata database](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)

to run the code, put in the share folder between your computer and VirtualBox.
Access using vagrant and cd /vagrant (this is your share folder between your VirtualBox and your PC).
Full guide on how to install and configure Vagrant is [here](https://www.udacity.com/wiki/ud088/vagrant).

To run the code:
```
python3 code.py
```

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
SELECT PATH,
       count(*) AS total_visits
FROM log
WHERE PATH <> '/'
GROUP BY PATH
ORDER BY total_visits DESC
LIMIT 3;
```
-----------------------------------

##### Popular Authors
Q2: Who are the most popular article authors of all time?
to answer this question, I created 2 views. First one will have the path/slug after fixing it to match the one in the slug column in the article table
The where statement checks if the path have the word article at the beginning because I saw some paths like: '/spam-spam-spam-humbug' '/%20%20%20''/+++ATH0',
which (i think) are not articles. I used SUBSTR to get the slug from the full path.
here is the view creation statement:
```
CREATE VIEW article_total_views AS
SELECT SUBSTR(PATH, 10) AS slug,
       count(*) AS total_visits
FROM log
WHERE PATH <> '/'
  AND PATH LIKE '/article/%'
GROUP BY PATH
ORDER BY total_visits DESC;
```
The second view is to group all article authors and sum all their views, creation statement:
```
CREATE VIEW article_views AS
SELECT author,
       sum(total_views) AS total_reads
FROM
  (SELECT articles.author AS author,
          cast(article_total_views.total_visits AS integer) AS total_views
   FROM article_total_views
   LEFT JOIN articles ON article_total_views.slug= articles.slug)AS authors_views
GROUP BY author
ORDER BY total_reads DESC;
```
after this I can now get the authors and their total articles visits using inner join between authors
reference:
- [SUBSTR](https://webfocusinfocenter.informationbuilders.com/wfappent/TLs/TL_srv_dm/source/sql_char21.htm)
- [CAST- to convert string to intger](https://stackoverflow.com/questions/10518258/typecast-string-to-integer-postgres) 

Final query to get the results:
```
SELECT authors.name,
       article_views.total_reads
FROM authors
LEFT JOIN article_views ON article_views.author = authors.id;
```

-----------------------------------

##### Errors more than 1%
Q3: On which days did more than 1% of requests lead to errors? 
I created a view to help answer this question, the view calculate total logs by date and the total of those log who were 200 OK.
here is the view creation statement:
```
CREATE VIEW total_visits_by_day_status AS
SELECT TO_CHAR(TIME :: DATE, 'MON dd, yyyy') AS date,
       count(status) AS total,
       SUM (CASE
                WHEN status = '404 NOT FOUND' THEN 0
                ELSE 1
            END) AS status_ok
FROM log
GROUP BY date;
```
Now all we have to do is do some math with python and answer this question.
- [Convert time to date format](http://www.postgresqltutorial.com/postgresql-date/) (MON dd,yyyy)
- [Get % in SQL](https://stackoverflow.com/questions/18721648/calculate-percent-difference-in-sql-server)

The query to answer the question is:
```
SELECT date, (total-status_ok)*100.0/total AS perc_error
FROM total_visits_by_day_status
```
