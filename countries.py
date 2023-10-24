import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List
import geopandas as gpd


class City:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


class Country:
    def __init__(self, name: str, cities):
        self.name = name
        self.cities = cities

    def city_names(self):
        cities = []
        for city in self.cities:
            cities.append(city.name)
        return cities


def fetch_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch the webpage. Status Code: {response.status_code}"
        )

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")

    # Get headers
    headers = [th.text for th in table.find("tr").find_all("th")]

    # Get data
    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        values = [td.text for td in row.find_all("td")]
        data.append(values)
    return data, headers


def fetch_countries_csv(url):
    data, headers = fetch_data(url)

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(data, columns=headers)
    df.to_csv("countries.csv", index=False)
    return df


def fetch_cities_csv(url, abbreviation):
    data, headers = fetch_data(url)
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(f"{abbreviation}.csv", index=False)
    return df


def get_country_names_from_webpage(url, csv_url):
    # Load the CSV data into a pandas DataFrame
    df = fetch_countries_csv(csv_url)

    # Get list of countries from the 'name' column
    countries = df["name"].tolist()

    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch the webpage. Status Code: {response.status_code}"
        )

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract all text from the webpage
    webpage_text = soup.get_text().split()

    country_names = list(set(word for word in webpage_text if word in countries))
    abbreviations = df.set_index("name").loc[country_names, "country"].tolist()
    countries = list(zip(country_names, abbreviations))

    return countries, country_names


def get_city_names_from_webpage(abbreviation, url):
    csv_url = f"https://geokeo.com/database/city/{abbreviation.lower()}/"
    df = fetch_cities_csv(csv_url, abbreviation)
    cities_df = df["Name"].tolist()

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch the webpage. Status Code: {response.status_code}"
        )

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract all text from the webpage
    webpage_text = soup.get_text().split()

    # Identify country names in the webpage text
    city_names = list(set(word for word in webpage_text if word in cities_df))
    latitude = df.set_index("Name").loc[city_names, "Latitude"].tolist()
    longitude = df.set_index("Name").loc[city_names, "Longitude"].tolist()
    cities = list(zip(city_names, latitude, longitude))
    return cities, city_names


def preprocess_countries(countries, url):
    country_objects = []
    for country in countries:
        cities, city_names = get_city_names_from_webpage(country[1], url)
        city_objects = []
        # Not done
        for city in cities:
            city_objects.append(City(name=city[0], latitude=city[1], longitude=city[2]))
        country_objects.append(Country(name=country[0], cities=city_objects))
    return country_objects


def runner():
    url = "https://www.cnbc.com/2023/10/19/israel-hamas-war-gaza-live-updates-latest-news.html"
    csv_url = "https://developers.google.com/public-data/docs/canonical/countries_csv"
    countries, country_names = get_country_names_from_webpage(url, csv_url)
    country_objects = preprocess_countries(countries, url)
    cities = []
    for country in country_objects:
        for city in country.cities:
            cities.append(city)
    return countries, country_names, cities
