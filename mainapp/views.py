from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
# Create your views here.
from django.contrib import messages
from emarket.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRETS_KEY 
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import razorpay
from random import randrange
from django.db.models import Q

def index(Request):
    data=Product.objects.all().order_by('id').reverse()[:8]

    return render(Request,'index.html',{"data":data})



def shop(Request,mc,sc,br):

    if (mc=="All" and sc=="All" and br=="All"):
        data=Product.objects.all().order_by('id').reverse()
    
    elif(mc!="All" and sc=="All" and br=="All"):
        data=Product.objects.filter(maincategory=MainCategory.objects.get(name=mc)).order_by('id').reverse() 

    elif(mc=="All" and sc!="All" and br=="All"):
        data=Product.objects.filter(subcategory=SubCategory.objects.get(name=sc)).order_by('id').reverse() 

    elif(mc=="All" and sc=="All" and br!="All"):
        data=Product.objects.filter(brand=Brand.objects.get(name=br)).order_by('id').reverse() 

    elif(mc!="All" and sc!="All" and br=="All"):
        data=Product.objects.filter(maincategory=MainCategory.objects.get(name=mc),subcategory=SubCategory.objects.get(name=sc)).order_by('id').reverse()


    elif(mc!="All" and sc!="All" and br!="All"):
        data=Product.objects.filter(maincategory=MainCategory.objects.get(name=mc),subcategory=SubCategory.objects.get(name=sc),brand=Brand.objects.get(name=br)).order_by('id').reverse()
        
    elif(mc=="All" and sc!="All" and br!="All"):
        data=Product.objects.filter(subcategory=SubCategory.objects.get(name=sc),brand=Brand.objects.get(name=br)).order_by('id').reverse()
    
    elif(mc!="All" and sc=="All" and br!="All"):
        data=Product.objects.filter(maincategory=MainCategory.objects.get(name=sc),brand=Brand.objects.get(name=br)).order_by('id').reverse()

    maincategory=MainCategory.objects.all().order_by('id').reverse()
    subcategory=SubCategory.objects.all().order_by('id').reverse()
    brand=Brand.objects.all().order_by('id').reverse()

    return render(Request,"shop.html",{"data":data,"mc":mc,'br':br,'sc':sc,"maincategory":maincategory,'subcategory':subcategory,'brand':brand})


def searchpage(Request):
    search=Request.POST.get("search")
    data=Product.objects.filter(Q(name__icontains=search) | Q(color__icontains=search) | Q(size__icontains=search))
    subcategory=SubCategory.objects.all()
    maincategory=MainCategory.objects.all()
    brand=Brand.objects.all()

    return render(Request,'shop.html',{'mc':'All','br':'All','sc':'All','data':data,'maincategory':maincategory,'subcategory':subcategory,'brand':brand})


def SingleProduct(Request,id):
    detail=Product.objects.get(id=id)
    return render (Request,'singleproduct.html',{'detail':detail})



def loginPage(Request):

    if Request.method=='POST':
        username=Request.POST.get("username1")
        password=Request.POST.get("password1")
        user=authenticate(username=username,password=password)
        if user is not None:
            login(Request,user)
            if user.is_superuser:
                return redirect("/admin")
            
            else:
                return redirect("/profile")
        else:
            messages.error(Request,"Invalid Username & Password")
    
    return render(Request,"login.html")


def logoutpage(Request):
    logout(Request)
    return redirect("/login")


def SignupPage(Request):
    if Request.method=="POST":
        password=Request.POST.get("password")
        cpassword=Request.POST.get("cpassword")
        username=Request.POST.get("username")
        phone=Request.POST.get("phone")
        email_id=Request.POST.get("email")

        if not(email_id and password and cpassword):
            messages.error(Request,"Please Provide all the details")
            
    

        if password!=cpassword:
            messages.error(Request,"Password and confirm Password do not match")
            
        

        is_user_exist=User.objects.filter(email=email_id)

        if is_user_exist:
            messages.error(Request,"User with this username already exist")
            

    


        if User.objects.filter(username=username).exists():
            messages.error(Request,"User with this username already exist.Please usedifferent username")
            
        
        b=Buyer()
        b.name=Request.POST.get('name')
        b.username=username
        b.email=email_id
        b.phone=phone
        user=User(username=username,email=email_id)
        if User():
            user.set_password(password)
            user.save()
            b.save()
            subject="Your Account is Created: Team Eshop"
            message='Hello '+b.name+'\nThanks to Create a Buyer Account with us\n Now You can Buy our latest Product \n Team Eshop'
            email_from=settings.EMAIL_HOST_USER
            recipient_list=[b.email,]
            send_mail(subject,message,email_from,recipient_list)
            return redirect('/login/')
        
        else:
            messages.error(Request,"User with this username or Email Id already exist.Please usedifferent username")
    return render(Request,"signup.html")




@login_required(login_url="/login/")
def profilepage(Request):
    user=User.objects.get(username=Request.user)

    if user.is_superuser:
        return redirect("/admin")
    
    else:
        buyer=Buyer.objects.get(username=user.username)
        wishlist=Wishlist.objects.filter(user=buyer)
        orders=Checkout.objects.filter(user=buyer)
    return render(Request,'profile.html',{'users':buyer,'wishlist':wishlist,'order':orders})



@login_required(login_url='/login/')
def updateprofile(Request):
    user=User.objects.get(username=Request.user)
    if (user.is_superuser):
        return redirect('/admin')
    else:
        buyer=Buyer.objects.get(username=user.username)
        if(Request.method=='POST'):
          buyer.name=Request.POST.get('name')  
          buyer.email=Request.POST.get('email')  
          buyer.phone=Request.POST.get('phone')  
          buyer.address=Request.POST.get('address')  
          if Request.FILES.get("pic")!="":
              buyer.pic=Request.FILES.get("pic") 
          buyer.save()
          return redirect("/profile")
    return render (Request,'updatepage.html',{'user':buyer})




@login_required(login_url='/login/')
def addtocart(Request,id):
    cart=Request.session.get('cart',None)
    p=Product.objects.get(id=id)
    if cart is None:
        cart={str(p.id):{'pid':str(p.id),'name':p.name,'size':p.size,'color':p.color,'brand':p.brand.name,'maincategory':p.maincategory.name,'subcategory':p.subcategory.name,'total':p.finalprice,'price':p.finalprice,'pic':p.pic1.url,'qty':1}}

    else:
        if str(p.id) in cart:
            item=cart[str(p.id)]
            item['qty']=item['qty']+1
            item['total']=item['total']+1
            item['total']=item['total']+item['price']
            cart[str(p.id)]=item

        else:
            cart.setdefault(str(p.id),{'pid':str(p.id),'name':p.name,'size':p.size,'color':p.color,'brand':p.brand.name,'maincategory':p.maincategory.name,'subcategory':p.subcategory.name,'total':p.finalprice,'price':p.finalprice,'pic':p.pic1.url,'qty':1})

    Request.session['cart']=cart
    Request.session.set_expiry(60*60*24*45)
    return redirect('/cart')


@login_required(login_url='/login/')
def cartpage(Request):
    cart=Request.session.get('cart',None)
    c=[]
    total=0
    shipping=0
    for value in cart.values():
        total=total+value['total']
        c.append(value)
        print(value,"\n\n")
        print(c)
    if total<5000 and total>0:
            shipping=150

    final=total+shipping
    return render(Request,'cart.html',{'cart':c,'total':total,'shipping':shipping,'final':final})


@login_required(login_url='/login/')
def deletecart(Request,pid):
    cart=Request.session.get('cart',None)
    if cart:
        for key in cart.keys():
            if str(pid)==key:
                del cart[key]
                break
        Request.session['cart']=cart

    return redirect('/cart')



@login_required(login_url='/login/')
def updatecart(Request,pid,op):
    cart=Request.session.get('cart',None)
    if cart:
        for key,values in cart.items():
            if str(pid)==key:
                if op=='inc':
                    values['qty']=values['qty']+1
                    values['total']=values['total']+values['price']

                elif(op=='dec' and values['qty']>1):
                    values['qty']=values['qty']-1
                    values['total']=values['total']-values['price']
                    
                cart[key]=values
                break
        Request.session['cart']=cart
    return redirect('/cart')
 


@login_required(login_url='/login/')
def addtowishlist(Request,pid):
    try:
        user=Buyer.objects.get(username=Request.user.username)
        p=Product.objects.get(id=pid)
        try:
            w=Wishlist.objects.get(user=user,product=p) 
        except:
            w=Wishlist()
            w.user=user
            w.product=p
            w.save()

        return redirect('/profile')
    except:
        return redirect('/admin')
    



@login_required(login_url='/login/')
def deletewishlist(Request,pid):
        try:
            user=Buyer.objects.get(username=Request.user.username)
            p=Product.objects.get(id=pid)
            try:
                w=Wishlist.objects.get(user=user,product=p)
                w.delete()

            except:
                pass

        except:
            pass

        return redirect("/profile")




@login_required(login_url='/login/')
def checkoutpage(Request):
    try:
        buyer=Buyer.objects.get(username=Request.user)
        cart=Request.session.get('cart',None)
        c=[]
        total=0
        shipping=0
        final=0
        if cart is not None:
            for value in cart.values():
                total=total+value['total']
                c.append(value)
            if (total<5000 and total>0):
                shipping=150

        final=total+shipping
        return render(Request,'checkout.html',{'user':buyer,'cart':c,'shipping':shipping,'total':total,'final':final})

    except:
        return redirect('/admin')
    



# client=razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRETS_KEY))
# @login_required(login_url='/login/')       
# def orderpage(Request):
#     if (Request.method=='POST'):
#         mode=Request.POST.get('mode')

#         user=Buyer.objects.get(username=Request.user.username)
#         cart=Request.session.get('cart',None)
#         if cart is None:
#             return redirect('/cart')
#         else:
#             check=Checkout()
#             check.user=user
#             total=0
#             shipping=0
#             for value in cart.values():
#                     totaL=total+value['total']
            
#             if(total<5000 and total>0):
#                 shipping=150

#             final=total+shipping
#             print(total)
#             print(final)
#             check.total=total
#             check.shipping=shipping
#             check.final=final
#             check.save()

#             for value in cart.values():
#                 cp=Checkoutproduct()
#                 cp.checkout=check
#                 cp.prod=Product.objects.get(id=value['pid'])
#                 cp.total=value['total']
#                 cp.qty=value['qty']
#                 cp.save()
                

#             Request.session['cart']={}
#             subject="Your Order is Placed: Team E-Mart"
#             message=f"Thanks to shop with us \n Your order  is placed & it will deliver in 5 Business days."
#             email_from=settings.EMAIL_HOST_USER 
#             recipient_list=[user.email,]
#             send_mail(subject,message,email_from,recipient_list)
#             if mode=="COD":
#                 return redirect('/confirmation')
#             else:
#                 orderAmount=check.final*100
#                 orderCurrency='INR'
#                 paymentOrder=client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
#                 paymentID=paymentOrder['id']
#                 check.mode='Net Banking'
#                 check.save()


#                 return render(Request,'pay.html',{
#                     'amount':orderAmount,
#                     'api_key':RAZORPAY_API_KEY,
#                     'order_id':paymentID,
#                     'User':user
#                 })
# 
    # else:
    #     return redirect('/checkout')
    

client=razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRETS_KEY))
@login_required(login_url='/login/')
def orderpage(Request):
    if (Request.method=='POST'):
        mode=Request.POST.get('mode')
        
        user=Buyer.objects.get(username=Request.user.username)
        cart=Request.session.get('cart',None)
        if(cart is None):
                return redirect('/cart')
        else:
                check=Checkout()
                check.user=user
                total=0
                shipping=0
                for value in cart.values():
                       
                        total=total+value['total']
                if(total<22000 and total>0):
                        shipping=150
                    
                final=total+shipping
                check.total=total
                check.shipping=shipping
                check.final=final
                check.save()

                for value in cart.values():
                        cp=Checkoutproduct()
                        cp.checkout=check
                        cp.prod=Product.objects.get(id=value['pid'])
                        cp.qty=value['qty'] 
                        cp.total=value['total'] 
                        cp.save()
                        
                Request.session['cart']={}
                subject="Your Order is Placed: Team Eshop"
                message='Thanks to Shop with us\n Your order has been placed\n Now you can track your order in Profile Page\n Team Eshop'

                email_from=settings.EMAIL_HOST_USER
                recipient_list=[user.email, ]
                send_mail(subject,message,email_from,recipient_list)
                if(mode=="COD"):
                    return redirect("/confirmation")
                else:
                    orderAmount=check.final*100
                    orderCurrency="INR"
                    paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))

                    paymentID=paymentOrder['id']
                    check.mode='Net Banking'
                    check.save()
                    # orderAmount = str(check.final*100)
                    # orderCurrency = "INR"
                    # paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
                    # paymentID = paymentOrder['id']
                    # check.mode="Net Banking"
                    # check.save()
                    return render(Request,'pay.html',{
                        "amount":orderAmount,
                        "api_key":RAZORPAY_API_KEY,
                        "order_id":paymentID,
                        "User":user

                    })   
 
    else:
        return redirect("/checkout")

@login_required(login_url='/login/')
def paymentSuccess(request,rppid,rpoid,rpsid):
    buyer=Buyer.objects.get(username=request.user.username)
    check=Checkout.objects.filter(buyer=buyer)
    check=check[::-1]
    check=check[0]
    check.rppid=rppid
    check.paymentstatus=2
    check.save()
    return redirect("/confirmation/")



@login_required(login_url='/login/')
def confirmationpage(Request):
    return render(Request,'confirmation.html')


def forgetusername(Request):
    if Request.method=="POST":
        username=Request.POST.get('username')
        try:
            user=User.objects.get(username=username)
            if user.is_superuser:
                return redirect('/admin')
            else:
                buyer=Buyer.objects.get(username=username)
                otp=randrange(100000,999999)
                buyer.otp=otp
                buyer.save()
                subject="OTP for Password Reset: Team E-Market"
                message=f'OTP for Password reset is {str(otp)} \n Team E-Mart'
                email_from=settings.EMAIL_HOST_USER
                recipient_list=[buyer.email,'amandeep.9j@gmail.com']
                send_mail(subject,message,email_from,recipient_list)
                Request.session['resetuser']=username
                return redirect('/forget-otp')
            
        except:
            messages.error(Request,'Invalid Username!!!')
    return render(Request,'forgetusername.html')
    


def forgetotp(Request):
    if Request.method=="POST":
            otp=Request.POST.get('otp')
            username=Request.session.get("resetuser",None)
            if username:
                buyer=Buyer.objects.get(username=username)
                if int(otp)==buyer.otp:
                    return redirect('/forgetpassword')
                else:
                    messages.error(Request,'Invalid OTP')
            else:
                messages.error(Request,"Unautorized User")
    return render(Request,"forget-otp.html")

def forgetpassword(Request):
    if Request.method=='POST':
        username=Request.POST.get('username')
        password=Request.POST.get('password')
        cpassword=Request.POST.get('cpassword')

        if username:
            if password==cpassword:
                user=User.objects.get(username=username)
                user.set_password(password)
                user.save()
                return redirect('/login')
            else:
                messages.error(Request,'Password and Confirm Password do not match')

        else:
                messages.error(Request,'Unautorized username')

    return render(Request,'forget-password.html')
        
        



def contactpage(Request):
    if (Request.method=='POST'):
        c=Contact()
        c.name=Request.POST.get('name')
        c.email=Request.POST.get('email')
        c.phone=Request.POST.get('phone')
        c.subject=Request.POST.get('Subject')
        c.message=Request.POST.get('Message')
        c.save()
        messages.success(Request,'Thanks for sharing your Query with us')

    return render(Request,'contact.html')
