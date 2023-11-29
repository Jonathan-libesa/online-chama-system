from django.urls import path
from.import views

urlpatterns = [
    #path('',views.homeview,name="home"),
    #path('contact_open_heavens_ministry',views.contact,name="contact_open"),
    #path('donate_view/',views.donate,name="give"),
    path('payment/success/',views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
 ] 