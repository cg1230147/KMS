$(function () {
    $.fn.extend({
        createdTree : function(data, id) {
            if (this.children().length === 0) {
                this.append('<ul class="root-node"></ul>')
            }
            for (let i=0;i<data.length;i++){
                let elem =
                        '<li>' +
                        '   <span>' +
                        '       <span class="node-icon"><i class="fa fa-plus-square fa-fw"></i></span>' +
                        '       <span class="node-choice"><input type="checkbox"></span>' +
                        '       <span class="node-name folder-closed">' +
                        '           <a href="javascript:void(0)" deptid="'+data[i].id+'" superiordeptid="'+data[i].superior_dept+'" ' +
                        '           deptlevel="'+data[i].dept_level__department_level+'">'+ data[i].name+'</a></span>' +
                        '   </span>' +
                        '   <ul class="sub-node" style="display:none;"></ul>'+
                        '</li>' ;
                // 判断是否有子节点
                if (data[i].nodes && data[i].nodes.length > 0){
                    if (this.find('.root-node').children().length === 0) {
                        this.children().append(elem)
                    }else {
                        $('.node-name').each(function () {
                            if (Number($(this).children().attr('deptid')) === id){
                                $(this).parent().next().append(elem);
                            }
                        });
                    }
                    // 递归添加所有节点
                    this.createdTree(data[i].nodes,data[i].id);
                }else {
                    let lastElem =
                            '<li style="padding-left: 24px">' +
                            '   <span>' +
                            '       <span class="node-icon "><i class="fa fa-plus-square fa-fw hide"></i></span>' +
                            '       <span class="node-choice"><input type="checkbox"></span>' +
                            '       <span class="node-name last-node">' +
                            '           <a href="javascript:void(0)" deptid="'+data[i].id+'" superiordeptid="'+data[i].superior_dept+'" ' +
                            '           deptlevel="'+data[i].dept_level__department_level+'">'+ data[i].name+'</a></span>' +
                            '   </span>' +
                            '</li>' ;
                    // 添加最后的节点元素
                    $('.node-name').each(function () {
                        if (Number($(this).children().attr('deptid')) === id){
                            let lastSubNode = $(this).parent().next();
                            lastSubNode.append(lastElem);
                            // lastSubNode.css('padding-left', '24px');
                            // lastSubNode.find('.node-name').addClass('last-node');
                            // lastSubNode.find('.node-icon').remove('.node-icon');
                        }
                    });
                }
            }
        },
        unfoldFold : function () {
            $('.root-node .node-icon, .node-name').on("click",function () {
                // 找到紧邻的子节点
                let subNode = $(this).parent().next();
                // 判断点击的是加减号图标还是节点名称
                if ($(this)[0].className === 'node-icon'){
                    if (subNode.css('display') === 'none'){
                        $(this).nextAll('.node-name').addClass('folder-open');  // 改变展开后的图标
                        $(this).children().toggleClass('fa-minus-square');  // 展开后改为减号
                        subNode.slideDown(200);    // 展示子节点
                    }else {
                        $(this).nextAll('.node-name').removeClass('folder-open');   // 改变折叠后的图标
                        $(this).children().removeClass('fa-minus-square');  // 折叠后移除减号图标
                        subNode.find('.node-icon').children().removeClass('fa-minus-square');   // 折叠后移除子节点减号图标
                        subNode.find('.sub-node').slideUp();    // 隐藏所有子节点
                        subNode.slideUp(200);  // 隐藏当前节点
                    }
                }else {
                    if (subNode.css('display') === 'none'){
                        $(this).addClass('folder-open');    // 改变展开后的图标
                        $(this).prevAll('.node-icon').children().toggleClass('fa-minus-square');    // 展开后改为减号
                        subNode.slideDown(200);
                    }else {
                        $(this).removeClass('folder-open'); // 改变折叠后的图标
                        subNode.find('.node-name').removeClass('folder-open');  // 改变折叠后子节点的图标
                        $(this).prevAll('.node-icon').children().removeClass('fa-minus-square');    // 折叠后移除减号图标
                        subNode.find('.node-icon').children().removeClass('fa-minus-square');  // 折叠后移除子节点减号图标
                        subNode.find('.sub-node').slideUp();    // 隐藏所有子节点
                        subNode.slideUp(200);  // 隐藏当前节点
                    }
                }
            });
        },
    });
});