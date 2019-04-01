#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class CustomPaginator(object):
    def __init__(self, query_set, current_page, show_number_page=5, number=20):
        self.query_set = query_set
        self.number = number
        self.snp = show_number_page
        self.current_page = current_page

    def paginator(self):
        pag = Paginator(list(self.query_set), self.number)  # 定义分页器，每页显示16条
        try:
            # 当前页。转换为int类型,出现异常赋值为1
            self.current_page = int(self.current_page)
        except:
            self.current_page = 1

        try:
            # 获取分页对象
            page_obj = pag.page(self.current_page)
        except PageNotAnInteger:
            page_obj = pag.page(1)
        except EmptyPage:
            page_obj = pag.page(pag.num_pages)

        data_set = list()   # 当前页的数据列表
        for row in page_obj:
            data_set.append(row)

        has_per_page = page_obj.has_previous()  # 当前页是否有上一页
        if has_per_page:
            per_page_number = page_obj.previous_page_number()  # 上一页页码
        else:
            per_page_number = None

        # total_page = [page for page in pag.page_range] # 总页数列表
        # print(pag.page_range.start,pag.page_range.stop,len(pag.page_range))
        # 控制页面上面只展示5页
        """
        if len(pag.page_range) < 5:
            s, e = 1, len(pag.page_range)
        elif self.current_page - 5 < 1:
            s, e = 1, 5
        elif self.current_page + 5 > len(pag.page_range):
            s, e = len(pag.page_range) - 4, len(pag.page_range)
        else:
            s, e = self.current_page - 2, self.current_page + 2
        """

        if len(pag.page_range) < self.snp:
            s, e = 1, len(pag.page_range)
        elif self.current_page - self.snp < 1:
            s, e = 1, self.snp
        elif self.current_page + self.snp > len(pag.page_range):
            s, e = len(pag.page_range) - (self.snp - 1), len(pag.page_range)
        else:
            s, e = self.current_page - (self.snp - 1 ) / 2, self.current_page + (self.snp - 1 ) / 2
        # 当前显示的页码
        curr_show_pages = [i for i in range(s, e + 1)]

        has_next_page = page_obj.has_next()  # 当前页是否有下一页
        if has_next_page:
            next_page_number = page_obj.next_page_number()  # 下一页页码
        else:
            next_page_number = None

        paging_param = {'has_per_page': has_per_page, 'per_page_number': per_page_number,
                        'total_page': len(pag.page_range),
                        'has_next_page': has_next_page, 'next_page_number': next_page_number,
                        'current_page': self.current_page,
                        'curr_show_pages': curr_show_pages}
        return paging_param,data_set