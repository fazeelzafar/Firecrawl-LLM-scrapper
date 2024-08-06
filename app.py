from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime

def dataScrapper(url):
    load_dotenv()

    fcApp = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

    scrappedData = fcApp.scrape_url(url)
    # if 'markdown' in scrappedData:
    #     return scrappedData['markdown']
    # else:
    #     raise KeyError('Markdown non-existent in extracted data')
    
    return scrappedData['markdown'] if 'markdown' in scrappedData else print('Markdown non-existent in extracted data')
    
def saveRaw(rawData, timestamp, out_folder='Output'):

    os.makedirs(out_folder, exist_ok=True)

    out_path = os.path.join(out_folder, f'extracted_markdown{timestamp}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(rawData)
    print(f'Saved to {out_path}')


def formatData(data, fields=None):
    load_dotenv()

    client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))

    if fields is None:
        fields = ["Address", "Real Estate Agency", "Price", "Beds", "Baths", "Sqft", "Home Type", "Listing Age", "Picture of home URL", "Listing URL"]

    system_message = f"""You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
                        from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
                        with no additional commentary, explanations, or extraneous information. 
                        You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words before or after the JSON:"""
    
    user_message = f"Extract the following information from the provided text:\nPage content:\n\n{data}\n\nInformation to extract: {fields}"

    response = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

    )

    if response and response.choices:
        frData = response.choices[0].message.content.strip()
        print(f"Received formatted data{frData} from OpenAI API")

        try:
            jsonParsed = json.loads(frData)
        except json.JSONDecodeError as e:
            print(f"Decoding Error: {e}")
            print(f"data that caused the error: {frData}")

            raise ValueError("Data could not be decoded to JSON")
        return jsonParsed
    
    else:
        raise ValueError("Expected choices data not available OpenAI API response.")
    

def saveData(frData, timestamp, out_folder='Output'):
    
    os.makedirs(out_folder, exist_ok=True)
    out_path = os.path.join(out_folder, f'json_Sorted{timestamp}.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(frData, f, indent=4)
    print(f'Fomatted Data Saved to {out_path}')


    if isinstance(frData, dict) and len(frData) == 1:
        key = next(iter(frData))
        frData = frData[key]
    df = pd.DataFrame(frData)


    if isinstance(frData, dict):
        frData = [frData]
    df = pd.DataFrame(frData)


    excelPath = os.path.join(out_folder, f'excel_Sorted{timestamp}.json')
    df.to_excel(excelPath, index=False)
    print(f"Excel formatted data saved to {excelPath}")


if __name__ == "__main__":

    url = 'https://www.zillow.com/salt-lake-city-ut/'
    # url = 'https://www.trulia.com/CA/San_Francisco/'
    
    try:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        scrape = dataScrapper(url)
        rawSave = saveRaw(scrape, ts)
        formattedData = formatData(rawSave)
        saveFormattedData = saveData(formattedData, ts)
    except Exception as e:
        print(f"Error occured: {e}")
