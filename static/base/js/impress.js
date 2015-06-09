/**
 * impress.js
 *
 * impress.js is a presentation tool based on the power of CSS3 transforms and transitions
 * in modern browsers and inspired by the idea behind prezi.com.
 *
 *
 * Copyright 2011-2012 Bartek Szopka (@bartaz)
 *
 * Released under the MIT and GPL Licenses.
 *
 * ------------------------------------------------
 *  author:  Bartek Szopka
 *  version: 0.5.3
 *  url:     http://bartaz.github.com/impress.js/
 *  source:  http://github.com/bartaz/impress.js/
 */

/*jshint bitwise:true, curly:true, eqeqeq:true, forin:true, latedef:true, newcap:true,
         noarg:true, noempty:true, undef:true, strict:true, browser:true */

// 好吧，你就是那种打破沙锅问到底的人
// 下面就是他的全部运行机制：
(function (document, window)
{
    'use strict';

    // HELPER FUNCTIONS
    // -------------------------------助手函数

    // 'pfx' 是个将标准的css属性名转换为对应参数的函数，它最终会为您使用的不同浏览器返回相应的属性版本。
    // 本代码由Modernizr http://www.modernizr.com/ 提供
    var pfx = (function ()
    {

        var style = document.createElement('dummy').style,  // 创建一个测试用元素
            prefixes = 'Webkit Moz O ms Khtml'.split(' '),  // 把可能的前缀都列出来
            memory = {};

        return function (prop)
        {  // 返回一个函数，这里实际上是创建了一个闭包，这样memory可以当作缓存用，提高性能
            if (typeof memory[prop] === "undefined")
            {  // 如果缓存没命中

                var ucProp = prop.charAt(0).toUpperCase() + prop.substr(1),    // 将目标属性首字母大写，因为css中是驼峰命名
                    props = (prop + ' ' + prefixes.join(ucProp + ' ') + ucProp).split(' ');   // 构造所有可能的属性，这里非常巧妙的使用了join。需要 注意的是join之后又加了一个ucProp，因为join只会添加n-1个属性，列表中最后一个元素并没有添加属性，所以最后需要加上一个ucProp。不太好理解，大家可以自己在 命令行里运行一下这行代码。

                memory[prop] = null;  // 初始化，个人感觉意义不是特别大，因为能运行到这里说明memory[prop]本来就没有值。
                for (var i in props)
                {    // 遍历所有构造好的属性
                    if (style[props[i]] !== undefined)
                    {    // 如果有这个属性，说明找到了正确的前缀
                        memory[prop] = props[i];  // 把这个正确的属性记录下来
                        break;  // 直接break
                    }
                }

            }

            return memory[prop];  // 返回这个属性
        };

    })();   // 注意这里直接调用了函数，生成闭包

    // 把Array-Like对象转换成真正的Array对象。由于Array-Like对象无法使用大部分Array对象的方法，所以必须转换过来才行。这是一个常用的方法，大家要记一下。Array-Like对象是什么呢？常见的就是querySelectAll的返回值。
    var arrayify = function (a)
    {
        return [].slice.call(a);
    };

    // 把props中的属性添加到el中，由于props中是标准属性，所以调用pfx来获取当前浏览器可用的带前缀的属性
    var css = function (el, props)
    {
        var key, pkey;
        for (key in props)
        {
            if (props.hasOwnProperty(key))
            {
                pkey = pfx(key);
                if (pkey !== null)
                {
                    el.style[pkey] = props[key];
                }
            }
        }
        return el;
    };

    // 转换数字，如果被转换的变量并不是数字就返回默认值fallback，如果没有传入fallback就返回0
    var toNumber = function (numeric, fallback)
    {
        return isNaN(numeric) ? (fallback || 0) : Number(numeric);
    };

    // 通过id获取元素
    var byId = function (id)
    {
        console.log("id="+id)
        return document.getElementById(id);
    };

    // 返回满足selector的第一元素
    var $ = function (selector, context)
    {
        context = context || document;  // 如果没有指定context就使用document作为context
        return context.querySelector(selector);
    };

    // 返回满足selector的所有元素
    var $$ = function (selector, context)
    {
        context = context || document;
        return arrayify(context.querySelectorAll(selector));  // 注意这里调用了arrayify，把qSA的返回值转换成Array对象
    };

    // 在el上触发eventName事件
    var triggerEvent = function (el, eventName, detail)
    {
        var event = document.createEvent("CustomEvent");    // 创建事件
        event.initCustomEvent(eventName, true, true, detail);   // 初始化事件，这里的detail是传入事件的参数，可以由用户自定义。我们在下面会看到如何使用
        el.dispatchEvent(event);    // 在el上触发事件
    };

    // 参数转字符串，不用多说了吧
    var translate = function (t)
    {
        return " translate3d(" + t.x + "px," + t.y + "px," + t.z + "px) ";
    };

    // 参数转字符串，如果传入了revert变量就反过来
    var rotate = function (r, revert)
    {
        var rX = " rotateX(" + r.x + "deg) ",
            rY = " rotateY(" + r.y + "deg) ",
            rZ = " rotateZ(" + r.z + "deg) ";

        return revert ? rZ + rY + rX : rX + rY + rZ;
    };

    // 参数转字符串
    var scale = function (s)
    {
        return " scale(" + s + ") ";
    };

    // 参数转字符串
    var perspective = function (p)
    {
        return " perspective(" + p + "px) ";
    };

    // 从hash获取元素
    var getElementFromHash = function ()
    {
        // 先从hash中获取id，再用id去获取元素
        return byId(window.location.hash.replace(/^#\/?/, ""));
    };

    // 计算scale，主要用于窗口resize的时候调整canvas大小
    var computeWindowScale = function (config)
    {
        var hScale = window.innerHeight / config.height,
            wScale = window.innerWidth / config.width,
            scale = hScale > wScale ? wScale : hScale;

        if (config.maxScale && scale > config.maxScale)
        {
            scale = config.maxScale;
        }

        if (config.minScale && scale < config.minScale)
        {
            scale = config.minScale;
        }

        return scale;
    };

    // 查看是否支持impress需要的css3属性
    var body = document.body;

    var ua = navigator.userAgent.toLowerCase(); // 获取用户浏览器信息
    var impressSupported =
                          // 需要支持3D抓好
                           (pfx("perspective") !== null) &&

                          // 以及classList和dataset，classList的作用就是操作元素的类，dataset是获取用户设置的用'data-'开头的数据比如
                           (body.classList) &&
                           (body.dataset) &&

                          // 由于这些设备对3D效果支持并不好，所以过滤他们
                           (ua.search(/(iphone)|(ipod)|(android)/) === -1);

    if (!impressSupported)
    {    // 如果不支持impress，那就加上" impress-not-supported "类
        // 注意这里的细节，由于不知道是否支持classList，所以使用className来操作元素的类
        body.className += " impress-not-supported ";
    } else
    {    // 如果支持就加上"impress-supported"类
        body.classList.remove("impress-not-supported");
        body.classList.add("impress-supported");
    }

    // 全局变量
    var roots = {};

    // 默认设置
    var defaults = {
        width: 1024,
        height: 768,
        maxScale: 1,
        minScale: 0,

        perspective: 1000,

        transitionDuration: 1000
    };

    // 没用的函数
    var empty = function () { return false; };

    // impress对象，注意绑定到了window上，成为全局变量
    var impress = window.impress = function (rootId)
    {

        // 如果不支持impress，返回什么用都没有的那个函数
        if (!impressSupported)
        {
            return {
                init: empty,
                goto: empty,
                prev: empty,
                next: empty
            };
        }

        rootId = rootId || "impress";   // js中很常见的赋默认值的方法

        // 如果已经初始化过了，那就直接返回
        if (roots["impress-root-" + rootId])
        {
            return roots["impress-root-" + rootId];
        }

        // 所有step的data
        var stepsData = {};

        // 当前活跃step，也就是当前显示的step
        var activeStep = null;

        // canvas的当前状态
        var currentState = null;

        // step元素数组
        var steps = null;

        // 配置项
        var config = null;

        // 窗口scale
        var windowScale = null;

        // 根元素，也就是canvas画布的父元素
        var root = byId(rootId);
        var canvas = document.createElement("div"); // 注意，canvas只是一个div，和css3的canvas没有任何属性
        canvas.id = "impressCanvas"
        var initialized = false;    // 标记是否已经初始化过

        // 上一次进入的step
        var lastEntered = null;

        // 进入step的时候触发这个事件
        var onStepEnter = function (step)
        {
            if (lastEntered !== step)
            {     // 但是如果目标step和上一次进入的step相同的话是不会触发的
                triggerEvent(step, "impress:stepenter");
                lastEntered = step;
            }
        };

        // 离开step的时候触发这个事件，这个和stepenter事件成对出现，每次切换step的时候先触发leave再触发enter
        var onStepLeave = function (step)
        {
            if (lastEntered === step)
            {     // 如果目标step和上一次进入的step相同才会触发，这里和stepenter那里的条件需要仔细理解一下
                triggerEvent(step, "impress:stepleave");
                lastEntered = null;
            }
        };

        // 从dataset中读取用户设定的属性并赋值给step，这个函数会被init()函数调用
        var initStep = function (el, idx)
        {
            var data = el.dataset,
                step = {
                    translate: {
                        x: toNumber(data.x),
                        y: toNumber(data.y),
                        z: toNumber(data.z)
                    },
                    rotate: {
                        x: toNumber(data.rotateX),
                        y: toNumber(data.rotateY),
                        z: toNumber(data.rotateZ || data.rotate)
                    },
                    scale: toNumber(data.scale, 1),
                    el: el
                };

            if (!el.id)
            {
                el.id = "step-" + (idx + 1);
            }

            stepsData["impress-" + el.id] = step;

            css(el, {
                position: "absolute",
                transform: "translate(-50%,-50%)" + // 这里的-50%不是太懂，貌似是为了让初始化过程更好看？不过初始化一般瞬间就完成了，也看不到。
                           translate(step.translate) +
                           rotate(step.rotate) +
                           scale(step.scale),
                transformStyle: "preserve-3d"
            });
        };

        // 初始化函数
        var init = function (flag)
        {
            if (initialized && flag !== "revise")
            {
                return;
            }    // 如果已经初始化过就返回
            // 这里设置viewport的原因是iPad有个bug，如果不设置的话iPad会卡。
            var meta = $("meta[name='viewport']") || document.createElement("meta");
            meta.content = "width=device-width, minimum-scale=1, maximum-scale=1, user-scalable=no";
            if (meta.parentNode !== document.head)
            {
                meta.name = 'viewport';
                document.head.appendChild(meta);
            }

            // 初始化配置对象
            var rootData = root.dataset;
            config = {
                width: toNumber(rootData.width, defaults.width),  // 注意这里toNumber函数的用法，第二个参数是默认值
                height: toNumber(rootData.height, defaults.height),
                maxScale: toNumber(rootData.maxScale, defaults.maxScale),
                minScale: toNumber(rootData.minScale, defaults.minScale),
                perspective: toNumber(rootData.perspective, defaults.perspective),
                transitionDuration: toNumber(rootData.transitionDuration, defaults.transitionDuration)
            };

            windowScale = computeWindowScale(config);     // 计算scale


            // 这里有点绕：先把所有step从root里放到canvas里，再把canvas放到root里。这样做的原因是，切换step的时候root负责缩放，canvas负责移动

            arrayify(root.childNodes).forEach(function (el)
            {
                canvas.appendChild(el);
            });
            root.appendChild(canvas);

            // documentElement就是html元素，设置他的初始高度
            document.documentElement.style.height = "100%";

            // 设置body的初始参数
            css(body, {
                height: "100%",
                overflow: "hidden"
            });

            // 设置root的初始参数
            var rootStyles = {
                position: "absolute",
                transformOrigin: "top left",
                transition: "all 0s ease-in-out",
                transformStyle: "preserve-3d"
            };

            css(root, rootStyles);  // 应用css属性
            css(root, {
                top: "50%",
                left: "50%",
                transform: perspective(config.perspective / windowScale) + scale(windowScale)
            });
            css(canvas, rootStyles);

            body.classList.remove("impress-disabled");  // 注意细节，由于不确定有没有，所以先remove一下
            body.classList.add("impress-enabled");

            // 初始化所有step，调用了initStep函数
            steps = $$(".step", root);
            steps.forEach(initStep);

            // 给canvas设置一个初始状态
            currentState = {
                translate: { x: 0, y: 0, z: 0 },
                rotate: { x: 0, y: 0, z: 0 },
                scale: 1
            };

            initialized = true;     // 标记已经初始化过

            triggerEvent(root, "impress:init", { api: roots["impress-root-" + rootId] }); // 触发init事件，注意这里传入的{api:...}就是对应创建事件时候的detail，后面会用到
        };

        // 获取step
        var getStep = function (step)
        {
            if (typeof step === "number")
            { // 如果参数是数字，说明是数组的序号，直接从数组中取
                step = step < 0 ? steps[steps.length + step] : steps[step];  // 注意这里是如何支持负数的，用长度相加就可以
            } else if (typeof step === "string")
            {  // 如果是字符串，说明参数是id，用byId函数获取
                step = byId(step);
            }
            return (step && step.id && stepsData["impress-" + step.id]) ? step : null;  // 如果都不是的话，那么参数本身就是一个元素，目的是判断参数是不是一个step，如果不是就返回null
        };

        // stepenter事件会用到这个，因为要先stepleave再stepenter，所以必须等stepleave完成后才能运行stepenter
        var stepEnterTimeout = null;

        // 切换到指定step
        var goto = function (el, duration)
        {

            if (!initialized || !(el = getStep(el)))
            {
                // 如果没初始化过或者el不是一个step就返回，注意这里对应上面的getStep函数，大家要好好理解。同时，这里还完成了对el的赋值，这也是js中很常见的用法
                return false;
            }

            // 这里详细解释一下，因为浏览器载入的时候有bug，即使设置了overflow:hidden，也有可能会滚动，所以强制滚动到（0，0）
            window.scrollTo(0, 0);

            var step = stepsData["impress-" + el.id];   // 获取step的数据

            if (activeStep)
            {     // 清除当前活跃step的标记
                activeStep.classList.remove("active");
                body.classList.remove("impress-on-" + activeStep.id);
            }
            window.sessionStorage.setItem("elid",(el.id));
            el.classList.add("active");     // 把目标step标记为活跃

            body.classList.add("impress-on-" + el.id);

            // 根据step数据计算canvas需要做什么变换
            var target = {
                rotate: {
                    x: -step.rotate.x,
                    y: -step.rotate.y,
                    z: -step.rotate.z
                },
                translate: {
                    x: -step.translate.x,
                    y: -step.translate.y,
                    z: -step.translate.z
                },
                scale: 1 / step.scale
            };

            // 这里需要注意！
            // 先用scale来判断要缩小还是要放大
            // 缩放和位置的移动是分开的，为了让这个动作更自然，有两种情况：
            // 如果要缩小，那么先执行缩放动作，再执行移动动作
            // 如果要放大，先执行移动动作，再执行缩放动作
            // 大家可以结合impress.js官方demo里面那个缩放的地方来理解一下，这样做可以让整个切换看起来舒服很多！
            // 到这里大家应该也明白了为什么要分成root和canvas，因为两个动作有一半时间是重叠的，所以必须分开才行。
            var zoomin = target.scale >= currentState.scale;

            duration = toNumber(duration, config.transitionDuration);
            var delay = (duration / 2);     // 这个delay就是两个动作之间的间隔时间

            // 如果el就是当前活跃step，那么可能是因为触发了resize事件，重新计算一下scale
            if (el === activeStep)
            {
                windowScale = computeWindowScale(config);
            }

            var targetScale = target.scale * windowScale;

            // 如果el不是当前活跃step，触发stepleave事件。如果el就是当前活跃step的话那根本就不用动，自己不用切换到自己。
            if (activeStep && activeStep !== el)
            {
                onStepLeave(activeStep);
            }

            // root负责缩放，canvas负责移动
            css(root, {
                // to keep the perspective look similar for different scales
                // we need to 'scale' the perspective, too
                transform: perspective(config.perspective / targetScale) + scale(targetScale),
                transitionDuration: duration + "ms",
                transitionDelay: (zoomin ? delay : 0) + "ms"
            });

            css(canvas, {
                transform: rotate(target.rotate, true) + translate(target.translate),
                transitionDuration: duration + "ms",
                transitionDelay: (zoomin ? 0 : delay) + "ms"
            });

            // 如果当前状态和目标状态完全一样，那么说明根本就不用变换，把delay设为0
            if (currentState.scale === target.scale ||
                (currentState.rotate.x === target.rotate.x && currentState.rotate.y === target.rotate.y &&
                 currentState.rotate.z === target.rotate.z && currentState.translate.x === target.translate.x &&
                 currentState.translate.y === target.translate.y && currentState.translate.z === target.translate.z))
            {
                delay = 0;
            }

            // 存储当前状态
            currentState = target;
            activeStep = el;

            // 延迟触发stepenter事件。注意延迟时间是duration+delay，duration是translate运行需要的时间，delay是因为缩放和移动的间隔时间，所以完成整个切换动作的时间是duration+delay
            window.clearTimeout(stepEnterTimeout);
            stepEnterTimeout = window.setTimeout(function ()
            {
                onStepEnter(activeStep);
            }, duration + delay);

            return el;
        };

        // 切换到上一个step
        var prev = function ()
        {
            var prev = steps.indexOf(activeStep) - 1;     // step的顺序是由他们在steps数组中的位置决定的
            prev = prev >= 0 ? steps[prev] : steps[steps.length - 1]; // 如果已经是第一个就切换到最后一个

            return goto(prev);  // 注意，这里调用goto
        };

        // 切换到下一个step
        var next = function ()
        {
            var next = steps.indexOf(activeStep) + 1;
            next = next < steps.length ? steps[next] : steps[0];    // 如果已经是最后一个就切换到第一个

            return goto(next);
        };

        // step有三种状态，future,past,present，present是当前活跃step，future是没显示过的step，past是显示过的step。这些标记的作用是让用户可以在css中设定对应的样式
        root.addEventListener("impress:init", function ()
        {   // 注意这里绑定到了init事件
            // STEP CLASSES
            steps.forEach(function (step)
            { // 开始全部是future
                step.classList.add("future");
            });

            root.addEventListener("impress:stepenter", function (event)
            {   // stepenter的时候标记present
                event.target.classList.remove("past");
                event.target.classList.remove("future");
                event.target.classList.add("present");
            }, false);

            root.addEventListener("impress:stepleave", function (event)
            {   // stepleave时候标记past
                event.target.classList.remove("present");
                event.target.classList.add("past");
            }, false);

        }, false);

        // 对hash的处理
        root.addEventListener("impress:init", function ()
        {

            // 上一个hash
            var lastHash = "";

            // 要用`#/step-id`而不是`#step-id`，因为后者在Chrome里运行时候会卡
            root.addEventListener("impress:stepenter", function (event)
            {
                window.location.hash = lastHash = "#/" + event.target.id;
            }, false);

            window.addEventListener("hashchange", function ()
            {
                // 因为进入step的时候hash会更新，所以为了防止无限goto，这里要加一个判断
                if (window.location.hash !== lastHash)
                {
                    goto(getElementFromHash());
                }
            }, false);

            // 初始化完毕后切换到当前hash指定的step或者第一个step
            goto(getElementFromHash() || steps[0], 0);
        }, false);

        body.classList.add("impress-disabled");     // 这里不太理解，好像没什么用。可能是为了标记impress对象构造已经结束？

        // 暴露四个API
        return (roots["impress-root-" + rootId] = {
            init: init,
            goto: goto,
            next: next,
            prev: prev
        });

    };

    // 暴露支持变量
    impress.supported = impressSupported;

})(document, window);

// 用于控制键盘事件、点击事件、触摸事件以及resize事件
(function (document, window)
{
    'use strict';

    // 一个代理函数，作用是延迟delay秒执行fn。
    var throttle = function (fn, delay)
    {
        var timer = null;
        return function ()
        {
            var context = this, args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function ()
            {
                fn.apply(context, args);
            }, delay);
        };
    };

    // 触发init事件时候绑定各种东西
    document.addEventListener("impress:init", function (event)
    {
        // 还记得吗？这里对应上面创建事件时候传入的detail，里面有api，所以我们不用再获取根对象
        var api = event.detail.api;

        // 绑定键盘事件，为了防止别的事件干扰，所以触发keydown时候禁止冒泡
        document.addEventListener("keydown", function (event)
        {
            if (event.keyCode === 9 || (event.keyCode >= 32 && event.keyCode <= 34) || (event.keyCode >= 37 && event.keyCode <= 40))
            {
                event.preventDefault();
            }
        }, false);

        // 松开按键时候触发事件

        document.addEventListener("keyup", function (event)
        {
            if (event.keyCode === 9 || (event.keyCode >= 32 && event.keyCode <= 34) || (event.keyCode >= 37 && event.keyCode <= 40))
            {
                switch (event.keyCode)
                {
                    case 33: // pg up
                    case 37: // left
                    case 38: // up
                        api.prev();    // 上一个step
                        break;
                    case 9:  // tab
                    case 32: // space
                    case 34: // pg down
                    case 39: // right
                    case 40: // down
                        api.next();    // 下一个step
                        break;
                }

                event.preventDefault();     // 禁止冒泡
            }
        }, false);

        // 处理点击链接事件，这个链接的地址可能是另一个step的地址，如果不手动处理的话浏览器会刷新页面
        document.addEventListener("click", function (event)
        {
            // 判断目标是不是一个链接元素a，由于页面上可能有很多层div，所以从下往上找直到找到一个a
            var target = event.target;
            while ((target.tagName !== "A") &&
                    (target !== document.documentElement))
            {
                target = target.parentNode;
            }

            if (target.tagName === "A")
            { // 如果找到了，
                var href = target.getAttribute("href");

                // 判断是不是step的地址
                if (href && href[0] === '#')
                {
                    target = document.getElementById(href.slice(1));
                }
            }

            if (api.goto(target))
            {   // 如果是step的地址就goto，如果不是那就不管了，冒泡传递上去
                event.stopImmediatePropagation();
                event.preventDefault();
            }
        }, false);

        // 如果点击的目标是一个step元素，那就goto过去
        document.addEventListener("click", function (event)
        {
            var target = event.target;
            // 从下往上找，找到第一个不活跃的step
            while (!(target.classList.contains("step") && !target.classList.contains("active")) &&
                    (target !== document.documentElement))
            {
                target = target.parentNode;
            }

            if (api.goto(target))
            {   // 如果目标是一个step那就goto，不是的话就不管了，冒泡传递上去
                event.preventDefault();
            }
        }, false);

        // 判断触摸屏幕区域
        document.addEventListener("touchstart", function (event)
        {
            if (event.touches.length === 1)
            {
                var x = event.touches[0].clientX,
                    width = window.innerWidth * 0.3,    // 可以看到，如果点击到左侧30%的屏幕就会判断是左
                    result = null;

                if (x < width)
                {
                    result = api.prev();
                } else if (x > window.innerWidth - width)
                {   // 如果点击到右侧30%的屏幕就会判断是右
                    result = api.next();
                }

                if (result)
                {   // 如果是左或者右，那就禁止冒泡。如果不是就传递上去
                    event.preventDefault();
                }
            }
        }, false);

        // 窗口大小变化的时候调用goto，对应goto中重新计算scale那里
        window.addEventListener("resize", throttle(function ()
        {
            // force going to active step again, to trigger rescaling
            api.goto(document.querySelector(".step.active"), 500);
        }, 250), false);

    }, false);

})(document, window);