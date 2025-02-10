from django.http import QueryDict

class Pagination(object):
    def __init__(self, current_page, all_count, base_url, query_params, per_page=10, per_page_count=11):
        """
        :param current_page: 当前页数（可以是字符串，需要转换为 int）
        :param all_count: 数据总条数
        :param base_url: 基础 URL，如 request.path_info
        :param query_params: 查询参数（一般为 request.GET），用于拼接 URL
        :param per_page: 每页显示条数
        :param per_page_count: 分页栏最多显示的页码个数（新方案中不使用该参数，仅为兼容）
        """
        try:
            self.current_page = int(current_page)
        except Exception:
            self.current_page = 1

        self.all_count = all_count
        self.base_url = base_url
        # 将 query_params 复制一份，避免修改原始数据
        self.query_params = query_params.copy() if isinstance(query_params, QueryDict) else query_params
        self.per_page = per_page

        # 计算总页数
        self.total_pages, remainder = divmod(all_count, per_page)
        if remainder:
            self.total_pages += 1

    @property
    def start(self):
        """当前页数据切片起始位置"""
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """当前页数据切片结束位置"""
        return self.current_page * self.per_page

    def page_html(self):
        html_list = []
        cp = self.current_page
        total = self.total_pages

        # 根据总页数和当前页确定需要显示的页码列表
        if total <= 5:
            pages = list(range(1, total + 1))
        else:
            if cp <= 2:
                # 当前页为1或2时：显示 1,2,3,省略号,最后一页
                pages = [1, 2, 3, '...', total]
            elif cp == 3:
                # 当前页为3时：显示 1,2,3,4,省略号,最后一页
                pages = [1, 2, 3, 4, '...', total]
            elif cp >= 4 and cp <= total - 3:
                # 中间部分：显示 第一页,省略号,当前页前一页、当前页、当前页后一页,省略号,最后一页
                pages = [1, '...', cp - 1, cp, cp + 1, '...', total]
            elif cp == total - 2:
                # 当前页为倒数第三页：显示 第一页,省略号,倒数第四页、倒数第三页、倒数第二页,最后一页
                pages = [1, '...', total - 3, total - 2, total - 1, total]
            else:  # cp == total - 1 或 cp == total
                # 当前页为倒数第二页或最后一页：显示 第一页,省略号,倒数第三页、倒数第二页、最后一页
                pages = [1, '...', total - 2, total - 1, total]

        # 构造“上一页”链接
        if cp <= 1:
            html_list.append('<li class="disabled"><a href="javascript:void(0);">&laquo;</a></li>')
        else:
            params = self.query_params.copy()
            params['page'] = cp - 1
            prev_url = "{}?{}".format(self.base_url, params.urlencode())
            html_list.append('<li><a href="{}">&laquo;</a></li>'.format(prev_url))

        # 构造数字页码链接和省略号
        for p in pages:
            if p == '...':
                html_list.append('<li class="disabled"><a href="javascript:void(0);">...</a></li>')
            else:
                params = self.query_params.copy()
                params['page'] = p
                url = "{}?{}".format(self.base_url, params.urlencode())
                if p == cp:
                    html_list.append('<li class="active"><a href="{}">{}</a></li>'.format(url, p))
                else:
                    html_list.append('<li><a href="{}">{}</a></li>'.format(url, p))

        # 构造“下一页”链接
        if cp >= total:
            html_list.append('<li class="disabled"><a href="javascript:void(0);">&raquo;</a></li>')
        else:
            params = self.query_params.copy()
            params['page'] = cp + 1
            next_url = "{}?{}".format(self.base_url, params.urlencode())
            html_list.append('<li><a href="{}">&raquo;</a></li>'.format(next_url))

        return "".join(html_list)
