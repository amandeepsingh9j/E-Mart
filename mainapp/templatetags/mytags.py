from mainapp.models import Checkout,Checkoutproduct,Product
from django import template


register= template.Library()

@register.filter(name="checkoutProduct")
def checkoutProduct(checkoutid):
    checkout=Checkout.objects.get(id=checkoutid)
    cp=Checkoutproduct.objects.filter(checkout=checkout)
    c=[]
    print(cp)
    for item in cp:
        x={'name':item.prod.name,'maincategory':item.prod.maincategory,'subcategory':item.prod.subcategory,'brand':item.prod.brand,'size':item.prod.size,'price':item.prod.finalprice,'qty':item.qty,'total':item.total,'pic':item.prod.pic1.url,}
        c.append(x)

    return c


@register.filter(name='paymentstatus')
def paymentstatus(op):
    if op==0:
        return 'Pending'
    else:
        return 'Done'
    

@register.filter(name='orderstatus')
def orderstatus(os):
    if os==0:
        return 'Order Placed'
    
    elif os==1:
        return 'Not Packed'
    
    elif os==2:
        return 'Packed'

    elif os==3:
        return 'Ready To Ship'
    
    elif os==4:
        return 'Shipped'
    
    elif os==5:
        return 'Out For Delivery'
    
    elif os==6:
        return 'Delivered'
    
    elif os==7:
        return 'Cancelled'
    

@register.filter(name='paymentmode')
def paymentmode(op):
    if op==0:
        return 'COD'
    
    else:
        return 'Net Banking'


