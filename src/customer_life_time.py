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


N = 2     # number of top customers that this program has to return 
AVG_CUST_LIFESPAN = 10

def main():
    """
    This is main function and entery point for the entire script. It calls other
    functions to filter data, to preprocess data, and to calculate simple
    customer life time value. At the end stores top customers in a file.
    """
    
    order, visit = ingest()
    order_final, visit_final = pre_process(order, visit)
    top_customers = top_two_simple_ltv_customers(order_final, visit_final)
    top_customers.to_csv(r'D:\Shutterfly-code-challenge\output\top_two_customers.csv', index=False)    
    
def ingest():
    """
    This function reads the input data from json file from local directory
    location and filters the input json data based on events(orders, visits, image upload, customer).
    In this case data are filterd by evnts orders and visits.
    
    Output:
    * order_df(dataframe): dataframe that has data about customer orders event
    * site_visit_df(dataframe): dataframe that has data about site visits by customers
    
    """
    order_list = []
    site_visit_list = []
    with open(r'D:\Shutterfly-code-challenge\input\input.json') as input_data:
        json_data = json.load(input_data)
    for event in json_data:
        if event['type'] == 'ORDER':
            if event['customer_id'] != ' ':             #considers record only if customer id is present
                event_time = datetime.strptime(str(event['event_time']), '%Y-%m-%dT%H:%M:%S.%fZ')
                amount = float(event['total_amount'].split(' ')[0])       # separates amount from USD, and takes only amount
                week_number = int(event_time.strftime('%U'))        #returns week number of event time
                order_list.append([str(event['customer_id']), event['verb'], event['key'], event_time, amount, week_number])
        if event['type'] == 'SITE_VISIT':
            if event['customer_id'] != ' ':             #considers record only if customer id is present
                event_time = datetime.strptime(str(event['event_time']), '%Y-%m-%dT%H:%M:%S.%fZ')
                week_number = int(event_time.strftime('%U'))       #returns week number of event time
                visit = 1              #number for each visit to site 
                site_visit_list.append([str(event['customer_id']), event['key'], event_time, week_number, visit])
        else:
            pass
    order_df = pd.DataFrame(order_list, columns=['CustomerId', 'Verb', 'OrderId', 'EventTime', 'Amount', 'WeekNumber'])
    site_visit_df = pd.DataFrame(site_visit_list, columns=['CustomerId', 'PageId', 'EventTime', 'WeekNumber', 'Visits'])
    
    return order_df, site_visit_df

def pre_process(order_df, visit_df):
    """
    This function does preprocessing on order and visit data. If there are any 
    updates on order id, considers most recent transaction and ignoring previous
    transactions. If there areany redundant entries in site visit data, function
    keeps one entry and deletes others.
    
    Input:
    * order_df(dataframe): dataframe that has data about customer transactions such as
                           customer_id, nature of order(NEW/UPDATE),order id,time of transaction,
                           amount they spent, week number in which given time of transaction falls.
    * visit_df(dataframe): dataframe has data about customer visits to website such as 
                            custommer id, page id, time visited, week number in
                            which given time visited falls, count for each visit
                                
    Output:
    * order_df, visit_df dataframes after preprocessing.
    
    """
    
    # considers recent updated entry for a given order id if there are any.
    order_df = order_df.sort_values(by=['CustomerId', 'OrderId', 'EventTime'], ascending=True)
    #print order_df
    length = len(order_df)
    i = 0
    while i <= length:
        if i == length - 1:
            break
        elif order_df.loc[i]['OrderId'] == order_df.loc[i+1]['OrderId']:
            if order_df.loc[i]['Verb'] == 'NEW' and order_df.loc[i+1]['Verb'] == 'UPDATE':
                order_df.drop(order_df.index[i], inplace=True)
                order_df = order_df.reset_index(drop=True)
                i = i - 1
                length = length - 1
                continue
            elif order_df.loc[i]['Verb'] == 'UPDATE' and order_df.loc[i+1]['Verb'] == 'UPDATE':
                order_df.drop(order_df.index[i], inplace=True)
                order_df = order_df.reset_index(drop=True)
                i = i - 1
                length = length - 1
                continue
        else:
            i = i + 1
            continue
    
    #removes dupliactes (from site visit data) except first occuurence based on columns customer_id, page id, event time
    visit_df.drop_duplicates(subset=['CustomerId', 'PageId', 'EventTime'], keep='first', inplace=True)

    return order_df, visit_df
            
def top_two_simple_ltv_customers(order_final, site_visit_final):
    """
    This function calculates life time value of each customer and 
    return top two customer id
    
    Input:
    * order_final(dataframe): dataframe that has data about customer transactions such as
                           customer_id, time of transaction, amount they spent, week number in
                           which given time of transaction falls.
    * site_visit_final(dataframe): dataframe has data about customer visits to website such as 
                                custommer id, time visited, week number in
                                which given time visited falls, count for each visit
                                
    Output:
    * Top two Customers(dataframe): list of customer ids, respective life time value amount. 
    """
    
    #calculates number of weeks in entire data
    num_of_weeks = max(site_visit_final['WeekNumber']) - min(site_visit_final['WeekNumber']) + 1 
    
    # calculates total expenditure of each customer in a given timeframe.
    # The resultant dataframe has two columns: CustomerId, Amount.
    order_ser = order_final.groupby(['CustomerId'])['Amount'].sum()   
    order_final = order_ser.reset_index()
    
    # calculates number of customer visits of each customer in a given timeframe.
    # The resultant dataframe has two columns: CustomerId, Visits.
    site_visit_ser = site_visit_final.groupby('CustomerId')['Visits'].count()   
    site_visit_final = site_visit_ser.reset_index()
    
    visit_order_df = pd.merge(site_visit_final, order_final, on ='CustomerId', how='left')
    visit_order_df.fillna(0, inplace=True)      #useful when customer has visited site but no orders in a given timeframe
    visit_order_df['NumberOfWeeks'] = num_of_weeks
    visit_order_df['ExpenditurePerVisit'] = visit_order_df['Amount'] / visit_order_df['Visits']
    visit_order_df['SiteVisitPerWeek'] = visit_order_df['Visits'] / num_of_weeks
    visit_order_df['CustomerLTV'] = visit_order_df['ExpenditurePerVisit'] * visit_order_df['SiteVisitPerWeek']
    visit_order_df['CustomerLTV'] = visit_order_df['CustomerLTV'] * 52 * AVG_CUST_LIFESPAN
    visit_order_df.sort_values(by='CustomerLTV', inplace=True, ascending=False)
    visit_order_df.rename(columns={'Amount': 'TotalExpenditure'}, inplace=True)
    visit_order_df.to_csv('D:\Shutterfly-code-challenge\output\customer_ltv.csv', index=False)  
    
    return visit_order_df.head(N)[['CustomerId', 'CustomerLTV']]
    
    
if __name__ == "__main__":
    main()
    
