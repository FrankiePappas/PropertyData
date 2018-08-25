import os
import sys

sys.path.append('/usr/local/lib/python3.6/site-packages')

from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from time import sleep
from random import randint
from PIL import Image
import pytesseract
import cv2
import urllib
from resizeimage import resizeimage
import re



def scrape_all_for_sale_pages(for_sale_page_01):
	
	for_sale_pages = []
	
	for_sale_pages.append(for_sale_page_01)
	print(for_sale_page_01)

	alpha = 2
	omega = 7062

	while alpha <= omega:

		page_prefix = for_sale_page_prefix
		page_slash = for_sale_page_slash
		page_number = alpha
		page_suffix = for_sale_page_suffix
		

		for_sale_page = page_prefix + page_slash + str(page_number) + page_suffix
		for_sale_pages.append(for_sale_page)

		print(for_sale_page)

		alpha = alpha + 1

	return(for_sale_pages)


def scrape_all_properties(for_sale_pages):

	# define headers
	headers = {"User-Agent": "Hello", "User-Agent": "My", "User-Agent": "Name", "User-Agent": "is", "User-Agent": "Property", "User-Agent": "24"}


	# create csv file
	file_directory = ""
	file_name = "ForSale_Houses_List_SouthAfrica.csv"
	file_path = file_directory + file_name

	# open csv file
	csv_file = open(file_path, "w")
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(["City_Name", "Suburb_Name", "Asking_Price", "Unit_Size", "Price / Square_Metre", "Bedrooms", "Bathrooms", "Parkings", "URL", "Estate_Agent"])

	# create lists to store scraped data
	property_cities = []
	property_suburbs = []
	property_asking_prices = []
	property_sizes = []
	property_prices_per_square_metre = []
	property_bedrooms = []
	property_bathrooms = []
	property_parkings =[]
	property_urls =[]
	property_estate_agents = []

	# prepare monitoring the loop
	for_sale_page_number = -1

	print("\nSCRAPE_ALL_PROPERTIES HAS BEGUN\n")

	# for every street href
	for for_sale_page in for_sale_pages:
		
		try:

			# sleep a random amount of time
			sleep(randint(1,3))
				
			for_sale_page_number = for_sale_page_number + 1

			for_sale_page = for_sale_pages[for_sale_page_number]

			# get street_url
			response = requests.get(for_sale_page, headers=headers)

			# create html_soup
			html_soup = BeautifulSoup(response.text, "lxml")

			# create a list of all the films_containers
			property_containers = html_soup.find_all("div", class_ ="p24_details")

			for property_container in property_containers:

				# get the property city
				if property_container.findAll("a")[0]:
					property_suburb_and_city = property_container.findAll("a")[0]["title"]
					property_suburb_and_city = str(property_suburb_and_city.encode("ascii","ignore"))
					property_suburb_and_city = property_suburb_and_city[2:-1]
					property_city = property_suburb_and_city.split(" ")[-1]
					property_cities.append(property_city)

					print("City: " + str(property_city))

				# get the property suburb
				if property_container.findAll("a")[0]:
					property_suburb_and_city = property_container.findAll("a")[0]["title"]
					property_suburb_and_city = str(property_suburb_and_city.encode("ascii","ignore"))
					property_suburb_and_city = property_suburb_and_city[2:-1]
					property_suburb_and_city = property_suburb_and_city.split(" in ")[1]
					property_suburb = property_suburb_and_city.split("-")[0].strip()
					property_suburbs.append(property_suburb)

					print("Suburb: " + str(property_suburb))


				# get the property_asking_price
				if property_container.find("span", class_="p24_content").find("span", class_="p24_schema").find("span", class_="p24_top").find("span", class_="p24_price")["content"]:
					property_asking_price = property_container.find("span", class_="p24_content").find("span", class_="p24_schema").find("span", class_="p24_top").find("span", class_="p24_price")["content"]
					property_asking_price = str(property_asking_price.encode("ascii","ignore"))
					property_asking_price = property_asking_price[2:-1]
					property_asking_price = property_asking_price.split(".")[0]	
				else: property_asking_price = 0

				property_asking_prices.append(property_asking_price)
				print("Price: " + property_asking_price)

				# get the property_size
				if property_container.find("span", class_="p24_icons").find("span", class_="p24_size"):
					property_size = property_container.find("span", class_="p24_icons").find("span", class_="p24_size").find("span", class_="p24_bold").text
					property_size = str(property_size.encode("ascii","ignore"))
					property_size = property_size[2:-1]
					if "m" in property_size:
						property_size = property_size.replace("m","").replace(" ", "")
						property_size = str(property_size).split(".")[0]
					elif "ha" in property_size:
						property_size = property_size.replace("ha","").replace(" ", "")
						property_size = float(property_size) * 10000
						property_size = str(property_size).split(".")[0]
					elif "acres" in property_size:
						property_size = property_size.replace("acres","").replace(" ", "")
						property_size = float(property_size) * 4047
						property_size = str(property_size).split(".")[0]

				else: property_size = 0	

				property_sizes.append(property_size)
				print("Size: " + str(property_size))

				# get the property_price_per_square_metre
				if property_container.find("span", class_="p24_icons").find("span", class_="p24_size"):
					if property_asking_price == "":
						property_asking_price = 0
					property_price_per_square_metre = int(property_asking_price) / int(property_size)
					property_price_per_square_metre = int(property_price_per_square_metre)
					property_prices_per_square_metre.append(property_price_per_square_metre)

					print("Price/sqm: " + str(property_price_per_square_metre))

				# get the property_bedroom
				if property_container.find("span", class_="p24_content").find("span", class_="p24_features"):
					property_features_container = property_container.find("span", class_="p24_content").find("span", class_="p24_features")
					if property_features_container.find("img", title="Beds"):
						property_bedroom = property_features_container.find("img", title="Beds").find_next_sibling("span").text
						property_bedroom = str(property_bedroom)
						property_bedroom = property_bedroom.strip()
					else: property_bedroom = 0

					property_bedrooms.append(property_bedroom)
					print("Bedrooms: " + str(property_bedroom))

				# get the property_bathroom
				if property_container.find("span", class_="p24_content").find("span", class_="p24_features"):
					property_features_container = property_container.find("span", class_="p24_content").find("span", class_="p24_features")
					if property_features_container.find("img", title="Bathrooms"):
						property_bathroom = property_features_container.find("img", title="Bathrooms").find_next_sibling("span").text
						property_bathroom = str(property_bathroom)
						property_bathroom = property_bathroom.strip()
					else: property_bathroom = 0

					property_bathrooms.append(property_bathroom)
					print("Bathrooms: " + str(property_bathroom))

				# get the property_parking
				if property_container.find("span", class_="p24_content").find("span", class_="p24_features"):
					property_features_container = property_container.find("span", class_="p24_content").find("span", class_="p24_features")
					if property_features_container.find("img", title="Garages"):
						property_parking = property_features_container.find("img", title="Garages").find_next_sibling("span").text
						property_parking = str(property_parking)
						property_parking = property_parking.strip()
					else: property_parking = 0	

					property_parkings.append(property_parking)
					print("Parkings: " + str(property_parking))

				# get the property_url
				if property_container.findAll("a")[0]["href"]:
					property_url = property_container.findAll("a")[0]["href"]
					property_url = str(property_url.encode("ascii","ignore"))
					property_url = property_url[2:-1]
					property_url = "https://www.property24.com/" + str(property_url)
					property_urls.append(property_url)

					print("URL: " + str(property_url))

				# get the property_estate_agent
				if property_container.find("span", class_="p24_content").find("span", class_="p24_schema").find("span", class_="js_agencyBrandingLink js_disablePropagation"):
					property_estate_agent = property_container.find("span", class_="p24_content").find("span", class_="p24_schema").find("span", class_="js_agencyBrandingLink js_disablePropagation")["title"]
					property_estate_agent = str(property_estate_agent.encode("ascii","ignore"))
					property_estate_agent = property_estate_agent[2:-1]
					property_estate_agent = property_estate_agent.split(" for ")[-1]
				else:
					property_estate_agent = "Not Available"

					property_estate_agents.append(property_estate_agent)
					print("Agent: " + str(property_estate_agent))

				# write info to csv
				csv_writer.writerow([property_city, property_suburb, property_asking_price, property_size, property_price_per_square_metre, property_bedroom, property_bathroom, property_parking, property_url, property_estate_agent])

				print("\n")

		except KeyError:
			print("KeyError encountered...")
			pass

		except ValueError:
			print("ValueError encountered...")
			pass			


# define houses_sale_page_01
for_sale_page_prefix = "https://www.property24.com/houses-for-sale/advanced-search/results"
for_sale_page_slash = "/p"
for_sale_page_number = 0
for_sale_page_suffix = r"?sp=pid%3d1%2c5%2c14%2c6%2c3%2c2%2c7%2c9%2c8"


for_sale_page_01 = for_sale_page_prefix + for_sale_page_suffix

# scrape all_houses_for_sale_pages from houses_for_sale_page_01
for_sale_pages = scrape_all_for_sale_pages(for_sale_page_01)

# scrape_all_properties from all_houses_for_sale_pages
scrape_all_properties(for_sale_pages)


# https://www.property24.com/houses-for-sale/advanced-search/results/p7062?sp=pid%3d1%2c5%2c14%2c6%2c3%2c2%2c7%2c9%2c8

