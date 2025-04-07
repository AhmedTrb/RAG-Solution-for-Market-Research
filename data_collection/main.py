import requests
from bs4 import BeautifulSoup
import json 
import random
import time
from fake_useragent import UserAgent
from urllib.parse import urljoin, quote
from configgeneral import configurations
import re
import argparse
from dotenv import load_dotenv

load_dotenv()
import os

def clean_comment(text):
    if not text or text == 'N/A':
        return ''
    text = ' '.join(text.strip().split())
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = text.replace('"', "'")
    return text + '\n' 

# Fonction pour utiliser ScraperAPI
def fetch_with_scraperapi(url, api_key):
    api_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"
    try:
        response = requests.get(api_url, timeout=30)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        print(f"Erreur ScraperAPI: {str(e)}")
        return None

# Headers pour le fallback
def get_random_headers():
    user_agent = UserAgent()
    return {'User-Agent': user_agent.random, 'Accept-Language': 'en-US,en;q=0.9'}

# Fonctions d'extraction
def extract_product_urls(soup, base_url, config):
    product_urls = []
    products = soup.find_all(
        config['product_container']['tag'],
        config['product_container']['attrs']
    )
    
    for product in products:
        link = product.find(
            config['product_link']['tag'],
            config['product_link']['attrs']
        )
        if link and 'href' in link.attrs:
            product_url = urljoin(base_url, link['href'])
            if config['url_cleanup']:
                product_url = product_url.split('?')[0]
            product_urls.append(product_url)
    return product_urls

def extract_product_details(soup, url, config):
    try:
        result = {"URL": url}
        for field_name, field_config in config['fields'].items():
            try:
                if 'attrs' in field_config:
                    elements = soup.find_all(field_config['selector'], field_config['attrs'])
                else:
                    elements = soup.select(field_config['selector'])
                if elements:
                    if field_name == 'comment':
                        raw_text = elements[0].get_text(strip=True) if elements else 'N/A'
                        result[field_name] = clean_comment(raw_text)
                    else:
                        result[field_name] = field_config['processing'](elements[0] if elements else None)
                else:
                    result[field_name] = config['default_value']
            except Exception as field_error:
                print(f"Erreur traitement champ {field_name}: {str(field_error)}")
                result[field_name] = config['default_value']       
        return result
    except Exception as e:
        print(f"Erreur extraction détails produit: {str(e)}")
        return None
    
def get_next_page_url(soup, base_url, config):
    if not config['enabled']:
        return None
    next_page = soup.find(config['selector'], config['attrs'])
    return urljoin(base_url, next_page['href']) if next_page and 'href' in next_page.attrs else None

def scrape_website(platform, query):
    """Fonction principale pour scraper une plateforme spécifique"""
    config = configurations[platform]
    data = []
    start_url = config['start_url'].format(query=quote(query))
    current_url = start_url
    page_count = 1
    
    print(f"\nScraping {platform} pour: '{query}'")
    print(f"URL: {start_url}")

    while current_url and page_count <= config['MAX_PAGES']:
        print(f"Page {page_count} - {current_url}")
        time.sleep(random.uniform(1, 3))

        html_content = fetch_with_scraperapi(current_url,os.getenv('SCRAPERAPI_KEY'))
        if not html_content:
            try:
                response = requests.get(current_url, headers=get_random_headers())
                html_content = response.text if response.status_code == 200 else None
            except Exception as e:
                print(f"Erreur requête directe: {str(e)}")
                break

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            product_urls = extract_product_urls(soup, config['base_url'], config['URL_EXTRACTION_CONFIG'])
            print(f"Produits trouvés: {len(product_urls)}")    
            
            for product_url in product_urls[:10]:  
                print(f"Scraping: {product_url}")
                time.sleep(random.uniform(2, 5))
                
                product_html = fetch_with_scraperapi(product_url,os.getenv('SCRAPERAPI_KEY'))
                if not product_html:
                    try:
                        response = requests.get(product_url, headers=get_random_headers())
                        product_html = response.text if response.status_code == 200 else None
                    except Exception as e:
                        print(f"Erreur requête produit: {str(e)}")
                        continue
                
                if product_html:
                    product_soup = BeautifulSoup(product_html, 'html.parser')
                    product_data = extract_product_details(
                        product_soup, product_url, config['DETAILS_EXTRACTION_CONFIG'])
                    if product_data:
                        data.append(product_data)
            
            current_url = get_next_page_url(
                soup, config['base_url'], config['PAGINATION_CONFIG']['next_page'])
            page_count += 1
        else:
            print("Aucun contenu HTML reçu")
            break
    return data

def scrape_all_websites(query):
    """Scraper toutes les plateformes configurées"""
    all_data = {}
    for platform in configurations.keys():
        platform_data = scrape_website(platform, query)
        all_data[platform] = platform_data
    
    # Sauvegarde combinée
    combined_filename = f"all_products_{query.replace(' ', '_')}.json"
    with open(combined_filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"\nToutes les données sauvegardées dans {combined_filename}")

def main():
    parser = argparse.ArgumentParser(description='Scraper e-commerce')
    parser.add_argument('--query', type=str, required=True, help='Terme de recherche')
    args = parser.parse_args()
    
    if not args.query:
        print("Veuillez spécifier une requête avec --query")
        return
    
    print(f"\nLancement du scraping pour: '{args.query}'")
    scrape_all_websites(args.query)

if __name__ == "__main__":
    main()