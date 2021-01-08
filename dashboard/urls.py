from django.urls import path
from . import views
from django.views.generic import TemplateView
urlpatterns = [
    
    path('',views.dashboard_index,name='dashboard_index'),
    path('add_fund',views.add_fund,name='add_fund'),
    path('send_money',views.send_money,name='send_money'),
    path('request_money',views.request_money,name='request_money'),
    path('pending_requests',views.pending_requests,name='pending_requests'),
    path('delete_request/<int:id>',views.delete_request,name='delete_request'),
    path('approve_request/<int:id>',views.approve_request,name='approve_request'),
    path('donate_link',TemplateView.as_view(template_name='dashboard/donation-link.html'),name='donate_link')
    
    ]
