import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download('punkt')  # Download the punkt tokenizer data if not already downloaded

# Function to display usage instructions in the sidebar
def display_instructions():
    st.sidebar.title(" NOTE: Since all generative AIs that are available on the internet were either paid or unusable in our required app, I was unable to make use of the generative AI to create more natural conversations with the bot. However the bot still works to provide the straightforward answers to our commands.")
    st.sidebar.title("Instructions")
    st.sidebar.markdown("1. Enter the product URL in the main section.")
    st.sidebar.markdown("2. Type your query or command in the 'You >>' text area.")
    st.sidebar.markdown("3. Click the 'Send' button to get information.")
    st.sidebar.markdown("4. Valid commands: 'price', 'rating', 'availability', 'reviews'")
    st.sidebar.markdown("5. Example commands: 'What's the price?', 'Show me the rating', 'Tell me about availability', 'Get reviews'")
    st.sidebar.markdown("6. The assistant will respond with the requested information.")
    st.sidebar.markdown("7. You can have a conversation by typing sentences or asking questions.")

# Function to summarize text
def summarize_text(text, num_sentences):
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

# Main chatbot function
def main():
    st.title("SHopy, your Shopping assistant :)")
    st.write("Give me the link for the product:")
    
    webpage_url = st.text_input("URL")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    user_input = st.text_area("You >> ", value=st.session_state.user_input)
    
    if st.button("Send"):
        st.session_state.user_input = user_input.lower()
        st.session_state.chat_history.append(f"You: {st.session_state.user_input}")
        
        # Scrape product data
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            session = requests.Session()
            time.sleep(2)
            response = session.get(webpage_url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get title
                try:
                    title = soup.find("span", attrs={"id": 'productTitle'})
                    title_value = title.text
                    title_string = title_value.strip()
                    if title_string == "Title not available":
                        title_string = None
                except Exception:
                    title_string = None

                # Get price
                try:
                    price_whole = soup.find("span", class_='a-price-whole').text.strip()
                    price_fractional = soup.find("span", class_='a-price-fraction').text.strip()
                    price_currency = soup.find("span", class_='a-price-symbol').text.strip()
                    price = f"{price_currency}{price_whole}.{price_fractional}"
                except Exception:
                    price = "Price not available"

                # Get rating
                try:
                    rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
                except Exception:
                    try:
                        rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
                    except:
                        rating = "Rating not available"

                # Get availability
                try:
                    available = soup.find("div", attrs={'id': 'availability'})
                    available = available.find("span").string.strip()
                except Exception:
                    available = "Availability not available"

                # Get reviews
                reviews = []
                review_elements = soup.find_all("div", class_="a-row a-spacing-small review-data")

                for i, element in enumerate(review_elements[:10]):  # Extract the first 10 reviews
                    review_text = element.find("span", class_="a-size-base review-text").text.strip()
                    review_lines = review_text.split('\n')
                    for line in review_lines:
                        if line.strip():
                            reviews.append(f"{i + 1}. {line.strip()}")

                if not reviews:
                    reviews = ["No reviews available"]  # Assign a default value if no reviews are found

                if 'reviews' in st.session_state.user_input:
                    # Summarize the reviews
                    num_reviews_to_display = 5  # You can adjust this number as needed
                    review_summary = summarize_text('\n'.join(reviews), num_reviews_to_display)

                    # Display the review summary
                    st.session_state.chat_history.append("Here is a summary of the reviews:")
                    st.session_state.chat_history.append(review_summary)
                else:
                    scraped_data = {
                        'title': title_string,
                        'price': price,
                        'rating': rating,
                        'availability': available,
                        'reviews': reviews,
                    }

                    st.success("Data successfully scraped!")

                    # Display only the title of the product under the "Scraped Product Data" section
                    st.header("Scraped Product Data")
                    st.write(f"Title: {title_string}")

                    # Extract keywords from user input
                    keywords = st.session_state.user_input.split()
                    found_match = False

                    for key in keywords:
                        if key in scraped_data:
                            value = scraped_data[key]
                            response = f"The {key} of the product is: {value}"
                            st.session_state.chat_history.append(response)
                            found_match = True

                    if not found_match:
                        st.session_state.chat_history.append("I'm sorry, I didn't understand your question. Could you please rephrase it?")
                        
            else:
                st.error(f"Failed to retrieve the Amazon page: {webpage_url}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
        st.session_state.user_input=""
        
    st.text_area("Chat:", value="\n".join(st.session_state.chat_history), height=200)

# Display usage instructions in the sidebar
display_instructions()

main()
