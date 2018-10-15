#!/usr/bin/env python3
#####################################################
#                   Ali Alohali                     #
#                    alioh.com                      #
#                                                   #
#    Udacity Full Stack Web Developer Nanodegree    #
#           Project One: Logs Analysis              #
#     Read README.md file for more explanation      #
#####################################################

import psycopg2
#   database connection - add the code to vagrant folder
#   and run it in virtualbox
#   psycopg2 doc: https://wiki.postgresql.org/wiki/Psycopg2_Tutorial
conn = psycopg2.connect(database="news")
cur = conn.cursor()

#   Q1
query1 = """
SELECT PATH,
       count(*) AS total_visits
FROM log
WHERE PATH <> '/'
GROUP BY PATH
ORDER BY total_visits DESC
LIMIT 3"""

cur.execute(query1)
rows = cur.fetchall()
q1 = []
for row in rows:
    q1.append(row)

#   Fixing the output:
#   here I loop the list i previously created, I replaces/removed
#   '/article/' in the path and then replace each '-' with a space.
#   then I used python method .title() to make the result look better,
#   I then added the number of visit after I changed its type to string
#   so i can concatenate it with the title
print('Q1: What are the most popular three articles of all time?')
print('    Title      /    Total visits')
for i in range(3):
    print(q1[i][0].replace('/article/', '').replace('-', ' ').title() +
          '        ' + str(q1[i][1])
          )


#   Q2
query2 = """
SELECT authors.name,
       article_views.total_reads
FROM authors
LEFT JOIN article_views ON article_views.author = authors.id
"""

cur.execute(query2)
rows = cur.fetchall()
q2 = []
for row in rows:
    q2.append(row)


#   fix the output -- similar to what I did in first question
print('\n\nQ2: Who are the most popular article authors of all time?')
print('    Author      /    Total visits')
for i in range(3):
    print(q2[i][0].title() + '        ' + str(q2[i][1]))


#   Q3
#   first we get the total, it return as tuple so I convert it to
#   list then just got the total number.

query3 = """
SELECT date, (total-status_ok)*100.0/total AS perc_error
FROM total_visits_by_day_status
"""

cur.execute(query3)
rows = cur.fetchall()

print('\n\nQ3: On which days did more than 1% of requests lead to errors? ')
#   I ran this query to check and print the days when errors was larger than 1%
for row in rows:
    if row[1] > 1:
        print('On {}, Error percentage was {}%.'.format(row[0],
              round(row[1], 2)))
