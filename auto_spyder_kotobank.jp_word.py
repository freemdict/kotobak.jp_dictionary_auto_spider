# -*- coding: UTF-8 -*-
# This little programme intends to collect dictionary data 
#     on https://kotobank.jp/dictionary/ automatically
# =========================
# =      FreeMdict        =
# =       By Hua          =
# =     Visit us at       =
# = https://freemdict.com =
# =        Github         =
# = https://github.com/freemdict/kotobak.jp_dictionary_auto_spider =
# ==================================================================

# reference
# https://blog.csdn.net/qianghaohao/article/details/52117082
# https://bearfly1990.github.io/2018/09/12/PyProgressBar/
# https://www.jianshu.com/p/a5d96457c4a4 Full to half

# start of import modules

import shutil
import threading
import codecs # coding format
import time
import os # operate files and paths
import requests # similar function with your browser
import psutil # get how many logical cores your computer has to help allocate threads
import urllib.parse
import sys

from bs4 import BeautifulSoup # a advanced tool to deal with HTML files
from requests.adapters import HTTPAdapter
from colorama import  init, Fore, Back, Style # change text style in the Python Terminal
init(autoreset=True)
from math import floor
#import multiprocessing
#from multiprocessing import Process

# end of import modules
#===============================================
# start of FUNCTIONS

# ---------------some parameters of colorama module------------------
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL
#
class Colored(object):
    #  example : fontColor:WHITE  backgroundColor:GREEN
    def white_green(self, s):
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET
    def blue_(self,s):
        return Fore.BLUE + s + Fore.RESET
    def yellow_(self,s):
        return Fore.YELLOW + s + Fore.RESET
color = Colored()
# print(color.white_green('I am green'))
#-----------------------------------------------------------------
exit_checker = False

# def find_proxies():


def strQ2B(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # Full 'Space' ' '  conversion
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # Full string conversion
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    output = ''
    for i in ss:
        output = output + i
    return output

# progress_bar
def view_bar(num,total):
    rate = num / total
    rate_num = int(rate * 100)
    #r = '\r %d%%' %(rate_num)
    r = '\r%s>%d%%' % ('=' * rate_num, rate_num,)
    sys.stdout.write(r)
    sys.stdout.flush

def get_dictionary_list(): # get dictionaries available on 
    url = "https://kotobank.jp/dictionary/"
    thread = requests.Session()
    thread.mount('https://', HTTPAdapter(max_retries=4))
    data = thread.get(url).text
    data = BeautifulSoup(data, 'html.parser').find_all('div',{'class':'dictionary'})
    data = BeautifulSoup(str(data),'html.parser').find_all('h3')
    if(not os.path.exists('dictionary')):
        os.mkdir('dictionary')
    with open('dictionary/DictionaryList.txt','w+',encoding="utf8") as f:
        for i in data:
            i = str(i)
            f.writelines('https://kotobank.jp' + i[i.find('href=')+6:i.find('">')] + '\n')
            f.writelines(i[i.find('">')+2:i.find('</h3>')].replace('</a>','')+'\n')
    return 'Finish Finding Dictionaries, The data is stored in dictionary/DictionaryList.txt'

def select_dictionary(): # give a interface for user to choose dictionary
    with open('dictionary/DictionaryList.txt','r',encoding="utf8") as f:
        f = f.readlines()
        count = 0
        while count <= len(f):
            if count%2 == 1:
                print(str(int((count+1)/2)) + ' ' + f[count])
            count += 1
        select_dictionary_checker = True
        while(select_dictionary_checker):
            selected_dictionary = input('Which dictionary data do you want collect?\n \
(Input number only)\nYour choice: ')
            if(not selected_dictionary.isdigit()):
                print('What you input is not a number,please check and try again.')
            elif int(selected_dictionary) > int((count+1)/2) or int(selected_dictionary) <= 0:
                print('The number input is invalid, please try again.')
            else:
                print('Successfully, the dictionary you choose is ' + str(selected_dictionary) \
                    + ' ' + f[2*int(selected_dictionary)-1])
                selected_dictionary_confirm_checker = input('Confirm your choice, please choose option.\n(Input yes or no)\n \
    1) Yes \n \
    2) No \n(Input 1 or 2) Your choice is: ')
                if selected_dictionary_confirm_checker == '1':
                    select_dictionary_checker = False
        
        return f[2*int(selected_dictionary)-2].replace('\n',''), \
            f[2*int(selected_dictionary)-1].replace('\n','')
def generate_url(dictionary_url,name):
    os.chdir('dictionary')
    if(not os.path.exists(name)):
        os.mkdir(name)
    os.chdir('..')
    thread = requests.Session()
    thread.mount('https://', HTTPAdapter(max_retries=4))
    name_url_encode = urllib.parse.quote(name[0:name.find('｜')]).replace('%','.')
    name_url_encode = name_url_encode[1:len(name_url_encode)]
    # calculate how many pages in this dictionary index
    # here needs some improvement
    mid = 2000
    left = 0
    right = 4000
    while right-left > 4:
        if BeautifulSoup(thread.get(dictionary_url+str(mid)+'/', \
            timeout=4).text,'html.parser').find_all('ul',{'class':'grid02 cf'}) == []:
            right = mid
            if left == 0:
                mid = floor(mid/2)
            else:
                mid = floor((mid+left)/2)
        elif BeautifulSoup(thread.get(dictionary_url+str(mid)+'/', \
            timeout=4).text,'html.parser').find_all('ul',{'class':'grid02 cf'}) != []:
            left = mid
            if right == 0:
                mid = mid*2
            else:
                mid = floor((mid+right)/2)
    with open('dictionary/' + name+'/urls.txt','w+',encoding="utf8") as f:
        with open('dictionary/' + name+'/exist_entry.txt','w+',encoding="utf8") as f1:
            os.chdir('dictionary/' + name)
            print("Collecting dictionary entry's url, please hold on a while.")
            count = 1
            while count < right:
                page_url = dictionary_url + str(count) + '/'
                data = BeautifulSoup(thread.get(page_url,timeout=4).text,'html.parser')
                data = str(data.find_all('ul',{'class':'grid02 cf'}))
                data = BeautifulSoup(data,'html.parser').find_all('li')
                for i in data:
                    i = str(i)
                    i = i[13:i.find('" ')].replace(name_url_encode,'').replace('#','')
                    f.writelines('https://kotobank.jp' + i + '\n')
                    '''
                    if '-' in i:
                        f1.writelines(i[i[1:].find('/')+2:i.find('-')]+'\n')
                    elif '-' not in i:
                    ''' 
                    f1.writelines(i[i[1:].find('/')+2:]+'\n')
                count += 1
                view_bar(count,right)
            print("\nFinish collecting dictionary entry's url. Now proceed to collect entry's data")
    return dictionary_url,name

def get_entry_data(url_list,process_count,entry_id_1,entry_id_2):
    length = len(url_list)
    # find the position of the fourth '/' in the url
    count = 0
    checker = 0
    for i in url_list[0]:
        if i == '/':
            checker += 1
            if checker == 4:
                start = count
        count += 1
    count = 0
    start += 1
    if(not os.path.exists('parts')):
        os.mkdir('parts')
    with open('parts/dictionaryDataPart_' + str(process_count) + '.txt','w+',encoding="utf8") as f:
        while count < length:
            browser = requests.Session()
            browser.mount('https://', HTTPAdapter(max_retries=4))
            url = url_list[count].replace('\n','')
            raw_data = browser.get(url,timeout=4).text # proxy can be added here
            raw_data = BeautifulSoup(raw_data,'html.parser')
            entry_id_1 = str(entry_id_1)
            entry_id_2 = str(entry_id_2)
            data = raw_data.find_all('article',{'id':entry_id_2})
            data = data + raw_data.find_all('article',{'id':entry_id_1})
            entry_name = urllib.parse.unquote(url[start:url.find('-')])
            entry_name = entry_name.replace('‐','')
            entry_name_list = []
            article_entry_names = BeautifulSoup(str(data),'html.parser').find_all('h3')
            for new_entry in article_entry_names:
                new_entry = str(new_entry)
                new_entry = new_entry.replace('<h3>','').replace('</h3>','')
                new_entry = strQ2B(new_entry)
                if entry_name != new_entry:
                    entry_name_list.append(new_entry)

            for item in data:
                item = str(item).replace('\n','')
                item = item.replace(item[item.find('<p class="source">出典'):item.find('<!-- /.source -->')+17],'')
                item = item.replace(item[item.find('<h2>'):item.find('</h2>')+5],'')
                item = item.replace('id="' + entry_id_2 + '"','').replace('"ex cf"','"excf"')
                item = item.replace('<div class="pc-iframe-ad"></div>','').replace('<!-- /.ex 解説 -->','')
                #item = item.replace('/image/dictionary/'+entry_id_1+'/','file://')
                item = item.replace('href="/word/','href="entry://').replace('   ','')
                # check whether or not jumper are in the current dictionary 
                '''
                while(True):
                    if 'entry://' not in item[start1:]:
                        break
                    else:
                        start1 = item[start1:].find('entry://') + 8
                        if item[start1:item[start1:].find('">')] not in exist_entries:
                            item = item.replace(item[start1:][start1-14:item[start1:].find('">')],'')
                        else:
                            if '-' in item:
                                item = item.replace(item[start1:][:item[start1:].find('">')],item[start1:][:item[start1:].find('-')])
                '''
                for entry in entry_name_list:
                    f.writelines(entry + '\n@@@LINK=' + entry_name + '\n</>\n')
                f.writelines(entry_name + '\n' + item + '\n</>\n')
            count += 1
            view_bar(count,length)

def assign_get_entry_data(dictionary_url,name):
    dictionary_url = str(dictionary_url)
    name = str(name)
    os.chdir('..')
    entry_id_1 = dictionary_url[dictionary_url.find('dictionary/')+11:-1]
    entry_id_2 = urllib.parse.quote(name[0:name.find('｜')]).replace('%','.')
    entry_id_2 = entry_id_2[1:len(entry_id_2)]
    with open(name+'/urls.txt','r',encoding="utf8") as f:
        f = f.readlines()
        length = len(f)
        segment = floor(int(length)/int(thread_accepted))
        os.chdir(name)
        start = 0
        count = 1
        assign_list =[]
        while start < length:
            if start+segment > length:
                assign_list.append(f[start:length])
            else:
                assign_list.append(f[start:start+segment])
            start = start + segment
            count += 1
    return assign_list,entry_id_1,entry_id_2

def conbine_all_parts():
    with open('conbination_of_data.txt','w+',encoding="utf8") as write:
        os.chdir('parts')
        count = 0
        total = len([name for name in os.listdir('.') if os.path.isfile(os.path.join('.', name))])
        print('\nCombining entry data parts.')
        for i in os.listdir():
            with open(i,'r',encoding='utf8') as read:
                for line in read.readlines():
                    write.writelines(line)
            view_bar(count,total)
        os.chdir('..')
    return '\nFinish combining the parts'
def generate_img_url_and_download():
    with open('img_url_tmp.txt','w+',encoding="utf8") as write:
        print('\nGenerating image urls if possible. Some dictionary does not come with any images.')
        count = 0
        with open('conbination_of_data.txt','r',encoding="utf8") as read:
            read_tmp = read.readlines()
            total = len(read_tmp)
            for line in read_tmp:
                start = 0
                while len(line) > 10:
                    line = line[start:]
                    if '/image/dictionary' in line:
                        begin = line.find('/image/dictionary')
                        if '.gif' in line:
                            end = line.find('.gif') + 4
                        elif '.bmp' in line:
                            end = line.find('.bmp') + 4
                        tmp = 'https://kotobank.jp' + line[begin:end] + '\n'
                        write.writelines(tmp)
                        start = end
                    else:
                        break
                view_bar(count,total)
                count += 1
    img_url_list = []
    print('\nEliminating duplicated image urls.')
    with open('img_url_tmp.txt','r',encoding="utf8") as read:
        for line in read.readlines():
            if line not in img_url_list:
                img_url_list.append(line)
    with open('img_url.txt','w+',encoding="utf8") as write:
        for i in img_url_list:
            write.writelines(i)
    print('\nDownloading images.')
    # download
    with open('img_url.txt','r',encoding="utf8") as read:
        read_tmp = read.readlines()
        if(not os.path.exists('data')):
            os.mkdir('data')
        os.chdir('data')
        if(not os.path.exists('img')):
            os.mkdir('img')
        os.chdir('img')
        count = 0
        total = len(read_tmp)
        for url in read_tmp:
            url = url.replace('\n','')
            file_name = url.replace('https://kotobank.jp/image/dictionary/','').replace(entry_id_1_global+'/','')
            r = requests.get(url)
            with open(str(file_name),'wb') as f:
                f.write(r.content)
            view_bar(count,total)
            count += 1
        os.chdir('..')
        os.chdir('..')

def last_modify_data():
    print('\nStarting last modify of data such as Add Entry for Hiragana(平仮名，ひらがな) and Katakana(片仮名，かたかな)  \
and eliminating jumpers which do not exist in this dictionary. \
\nThis is the last step of the progrmme by the way.')
    with open("conbination_of_data.txt",'r',encoding="utf8") as data:
        with open("final_data.txt",'w+',encoding="utf8") as write:

        # not sure the entries adding here will be duplicates with previous entries
            """
            print('\nAdding entries.')
            count = 0
            total = len(data.readlines())
            for line in data.readlines():
                if count%3 == 0:
                    if '【' in line:
                        jumper = line[line.find('【')+1:line.find('】')]
                        jumper = jumper + '\n' + '@@@LINK=' + line + '\n</>\n'
                        write.writelines(jumper)
                count += 1
                view_bar(count,total)

            # several lines to kick out HTML tags in a string
            html = '<h3>しちょう <span style="font-size:12px">シテウ</span>【斯調】</h3>'
            test = re.sub(r'<[^>]+>',"",html,re.S)
            print(test)
            print(test[0])
            
            """
            with open('exist_entry.txt','r',encoding="utf8") as exist:
                print('\nEliminating non-exist entries.')
                exist_read = exist.read()
                count = 0
                total = len(data.readlines())
                with open("conbination_of_data.txt",'r',encoding="utf8") as data:
                    for line in data.readlines():
                        line = line.replace('/image/dictionary/' + entry_id_1_global + '/','file://img/')
                        line = line.replace('<article','<link rel="stylesheet" type="text/css" href="' + entry_id_1_global + '.css"><article')
                        if (count-1)%3 == 0:
                            href_list = BeautifulSoup(line,'html.parser').find_all('a')
                            if href_list == []:
                                pass
                            else:
                                for i in href_list:
                                    i = str(i)
                                    i_1 = i[:i.find('">')]
                                    i_1 = i_1.replace('<a href="entry://','')
                                    if i_1 in exist_read:
                                        line = line.replace(i_1,i_1[:i_1.find('-')])
                                    else:
                                        line = line.replace(i[3:i.find('">')],'')
                        write.writelines(line)
                        count += 1
                        view_bar(count,total)
    with open(entry_id_1_global+'.css','w+',encoding="utf8") as csss:
        print('')
def del_useless_files():
    print('\nDeleting useless files.')
    os.remove('conbination_of_data.txt')
    os.remove('exist_entry.txt')
    os.remove('img_url.txt')
    os.remove('img_url_tmp.txt')
    os.remove('urls.txt')
    shutil.rmtree('parts')
# end of FUNCTIONS

# start of Main
start_number_checker = True
start_checker = False
while(start_number_checker):
    print('Do you want to start finding all the dictionaries on the website?\n' +  \
    color.blue_('1) Yes, start sniffing the dictionaries.') + '\n' + \
    color.blue_('2) No, just quit without touching anything.') + '\n')
    start_selection_number = input('(input 1 or 2) Your choice:')
    if start_selection_number == '1':
        start_number_checker = False
        start_checker = True
    elif start_selection_number == '2':
        start_number_checker = False
    else:
        print('\nInvalid input, possibly you have input something non-numerical,\nPlease try again.\n')
if(start_checker):
    max_threads = psutil.cpu_count()
    thread_accepted_checker = True
    while(thread_accepted_checker):
        thread_accepted = input("Please input how many threads you want the programme to run concurrently.\n \
Basically, the more threads, the faster the programme can run, but there is a limit on your computer to run too many threads,\n \
and for your computer, this recommend limit is " + str(max_threads) + 'You can exceed it. Please kindly input a number which is similar to this limit.\n \
or you can just try to increase your number and watch your computer load.\n \
Example: 16 Your choice is: ')
        if(thread_accepted.isdigit()) and int(thread_accepted) <= 4*max_threads:
            thread_accepted_checker = False
        else:
            print('Invalid input, please input a number and try again')
    print('\n' + color.yellow_('[1/7] Getting dictionary list.'))
    print(get_dictionary_list())
    print('\n' + color.yellow_('[2/7] Select dictionary.'))
    dictionary_url_and_name = select_dictionary()
    print('\n' + color.yellow_("[3/7] Generating entries' url"))
    temp = generate_url(dictionary_url_and_name[0],dictionary_url_and_name[1])
    with open('exist_entry.txt','r',encoding="utf8") as exist_entries:
        exist_entries = exist_entries.read()
    temp1 = assign_get_entry_data(temp[0],temp[1])
    print('\n' + color.yellow_('[4/7] Assigning download threads.'))
    entry_id_1_global = temp1[1]
    count_proc = 1
    thread_pool = []
    print('Collecting entry data, this maybe takes a long while.')
    for task in temp1[0]:
        thread_pool.append(threading.Thread(target=get_entry_data,args=(task,count_proc,temp1[1],temp1[2],)))
        count_proc += 1
        if count_proc == len(temp1[0])+1:
            for threads in thread_pool:
                threads.start()
            for threads in thread_pool:
                threads.join()
    print('\n' + color.yellow_('[5/7] Combining data parts'))
    conbine_all_parts()
    print('\n' + color.yellow_('[6/7] Generating image urls and download images.'))
    generate_img_url_and_download()
    print('\n' + color.yellow_('[7/7] Nearly finish, doing last modifying on the data'))
    last_modify_data()

    print('\nDo you want to delete useless files?\n \
    1) Yes\n \
    2) No')
    del_or_not = input('(Input 1 or 2) Your choice is: ')
    if del_or_not == '1':
        del_useless_files()
    exit_checker = True

# ending of programme
if exit_checker == True:
    if start_selection_number == '1':
        print('\nThank you for using this programme and if you have any issues, kindly cantact us on https://freemdict.com')
    if start_selection_number == '2':
        print('The programme is now exiting.\nThank you and hope to see you again!')

# end of Main
