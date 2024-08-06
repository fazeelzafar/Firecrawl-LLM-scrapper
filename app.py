from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime

# Load environment variables once
load_dotenv()

# Initialize API clients once with proper checks
firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not firecrawl_api_key:
    raise ValueError("Firecrawl API key is not set in the environment variables.")
if not openai_api_key:
    raise ValueError("OpenAI API key is not set in the environment variables.")

fcApp = FirecrawlApp(api_key=firecrawl_api_key)
client = OpenAI(api_key=openai_api_key)

def dataScrapper(url):
    scrappedData = fcApp.scrape_url(url)
    if 'markdown' in scrappedData:
        return scrappedData['markdown']
    else:
        raise KeyError('Markdown non-existent in extracted data')

def saveRaw(rawData, timestamp, out_folder='Output'):
    os.makedirs(out_folder, exist_ok=True)
    out_path = os.path.join(out_folder, f'extracted_markdown_{timestamp}.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(rawData)
    print(f'Saved to {out_path}')

def formatData(data, fields=None):
    if fields is None:
        fields = ["Address", "Real Estate Agency", "Price", "Beds", "Baths", "Sqft", "Home Type", "Listing Age", "Picture of home URL", "Listing URL"]

    system_message = f"""You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
    from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
    with no additional commentary, explanations, or extraneous information."""

    user_message = f"Extract the following information from the provided text:\nPage content:\n\n{data}\n\nInformation to extract: {fields}"

    response = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    if response and response.choices:
        frData = response.choices[0].message.content.strip()
        try:
            jsonParsed = json.loads(frData)
            return jsonParsed
        except json.JSONDecodeError as e:
            raise ValueError(f"Data could not be decoded to JSON: {e}")
    else:
        raise ValueError("Expected choices data not available in OpenAI API response.")

def saveData(frData, timestamp, out_folder='Output'):
    os.makedirs(out_folder, exist_ok=True)
    
    # Save as JSON
    json_path = os.path.join(out_folder, f'json_Sorted_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(frData, f, indent=4)
    print(f'Formatted Data Saved to {json_path}')
    
    # Save as Excel
    if isinstance(frData, dict) and len(frData) == 1:
        key = next(iter(frData))
        frData = frData[key]

    if isinstance(frData, dict):
        frData = [frData]

    df = pd.DataFrame(frData)
    excel_path = os.path.join(out_folder, f'excel_Sorted_{timestamp}.xlsx')
    df.to_excel(excel_path, index=False)
    print(f'Excel formatted data saved to {excel_path}')

if __name__ == "__main__":
    url = 'https://www.zillow.com/salt-lake-city-ut/'
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scraped_data = dataScrapper(url)
        saveRaw(scraped_data, timestamp)
        formatted_data = formatData(scraped_data)
        saveData(formatted_data, timestamp)
    except Exception as e:
        print(f"Error occurred: {e}")
