"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    # 公户
    # url(r'^customer_list/',views.customer_list,name='customer'),
    # #私户
    # url(r'^mycustomer_list/',views.customer_list,name='mycustomer'),
    # CBV
    url(r'^customer_list/', views.CustomerList.as_view(), name='customer'),
    url(r'^mycustomer_list/', views.CustomerList.as_view(), name='mycustomer'),
    url(r'^show_page/', views.show_page),
    url(r'^add_customer', views.add_customer, name='add_customer'),
    url(r'^edit_customer/(\d+)', views.edit_customer, name='edit_customer'),
    # 展示跟进记录
    url(r'^consultrecord/(\d+)', views.ConsultRecord.as_view(), name='consultrecord'),
    # 添加跟进记录
    url(r'^add_consultrecord', views.add_consultrecord, name='add_consultrecord'),
    url(r'^edit_consultrecord/(\d+)/', views.edit_consultrecord, name='edit_consultrecord'),
    # 展示报名记录
    url(r'^enrollment_record/(?P<customer_id>\d+)', views.EnrollmentRecord, name='enrollment_record'),
    # 添加报名记录
    url(r'^enrollment_add/(?P<customer_id>\d+)', views.enrollment, name='enrollment_add'),

]
