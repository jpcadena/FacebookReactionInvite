import sys
import argparse
from selenium import webdriver
import pandas as pd
import logging as log
from lxml import html

parser = argparse.ArgumentParser()
parser.add_argument('username', help='This is the username')
parser.add_argument('password', help='This is the password')
parser.add_argument('link', default='https://www.facebook.com', help='URL from FB post')
args = parser.parse_args()
setup_parameters = sys.argv[1:]
log.basicConfig(level=log.INFO, format='%(asctime)-15s %(message)s')


class Testsite(object):
    def __init__(self):
        self.username = setup_parameters[0]
        self.password = setup_parameters[1]
        self.link = setup_parameters[2]
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(15)
        self.site_login()
        self.browser.implicitly_wait(30)
        self.reactions()

    # Metodo para iniciar sesion
    def site_login(self):
        self.browser.get(self.link)
        self.browser.find_element_by_id("email").send_keys(self.username)
        self.browser.find_element_by_id("pass").send_keys(self.password)
        self.browser.find_element_by_id("loginbutton").click()
        self.browser.maximize_window()
        self.browser.implicitly_wait(10)

    def reactions(self):
        outpath = r'C:\Users\juanp\PycharmProjects\NODEL3\output'
        log.info(outpath)
        df_result = pd.DataFrame(columns=['post_url', 'user', 'reaction', 'user_url'])
        page_count = 0
        next_link = str(self.link)
        self.browser.get(next_link)
        log.info('%s | Crawling : %s ' % (outpath, next_link))
        tree = html.fromstring(self.browser.page_source)

        # Existe reaccion?
        next_link_list = tree.xpath("//a[contains(@href,'reaction/profile')]//img")
        next_link_list_check = tree.xpath('//a[contains(@href,"reaction/profile")][1]/div/div')
        if len(next_link_list) == 0 or len(next_link_list_check) == 0:
            log.info("Like Count = 0 QAQ")
            log.info(next_link)
        self.browser.find_element_by_xpath("//a[contains(@href,'reaction/profile')]").click()

        while True:
            tree = html.fromstring(self.browser.page_source)
            table_xpath = "//table//li/table/tbody/tr/td[@class]/table/tbody/tr"
            user = tree.xpath(table_xpath + "/td[3]//a/text()")
            user_url = tree.xpath(table_xpath + "/td[3]//a/@href")
            reaction = tree.xpath(table_xpath + "/td[2]//img/@alt")
            data = {'post_url': [next_link] * len(user), 'user': user, 'reaction': reaction, 'user_url': user_url}
            df_result = df_result.append(pd.DataFrame(columns=df_result.columns, data=data))

            # revisar si existen mas reacciones
            next_link = tree.xpath('//span[contains(text() ,"See More")]/parent::a/@href')
            if len(next_link) != 0:
                self.browser.find_element_by_xpath('//span[contains(text() ,"See More")]/parent::a').click()
                if page_count % 5 == 0:
                    log.info('crawled %d page' % page_count)
                page_count = page_count + 1
        df_result.to_csv(outpath, index=False)


if __name__ == '__main__':
    Testsite().site_login()
