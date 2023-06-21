from django import forms
from django.forms.models import inlineformset_factory
from root.forms import BaseForm  # optional

from .models import ProductCategory


class ProductCategoryForm(BaseForm, forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
            "sorting_order",
            "slug",
            "is_featured",
        ]


from .models import Product


class ProductForm(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
            "sorting_order",
            "slug",
            "is_featured",
            "image",
            "description",
            "product_id",
        ]


from .models import CustomerProduct


class CustomerProductForm(BaseForm, forms.ModelForm):
    class Meta:
        model = CustomerProduct
        fields = "__all__"
        exclude = [
            "is_deleted",
            "status",
            "deleted_at",
            "sorting_order",
            "slug",
            "is_featured",
            "agent",
        ]

from .models import ProductStock

class ProductStockForm(BaseForm, forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = '__all__'
        exclude = [ 'sorting_order', 'is_featured', 'is_deleted', 'status', 'deleted_at',]


from .models import BranchStock
class BranchStockForm(BaseForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'] = forms.ModelChoiceField(queryset=Product.objects.all())
        self.fields["product"].widget.attrs = {
            "class":"form-select",
            "data-control": "select2",
            "data-placeholder": "Select Item",
        }

    class Meta:
        model = BranchStock
        fields = '__all__'
        exclude = ['is_deleted', 'status', 'deleted_at','sorting_order', 'is_featured']
 