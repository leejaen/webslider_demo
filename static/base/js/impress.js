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

// �ðɣ���������ִ���ɳ���ʵ��׵���
// �����������ȫ�����л��ƣ�
(function (document, window)
{
    'use strict';

    // HELPER FUNCTIONS
    // -------------------------------���ֺ���

    // 'pfx' �Ǹ�����׼��css������ת��Ϊ��Ӧ�����ĺ����������ջ�Ϊ��ʹ�õĲ�ͬ�����������Ӧ�����԰汾��
    // ��������Modernizr http://www.modernizr.com/ �ṩ
    var pfx = (function ()
    {

        var style = document.createElement('dummy').style,  // ����һ��������Ԫ��
            prefixes = 'Webkit Moz O ms Khtml'.split(' '),  // �ѿ��ܵ�ǰ׺���г���
            memory = {};

        return function (prop)
        {  // ����һ������������ʵ�����Ǵ�����һ���հ�������memory���Ե��������ã��������
            if (typeof memory[prop] === "undefined")
            {  // �������û����

                var ucProp = prop.charAt(0).toUpperCase() + prop.substr(1),    // ��Ŀ����������ĸ��д����Ϊcss�����շ�����
                    props = (prop + ' ' + prefixes.join(ucProp + ' ') + ucProp).split(' ');   // �������п��ܵ����ԣ�����ǳ������ʹ����join����Ҫ ע�����join֮���ּ���һ��ucProp����Ϊjoinֻ�����n-1�����ԣ��б������һ��Ԫ�ز�û��������ԣ����������Ҫ����һ��ucProp����̫����⣬��ҿ����Լ��� ������������һ�����д��롣

                memory[prop] = null;  // ��ʼ�������˸о����岻���ر����Ϊ�����е�����˵��memory[prop]������û��ֵ��
                for (var i in props)
                {    // �������й���õ�����
                    if (style[props[i]] !== undefined)
                    {    // �����������ԣ�˵���ҵ�����ȷ��ǰ׺
                        memory[prop] = props[i];  // �������ȷ�����Լ�¼����
                        break;  // ֱ��break
                    }
                }

            }

            return memory[prop];  // �����������
        };

    })();   // ע������ֱ�ӵ����˺��������ɱհ�

    // ��Array-Like����ת����������Array��������Array-Like�����޷�ʹ�ô󲿷�Array����ķ��������Ա���ת���������С�����һ�����õķ��������Ҫ��һ�¡�Array-Like������ʲô�أ������ľ���querySelectAll�ķ���ֵ��
    var arrayify = function (a)
    {
        return [].slice.call(a);
    };

    // ��props�е�������ӵ�el�У�����props���Ǳ�׼���ԣ����Ե���pfx����ȡ��ǰ��������õĴ�ǰ׺������
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

    // ת�����֣������ת���ı������������־ͷ���Ĭ��ֵfallback�����û�д���fallback�ͷ���0
    var toNumber = function (numeric, fallback)
    {
        return isNaN(numeric) ? (fallback || 0) : Number(numeric);
    };

    // ͨ��id��ȡԪ��
    var byId = function (id)
    {
        console.log("id="+id)
        return document.getElementById(id);
    };

    // ��������selector�ĵ�һԪ��
    var $ = function (selector, context)
    {
        context = context || document;  // ���û��ָ��context��ʹ��document��Ϊcontext
        return context.querySelector(selector);
    };

    // ��������selector������Ԫ��
    var $$ = function (selector, context)
    {
        context = context || document;
        return arrayify(context.querySelectorAll(selector));  // ע�����������arrayify����qSA�ķ���ֵת����Array����
    };

    // ��el�ϴ���eventName�¼�
    var triggerEvent = function (el, eventName, detail)
    {
        var event = document.createEvent("CustomEvent");    // �����¼�
        event.initCustomEvent(eventName, true, true, detail);   // ��ʼ���¼��������detail�Ǵ����¼��Ĳ������������û��Զ��塣����������ῴ�����ʹ��
        el.dispatchEvent(event);    // ��el�ϴ����¼�
    };

    // ����ת�ַ��������ö�˵�˰�
    var translate = function (t)
    {
        return " translate3d(" + t.x + "px," + t.y + "px," + t.z + "px) ";
    };

    // ����ת�ַ��������������revert�����ͷ�����
    var rotate = function (r, revert)
    {
        var rX = " rotateX(" + r.x + "deg) ",
            rY = " rotateY(" + r.y + "deg) ",
            rZ = " rotateZ(" + r.z + "deg) ";

        return revert ? rZ + rY + rX : rX + rY + rZ;
    };

    // ����ת�ַ���
    var scale = function (s)
    {
        return " scale(" + s + ") ";
    };

    // ����ת�ַ���
    var perspective = function (p)
    {
        return " perspective(" + p + "px) ";
    };

    // ��hash��ȡԪ��
    var getElementFromHash = function ()
    {
        // �ȴ�hash�л�ȡid������idȥ��ȡԪ��
        return byId(window.location.hash.replace(/^#\/?/, ""));
    };

    // ����scale����Ҫ���ڴ���resize��ʱ�����canvas��С
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

    // �鿴�Ƿ�֧��impress��Ҫ��css3����
    var body = document.body;

    var ua = navigator.userAgent.toLowerCase(); // ��ȡ�û��������Ϣ
    var impressSupported =
                          // ��Ҫ֧��3Dץ��
                           (pfx("perspective") !== null) &&

                          // �Լ�classList��dataset��classList�����þ��ǲ���Ԫ�ص��࣬dataset�ǻ�ȡ�û����õ���'data-'��ͷ�����ݱ���
                           (body.classList) &&
                           (body.dataset) &&

                          // ������Щ�豸��3DЧ��֧�ֲ����ã����Թ�������
                           (ua.search(/(iphone)|(ipod)|(android)/) === -1);

    if (!impressSupported)
    {    // �����֧��impress���Ǿͼ���" impress-not-supported "��
        // ע�������ϸ�ڣ����ڲ�֪���Ƿ�֧��classList������ʹ��className������Ԫ�ص���
        body.className += " impress-not-supported ";
    } else
    {    // ���֧�־ͼ���"impress-supported"��
        body.classList.remove("impress-not-supported");
        body.classList.add("impress-supported");
    }

    // ȫ�ֱ���
    var roots = {};

    // Ĭ������
    var defaults = {
        width: 1024,
        height: 768,
        maxScale: 1,
        minScale: 0,

        perspective: 1000,

        transitionDuration: 1000
    };

    // û�õĺ���
    var empty = function () { return false; };

    // impress����ע��󶨵���window�ϣ���Ϊȫ�ֱ���
    var impress = window.impress = function (rootId)
    {

        // �����֧��impress������ʲô�ö�û�е��Ǹ�����
        if (!impressSupported)
        {
            return {
                init: empty,
                goto: empty,
                prev: empty,
                next: empty
            };
        }

        rootId = rootId || "impress";   // js�кܳ����ĸ�Ĭ��ֵ�ķ���

        // ����Ѿ���ʼ�����ˣ��Ǿ�ֱ�ӷ���
        if (roots["impress-root-" + rootId])
        {
            return roots["impress-root-" + rootId];
        }

        // ����step��data
        var stepsData = {};

        // ��ǰ��Ծstep��Ҳ���ǵ�ǰ��ʾ��step
        var activeStep = null;

        // canvas�ĵ�ǰ״̬
        var currentState = null;

        // stepԪ������
        var steps = null;

        // ������
        var config = null;

        // ����scale
        var windowScale = null;

        // ��Ԫ�أ�Ҳ����canvas�����ĸ�Ԫ��
        var root = byId(rootId);
        var canvas = document.createElement("div"); // ע�⣬canvasֻ��һ��div����css3��canvasû���κ�����
        canvas.id = "impressCanvas"
        var initialized = false;    // ����Ƿ��Ѿ���ʼ����

        // ��һ�ν����step
        var lastEntered = null;

        // ����step��ʱ�򴥷�����¼�
        var onStepEnter = function (step)
        {
            if (lastEntered !== step)
            {     // �������Ŀ��step����һ�ν����step��ͬ�Ļ��ǲ��ᴥ����
                triggerEvent(step, "impress:stepenter");
                lastEntered = step;
            }
        };

        // �뿪step��ʱ�򴥷�����¼��������stepenter�¼��ɶԳ��֣�ÿ���л�step��ʱ���ȴ���leave�ٴ���enter
        var onStepLeave = function (step)
        {
            if (lastEntered === step)
            {     // ���Ŀ��step����һ�ν����step��ͬ�Żᴥ���������stepenter�����������Ҫ��ϸ���һ��
                triggerEvent(step, "impress:stepleave");
                lastEntered = null;
            }
        };

        // ��dataset�ж�ȡ�û��趨�����Բ���ֵ��step����������ᱻinit()��������
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
                transform: "translate(-50%,-50%)" + // �����-50%����̫����ò����Ϊ���ó�ʼ�����̸��ÿ���������ʼ��һ��˲�������ˣ�Ҳ��������
                           translate(step.translate) +
                           rotate(step.rotate) +
                           scale(step.scale),
                transformStyle: "preserve-3d"
            });
        };

        // ��ʼ������
        var init = function (flag)
        {
            if (initialized && flag !== "revise")
            {
                return;
            }    // ����Ѿ���ʼ�����ͷ���
            // ��������viewport��ԭ����iPad�и�bug����������õĻ�iPad�Ῠ��
            var meta = $("meta[name='viewport']") || document.createElement("meta");
            meta.content = "width=device-width, minimum-scale=1, maximum-scale=1, user-scalable=no";
            if (meta.parentNode !== document.head)
            {
                meta.name = 'viewport';
                document.head.appendChild(meta);
            }

            // ��ʼ�����ö���
            var rootData = root.dataset;
            config = {
                width: toNumber(rootData.width, defaults.width),  // ע������toNumber�������÷����ڶ���������Ĭ��ֵ
                height: toNumber(rootData.height, defaults.height),
                maxScale: toNumber(rootData.maxScale, defaults.maxScale),
                minScale: toNumber(rootData.minScale, defaults.minScale),
                perspective: toNumber(rootData.perspective, defaults.perspective),
                transitionDuration: toNumber(rootData.transitionDuration, defaults.transitionDuration)
            };

            windowScale = computeWindowScale(config);     // ����scale


            // �����е��ƣ��Ȱ�����step��root��ŵ�canvas��ٰ�canvas�ŵ�root���������ԭ���ǣ��л�step��ʱ��root�������ţ�canvas�����ƶ�

            arrayify(root.childNodes).forEach(function (el)
            {
                canvas.appendChild(el);
            });
            root.appendChild(canvas);

            // documentElement����htmlԪ�أ��������ĳ�ʼ�߶�
            document.documentElement.style.height = "100%";

            // ����body�ĳ�ʼ����
            css(body, {
                height: "100%",
                overflow: "hidden"
            });

            // ����root�ĳ�ʼ����
            var rootStyles = {
                position: "absolute",
                transformOrigin: "top left",
                transition: "all 0s ease-in-out",
                transformStyle: "preserve-3d"
            };

            css(root, rootStyles);  // Ӧ��css����
            css(root, {
                top: "50%",
                left: "50%",
                transform: perspective(config.perspective / windowScale) + scale(windowScale)
            });
            css(canvas, rootStyles);

            body.classList.remove("impress-disabled");  // ע��ϸ�ڣ����ڲ�ȷ����û�У�������removeһ��
            body.classList.add("impress-enabled");

            // ��ʼ������step��������initStep����
            steps = $$(".step", root);
            steps.forEach(initStep);

            // ��canvas����һ����ʼ״̬
            currentState = {
                translate: { x: 0, y: 0, z: 0 },
                rotate: { x: 0, y: 0, z: 0 },
                scale: 1
            };

            initialized = true;     // ����Ѿ���ʼ����

            triggerEvent(root, "impress:init", { api: roots["impress-root-" + rootId] }); // ����init�¼���ע�����ﴫ���{api:...}���Ƕ�Ӧ�����¼�ʱ���detail��������õ�
        };

        // ��ȡstep
        var getStep = function (step)
        {
            if (typeof step === "number")
            { // ������������֣�˵�����������ţ�ֱ�Ӵ�������ȡ
                step = step < 0 ? steps[steps.length + step] : steps[step];  // ע�����������֧�ָ����ģ��ó�����ӾͿ���
            } else if (typeof step === "string")
            {  // ������ַ�����˵��������id����byId������ȡ
                step = byId(step);
            }
            return (step && step.id && stepsData["impress-" + step.id]) ? step : null;  // ��������ǵĻ�����ô�����������һ��Ԫ�أ�Ŀ�����жϲ����ǲ���һ��step��������Ǿͷ���null
        };

        // stepenter�¼����õ��������ΪҪ��stepleave��stepenter�����Ա����stepleave��ɺ��������stepenter
        var stepEnterTimeout = null;

        // �л���ָ��step
        var goto = function (el, duration)
        {

            if (!initialized || !(el = getStep(el)))
            {
                // ���û��ʼ��������el����һ��step�ͷ��أ�ע�������Ӧ�����getStep���������Ҫ�ú���⡣ͬʱ�����ﻹ����˶�el�ĸ�ֵ����Ҳ��js�кܳ������÷�
                return false;
            }

            // ������ϸ����һ�£���Ϊ����������ʱ����bug����ʹ������overflow:hidden��Ҳ�п��ܻ����������ǿ�ƹ�������0��0��
            window.scrollTo(0, 0);

            var step = stepsData["impress-" + el.id];   // ��ȡstep������

            if (activeStep)
            {     // �����ǰ��Ծstep�ı��
                activeStep.classList.remove("active");
                body.classList.remove("impress-on-" + activeStep.id);
            }
            window.sessionStorage.setItem("elid",(el.id));
            el.classList.add("active");     // ��Ŀ��step���Ϊ��Ծ

            body.classList.add("impress-on-" + el.id);

            // ����step���ݼ���canvas��Ҫ��ʲô�任
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

            // ������Ҫע�⣡
            // ����scale���ж�Ҫ��С����Ҫ�Ŵ�
            // ���ź�λ�õ��ƶ��Ƿֿ��ģ�Ϊ���������������Ȼ�������������
            // ���Ҫ��С����ô��ִ�����Ŷ�������ִ���ƶ�����
            // ���Ҫ�Ŵ���ִ���ƶ���������ִ�����Ŷ���
            // ��ҿ��Խ��impress.js�ٷ�demo�����Ǹ����ŵĵط������һ�£������������������л�����������ܶ࣡
            // ��������Ӧ��Ҳ������ΪʲôҪ�ֳ�root��canvas����Ϊ����������һ��ʱ�����ص��ģ����Ա���ֿ����С�
            var zoomin = target.scale >= currentState.scale;

            duration = toNumber(duration, config.transitionDuration);
            var delay = (duration / 2);     // ���delay������������֮��ļ��ʱ��

            // ���el���ǵ�ǰ��Ծstep����ô��������Ϊ������resize�¼������¼���һ��scale
            if (el === activeStep)
            {
                windowScale = computeWindowScale(config);
            }

            var targetScale = target.scale * windowScale;

            // ���el���ǵ�ǰ��Ծstep������stepleave�¼������el���ǵ�ǰ��Ծstep�Ļ��Ǹ����Ͳ��ö����Լ������л����Լ���
            if (activeStep && activeStep !== el)
            {
                onStepLeave(activeStep);
            }

            // root�������ţ�canvas�����ƶ�
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

            // �����ǰ״̬��Ŀ��״̬��ȫһ������ô˵�������Ͳ��ñ任����delay��Ϊ0
            if (currentState.scale === target.scale ||
                (currentState.rotate.x === target.rotate.x && currentState.rotate.y === target.rotate.y &&
                 currentState.rotate.z === target.rotate.z && currentState.translate.x === target.translate.x &&
                 currentState.translate.y === target.translate.y && currentState.translate.z === target.translate.z))
            {
                delay = 0;
            }

            // �洢��ǰ״̬
            currentState = target;
            activeStep = el;

            // �ӳٴ���stepenter�¼���ע���ӳ�ʱ����duration+delay��duration��translate������Ҫ��ʱ�䣬delay����Ϊ���ź��ƶ��ļ��ʱ�䣬������������л�������ʱ����duration+delay
            window.clearTimeout(stepEnterTimeout);
            stepEnterTimeout = window.setTimeout(function ()
            {
                onStepEnter(activeStep);
            }, duration + delay);

            return el;
        };

        // �л�����һ��step
        var prev = function ()
        {
            var prev = steps.indexOf(activeStep) - 1;     // step��˳������������steps�����е�λ�þ�����
            prev = prev >= 0 ? steps[prev] : steps[steps.length - 1]; // ����Ѿ��ǵ�һ�����л������һ��

            return goto(prev);  // ע�⣬�������goto
        };

        // �л�����һ��step
        var next = function ()
        {
            var next = steps.indexOf(activeStep) + 1;
            next = next < steps.length ? steps[next] : steps[0];    // ����Ѿ������һ�����л�����һ��

            return goto(next);
        };

        // step������״̬��future,past,present��present�ǵ�ǰ��Ծstep��future��û��ʾ����step��past����ʾ����step����Щ��ǵ����������û�������css���趨��Ӧ����ʽ
        root.addEventListener("impress:init", function ()
        {   // ע������󶨵���init�¼�
            // STEP CLASSES
            steps.forEach(function (step)
            { // ��ʼȫ����future
                step.classList.add("future");
            });

            root.addEventListener("impress:stepenter", function (event)
            {   // stepenter��ʱ����present
                event.target.classList.remove("past");
                event.target.classList.remove("future");
                event.target.classList.add("present");
            }, false);

            root.addEventListener("impress:stepleave", function (event)
            {   // stepleaveʱ����past
                event.target.classList.remove("present");
                event.target.classList.add("past");
            }, false);

        }, false);

        // ��hash�Ĵ���
        root.addEventListener("impress:init", function ()
        {

            // ��һ��hash
            var lastHash = "";

            // Ҫ��`#/step-id`������`#step-id`����Ϊ������Chrome������ʱ��Ῠ
            root.addEventListener("impress:stepenter", function (event)
            {
                window.location.hash = lastHash = "#/" + event.target.id;
            }, false);

            window.addEventListener("hashchange", function ()
            {
                // ��Ϊ����step��ʱ��hash����£�����Ϊ�˷�ֹ����goto������Ҫ��һ���ж�
                if (window.location.hash !== lastHash)
                {
                    goto(getElementFromHash());
                }
            }, false);

            // ��ʼ����Ϻ��л�����ǰhashָ����step���ߵ�һ��step
            goto(getElementFromHash() || steps[0], 0);
        }, false);

        body.classList.add("impress-disabled");     // ���ﲻ̫��⣬����ûʲô�á�������Ϊ�˱��impress�������Ѿ�������

        // ��¶�ĸ�API
        return (roots["impress-root-" + rootId] = {
            init: init,
            goto: goto,
            next: next,
            prev: prev
        });

    };

    // ��¶֧�ֱ���
    impress.supported = impressSupported;

})(document, window);

// ���ڿ��Ƽ����¼�������¼��������¼��Լ�resize�¼�
(function (document, window)
{
    'use strict';

    // һ�����������������ӳ�delay��ִ��fn��
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

    // ����init�¼�ʱ��󶨸��ֶ���
    document.addEventListener("impress:init", function (event)
    {
        // ���ǵ��������Ӧ���洴���¼�ʱ�����detail��������api���������ǲ����ٻ�ȡ������
        var api = event.detail.api;

        // �󶨼����¼���Ϊ�˷�ֹ����¼����ţ����Դ���keydownʱ���ֹð��
        document.addEventListener("keydown", function (event)
        {
            if (event.keyCode === 9 || (event.keyCode >= 32 && event.keyCode <= 34) || (event.keyCode >= 37 && event.keyCode <= 40))
            {
                event.preventDefault();
            }
        }, false);

        // �ɿ�����ʱ�򴥷��¼�

        document.addEventListener("keyup", function (event)
        {
            if (event.keyCode === 9 || (event.keyCode >= 32 && event.keyCode <= 34) || (event.keyCode >= 37 && event.keyCode <= 40))
            {
                switch (event.keyCode)
                {
                    case 33: // pg up
                    case 37: // left
                    case 38: // up
                        api.prev();    // ��һ��step
                        break;
                    case 9:  // tab
                    case 32: // space
                    case 34: // pg down
                    case 39: // right
                    case 40: // down
                        api.next();    // ��һ��step
                        break;
                }

                event.preventDefault();     // ��ֹð��
            }
        }, false);

        // �����������¼���������ӵĵ�ַ��������һ��step�ĵ�ַ��������ֶ�����Ļ��������ˢ��ҳ��
        document.addEventListener("click", function (event)
        {
            // �ж�Ŀ���ǲ���һ������Ԫ��a������ҳ���Ͽ����кܶ��div�����Դ���������ֱ���ҵ�һ��a
            var target = event.target;
            while ((target.tagName !== "A") &&
                    (target !== document.documentElement))
            {
                target = target.parentNode;
            }

            if (target.tagName === "A")
            { // ����ҵ��ˣ�
                var href = target.getAttribute("href");

                // �ж��ǲ���step�ĵ�ַ
                if (href && href[0] === '#')
                {
                    target = document.getElementById(href.slice(1));
                }
            }

            if (api.goto(target))
            {   // �����step�ĵ�ַ��goto����������ǾͲ����ˣ�ð�ݴ�����ȥ
                event.stopImmediatePropagation();
                event.preventDefault();
            }
        }, false);

        // ��������Ŀ����һ��stepԪ�أ��Ǿ�goto��ȥ
        document.addEventListener("click", function (event)
        {
            var target = event.target;
            // ���������ң��ҵ���һ������Ծ��step
            while (!(target.classList.contains("step") && !target.classList.contains("active")) &&
                    (target !== document.documentElement))
            {
                target = target.parentNode;
            }

            if (api.goto(target))
            {   // ���Ŀ����һ��step�Ǿ�goto�����ǵĻ��Ͳ����ˣ�ð�ݴ�����ȥ
                event.preventDefault();
            }
        }, false);

        // �жϴ�����Ļ����
        document.addEventListener("touchstart", function (event)
        {
            if (event.touches.length === 1)
            {
                var x = event.touches[0].clientX,
                    width = window.innerWidth * 0.3,    // ���Կ����������������30%����Ļ�ͻ��ж�����
                    result = null;

                if (x < width)
                {
                    result = api.prev();
                } else if (x > window.innerWidth - width)
                {   // ���������Ҳ�30%����Ļ�ͻ��ж�����
                    result = api.next();
                }

                if (result)
                {   // �����������ң��Ǿͽ�ֹð�ݡ�������Ǿʹ�����ȥ
                    event.preventDefault();
                }
            }
        }, false);

        // ���ڴ�С�仯��ʱ�����goto����Ӧgoto�����¼���scale����
        window.addEventListener("resize", throttle(function ()
        {
            // force going to active step again, to trigger rescaling
            api.goto(document.querySelector(".step.active"), 500);
        }, 250), false);

    }, false);

})(document, window);