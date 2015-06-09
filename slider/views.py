#coding=utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from slider_DB.models import *
import datetime
import time
from django.template import loader
from django.template.context import RequestContext
import math
from django.db import connection
from siteuser.users.models import *

from siteuser import settings as siteuser_settings
from slider.qrcoder import qrcode_datauri
from django.core import serializers
import json
from django.core.urlresolvers import reverse

'''导入json转换方法'''
from extensions.ajaxJson import json_encode 

if siteuser_settings.USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites
#导航到添加幻灯片视图
def newslider(request):
    now = datetime.datetime.now()
    tags = Tag.objects.all()[:12]
    myTags = '<table id="myTags" class="table">'
    i = 0
    for tag in tags:
        if i % 6 == 0:
            myTags = myTags + '<tr>'
        myTags = myTags + '<td>' + '<input type="checkbox" id="_' + tag.tag_ID + '"><label for="_' + tag.tag_ID + '">' + tag.tag_name + '</label>' + '</td>'
        if (i + 1) % 6 == 0:
            myTags = myTags + '</tr>'
        i+=1
    myTags = myTags + '</table>'
    return render_to_response('newslider.html',{'current_date':now,'myTags':myTags})

def create(request):
    return render_to_response("create_slider.html")

def getAnUniqueTitle():
    '''获取唯一列'''
    theTitle = ""

    '''随机数字作shortTitle，此方式有个缺点，当前表中的内容越来越多时会导致生成速度越来越慢'''
    #Thanks for
    #http://stackoverflow.com/questions/13496087/python-how-to-generate-a-12-digit-random-number
    #theTitle = "%0.7d" % random.randint(0,9999999)
    #theSlider = Slider.objects.get(shortTitle=theTitle)
    #if theSlider is not None:
    #    getAnUniqueTitle()

    '''产生最新的字段值产生方式是以20000000为基值，加上当前表的总记录数，包括不是数字型的shortTitle'''
    slidersCount = Slider.objects.all().count()
    theTitle = int(20000000) + int(slidersCount)
    theSliderCount = Slider.objects.filter(shortTitle = theTitle).count()
    if theSliderCount > 0:#否则用随机数形式
        theTitle = "%0.8d" % random.randint(0,99999999)

        
    theTitle = "%0.8d" % random.randint(0,99999999)

    return theTitle

#ajax 添加幻灯片
from django.utils import simplejson
import pickle 
import hashlib
import random
import re
#动态加载
def addNewSlider(request):
    sliderTitle = request.POST.getlist('sliderTitle')[0]
    sliders = u"%s" % request.POST.getlist('sliders')[0]
    sliders = sliders.replace("\\","\\\\")#替换转义字符
    t = request.POST.getlist('tags')[0]

    t = re.sub('\s+', ' ', t).replace("?","").strip()#正则表达式把多个空白字符替换成一个空格,替换左右空格
    p = re.compile('[a-zA-Z0-9_\u4e00-\u9fa5\s]+')
    #t=p.findall(t)
    '''thanks for: http://stackoverflow.com/questions/2077897/substitute-multiple-whitespace-with-single-whitespace-in-python'''
    
    '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ step 1: 保存一篇post@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
    #return HttpResponse(sliders)
    json = simplejson.loads("[" + sliders + "]", strict=False)
    tlist = list(json)#string转换成list
    newSlider = Slider(isliving="0"
                       ,author=SiteUser.objects.get(id=request.session["uid"])
                       ,shortTitle=getAnUniqueTitle()
                       ,status=Slider_Status.objects.get(status_id='defaultkey')
                       ,title=sliderTitle.strip(' \t\n\r').replace('?','').replace('&','').replace('/','_').replace('\\','_').replace('=','_').replace(':','_')#替换危险字符
                       ,creation_date=time.strftime('%Y-%m-%d %X', time.localtime()))
    newSlider.save()

    '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ step 2: 保存标签@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
    Tags = t.split(" ")
    tempTags = []
    for tag in Tags:#过滤出系统中还没有的标签
        if tag is '' or tag is None or tag is ' ':
            continue
        try:
            if Tag.objects.filter(tag_name = tag).count() <= 0:
                tempTags.append(tag)
        except:
            continue

    newTags = []
    for tag in tempTags:#添加系统中还没有的标签
        if tag is '' or tag is None:
            continue
        newTags.append(Tag(tag_ID=hashlib.sha1(str(random.random())).hexdigest()
                               ,tag_name=tag
                               ,width=50
                               ,height=50
                               ,creator=SiteUser.objects.get(id = request.session["uid"])))
    Tag.objects.bulk_create(newTags)

    for tag in t.split(" "):#在系统中筛选本post需要的标签
        if tag is '' or tag is None:
            continue
        newSlider.tags.add(Tag.objects.get(tag_name=tag))#
    newSlider.save()

    '''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ step 3: 保存详细内容@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
    theSlider = Slider.objects.get(slider_ID=newSlider.slider_ID)#获取一条
    if newSlider.slider_ID is not None:
        newSliders = []
        i = 0
        for obj in tlist:
            i+=1
            contexter = obj['_context'].replace('>&nbsp;</pre>','>')
            contexter = re.sub('<pre class=.{0,20}></pre>', '</pre>', contexter)
            newSliders.append(Slider_Content(slider_content_ID=hashlib.sha1(str(random.random())).hexdigest()
                                             ,slider_nav_id=obj['_slider_nav_id']
                                             ,sequenceNo=i
                                             ,slider=theSlider
                                             ,slider_class=obj['_slider_class']
                                             ,slider_title=obj['_slider_title']
                                             ,dataX=obj['_dataX']
                                             ,dataY=obj['_dataY']
                                             ,dataZ=obj['_dataZ']
                                             ,data_skew=obj['_data_skew']
                                             ,data_rotate_x=obj['_data_rotate_x']
                                             ,data_rotate_y=obj['_data_rotate_y']
                                             ,data_rotate=obj['_data_rotate']
                                             ,data_scale=obj['_data_scale']
                                             ,data_scale3d=obj['_data_scale3d']
                                             ,data_perspective=obj['_data_perspective']
                                             ,context=contexter
                                             ,slider_memo=obj['_slider_memo']))
        Slider_Content.objects.bulk_create(newSliders)
        return HttpResponse("succeed")
    else:
        return HttpResponse("failed")
    
from django.views.generic import list_detail
def updateslider(request,userURL=None,sliderURL=None):
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userURL)
    except:
        siteuser = SiteUser.objects.get(id__exact=userURL)
#浏览的幻灯片
    #return
    #HttpResponse(Slider.objects.filter(author=siteuser,slider_ID=sliderURL).query.__str__())
    try:
        theslider = Slider.objects.get(author=siteuser,shortTitle=sliderURL)
        if not theslider:
            theslider = Slider.objects.get(author=siteuser,slider_ID=sliderURL)
    except:
        theslider = Slider.objects.get(author=siteuser,slider_ID=sliderURL)
    
    if theslider is None:
        return Http404()

#获取内容
    sliderPage = Slider_Content.objects.filter(slider=theslider).extra({"comments_count":"select count(*) from slider_DB_comment as c where c.to_slider_content_id = slider_DB_slider_content.slider_content_ID"}).order_by('sequenceNo')

    #return HttpResponse(Slider_Content.objects.filter(slider=theslider).extra({"comments_count":"select count(*) from slider_DB_comment as c where c.to_slider_content_id = slider_DB_slider_content.slider_content_ID"}).order_by('sequenceNo').query.__str__())
    sliderJSON=Slider_Content.objects.raw('SELECT (select count(*) from slider_DB_comment as c where c.to_slider_content_id = slider_DB_slider_content.slider_content_ID) AS comments_count, slider_DB_slider_content.slider_content_ID, slider_DB_slider_content.slider_nav_id, slider_DB_slider_content.sequenceNo, slider_DB_slider_content.slider_id, slider_DB_slider_content.slider_class, slider_DB_slider_content.slider_title, slider_DB_slider_content.dataX, slider_DB_slider_content.dataY, slider_DB_slider_content.dataZ, slider_DB_slider_content.data_skew, slider_DB_slider_content.data_rotate_x, slider_DB_slider_content.data_rotate_y, slider_DB_slider_content.data_rotate, slider_DB_slider_content.data_scale, slider_DB_slider_content.data_scale3d, slider_DB_slider_content.data_perspective, slider_DB_slider_content.syntax_highlighter, slider_DB_slider_content.context, slider_DB_slider_content.slider_memo FROM slider_DB_slider_content WHERE slider_DB_slider_content.slider_id = \'%s\' ORDER BY slider_DB_slider_content.sequenceNo ASC', [theslider.slider_ID])

    #json
    listSliderJSON=list(sliderPage)
    slider_JSON=serializers.serialize('json', listSliderJSON, fields=('comments_count', 'slider_content_ID', 'slider_nav_id','sequenceNo','slider_id','slider_class','slider_title','dataX','dataY','dataZ','data_skew','data_rotate_x','data_rotate_y','data_rotate','data_scale','data_scale3d','data_perspective','syntax_highlighter','context','slider_memo'))

    ##解决在template里读不出字段名的问题
    i = 0
    for content in sliderPage:
        sliderPage[i].dataX = content.dataX
        sliderPage[i].dataY = content.dataY
        sliderPage[i].dataY = content.dataY
        sliderPage[i].data_rotate_x = content.data_rotate_x
        sliderPage[i].data_rotate_y = content.data_rotate_y
        sliderPage[i].data_rotate = content.data_rotate
        i = i + 1
#视图
    t = loader.get_template('update_slider.html')
    c = RequestContext(request,{"slider":theslider,'sliderData':sliderPage,'sliderJSON':slider_JSON})
    return HttpResponse(t.render(c))

def slider_by_title(request,userURL=None,sliderURL=None):
    '''根据幻灯片标题定位幻灯片，如：http://127.0.0.1:8000/slider/%E5%8E%A6%E9%97%A8%EF%BC%8C%E5%87%A4%E5%87%B0%E6%9C%A8%E6%AD%A3%E8%89%B3'''
#作者
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userURL)
    except:
        siteuser = SiteUser.objects.get(id__exact=userURL)
#当前用户
    if 'uid' in request.session:
        curruser = SiteUser.objects.get(id__exact=request.session['uid'])
    else:
        curruser = 0
#浏览的幻灯片
    #return
    #HttpResponse(Slider.objects.filter(author=siteuser,slider_ID=sliderURL).query.__str__())
    try:
        theslider = Slider.objects.get(author=siteuser,shortTitle=sliderURL)
        if not theslider:
            theslider = Slider.objects.get(author=siteuser,slider_ID=sliderURL)
    except:
        theslider = Slider.objects.get(author=siteuser,slider_ID=sliderURL)
    
    if theslider is None:
        return Http404()

#获取内容
    sliderPage = Slider_Content.objects.filter(slider=theslider).extra({"comments_count":"select count(*) from slider_DB_comment as c where c.to_slider_content_id = slider_DB_slider_content.slider_content_ID"}).order_by('sequenceNo')
    #return
    #HttpResponse(Slider_Content.objects.filter(slider=theslider).extra({"comments_count":"select
    #count(*) from slider_DB_comment as c where c.to_slider_content_id =
    #slider_DB_slider_content.slider_content_ID"}).order_by('sequenceNo').query.__str__())

    ##解决在template里读不出字段名的问题
    i = 0
    navbar = []
    sliderData = []
    for content in sliderPage:
        i = i + 1
        sliderPage[i - 1].dataX = content.dataX * i
        sliderPage[i - 1].dataY = content.dataY * i
        sliderPage[i - 1].dataY = content.dataY * i
        sliderPage[i - 1].data_rotate_x = content.data_rotate_x * i
        sliderPage[i - 1].data_rotate_y = content.data_rotate_y * i
        sliderPage[i - 1].data_rotate = content.data_rotate * i
#二维码
    qrcodeHTML = ""
    minor_url = ""#需要在此处定义否则在RequestContext找不到minor_url变量
    if len(sliderPage) != 0:
        url = "%s" % request.build_absolute_uri(None)#获取当前页面url
        urlpart = url.split('/')
        urlpart[-2] = sliderURL
        minor_url = ('/'.join(urlpart))
        #return HttpResponse(minor_url)
        if not theslider.qrcode:
            theslider.qrcode = qrcode_datauri(minor_url)
            theslider.save()
            
    extra={}
    if 'uid' in request.session:
        extra['isSelf'] = request.session['uid'] == siteuser.id
    else:
        extra['isSelf'] = False
        

#视图
    #return HttpResponse(theslider.qrcode);
    t = loader.get_template('slider.html')
    c = RequestContext(request,{"slider":theslider
                                ,"curruser":curruser
                                ,'sliderData':sliderPage
                                ,"extraInfo":extra
                                ,'qrcode':{"minor_url":minor_url}})
    return HttpResponse(t.render(c))

def ajax_getComments(request):
    '''ajax获取某一幻灯片页面的所有评论'''
    slider_page_id = request.POST.getlist('pageid')[0]

    comments = Comment.objects.filter(to_slider_content=slider_page_id).extra({"avatar_url":"""
                                                        case when (select avatar_url from users_siteuser u where u.id=slider_DB_comment.poster_id) is null
                                                        then (select CONCAT('%s',avatar_name) from users_siteuser u where u.id=slider_DB_comment.poster_id)
                                                        else (select avatar_url from users_siteuser u where u.id=slider_DB_comment.poster_id)
                                                        end
                                                    """ % (AVATAR_URL_PREFIX),
                                      "username":"select username from users_siteuser u where u.id=slider_DB_comment.poster_id",},).values("username","avatar_url","comment_ID","poster_id","comment_tag","comment_content"
                                              ,"comment_datetime","to_slider_content_id").order_by("-comment_datetime")
    return HttpResponse(json_encode(comments))

def sendMSG(request,message,targetUserName,msgtype):
    if 'uid' in request.session:
        sender = SiteUser.objects.get(id__exact=request.session['uid'])#我的账户
    else:
        return HttpResponse("notLogin")#没有登录
    try:
        receiveUser = SiteUser.objects.get(urlname__exact=targetUserName)
    except:
        try:
            receiveUser = SiteUser.objects.get(id__exact=targetUserName)
        except:
            #@错误
            return False
            pass
    if receiveUser and sender:
        Message = UserMessage(FromUser=sender,
                            ToUser=receiveUser,
                            MsgType=msgtype,
                            MessageText=message,
                            CreationDate=datetime.datetime.now())
        Message.save()

import re  
def fixAT(request,content,userURL,sliderURL):
    regex = u"@[a-zA-Z0-9_\u4e00-\u9fa5]+"#正则表达式
    result = re.findall(regex,content)
    result.sort(key=lambda x:len(x),reverse=True) 
    for r in {}.fromkeys(result).keys():#去重后循环
        content = content.replace(r,"@<a href='" + reverse('siteuser_account_url', kwargs={'userurlname': r[1:]}) + "'target='_blank'>" + r[1:] + "</a>")
    for r in {}.fromkeys(result).keys():#去重后循环
        sendMSG(request,(u"<a href='%s'target='_blank'>在这提到了我</a>：%s" % (sliderURL,"asdf")),r[1:],'1')#消息类型，0站内信，1@，2回复我的评论，3收到的评论
    sendMSG(request,(u"收到回复：%s" % (content)),userURL,'3')#消息类型，0站内信，1@，2回复我的评论，3收到的评论
    return content

def ajax_postComment(request):
    '''ajax评论幻灯片'''
    comment = request.POST.getlist('comment')[0]
    slider_page_id = request.POST.getlist('pageid')[0]
    userURL = request.POST.getlist('userURL')[0]
    Slider_content = Slider_Content.objects.get(slider_content_ID__exact=str(slider_page_id))
    sliderURL = reverse('slider_url',kwargs={"userURL":userURL,"sliderURL":Slider_content.slider.fixedSliderURL})#获得一个视图的url
    comment = fixAT(request,comment,userURL,sliderURL)
    try:
        newComment = Comment(poster =SiteUser.objects.get(id__exact=request.session['uid']),
                            to_slider_content=Slider_content,
                            comment_tag=0,
                            comment_content=comment,
                            recomment=0,
                            comment_datetime=time.strftime('%Y-%m-%d %X',time.localtime()))
        newComment.save()
    except:
        return HttpResponse("error")
    return HttpResponse("success")

def getIsfavoriteTag(request,tagname):
    try:
        innerUser = InnerUser.objects.get(user__id__exact = request.session['uid'])
        for intrestedTag in innerUser.intersting_tags.all():
            if (u'%s' % intrestedTag) == (u"%s" % tagname):
                return "yes"
                break
        return "no"
    except:
        return "no"
    
def slider_by_tag(request,tagname,page=1):
    '''获取某一个tag下的所有幻灯片'''
    
    if 'uid' in request.session:
        theslider = Slider.objects.filter(tags__tag_name__exact=tagname).extra(select={
                    'likes': 'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id',
                    'collections': 'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id',
                    'amILikeIt':'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id and users_siteuser_slider_like.siteuser_id=%s' % (request.session['uid']),
                    'amICollectIt':'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id and users_siteuser_slider_collection.siteuser_id=%s' % (request.session['uid']),
                },).order_by("-creation_date")[int(page) * 10 - 10:int(page) * 10]
    else:
        theslider = Slider.objects.filter(tags__tag_name__exact=tagname).extra(select={
                    'likes': 'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id',
                    'collections': 'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id',
                    'amILikeIt':'0',
                    'amICollectIt':'0',
                },).order_by("-creation_date")[int(page) * 10 - 10:int(page) * 10]
    if theslider is None:
        return Http404()
    extra = {}
    extra["tagname"] = tagname
    extra["page"] = int(page)
    extra["slideCount"] = Slider.objects.filter(tags__tag_name__exact=tagname).count()
    extra["pageCount"] = int(math.ceil(extra["slideCount"] / 10.0))#取整
    #extra["myIntrestingTag"]=InnerUser.objects.get()

    endxrange = extra["page"] / 10 * 10 + 10
    if endxrange > extra["slideCount"] / 10 + 1:
        endxrange = extra["slideCount"] / 10 + 1
    extra['loop_times'] = xrange(extra["page"] / 10 * 10 + 1,endxrange + 1)
    extra["isFavorite"] = getIsfavoriteTag(request,tagname)
    extra['favoriteCount'] = InnerUser.objects.filter(intersting_tags__tag_name__exact=tagname).count()
    
    #用户信息
    if siteuser_settings.USING_SOCIAL_LOGIN:#允许使用社交网站登录
        socialsites = SocialSites(settings.SOCIALOAUTH_SITES)
    info = {}
    if 'uid' in request.session:
        thisUser = SiteUser.objects.get(id=request.session['uid'])
        info['id'] = thisUser.id
        info['social'] = thisUser.is_social
        
        if siteuser_settings.USING_SOCIAL_LOGIN and info['social']:
            info['social'] = socialsites.get_site_object_by_name(thisUser.social_user.site_name).site_name_zh
            
        info['username'] = thisUser.username
        info['avatar'] = thisUser.avatar
        info['current'] = request.siteuser and request.siteuser.id == thisUser.id

        fanscound = UserFriends.objects.filter(target=thisUser.id).count()
        info['fansCount'] = fanscound if fanscound is None else 0

        focusCount = UserFriends.objects.filter(source=thisUser.id).count()
        info['focusCount'] = focusCount if focusCount is None else 0

    t = loader.get_template('slider_by_tag.html')
    c = RequestContext(request,{'theslider':theslider,'extra':extra,'users':info})
    return HttpResponse(t.render(c))

def favoriteTag(request):
    tagname = request.POST.getlist('tagname')[0]
    try:
        innerUser = InnerUser.objects.get(user__id__exact = request.session['uid'])
        innerUser.intersting_tags.add(Tag.objects.get(tag_name=tagname))
        innerUser.save()
    except:
        return HttpResponse("errorFavorite")
    
    for intrestedTag in innerUser.intersting_tags.all():
        if (u'%s' % intrestedTag) == (u"%s" % tagname):
            return HttpResponse("successFavorite")
            break
    return HttpResponse("failedFavorite")

def unfavoriteTag(request):
    tagname = request.POST.getlist('tagname')[0]
    try:
        innerUser = InnerUser.objects.get(user__id__exact = request.session['uid'])
        innerUser.intersting_tags.remove(Tag.objects.get(tag_name=tagname))
        innerUser.save()
    except:
        return HttpResponse("errorUnfavorite")
    
    for intrestedTag in innerUser.intersting_tags.all():
        if (u'%s' % intrestedTag) == (u"%s" % tagname):
            return HttpResponse("failedUnfavorite")
            break
    return HttpResponse("successUnfavorite")

def usersFavoriteTag(request,tagname,page=1):
    '''关注某一标签的所有用户'''
    t = loader.get_template('users_by_tag.html')
    c = RequestContext(request,{'theslider':'theslider','extra':'extra'})
    return HttpResponse(t.render(c))

def likeAslider(request):
    '''ajax喜欢某一幻灯片'''
    sliderid = request.POST.getlist('sliderid')[0]
    try:
        siteUser = SiteUser.objects.get(id__exact = request.session['uid'])
        siteUser.slider_like.add(Slider.objects.get(slider_ID__exact=sliderid))
        siteUser.save()
    except:
        return HttpResponse("error")
    for like in siteUser.slider_like.all():
        if (u'%s' % like.slider_ID) == (u"%s" % sliderid):
            return HttpResponse("success")
            break
    return HttpResponse("failed")
def unlikeAslider(request):
    '''ajax取消喜欢某一幻灯片'''
    sliderid = request.POST.getlist('sliderid')[0]
    try:
        siteUser = SiteUser.objects.get(id__exact = request.session['uid'])
        siteUser.slider_like.remove(Slider.objects.get(slider_ID__exact=sliderid))
        siteUser.save()
    except:
        return HttpResponse("error")
    for like in siteUser.slider_like.all():
        if (u'%s' % like.slider_ID) == (u"%s" % sliderid):
            return HttpResponse("failed")
            break
    return HttpResponse("success")

def collectAslider(request):
    '''ajax收藏某一幻灯片'''
    sliderid = request.POST.getlist('sliderid')[0]
    try:
        siteUser = SiteUser.objects.get(id__exact = request.session['uid'])
        siteUser.slider_collection.add(Slider.objects.get(slider_ID__exact=sliderid))
        siteUser.save()
    except:
        return HttpResponse("error")
    for like in siteUser.slider_collection.all():
        if (u'%s' % like.slider_ID) == (u"%s" % sliderid):
            return HttpResponse("success")
            break
    return HttpResponse("failed")
def uncollectAslider(request):
    '''ajax收藏喜欢某一幻灯片'''
    sliderid = request.POST.getlist('sliderid')[0]
    try:
        siteUser = SiteUser.objects.get(id__exact = request.session['uid'])
        siteUser.slider_collection.remove(Slider.objects.get(slider_ID__exact=sliderid))
        siteUser.save()
    except:
        return HttpResponse("error")
    for like in siteUser.slider_collection.all():
        if (u'%s' % like.slider_ID) == (u"%s" % sliderid):
            return HttpResponse("failed")
            break
    return HttpResponse("success")