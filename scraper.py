#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import requests as re
from bs4 import BeautifulSoup as bs
import pandas as pd


def get_html(url) :
    response = re.get(url)
    html = bs(response.text, "html.parser")
    return html



#THIS FUNCTION THASN'T HANDLE SITES WITH MENU ICONE
def get_topic_list(url) :
    html = get_html(url)
    if html :
        if data["nav_ul_id"]!="" :        
            topics = html.find('ul', id=data['nav_ul_id'])
            
            return topics.find_all('li')
        
        elif data["nav_ul_class"]!="" : 
            topics = html.find('ul', class_=data['nav_ul_class'])
            if topics :
                #print(data['nav_ul_class'])
                #print(topics)
                return topics.find_all('li')
        
        else :
            topics = html.find('ul')
            return topics.find_all('li')
        
    return []



#GET ALL CATEGORIES OF THE NAV BAR AND URL
def get_categorie_url(url) :
    lis = get_topic_list(url)
    dict = {}
    for li in lis :
        if li.find('a').get('href')!=url and li.find('a').get('href')!="/" and li.find('a').get('href')!=url[:-1] : 
            str = li.find('a').get('href')
                    
            if str[-1:]=="/" :
                str1 = str[:-1]
            else :
                str1 = str
                
            if data["Pagination"]=="/index.{}.html" :
                str2 = str1[:-13]
            else :
                str2 = str1
                    
            if data["Pagination"][:1]=="/" and str2[-5:]==".html" :
                str3 = str2[:-5]
            else :
                str3 = str2
            
            if data["home_url"][5:] in str3 :
                dict[li.find('a').text] = str3
            else :
                if str3[:1]!='/':
                    dict[li.find('a').text] = url + str3
                else :
                    dict[li.find('a').text] = url[:-1] +str3          
                
    return dict



#GET LINKS OF ALL ARTICLES OF A PAGE 
def get_page_articles(url) :
    html = get_html(url)
    if html :
        if data["div_page_id"]!="" :        
            topics = html.find('div', id=data['div_page_id'])
        elif data["div_page_class"]!="" : 
            topics = html.find('div', class_=data['div_page_class'])
        links = []
        if topics :
            if data['div_item_class']!='':
                articles = topics.find_all('div', class_=data['div_item_class'])
            
            else :
                articles = topics.find_all('li')
                #print(articles)
                
            for topic in articles :
                if topic.find('a'):
                    link = topic.find('a').get('href')
                    home = data["home_url"]
                    if home in link :
                        links.append(link)
                    elif link[:1]!='/':
                        str = home + link
                        links.append(str)
                    else :
                        str = home[:-1] + link
                        links.append(str)
        return links




#GET CONTENT, DATE AND VOTES OF ALL COMMENTS OF AN ARTICLE
def get_article_comments(url, categorie) :
    html = get_html(url)
    if html :
        liste = html.find_all('div', class_=data['comment_class'])
        if liste:
            comments = {'article' : [], 'categorie' : [], 'date' : [], 'text' : [], 'vote' : []}
            article_title = html.find('h1', class_=data['article_title_class']).get_text()

            for comment in liste:
                if data["comment_text_tag"]!="" and comment.find(data["comment_text_tag"], class_=data['comment_text_class']) :
                    text = comment.find(data["comment_text_tag"], class_=data['comment_text_class']).get_text()

                elif comment.find('div', class_=data['comment_text_class']):
                    text = comment.find('div', class_=data['comment_text_class']).get_text()
                else :
                    continue
                text = text.replace('،', ' ')
                text = text.replace(',', ' ')
                if data['comment_vote_class']!="" :
                    vote = comment.find('div', class_=data['comment_vote_class']).get_text()
                    comments['vote'].append(vote.replace('\n', ''))
                comments['article'].append(article_title)
                comments['date'].append(comment.find(data['comment_date_tag']).get_text())
                comments['text'].append(text.replace('\n', ' '))
                comments['categorie'].append(categorie.replace('\n', ''))
 
        return comments



#GET CONFIGURATION OF config.json FILE
with open('config.json') as file :
     data = json.load(file)
     print(data)
     print (data['nav_ul_id'])



url = data["home_url"]
print(url)
html = get_html(url)
for topic in get_topic_list(url) :
    print(topic)
    print("----------------------------------------------------------------------")





file = data['file_name'] + '.csv'
if data['comment_vote_class']=="" :
    attr = ['article', 'categorie', 'date', 'text']
else:
    attr = ['article', 'categorie', 'date', 'text', 'vote']


categories = get_categorie_url(url)
print(categories)




#CRAWL ALL URL OF ARTICLES, GET COMMENTS DETAILS AND LOAD THEM IN THE CSV FILE
for key in categories :
    cat = categories[key]

    i=0
    while(i<200) :

        str = cat + data['Pagination'].format(i)
        print(str)
        lis =[]
        lis = get_page_articles(str)
        str1 = "-----------------------------{}-----------------------------"
        print(str1.format(len(lis)))
        print(lis)
        
        for li in lis :
            html = get_html(li)
            if html :
                comments = get_article_comments(li, key)
                content = pd.DataFrame(comments, columns=attr)
                print(content)
                content.to_csv(file, mode='a', index=False, header=False)
            
        i=i+1