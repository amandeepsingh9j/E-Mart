from django.db import models

# Create your models here.


class MainCategory(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class SubCategory(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=150)
    maincategory=models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    subcategory=models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    brand=models.ForeignKey(Brand, on_delete=models.CASCADE)
    size=models.CharField(max_length=50)
    color=models.CharField(max_length=50)
    stock=models.CharField(max_length=50,default="In Stock",null=True,blank=True)
    description=models.TextField(default="This is the best Product",null=True,blank=True)
    baseprice=models.IntegerField()
    discount=models.IntegerField(default=0,blank=True,null=True)
    finalprice=models.IntegerField()
    pic1=models.ImageField(upload_to="upload",default="", height_field=None, width_field=None, null=True,blank=True)
    pic2=models.ImageField(upload_to="upload",default="" ,height_field=None, width_field=None, null=True,blank=True)


    def __str__(self):
        return self.name
    

class Buyer(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    username=models.CharField(max_length=50)
    email=models.EmailField(max_length=254)
    phone=models.CharField(max_length=10)
    address=models.CharField(max_length=50,blank=True,null=True,default="")
    otp=models.IntegerField(default="-121212")
    pic=models.ImageField(upload_to="upload", height_field=None, width_field=None,default="",blank=True,null=True)

    def __str__(self):
        return str(self.id)+ " "+ self.username
    


class Wishlist(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(Buyer, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)+" "+self.user.username+" "+self.product.name


payment=((0,'Pending'),(1,'Done'))
mode=((0,'COD'),(1,'Net Banking'))
status=((0,'Order Placed'),(1,'Not Packed'),(2,'Packed'),(3,'Ready to Shipped'),(4,'Shipped'),(5,'Out For Delivery'),(6,'Delivered'),(7,'Cancelled'))
class Checkout(models.Model):
    id=models.AutoField(primary_key=True)
    user=models.ForeignKey(Buyer, on_delete=models.CASCADE)
    total=models.IntegerField()
    shipping=models.IntegerField()
    final=models.IntegerField()
    rppid=models.CharField(max_length=50,default="",null=True,blank=True)
    date=models.DateTimeField(auto_now=True)
    paymentmode=models.IntegerField(choices=mode,default=0)
    paymentstatus=models.IntegerField(choices=payment,default=0)
    orderstatus=models.IntegerField(choices=status,default=0)

    def __str__(self):
        return str(self.id)+" "+self.user.username


class Checkoutproduct(models.Model):
    id=models.AutoField(primary_key=True)
    prod=models.ForeignKey(Product, on_delete=models.CASCADE)
    checkout=models.ForeignKey(Checkout, on_delete=models.CASCADE)
    qty=models.IntegerField(default='1')
    total=models.IntegerField()

    def __str__(self):
        return str(self.id)+" "+str(self.checkout.id)
    


contactstatus=((0,'Active'),(1,'Done'))
class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.EmailField(max_length=54)
    phone=models.CharField(max_length=15)
    subject=models.CharField(max_length=200)
    message=models.TextField()
    status=models.IntegerField(choices=contactstatus,default=0)
    date=models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)+" "+self.name
    