
function Search(page){
    let searchCategory = $('[name=search-category]').val();
    let searchCondition = $('[name=search]').val();
    if (searchCondition === ""){
        $('[name=search]').focus();
        // alert("请输入关键字在搜索！")
        return;
    }
    $.ajax({
        url: '/search/',
        method: 'post',
        dataType: 'json',
        data: {'searchCategory':searchCategory,'searchCondition': searchCondition,'page': page},
        success:function (data) {
            if (data.status) {
                let tbody = $('.content table tbody');
                let pageNumber = 16;
                tbody.empty();
                for (let i = 0; i < pageNumber; i++) {
                    if (data.query_data[i]) {
                        var td = "<td><input type='checkbox'/></td>" +
                            "<td style='text-align: left;'><a href='/view_form/?doc_uuid=" +
                            data.query_data[i].uuid + "'target='_blank'>" + data.query_data[i].title + "</a></td>" +
                            "<td>" + data.query_data[i].issuer + "</td>" +
                            "<td>" + data.query_data[i].classify_name + "</td>" +
                            "<td>" + data.query_data[i].issuer_dept + "</td>" +
                            "<td>" + data.query_data[i].auditor + "</td>" +
                            "<td>" + data.query_data[i].release_date + "</td>";

                    } else {
                        var td = "<td></td><td style='text-align: left;'></td>" +
                            "<td></td>" + "<td></td>" + "<td></td>" + "<td></td>" + "<td></td>";
                    }
                    tbody.append("<tr></tr>");
                    tbody.children('tr').last().append(td);
                }

                $('.pagination').empty();
                //上一页
                if (data.paging_param.has_per_page) {
                    let perPage = '<li><a href="#" aria-label="Previous" onclick="GetSearchPagingData('
                        + data.paging_param.per_page_number + ')"><span aria-hidden="true">&laquo;</span></a></li>';
                    $('.pagination').append(perPage)
                } else {
                    let perPage = '<li><a href="#" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>';
                    $('.pagination').append(perPage)
                }
                // 页码
                for (let i = 0; i < data.paging_param.curr_show_pages.length; i++) {
                    if (data.paging_param.current_page === data.paging_param.curr_show_pages[i]) {
                        let page = '<li><a href="#" style="background-color: #eeeeee;" onclick="GetSearchPagingData(' +
                            data.paging_param.curr_show_pages[i] + ');">' + data.paging_param.curr_show_pages[i] + '</a></li>';
                        $('.pagination').append(page)
                    } else {
                        let page = '<li><a href="#" onclick="GetSearchPagingData(' +
                            data.paging_param.curr_show_pages[i] + ');">' + data.paging_param.curr_show_pages[i] + '</a></li>';
                        $('.pagination').append(page)
                    }
                }

                // 下一页
                if (data.paging_param.has_next_page) {
                    let nextPage = '<li><a href="#" aria-label="Next" onclick="GetSearchPagingData(' +
                        data.paging_param.next_page_number + ')"><span aria-hidden="true">&raquo;</span></a></li>';
                    $('.pagination').append(nextPage)
                } else {
                    let nextPage = '<li><a href="#" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>';
                    $('.pagination').append(nextPage)
                }
                $('.pagination').append('<li style="position: absolute;align-self: center;right: 10px;">总页数:' +
                    data.paging_param.total_page + '页</li>')
            }
        }
    })
}
function GetSearchPagingData(page) {
    Search(page);
}