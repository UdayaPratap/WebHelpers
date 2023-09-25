import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

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

                if title_string:
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
                    st.error("Product title is not available.")
            else:
                st.error(f"Failed to retrieve the Amazon page: {webpage_url}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            
        st.session_state.user_input=""
        
    st.text_area("Chat:", value="\n".join(st.session_state.chat_history), height=200)

main()

# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# import time
# def main():
#     st.title("SHopy, your Shopping assistant :)")
#     st.write("Give me the link for the product:")
    
#     webpage_url = st.text_input("URL")
    
#     if 'chat_history' not in st.session_state:
#         st.session_state.chat_history = []
#     if 'user_input' not in st.session_state:
#         st.session_state.user_input = ""
    
#     user_input = st.text_area("You >> ", value=st.session_state.user_input)
    
#     if st.button("Send"):
#         st.session_state.user_input = user_input.lower()
#         st.session_state.chat_history.append(f"You: {st.session_state.user_input}")
        
#         # Scrape product data
#         try:
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             }
#             session = requests.Session()
#             time.sleep(2)
#             response = session.get(webpage_url, headers=headers)

#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, 'html.parser')
                
#                 # Get title
#                 try:
#                     title = soup.find("span", attrs={"id": 'productTitle'})
#                     title_value = title.text
#                     title_string = title_value.strip()
#                     if title_string == "Title not available":
#                         title_string = None
#                 except Exception:
#                     title_string = None

#                 # Get price
#                 try:
#                     price_whole = soup.find("span", class_='a-price-whole').text.strip()
#                     price_fractional = soup.find("span", class_='a-price-fraction').text.strip()
#                     price_currency = soup.find("span", class_='a-price-symbol').text.strip()
#                     price = f"{price_currency}{price_whole}.{price_fractional}"
#                 except Exception:
#                     price = "Price not available"

#                 # Get rating
#                 try:
#                     rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()
#                 except Exception:
#                     try:
#                         rating = soup.find("span", attrs={'class': 'a-icon-alt'}).string.strip()
#                     except:
#                         rating = "Rating not available"

#                 # Get availability
#                 try:
#                     available = soup.find("div", attrs={'id': 'availability'})
#                     available = available.find("span").string.strip()
#                 except Exception:
#                     available = "Availability not available"

#                 # Get reviews
#                 reviews = []
#                 review_elements = soup.find_all("div", class_="a-row a-spacing-small review-data")

#                 for i, element in enumerate(review_elements[:10]):  # Extract the first 10 reviews
#                     review_text = element.find("span", class_="a-size-base review-text").text.strip()
#                     review_lines = review_text.split('\n')
#                     for line in review_lines:
#                         if line.strip():
#                             reviews.append(f"{i + 1}. {line.strip()}")

#                 if not reviews:
#                     reviews = ["No reviews available"]  # Assign a default value if no reviews are found
    
#                 if not reviews:
#                     reviews = ["No reviews available"]  # Assign a default value if no reviews are found

#                 if title_string:
#                     scraped_data = {
#                         'title': title_string,
#                         'price': price,
#                         'rating': rating,
#                         'availability': available,
#                         'reviews': reviews,
#                     }
                    
#                     st.success("Data successfully scraped!")
                    
#                     # Display only the title of the product under the "Scraped Product Data" section
#                     st.header("Scraped Product Data")
#                     st.write(f"Title: {title_string}")
                    
#                     found_match = False

#                     for key in scraped_data.keys():
#                         if key in st.session_state.user_input:
#                             value = scraped_data.get(key, "Not available.")
#                             response = f"The {key} of the product is: {value}"
#                             st.session_state.chat_history.append(response)
#                             found_match = True

#                     if not found_match:
#                         st.session_state.chat_history.append("I'm sorry, I didn't understand your question. Could you please rephrase it?")
                        
#                 else:
#                     st.error("Product title is not available.")
#             else:
#                 st.error(f"Failed to retrieve the Amazon page: {webpage_url}")
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
            
#         st.session_state.user_input=""
        
#     st.text_area("Chat:", value="\n".join(st.session_state.chat_history), height=200)

# main()
