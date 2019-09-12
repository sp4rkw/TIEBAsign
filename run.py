# -*- coding:utf-8 -*-
import requests,datetime,re,os,sys,time
from bs4 import BeautifulSoup


'''
    函数match_bar_name用来获取
    1、当前页
    2、关注贴吧名字和链接，返回列表数据，格式[{'name':'abc','link':'www.asdfaf.asdfasdf'},'name':'abc','link':'www.asdfaf.asdfasdf'}]，
'''
def match_bar_name(soup):
    list=[]
    for i in soup.find_all('a'):
        if i.has_attr('href') and not i.has_attr('class') and i.has_attr('title'):
            if i.string != 'lua':
                list.append({'name':i.string,'link':'http://tieba.baidu.com/'+i.get('href')+'&fr=home'})
    return list


'''
    函数get_bar_link用来获取
    1、所有页
    2、关注贴吧
    3、名字和链接
'''
def get_bar_link(s,header):#遍历所有页，直到最后一页
    url=r'http://tieba.baidu.com/f/like/mylike?pn=%d'
    pg=1
    tieba_list = []
    try:
        while 1:
            res=s.get(url%pg,headers=header)
            soup=BeautifulSoup(res.text,'html.parser')
            tieba_list.extend(match_bar_name(soup))
            if '下一页' in str(soup):
                pg+=1
            else:
                return tieba_list
    except:
        return 'error'

'''
    name: 贴吧名字
    link：贴吧链接
'''
def check(name,link,header,s):#获取每个关注贴吧 提交数据tbs，然后签到，并返回签到结果
    try:
        res=s.post(link)
        tbs=re.compile('\'tbs\': "(.*?)"')
        find_tbs=re.findall(tbs,res.text)
        if not find_tbs:   #　没有查找到tbs,跳过这个吧的签到
            return -2
        data={
            'ie':'utf-8',
            'kw':name,
            'tbs':find_tbs[0],
        }
        url='http://tieba.baidu.com/sign/add'
        res=s.post(url,data=data,headers=header)          ######## 签到 post
        # print(datetime.datetime.now(),'    ',name,'   ',res.json())
        return int(res.json()['no'])   #########返回提交结果
    except:
        return -1

def SignIn(data,header,s):
    try:
        res=check(data['name'], data['link'],header,s)
        if res==0:
            # print( data['name'] +'吧签到成功\n')
            return (True,data['name'] +'吧签到成功')
        elif res==1101:
            # print(  data['name'] +'吧已经签过\n')
            return (True,data['name'] +'吧已经签过')
        elif res==1102:
            # print( data['name'] + '吧，签到太快，重新签到本吧\n')
            time.sleep(10)
            return (False,data['name'] + '吧，签到太快，重新签到本吧')
        else:
            print(res)
            # print('未知返回值，重新签到'+ data['name']+'吧')
            return (False,u'未知返回值，重新签到'+ data['name']+'吧')
    except :
        # print('未知报错 重新签到'+ data['name']+'吧')
        return (False,u'未知报错 重新签到'+ data['name']+'吧')

if __name__ == "__main__":
    s=requests.session()
    cookie =''
    headers={
        'Cookie':cookie,
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    }

    for i in get_bar_link():#根据签到的返回值处理结果,利用count做最多三次异常重复签到
        flag = False
        count = 0
        while flag == False:
            flag = SignIn(i)
            time.sleep(2)   #控制签到速度
            count = count + 1
            if count >= 3:
                print(i['name']+'吧异常，无法签到，已经跳过')
                break



'''
附上 3种 签到返回json
签到太快    {'no': 1102, 'error': '您签得太快了 ，先看看贴子再来签吧:)', 'data': ''}
已经签过到  {'no': 1101, 'error': '亲，你之前已经签过了', 'data': ''}
成功签到的  {'no': 0, 'error': '', 'data': {'errno': 0, 'errmsg': 'success', 'sign_version': 2, 'is_block': 0, 'finfo': {'forum_info': {'forum_id': 548717, 'forum_name': 'katana'}, 'current_rank_info': {'sign_count': 966}}, 'uinfo': {'user_id': 774850436, 'is_sign_in': 1, 'user_sign_rank': 966, 'sign_time': 1548040220, 'cont_sign_num': 1, 'total_sign_num': 1, 'cout_total_sing_num': 1, 'hun_sign_num': 0, 'total_resign_num': 0, 'is_org_name': 0}}}

'''





