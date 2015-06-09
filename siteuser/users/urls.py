# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from siteuser.users import views
from siteuser.settings import USING_SOCIAL_LOGIN

urlpatterns = patterns('',
    url(r'^user/$', views.SiteUserAccountIndexView, name='siteuser_account'),
    url(r'^user/(?P<userurlname>[-\w]+)/$', views.SiteUserAccountIndexView, name='siteuser_account_url'),#xxx的所有动态
    url(r'^(?P<userurlname>[-\w]+)/userSlider/$', views.SiteUserSliderView, name='siteuser_account_slider'),#主题
    url(r'^(?P<userurlname>[-\w]+)/userSlider/(?P<page>[-\w]+)/$', views.SiteUserSliderView, name='siteuser_account_slider_page'),
    url(r'^(?P<userurlname>[-\w]+)/tag/$', views.SiteUserTagView, name='siteuser_account_tag'),#关注的标签
    url(r'^(?P<userurlname>[-\w]+)/tag/(?P<page>[-\w]+)/$', views.SiteUserTagView, name='siteuser_account_tag_page'),
    url(r'^changeSignature/$', views.SiteUserSignatureView, name='changeSignature'),#修改个性签名（ajax）
    url(r'^my/like/$', views.MyLikeSlidersView, name='likes_liders'),#我的喜欢
    url(r'^my/like/(?P<page>\d+)/$', views.MyLikeSlidersView, name='likes_liders_with_page'),#我的喜欢
    url(r'^my/favo/$', views.MyFavoSlidersView, name='collect_liders'),#我的收藏
    url(r'^my/favo/(?P<page>\d+)/$', views.MyFavoSlidersView, name='collect_liders_with_page'),#我的收藏

    url(r'^account/message/$', views.SiteUserMessageView, name='siteuser_private_message'),#消息
    url(r'^account/message/(?P<page>[-\w]+)/$', views.SiteUserMessageView, name='siteuser_private_message_with_page'),
    url(r'^account/atme/$', views.SiteUserMessageView_atme, name='siteuser_private_atme'),
    url(r'^account/atme/(?P<page>[-\w]+)/$', views.SiteUserMessageView_atme, name='siteuser_private_atme_with_page'),
    url(r'^account/replyme/$', views.SiteUserMessageView_replyme, name='siteuser_private_replyme'),
    url(r'^account/replyme/(?P<page>[-\w]+)/$', views.SiteUserMessageView_replyme, name='siteuser_private_replyme_with_page'),
    url(r'^account/myreply/$', views.SiteUserMessageView_myreply, name='siteuser_private_myreply'),
    url(r'^account/myreply/(?P<page>[-\w]+)/$', views.SiteUserMessageView_myreply, name='siteuser_private_myreply_with_page'),

    url(r'^(?P<userurlname>[-\w]+)/fans/$', views.MyFansView, name='my_fans'),#我的粉丝
    url(r'^(?P<userurlname>[-\w]+)/fans/(?P<page>\d+)/$', views.MyFansView, name='my_fans_with_page'),#我的粉丝
    url(r'^(?P<userurlname>[-\w]+)/focus/$', views.MyFocusView, name='my_focus'),#我的关注
    url(r'^(?P<userurlname>[-\w]+)/focus/(?P<page>\d+)/$', views.MyFocusView, name='my_focus_with_page'),#我的关注
    url(r'^account/login/$', views.SiteUserLoginView.as_view(), name='siteuser_login'),
    url(r'^account/register/$', views.SiteUserRegisterView.as_view(), name='siteuser_register'),
    url(r'^account/fromsocial/$', views.SiteUserRegisterView.as_view(), name='siteuser_as_register'),

    url(r'^search/(?P<word>[-\w])+/$', views.focusPerson, name='search'),
    
    url(r'^account/fans/$', views.UserFriendsView.as_view(), name='UserFriends'),
    url(r'^focusperson/$', views.focusPerson, name='focusperson'),
    url(r'^unfocusperson/$', views.unfocusperson, name='unfocusperson'),
    url(r'^removemyfocusfromperson/$', views.removemyfocusfromperson, name='removemyfocusfromperson'),
    url(r'^sendprivatemsg/$', views.sendprivatemsg, name='sendprivatemsg'),
    url(r'^setAllMessageToBeReaded/$', views.setAllMessageToBeReaded, name='setAllMessageToBeReaded'),

    # 丢失密码，重置第一步，填写注册邮件
    url(r'^account/resetpw/step1/$', views.SiteUserResetPwStepOneView.as_view(), name='siteuser_reset_step1'),
    url(r'^account/resetpw/step1/done/$', views.SiteUserResetPwStepOneDoneView.as_view(), name='siteuser_reset_step1_done'),

    # 第二布，重置密码。token是django.core.signing模块生成的带时间戳的加密字符串
    url(r'^account/resetpw/step2/done/$', views.SiteUserResetPwStepTwoDoneView.as_view(), name='siteuser_reset_step2_done'),
    url(r'^account/resetpw/step2/(?P<token>.+)/$', views.SiteUserResetPwStepTwoView.as_view(), name='siteuser_reset_step2'),

    # 登录用户修改密码
    url(r'^account/changepw/$', views.SiteUserChangePwView.as_view(), name='siteuser_changepw'),
    url(r'^account/changepw/done/$', views.SiteUserChangePwDoneView.as_view(), name='siteuser_changepw_done'),

    # 以上关于密码管理的url只能有本网站注册用户才能访问，第三方帐号不需要此功能


    url(r'^account/logout/$', views.logout, name='siteuser_logout'),
)


# 只有设置 USING_SOCIAL_LOGIN = True 的情况下，才会开启第三方登录功能
if USING_SOCIAL_LOGIN:
    urlpatterns += patterns('',
        url(r'^account/oauth/(?P<sitename>\w+)/?$', views.social_login_callback),
    )
