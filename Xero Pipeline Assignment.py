#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import requests
import webbrowser
import base64
import os


# In[2]:


#Set parameters for XERO API use
client_id = '[Enter_Client_ID]'
client_secret = '[Enter_Client_Secret]'
redirect_url = 'https://developer.xero.com/'
scope = 'offline_access accounting.transactions accounting.contacts'
b64_id_secret = base64.b64encode(bytes(client_id + ':' + client_secret, 'utf-8')).decode('utf-8')


# In[ ]:


def XeroFirstAuth():
    # 1. Send a user to authorize your app
    auth_url = ('''https://login.xero.com/identity/connect/authorize?''' +
                '''response_type=code''' +
                '''&client_id=''' + client_id +
                '''&redirect_uri=''' + redirect_url +
                '''&scope=''' + scope +
                '''&state=123''')
    webbrowser.open_new(auth_url)
    
    # 2. Users are redirected back to you with a code
    auth_res_url = input('Enter the response URL : ')
    start_number = auth_res_url.find('code=') + len('code=')
    end_number = auth_res_url.find('&scope')
    auth_code = auth_res_url[start_number:end_number]
    print(auth_code)
    print('\n')
    
    # 3. Exchange the code
    exchange_code_url = 'https://identity.xero.com/connect/token'
    try:
        response = requests.post(exchange_code_url, 
                                headers = {
                                    'Authorization': 'Basic ' + b64_id_secret
                                },
                                data = {
                                    'grant_type': 'authorization_code',
                                    'code': auth_code,
                                    'redirect_uri': redirect_url
                                })

    except Exception as e:
        print(e)
        raise
        
    json_response = response.json()
    # todo validate state value
    if response is None or json_response['access_token'] is None:
        return "Access denied: response=%s" % json_response
    
    
    print(json_response)
    print('\n')
    
    # 4. Receive your tokens
    return [json_response['access_token'], json_response['refresh_token']]


# In[7]:


def XeroRefreshToken(refresh_token):
    token_refresh_url = 'https://identity.xero.com/connect/token'
    response = requests.post(token_refresh_url,
                            headers = {
                                'Authorization' : 'Basic ' + b64_id_secret,
                                'Content-Type': 'application/x-www-form-urlencoded'
                            },
                            data = {
                                'grant_type' : 'refresh_token',
                                'refresh_token' : refresh_token
                            })
    
    json_response = response.json()
    print(json_response)
    new_refresh_token = json_response['refresh_token']
    
    #Save refresh token in a txt file
    rt_file = open("C:\\Users\\sunil\\Desktop\\test\\refresh_token.txt", 'w')
    rt_file.write(new_refresh_token)
    rt_file.close()
    
    return [json_response['access_token'], json_response['refresh_token']]


# In[8]:


#First time authentication for XERO API
old_tokens = XeroFirstAuth()
XeroRefreshToken(old_tokens[1])


# In[ ]:


# 5. Check the full set of tenants you've been authorized to access
def XeroTenants(access_token):
    connections_url = 'https://api.xero.com/connections'
    response = requests.get(connections_url,
                           headers = {
                               'Authorization': 'Bearer ' + access_token,
                               'Content-Type': 'application/json'
                           })
    json_response = response.json()
    print(json_response)
    
    for tenants in json_response:
        json_dict = tenants
    return json_dict['tenantId']


# In[ ]:


# XERO API call for invoices 

old_refresh_token = open("C:\\Users\\sunil\\Desktop\\test\\refresh_token.txt", 'r').read()
new_tokens = XeroRefreshToken(old_refresh_token)
xero_tenant_id = XeroTenants(new_tokens[0])

get_url = 'https://api.xero.com/api.xro/2.0/Invoices'
response = requests.get(get_url,
                       headers = {
                           'Authorization': 'Bearer ' + new_tokens[0],
                           'Xero-tenant-id': xero_tenant_id,
                           'Accept': 'application/json'
                       })
json_response = response.json()

#Save API response
xero_output = open('C:\\Users\\sunil\\Desktop\\test\\xero_output.txt', 'w')
xero_output.write(response.text)
xero_output.close()

#Convert invoice data into csv

invoices = open(r'C:\\Users\\sunil\\Desktop\\test\\xero_invoices.txt', 'r').read()
json_invoice = json.loads(invoices)
analysis = open(r'C:\\Users\\sunil\\Desktop\\test\\invoices.csv', 'w')
#write headers for invoices.csv
analysis.write('Type' + ','
               + 'InvoiceID' + ','
               + 'InvoiceNumber' + ',' 
               + 'Reference' + ','
               + 'AmountDue' + ',' 
               + 'AmountPaid' + ',' 
               + 'AmountCredited' + ',' 
               + 'IsDiscounted' + ',' 
               + 'HasAttachments' + ',' 
               + 'HasErrors' + ',' 
               + 'ContactID' + ',' 
               + 'ContactName' + ',' 
               + 'InvoiceDate' + ',' 
               + 'InvoiceDueDate' + ',' 
               + 'InvoiceStatus' + ',' 
               + 'SubTotal' + ',' 
               + 'TotalTax' + ',' 
               + 'Total' + ',' 
               +  'CurrencyCode' )
analysis.write('\n')
for invoices in json_invoice['Invoices']:
    analysis.write(invoices['Type'] + ',' 
                   + invoices['InvoiceID'] + ','
                   + invoices['InvoiceNumber'] + ','
                   + invoices['Reference'] + ','
                   + str(invoices['AmountDue']) + ','
                   + str(invoices['AmountPaid']) + ','
                   + str(invoices['AmountCredited']) + ','
                   + str(invoices['IsDiscounted']) + ','
                   + str(invoices['HasAttachments']) + ','
                   + str(invoices['HasErrors']) + ','
                   + invoices['Contact']['ContactID'] + ','
                   + invoices['Contact']['Name'] + ','
                   + invoices['DateString']+ ','
                   + invoices['DueDateString']+ ','
                   + invoices['Status']+ ','
                   + str(invoices['SubTotal'])+ ','
                   + str(invoices['TotalTax'])+ ','
                   + str(invoices['Total'])+ ','
                  + invoices['CurrencyCode'])
    analysis.write('\n')
analysis.close()

# Xero API call for Contacts

get_url = 'https://api.xero.com/api.xro/2.0/Contacts'
response = requests.get(get_url,
                       headers = {
                           'Authorization': 'Bearer ' + new_tokens[0],
                           'Xero-tenant-id': xero_tenant_id,
                           'Accept': 'application/json'
                       })
json_response = response.json()

xero_output = open("C:\\Users\\sunil\\Desktop\\test\\xero_contacts.txt", 'w')
xero_output.write(response.text)
xero_output.close()

#Convert contacts data into csv

contacts = open(r'C:\\Users\\sunil\\Desktop\\test\\xero_contacts.txt', 'r').read()
json_contacts = json.loads(contacts)
analysis = open(r'C:\\Users\\sunil\\Desktop\\test\\contacts.csv', 'w')

#write headers for contacts.csv
analysis.write('ContactsID' + ','
               + 'ContactStatus' + ','
               + 'ContactName')
analysis.write('\n')

for contacts in json_contacts['Contacts']:            
    analysis.write(contacts['ContactID'] + ',' 
                   + contacts['ContactStatus'] + ','
                   + contacts['Name'])
    analysis.write('\n')
analysis.close()

#Write addresses cv
analysis = open(r'C:\\Users\\sunil\\Desktop\\test\\contacts_addresses.csv', 'w')
analysis.write('ContactID' + ','
               +'AddressType' + ',' 
               + 'City' + ',' 
               + 'Region' + ',' 
               + 'PostalCode' + ',' 
               + 'Country')
analysis.write('\n')


#Create contacts_addresses.csv
for contacts in json_contacts['Contacts']:
    for contact in contacts['Addresses']:
        for c in contact:
            analysis.write(contacts['ContactID'])
            if 'AddressType' in c:
                analysis.write(','+ contact['AddressType'])
            else:
                analysis.write(',' + 'NA')
                
            if 'City' in c:
                analysis.write(','+ contact['City'])
            else:
                analysis.write(','+ 'NA')
                
            if 'Region' in c:
                analysis.write(','+ contact['Region'])
            else:
                analysis.write(','+ 'NA')
                
            if 'PostalCode' in c:
                analysis.write(','+ contact['PostalCode'])
            else:
                analysis.write(','+ 'NA')
                
            if 'Country' in c:
                analysis.write(','+ contact['Country'])
            else:
                analysis.write(','+ 'NA')
                
            analysis.write('\n')

analysis.close()

#Write contacts_phones cv
analysis = open(r'C:\\Users\\sunil\\Desktop\\test\\contacts_phones.csv', 'w')
analysis.write('ContactID' + ','
               +'PhoneType' + ',' 
               + 'PhoneNumber' + ',' 
               + 'PhoneAreaCode' + ',' 
               + 'PhoneCountryCode')
analysis.write('\n')

#Create contacts_addresses.csv
for contacts in json_contacts['Contacts']:
    for contact in contacts['Phones']:
        for c in contact:
            analysis.write(contacts['ContactID'])
            if 'PhoneType' in c:
                analysis.write(','+ contact['PhoneType'])
            else:
                analysis.write(',' + 'NA')
                
            if 'PhoneNumber' in c:
                analysis.write(','+ contact['PhoneNumber'])
            else:
                analysis.write(','+ 'NA')
                
            if 'PhoneAreaCode' in c:
                analysis.write(','+ contact['PhoneCountryCode'])
            else:
                analysis.write(','+ 'NA')
                
            if 'PostalCode' in c:
                analysis.write(','+ contact['PostalCode'])
            else:
                analysis.write(','+ 'NA')
            analysis.write('\n')

analysis.close()


# In[ ]:


#Load data into bigQuery

import pandas as pd
from pandas.io import gbq
import pandas as pd
import numpy as np

#Read all CSV files created from XERO API raw data

invoices_data = pd.read_csv('C:\\Users\\sunil\\Desktop\\test\\invoices.csv')

contacts_data= pd.read_csv('C:\\Users\\sunil\\Desktop\\test\\contacts.csv')

contacts_addresses_data= pd.read_csv('C:\\Users\\sunil\\Desktop\\test\\contacts_addresses.csv')

contacts_phones_data= pd.read_csv('C:\\Users\\sunil\\Desktop\\test\\contacts_addresses.csv')


# In[10]:


#Call bigQuery API for loading invoices data into schema
invoices_data.to_gbq(destination_table='Xero_Demo_Company.Invoice_table',project_id= 'xero-pipeline-assignment', if_exists='append')


# In[ ]:


#Call bigQuery API for loading contacts data into schema
contacts_data.to_gbq(destination_table='Xero_Demo_Company.Contact_table',project_id= 'xero-pipeline-assignment', if_exists='append')


# In[ ]:


#Call bigQuery API for loading contacts address data into schema
contacts_addresses_data.to_gbq(destination_table='Xero_Demo_Company.Contact_Addresses_table',project_id= 'xero-pipeline-assignment', if_exists='replace')


# In[ ]:


#Call bigQuery API for loading contacts phone data into schema
contacts_phones_data.to_gbq(destination_table='Xero_Demo_Company.Contact_Phones_table',project_id= 'xero-pipeline-assignment', if_exists='replace')

