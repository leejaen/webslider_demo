#在管理页面添加此部分业务的管理配置逻辑
from django.contrib import admin
from django.db import models
from siteuser.users.models import SiteUser,InnerUser,SocialUser,UserFriends
from slider_DB.models import Tag,Slider,Slider_Status,Slider_Gallery,Comment,Slider_Content,Content_Class_Style#, OauthType, Member
from PIL import Image

#class OauthAdmin(admin.ModelAdmin):
#    list_display = ('type_ID','type_name')#定义显示列
#    search_fields = ('type_ID','type_name')#定义搜索列

#class MemberAdmin(admin.ModelAdmin):
#    list_display =
#    ('ID','oauth_type','oauth_ID','last_oauth_time','sex')#定义显示列
#    search_fields = ('oauth_type', 'oauth_ID','last_oauth_time')#定义搜索列
#    ordering = ('-last_oauth_time',)
#    fields = ('ID','oauth_type', 'oauth_ID','sex', 'last_oauth_time')#定义字段顺序

#以下内容在定义的时候一定记得不要忘了最后一个项目的逗号！！！！！！！！！！
class StatusAdmin(admin.ModelAdmin):
    list_display = ('status_id','status_name','status_creator','status_description','creation_datetime')#定义显示列
    search_fields = ('status_name','status_creator','status_description')#定义搜索列
    list_filter = ('status_creator',)#定义过滤器
    ordering = ('-creation_datetime',)#定义排序
    raw_id_fields = ('status_creator',)#某个一对多字段显示（）

class SliderAdmin(admin.ModelAdmin):
    list_display = ('slider_ID','author','title','description','status','creation_date')#定义显示列
    search_fields = ('title','tags','title')#定义搜索列
    list_filter = ('title','tags','title','description','creation_date')#定义过滤器
    ordering = ('-creation_date',)#定义排序
    #fields = ('slider_ID','member', 'title','creation_date')#定义字段顺序
    filter_horizontal = ('tags','visitors')#某个多对多字段显示（多个结果），注意此字段的verbose_name是中文时要使用.decode('utf8')显示，否则显示不出过滤器控件
    raw_id_fields = ('author','status')#某个一对多字段显示（多个结果）

from filebrowser.widgets import FileInput
class GalleryAdmin(admin.ModelAdmin):
    formfield_overrides = {#上传图片功能
                           
models.ImageField: {'widget': FileInput},
    }
    list_display = ('gallery_id','slider','image','gallery_word','gallery_date')#定义显示列
    search_fields = ('recommended_id','slider','gallery_word','gallery_date')#定义搜索列
    list_filter = ('slider','gallery_word','gallery_date')#定义过滤器
    ordering = ('-gallery_date',)#定义排序
    fields = ('gallery_id','slider','gallery_word','image','gallery_date')#定义字段顺序
    '''
    filter_horizontal = ('tags','visitors')#某个多对多字段显示（多个结果），注意此字段的verbose_name是中文时要使用.decode('utf8')显示，否则显示不出过滤器控件
    '''
    raw_id_fields = ('slider',)#某个一对多字段显示（多个结果）

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_ID','tag_name','pic','creation_date','creator')#定义显示列
    search_fields = ('tag_ID','tag_name','creation_date')#定义搜索列
    list_filter = ('tag_ID','tag_name','creation_date')#定义过滤器
    ordering = ('-creation_date',)#定义排序
    #fields = ('CCS_ID','slider_ID','creation_datetime')#定义字段顺序
    raw_id_fields = ('creator',)#某个一对多字段显示（多个结果）

class CommentAdmin(admin.ModelAdmin):
    class Media:#定义文本编辑器组件修改内容
        js = ('/static/tinymce/tinymce.min.js',
                '/static/tinymce/textareas.js',)
    list_display = ('comment_ID','to_slider_content','comment_content','recomment','comment_datetime')#定义显示列
    search_fields = ('comment_ID','to_slider_content','comment_content','recomment','comment_datetime')#定义搜索列
    list_filter = ('comment_ID','to_slider_content','comment_content','recomment','comment_datetime')#定义过滤器
    ordering = ('-comment_datetime',)#定义排序
    filter_horizontal = ('agrees','disagrees')#某个多对多字段显示（多个结果），注意此字段的verbose_name是中文时要使用.decode('utf8')显示，否则显示不出过滤器控件
    raw_id_fields = ('to_slider_content',)#某个一对多字段显示（多个结果）

class ContentAdmin(admin.ModelAdmin):
    class Media:#定义文本编辑器组件修改内容
        js = ('/static/tinymce/tinymce.min.js',
                '/static/tinymce/textareas.js',)
    list_display = ('slider_content_ID','slider_nav_id','sequenceNo','slider','slider_class','slider_title','dataX','dataY','dataZ','data_skew','data_rotate_x','data_rotate_y','data_rotate','data_scale','data_scale3d','data_perspective','syntax_highlighter','context','slider_memo')#定义显示列
    search_fields = ('slider_content_ID','sequenceNo','context')#定义搜索列
    list_filter = ('slider_content_ID','sequenceNo','slider','dataX','dataY','dataZ','data_skew','data_rotate_x','data_rotate_y','data_rotate','data_scale','data_scale3d','data_perspective')#定义过滤器
    ordering = ('-sequenceNo',)#定义排序
    fields = ('slider_content_ID','slider_nav_id','sequenceNo','slider','slider_class','slider_title','dataX','dataY','dataZ','data_skew','data_rotate_x','data_rotate_y','data_rotate','data_scale','data_scale3d','data_perspective','syntax_highlighter','context','slider_memo')#定义字段顺序
    raw_id_fields = ('slider',)#某个一对多字段显示（多个结果）

class CCSAdmin(admin.ModelAdmin):
    list_display = ('CCS_ID','slider_ID','creation_datetime')#定义显示列
    search_fields = ('CCS_ID','slider_ID','creation_datetime')#定义搜索列
    list_filter = ('CCS_ID','slider_ID','creation_datetime')#定义过滤器
    ordering = ('-creation_datetime',)#定义排序
    fields = ('CCS_ID','slider_ID','creation_datetime')#定义字段顺序
    raw_id_fields = ('slider_ID',)#某个一对多字段显示（多个结果）

class SiteUserAdmin(admin.ModelAdmin):
    list_display = ('username','is_social','is_active','date_joined','signature','avatar_url','avatar_name')#定义显示列
    search_fields = ('username','is_social','is_active','date_joined')#定义搜索列
    list_filter = ('username','is_social','is_active','date_joined')#定义过滤器
    ordering = ('-date_joined',)#定义排序
    fields = ('username','is_social','is_active','date_joined','signature','avatar_url','avatar_name')#定义字段顺序

class InnerUserAdmin(admin.ModelAdmin):
    list_display = ('user','email','passwd','joinSocialUser')#定义显示列
    search_fields = ('user','email','passwd','joinSocialUser')#定义搜索列
    list_filter = ('user','email','passwd','joinSocialUser')#定义过滤器
    filter_horizontal = ('friends','intersting_tags')#某个多对多字段显示（多个结果），注意此字段的verbose_name是中文时要使用.decode('utf8')显示，否则显示不出过滤器控件
    fields = ('user','email','passwd','joinSocialUser')#定义字段顺序
    raw_id_fields = ('friends','intersting_tags')#某个一对多字段显示（多个结果）

class SocialUserAdmin(admin.ModelAdmin):
    list_display = ('user','site_uid','site_name')#定义显示列
    search_fields = ('user','site_uid','site_name')#定义搜索列
    list_filter = ('user','site_uid','site_name')#定义过滤器
    fields = ('user','site_uid','site_name')#定义字段顺序

class UserFriendsAdmin(admin.ModelAdmin):
    list_display = ('source','target','comment','date_joined')#定义显示列
    search_fields = ('source','target','comment','date_joined')#定义搜索列
    list_filter = ('source','target','comment','date_joined')#定义过滤器
    fields = ('source','target','comment','date_joined')#定义字段顺序
    raw_id_fields = ('source','target')#某个一对多字段显示（多个结果）

#admin.site.register(OauthType,OauthAdmin)
#admin.site.register(Member,MemberAdmin)

admin.site.register(Tag,TagAdmin)
admin.site.register(Slider,SliderAdmin)
admin.site.register(Slider_Status,StatusAdmin)
admin.site.register(Slider_Gallery,GalleryAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Slider_Content,ContentAdmin)
admin.site.register(Content_Class_Style,CCSAdmin)

admin.site.register(SiteUser,SiteUserAdmin)
admin.site.register(InnerUser,InnerUserAdmin)
admin.site.register(SocialUser,SocialUserAdmin)
admin.site.register(UserFriends,UserFriendsAdmin)