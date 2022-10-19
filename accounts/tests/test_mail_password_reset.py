from django.core import mail 
from django.contrib.auth.models import User  
from django.urls import reverse 
from django.test import TestCase

class PasswordResetMailTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='john', email='john@doe.com',password='123')
        self.email = mail.outbox 
        
    
        
        
        