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

def is_category(line):
	# TODO: Should be only caps
	if re.match(r'^ (\w+ )+\s*(obsah \d)?$', line):
		return True
	return False

def get_headline(lines_iter):
	
	headline = ''
	
	while True:
		line = lines_iter.__next__()
		logger.debug('Processed line: ' + line)
		partial_headline_match = re.match('^ (\S.*/)\s*$', line)
		if (partial_headline_match):
			logger.debug('Found partial headline: ' + partial_headline_match.group(1))
			headline = headline + partial_headline_match.group(1) + ' '
		else:
			headline_match = re.match('^ (\S.*[^\.])\.* (\d\d\d)$', line)
			if headline_match:
				headline = headline + headline_match.group(1)
				page = headline_match.group(2)
				logger.debug('Found headline: ' + headline_match.group(1) + ' at page: ' + page)
				logger.info('Page: ' + page + ' Headline:' + headline)
				return headline, page
			else:
				logger.debug('Neither partial nor headline: ' + line)
		 		
def get_content(page_num):
	content1 = remove_pre(get_page(page_num))
	
	content_iter = content1.__iter__()
	while True:
		try:
			headline, page = get_headline(content_iter)
			print(' [HEADLINE] ', page, headline)
		except StopIteration:
			break
		except:
			pass	
		
	#	print(is_headline(line), line)

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
	
get_content(110)
get_content(111)
get_content(130)
get_content(131)


import unittest

class TestIsCategory(unittest.TestCase):
	def home_categories(self):
		self.assertTrue(is_category(' ZE SVĚTA                        obsah 1'))
		self.assertTrue(is_category(' ZE SVĚTA                        obsah 2'))
		self.assertTrue(is_category(' STRUČNĚ                                '))
		self.assertTrue(is_category(' EKONOMIKA                              '))

	def world_categories(self):
		self.assertTrue(is_category(' ZE SVĚTA                        obsah 1'))
		self.assertTrue(is_category(' ZE SVĚTA                        obsah 2'))
		self.assertTrue(is_category(' STRUČNĚ                                '))
		self.assertTrue(is_category(' EKONOMIKA                              '))

	def invalid(self):
		self.assertFalse(is_category('                                        '))
		self.assertFalse(is_category('                        z tisku  >> 150 '))
		self.assertFalse(is_category(' Dohoda MZV a MPO o spolupráci...... 128'))
		self.assertFalse(is_category(' Zeman: Imunitu jen na verbální projev /'))
		self.assertFalse(is_category('                        obsah 2  >> 111 '))


if __name__ == '__main__':
	unittest.main()
