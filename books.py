import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import random
import re

def loadUserAgents(file='user_agents.txt'):
	with open(file, 'r') as f:
		data = f.readlines()
	data = [{"User-Agent":x[0:-1]} for x in data] #remove \n from string
	return data

def saveBook(href, author, title, dir=Path.cwd()):
	extension = href.split(".")[-1]
	file_name = fr'{author} - {title}.{extension}'
	file_name = file_name.replace('/', '-').replace(':', '-').replace(',', '-')
	save_path = dir / file_name
	download_url = fr'https://link.springer.com{href}'

	print(fr'{download_url} --> {save_path}')

	response = requests.get(download_url)
	expdf = response.content
	egpdf = save_path.open("wb")
	egpdf.write(expdf)
	egpdf.close()

def getBooks(row, user_agent_dict):
	#/content/pdf/10.1007%2F0-306-48048-4_16.pdf
	# https://link.springer.com/
	url = row['OpenURL']
	tree = requests.get(url, headers=random.choice(user_agent_dict))
	tree.raise_for_status()
	soup = BeautifulSoup(tree.content, 'html.parser')

	links = soup.findAll('a', attrs={'href': re.compile("/content/")})
	href = links[0].get('href')

	title = row['Book Title']
	author = [x.strip() for x in row['Author'].split(',')]

	if len(author) > 2:
		author = " & ".join(author[0:2]) + ', Et al.'
	elif len(author) == 2:
		author = " & ".join(author[0:2])
	else:
		author = author[0]

	saveBook(href, author, title)


if __name__ == "__main__":
	df = pd.read_csv('free_books.csv', usecols=['Book Title','Author','OpenURL'])
	user_agents_dict = loadUserAgents()

	df.apply(lambda row: getBooks(row, user_agents_dict), axis=1)
