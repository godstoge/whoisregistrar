import whois  # folder
import sys
import argparse
import time
import pandas as pd

parser = argparse.ArgumentParser(description="Awesomeness", epilog="Epi awesomeness", formatter_class=argparse.RawDescriptionHelpFormatter)
args_group = parser.add_mutually_exclusive_group()
args_group.add_argument('--file', action='store', help="File to read domains from.") 
args_group.add_argument('--domain', action='store', help="Specific domain to check.")   # Display pretty dict to console
cliargs = parser.parse_args()

outputdata = {}


def perform_whois(domain_to_check):
    # Check the domain and add to outputdata.
    wh = whois.whois(domain_to_check)
    outputdata[domain_to_check] = {
        "organisation": wh.org_name,
        "orgnr":        wh.org_orgnr,
        "postal_code":  wh.postal_code,
        "postal_area":  wh.postal_area,
        "contact":      wh.contact_name,
        "contact_phone":wh.contact_phone,
        "contact_email":wh.contact_email  
    }
    
    #DEBUG 
    #print(wh.text)  # Dump everythingreturned from whoisserver.
    return

# Function to colorize postal codes
def color_postal_code(postal_code):
    if postal_code is None: 
        return
    elif "NO-7" in postal_code:
        # ANSI escape code for green color
        return f"\033[92m{postal_code}\033[0m"  # Green color
    return f"{postal_code}"



if cliargs.file:     
   # Open file
    counter=0
    try:
        with open(cliargs.file, encoding='utf-8') as fh:
            fstring = fh.readlines() #.readlines creates list
            for line in fstring:
                counter+=1
                perform_whois(line.strip()) # Check actual whois on the domain
                print(".", end = '', flush=True)
                if counter >= 60:
                    print("\nHit rate limit boundary - sleeping for 60 seconds.")
                    time.sleep(61)
                    print("Continuing")
                    counter=0
         
    except: 
        print("[!] Unable to open file %s" % cliargs.file)
        exit()
      
   
elif cliargs.domain:   
   # Remove desired services from all_se
   perform_whois(cliargs.domain)
   #print(outputdata)


#Convert the dictionary into a Pandas DataFrame
df = pd.DataFrame.from_dict(outputdata, orient="index")

# Reset the index to make keys into a column
df.reset_index(inplace=True)


pd.set_option('display.colheader_justify', 'center')    # Set display options to left-align text in the output
pd.set_option('display.max_rows', None)  # This will show all rows
pd.set_option('display.max_rows', None)            # Show all rows
pd.set_option('display.max_columns', None)         # Show all columns
pd.set_option('display.max_colwidth', None)        # Avoid truncating column content
pd.set_option('display.width', None)               # Auto adjust to terminal width

# Sort the DataFrame by 'Postal Code' in ascending order
df_sorted   = df.sort_values(by="postal_code", ascending=True)

# Filter out all postal_codes that start with NO-7
try:
    df_sorted_clean = df_sorted.dropna(subset=['postal_code']) # Drop all lines with NaN/None in postal_code
    df_filtered = df_sorted_clean[df_sorted_clean['postal_code'].str.startswith('NO-7')]  
except:
    print("Failed at df_filtered")
    df_filtered = "Failure at sorting operation. No data to show. :("


# Print the sorted DataFrame
print("\n-------------------------")
print(df_sorted)

print("\n-------------------------")
print(df_filtered)


'''WHOIS
Limit: 3000 per day per registrar.
Action: Automatic lockout till midnight if daily limit is exceeded.  
Limit: 60 per minute per registrar (insofar as is consistent with limit 2.1).
Action: Automatic lockout for a period of 30 seconds if minute limit is exceeded.
https://teknisk.norid.no/en/administrere-domenenavn/aup/



{
  "domain_name": "atea.no",
  "creation_date": "2021-08-03 00:00:00",
  "updated_date": [
    "2024-10-23 00:00:00",
    "2023-12-14 00:00:00"
  ],
  "postal_code": "NO-0579",
  "postal_area": "OSLO",
  "postal_adr": "Karvesvingen 5",
  "org_name": "ATEA ASA",
  "org_orgnr": "920237126",
  "contact_name": "Sundberg Mats",
  "contact_phone": "+47.22095000",
  "contact_email": "hostmaster@atea.dk"
}

'''