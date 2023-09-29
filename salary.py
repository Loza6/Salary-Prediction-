# -*- coding: utf-8 -*-
"""Salary.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sj3kFdYZ8I5X8VM-sD48ICaIvlHi_O0K

HOMEWORK 3
"""

import matplotlib.pyplot as plt
from google.colab import files
import seaborn as sb
import sqlite3
import pandas
import numpy
import io

conn = sqlite3.connect('lahman2014.sqlite')

salary_query = "SELECT yearID, sum(salary) as total_payroll FROM Salaries WHERE lgID == 'AL' GROUP BY yearID"

team_salaries = pandas.read_sql(salary_query, conn)
team_salaries.head()

"""# **PART 1: Wrangling**

> **Problem 1**

# Description:
'Teams' was chosen to left join 'Salaries' to make sure that thier representation was complete

Since The National League and AllStart League are the focus for this assignment, all other leagues' data was dropped
"""

query = \
'''
select teams.teamid, teams.yearid, teams.w, teams.l, teams.g, teams.franchid, salaries.lgid, sum(salaries.salary) as payroll
from teams
left join
salaries
on
teams.teamid = salaries.teamid
and
teams.yearid = salaries.yearid
group by
teams.teamid, teams.yearid
'''

teamData = pandas.read_sql(query, conn)

teamData['win %'] = (teamData['W']/teamData['G'])*100

teamData = teamData[teamData['lgID'].notna()]
teamData = teamData.sort_values('win %')

print(teamData)

"""# **Part 2: Exploratory Data Analysis**

> **Problem 2**
"""

query = \
'''
select teams.teamid, teams.yearid, salaries.lgid, sum(salaries.salary) as total_salary
from teams
inner join
salaries
on
teams.teamid = salaries.teamid
and
teams.yearid = salaries.yearid
where
teams.yearid > 1989
and
teams.yearid <2015
group by
teams.teamid, teams.yearid
order by
teams.yearid
'''

df = pandas.read_sql(query, conn)
teams = df.teamID.unique()

rows = 7
columns = 5

count = 0

plt.rcParams["figure.figsize"] = (25,25)

for team in teams:
  count+=1

  plt.subplot(rows, columns, count)
  x_values = df[df.teamID == team]['yearID']
  y_values = df[df.teamID == team]['total_salary']
  plt.plot(x_values, y_values)
  plt.grid()
  plt.xlabel('years')
  plt.ylabel('salary')
  plt.legend([team])

plt.suptitle("Salary VS time for all 35 teams between the years 1990 and 2014" , fontsize=20)
plt.show()

"""> **Question 1**

A statemnt that can be made about the distribution of payrolls over time is that the mean salary of all the teams has increased 8 fold between the years 1990 and 2014

> **Problem 3**
"""

query = \
"""
select teams.yearid, avg(salaries.salary) as mean
from teams
left join
salaries
on
teams.teamid = salaries.teamid
and
teams.yearid = salaries.yearid
where
teams.yearid > 1989 and teams.yearid <2015
group by
teams.yearid
order by
teams.yearid
"""
df = pandas.read_sql(query, conn)

x_means = df['yearID']
y_means = df['mean']

plt.plot(x_means, y_means)
plt.scatter(x_means, y_means, color = "r")
plt.grid()
plt.xlabel("Years")
plt.ylabel("mean salary")
plt.title("Mean Salary of all teams/players over the years")
plt.rcParams["figure.figsize"] = (10,10)
plt.show()

"""> **Problem 4**"""

query = \
'''
select
salaries.teamID, salaries.yearID, teams.W, teams.G, salaries.salary
from salaries
inner join
teams
on
teams.yearID = salaries.yearID
and
teams.teamID = salaries.teamID
group by salaries.teamID, salaries.yearID
order by salaries.yearID
'''
df = pandas.read_sql(query, conn)
df['win_percentage'] = (df['W']/df['G'])*100

def plot_graph(means, year_ranges):

  rows = 2
  columns = 3

  count = 0

  plt.rcParams["figure.figsize"] = (20,10)

  for item in means:
    temp_item = pandas.DataFrame({"payroll":item[0], "wins":item[1]}).sort_values('payroll')

    count+=1

    plt.subplot(rows, columns, count)
    plt.scatter(temp_item['payroll'], temp_item['wins'], color = "r")
    plt.xlabel("Mean Salary")
    plt.ylabel("Mean Win %")

    plt.title(str(year_ranges[count-1]))
    plt.grid()
  plt.suptitle("Mean Win % VS Mean Payroll (each point is a consecutive year)")
  plt.show()

def get_means(df, year_ranges):


  means = []

  for range in year_ranges:
    lower_limit = range[0]
    upper_limit = range[1]

    range_df = df[(df['yearID']>= lower_limit) & (df['yearID'] < upper_limit)]
    years = range_df['yearID'].unique()

    payroll_means = []
    percentage_means = []

    for year in years:
      temp_df = range_df[range_df['yearID'] == year]

      payroll_means.append(temp_df['salary'].mean())
      percentage_means.append(temp_df['win_percentage'].mean())

    means.append([payroll_means, percentage_means])

  return means

year_ranges = [[1985,1990], [1990,1995], [1995,2000], [2000,2005], [2005,2010], [2010, 2015]]
means = get_means(df, year_ranges)
plot_graph(means, year_ranges)

"""> **Question 2**

# Description:
 It appears that there isn't much correlation between the average of the payroll and the avereage of the win percentage. As the mean payroll increases, there is no consistent increase in the mean win percentage.

# **Part 3: Data transformations**

>**Problem 5**
"""

year_ranges = [[1985,1990], [1990,1995], [1995,2000], [2000,2005], [2005,2010], [2010, 2015]]

for range in year_ranges:
  lower_limit = range[0]
  upper_limit = range[1]

  range_df = df[(df['yearID']>= lower_limit) & (df['yearID'] < upper_limit)]
  teams = range_df['teamID'].unique()

  payroll_means = []
  percentage_means = []

  for team in teams:
    temp = df[(df['yearID']>= lower_limit) & (df['yearID'] < upper_limit) & (df['teamID'] == team)]
    temp['salary'] = (temp['salary'] - temp['salary'].mean())/temp['salary'].std()
    df[(df['yearID']>= lower_limit) & (df['yearID'] < upper_limit) & (df['teamID'] == team)] = temp

df.head()

""">**Problem 6**"""

means = get_means(df, year_ranges)
plot_graph(means, year_ranges)

""">**Question 3**

# Description:
In comparing the two variables and the effects it had on the graphs, we see that the bias has a severe effect on the represenation of the data. By normalising the 'mean salary' to a range similar to that of the mean winning percentage, we are given a much more accurate plot

>**Problem 7**
"""

query = \
'''
select
salaries.teamID, salaries.yearID, teams.W, teams.G, salaries.salary
from salaries
inner join
teams
on
teams.yearID = salaries.yearID
and
teams.teamID = salaries.teamID
group by salaries.teamID, salaries.yearID
order by salaries.yearID
'''
df = pandas.read_sql(query, conn)
df['win_percentage'] = (df['W']/df['G'])*100

df['salary'] = (df['salary'] - df['salary'].mean())/df['salary'].std()

sb.regplot(x = "salary", y = "win_percentage", ci = None, data = df)

""">**Problem 8**"""

df['expected_win%'] = 50 + 2.5*df['salary']
df['efficiency'] = df['win_percentage'] - df['expected_win%']

df.head()

selected_teams = ['OAK', 'BOS', 'NYA', 'ATL', 'TBA']

for team in selected_teams:
  plt.scatter(df[df['teamID']== team]['yearID'], df[df['teamID']== team]['efficiency'])
  plt.plot(df[df['teamID']== team]['yearID'], df[df['teamID']== team]['efficiency'])

plt.rcParams["figure.figsize"] = (20,5)
plt.xlabel("Years")
plt.ylabel("Efficiency")
plt.title("Efficiency of 6 teams plotted throughout the years")
plt.legend(['OAK', 'BOS', 'NYA', 'ATL', 'TBA']);
plt.grid()
plt.show()

""">**Question 4**

# Description:
Over the years, The (Oaklands As) had noticable increase in efficiency during various years, from 1987-1993 and 1993-1997, with the 1987-1993 being a period of high efficency and the latter being a time of low efficiency. In the 1985 - 1990 period the leading team NYA dropped to the second worst team in 1990 while OAK became the best team in 1990

In the MoneyBall period, The Oaklands As saw a consistent increase in efficiency, which they were able to maintain for a longer period compared to their previous years. It should also be noted that they were able to maintain this increase in efficeincy while the other teams saw a decrease in efficiency.
"""