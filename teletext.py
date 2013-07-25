import urllib.request
import re
import logging

def get_page(page_num):
	base_page='http://www.ceskatelevize.cz/services/teletext/text.php?channel=CT1&page='
	page_url = base_page + str(page_num)
	response = urllib.request.urlopen(page_url)
	page = str(response.read(), encoding='windows-1250')
	lines = page.split('\n')
	return lines

def remove_pre(page_lines):
	return [line for line in page_lines if not re.match('\s*</?pre>\s*', line)]

class Headline:
	def __init__(self, category, headline, page):
		self.category = category
		self.headline = headline
		self.page = page

	def __str__(self):
		return '[' + self.category + '] ' + self.headline + ' ' + self.page 
	
class ContentParser:
	def __init__(self, text):
		self.pages = text
		self._current_category = None
		self.headlines = None

	def get_categories(self):
		if not self.categories:
			self.categories = self.parse_pages()
		return self.categories
		
	def get_category(self, line):
		# TODO: Should allow only caps
		match = re.match(r'^ ((\w+ )+)\s*(obsah \d)?$', line) 
		if match:
			return match.group(1).strip()
		return None

	def get_headlines(self):
		if self.headlines:
			return self.headlines
		
		content_iter = self.pages.__iter__()
		self.headlines = []
		while True:
			try:
				headline = self._get_headline(content_iter)
				self.headlines.append(headline)
			except StopIteration:
				return self.headlines

	def _get_headline(self, lines_iter):
		
		headline = ''
		
		while True:
			line = lines_iter.__next__()
			logger.debug('Processed line: ' + line)

			category = self.get_category(line)
			partial_headline_match = re.match('^ (\S.*/)\s*$', line)
			headline_match = re.match('^ (\S.*[^\.])\.* (\d\d\d)$', line)
			
			if category:
				logger.debug('Change category: ' + category)
				self._current_category = category 
			elif partial_headline_match:
				logger.debug('Found partial headline: ' + partial_headline_match.group(1))
				headline = headline + partial_headline_match.group(1) + ' '
			elif headline_match:
				headline = headline + headline_match.group(1)
				page = headline_match.group(2)
				logger.debug('Found headline: ' + headline_match.group(1) + ' at page: ' + page)
				logger.info('Page: ' + page + ' [' + self._current_category + '] ' + headline)
				return Headline(self._current_category, headline, page)
			else:
				logger.debug('Neither partial nor headline: ' + line)
		 		

def get_headlines(pages_num):
	content = []
	for page_num in pages_num:
		page_content = remove_pre(get_page(page_num))
		content += page_content
	
	parser = ContentParser(content)
	return parser.get_headlines()
	
def get_home_headlines():
	return get_headlines([110, 111])

def get_world_headlines():
	return get_headlines([130, 131])
		 		

# create logger
logger = logging.getLogger("TT")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
	
home_headlines = get_home_headlines()
world_headlines = get_world_headlines()

for headline in home_headlines:
	print(headline)

for headline in world_headlines:
	print(headline)
#get_content(111)
#get_content(130)
#get_content(131)


import unittest

class TestIsCategory(unittest.TestCase):
	def home_categories(self):
		self.assertTrue('Z DOMOVA', get_category(' Z DOMOVA                        obsah 1'))
		self.assertTrue('Z DOMOVA', get_category(' Z DOMOVA                        obsah 2'))
		self.assertTrue('STRUČNĚ', get_category(' STRUČNĚ                                '))
		self.assertTrue('EKONOMIKA', get_category(' EKONOMIKA                              '))

	def world_categories(self):
		self.assertEqual('ZE SVĚTA', get_category(' ZE SVĚTA                        obsah 1'))
		self.assertEqual('ZE SVĚTA', get_category(' ZE SVĚTA                        obsah 2'))
		self.assertEqual('STRUČNĚ', get_category(' STRUČNĚ                                '))
		self.assertEqual('EKONOMIKA', get_category(' EKONOMIKA                              '))

	def invalid(self):
		self.assertIsNone(get_category('                                        '))
		self.assertIsNone(get_category('                        z tisku  >> 150 '))
		self.assertIsNone(get_category(' Dohoda MZV a MPO o spolupráci...... 128'))
		self.assertIsNone(get_category(' Zeman: Imunitu jen na verbální projev /'))
		self.assertIsNone(get_category('                        obsah 2  >> 111 '))


if __name__ == '__main__':
	unittest.main()
