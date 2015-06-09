manage.py test filebrowser错误解决方法：

C:\Users\Administrator\Dropbox\project\Django\webslider>manage.py test filebrowser
Creating Test for the FileBrowser site: filebrowser
Creating test database for alias 'default'...
...........FF....FE
======================================================================
ERROR: runTest (filebrowser.tests.sites.TestSite_filebrowser)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Python27\lib\site-packages\filebrowser\tests\sites.py", line 233, inrunTest
    test_browse(self)
  File "C:\Python27\lib\site-packages\filebrowser\tests\sites.py", line 40, in test_browse
    response = test.c.get(url)
  File "C:\Python27\lib\site-packages\django\test\client.py", line 439, in get
    response = super(Client, self).get(path, data=data, **extra)
  File "C:\Python27\lib\site-packages\django\test\client.py", line 244, in get
    return self.request(**r)
  File "C:\Python27\lib\site-packages\django\core\handlers\base.py", line 111, in get_response
    response = callback(request, *callback_args, **callback_kwargs)
  File "C:\Python27\lib\site-packages\filebrowser\decorators.py", line 23, in decorator
    raise ImproperlyConfigured, _("Error finding Upload-Folder (MEDIA_ROOT + DIRECTORY). Maybe it does not exist?")
ImproperlyConfigured: Error finding Upload-Folder (MEDIA_ROOT + DIRECTORY). Maybe it does not exist?

配置MEDIA_ROOT：MEDIA_ROOT = os.path.join(HERE , 'static/media-files/').replace('\\','/') 
建立需要的目录：static/media-files/
查看DIRECTORY配置（C:\Python27\Lib\site-packages\filebrowser\settings.py）的28行：DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')
建立需要的目录：static/media-files/uploads/


======================================================================
FAIL: test_directory (filebrowser.tests.settings.SettingsTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Python27\lib\site-packages\filebrowser\tests\settings.py", line 29, in test_directory
    self.assertEqual(os.path.exists(os.path.join(MEDIA_ROOT,DIRECTORY)), 1)
AssertionError: False != 1

配置MEDIA_ROOT：MEDIA_ROOT = os.path.join(HERE , 'static/media-files/').replace('\\','/') 
建立需要的目录：static/media-files/
查看DIRECTORY配置（C:\Python27\Lib\site-packages\filebrowser\settings.py）的28行：DIRECTORY = getattr(settings, "FILEBROWSER_DIRECTORY", 'uploads/')
建立需要的目录：static/media-files/uploads/

======================================================================
FAIL: test_media_root (filebrowser.tests.settings.SettingsTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Python27\lib\site-packages\filebrowser\tests\settings.py", line 23, in test_media_root
    self.assertEqual(os.path.exists(MEDIA_ROOT), 1)
AssertionError: False != 1
配置MEDIA_ROOT：MEDIA_ROOT = os.path.join(HERE , 'static/media-files/').replace('\\','/') 
建立需要的目录：static/media-files/

======================================================================
FAIL: test_versions_basedir (filebrowser.tests.settings.SettingsTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Python27\lib\site-packages\filebrowser\tests\settings.py", line 43, in test_versions_basedir
    self.assertEqual(os.path.exists(os.path.join(MEDIA_ROOT,VERSIONS_BASEDIR)),
1)
AssertionError: False != 1
配置MEDIA_ROOT：MEDIA_ROOT = os.path.join(HERE , 'static/media-files/').replace('\\','/') 
建立需要的目录：static/media-files/

----------------------------------------------------------------------
Ran 19 tests in 0.340s

FAILED (failures=3, errors=1)
Destroying test database for alias 'default'...

C:\Users\Administrator\Dropbox\project\Django\webslider>