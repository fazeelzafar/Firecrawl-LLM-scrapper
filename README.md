# Web Scrapping using Firecrawl and GPT-4o

Firecrawl-LLM Scrapper is a web scraping tool designed to extract data from websites using Large Language Models (LLMs). It uses Firecrawl, which is an API service that takes a URL, crawls it, and converts it into clean markdown or structured data. The clean data is then passed on to OpenAI's GPT-4o model to extract the data needed from a webpage.

Clone the repository and then run the command:
```
pip install -r requirements.txt
```

After the libraries are installed, you will need to open the ```app.py``` file and set the ```url``` variable to the URL that you want to scrape. The code in this repository is set to scrape real estate websites by default but can be adapted to scrape other websites as well.

To scrape a different website, you must also set the ```Fields``` that you want to extract from the scraped webpage in the fields list. For example, if you're scraping products on Amazon, you can set "Product Name," "Product Title," "Price," "Ratings," "Reviews," etc., in the ```fields``` list to extract all of that information.
