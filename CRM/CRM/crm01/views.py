from copy import deepcopy

from django.contrib import auth
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views import View

from crm01 import models
from crm01.forms import RegForm, CustomerForm, ConsultRecordForm,EnrollmentForm
from . import page


# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        obj = auth.authenticate(request, username=username, password=password)
        if obj:
            auth.login(request, obj)
            return redirect(reverse('mycustomer'))
        err_msg = '用户名或密码错误'
        return render(request, 'login.html', {'msg': err_msg})


def reg(request):
    form_obj = RegForm()
    if request.method == 'POST':
        # 将POST的数据传到Form表单对象中进行校验
        form_obj = RegForm(request.POST)
        # 判断输入是否合法
        if form_obj.is_valid():
            # 第一种方法
            # form_obj.cleaned_data.pop('re_password')
            # models.UserProfile.objects.create_user(**form_obj.cleaned_data)
            # 方法二
            obj = form_obj.save()
            # 将密码加密并存储在数据库中
            obj.set_password(obj.password)
            obj.save()
            # 注册完跳转登陆页面
            return redirect('/login/')
    return render(request, 'reg.html', {'form_obj': form_obj})


# FBV展示客户列表
def customer_list(request):
    try:
        request.GET.get('page')
        current_page = int(request.GET.get('page'))
    except:
        current_page = 1
    if request.path_info == reverse('customer'):
        # 获取公户个数及公户对象
        all_count = models.Customer.objects.filter(consultant__isnull=True).count()
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        # 获取私户个数及私户对象
        all_count = models.Customer.objects.filter(consultant=request.user).count()
        all_customer = models.Customer.objects.filter(consultant=request.user)
        print('**********************', request.user)
    per_page = 10
    base_url = '/crm/customer_list'
    P = page.PageInfo(current_page, per_page, all_count, 11, base_url)

    return render(request, 'customer_list.html', {'all_customer': all_customer[P.start():P.end()], 'page': P})


user_list = [{'name': 'alex{}'.format(i)} for i in range(1, 302)]


# CBV展示客户列表
class CustomerList(View):
    def get(self, request):
        try:
            request.GET.get('page')
            current_page = int(request.GET.get('page'))
        except:
            current_page = 1
        # 获取查询条件，默认为空
        query = request.GET.get('query', '')
        if request.path_info == reverse('customer'):
            # Q是模糊查询
            all_count = models.Customer.objects.filter(Q(qq__contains=query) | Q(name__contains=query),
                                                       consultant__isnull=True).count()
            all_customer = models.Customer.objects.filter(Q(qq__contains=query) | Q(name__contains=query),
                                                          consultant__isnull=True)
        else:
            all_count = models.Customer.objects.filter(Q(qq__contains=query) | Q(name__contains=query),
                                                       consultant=request.user).count()
            all_customer = models.Customer.objects.filter(Q(qq__contains=query) | Q(name__contains=query),
                                                          consultant=request.user)
            print('**********************', request.user)
        print('all_count: ', all_count)
        # 每页显示一条数据
        per_page = 1
        base_url = '/crm/mycustomer_list'
        query_params = deepcopy(request.GET)  # 深拷贝,也可以使用request.GET.copy()，也是深拷贝，request.GET返回的是QueryDict对象
        print('query_params: ', query_params)
        P = page.PageInfo(current_page, per_page, all_count, 11, base_url, query_params)
        # 生成新建按钮及获取当前页url的参数
        add_btn, query_params = self.get_add_btn()
        return render(request, 'mycustomer.html', {'all_customer': all_customer[P.start():P.end()],
                                                      'page': P, 'add_btn': add_btn,
                                                      'query_params': query_params})

    def post(self, request):
        print(request.POST)
        # 获取需要操作的方法名
        action = request.POST.get('action')
        # 利用反射执行方法
        if not hasattr(self, action):
            return HttpResponse('...')
        ret = getattr(self, action)()
        return self.get(request)

    def multi_pri(self):
        # 公户变私户
        # 获取需要更改的用户的id
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).update(consultant=self.request.user)

    def multi_pub(self):
        # 私户变公户
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).update(consultant=None)

    def get_add_btn(self):
        url = self.request.get_full_path()
        # 新建QueryDict()对象
        qd = QueryDict()
        # 添加修改权限
        qd._mutable = True
        # 增加一堆键值对
        qd['next'] = url
        # 将QueryDict对象转化成a=b的形式
        query_params = qd.urlencode()
        # 生成一个新建标签，并拼接url
        add_btn = '<a class="btn btn-primary" href="{}?{} ">增加</a>'.format(reverse('add_customer'), query_params)
        return add_btn, query_params


def show_page(request):
    current_page = int(request.GET.get('page'))
    all_count = len(user_list)
    per_page = 10
    base_url = '/crm/show_page'
    P = page.PageInfo(current_page, per_page, all_count, 11, base_url)

    data = user_list[P.start():P.end()]  # 注意是冒号
    print(data)
    return render(request, 'show_page.html', {'data': data, 'page': P})


def add_customer(request):
    customer = CustomerForm()
    if request.method == 'POST':
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            customer.save()
            # 获取当前页url中next参数的值，便于操作完后返回原url
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(reverse('customer'))
    return render(request, 'add_customer.html', {'customer': customer})


def edit_customer(request, edit_id):
    # 根据id查出需要编辑的客户对象
    print(edit_id)
    obj = models.Customer.objects.filter(id=edit_id).first()
    customer = CustomerForm(instance=obj)
    if request.method == 'POST':
        customer = CustomerForm(request.POST, instance=obj)
        if customer.is_valid():
            customer.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(reverse('customer'))
    return render(request, 'edit_customer.html', {'customer': customer})


class ConsultRecord(View):

    def get(self,request,customer_id):
        if customer_id == '0':
            all_consultrecord = models.ConsultRecord.objects.filter(delete_status=False,consultant=request.user)
        else:
            all_consultrecord = models.ConsultRecord.objects.filter(customer_id=customer_id,delete_status=False)
        return render(request,'consultrecord.html',{'all_consultrecord':all_consultrecord})
    def post(self,request):
        pass


def add_consultrecord(request):
    obj = models.ConsultRecord(consultant=request.user)
    print(request.user)
    form_obj = ConsultRecordForm(instance=obj)
    # form_obj = ConsultRecordForm()
    if request.method == 'POST':
        print('2222222222222222',request.POST)
        try:
            form_obj = ConsultRecordForm(request.POST,instance=obj)
        except:
            pass

        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consultrecord',args=(0,)))
    return render(request,'add_consultrecord.html',{'obj':form_obj})


def edit_consultrecord(request,edit_id):
    obj = models.ConsultRecord.objects.filter(id=edit_id).first()
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consultrecord',args=(0,)))
    return render(request, 'edit_consultrecord.html', {'obj': form_obj})


# 展示报名记录
class EnrollmentRecord(View):
    def get(self,request,customer_id):
        if customer_id == '0':
            all_record = models.Enrollment.objects.filter(delete_status=False,customer__consultant=request.user)
        else:
            all_record = models.Enrollment.objects.filter(customer_id=customer_id,delete_status=False)
        return render(request,'enrollrecord.html',{'all_consultrecord':all_record})
    def get_query_params(self):
        url = self.request.get_full_path()
        # 新建QueryDict()对象
        qd = QueryDict()
        # 添加修改权限
        qd._mutable = True
        # 增加一堆键值对
        qd['next'] = url

        query_params = qd.urlencode()
        return query_params

# 添加报名记录
def enrollment(request,customer_id):
    obj = models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(instance=obj)
        form_obj.save()
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect(reverse('mycustomer'))


    return render(request,'enrollment.html',{'form_obj':form_obj})