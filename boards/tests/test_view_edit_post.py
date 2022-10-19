from django.forms import ModelForm
from pydoc import resolve
from django.contrib.auth.models import User   
from django.test import TestCase
from django.urls import reverse 
from ..models import Board, Post, Topic 
from ..views import PostUpdateView, topic_posts

class PostUpdateViewTestCase(TestCase):
    '''
    Base test case to be used to all 'PostUpdateView' view tests
    '''
    
    def setUp(self):
        self.board = Board.objects.create(name='Django' , description='Django board.')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('edit_post', kwargs={
            'pk': self.board.pk,
            'topic_pk': self.topic.pk,
            'post_pk': self.post.pk
        })
        
class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        '''
        Test if only logged in users can edit the posts
        '''        
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
        
class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        '''
        Create a new user different from the one who posted 
        '''
        super().setUp()
        username = 'jane'
        password = '321'
        user = User.objects.create_user(username=username, email='jane@doe.com', password=password)
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)
        
    def test_status_code(self):
        '''
        A topic should be edited only by the user.
        Unauthorized users should get a 404 repsonse (Page Not Found)
        '''
        self.assertEquals(self.response.status_code, 404)
        
class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(password=self.password)
        self.response = self.client.get(self.url)
        
class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'edited message'})
        
    def test_redirection(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url)
    
    def test_post_changed(self):
        self.post.refresh_from_db()
        self.assertEquals(self.post.message, 'edited message')
            
class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})
        
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
        
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)