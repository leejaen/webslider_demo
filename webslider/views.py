#coding=utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse
from slider_DB.models import *
from django.db.models import Count

import datetime
from django.utils import timezone
from django.template.context import RequestContext
from django.template import loader

from siteuser.users.models import SiteUser, UserFriends,InnerUser,SocialUser
from siteuser import settings as siteuser_settings
from webslider import settings
from siteuser.users.views import getUserIdFromInnerUser, getTargetIdFromFriends
if siteuser_settings.USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites

def defalut(request):

    '''tagCloud'''
    #统计表潜在每一篇文档中出现的次数
    tags_with_slider = Tag.objects.all().annotate(counter=Count('Slider_Tags'))
    tagCloud = tags_with_slider.values('tag_name', 'counter').order_by('-counter')[:50]#group by

    #头条
    sliderHeadlines = Slider.objects.filter(headline_date__isnull=False).order_by('-creation_date')[:10]
    #头条
    recommends = Slider.objects.filter(recommended_date__isnull=False).order_by('-creation_date')[:20]

    #轮播
    now = timezone.now()
    galleries=Slider_Gallery.objects.filter(gallery_date__gt=now).order_by('-gallery_date')[:5]
    #galleries = Slider_Gallery.objects.all().order_by('-gallery_date')[:5]

    #用户信息
    if siteuser_settings.USING_SOCIAL_LOGIN:#允许使用社交网站登录
        socialsites = SocialSites(settings.SOCIALOAUTH_SITES)
    
    #新注册用户
    newUsers=SiteUser.objects.all().order_by('-date_joined')[:10]
    
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

        if not thisUser.is_social:
            user = InnerUser.objects.get(user_id=thisUser.id)
            fanscound = UserFriends.objects.filter(target = user).count()
            info['fansCount'] = fanscound if fanscound is not None else 0

            focusCount = UserFriends.objects.filter(source = user).count()
            info['focusCount'] = focusCount if focusCount is not None else 0
    
        #关注的人的slider
        if thisUser.is_social:
            focuspeoples_sliders = Slider.objects.filter(author__in=SiteUser.objects.filter(id__in=
                                    map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                            map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
                                                SocialUser.objects.get(user_id=thisUser.id))))))))).order_by('-creation_date')[:10]
        else:
            focuspeoples_sliders = Slider.objects.filter(author__in=SiteUser.objects.filter(id__in=
                                    map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                            map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
                                                InnerUser.objects.get(user_id=thisUser.id))))))))).order_by('-creation_date')[:10]
        #return HttpResponse(Slider.objects.filter(author__in=SiteUser.objects.filter(id__in=
        #                            map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
        #                                    map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
        #                                        InnerUser.objects.get(user_id=thisUser.id)))))))))
        #                    .query.__str__())
        if not thisUser.is_social:
            mytags_sliders = Slider.objects.filter(tags__in=InnerUser.objects.get(user__id__exact=thisUser.id).intersting_tags.all()).distinct().order_by('-creation_date')[:10]
        else:
            mytags_sliders={}
    else:
        focuspeoples_sliders = None
        mytags_sliders={}

    #from siteuser.context_processors import social_sites
    #return render_to_response('default.html',
    #        {'tagCloud':tagCloud,"headlines":headlines,'galleries':recommendHTML},
    #        context_instance=RequestContext(request,
    #        processors=[social_sites]))
    '''导入公共配置social_sites，上面方法在django1.4需要手动引入social_sites，HttpResponse不需要'''
    t = loader.get_template('default.html')
    c = RequestContext(request,{'tagCloud':tagCloud,"headlines":sliderHeadlines,"recommends":recommends,'galleries':galleries,'focus_sliders':focuspeoples_sliders,'mytags_sliders':mytags_sliders,'user':request.siteuser,'userInfo': info,'newUsers':newUsers})
    return HttpResponse(t.render(c))