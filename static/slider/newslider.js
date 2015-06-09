
Array.prototype.move = function (old_index, new_index)
{//thanks for http://stackoverflow.com/questions/5306680/move-an-array-element-from-one-array-position-to-another
    /*Which should account for things like [1, 2, 3, 4, 5].move(-1, -2) properly (move the last element to the second to last place). 
    Result for that should be [1, 2, 3, 5, 4].
    Either way, in your original question, you would do arr.move(0, 2) for a after c. For d before b, you would do arr.move(3, 1).*/
    while (old_index < 0)
    {
        old_index += this.length;
    }
    while (new_index < 0)
    {
        new_index += this.length;
    }
    if (new_index >= this.length)
    {
        var k = new_index - this.length;
        while ((k--) + 1)
        {
            this.push(undefined);
        }
    }
    this.splice(new_index, 0, this.splice(old_index, 1)[0]);
    return this; // for testing purposes
};
//注意，OBJ控制localstorage，localstorage控制thumbnail

window.onload = function ()
{
    if (!window.localStorage["sliders"])
    {//不存在用户以前编辑未保存的幻灯片
        slider.sliderOBJ.push(slider.createNewPage());
        window.localStorage["sliders"] = slider.stringifySliderOBJ();
        window.localStorage["choisesyntax"] = "plain";
    }
    else
    {//存在，显示
        var sliders = JSON.parse("[" + window.localStorage["sliders"] + "]");
        for (var i = 0; i < sliders.length; i++)
        {
            slider.sliderOBJ.push(sliders[i]);//把已存在的缓存对象存入到slider对象
        }
        slider.initSlider();//根据slider对象生成缩略图
    }
}
var moveMonitor = {
    _move: false//移动标记
    , _x: null
    , _y: null//鼠标离控件左上角的相对位置
    , thisLI: null
    , couldDrop: false
    , timeoutMoving: { fun: null, delay: 300 }

}
//+++++++++++++++++++++++++++++++++++++++++++++slider controller begin+++++++++++++++++++++++++++++++++++++++++++++
var slider = {
    sliderOBJ: []
    , index: 0
    , templateProfile: {
        rotate_up: { DataX: 0, DataY: 800, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 120, Data_rotate_z: 0, Data_scale: 1, name: '螺旋上升' }//螺旋上升
        , rotate_down: { DataX: 0, DataY: -800, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 120, Data_rotate_z: 0, Data_scale: 1, name: '螺旋下降' }//螺旋下降
        , rotate_left: { DataX: 1010, DataY: 0, DataZ: 0, Data_rotate_x: 120, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1, name: '向右滚动' }//向右滚动
        , rotate_right: { DataX: -1010, DataY: 0, DataZ: 0, Data_rotate_x: 120, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1, name: '向左滚动' }//向左滚动
        , rotate_closer: { DataX: 0, DataY: 0, DataZ: -1500, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 45, Data_scale: 0, name: '螺旋靠近' }//螺旋靠近
        , rotate_away: { DataX: 0, DataY: 0, DataZ: 1500, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 45, Data_scale: 0, name: '螺旋远离' }//螺旋远离

        , movefrom_left: { DataX: 1500, DataY: 0, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '左侧滑入' }//左侧滑入
        , movefrom_right: { DataX: -1500, DataY: 0, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '右侧滑入' }//右侧滑入
        , movefrom_top: { DataX: 0, DataY: 1500, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '上部滑入' }//上部滑入
        , movefrom_bottom: { DataX: 0, DataY: -1500, DataZ: 0, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '下部滑入' }//下部滑入
        , movefrom_away: { DataX: 0, DataY: 0, DataZ: 1500, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '靠近' }//靠近
        , movefrom_near: { DataX: 0, DataY: 0, DataZ: -1500, Data_rotate_x: 0, Data_rotate_y: 0, Data_rotate_z: 0, Data_scale: 1.5, name: '远离' }//远离
    }
    //, customTemplate: slider.templateProfile.movefrom_left
    , createNewPage: function (Slider_content_ID
            , Slider_nav_id
            , Slider_class
            , Slider_title
            , DataX
            , DataY
            , DataZ
            , Data_skew
            , Data_rotate_x
            , Data_rotate_y
            , Data_rotate
            , Data_scale
            , Data_scale3d
            , Data_perspective
            , Context
            , Slider_memo)
    {//新建一页幻灯片对象
        var sliderPage = {//存储所有的sliderPage对象
            _slider_content_ID: (Slider_content_ID == undefined || Slider_content_ID == null || Slider_content_ID == "" ? Date.parse(new Date()) : Slider_content_ID)//id
            , _slider_nav_id: (Slider_nav_id == undefined || Slider_nav_id == null || Slider_nav_id == "" ? "" : Slider_nav_id)//class
            , _slider_class: (Slider_class == undefined || Slider_class == null || Slider_class == "" ? "step" : Slider_class)//class
            , _slider_title: (Slider_title == undefined || Slider_title == null || Slider_title == "" ? "新建幻灯片" : Slider_title)//标题
            , _dataX: (DataX == undefined || DataX == null || DataX == "" ? slider.templateProfile.rotate_left.DataX : DataX)  //translate3d平移分量
            , _dataY: (DataY == undefined || DataY == null || DataY == "" ? slider.templateProfile.rotate_left.DataY : DataY)  //translate3d平移分量
            , _dataZ: (DataZ == undefined || DataZ == null || DataZ == "" ? slider.templateProfile.rotate_left.DataZ : DataZ)  //translate3d平移分量
            , _data_skew: (Data_skew == undefined || Data_skew == null || Data_skew == "" ? 0 : Data_skew)//X轴缩放数值
            , _data_rotate_x: (Data_rotate_x == undefined || Data_rotate_x == null || Data_rotate_x == "" ? slider.templateProfile.rotate_left.Data_rotate_x : Data_rotate_x)//x轴旋转
            , _data_rotate_y: (Data_rotate_y == undefined || Data_rotate_y == null || Data_rotate_y == "" ? slider.templateProfile.rotate_left.Data_rotate_y : Data_rotate_y)//y轴旋转
            , _data_rotate: (Data_rotate == undefined || Data_rotate == null || Data_rotate == "" ? slider.templateProfile.rotate_left.Data_rotate_z : Data_rotate)//旋转
            , _data_scale: (Data_scale == undefined || Data_scale == null || Data_scale == "" ? slider.templateProfile.rotate_left.Data_scale : Data_scale)//缩放
            , _data_scale3d: (Data_scale3d == undefined || Data_scale3d == null || Data_scale3d == "" ? 0 : Data_scale3d)//3d缩放
            , _data_perspective: (Data_perspective == undefined || Data_perspective == null || Data_perspective == "" ? 0 : Data_perspective)//视距视角,暂不实现
            , _context: (Context == undefined || Context == null || Context == "" ? "<p class='defaultStyle'>此处编辑您的内容</p>" : Context)//幻灯片内容
            , _slider_memo: (Slider_memo == undefined || Slider_memo == null || Slider_memo == "" ? "简要说明" : Slider_memo)//备注
        };
        sliderPage.updateContext = function (_slider_memo)
        {
            if (_slider_content_ID)
                sliderPage._slider_memo = _slider_memo;
        }
        , sliderPage.update = function (
            _slider_content_ID
            , _slider_nav_id
            , _slider_class
            , _slider_title
            , _dataX
            , _dataY
            , _dataZ
            , _data_skew
            , _data_rotate_x
            , _data_rotate_y
            , _data_rotate
            , _data_scale
            , _data_scale3d
            , _data_perspective
            , _context
            , _slider_memo
            )
        {
            if (_slider_content_ID) sliderPage._slider_content_ID = _slider_content_ID;
            if (_slider_nav_id) sliderPage._slider_nav_id = _slider_nav_id;
            if (_slider_class) sliderPage._slider_class = _slider_class;
            if (_slider_title) sliderPage._slider_title = _slider_title;
            if (_dataX) sliderPage._dataX = _dataX;
            if (_dataY) sliderPage._dataY = _dataY;
            if (_dataZ) sliderPage._dataZ = _dataZ;
            if (_data_skew) sliderPage._data_skew = _data_skew;
            if (_data_rotate_x) sliderPage._data_rotate_x = _data_rotate_x;
            if (_data_rotate_y) sliderPage._data_rotate_y = _data_rotate_y;
            if (_data_rotate) sliderPage._data_rotate = _data_rotate;
            if (_data_scale) sliderPage._data_scale = _data_scale;
            if (_data_scale3d) sliderPage._data_scale3d = _data_scale3d;
            if (_data_perspective) sliderPage._data_perspective = _data_perspective;
            if (_context) sliderPage._context = _context;
            if (_slider_content_ID) sliderPage._slider_memo = _slider_memo;
        };
        return sliderPage;
    }
    , syncTemplateData: function (templateData)
    {//选中模板选项时同步数据和显示
        //同步数据
        this.sliderOBJ[this.index]._dataX = templateData.DataX;
        this.sliderOBJ[this.index]._dataY = templateData.DataY;
        this.sliderOBJ[this.index]._dataZ = templateData.DataZ;
        this.sliderOBJ[this.index]._data_rotate_x = templateData.Data_rotate_x;
        this.sliderOBJ[this.index]._data_rotate_y = templateData.Data_rotate_y;
        this.sliderOBJ[this.index]._data_rotate_z = templateData.Data_rotate_z;
        this.sliderOBJ[this.index]._data_scale = templateData.Data_scale;

        window.localStorage["sliders"] = this.stringifySliderOBJ();

        //同步显示
        rangers.rotate.setValue(templateData.Data_rotate);
        rangers.rotate_x.setValue(templateData.Data_rotate_x);
        rangers.rotate_y.setValue(templateData.Data_rotate_y);
        rangers.translate_z.setValue(templateData.DataZ);
        rangers.translate_x.setValue(templateData.DataX);
        rangers.translate_y.setValue(templateData.DataY);
        rangers.scale.setValue(templateData.Data_scale);
    }
    , pickThumbByIndex: function ()
    {//根据当前下标选择某一缩略图
        $("#titleController input").val(this.sliderOBJ[this.index]._slider_title);
        $('#iptNavId').val(this.sliderOBJ[this.index]._slider_nav_id);
        $("#thumbnails dt").find(".description").css({ "background-image": "" });
        $("#thumbnails dt").eq(this.index).find(".description").css({ "background-image": "url(/static/images/slected.png)" });
    }
    , refreshNavData: function (that)
    {//更新当前选中的数据对象，
        moveMonitor.thisLI = $(that).parents("dt");
        this.index = $("#thumbnails dt").index(moveMonitor.thisLI);

        this.pickThumbByIndex();
    }
    , addBeforeIndex: function (that)
    {//在某Index之前插入
        this.refreshNavData(that);
        this.sliderOBJ.splice(this.index, 0, this.createNewPage());
        window.localStorage["sliders"] = this.stringifySliderOBJ();

        $(that).parents("dt").before(this.returnThumbHTML(this.index, "before"));

        //var left = $("#thumbnails").scrollLeft();
        //$("#thumbnails").scrollLeft(left - 200)
        //$("#thumbnails").animate({ scrollLeft: left - 200 }, 300);

        this.pickThumbByIndex();
        //slider.index -= 1;//选中新插入的项目
    }
    , addAfterIndex: function (that)
    {//在某Index之后插入
        this.refreshNavData(that);
        this.index++;
        this.sliderOBJ.splice(this.index, 0, this.createNewPage());
        window.localStorage["sliders"] = this.stringifySliderOBJ();

        $(that).parents("dt").after(this.returnThumbHTML(this.index, "after"));

        var left = $("#thumbnails").scrollLeft();
        //$("#thumbnails").scrollLeft(left + 200)
        $("#thumbnails").animate({ scrollLeft: left + 200 }, 300);
        this.pickThumbByIndex();
        //slider.index += 1;//选中新插入的项目
    }
    , moveOldItoNewI: function (new_index)
    {//把旧位置的元素移动到新位置
        this.sliderOBJ.move(this.index, new_index);//排序

        window.localStorage["sliders"] = this.stringifySliderOBJ();//同步数据
        this.index = new_index;//选中
        this.initSlider();//重新显示元素
    }
    , deleteSliderPageByIndex: function ()
    {//根据Index删除某页幻灯片
        //删除存储对象
        this.sliderOBJ.splice(this.index, 1);
        window.localStorage["sliders"] = this.stringifySliderOBJ();

        //删除页面元素
        var sliderPage = $("#thumbnails dt").eq(this.index)
        var inserPos = sliderPage.next()
        sliderPage.remove();
        inserPos.remove();

        //更新当前选择项目
        var that = null;
        //前边有元素时选前边的，没有的话选后边的，都没有不选择
        //console.log("slider.index = " + slider.index);
        if (this.index - 1 >= 0)
        {
            that = $("#thumbnails dt").eq(this.index - 1).find(".thumbnail");
        }
        else if (this.index + 1 > 0)
        {
            that = $("#thumbnails dt").eq(this.index).find(".thumbnail");
        }
        else
        {
            return false;
        }
        this.refreshNavData(that);
    }
    , returnThumbHTML: function (index, pos)
    {//根据OBJ对象获取缩略图HTML
        var thumbnailsHTML = "";
        for (var i = (index == undefined ? 0 : index) ; i < (index == undefined ? slider.sliderOBJ.length : parseInt(index) + 1) ; i++)
        {
            if (pos == "after" || index == undefined)
            {//之后插入或全部生成（只生成提供index下标的图）
                thumbnailsHTML += '<dd class="inserPos">&nbsp;</dd>';
            }
            thumbnailsHTML += '<dt class="span2" id="' + slider.sliderOBJ[i]._slider_content_ID + '">'
                                + '<div class="thumbnail">'
                                    + '<div class="thumbtitlebar">' + slider.sliderOBJ[i]._slider_title + '</div>'
                                    + '<div class="insertL"></div>'
                                    + '<div class="description">' + slider.sliderOBJ[i]._slider_memo + '</div>'
                                    + '<div class="insertR"></div>'
                                    + '<img data-src="holder.js/125x1" alt="" src="/static/images/125x1.png">'
                                + '</div>'
                            + '</dt>';
            if (pos == "before" && index != undefined)
            {//之前插入且不是全部生成（只生成提供index下标的图）
                thumbnailsHTML += '<dd class="inserPos">&nbsp;</dd>';
            }

        }
        if (thumbnailsHTML != "" && index == undefined)
        {//生成全部（有内容，并且没有传递下标位置参数）
            thumbnailsHTML += '<dd class="inserPos">&nbsp;</dd>';
        }
        return thumbnailsHTML;
    }
    , initSlider: function ()
    {//根据slider对象生成缩略图
        var thumbnailsHTML = this.returnThumbHTML();
        if (thumbnailsHTML != "")
        {
            $("#thumbnails").html(thumbnailsHTML);
        }
        var that = $("#thumbnails dt").eq(this.index).find(".thumbnail");
        this.refreshNavData(that);
        this.setEditorHTML(this.sliderOBJ[this.index]._context);/*选中缩略图后编辑器显示对应内容*/
    }
    , stringifySliderOBJ: function ()
    {//所有对象内容字符串化
        var OBJstring = "";
        for (var i = 0; i < slider.sliderOBJ.length; i++)
        {
            if (i > 0)
            {
                OBJstring += ",";
            }
            OBJstring += '{"_slider_content_ID":"' + slider.sliderOBJ[i]._slider_content_ID + '"'
                + ',"_slider_nav_id":"' + slider.sliderOBJ[i]._slider_nav_id + '"'
                + ',"_slider_class":"' + slider.sliderOBJ[i]._slider_class + '"'
                + ',"_slider_title":"' + slider.sliderOBJ[i]._slider_title + '"'
                + ',"_dataX":"' + slider.sliderOBJ[i]._dataX + '"'
                + ',"_dataY":"' + slider.sliderOBJ[i]._dataY + '"'
                + ',"_dataZ":"' + slider.sliderOBJ[i]._dataZ + '"'
                + ',"_data_skew":"' + slider.sliderOBJ[i]._data_skew + '"'
                + ',"_data_rotate_x":"' + slider.sliderOBJ[i]._data_rotate_x + '"'
                + ',"_data_rotate_y":"' + slider.sliderOBJ[i]._data_rotate_y + '"'
                + ',"_data_rotate":"' + slider.sliderOBJ[i]._data_rotate + '"'
                + ',"_data_scale":"' + slider.sliderOBJ[i]._data_scale + '"'
                + ',"_data_scale3d":"' + slider.sliderOBJ[i]._data_scale3d + '"'
                + ',"_data_perspective":"' + slider.sliderOBJ[i]._data_perspective + '"'
                + ',"_context":"' + slider.sliderOBJ[i]._context + '"'
                + ',"_slider_memo":"' + slider.sliderOBJ[i]._slider_memo + '"' + '}';
            /*{'_slider_content_ID':'1370399488000','_slider_class':'asdfadasd','_slider_title':'新建幻灯片','_dataX':'test1','_dataY':'0','_dataZ':'0','_data_skew':'0','_data_rotate':'0','_data_rotate3d':'0','_data_scale':'0','_data_scale3d':'0','_data_perspective':'0','_context':'0','_slider_memo':'简要说明'}*/
        }
        return OBJstring.replace(/\s+/g, ' ');
    },
    getEditorHTML: function ()
    {
        return tinyMCE.EditorManager.get("editorcontainer").getContent();
    },
    setEditorHTML: function (context)
    {//编辑器显示指定HTML
        tinyMCE.get("editorcontainer").setContent(context)/*选中缩略图后编辑器显示对应内容*/
    },
    updateHTML: function (html)
    {//编辑器有内容更新时候触发，from textareas.js->setup->change
        this.sliderOBJ[this.index]._context = this.getEditorHTML().replace(/"/g, "'");
        window.localStorage["sliders"] = this.stringifySliderOBJ();
    }
    , btnRelease: function ()
    {
        if (!window.localStorage["sliderTitle"])
        {//还没有填写标题
            $('#myModal').modal();
            alert("请填写或选择标签，标签只能由汉字、字母或数字组成，每个标签之前以空格分隔");
            return false;
        }
        if (window.localStorage["sliderTitle"].length>=100)
        {
            alert("标题长度太长了，请限制在100个字符以内（其实我们认为100个也太长~）");
            return false;
        }
        //除了汉字字母数字以外的所有字符均替换成空格，然后将所有的空白字符删除
        if (!!($("#sliderTags").val().replace(/((?![\u4e00-\u9fa5a-zA-Z0-9]).)/g, " ").replace(/[\s]{1,10}/g, '')) == false)
        {
            alert("请填写或选择标签，标签只能由汉字、字母或数字组成，每个标签之前以空格分隔");
            $('#myModal').modal();
            return false;
        }
        this.release();
    }
    , release: function ()
    {
        var csrftoken = getCookie('csrftoken');
        $.post("/addNewSlider/", {
            date: new Date()
            , 'csrfmiddlewaretoken': csrftoken
            , sliderTitle: window.localStorage["sliderTitle"]
            , sliders: window.localStorage["sliders"]
            , tags: $("#sliderTags").val().replace(/((?![\u4e00-\u9fa5a-zA-Z0-9]).)/g, " ").replace(/[\s]{1,10}/g, ' ')////除了汉字字母数字以外的所有字符均替换成空格，然后将替换1-10个空白字符串为一个空格
        }, function (status)
        {
            if (status == "succeed")
            {
                //提示成功
                try
                {
                    $("#alertRlease").remove();
                } catch (e)
                {

                }
                $('#myModal').modal('hide').after('<div id="alertRlease" class="alert alert-success" style="display:none;"><button type="button" class="close" data-dismiss="alert">&times;</button><h4>发布成功</h4><p>发布成功</p></div>');//，您可以<a href="#">前往查看</a>或<a href="#">干点别的</a>
                $("#alertRlease").show().animate({ "opacity": "0" }, 10000, function ()
                {
                    $("#alertRlease").remove();
                });
                window.localStorage["sliderTitle"] = "";
                window.localStorage["sliders"] = "";
                window.sessionStorage["tags"] = "";
            }
            else
            {
                //提示错误
                try
                {
                    $("#alertRlease").remove();
                } catch (e)
                {

                }
                $('#myModal').modal('hide').after('<div id="alertRlease" class="alert alert-error" style="display:none;"><button type="button" class="close" data-dismiss="alert">&times;</button><h4>发布失败</h4><p>发布失败，请检查您的网络连接或者稍候再试，网页关闭后数据缓存在本地不会丢失。</p></div>');
                $("#alertRlease").show().animate({ "opacity": "0" }, 10000, function ()
                {
                    $("#alertRlease").remove();
                });
            }
        });
    }

    , insertCodeInit: function ()
    {
        $('#insertCode').modal();
    }
}
//+++++++++++++++++++++++++++++++++++++++++++++slider controller begin+++++++++++++++++++++++++++++++++++++++++++++

$(function ()
{
    //+++++++++++++++++++++++++++++++++++++++++++++moving div begin+++++++++++++++++++++++++++++++++++++++++++++
    $(document).on("mousedown", ".thumbtitlebar", function (e)
    {//开始拖动          原来层不变，复制一个层，跟随鼠标
        slider.refreshNavData(this);

        moveMonitor._move = true;
        var wleft = moveMonitor.thisLI.css("left");
        if (wleft == "auto")
        {
            moveMonitor._x = e.pageX;
        }
        else
        {
            moveMonitor._x = e.pageX - parseInt(moveMonitor.thisLI.css("left"));
        }
        moveMonitor._y = e.pageY - parseInt(moveMonitor.thisLI.css("top"));

        //高亮可以放置位置的标记
        $(".inserPos").not(moveMonitor.thisLI.next()).not(moveMonitor.thisLI.prev()).css({ "opacity": ".2" });

        moveMonitor.timeoutMoving.fun = setTimeout(function ()
        {//解决与click事件冲突，鼠标300ms没有抬起视为拖动，否则只有单击。对应于".thumbtitlebar"的mouseup事件的clearTimeout。
            //重新改变正在移动层的边框样式
            moveMonitor.thisLI.children().css({ "border": "1px dashed blue" });

            //正在移动的缩略图苗条一下
            moveMonitor.thisLI.animate({ "width": "10px", "opacity": ".1" }, 100)
        }, moveMonitor.timeoutMoving.delay);
        //
    });
    $(document).on("mouseup", ".thumbtitlebar", function ()
    {//拖动完成（放弃排序），释放鼠标          复制的层隐藏
        //使用代表层
        clearTimeout(moveMonitor.timeoutMoving.fun);//解决与click事件冲突
        $("#copycat").css({ "display": "none", "left": moveMonitor._x, "top": moveMonitor._y });
    });
    $("#copycat").mouseup(function ()
    {
        if (moveMonitor.couldDrop == true)
        {
            slider.deleteSliderPageByIndex();
        }
    });
    $(document).mousemove(function (e)
    {//正在移动鼠标          复制的层跟随鼠标
        if (moveMonitor._move == true)
        {
            var x = e.pageX - moveMonitor._x;//移动时根据鼠标位置计算控件左上角的绝对位置
            var y = e.pageY - moveMonitor._y;
            var top = 230 - ($(window).height() - e.pageY);
            //top = top > 95 ? 95 : top;
            if (top > 95)
            {
                $("#copycat").css({ "pointer-events": "none" });
            }
            else
            {
                $("#copycat").css({ "pointer-events": "" });
            }
            if (top <= 0)
            {//此时可以删除正在拖动的slider
                moveMonitor.couldDrop = true;
                $("#copycat").css({ "background-image": "url(/static/images/delete.png)", "background-color": "rgba(255,255,255,0)" });//控件新位置
            }
            else
            {
                moveMonitor.couldDrop = false;
                $("#copycat").css({ "background-image": "", "background-color": "#888" });//控件新位置
            }
            $("#copycat").css({ "display": "block", top: top, left: e.pageX - 60 });//控件新位置
        }
    }).mouseup(function ()
    {//拖动完成          控制标记
        moveMonitor._move = false;
        $("#copycat").css({ "display": "none", "left": moveMonitor._x, "top": moveMonitor._y });
        $(".inserPos").css({ "opacity": ".01" });//所有的可移动位置标记隐藏
        //重新改变正在移动层的边框样式
        if (moveMonitor.thisLI == null)
        {
            return false;
        }
        moveMonitor.thisLI.children().css({ "border": "" });
        //正在移动(苗条)的缩略图胖一下
        moveMonitor.thisLI.animate({ "width": "170", "opacity": "1" }, 100);
    });
    $(document).on("mouseenter", ".inserPos", function ()
    {//插入点显示
        //console.log("moveMonitor._move=" + moveMonitor._move);
        if (moveMonitor._move == true)
        {
            var isNeighbor = ((moveMonitor.thisLI[0]) == ($(this).next()[0]) || (moveMonitor.thisLI[0]) == ($(this).prev()[0]));//判断新位置不能是原来位置
            if (isNeighbor == false)
            {
                $(this).css({ "opacity": "1" });
            }
        }
    });
    $(document).on("mouseleave", ".inserPos", function ()
    {//插入点隐藏
        if (moveMonitor._move == true)
        {
            var isNeighbor = ((moveMonitor.thisLI[0]) == ($(this).next()[0]) || (moveMonitor.thisLI[0]) == ($(this).prev()[0]));//判断新位置不能是原来位置
            if (isNeighbor == false)
            {
                $(this).css({ "opacity": ".1" });
            }
        }
    });
    $(document).on("mouseup", ".inserPos", function ()
    {//拖动到新位置，把dom排序，把数据排序
        if (moveMonitor._move == true)
        {
            //var oldIndex = $("#thumbnails dt").index(moveMonitor.thisLI);//原来的index
            var newIndex = $("#thumbnails dd").index($(this));//要移动到的index
            if (newIndex == slider.index)
            {
                return false;
            }
            if (newIndex > slider.index)
            {
                newIndex -= 1;
            }
            //console.log(oldIndex + " to " + newIndex);
            slider.moveOldItoNewI(newIndex);
            //var isNeighbor = ((moveMonitor.thisLI[0]) == ($(this).next()[0]) || (moveMonitor.thisLI[0]) == ($(this).prev()[0]));//判断新位置不能是原来位置
            //if (isNeighbor == false)
            //{
            //}
        }
    });
    //+++++++++++++++++++++++++++++++++++++++++++++moving div end+++++++++++++++++++++++++++++++++++++++++++++


    //+++++++++++++++++++++++++++++++++++++++++++++insert slider begin+++++++++++++++++++++++++++++++++++++++++++++
    $(document).on("click", ".insertL,.insertR", function (e)
    {
        var classname = $(this).attr("class");
        //var Index = $("#thumbnails dt").index($(this).parents("dt"));
        if (classname == "insertL")
        {
            slider.addBeforeIndex(this);
        }
        else
        {
            slider.addAfterIndex(this);
        }
        return false;//阻止事件冒泡（".thumbnail"的click）
        e.preventDefault();
    });
    //+++++++++++++++++++++++++++++++++++++++++++++insert slider end+++++++++++++++++++++++++++++++++++++++++++++

    $("#updateTitle").click(function ()
    {
        slider.sliderOBJ[slider.index]._slider_title = $(this).prev().val().replace(/"/g, "'");

        //同步本地数据
        window.localStorage["sliders"] = slider.stringifySliderOBJ();
        //同步显示标题
        $("#thumbnails dt").eq(slider.index).find(".thumbtitlebar").html(slider.sliderOBJ[slider.index]._slider_title)
    });
    $(document).on("click", ".thumbnail", function (e)
    {//单击缩略图显示标题更改
        slider.refreshNavData(this);
        e.preventDefault();
    })

    var thumbnailsClick = { timeoutFun: { fun: null, clicksCount: 0, delay: 300 } }
    $("#thumbnails").on("click", function (e)
    {//选中缩略图后编辑器显示对应内容，双击显示对应演示编辑器
        thumbnailsClick.timeoutFun.clicksCount++;  //count clicks
        if (thumbnailsClick.timeoutFun.clicksCount === 1)
        {
            thumbnailsClick.timeoutFun.fun = setTimeout(function ()
            {//单击此处给编辑器赋值
                slider.setEditorHTML(slider.sliderOBJ[slider.index]._context);/*选中缩略图后编辑器显示对应内容*/
                thumbnailsClick.timeoutFun.clicksCount = 0;             //after action performed, reset counter

            }, thumbnailsClick.timeoutFun.delay);
        }
        else
        {//双击此处给编辑器赋值，显示对应的幻灯片编辑器和控制图标
            clearTimeout(thumbnailsClick.timeoutFun.fun);    //prevent single-click action
            slider.setEditorHTML(slider.sliderOBJ[slider.index]._context);/*选中缩略图后编辑器显示对应内容*/

            //正面显示，转到背面
            $("#sliderEditorController").addClass("flipToBack").removeClass("flipToFront");
            $("#sliderEditor").addClass("bounceInUp").removeClass("bounceOutDown");

            thumbnailsClick.timeoutFun.clicksCount = 0;             //after action performed, reset counter
        }
    }).on("dblclick", function (e)
    {
        e.preventDefault();  //cancel system double-click event
    }).on("mousewheel", function (event)
    {
        var left = $(this).scrollLeft();
        $(this).animate({ scrollLeft: left - (event.originalEvent.wheelDelta * 2) }, 10)

        event.preventDefault();
    });

    $("#sliderEditorController").click(function ()
    {
        if (!$(this).hasClass("flipToBack"))
        {//正面显示，转到背面
            $(this).addClass("flipToBack").removeClass("flipToFront");
            $("#sliderEditor").addClass("bounceInUp").removeClass("bounceOutDown");
            $("#titleController").addClass("floatOut");
        }
        else
        {
            $(this).addClass("flipToFront").removeClass("flipToBack");
            $("#sliderEditor").addClass("bounceOutDown").removeClass("bounceInUp");
            $("#titleController").removeClass("floatOut");
        }
    });


    //多选菜单 thanks for http://stackoverflow.com/questions/13022543/multi-select-twitter-bootstrap-dropdown
    /* Multi select - allow multiple selections */
    /* Allow click without closing menu */
    /* Toggle checked state and icon */
    $('.multicheck').click(function (e)
    {
        if ($(this).hasClass("enabledmulticheck"))
        {
            return false;
        }

        $(this).toggleClass("checked");
        $(this).find("span").toggleClass("icon-ok");

        var className = $(this).attr("value");
        var classes = $("#selectedClasses").val().replace(/  /gi, " ");
        if ($(this).hasClass("checked"))
        {
            $("#selectedClasses").val(classes + " " + className);
        }
        else
        {
            $("#selectedClasses").val(classes.replace(className, ""));
        }
        //同步数据
        slider.sliderOBJ[slider.index]._slider_class = $("#selectedClasses").val().replace(/  /gi, " ");
        window.localStorage["sliders"] = slider.stringifySliderOBJ();
        return false;
    });
    //多选菜单

    //range控件
    //console.log($('.sliderbar'));
    var rangers = {
        rotate: null
        , rotate_x: null
        , rotate_y: null
        , translate_z: null
        , translate_x: null
        , translate_y: null
        , scale: null
    }
    rangers.rotate = $("#rotate")
        .slider({ formater: function (value) { return "平面内" + (value >= 0 ? "顺时针" : "逆时针") + "旋转" + Math.abs(value) + "°"; } })
        .on("slideStop", function ()
        {
            var value = rangers.rotate.getValue()
            if (value != 0)
            {
                $("#label_rotate").addClass("label-info");
            }
            else
            {
                $("#label_rotate").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._data_rotate = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');
    rangers.rotate_x = $("#rotate_x")
        .slider({ formater: function (value) { return "横向" + (value >= 0 ? "顺时针" : "逆时针") + "旋转" + Math.abs(value) + "°"; } })
        .on("slideStop", function ()
        {
            var value = rangers.rotate_x.getValue()
            if (value != 0)
            {
                $("#label_rotate_x").addClass("label-info");
            }
            else
            {
                $("#label_rotate_x").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._data_rotate_x = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');
    rangers.rotate_y = $("#rotate_y")
        .slider({ formater: function (value) { return "纵向" + (value >= 0 ? "顺时针" : "逆时针") + "旋转" + Math.abs(value) + "°"; } })
        .on("slideStop", function ()
        {
            var value = rangers.rotate_y.getValue()
            if (value != 0)
            {
                $("#label_rotate_y").addClass("label-info");
            }
            else
            {
                $("#label_rotate_y").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._data_rotate_y = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');

    rangers.translate_z = $("#translate_z")
        .slider({ formater: function (value) { return (value >= 0 ? "远离" : "拉近") + Math.abs(value) + "像素"; } })
        .on("slideStop", function ()
        {
            var value = rangers.translate_z.getValue()
            if (value != 0)
            {
                $("#label_translate_z").addClass("label-info");
            }
            else
            {
                $("#label_translate_z").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._dataZ = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');
    rangers.translate_x = $("#translate_x")
        .slider({ formater: function (value) { return (value >= 0 ? "向左" : "向右") + "平移" + Math.abs(value) + "像素"; } })
        .on("slideStop", function ()
        {
            var value = rangers.translate_x.getValue()
            if (value != 0)
            {
                $("#label_translate_x").addClass("label-info");
            }
            else
            {
                $("#label_translate_x").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._dataX = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');
    rangers.translate_y = $("#translate_y")
        .slider({ formater: function (value) { return (value >= 0 ? "向上" : "向下") + "平移" + Math.abs(value) + "像素"; } })
        .on("slideStop", function ()
        {
            var value = rangers.translate_y.getValue()
            if (value != 0)
            {
                $("#label_translate_y").addClass("label-info");
            }
            else
            {
                $("#label_translate_y").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._dataY = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');

    rangers.scale = $("#scale")
        .slider({ formater: function (value) { return (value >= 0 ? "放大" : "缩小") + Math.abs(value) + "倍"; } })
        .on("slideStop", function ()
        {
            var value = rangers.scale.getValue()
            if (value != 0)
            {
                $("#label_scale").addClass("label-info");
            }
            else
            {
                $("#label_scale").removeClass("label-info");
            }
            //同步数据
            slider.sliderOBJ[slider.index]._data_scale = value;
            window.localStorage["sliders"] = slider.stringifySliderOBJ();
        }).data('slider');
    //range控件
    $('#iptNavId').blur(function ()
    {
        $('#iptNavId').popover("hide");
        //检测是否重复使用过此标记
        var value = $("#iptNavId").val();
        for (var i = 0; i < slider.sliderOBJ.length; i++)
        {
            if (i == slider.index)
            {
                if (slider.sliderOBJ[i]._slider_nav_id == value)
                {//跟之前的ID一样，不处理
                    return false;
                    break;
                }
                continue;
            }
            if (slider.sliderOBJ[i]._slider_nav_id == value)
            {//使用过，当前填写无效，使用之前的
                $('#iptNavId').val(slider.sliderOBJ[slider.index]._slider_nav_id);
                return false;
                break;
            }
        }
        //没有使用过
        slider.sliderOBJ[slider.index]._slider_nav_id = $("#iptNavId").val();
        window.localStorage["sliders"] = slider.stringifySliderOBJ();
    });
    $("#btnNavId").click(function ()
    {//input上按回车和按确定按钮后，同步数据
        var value = $("#iptNavId").val();

        //检测是否重复使用过此标记
        for (var i = 0; i < slider.sliderOBJ.length; i++)
        {
            if (i == slider.index)
            {
                if (slider.sliderOBJ[i]._slider_nav_id == value)
                {//跟之前的ID一样，不处理
                    return false;
                    break;
                }
                continue;
            }
            if (slider.sliderOBJ[i]._slider_nav_id == value)
            {//使用过，当前填写无效
                value = "setp-" + (parseInt(slider.index) + 1);
                $('#iptNavId')[0].select();
                $('#iptNavId').popover("show");
                return false;
                break;
            }
        }
        $('#iptNavId')[0].blur();
        //没有使用过
        slider.sliderOBJ[slider.index]._slider_nav_id = $("#iptNavId").val();
        window.localStorage["sliders"] = slider.stringifySliderOBJ();
    });
    $("#template_details a").click(function ()
    {
        var template = $(this).attr("id");
        var text = $(this).text();
        if (!template)
        {//没有选择
            $("#choisen").text("");
            return false;
        }
        var templateProfile = eval("slider.templateProfile." + template);
        slider.syncTemplateData(templateProfile);
        $("#choisen").text("（" + text + "）");
    });

    var detailsClick = { timeoutFun: { fun: null, clicksCount: 0, delay: 200 } }
    $("#detailsMan").on("click", function (e)
    {//选中缩略图后编辑器显示对应内容，双击显示对应演示编辑器
        detailsClick.timeoutFun.clicksCount++;  //count clicks
        if (detailsClick.timeoutFun.clicksCount === 1)
        {
            detailsClick.timeoutFun.fun = setTimeout(function ()
            {//单击此处给编辑器赋值
                detailsClick.timeoutFun.clicksCount = 0;             //after action performed, reset counter

            }, detailsClick.timeoutFun.delay);
        }
        else
        {//双击此处隐藏过渡编辑器
            detailsClick.timeoutFun.clicksCount = 0;
            $("#sliderEditorController").click();
        }
    }).on("dblclick", function (e)
    {
        e.preventDefault();  //cancel system double-click event
    });


    $("#sliderTags").on("change", function (e)
    {
        var tags = $(this).val().replace(/((?![\u4e00-\u9fa5a-zA-Z0-9=]).)/g, " ").replace(/[\s]{1,10}/g, ' ').replace(/\s+/g, " ");
        $(this).val(tags);
        $('#myTags input').iCheck('uncheck');
        var tagArr = tags.split(" ");
        for (var i = 0; i < tagArr.length; i++)
        {
            console.log(tagArr[i]);
            $("#myTags div:contains('" + tagArr[i] + "')").find("input").iCheck('check');
        }
        e.preventDefault();
    }).on("keyup", function ()
    {
        var sliderTags = $("#sliderTags").val();
        $("#sliderTags").val(sliderTags.replace(/((?![\u4e00-\u9fa5a-zA-Z0-9=]).)/g, " ").replace(/[\s]{1,10}/g, ' '));
    });
    $("#iptSliderTitle").on("change", function (e)
    {
        $("#btnInputTitle").removeClass("disabled");
    });
    $("#btnInputTitle").on("click", function (e)
    {
        var title = $("#iptSliderTitle").val();
        if (!title)
        {
            $("#iptSliderTitle").focus();
            return false;
        }
        window.localStorage["sliderTitle"] = title;
        slider.release();
    });
    $("#btnInsertCode").on("click", function (e)
    {
        var code = "<pre class='brush: " + window.localStorage["choisesyntax"] + ";'>" + $("#mceNoEditor").val() + "</pre>";
        if (!($("#mceNoEditor").val()))
        {
            $("#mceNoEditor").focus();
            return false;
        }
        console.log(code);
        tinymce.activeEditor.execCommand('mceInsertContent', false, code);
    });
    $(".languagesSelector").on("click", function (e)
    {
        window.localStorage["choisesyntax"] = $(this).attr("for");
        $("#selectedLanguage").html("已选择：" + window.localStorage["choisesyntax"] + "配置");
    });

    $('#myTags input').each(function ()
    {
        var self = $(this),
          label = self.next(),
          label_text = label.text();

        label.remove();
        self.iCheck({
            checkboxClass: 'icheckbox_line-blue',
            radioClass: 'iradio_line-blue',
            insert: '<div class="icheck_line-icon"></div>' + label_text,
            uncheckedClass: 'unchecked',
            //checkboxClass: 'icheckbox'
        });
    }).on('ifChecked', function (event)
    {//选中
        var tags = $("#sliderTags").val();
        var text = $(this).parent().text();
        $("#sliderTags").val((tags + " " + text).replace(/[\s]{1,10}/g, ' '));//替换1-10个空白字符串为一个空格
    }).on('ifUnchecked', function (event)
    {//取消
        var tags = $("#sliderTags").val();
        var tag = $(this).parent().text();
        tags = tags.replace(tag, '');
        $("#sliderTags").val(tags.replace(/[\s]{1,10}/g, ' '));//替换1-10个空白字符串为一个空格
    });
});