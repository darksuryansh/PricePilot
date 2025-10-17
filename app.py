import subprocess
import json
from flask import Flask, render_template, request, jsonify
import os

# Initialize the Flask application
app = Flask(__name__)

# The main route for your website's homepage
@app.route('/')
def index():
    # This just shows the main webpage to the user.
    return render_template('index.html')

# The API route that the frontend will call to start scraping
@app.route('/scrape', methods=['POST'])
def scrape():
    # Get the product URL that the user submitted
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    spider_name = ''
    # Determine which spider to use based on the URL
    if 'amazon.in' in url:
        spider_name = 'amazon'
    elif 'myntra.com' in url:
        spider_name = 'myntra'
    elif 'flipkart.com' in url:
        spider_name = 'flipkart'
    elif 'meesho.com' in url:
        spider_name = 'meesho'
    else:
        return jsonify({'error': 'Unsupported website'}), 400

    # Define the output file for the scraped data
    output_file = 'output.json'
    
    # --- IMPORTANT ---
    # We need to run the scrapy command from its project directory
    scrapy_project_path = 'price_scraper'
    
    # Construct the Scrapy command
    # We use "-O" to overwrite the file each time for simplicity
    command = [
        'scrapy', 'crawl', spider_name, 
        '-O', output_file, 
        '-a', f'start_url={url}' # Pass the URL to the spider
    ]

    try:
        # Run the Scrapy command from the correct directory
        subprocess.run(command, check=True, cwd=scrapy_project_path)
        
        # After the spider runs, read the JSON file it created
        with open(os.path.join(scrapy_project_path, output_file), 'r') as f:
            # The output is a list of items, we just need the first one
            data = json.load(f)
            if data:
                return jsonify(data[0])
            else:
                return jsonify({'error': 'Could not scrape data.'}), 500

    except subprocess.CalledProcessError as e:
        # If the scrapy command fails, return an error
        return jsonify({'error': f'Scraping failed: {e}'}), 500
    except FileNotFoundError:
        # If the output file isn't created, return an error
        return jsonify({'error': 'Output file not found after scraping.'}), 500
    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

# This allows you to run the app directly
if __name__ == '__main__':
    app.run(debug=True)
