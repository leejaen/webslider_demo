# -*- coding: utf-8 -*-
import re
import json
import hashlib
from functools import wraps

from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.views.generic import View
from django.db.models import Q

from siteuser.users.models import InnerUser, SiteUser, SocialUser,UserFriends,UserMessage
from siteuser.users.tasks import send_mail
from siteuser.settings import (
    USING_SOCIAL_LOGIN,
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    SOCIALOAUTH_SITES,
    SOCIAL_LOGIN_DONE_REDIRECT_URL,
    SOCIAL_LOGIN_ERROR_REDIRECT_URL,
)
from siteuser.utils.load_user_define import user_defined_mixin
import datetime
from slider_DB.models import Slider, Tag
import math
from datetime import time

if USING_SOCIAL_LOGIN:
    from socialoauth import SocialSites, SocialAPIError, SocialSitesConfigError

# 注册，登录，退出等都通过 ajax 的方式进行

EMAIL_PATTERN = re.compile('^.+@.+\..+$')

class InnerAccoutError(Exception):
    pass

make_password = lambda passwd: hashlib.sha1(passwd).hexdigest()

def inner_account_ajax_guard(func):
    @wraps(func)
    def deco(self, request, *args, **kwargs):
        dump = lambda d: HttpResponse(json.dumps(d), mimetype='application/json')
        if request.siteuser:
            return dump({'ok': False, 'msg': '你已登录'})

        try:
            func(self, request, *args, **kwargs)
        except InnerAccoutError as e:
            return dump({'ok': False, 'msg': str(e)})

        return dump({'ok': True})
    return deco

def inner_account_http_guard(func):
    @wraps(func)
    def deco(self, request, *args, **kwargs):
        if request.siteuser:
            return HttpResponseRedirect('/')
        try:
            return func(self, request, *args, **kwargs)
        except InnerAccoutError as e:
            ctx = self.ctx_getter(request)
            ctx.update(getattr(self, 'ctx', {}))
            ctx.update({'error_msg': e})
            return render_to_response(self.tpl,
                ctx,
                context_instance=RequestContext(request))
    return deco


class SiteUserMixIn(object):
    """用户可以自定义 SITEUSER_ACCOUNT_MIXIN 来覆盖这些配置"""
    login_template = 'siteuser/login.html'
    register_template = 'siteuser/register.html'
    reset_passwd_template = 'siteuser/reset_password.html'
    change_passwd_template = 'siteuser/change_password.html'

    # 用于生成重置密码链接的key,用于加密解密
    sign_key = 'siteuser_signkey'

    # 重置密码邮件的标题
    reset_passwd_email_title = u'重置密码'
    reset_passwd_email_template = 'siteuser/reset_password_email.html'

    # 多少小时后重置密码的链接失效
    reset_passwd_link_expired_in = 24

    # 在渲染这些模板的时候，如果你有额外的context需要传入，请重写这些方法
    def get_login_context(self, request):
        return {'info' : 'test'}

    def get_register_context(self, request):
        return {}

    def get_reset_passwd_context(self, request):
        return {}

    def get_change_passwd_context(self, request):
        return {}

    def get(self, request, *args, **kwargs):
        """使用此get方法的Class，必须制定这两个属性：
        self.tpl - 此view要渲染的模板名
        self.ctx_getter - 渲染模板是获取额外context的方法名
        """
        if request.siteuser:
            return HttpResponseRedirect('/')
        ctx = self.ctx_getter(request)
        ctx.update(getattr(self, 'ctx', {}))
        return render_to_response(self.tpl,
            ctx,
            context_instance=RequestContext(request))

    def _reset_passwd_default_ctx(self):
        return {
            'step1': False,
            'step1_done': False,
            'step2': False,
            'step2_done': False,
            'expired': False,
        }

    def _normalize_referer(self, request):
        referer = request.META.get('HTTP_REFERER', '/')
        if referer.endswith('done/'):
            referer = '/'
        return referer



class SiteUserLoginView(user_defined_mixin(), SiteUserMixIn, View):
    """登录"""
    def __init__(self, **kwargs):
        self.tpl = self.login_template
        self.ctx_getter = self.get_login_context
        super(SiteUserLoginView, self).__init__(**kwargs)

    def get_login_context(self, request):
        """
        注册和登录都是通过ajax进行的，这里渲染表单模板的时候传入referer，
        当ajax post返回成功标识的时候，js就到此referer的页面。
        以此来完成注册/登录完毕后自动回到上个页面
        """
        ctx = super(SiteUserLoginView, self).get_login_context(request)
        ctx['referer'] = self._normalize_referer(request)
        return ctx

    @inner_account_ajax_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        passwd = request.POST.get('passwd', None)

        if not email or not passwd:
            raise InnerAccoutError('请填写email和密码')

        try:
            user = InnerUser.objects.get(email=email)
        except InnerUser.DoesNotExist:
            raise InnerAccoutError('用户不存在')

        if user.passwd != hashlib.sha1(passwd).hexdigest():
            raise InnerAccoutError('密码错误')

        request.session['uid'] = user.user.id

class UserFriendsView(user_defined_mixin(), SiteUserMixIn, View):
    '''关注'''
    def __init__(self, **kwargs):
        #print "@@@@@@@@@@@@"+"__init__"
        self.tpl = self.register_template
        #print "@@@@@@@@@@@@"+str(self.tpl)
        self.ctx_getter = self.get_register_context
        #print "@@@@@@@@@@@@"+str(self.get_register_context)
        super(UserFriendsView, self).__init__(**kwargs)
        #print "@@@@@@@@@@@@"+"get_register_context"

    def get_register_context(self, request):
        ctx = super(UserFriendsView, self).get_register_context(request)
        ctx['referer'] = self._normalize_referer(request)
        return ctx


    @inner_account_ajax_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        username = request.POST.get('username', None)
        passwd = request.POST.get('passwd', None)

        import logging
        logger = logging.getLogger(__name__)
        logger.error('This is an error')

        if not email or not username or not passwd:
            raise InnerAccoutError('请完整填写注册信息')

        if len(email) > MAX_EMAIL_LENGTH:
            raise InnerAccoutError('电子邮件地址太长')

        if EMAIL_PATTERN.search(email) is None:
            raise InnerAccoutError('电子邮件格式不正确')

        if InnerUser.objects.filter(email=email).exists():
            raise InnerAccoutError('此电子邮件已被占用')

        if len(username) > MAX_USERNAME_LENGTH:
            raise InnerAccoutError('用户名太长，不要超过{0}个字符'.format(MAX_USERNAME_LENGTH))

        if SiteUser.objects.filter(username=username).exists():
            raise InnerAccoutError('用户名已存在')

        passwd = make_password(passwd)
        user = InnerUser.objects.create(email=email, passwd=passwd, username=username)
        request.session['uid'] = user.user.id

class SiteUserRegisterView(user_defined_mixin(), SiteUserMixIn, View):
    """注册"""
    
    def __init__(self, **kwargs):
        #print "@@@@@@@@@@@@"+"__init__"
        self.tpl = self.register_template
        #print "@@@@@@@@@@@@"+str(self.tpl)
        self.ctx_getter = self.get_register_context
        #print "@@@@@@@@@@@@"+str(self.get_register_context)
        super(SiteUserRegisterView, self).__init__(**kwargs)
        #print "@@@@@@@@@@@@"+"get_register_context"

    def get_register_context(self, request):
        ctx = super(SiteUserRegisterView, self).get_register_context(request)
        ctx['referer'] = self._normalize_referer(request)
        return ctx


    @inner_account_ajax_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        username = request.POST.get('username', None)
        passwd = request.POST.get('passwd', None)

        import logging
        logger = logging.getLogger(__name__)
        logger.error('This is an error')

        if not email or not username or not passwd:
            raise InnerAccoutError('请完整填写注册信息')

        if len(email) > MAX_EMAIL_LENGTH:
            raise InnerAccoutError('电子邮件地址太长')

        if EMAIL_PATTERN.search(email) is None:
            raise InnerAccoutError('电子邮件格式不正确')

        if InnerUser.objects.filter(email=email).exists():
            raise InnerAccoutError('此电子邮件已被占用')

        if len(username) > MAX_USERNAME_LENGTH:
            raise InnerAccoutError('用户名太长，不要超过{0}个字符'.format(MAX_USERNAME_LENGTH))

        if SiteUser.objects.filter(username=username).exists():
            raise InnerAccoutError('用户名已存在')

        passwd = make_password(passwd)
        user = InnerUser.objects.create(email=email, passwd=passwd, username=username)
        request.session['uid'] = user.user.id


class SiteUserResetPwStepOneView(user_defined_mixin(), SiteUserMixIn, View):
    """丢失密码重置第一步，填写注册时的电子邮件"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step1'] = True
        super(SiteUserResetPwStepOneView, self).__init__(**kwargs)

    @inner_account_http_guard
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', None)
        if not email:
            raise InnerAccoutError('请填写电子邮件')
        if EMAIL_PATTERN.search(email) is None:
            raise InnerAccoutError('电子邮件格式不正确')
        try:
            user = InnerUser.objects.get(email=email)
        except InnerUser.DoesNotExist:
            raise InnerAccoutError('请填写您注册时的电子邮件地址')

        token = signing.dumps(user.user.id, key=self.sign_key)
        link = reverse('siteuser_reset_step2', kwargs={'token': token})
        link = request.build_absolute_uri(link)
        context = {
            'hour': self.reset_passwd_link_expired_in,
            'link': link
        }
        body = loader.render_to_string(self.reset_passwd_email_template, context)
        # 异步发送邮件
        body = unicode(body)
        send_mail.delay(email, self.reset_passwd_email_title, body)
        return HttpResponseRedirect(reverse('siteuser_reset_step1_done'))


class SiteUserResetPwStepOneDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """发送重置邮件完成"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step1_done'] = True
        super(SiteUserResetPwStepOneDoneView, self).__init__(**kwargs)


class SiteUserResetPwStepTwoView(user_defined_mixin(), SiteUserMixIn, View):
    """丢失密码重置第二步，填写新密码"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step2'] = True
        super(SiteUserResetPwStepTwoView, self).__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        try:
            self.uid = signing.loads(token, key=self.sign_key, max_age=self.reset_passwd_link_expired_in * 3600)
        except signing.SignatureExpired:
            # 通过context来控制到底显示表单还是过期信息
            self.ctx['expired'] = True
        except signing.BadSignature:
            raise Http404
        return super(SiteUserResetPwStepTwoView, self).get(request, *args, **kwargs)


    @inner_account_http_guard
    def post(self, request, *args, **kwargs):
        password = request.POST.get('password', None)
        password1 = request.POST.get('password1', None)
        if not password or not password1:
            raise InnerAccoutError('请填写密码')
        if password != password1:
            raise InnerAccoutError('两次密码不一致')
        uid = signing.loads(kwargs['token'], key=self.sign_key)
        password = make_password(password)
        InnerUser.objects.filter(user_id=uid).update(passwd=password)
        return HttpResponseRedirect(reverse('siteuser_reset_step2_done'))


class SiteUserResetPwStepTwoDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """重置完成"""
    def __init__(self, **kwargs):
        self.tpl = self.reset_passwd_template
        self.ctx_getter = self.get_reset_passwd_context
        self.ctx = self._reset_passwd_default_ctx()
        self.ctx['step2_done'] = True
        super(SiteUserResetPwStepTwoDoneView, self).__init__(**kwargs)


class SiteUserChangePwView(user_defined_mixin(), SiteUserMixIn, View):
    """已登录用户修改密码"""
    def render_to_response(self, request, **kwargs):
        ctx = self.get_change_passwd_context(request)
        ctx['done'] = False
        ctx.update(kwargs)
        return render_to_response(self.change_passwd_template,
            ctx,
            context_instance=RequestContext(request))

    def get(self, request, *args, **kwargs):
        if not request.siteuser:
            return HttpResponseRedirect('/')
        if not request.siteuser.is_active or request.siteuser.is_social:
            return HttpResponseRedirect('/')
        return self.render_to_response(request)

    def post(self, request, *args, **kwargs):
        if not request.siteuser:
            return HttpResponseRedirect('/')
        if not request.siteuser.is_active or request.siteuser.is_social:
            return HttpResponseRedirect('/')

        password = request.POST.get('password', None)
        password1 = request.POST.get('password1', None)
        if not password or not password1:
            return self.render_to_response(request, error_msg='请填写新密码')
        if password != password1:
            return self.render_to_response(request, error_msg='两次密码不一致')
        password = make_password(password)
        if request.siteuser.inner_user.passwd == password:
            return self.render_to_response(request, error_msg='不能与旧密码相同')
        InnerUser.objects.filter(user_id=request.siteuser.id).update(passwd=password)
        # 清除登录状态
        try:
            del request.session['uid']
        except:
            pass

        return HttpResponseRedirect(reverse('siteuser_changepw_done'))


class SiteUserChangePwDoneView(user_defined_mixin(), SiteUserMixIn, View):
    """已登录用户修改密码成功"""
    def get(self, request, *args, **kwargs):
        if request.siteuser:
            return HttpResponseRedirect('/')
        ctx = self.get_change_passwd_context(request)
        ctx['done'] = True
        return render_to_response(self.change_passwd_template,
            ctx,
            context_instance=RequestContext(request))


def logout(request):
    """登出，ajax请求，然后刷新页面"""
    try:
        del request.session['uid']
    except:
        pass
    return HttpResponseRedirect('/')
    #return HttpResponse('', mimetype='application/json')

def social_login_callback(request, sitename):
    """第三方帐号OAuth认证登录，只有设置了USING_SOCIAL_LOGIN=True才会使用到此功能"""
    code = request.GET.get('code', None)
    if not code:
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)

    socialsites = SocialSites(SOCIALOAUTH_SITES)
    try:
        site = socialsites.get_site_object_by_name(sitename)
        site.get_access_token(code)
    except(SocialSitesConfigError, SocialAPIError):
        return HttpResponseRedirect(SOCIAL_LOGIN_ERROR_REDIRECT_URL)
    # 首先根据site_name和site uid查找此用户是否已经在自身网站认证，
    # 如果查不到，表示这个用户第一次认证登陆，创建新用户记录
    # 如果查到，就跟新其用户名和头像
    try:
        user = SocialUser.objects.get(site_uid=site.uid, site_name=site.site_name)
        SiteUser.objects.filter(id=user.user.id).update(username=site.name, avatar_url=site.avatar)
    except SocialUser.DoesNotExist:
        user = SocialUser.objects.create(site_uid=site.uid,
            site_name=site.site_name,
            username=site.name,
            avatar_url=site.avatar)

    # set uid in session, then this user will be auto login
    request.session['uid'] = user.user.id
    return HttpResponseRedirect(SOCIAL_LOGIN_DONE_REDIRECT_URL)
'''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@扩展功能@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
def isFocused(selfUID,otherUID):
    '''判断是否已经关注某人'''
    try:
        siteuser = SiteUser.objects.get(id__exact=selfUID)
        myInnerUser = InnerUser.objects.get(user=siteuser)
    
        friendsInnerUser = InnerUser.objects.get(user=SiteUser.objects.get(id__exact=otherUID))

        friend = UserFriends.objects.get(source=myInnerUser,target=friendsInnerUser)
    except:
        return 'no'
    if friend:
        return "yes"
    return 'no'
def SiteUserAccountIndexView(request,userurlname=None):
    '''某用户基本信息视图'''
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userurlname)
    except:
        siteuser = SiteUser.objects.get(id__exact=userurlname)

    extra = {}
    extra["navgationTag"] = u'userInfo'
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['isSelf'] = request.session['uid'] == siteuser.id
        extra['isfocused'] = isFocused(request.session['uid'],siteuser.id)
    else:
        extra['islogin'] = False
        extra['isSelf'] = False
        extra['isfocused'] = "no"
    extra.update(getPublicDic(request,userurlname))

    if siteuser.is_social == 1:
        socialUser = SocialUser.objects.get(user_id__exact=siteuser.id)
    else:
        socialUser = []
        
    t = loader.get_template('siteuser/accountPage_userinfo.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'socialUser':socialUser})
    return HttpResponse(t.render(c))
def focusPerson(request):
    '''ajax关注用户'''
    uid = request.POST.getlist('uid')[0]
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session['uid'])
    else:
        return HttpResponse("notLogin")#没有登录
    if siteuser.is_social:
        return HttpResponse("notinnerusercannotbefocused")#非站内用户不允许关注
    myInnerUser = InnerUser.objects.get(user=siteuser)
    friendsInnerUser = InnerUser.objects.get(user=SiteUser.objects.get(id__exact=uid))
    
    if myInnerUser.id == friendsInnerUser.id:
        return HttpResponse("notfocusself")#关注人和被关注人相同
    if UserFriends.objects.filter(source=myInnerUser,target=friendsInnerUser):
        return HttpResponse("focused")#已经关注过
    m = UserFriends(source=myInnerUser,target=friendsInnerUser,date_joined=datetime.datetime.now())
    m.save()
    
    friend = UserFriends.objects.get(source=myInnerUser,target=friendsInnerUser)
    if friend:
        return HttpResponse("focussuccess")

    return HttpResponse("focusfailed")#没有关注成功
def unfocusperson(request):
    '''ajax取消关注用户'''
    uid = request.POST.getlist('uid')[0]
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session['uid'])
    else:
        return HttpResponse("notLogin")#没有登录
    if siteuser.is_social:
        return HttpResponse("notinnerusercannotbeunfocused")#非站内用户不允许关注
    myInnerUser = InnerUser.objects.get(user=siteuser)
    friendsInnerUser = InnerUser.objects.get(user__id__exact=SiteUser.objects.get(id__exact=uid).id)
    
    if not UserFriends.objects.filter(source=myInnerUser,target=friendsInnerUser):
        return HttpResponse("nofocused")#没有关注过
    m = UserFriends.objects.filter(source=myInnerUser,target=friendsInnerUser)
    m.delete()
    try:
        friend = UserFriends.objects.get(source=myInnerUser,target=friendsInnerUser)
    except:
        return HttpResponse("successunfocus")

    return HttpResponse("failedunfocus")#取消关注没有成功
def removemyfocusfromperson(request):
    '''ajax取消某用户对我的关注'''
    uid = request.POST.getlist('uid')[0]#正在查看的用户的uid
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session['uid'])#我的账户
    else:
        return HttpResponse("notLogin")#没有登录
    if siteuser.is_social:
        return HttpResponse("notinnerusercannotbeunfocused")#非站内用户不允许关注
    try:
        myInnerUser = InnerUser.objects.get(user=siteuser)
        friendsInnerUser = InnerUser.objects.get(user__id__exact=SiteUser.objects.get(id__exact=uid).id)
    
        if not UserFriends.objects.filter(source=friendsInnerUser,target=myInnerUser):
            return HttpResponse("nofocusonyou")#没有关注过
        m = UserFriends.objects.filter(source=friendsInnerUser,target=myInnerUser)
        m.delete()
    except:
        return HttpResponse("removeError")

    try:
        friend = UserFriends.objects.get(source=friendsInnerUser,target=myInnerUser)
    except:
        return HttpResponse("successremove")

    return HttpResponse("failedremove")#取消关注没有成功

def SiteUserSliderView(request,userurlname=None,page=1):
    '''某用户的所有主题视图'''
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userurlname)
    except:
        siteuser = SiteUser.objects.get(id__exact=userurlname)

    existsUser=Slider.objects.filter(author__id__exact=siteuser.id)
    if not existsUser:#空 #根据 slider_DB_slider.author_id选择出slider_DB_slider表有对应数据的话才执行下面语句，否则会出错
            sliders = Slider.objects.filter(author__id__exact=siteuser.id).extra(select={
                    'likes': '0',
                    'collections': '0',
                    'amILikeIt':'0',
                    'amICollectIt':'0',
                }).order_by('-creation_date')[int(page) * 10 - 10:int(page) * 10]
    else:
        if 'uid' in request.session:
            sliders = Slider.objects.filter(author__id__exact=siteuser.id).extra(select={
                    'likes': 'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id',
                    'collections': 'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id',
                    'amILikeIt':'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id and users_siteuser_slider_like.siteuser_id=%s' % (request.session['uid']),
                    'amICollectIt':'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id and users_siteuser_slider_collection.siteuser_id=%s' % (request.session['uid']),
                }).order_by('-creation_date')[int(page) * 10 - 10:int(page) * 10]
        else:
            sliders = Slider.objects.filter(author__id__exact=siteuser.id).extra(select={
                    'likes': 'SELECT COUNT(id) FROM users_siteuser_slider_like WHERE users_siteuser_slider_like.slider_id = slider_DB_slider.slider_id',
                    'collections': 'SELECT COUNT(id) FROM users_siteuser_slider_collection WHERE users_siteuser_slider_collection.slider_id = slider_DB_slider.slider_id',
                    'amILikeIt':'0',
                    'amICollectIt':'0',
                }).order_by('-creation_date')[int(page) * 10 - 10:int(page) * 10]

    extra = {}
    extra["navgationTag"] = 'userSlider'
    extra["page"] = int(page)
    
    extra["slideCount"] = Slider.objects.filter(author__id__exact=siteuser.id).count()
    extra["pageCount"] = int(math.ceil(extra["slideCount"] / 10.0))#取整
    endxrange = extra["page"] / 10 * 10 + 10
    if endxrange > extra["slideCount"] / 10 + 1:
        endxrange = extra["slideCount"] / 10 + 1
    extra['loop_times'] = xrange(extra["page"] / 10 * 10 + 1,endxrange + 1)
    
    #return HttpResponse("%s"%(request.session['uid'])+"|"+"%s"%(siteuser.id))
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['isSelf'] = request.session['uid'] == siteuser.id
        extra['isfocused'] = isFocused(request.session['uid'],siteuser.id)
    else:
        extra['islogin'] = False
        extra['isSelf'] = False
        extra['isfocused'] = "no"
    extra.update(getPublicDic(request,userurlname))

    if siteuser.is_social == 1:
        socialUser = SocialUser.objects.get(user_id__exact=siteuser.id)
    else:
        socialUser = []

    t = loader.get_template('siteuser/accountPage_slider.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'socialUser':socialUser,"sliders":sliders})
    return HttpResponse(t.render(c))

def SiteUserTagView(request,userurlname=None,page=1):
    '''某用户的所有标签视图'''
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userurlname)
    except:
        siteuser = SiteUser.objects.get(id__exact=userurlname)
        
    if siteuser.is_social == 1:#无关注标签功能
        return HttpResponse("当前帐户不具备此功能")
    else:
        socialUser = []
        if 'uid' in request.session:
            if userurlname.isdigit():
                InterstingTags = InnerUser.objects.get(user__id__exact=userurlname).intersting_tags.all().extra(select={
                            "isInterting":"select count(*) from users_inneruser_intersting_tags as it where it.inneruser_id=%s and it.tag_id=slider_DB_tag.tag_ID" % (InnerUser.objects.get(user__id__exact=request.session['uid']).id),
                            "intertingCount":"select count(*) from users_inneruser_intersting_tags as it where it.tag_id=slider_DB_tag.tag_ID",
                            "sliderCount":"select count(*) from slider_DB_slider_tags as st where st.tag_id=slider_DB_tag.tag_ID"
                        })[int(page) * 20 - 20:int(page) * 20]
            else:
                InterstingTags = InnerUser.objects.get(user__id__exact=SiteUser.objects.get(urlname__exact=userurlname).id).intersting_tags.all().extra(select={
                            "isInterting":"select count(*) from users_inneruser_intersting_tags as it where it.inneruser_id=%s and it.tag_id=slider_DB_tag.tag_ID" % (InnerUser.objects.get(user__id__exact=request.session['uid']).id),
                            "intertingCount":"select count(*) from users_inneruser_intersting_tags as it where it.tag_id=slider_DB_tag.tag_ID",
                            "sliderCount":"select count(*) from slider_DB_slider_tags as st where st.tag_id=slider_DB_tag.tag_ID"
                        })[int(page) * 20 - 20:int(page) * 20]
        else:
            if userurlname.isdigit():
                InterstingTags = InnerUser.objects.get(user__id__exact=userurlname).intersting_tags.all().extra(select={
                            "isInterting":"0",
                            "intertingCount":"select count(*) from users_inneruser_intersting_tags as it where it.tag_id=slider_DB_tag.tag_ID",
                            "sliderCount":"select count(*) from slider_DB_slider_tags as st where st.tag_id=slider_DB_tag.tag_ID"
                        })[int(page) * 20 - 20:int(page) * 20]
            else:
                InterstingTags = InnerUser.objects.get(user__id__exact=SiteUser.objects.get(urlname__exact=userurlname).id).intersting_tags.all().extra(select={
                            "isInterting":"0",
                            "intertingCount":"select count(*) from users_inneruser_intersting_tags as it where it.tag_id=slider_DB_tag.tag_ID",
                            "sliderCount":"select count(*) from slider_DB_slider_tags as st where st.tag_id=slider_DB_tag.tag_ID"
                        })[int(page) * 20 - 20:int(page) * 20]


    extra = {}
    extra["navgationTag"] = 'intrestingTag'
    extra["page"] = int(page)
    
    if userurlname.isdigit():
        extra["slideCount"] = InnerUser.objects.get(user__id__exact=userurlname).intersting_tags.all().count()
    else:
        extra["slideCount"] = InnerUser.objects.get(user__id__exact=SiteUser.objects.get(urlname__exact=userurlname).id).intersting_tags.all().count()

    extra["pageCount"] = int(math.ceil(extra["slideCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["slideCount"] / 20 + 1:
        endxrange = extra["slideCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)

    if 'uid' in request.session:
        extra['islogin'] = True
        extra['isSelf'] = request.session['uid'] == siteuser.id
        extra['isfocused'] = isFocused(request.session['uid'],siteuser.id)
    else:
        extra['islogin'] = False
        extra['isSelf'] = False
        extra['isfocused'] = "no"
    extra.update(getPublicDic(request,userurlname))

    t = loader.get_template('siteuser/accountPage_tag.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'socialUser':socialUser,"InterstingTags":InterstingTags})
    return HttpResponse(t.render(c))
def SiteUserSignatureView(request):
    '''ajax修改签名'''
    try:
        signatureText = request.POST.getlist('signatureText')[0]
        aria = request.POST.getlist('aria')[0]
        if 'uid' in request.session:
            if (u'%s' % aria) == (u"%s" % request.session['uid']):
                SiteUser.objects.filter(id=request.session['uid']).update(signature=signatureText)
            else:#编辑的不是自己的签名
                return HttpResponse("overpower")
        else:#
            return HttpResponse("overpower")
    except:
        return HttpResponse("faild")
    return HttpResponse("success")
def MyLikeSlidersView(request,page=1):
    '''获取我的喜欢'''
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id=request.session["uid"])
        sliders = SiteUser.objects.get(id=request.session["uid"]).slider_like.all()[int(page) * 10 - 10:int(page) * 10]
    else:
        siteuser = {}
        return HttpResponse("您无权查看此页")
    
    extra = {}
    extra["navgationTag"] = 'mylike'
    extra["page"] = int(page)
    extra["slideCount"] = SiteUser.objects.get(id=request.session["uid"]).slider_like.all().count()
    extra["pageCount"] = int(math.ceil(extra["slideCount"] / 10.0))#取整
    endxrange = extra["page"] / 10 * 10 + 10
    if endxrange > extra["slideCount"] / 10 + 1:
        endxrange = extra["slideCount"] / 10 + 1
    extra['loop_times'] = xrange(extra["page"] / 10 * 10 + 1,endxrange + 1)
    
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['isSelf'] = request.session['uid'] == siteuser.id
    else:
        extra['islogin'] = False
        extra['isSelf'] = False
    extra.update(getPublicDic(request))

    t = loader.get_template('siteuser/accountPage_like.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'sliders':sliders})
    return HttpResponse(t.render(c))
def MyFavoSlidersView(request,page=1):
    '''获取我的喜欢'''
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id=request.session["uid"])
        sliders = SiteUser.objects.get(id=request.session["uid"]).slider_collection.all()[int(page) * 10 - 10:int(page) * 10]
    else:
        siteuser = {}
        return HttpResponse("您无权查看此页")
    
    extra = {}
    extra["navgationTag"] = 'myfavo'
    extra["page"] = int(page)
    extra["slideCount"] = SiteUser.objects.get(id=request.session["uid"]).slider_collection.all().count()
    extra["pageCount"] = int(math.ceil(extra["slideCount"] / 10.0))#取整
    endxrange = extra["page"] / 10 * 10 + 10
    if endxrange > extra["slideCount"] / 10 + 1:
        endxrange = extra["slideCount"] / 10 + 1
    extra['loop_times'] = xrange(extra["page"] / 10 * 10 + 1,endxrange + 1)
    
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['isSelf'] = request.session['uid'] == siteuser.id
    else:
        extra['islogin'] = False
        extra['isSelf'] = False
    extra.update(getPublicDic(request))

    t = loader.get_template('siteuser/accountPage_favo.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'sliders':sliders})
    return HttpResponse(t.render(c))


def getUserIdFromInnerUser(row):
    '''用于MyFansView和MyFocusView中选择每一用户的id'''
    return row.user.id
def getSourceIdFromFriends(row):
    '''用于MyFansView中选择每一用户的粉丝的id'''
    return row.source.id
def getTargetIdFromFriends(row):
    '''用于MyFansView中选择每一用户的关注的人的id'''
    return row.target.id
def MyFansView(request,userurlname=None,page=1):
    '''获取我的粉丝'''
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userurlname)
    except:
        siteuser = SiteUser.objects.get(id__exact=userurlname)
    if siteuser.is_social == 1:
        return HttpResponse("当前帐户不具备此功能")
    #考虑使用map选择每一行的id
    if 'uid' in request.session:
        fans = SiteUser.objects.filter(id__in=
                                       map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                                 map(getSourceIdFromFriends,list(UserFriends.objects.filter(target = 
                                                            InnerUser.objects.get(user_id=siteuser.id)))))))).extra(select={
                            "isfocused":"select count(*)from users_userfriends fr where fr.source_id =(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id)" % (request.session["uid"]),
                            "fansCount":"select count(*)from users_userfriends fr where fr.target_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "focusCount":"select count(*)from users_userfriends fr where fr.source_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "iseachother":'''select count(*)from users_userfriends fr where 
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id))
                            or
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=users_siteuser.id)and fr.target_id=(select id from users_inneruser iu where iu.user_id=%s))''' % (request.session["uid"],request.session["uid"]),
                            })[int(page) * 20 - 20:int(page) * 20]
    else:
        fans = SiteUser.objects.filter(id__in=
                                       map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                                 map(getSourceIdFromFriends,list(UserFriends.objects.filter(target = 
                                                            InnerUser.objects.get(user_id=siteuser.id)))))))).extra(select={
                            "isfocused":"select count(*)from users_userfriends fr where fr.source_id =(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id)" % (0),
                            "fansCount":"select count(*)from users_userfriends fr where fr.target_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "focusCount":"select count(*)from users_userfriends fr where fr.source_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "iseachother":'''select count(*)from users_userfriends fr where 
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id))
                            or
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=users_siteuser.id)and fr.target_id=(select id from users_inneruser iu where iu.user_id=%s))''' % (0,0),
                            })[int(page) * 20 - 20:int(page) * 20]
    extra = {}
    extra["navgationTag"] = 'myfans'
    extra["page"] = int(page)
    
    extra["fansCount"] = SiteUser.objects.filter(id__in=
                                       map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                                 map(getSourceIdFromFriends,list(UserFriends.objects.filter(target = 
                                                            InnerUser.objects.get(user_id=siteuser.id)))))))).count()
    
    extra["pageCount"] = int(math.ceil(extra["fansCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["fansCount"] / 20 + 1:
        endxrange = extra["fansCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)
    
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['myuserid'] = request.session['uid']
        extra['isSelf'] = request.session['uid'] == siteuser.id
    else:
        extra['islogin'] = False
        extra['myuserid'] = 0
        extra['isSelf'] = False
    extra.update(getPublicDic(request,userurlname))

    t = loader.get_template('siteuser/accountPage_fansinfo.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'fans':fans})
    return HttpResponse(t.render(c))
def MyFocusView(request,userurlname=None,page=1):
    '''获取我关注的用户'''
    try:
        siteuser = SiteUser.objects.get(urlname__exact=userurlname)
    except:
        siteuser = SiteUser.objects.get(id__exact=userurlname)
    if siteuser.is_social == 1:
        return HttpResponse("当前帐户不具备此功能")
    #考虑使用map选择每一行的id
    
    if 'uid' in request.session:
        fans = SiteUser.objects.filter(id__in=
                                    map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                            map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
                                                InnerUser.objects.get(user_id=siteuser.id)))))))).extra(select={
                            "isfocused":"select count(*)from users_userfriends fr where fr.source_id =(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id)" % (request.session['uid']),
                            "fansCount":"select count(*)from users_userfriends fr where fr.target_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "focusCount":"select count(*)from users_userfriends fr where fr.source_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "iseachother":"""select count(*)from users_userfriends fr where 
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id))
                            or
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=users_siteuser.id) and fr.target_id=(select id from users_inneruser iu where iu.user_id=%s))
                            """ % (request.session['uid'],request.session['uid'])
                            })[int(page) * 20 - 20:int(page) * 20]
    else:
        fans = SiteUser.objects.filter(id__in=
                                    map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                            map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
                                                InnerUser.objects.get(user_id=siteuser.id)))))))).extra(select={
                            "isfocused":"select count(*)from users_userfriends fr where fr.source_id =(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id)" % (0),
                            "fansCount":"select count(*)from users_userfriends fr where fr.target_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "focusCount":"select count(*)from users_userfriends fr where fr.source_id = (select id from users_inneruser iu where iu.user_id=users_siteuser.id)",
                            "iseachother":"""select count(*)from users_userfriends fr where 
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=%s) and fr.target_id= (select id from users_inneruser iu where iu.user_id=users_siteuser.id))
                            or
                            (fr.source_id=(select id from users_inneruser iu where iu.user_id=users_siteuser.id) and fr.target_id=(select id from users_inneruser iu where iu.user_id=%s))
                            """ % (0,0)
                            })[int(page) * 20 - 20:int(page) * 20]

    extra = {}
    extra["navgationTag"] = 'myfocus'
    extra["page"] = int(page)
    #考虑使用map选择每一行的id
    extra["fansCount"] = SiteUser.objects.filter(id__in=
                                    map(getUserIdFromInnerUser,list(InnerUser.objects.filter(id__in=
                                            map(getTargetIdFromFriends,list(UserFriends.objects.filter(source = 
                                                InnerUser.objects.get(user_id=siteuser.id)))))))).count()
    
    extra["pageCount"] = int(math.ceil(extra["fansCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["fansCount"] / 20 + 1:
        endxrange = extra["fansCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)
    
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['myuserid'] = request.session['uid']
        extra['isSelf'] = request.session['uid'] == siteuser.id
    else:
        extra['islogin'] = False
        extra['myuserid'] = 0
        extra['isSelf'] = False
    extra.update(getPublicDic(request,userurlname))

    t = loader.get_template('siteuser/accountPage_fansinfo.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,'fans':fans})
    return HttpResponse(t.render(c))

def getPublicDic(request,userurlname=None):
    '''公共方法：获取正在访问的用户的粉丝数关注数标签关注数'''
    if userurlname is None:
        if "uid" in request.session:
            siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
        else:
            return {}
    else:
        try:
            siteuser = SiteUser.objects.get(urlname__exact=userurlname)
        except:
            siteuser = SiteUser.objects.get(id__exact=userurlname)
    if siteuser.is_social == 1:#第三方用户
        return {}
    theInnerUser = InnerUser.objects.get(user__id__exact=siteuser.id)
    userFansCount = UserFriends.objects.filter(target=theInnerUser).count()
    userFocusCount = UserFriends.objects.filter(source=theInnerUser).count()
    userTagsCount = theInnerUser.intersting_tags.count()
    return {"userFansCount":userFansCount,"userFocusCount":userFocusCount,"userTagsCount":userTagsCount}

def sendprivatemsg(request):
    '''ajax发送私信'''
    message = request.POST.getlist('message')[0]#消息内容
    targetUserId = request.POST.getlist('aria')[0]#正在查看的用户的uid
    targetMsgId = request.POST.getlist('areamsg')[0]#要回复的messageid
    if 'uid' in request.session:
        me = SiteUser.objects.get(id__exact=request.session['uid'])#我的账户
    else:
        return HttpResponse("notLogin")#没有登录
    try:
        receiveUser = SiteUser.objects.get(id__exact=targetUserId)
        replyMsg = UserMessage.objects.filter(id=targetMsgId)
        replyMsg.update(IsRead = True)
    except:
        return HttpResponse("dataerror")

    #try:
    if targetMsgId:#回复消息
        message = UserMessage(FromUser=me,
                            ToUser=receiveUser,
                            MsgType='0',#消息类型，0站内信，1@，2回复我的评论，3收到的评论
                            MessageText=message,
                            CreationDate=datetime.datetime.now())
        message.save()
        message.replyto = (replyMsg)
    else:
        message = UserMessage(FromUser=me,
                            ToUser=receiveUser,
                            MsgType='0',#消息类型，0站内信，1@，2回复我的评论，3收到的评论
                            MessageText=message,
                            CreationDate=datetime.datetime.now())
        message.save()
    #except:
    #    return HttpResponse("failedsent")

    return HttpResponse("successsent")#取消关注没有成功

def getNoReadMessageCount(request,siteuser):
    '''取所有没有读取的消息的统计数字'''
    extra = {}
    extra["noReadPrivate"] = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0',IsRead='0')).count()
    extra["noReadAtMe"] = UserMessage.objects.filter(ToUser=siteuser,MsgType='1',IsRead='0').count()
    extra["noReadReplyMe"] = UserMessage.objects.filter(ToUser=siteuser,MsgType='2',IsRead='0').count()
    extra["noReadGetReply"] = UserMessage.objects.filter(ToUser=siteuser,MsgType='3',IsRead='0').count() 
    
    extra["navgationTag"] = 'userMessage'
    if 'uid' in request.session:
        extra['islogin'] = True
        extra['myuserid'] = request.session['uid']
        extra['isSelf'] = True
    return extra

def SiteUserMessageView(request,page=1):
    '''用户消息'''
    extra = {}
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
    else:
        return HttpResponse("检测到您没有登录")
    
    extra.update(getNoReadMessageCount(request,siteuser))#取所有没有读取的消息的统计数字
    extra.update(getPublicDic(request,request.session["uid"]))
    
    #选择ToUser或FromUser是siteuser的message
    Private = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).extra(select={"replayToMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate")[int(page) * 20 - 20:int(page) * 20]
    #return HttpResponse(UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).extra(select={"replayMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate").query.__str__())
    extra["page"] = int(page)
    extra["messageCount"] = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).count()
    extra["pageCount"] = int(math.ceil(extra["messageCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["messageCount"] / 20 + 1:
        endxrange = extra["messageCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)

    t = loader.get_template('siteuser/accountPage_message.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,"Private":Private})
    return HttpResponse(t.render(c))
def SiteUserMessageView_atme(request,page=1):
    '''用户消息@'''
    extra = {}
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
    else:
        return HttpResponse("检测到您没有登录")
    
    extra.update(getNoReadMessageCount(request,siteuser))#取所有没有读取的消息的统计数字
    extra.update(getPublicDic(request,request.session["uid"]))
    
    #选择ToUser或FromUser是siteuser的message 消息类型，0站内信，1@，2回复我的评论，3收到的评论
    Private = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='1') | Q(FromUser=siteuser,MsgType='1')).extra(select={"replayToMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate")[int(page) * 20 - 20:int(page) * 20]
    #return HttpResponse(UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).extra(select={"replayMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate").query.__str__())
    extra["page"] = int(page)
    extra["messageCount"] = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='1') | Q(FromUser=siteuser,MsgType='1')).count()
    extra["pageCount"] = int(math.ceil(extra["messageCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["messageCount"] / 20 + 1:
        endxrange = extra["messageCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)

    t = loader.get_template('siteuser/accountPage_message_atme.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,"Private":Private})
    return HttpResponse(t.render(c))
def SiteUserMessageView_replyme(request,page=1):
    '''回复我的评论'''
    extra = {}
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
    else:
        return HttpResponse("检测到您没有登录")
    
    extra.update(getNoReadMessageCount(request,siteuser))#取所有没有读取的消息的统计数字
    extra.update(getPublicDic(request,request.session["uid"]))
    
    #选择ToUser或FromUser是siteuser的message 消息类型，0站内信，1@，2回复我的评论，3收到的评论
    Private = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='2') | Q(FromUser=siteuser,MsgType='2')).extra(select={"replayToMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate")[int(page) * 20 - 20:int(page) * 20]
    #return HttpResponse(UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).extra(select={"replayMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate").query.__str__())
    extra["page"] = int(page)
    extra["messageCount"] = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='2') | Q(FromUser=siteuser,MsgType='2')).count()
    extra["pageCount"] = int(math.ceil(extra["messageCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["messageCount"] / 20 + 1:
        endxrange = extra["messageCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)

    t = loader.get_template('siteuser/accountPage_message_replyme.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,"Private":Private})
    return HttpResponse(t.render(c))
def SiteUserMessageView_myreply(request,page=1):
    '''回复我的评论'''
    extra = {}
    if 'uid' in request.session:
        siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
    else:
        return HttpResponse("检测到您没有登录")
    
    extra.update(getNoReadMessageCount(request,siteuser))#取所有没有读取的消息的统计数字
    extra.update(getPublicDic(request,request.session["uid"]))
    
    #选择ToUser或FromUser是siteuser的message 消息类型，0站内信，1@，2回复我的评论，3收到的评论
    Private = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='3') | Q(FromUser=siteuser,MsgType='3')).extra(select={"replayToMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate")[int(page) * 20 - 20:int(page) * 20]
    #return HttpResponse(UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).extra(select={"replayMessageId":"select to_usermessage_id from users_usermessage_replyto rp where rp.from_usermessage_id=users_usermessage.id limit 1"}).order_by("-CreationDate").query.__str__())
    extra["page"] = int(page)
    extra["messageCount"] = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='3') | Q(FromUser=siteuser,MsgType='3')).count()
    extra["pageCount"] = int(math.ceil(extra["messageCount"] / 20.0))#取整
    endxrange = extra["page"] / 20 * 20 + 20
    if endxrange > extra["messageCount"] / 20 + 1:
        endxrange = extra["messageCount"] / 20 + 1
    extra['loop_times'] = xrange(extra["page"] / 20 * 20 + 1,endxrange + 1)

    t = loader.get_template('siteuser/accountPage_message_myreply.html')
    c = RequestContext(request,{'siteuser':siteuser,"extraInfo":extra,"Private":Private})
    return HttpResponse(t.render(c))
def setAllMessageToBeReaded(request):
    '''设置所有显示的消息为已读'''
    try:
        if 'uid' in request.session:
            siteuser = SiteUser.objects.get(id__exact=request.session["uid"])
        Private = UserMessage.objects.filter(Q(ToUser=siteuser,MsgType='0') | Q(FromUser=siteuser,MsgType='0')).order_by("-CreationDate")
        Private.update(IsRead=True)
    except:
        return HttpResponse("error")
    return HttpResponse("success")