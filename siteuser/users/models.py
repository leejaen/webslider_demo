# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.db import models
from django.utils import timezone

from siteuser.settings import (
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    AVATAR_URL_PREFIX,
    DEFAULT_AVATAR,
    AVATAR_DIR,
)

from siteuser.upload_avatar.signals import avatar_crop_done

"""
siteuser的核心，
    SocialUser - 保存第三方帐号
    InnerUser  - 网站自身注册用户
    SiteUser   - 用户信息表

目前 SocialUser, InnerUser 都不支持扩展，方法直接写死。
这种在只支持第三方登录的应用情况下，是够用的。

SiteUser 之定义了最基本的数据，用户可以自由的扩展字段。
需要注意的是， SiteUser中的 username 不能设置为 unique = True
因为第三方社交帐号的username也保存在这个表里，
然而不同社交站点的用户完全有可能重名。
"""



class SiteUserManager(models.Manager):
    def create(self, is_social, **kwargs):
        if 'user' not in kwargs and 'user_id' not in kwargs:
            siteuser_kwargs = {
                'is_social': is_social,
                'username': kwargs.pop('username'),
                'date_joined': timezone.now(),
            }
            if 'avatar_url' in kwargs:
                siteuser_kwargs['avatar_url'] = kwargs.pop('avatar_url')
            user = SiteUser.objects.create(**siteuser_kwargs)
            kwargs['user_id'] = user.id

        return super(SiteUserManager, self).create(**kwargs)


class SocialUserManager(SiteUserManager):
    def create(self, **kwargs):
        return super(SocialUserManager, self).create(True, **kwargs)


class InnerUserManager(SiteUserManager):
    def create(self, **kwargs):
        return super(InnerUserManager, self).create(False, **kwargs)


class SocialUser(models.Model):
    """第三方帐号"""
    user = models.OneToOneField('SiteUser', related_name='social_user',verbose_name='用户')
    site_uid = models.CharField(max_length=128,verbose_name='网站UID')
    site_name = models.CharField(max_length=32,verbose_name='网站名称')

    objects = SocialUserManager()

    class Meta:
        unique_together = (('site_uid', 'site_name'),)
        verbose_name = "第三方帐号"
        verbose_name_plural = "第三方帐号"


class InnerUser(models.Model):
    """自身注册用户"""
    user = models.OneToOneField('SiteUser', related_name='inner_user',verbose_name='用户')
    email = models.CharField(max_length=MAX_EMAIL_LENGTH, unique=True,verbose_name='E-mail')
    passwd = models.CharField(max_length=40,verbose_name='密码')
    joinSocialUser = models.ForeignKey(SocialUser,verbose_name='关联社交用户', null=True, blank=True, default = None)
    friends = models.ManyToManyField('self', through ='UserFriends',symmetrical = False,verbose_name='关注的人'.decode('utf8'))
    intersting_tags = models.ManyToManyField('slider_DB.Tag',blank = True, related_name='intersting_tags',verbose_name='关注的标签'.decode('utf8'))#关注的标签
    objects = InnerUserManager()
    class Meta:
        verbose_name = "站内用户"
        verbose_name_plural = "站内用户"

class UserFriends(models.Model):
    '''好友关注'''
    """thanks for http://stackoverflow.com/questions/3880489/how-do-i-write-a-django-model-with-manytomany-relationsship-with-self-through-a"""
    source = models.ForeignKey(InnerUser, related_name = 'source',verbose_name='源关注者')
    #                                     ^^^^^^^^^^^^
    # You need different `related_name` for each when you have
    # multiple foreign keys to the same table.
    target = models.ForeignKey(InnerUser, related_name = 'target',verbose_name='被关注者')
    comment = models.CharField(max_length = 255,verbose_name='注释')
    date_joined = models.DateTimeField(verbose_name='关注时间')
    class Meta:
        verbose_name = "好友关注"
        verbose_name_plural = "好友关注"

def _siteuser_extend():
    siteuser_extend_model = getattr(settings, 'SITEUSER_EXTEND_MODEL', None)
    if not siteuser_extend_model:
        return models.Model

    if isinstance(siteuser_extend_model, models.base.ModelBase):
        # 直接定义的 SITEUSER_EXTEND_MODEL
        if not siteuser_extend_model._meta.abstract:
            raise AttributeError("%s must be an abstract model" % siteuser_extend_model.__name__)
        return siteuser_extend_model

    # 以string的方式定义的 SITEUSER_EXTEND_MODEL
    _module, _model = siteuser_extend_model.rsplit('.', 1)
    try:
        m = __import__(_module, fromlist=['.'])
        _model = getattr(m, _model)
    except:
        m = __import__(_module + '.models', fromlist=['.'])
        _model = getattr(m, _model)
    
    if not _model._meta.abstract:
        raise AttributeError("%s must be an abstract model" % siteuser_extend_model)
    return _model

class UserMessage(models.Model):
    '''用户消息'''
    FromUser = models.ForeignKey('SiteUser',related_name = 'messageFromUser',verbose_name='发出者', null=False)
    ToUser = models.ForeignKey('SiteUser',related_name = 'messageToUser',verbose_name='接收者', null=False)
    MsgType = models.CharField(max_length=2,null=True,verbose_name='消息类型，0站内信，1@，2回复我的评论，3收到的评论')
    MsgDirectTo = models.CharField(max_length=200,null=True,verbose_name='消息指向链接，消息类型不是0时的指向的消息源')
    replyto = models.ManyToManyField('self',verbose_name='回复的消息'.decode('utf8'))#linux系统对表名区分大小写，但是syncdb命令 创建使用区分大小写的方法创建表，但是sql语句中使用小写，会引发(1146, "Table 'webslider.users_usermessage_replyto' doesn't exist")错误，使用小写规避此错误内容。
    MessageText = models.TextField(blank=False,verbose_name='消息内容')
    IsRead=models.BooleanField(default=False, verbose_name='是否已读')
    CreationDate = models.DateTimeField(verbose_name='发出时间')
    class Meta:
        verbose_name = "用户消息"
        verbose_name_plural = "用户消息"

class SiteUser(_siteuser_extend()):
    """用户信息，如果需要（大部分情况也确实是需要）扩展SiteUser的字段，
    需要定义SITEUSER_EXTEND_MODEL.此model必须设置 abstract=True
    """
    is_social = models.BooleanField(verbose_name='是否第三方用户')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    date_joined = models.DateTimeField(verbose_name='加入时间')
    urlname = models.CharField(max_length=MAX_USERNAME_LENGTH,blank=True,verbose_name='账户名')
    signature = models.CharField(max_length=100,blank=True,verbose_name='个性签名')
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, db_index=True,verbose_name='用户名')
    # avatar_url for social user
    avatar_url = models.CharField(max_length=255, blank=True,verbose_name='avatar URL')
    # avatar_name for inner user uploaded avatar
    avatar_name = models.CharField(max_length=64, blank=True,verbose_name='avatar Name')
    
    slider_like = models.ManyToManyField('slider_DB.Slider',blank = True, related_name='slider_like',verbose_name='喜欢的幻灯片'.decode('utf8'))
    slider_collection = models.ManyToManyField('slider_DB.Slider',blank = True, related_name='collection_slider',verbose_name='收藏的幻灯片'.decode('utf8'))

    def __unicode__(self):
        return u'<SiteUser %d, %s>' % (self.id, self.username)

    @property
    def userURL(self):
        if self.urlname:
            return self.urlname
        else:
            return self.id
    @property
    def avatar(self):
        if not self.avatar_url and not self.avatar_name:
            return AVATAR_URL_PREFIX + DEFAULT_AVATAR
        if self.is_social:
            return self.avatar_url
        return AVATAR_URL_PREFIX + self.avatar_name
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"

def _save_avatar_in_db(sender, uid, avatar_name, **kwargs):
    if not SiteUser.objects.filter(id=uid, is_social=False).exists():
        return

    old_avatar_name = SiteUser.objects.get(id=uid).avatar_name
    if old_avatar_name == avatar_name:
        # 上传一张图片后，连续剪裁的情况
        return

    if old_avatar_name:
        _path = os.path.join(AVATAR_DIR, old_avatar_name)
        try:
            os.unlink(_path)
        except:
            pass

    SiteUser.objects.filter(id=uid).update(avatar_name=avatar_name)


avatar_crop_done.connect(_save_avatar_in_db)
