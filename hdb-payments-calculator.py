#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import math

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from IPython.display import clear_output


### Get and save file
def get_file():
    
    '''
    Requests user to select a housing file to open
    '''
    
    # Create a root window
    root = Tk()
    
    filepath = filedialog.askopenfilename(filetypes=[('Excel files', '.xlsx')], title='Open housing file')

    # Close root window
    root.destroy()
    root.mainloop()
    
    return pd.read_excel(filepath, sheet_name='hdb-flats', dtype={'Proximity':'float','Price':'float'})


def save_file(df):
    
    '''
    Requests user to select a save location
    
    Parameters:
    df -- (DataFrame) table of HDB-related information
    '''
    
    
    df = df[['Town','Project_Name','Sale_Mode','Block','Unit_No','Flat_Type','Proximity','Lender','Price','CPF_w_Grants',
             'Deposit','Total_Fees','Loan','Mortgage','Deposit_in_Cash','Mortgage_in_Cash']]
    
    # Create a root window
    root = Tk()
    
    save_dir = filedialog.askdirectory(title='Select save location')

    # Close root window
    root.destroy()
    root.mainloop()
    
    df.to_excel(save_dir+'/hdb_payments-and-financing.xlsx', index=False, sheet_name='financing')
    
    print("\nYour file has been successfully saved!")
    

def print_attributes(incomes, cpfs, cpf_monthly):
    
    '''
    Prints information used to calculate HDB financing
    
    Parameters:
    incomes     -- (list) buyers' incomes
    cpfs        -- (list) buyers' CPF OA balances
    cpf_monthly -- (float) buyers' combined CPF monthly contribution
    '''
    
    clear_output()
    
    print("\n")
    print(10*"-" + "FINANCIAL INFORMATION" + 10*"-")
    print(f"Combined income:\t\t${sum(incomes):,}")
    print(f"Combined CPF OA balance:\t${sum(cpfs):,}")
    print(f"Combined CPF contribution:\t${cpf_monthly:,}")
 


### Get buyers' income and CPF balance
def get_buyer_details():
    
    '''
    Requests user to enter income and CPF OA balance
    
    Returns:
    incomes -- (list) buyers' incomes
    cpfs    -- (list) buyers' CPF OA balances
    '''
    
    incomes = []
    cpfs = []
    
    for i in range(2):
        while True:
            try:
                incomes.append(float(input(f"\nBuyer {i+1} monthly income: ")))
                break

            except ValueError:
                print("You did not enter a number! Please try again.")
        
        while True:
            try:
                cpfs.append(float(input(f"Buyer {i+1} CPF OA balance: ")))
                break
                
            except ValueError:
                print("You did not enter a number! Please try again.")
        
        clear_output()
        
    return incomes, cpfs



### Get financing details
def get_lenders():
    
    '''
    Requests user to enter a lender
    '''
    
    choice = ''
    lenders = ['hdb','bank','both']
    
    while choice not in lenders:
        
        choice = input("\nEnter lender (HDB/Bank/Both): ").lower()
        
    
    # Return lenders
    if choice == 'both':
        return lenders[:2]
    else:
        return [choice]
    

def get_loan_rate(lender):
    
    '''
    Get housing loan rate; requests user to enter bank loan rate (if required)
    
    Parameters:
    lender -- (str) either 'hdb' or 'bank'
    '''
    
    # If lender is HDB return 2.6%
    if lender == 'hdb':
        return 2.6/1200
    
    # If lender is bank, get bank housing loan rate
    while True:
        try:
            r = float(input("\nEnter bank loan rate (APY): "))
            return abs(r/1200)

        except ValueError:
            print("You did not enter a number! Please try again.\n")



### Calculate CPF balance, contribution
def calculate_monthly_cpf(incomes):
    
    '''
    Calculate monthly cpf contribution
    
    Parameters:
    incomes -- (list) buyers' incomes
    '''
    
    cpf_monthly = 0
    
    # CPF contribution applicable to first $6000 of individual income
    for income in incomes:
        cpf_monthly += min(income, 6000)
    
    # Contribution rates vary by age; 23% for people aged 35 and below
    return .23*cpf_monthly


def calculate_cpf_total(sale_mode, flat_type, proximity, income, cpf):
    
    '''
    Calculate total CPF OA balance after grants
    
    Parameters:
    sale_mode -- (str) either 'bto' or 'resale'
    flat_type -- (str) type of flat being purchased
    proximity -- (float) distance of flat from parents' house
    income    -- (float) buyers' combined income
    cpf       -- (float) buyers' combined CPF OA balance
    '''
    
    # First-time bto and resale buyers are eligible for Enhanced Housing Grant
    cpf += calculate_ehg(income)
    
    # Only first-time resale buyers are eligible for Family and Proximity Grant
    if sale_mode == 'resale':
        cpf += calculate_family_grant(flat_type, income) + calculate_proximity_grant(proximity)
    
    return cpf



### Calculate eligible housing grants
def calculate_ehg(income):
    
    '''
    Calculate Enhanced Housing Grant amount eligble for
    
    Parameters:
    income -- (float) buyers' combined income
    '''
    
    # Grant amount decreases by 5000 for every 500 increase in household income
    redux = math.ceil((income-1500) / 500)
    
    return max(80000 - 5000*redux, 0)


def calculate_family_grant(flat_type, income):
    
    '''
    Calculate Family Grant amount eligble for
    
    Parameters:
    flat_type -- (str) type of flat being purchased  
    income    -- (float) buyers' combined income  
    '''

    # Income ceiling set at 14000
    if income > 14000:
        return 0
    
    if flat_type in ['5-room','executive']:
        return 40000
    elif flat_type in ['3-room','4-room']:
        return 50000
    else:
        return 0


def calculate_proximity_grant(proximity):
    
    '''
    Calculate Proximity Grant amount eligible for
    
    Parameters:
    proximity -- (float) distance of flat from parents' house
    '''
    
    if (proximity > 0) & (proximity < 4):
        return 20000
    elif proximity == 0:
        # Those buying homes with parents are eligible for $30,000
        return 30000
    else:
        return 0



### Calculate fees and charges
def calculate_loan(price, cpf, ltv):
    
    '''
    Calculate housing loan required
    
    Parameters:
    price -- (float) price/valuation of flat
    cpf   -- (float) combined CPF OA balance including grants
    ltv   -- (float) loan-to-value ratio based on lender selected
    '''
    
    # Determine multiplier of price; bank loans require 5% cash deposit
    if ltv == .75:
        m = .2
    elif ltv == .9:
        m = .1
    
    # Calculate loan amount, adjusting for cpf balance
    if cpf > m*price:
        return max((m+ltv)*price - cpf, 0)
    else:
        return ltv * price


def calculate_bsd(price):
    
    '''
    Calculate buyer's stamp duty
    
    Parameters:
    price -- (float) price/valuation of flat
    '''
    
    bsd = 0
    rates = [.01,.02,.03,.04]
    tiers = [180000,180000,640000,float('inf')]
    
    for i in range(len(tiers)):
        if price > 0:
            bsd += min(tiers[i],price) * rates[i]
            price -= tiers[i]
        else:
            break
    
    return bsd


def calculate_conveyancing_fee(sale_mode, price, loan, gst=.07):
    
    '''
    Calculate conveyancing (legal) fees
    
    Parameters:
    sale_mode -- (str) either 'bto' or 'resale'
    price     -- (float) price/valuation of flat
    loan      -- (float) loan amount for flat
    gst       -- (float) goods and services tax payable (default 0.07)
    '''
    
    conveyancing = 0
    rates = {'bto':[.9,.72,.6], 'resale':[1.35,1.08,0.9]}
    rates_mortgage = [2.03,1.61,1.35]
    tiers = [30000, 30000, float('inf')]
    
    for i in range(len(tiers)):
        if price > 0:
            
            # Calculate fees payable for acting in purchase
            conveyancing += min(tiers[i],price)/1000 * rates[sale_mode][i]
            price -= tiers[i]
            
            # Calculate fees payable for acting in mortgage (if resale)
            if sale_mode == 'resale':
                conveyancing += min(tiers[i],loan)/1000 * rates_mortgage[i]
                loan -= tiers[i]
            
        else:
            break
    
    return math.ceil(conveyancing) * (1+gst)


def calculate_survey_fee(flat_type, gst=.07):
    
    '''
    Calculate survey fee
    
    Parameters:
    flat_type -- (str) type of flat being purchased
    gst       -- (float) goods and services tax payable (default 0.07)
    '''
    
    survey_fee = {'2-room':150,'3-room':212.5,'4-room':275,'5-room':325,'executive':375}
    
    try:
        return survey_fee[flat_type] * (1+gst)
    except KeyError:
        return 0


def calculate_other_fees(sale_mode, loan, survey_fee, mortgage_escrow=38.3,lease_escrow=38.3,caveat_fee=64.45,title_fee=32):
    
    '''
    Calculate other fees payable to HDB
    
    Parameters:
    sale_mode       -- (str) either 'bto' or 'resale'
    loan            -- (float) loan amount for flat
    survey_fee      -- (float) payable based on flat type being purchased
    mortgage_escrow -- (float) payable if HDB acts for you in the mortgage (default 38.3)
    lease_escrow    -- (float) payable if HDB acts for you in the flat purchase (default 38.3)
    caveat_fee      -- (float) payable for resale flats (default 64.45)
    title_fee       -- (float) payable for resale flats (default 32)
    '''
        
    # Applicable if hdb acts for buyer in mortgage
    mortgage_deed = min(0.004*loan, 500)
    
    if sale_mode == 'bto':
        return mortgage_deed + mortgage_escrow + lease_escrow + survey_fee
    elif sale_mode == 'resale':    
        return mortgage_deed + mortgage_escrow + lease_escrow + 2*caveat_fee + title_fee
    else:
        return 0



### Calculate cash requirements
def calculate_deposit_shortfall(cpf, deposit, fees, ltv):
    
    '''
    Calculate cash required for desposit, fees and charges
    
    Parameters:
    cpf     -- (float) combined CPF OA balance including grants 
    deposit -- (float) deposit required based on lender selected
    fees    -- (float) fees and charges payable to HDB
    ltv     -- (float) loan-to-value ratio based on lender selected
    '''
    
    # Determine multiplier of price; bank loans require 5% cash deposit
    if ltv == .75:
        m = .8
    elif ltv == .9:
        m = 1
        
    if cpf > m*deposit:
        return (1-m)*deposit + fees
    else:
        return deposit + fees - cpf


def calculate_mortgage_shortfall(mortgage, cpf_monthly):
    
    '''
    Calculate cash required for monthly mortgage
    
    Parameters:
    mortgage    -- (float) monthly mortgage based on loan amount
    cpf_monthly -- (float) buyers' combined CPF monthly contribution
    '''
    
    if mortgage > cpf_monthly:
        return mortgage - cpf_monthly
    else:
        return 0



### Calculate financing for flat purchase
def calculate_financing(tbl, lender, cpf_monthly):
    
    '''
    Calculate buyers' financial obligations
    
    Parameters:
    tbl         -- (DataFrame) table of HDB-related information
    lender      -- (str) either 'hdb' or 'bank'
    cpf_monthly -- (float) buyers' combined CPF monthly contribution
    
    Returns:
    df          -- (DataFrame) transformed table of HDB-related information
    '''
    
    
    df = tbl.copy()
    
    # Get loan-to-value ratio based on lender
    ltvs = {'hdb':.9, 'bank':.75}
    ltv = ltvs[lender]
    
    # Get housing loan interest rate
    r = get_loan_rate(lender)
    
    # Loan tenure (assumed to be 25 years)
    period = 25*12
    
    
    # Calculate deposit and mortgage
    df['Deposit'] = (1-ltv) * df['Price']
    df['Lender'] = lender
    df['Loan'] = df.apply(lambda x: calculate_loan(x['Price'], x['CPF_w_Grants'], ltv), axis=1)
    df['Mortgage'] = round(df['Loan'] * r * (1+r)**period/((1+r)**period - 1), 2)

    # Calculate fees and charges
    df['Stamp_Duty'] = df['Price'].apply(calculate_bsd)
    df['Conveyancing_Fee'] = df.apply(lambda x: calculate_conveyancing_fee(x['Sale_Mode'], x['Price'], x['Loan'], gst)
                                      , axis=1)
    df['Survey_Fee'] = df.apply(lambda x: calculate_survey_fee(x['Flat_Type'], gst), axis=1)
    df['Other_Fees'] = df.apply(lambda x: calculate_other_fees(x['Sale_Mode'], x['Loan'], x['Survey_Fee']), axis=1)
    df['Total_Fees'] = df['Stamp_Duty'] + df['Conveyancing_Fee'] + df['Other_Fees']
    
    # Calculate cash required for deposit and fees
    df['Deposit_in_Cash'] = df.apply(lambda x: calculate_deposit_shortfall(x['CPF_w_Grants'] ,x['Deposit'], x['Total_Fees'],
                                                                           ltv), axis=1)
    
    # Calculate cash required for mortgage payments
    df['Mortgage_in_Cash'] = df.apply(lambda x: calculate_mortgage_shortfall(x['Mortgage'], cpf_monthly), axis=1)
    
    return df



## Fixed variables
# Tax rate
gst = .07 # applicable to conveyancing, survey fees

# General fixed fees
lease_escrow = 38.3
mortgage_escrow = 38.3

# Resale fixed fees
rfv = 120
stay_extension = 20
caveat_fee = 64.45 # double if loan is from HDB
title_fee = 32



## Run program
# Get housing file
print("---WELCOME TO THE HDB PAYMENTS CALCULATOR---")
hdb = get_file()

# Get income and CPF information
incomes, cpfs = get_buyer_details()
cpf_monthly = calculate_monthly_cpf(incomes)
hdb['CPF_w_Grants'] = hdb.apply(lambda x: calculate_cpf_total(x['Sale_Mode'], x['Flat_Type'], x['Proximity'], sum(incomes),
                                                              sum(cpfs)), axis=1)

# Calculate financing
dfs = []
lenders = get_lenders()

for lender in lenders:
    dfs.append(calculate_financing(hdb, lender, cpf_monthly))

# Concatenate dataframes
hdb = pd.concat(dfs)

# Save HDB file
save_file(hdb)

# Print information used to compute HDB financing
print_attributes(incomes, cpfs, cpf_monthly)
