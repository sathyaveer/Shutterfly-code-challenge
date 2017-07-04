# Shutterfly-code-challenge: Calculation of simple Customer life time value and finding top top customers.

This repo contains python code that calculates customer life time value of each customer and returns top two customers based on customer life time value.
Note: This code can be used to return top ‘X’ (X can be any number) customers. In my input data, I have entries for five customers and returning top two customers. 
Total number of weeks (by considering global start and end times) in given a data set is four (4).

Software requirements, packages, execution:

This code is written in python 2.7 language. This code uses three standard python libraries: pandas, json, datetime. These libraries come with python 2.7. If there is any problem with unavailability of these libraries, please execute below command on command line.  Pip install library-name. Ex: pip install pandas.
Input data required for this program is there in ‘input’ folder with the name ‘input.json’.
Please execute this code either using command line: python name_of_the_module.py OR any IDE such as spyder, pycharm.

Design considerations & Assumptions:
•	Every event should have 'type' present. If type is empty, program will not consider that event. This design consideration is important as we should consider right type of events while calculating customer life time value and in future you may have some other events included in your input data set.
•	For event type 'SITE_VISIT', if there are multiple entries with same key, event_time, customer_id combination, program will consider those entries as redundant and keeps only one entry. I assume system sometimes writes same event multiple times because of some issues.
•	For event type 'SITE_VISIT', if customer_id is missing, program will discard that entry and will not be taken into consideration for further analysis.
•	For event type 'ORDER', if customer_id is missing, program will discard that entry and will not be taken into consideration for further analysis.
•	Customer can have only site visits and not have any orders in for a timeframe. So, program assign zero value to total expenditures.
•	For event type ‘ORDER’, if the value of ‘verb’ is UPDATE for order id, consider the latest total_amount of this updated order id based on time stamp (between timestamps of NEW and UPDATE order id, timestamp of UPDATE is latest). Remove the entry of NEW order for the same order_id. If there are multiple UPDATEs on same order id, consider the latest UPDATE.
There are two cases.
1)	For a given order id, there can be following verbs: NEW, UPDATE, UPDATE…In this case consider only last update (discard all previous UPDATEs and NEW).
2)	For a given order id, there can be only “NEW” verb in given time frame. Consider that ‘NEW’ entry.
•	Program assume that each ‘new order ‘will have only one entry in input data set.

Included all these exceptional scenarios as well in my test input data to test functionality of my code. 

Ouput result:
Output of program place in output folder. It has two files.
1)top_two_customers.csv: It has infomration about top tow customers with highest customer life time value.
2)customer_ltv.csv: It has information about all the customers with all the details such as CustomerId, Visits, TotalExpenditure, NumberOfWeeks, ExpenditurePerVisit, SiteVisitPerWeek, Customer life time value.

