import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
nltk.download('punkt')
import spacy

# Function to extract Product title
def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.text
        title_string = title_value.strip()
    except Exception:
        title_string = "Title not available"  # Assign a default value
    return title_string

# Function to extract Product Prices
def get_price(soup):
    try:
        price_whole = soup.find("span", class_='a-price-whole').text.strip()
        price_fractional = soup.find("span", class_='a-price-fraction').text.strip()
        price_currency = soup.find("span", class_='a-price-symbol').text.strip()
        price = f"{price_currency}{price_whole}.{price_fractional}"
    except Exception:
        price = "Price not available"  # Assign a default value
    return price

# Function to extract Product Rating
def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
    except Exception:
        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = "Rating not available"  # Assign a default value
    return rating

# Function to extract the number of reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).string.split()
    except Exception:
        review_count = "Review count not available"  # Assign a default value
    return review_count

# Function to extract the Product description
def get_product_description(soup):
    return "Description not available"
    # try:
    #     description = soup.find("ul", class_="a-unordered-list a-vertical a-spacing-mini")
    #     if description:
    #         description_text = " ".join([item.text.strip() for item in description.find_all("span", class_="a-list-item")])
    #         if description_text:
    #             return description_text
    #         else:
    #             return "Description not available"
    # except Exception:
    #     return "Description not available"  # Assign a default value

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()
    except Exception:
        available = "Availability not available"  # Assign a default value
    return available

# Function to extract product reviews
def get_reviews(soup):
    reviews = []
    review_elements = soup.find_all("div", class_="a-row a-spacing-small review-data")
    
    for element in review_elements[:10]:  # Extract the first 10 reviews
        review_text = element.find("span", class_="a-size-base review-text").text.strip()
        reviews.append(review_text)
    
    if not reviews:
        reviews = ["No reviews available"]  # Assign a default value if no reviews are found
    
    return reviews

# Function to scrape a single URL and store data in a dictionary
def scrape_single_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # Create a session to manage cookies and maintain state
        session = requests.Session()
        time.sleep(2)
        # Use the session for making requests
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {
                'title': get_title(soup),
                'price': get_price(soup),
                'rating': get_rating(soup),
                'reviews': get_reviews(soup),
                'availability': get_availability(soup),
                'description': get_product_description(soup)
            }
            return data
        else:
            st.error(f"Failed to retrieve the Amazon page: {url}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function for extractive summarization
def extractive_summarize(text, num_sentences=2):
    sentences = sent_tokenize(text)
    word_frequencies = {}
    
    for sentence in sentences:
        words = word_tokenize(sentence)
        for word in words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence):
            if word in word_frequencies:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] += word_frequencies[word]
    
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(summary_sentences)
    
    return summary

def chatbot(scraped_data, summarized_description, summarized_reviews):
    st.subheader("Chat with SHopy - Your Shopping Assistant")

    chatbot_responses = {
        'title': ['name', 'title', 'brand', 'product name', 'what is it called'],
        'price': ['price', 'cost', 'how much', 'value', 'worth', 'expense'],
        'description': ['short description', 'brief description', 'describe', 'details', 'detail', 'specs', 'specifications', 'features'],
        'rating': ['rating', 'ratings', 'rated', 'stars', 'feedback', 'reviews'],
        'reviews_count': ['reviews count', 'no of reviews', 'number of reviews', 'how many reviews'],
        'availability': ['deliver', 'delivery', 'available', 'availability', 'in stock', 'can I buy it'],
        'all_info': ['display all data', 'display all info', 'display all information', 'give all info', 'show everything', 'show all details']
    }

    # Function to initialize the conversation state
    def init_conversation():
        return []
    # Function to get the current conversation
    def get_conversation():
        if "conversation" not in st.session_state:
            st.session_state.conversation = init_conversation()
        return st.session_state.conversation
    # Initialize conversation
    conversation = get_conversation()
    # User input
    user_input = st.text_input("You:")
    
    # Submit button
    if st.button("Send"):
        user_input = user_input.lower()
        conversation.append(f"You: {user_input}")
        found_match = False
        for key, synonyms in chatbot_responses.items():
            for synonym in synonyms:
                if synonym in user_input.lower():
                    if key == 'description':
                        if 'short' in user_input.lower() or 'brief' in user_input.lower():
                            description = summarized_description if summarized_description else "No description available."
                            response = f"Short Description: {description}"
                        else:
                            description = scraped_data.get('description', "No description available.")
                            response = f"Full Description: {description}"
                    elif key == 'reviews':
                        if 'summarized' in user_input.lower():
                            reviews = summarized_reviews if summarized_reviews else "No summarized reviews available."
                            response = f"Summarized Reviews: {reviews}"
                        else:
                            reviews = "\n".join(scraped_data.get('reviews', []))
                            if reviews:
                                response = f"Full Reviews:\n{reviews}"
                            else:
                                response = "No reviews available."
                    else:
                        value = scraped_data.get(key, "Not available.")
                        response = f"The {key} of the product is: {value}"
                    found_match = True
        if not found_match:
            response = "I'm sorry, I didn't understand your question. Could you please rephrase it?"
        conversation.append(response)

    # Display conversation history
    st.text_area("Conversation History", value="\n".join(conversation), key="conversation_history")

# Streamlit app
def main():
    st.title("SHopy - Your Shopping Assistant")

    # Input for webpage URL
    webpage_url = st.text_input("Enter the URL of the webpage:")

    if st.button("Scrape Product Data"):
        scraped_data = scrape_single_url(webpage_url)

        if scraped_data:
            # Display the scraped data
            st.header("Scraped Product Data")
            st.write(scraped_data)

            # Access the description and reviews from your scraped_data dictionary
            description = scraped_data['description']
            reviews = "\n".join(scraped_data['reviews'])  # Join multiple reviews into a single string

            # Apply extractive summarization to the description and reviews
            summarized_description = extractive_summarize(description)
            summarized_reviews = extractive_summarize(reviews, num_sentences=3)  # Adjust the number of sentences as needed

            st.header("Summarized Description:")
            st.write(summarized_description)

            st.header("Summarized Reviews:")
            st.write(summarized_reviews)

            chatbot(scraped_data, summarized_description, summarized_reviews)

if __name__ == "__main__":
    main()
