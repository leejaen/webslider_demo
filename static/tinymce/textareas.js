tinyMCE.init({
    mode: "textareas"
    , height: 300
    , theme: "modern"
    , language: 'zh_CN'
    , editor_deselector: "mceNoEditor"
    , media_strict: false
    , theme_advanced_toolbar_location: "top"
    , theme_advanced_toolbar_align: "left"
    , valid_elements: "*[*]"
    , extended_valid_elements: ",pre[class]"//把div换成p
    //, invalid_elements: "script"
    //, forced_root_block: 'p'
    , plugins: "advlist autolink lists link image charmap print preview hr anchor pagebreak searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking save table contextmenu directionality emoticons template paste textcolor "
    , toolbar: "preview,undo,redo,cut,copy,paste,pastetext,pasteword,|,styleselect,fontselect,fontsizeselect,|,forecolor,backcolor,emoticons,|,alignleft,aligncenter,alignright,alignjustify,|,bold,italic,underline,strikethrough,link,unlink,anchor,image,media,cleanup,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,|,outdent,indent,blockquote,|,templates,styles,PageSetup,insertCode,|,myButton"
    , contextmenu: "paste | link image inserttable | cell row column deletetable"
    , setup: function (ed)
    {
        ed.on('change', function (ed, l)
        {
            try
            {
                if (slider.updateHTML)
                {
                    slider.updateHTML();
                }
            } catch (e)
            {

            }
        });
        //ed.on('focus', function (ed, evt)
        //{
        //    ed.getBody();
        //});
        ed.addButton('myButton', {
            text: '发布',
            icon: false,
            onclick: function ()
            {
                slider.btnRelease();
            }
        });
        ed.addButton('styles', {
            type: 'splitbutton',
            text: '使用样式',
            icon: false,
            onclick: function ()
            {
                slider.btnRelease();
            },
            menu: [{
                text: '引用', menu: [{ text: '左侧滑入', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_left; } }]
            }]
        });
        ed.addButton('PageSetup', {
            text: '页面设置',
            icon: false,
            onclick: function ()
            {
                alert("pagestyle,背景样式，前景样式……");
            }
        });
        ed.addButton('insertCode', {
            text: '插入代码',
            icon: false,
            onclick: function ()
            {
                slider.insertCodeInit();
            }
        });
        ed.addButton('templates', {
            type: 'splitbutton',
            text: '应用模板',
            icon: false,
            onclick: function ()
            {
                alert("当前使用模板：" + slider.customTemplate.name);
            },
            menu: [{
                text: '旋转', menu: [{ text: '螺旋上升', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_up; } }
                                    , { text: '螺旋下降', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_down; } }
                                    , { text: '向右滚动', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_right; } }
                                    , { text: '向左滚动', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_left; } }
                                    , { text: '螺旋靠近', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_closer; } }
                                    , { text: '螺旋远离', onclick: function () { slider.customTemplate = slider.templateProfile.rotate_away; } }]
            }, {
                text: '飞入', menu: [{ text: '左侧滑入', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_left; } }
                                    , { text: '右侧滑入', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_right; } }
                                    , { text: '上部滑入', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_top; } }
                                    , { text: '下部滑入', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_bottom; } }
                                    , { text: '靠近', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_away; } }
                                    , { text: '远离', onclick: function () { slider.customTemplate = slider.templateProfile.movefrom_near; } }]
            }]
        });
    }
});
//tinymce.create('tinymce.plugins.ExamplePlugin', {
//    init: function (ed, url)
//    {
//        // Register an example button
//        ed.addButton('example', {
//            title: 'example.desc',
//            onclick: function ()
//            {
//                // Display an alert when the user clicks the button
//                ed.windowManager.alert('Hello world!');
//            },
//            'class': 'bold' // Use the bold icon from the theme
//        });
//    }
//});