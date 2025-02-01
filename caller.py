import random
from typing import Set
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import time
from bs4 import BeautifulSoup

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)



def find_activities_by_type(activity_type: str, count: int = 3) -> Set[str]:
    """
    Retrieves a set of unique activities based on a specified activity type using the Bored API. It aims to return a specified
    number of unique activities.
    """

    # Define a set to keep track of activities
    activities = set() 

    # Create attempts variable to keep track of how many times API is called 
    attempts = 0 
    max_attempts = 3 * count 

    while len(activities) < count and attempts < max_attempts: 
        response = requests.get(f"http://www.boredapi.com/api/activity?type={activity_type}")

        if response.status_code == 200: 
            actual_activity_data = response.json()
            activities.add(actual_activity_data.get('activity'))

        attempts = attempts + 1

    return activities


def generate_story_text(
    activity_type: str, name: str, product_id: str, story_starter: str
) -> str:
    """
    Crafts a story using OpenAI API influenced by the given activity type, name, product ID, and an
    optional story starter.
    """


    activity_set = find_activities_by_type(activity_type)
    if activity_set:
        activity = random.choice(list(activity_set))
    else:
        activity = "relaxing"
    age = get_age_estimate(name)
    product = get_product_name_from_id(product_id)

    # Construct the prompt
    if story_starter:
        story_starter = f" {story_starter}"
    prompt = f"{name}, aged {age},{story_starter} was enjoying {activity} with {product}."

    # Generate the story
    story = get_completion(prompt)
    return story

def get_age_estimate(name: str) -> int:
    """
    Predicts a person's age based on their first name utilizing the Agify API.
    """

    response = requests.get(f"https://api.agify.io?name={name}")
    age_data = response.json()

    return age_data.get('age')



def get_product_name_from_id(product_id: str) -> str:
    """
    Extracts a product name using its ID from an online marketplace similar to eBay, starting at `https://www.etsy.com/listing/{id}`.
    It includes redirect following and scraping the final page for the product name.
    """

    url = f"https://www.etsy.com/listing/{product_id}"

    response = requests.get(url)
    html_content = response.text


    soup = BeautifulSoup(response.text, "html.parser")
    product_name_tag = soup.find("h1", {"data-buy-box-listing-title": "true"})

    if product_name_tag is None:
        # Additional check for any possible changes in the tag or attributes
        product_name_tag = soup.find("h1", class_="wt-text-body-01")
        if product_name_tag is None:
            return "Product name not found"  # Return a default or error message if no tag is found

    name = product_name_tag.text.strip()
    return name

def get_completion(prompt, model="gpt-3.5-turbo"):

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=0)
    return response.choices[0].message.content