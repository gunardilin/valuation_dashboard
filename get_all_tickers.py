import pandas as pd
import urllib.request as request
import json

def get_companies_from_sec():
    URL1 = 'https://www.sec.gov/files/company_tickers_exchange.json'
    URL2 = 'https://www.sec.gov/files/company_tickers.json'

    try:
        sec_dict = request.urlopen(URL1)
        mode = '1'
    except:
        sec_dict = request.urlopen(URL2)
        mode = '2'
    for line in sec_dict:
        decoded_line = line.decode("utf-8")
    company_dict = json.loads(decoded_line)
    if mode == '1':
        company_df = pd.DataFrame(company_dict['data'],columns=['cik', 'Security',
            'Symbol', 'exchange'])
    elif mode == '2':
        company_df = pd.DataFrame.from_dict(company_dict, orient='index')
        company_df.rename(columns={"cik_str": "cik", "ticker": "Symbol", \
            "title": "Security"}, inplace=True)
    return company_df[['Symbol', 'Security']]

def format_for_dashdropdown(pddataframe):
    return [{'label': "{}, {}".format(pddataframe.iloc[i].Symbol, 
                                        pddataframe.iloc[i].Security), 
             'value': pddataframe.iloc[i].Symbol} 
            for i in range(len(pddataframe.index))]

if __name__ == "__main__":
    print(format_for_dashdropdown(get_companies_from_sec().head()))