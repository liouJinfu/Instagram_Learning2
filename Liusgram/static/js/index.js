$(function () {
    var oExports = {
        initialize: fInitialize,
        // 渲染更多数据
        renderMore: fRenderMore,
        // 请求数据
        requestData: fRequestData,
        // 简单的模板替换
        tpl: fTpl
    };
    // 初始化页面脚本
    oExports.initialize();

    function fInitialize() {
        var that = this;
        // 常用元素
        that.listEl = $('article.js-index-list');
        // 初始化数据
        that.page = 1;
        that.pageSize = 5;
        that.listHasNext = true;
        // 绑定事件
        $('.js-load-more').on('click', function (oEvent) {
            var oEl = $(oEvent.currentTarget);
            var sAttName = 'data-load';
            // 正在请求数据中，忽略点击事件
            if (oEl.attr(sAttName) === '1') {
                return;
            }
            // 增加标记，避免请求过程中的频繁点击
            oEl.attr(sAttName, '1');
            that.renderMore(function () {
                // 取消点击标记位，可以进行下一次加载
                oEl.removeAttr(sAttName);
                // 没有数据隐藏加载更多按钮
                !that.listHasNext && oEl.hide();
            });
        });
    }

    function fRenderMore(fCb) {
        var that = this;
        // 没有更多数据，不处理
        if (!that.listHasNext) {
            return;
        }
        that.requestData({
            page: that.page + 1,
            pageSize: that.pageSize,
            call: function (oResult) {
                // 是否有更多数据
                that.listHasNext = !!oResult.has_next && (oResult.images || []).length > 0;
                // 更新当前页面
                that.page++;
                // 渲染数据
                var sHtml = '';
                $.each(oResult.images, function (nIndex, oImage) {
                    sHtml += that.tpl([
                        '<header class="mod-hd">',
                            '<time class="time">#{created_date}</time>',
                            '<a href="/profiles/#{user_id}" class="avatar">',
                                    '<img src="#{head_url}">',
                            '</a>',
                            '<div class="profile-info">',
                             '<a title="/profiles/#{user_name}" href="/profiles/#{user_id}">#{user_name}</a>',
                            '</div>',
                        '</header>',
                        '<div class="mod-bd">',
                            '<div class="img-box">',
                                '<a href="/image/#{id}">',
                                    '<img src="#{url}?imageView2/0/w/800/h/200">',
                                '</a>',

                            '</div>',
                        '</div>',
                        '<div class="mod-ft">',
                            '<ul class="discuss-list">',
                                '<li class="more-discuss">',
                                    '<a>',
                                        '<span>全部 </span><span class="">#{comment_count}</span>',
                                        '<span> 条评论</span></a>',
                                '</li>'].join(''), oImage);

                    for (var ni = 0; ni < oImage.comment_count; ni++) {
                        dict = {
                            'comment_user_username': oImage.comment_username[ni],
                            'comment_user_id': oImage.comment_userid[ni],
                            'comment_content': oImage.comment_username[ni]
                        };
                        sHtml += that.tpl(['<li>',
                            '<a class="_4zhc5 _iqaka" title="#{comment_user_username}" href="/profiles/#{comment_user_id}" data-reactid=".0.1.0.0.0.2.1.2:$comment-17856951190001917.1">#{comment_user_username}</a>',
                            '<span>',
                            '<span>#{comment_content}</span>',
                            '</span>',
                            '</li>',
                            '</ul>',].join(''), dict);

                    }
                    sHtml +=that.tpl([
                            '<section class="discuss-edit">',
                            '<a class="icon-heart"></a>',
                            '<form>',
                            '<input placeholder="添加评论..." type="text">',
                            '</form>',
                            '<button class="more-info">更多选项</button>',
                            '</section>',
                            '</div>'].join(''), oImage);
                });
                sHtml && that.listEl.append(sHtml);
            },
            error: function () {
                alert('出现错误，请稍后重试');
            },
            always: fCb
        });
    }

    function fRequestData(oConf) {
        var that = this;
        var sUrl = '/index/image'+ '/' + oConf.page + '/' + oConf.pageSize + '/';
        $.ajax({url: sUrl, dataType: 'json'}).done(oConf.call).fail(oConf.error).always(oConf.always);
    }

    function fTpl(sTpl, oData) {
        var that = this;
        sTpl = $.trim(sTpl);
        return sTpl.replace(/#{(.*?)}/g, function (sStr, sName) {
            return oData[sName] === undefined || oData[sName] === null ? '' : oData[sName];
        });
    }
});