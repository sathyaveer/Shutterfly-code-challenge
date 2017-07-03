# -*- coding: utf-8 -*-
"""

Customer life time value calculation

Created on Sun Jul 02 15:31:47 2017

@author: Sathyaveer
"""

# Standard module imports
from datetime import date, datetime
import json
import pandas as pd


def main():
    order, visit = input_process()
    customers = simple_ltv_customers(order, visit)
    print customers
    
def input_process():
    """
    This method reads the input data from json file from local directory 
    location and filters the input json data based on events(orders, visits, image upload, customer).
    In this case data are filterd by evnts orders and visits.
    
    Output:
    * order_df(dataframe): dataframe that has data about customer orders event
    * site_visit_df(dataframe): dataframe that has data about site visits by customers
    
    """
    order_list = []
    site_visit_list =[]
    with open(r'D:\Shutterfly\input\input.json') as input_data:
        json_data = json.load(input_data)
    for event in json_data:
        if event['type'] == 'ORDER':
            event_time = datetime.strptime(str(event['event_time']), '%Y-%m-%dT%H:%M:%S.%fZ')
            amount = float(event['total_amount'].split(' ')[0])       # separates amount from USD, and takes only amount
            week_number = int(event_time.strftime('%U'))        #returns week number of event time
            order_list.append([str(event['customer_id']), event_time, amount, week_number])
        if event['type'] == 'SITE_VISIT':
            event_time = datetime.strptime(str(event['event_time']), '%Y-%m-%dT%H:%M:%S.%fZ')
            week_number = int(event_time.strftime('%U'))        #returns week number of event time
            visit = 1               #number for each visit to site 
            site_visit_list.append([str(event['customer_id']), event_time, week_number, visit])
        else:
            pass
    
    order_df = pd.DataFrame(order_list, columns=['CustomerId', 'EventTime', 'Amount', 'WeekNumber'])
    site_visit_df = pd.DataFrame(site_visit_list, columns=['CustomerId', 'EventTime', 'WeekNumber', 'Visits'])
    
    return order_df, site_visit_df
    
def simple_ltv_customers(order_df, site_visit_df):
    """
    This method calculates life time value of each customer and 
    return top two customer id
    
    Input:
    * order_df(dataframe): dataframe that has data about customer transactions such as
                           customer_id, time of transaction, amount they spent, week number in
                           which given time of transaction falls.
    * site_visit_df(dataframe): dataframe has data about customer visits to website such as 
                                custommer id, time visited, week number in
                                which given time visited falls, count for each visit
                                
    Output:
    * Customer id(list): list of customer ids with highest life time value
    
    """
    avg_cust_lifespan = 10
    no_of_weeks = max(site_visit_df['WeekNumber']) - min(site_visit_df['WeekNumber']) + 1
    
    # calculates total expenditure of each customer in a given timeframe.
    # The resultant dataframe has two columns: CustomerId, Amount.
    order_ser = order_df.groupby(['CustomerId'])['Amount'].sum()   
    order_df = order_ser.reset_index()
    
    # calculates number of customer visits of each customer in a given timeframe.
    # The resultant dataframe has two columns: CustomerId, Visits.
    site_visit_ser = site_visit_df.groupby('CustomerId')['Visits'].count()   
    site_visit_df = site_visit_ser.reset_index()
    
    visit_order_df = pd.merge(site_visit_df, order_df, on = 'CustomerId', how='left')
    visit_order_df.fillna(0, inplace=True)      #useful when customer has visited site but no orders in a given timeframe
    visit_order_df['ExpenditurePerVisit'] = visit_order_df['Amount'] / visit_order_df['Visits']
    visit_order_df['SiteVisitPerWeek'] = visit_order_df['Visits'] / no_of_weeks
    visit_order_df['CustomerLTV'] = visit_order_df['ExpenditurePerVisit'] * visit_order_df['SiteVisitPerWeek']
    visit_order_df['CustomerLTV'] = visit_order_df['CustomerLTV'] * 52 * avg_cust_lifespan
    visit_order_df.sort_values(by = 'CustomerLTV', inplace=True, ascending=False)
    
    return list(visit_order_df.head(2)['CustomerId'])
    
    
if __name__ == "__main__":
    main()
    
