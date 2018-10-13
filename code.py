#---------------------------------------------------#
#                   Ali Alohali                     #
#                    alioh.com                      #
#                                                   #
#    Udacity Full Stack Web Developer Nanodegree    #
#           Project One: Logs Analysis              #
#     Read README.md file for more explanation      #
#---------------------------------------------------#

import psycopg2
#   database connection - add the code to vagrant folder and run it in virtualbox
#   psycopg2 doc: https://wiki.postgresql.org/wiki/Psycopg2_Tutorial
conn = psycopg2.connect(database="news")
cur = conn.cursor()

#   Q1
cur.execute("""SELECT path, count(*) as total_visits from log where path <> '/' group by path order by total_visits desc limit 3""")
rows = cur.fetchall()
q1   = []
for row in rows:
    q1.append(row)

#   fix the output
#   here I loop the list i previously created, I replaces/removed '/article/' in the path and then replace each '-' with a space. then I used python method .title()
#   to make the result look better, I then added the number of visit after I changed its type to string so i can concatenate it with the title
print('Q1: What are the most popular three articles of all time?')
print('    Title      /    Total visits')
for i in range(3):
    print(q1[i][0].replace('/article/','').replace('-',' ').title() + '        ' + str(q1[i][1]))


#   Q2
cur.execute(""" select  authors.name, article_views.total_reads from authors left join article_views on article_views.author = authors.id """)
rows = cur.fetchall()
q2   = []
for row in rows:
    q2.append(row)

#   fix the output -- similar to what I did in first question
print('\n\nQ2: Who are the most popular article authors of all time?')
print('    Author      /    Total visits')
for i in range(3):
    print(q2[i][0].title() + '        ' + str(q2[i][1]))


#   Q3
#   first we get the total, it return as tuple so I convert it to list then just got the total number.
cur.execute(""" select * from total_logs """)
row = cur.fetchall()
total = list(row[0])[0]
cur.execute(""" select status, TO_CHAR(time :: DATE, 'MON dd, yyyy') as date, count(*) as total_visits from log where status = '404 NOT FOUND' group by date, status """)
rows = cur.fetchall()

print('\n\nQ3: On which days did more than 1% of requests lead to errors? ')
print("   Date          Total errors %")

#   I ran this query to check and print the days when errors was larger than 1%
for row in rows:
    if  (round(row[2]/total,5)*100) > 0.01:
        print(row[1] + '          ' + "{0:.0%}".format(round(row[2]/total,5)*100))
