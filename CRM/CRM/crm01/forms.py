from django import forms
from crm01 import models
from django.core.exceptions import ValidationError


class RegForm(forms.ModelForm):

    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput())

    password = forms.CharField(
        label= '密码',
        widget=forms.widgets.PasswordInput(),
        min_length=6,
        error_messages={
            'required':'密码不能为空',
            'min_length':'最少6位密码',
        }
    )

    class Meta:
        model = models.UserProfile#引用用户信息表
        # fields = '__all__'#默认全部字段
        fields = ['username','password','re_password','name','department']#指定显示字段
        widgets = {
            'username':forms.widgets.EmailInput(attrs={'class':'form-control'}),#attrs为插件添加样式
            'password':forms.widgets.PasswordInput,
        }
        labels = {
            'username':'用户名',
            'password':'密码',
            're_password': '再次输入密码',#优先级低于 re_password = forms.CharField
            'name':'姓名',
            'department':'部门',
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})

    def clean(self):#全局钩子
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            return self.cleaned_data
        self.add_error('re_password','两次密码不一致')
        raise ValidationError('两次密码不一致')


class CustomerForm(forms.ModelForm):
    #新建用户表
    class Meta:
        model = models.Customer
        fields = '__all__'#获取全部字段
        widgets = {
            'course':forms.widgets.SelectMultiple  #多选
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class':'form-control'})


class ConsultRecordForm(forms.ModelForm):
    class Meta:
        model = models.ConsultRecord
        exclude = ['delete_status']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        print('instance: ',self.instance)
        # #限制客户是当前销售的客户
        # self.fields['customer'].widget.choices = [
        #     (i.id,i) for i in self.instance.consultant.customers.all()
        # ]
        # # 限制销售是当前用户
        # self.fields['consultant'].widget.choices = [
        #     (self.instance.consultant.username,self.instance.consultant),
        # ]customer_choice =[(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choice = [(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choice.insert(0,('','--------'))
        # 限制客户是当前销售的私户
        self.fields['customer'].widget.choices = customer_choice
        # 限制跟进人是当前的用户（销售）
        self.fields['consultant'].widget.choices = [(self.instance.consultant.id,self.instance.consultant),]


class EnrollmentForm(forms.ModelForm):

    class Meta:
        model = models.Enrollment
        exclude = ['delete_status','contract_approved']
        labels = {}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        print('instance: ',self.instance)

        # 限制客户是当前销售的私户
        self.fields['customer'].widget.choices = [(self.instance.customer_id, self.instance.customer), ]
        # 限制用户的当前意向
        # self.fields['enrolmennt_class'].widget.choices = [(i.id,i) for i in self.instance.customer.class_list.all()]