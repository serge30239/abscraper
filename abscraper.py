import requests
import string
import time
import pandas as pd
import csv
import json
import os

letters = list(string.ascii_lowercase)
scrape_output = 'scrape_output'

delay = 3
n_try = 3

class bcolors:
    NOTE = '\033[95m'
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'

if os.path.isdir(scrape_output):
    print(f"Using existing folder {scrape_output} for output")
else:
    os.makedirs(scrape_output)
    print(f"Created new folder {scrape_output} for output")

def get_agents(s, delay):
    time.sleep(delay)
    url = f'https://licensing.abcouncil.ab.ca/lookup/license/search/?city=&firstName=&lastName={s}&lookupType=agent&showHistory=false'
    r = requests.get(url)
    return r

def get_all_agents(s, delay, n_try):
    results = []
    errors = []
    if n_try == 0:
        print(f"{bcolors.WARNING}Warning: For '{s}' number of attempts exceeded")
    else:
        i = n_try
        status_code = 0
        while status_code != 200 and i > 0:
            try:
                result = get_agents(s, delay)
                n = len(eval(result.content))
                status_code = result.status_code
            except:
                status_code = 0
                i -= 1

        if status_code == 200:
            if n > 0:
                if n < 1000:
                    print(f"{bcolors.OKGREEN}Done '{s}' - {n} entries")
                    results.append(result)
                else:
                    print(f"{bcolors.NOTE}Note: Too many entries in '{s}' - will split")
                    for letter in letters:
                        r = get_all_agents(s + letter, delay, n_try)
                        results.extend(r[0])
                        errors.extend(r[1])
            else:
                r = get_all_agents(s, delay, n_try - 1)
                results.extend(r[0])
                errors.extend(r[1])

        else:
            print(f"{bcolors.ERROR}Error: Failed getting '{s}'")
            errors.append(s)
    return results, errors

for s in letters:
    if os.path.isfile(f"{scrape_output}/{s}.csv"):
        print(f"{bcolors.OKBLUE}{s} is already done!")
    else:
        print(f"\n{bcolors.OKBLUE}Starting scraping {s}")
        t0 = time.time()
        results, errors = get_all_agents(s, delay, n_try)
        t1 = time.time()
        print(f"\n{bcolors.OKBLUE}Finished scraping {s} in {round(t1 - t0)} seconds!")
        if len(errors) > 0:
            print(f"{bcolors.ERROR}Errors in {s}: len(errors)")
        else:
            print(f"{bcolors.OKGREEN}No errors in {s}")
        data = [r for result in results for r in eval(result.content)]
        df = pd.DataFrame(data)
        df = df.drop_duplicates()
        df.to_csv(f"{scrape_output}/{s}.csv", quoting=csv.QUOTE_ALL, index=False, header=True)
        with open(f"{scrape_output}/{s}_error.json", "w") as f:
            json.dump({s: errors}, f)

dfs = []
ne = 0
for s in letters:
    if os.path.isfile(f"{scrape_output}/{s}.csv"):
        dfs.append(pd.read_csv(f"{scrape_output}/{s}.csv", dtype='object'))
    else:
        print(f"{bcolors.ERROR}Scraped data for {s}: is missing")
    if os.path.isfile(f"{scrape_output}/{s}_error.json"):
        with open(f"{scrape_output}/{s}_error.json", "r") as f:
            e = len(json.load(f)[s])
            if e > 0:
                print(f"{bcolors.ERROR}Errors in {s}: {e}")
                ne += e
    else:
        print(f"{bcolors.WARNING}Error data for {s}: is missing")

if ne > 0:
    print(f"\n{bcolors.ERROR}Total errors: {ne}")
else:
    print(f"\n{bcolors.OKGREEN}All done no errors!")

df = pd.concat(dfs).drop_duplicates()
df.to_csv(f"{scrape_output}/scrape_all.csv", quoting=csv.QUOTE_ALL, index=False, header=True)
