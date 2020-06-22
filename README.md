# Xero-Pipeline-Assignment
A pipeline engineered to extract raw data from XERO APIs and loaded onto a database in bigQuery

The python script can be used to authenticate a XERO account through OAuth2.0 and use the XERO APIs for data such as Invoices and Contacts.

The script requires : 

1) A XERO Account
2) A Google Cloud Account
3) Python 3.5+
4) Anaconda


STEPS : 

1) Create an APP in XERO, secure the client_id and client_secret.
2) These credentials must be entered into the python file before execution
3) The prompt : 'Enter the response URL : ' will require you to enter the entire redirected URL once XERO login has been completed
4) The XERO OAuth2.0 mechanism will return an "access code" which has an expiry of 12 minutes and a "refresh token"
5) To deal with the expiry of the "access code" I have created the REFRESH method which takes the refresh token, gets a new refresh token from XERO and stores it in a text file.

6) Using the XERO API, the python script will extract INVOICE and CONTACT information from the selected company in your XERO account.
7) The data retrieved will be manipulated to logically create a CSV file. 
8) These CSV files will then be loaded onto bigQuery using the GBQ library 
9) To use gbq, enter the following command in your Anaconda Promit: conda install pandas-gbq -c conda-forge
10) Create a project in GBQ, note the "project_id" and replace it in the script where required.
11) Create a schema in BGQ (using the WEB UI)
12) The python code will proceed to create tables from the given CSV files onto bigQuery
