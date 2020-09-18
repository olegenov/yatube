from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("contact-us/", views.user_contact, name="contact"),
    path("thank-you/", views.thankyou, name="thanks"),
]
