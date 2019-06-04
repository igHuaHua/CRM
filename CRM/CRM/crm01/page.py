from django.http import QueryDict
class PageInfo:
    def __init__(self,current_page,per_page,all_count,show_page,base_url,query_params=QueryDict()):
        self.current_page = int(current_page)#当前页码
        self.per_page = per_page#每页显示几条数据
        self.all_count = all_count#数据总量
        self.show_page = show_page#页码显示几条
        self.base_url = base_url#基于的url
        self.query_params = query_params
        #修改QueryDict字典
        query_params._mutable = True
        a, b = divmod(all_count,per_page)#判断能否整除，不能就增加一页放数据
        if b:
            a = a+1
        self.all_page = a

    def last_page(self):
        return self.all_page

    def start(self):
        return int((self.current_page-1) * self.per_page)

    def end(self):
        return int(self.current_page * self.per_page)

    def pager(self):
        page_list = []

        half = int((self.show_page - 1)/2)

        if self.all_page < self.show_page:
            begin = 1
            stop = self.all_page + 1
        else:
            if self.current_page <= half:
                begin = 1
                stop = self.show_page + 1
            else:
                if self.current_page + half > self.all_page + 1:
                    begin = self.all_page - self.show_page + 1
                    stop = self.all_page + 1
                else:
                    begin = self.current_page - half
                    stop = self.current_page + half + 1
        self.query_params['page'] = 1
        first_page = "<li><a href='{0}?{1}'>首页</a></li>".format(self.base_url,self.query_params.urlencode())
        page_list.append(first_page)
        if self.current_page <=1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            self.query_params['page'] = self.current_page - 1
            prev = "<li><a href='{0}?{1}'>上一页</a></li>".format(self.base_url,self.query_params.urlencode())
        page_list.append(prev)
        for i in range(begin,stop):
            self.query_params['page'] = i
            if self.current_page == i:
                v = "<li class='active'><a href='{0}?{1}'>{2}</a></li>".format(self.base_url,self.query_params.urlencode(),i)
                page_list.append(v)
            else:
                v = "<li><a href='{0}?{1}'>{2}</a></li>".format(self.base_url,self.query_params.urlencode(), i)
                page_list.append(v)
        if self.current_page >= self.all_page:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            self.query_params['page'] = self.current_page+1
            nex = "<li><a href='{0}?{1}'>下一页</a></li>".format(self.base_url,self.query_params.urlencode())
        page_list.append(nex)

        self.query_params['page'] = self.last_page()
        last_page = "<li><a href='{0}?{1}'>尾页</a></li>".format(self.base_url, self.query_params.urlencode())
        page_list.append(last_page)
        return ' '.join(page_list)