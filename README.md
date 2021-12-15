# hdb-payment-plan
Description
========
Are you a first-time homeowner? The HDB payments calculator allows you to compare costs and fees across multiple HDB flats.
Make a quick and informed decision on flats that meet your budget!

Features
--------
- Compares costs and fees across multiple HDB flats
- Accounts for buyers' income and CPF balances
- Adjusts for HDB grants buyers are eligible for
- Determines cash requirement for deposit and fees and mortgage payments

Assumptions
--------
1) Buyers are first timers
2) Buyers are aged 35 and below
3) Buyers are engaged or married
     a) Additional restrictions apply to Singapore citizens who purchase HDB flats
4) HDB price is paid with CPF OA (includes deposit) whereas fees and charges are paid with cash
     a) Reduces loan amount and interest on interest owed
     b) Reduces conveyancing fees for resale flats
5) No cash over valuation for resale flats
     a) Cash over valuation must be paid in cash
     b) Loan amount will be the lower of sale price and HDB valuation of flat


Pre-requisites
========
- Filled out housing hdb-information Excel file
- numpy   -- pip install numpy
- pandas  -- pip install pandas
- tkinter -- pip install tkinter


Installation
========
1) Change directory to file save location.
2) Run: python hdb-payments-calculator.py


Contribute
========
- Issue Tracker: github.com/
- Source Code: github.com/

Contact
-------
If you are having issues, please let me know: m.qadhin@gmail.com


References
========
- https://www.hdb.gov.sg/residential/buying-a-flat/new/finance/costs-and-fees
- https://www.hdb.gov.sg/residential/buying-a-flat/resale/financing/costs-and-fees
- https://homes.hdb.gov.sg/home/calculator/payment-plan
- https://services2.hdb.gov.sg/webapp/BB14LFEESENQ/BB14PHomePage.jsp
