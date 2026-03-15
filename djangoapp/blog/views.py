from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import DetailView, ListView




PER_PAGE = 9

class PostListView(ListView):
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published() #type:ignore        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Home - ',
        })
        return context
    

class CreatedByListView(PostListView):
   def __init__(self, **kwargs: Any) -> None:
       super().__init__(**kwargs)
       self._temp_context: dict[str, Any] = {}

   def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()
        if user is None:
            raise Http404()
        
        self._temp_context.update({
            'author_pk':author_pk,
            'user': user
        })
        return super().get(request, *args, **kwargs)
   
   def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self._temp_context['user']
        user_full_name = user.username
        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = f'Posts de {user_full_name} - '

        context.update({
            'page_title':page_title,
        })
        return context
   
   def get_queryset(self) -> QuerySet[Any]:
       qs = super().get_queryset()
       qs = qs.filter(created_by__pk=self._temp_context['user'].pk)
       return qs


class CategoryListView(PostListView):
    allow_empty = False
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title = f'Posts da categoria {self.object_list[0].category.name} - ' #type:ignore
        context.update({
            'page_title':page_title,
        })
        return context
        
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs.get('slug')
        qs = qs.filter(category__slug=slug)
        return qs
    

class TagListView(PostListView):
    allow_empty = False
    
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs.get('slug')
        qs = qs.filter(tags__slug=slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        page_title = (
            f'Posts da tag {self.object_list[0] #type:ignore
                            .tags.filter(slug=slug).first().name} - '
                            )
        context.update({
            'page_title':page_title,
        })
        return context

class SearchListView(PostListView):

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:

        return super().get_queryset().filter(
            # Título contém search_value OU
            # Excerpt contém search_value OU
            # Conteúdo contém search_value 
            Q(title__icontains=self._search_value) |
            Q(excerpt__icontains=self._search_value) |
            Q(content__icontains=self._search_value)
        )[:PER_PAGE]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self._search_value
        page_title = f'{search_value[:30]} - Search - '
        context.update({
            'page_title': page_title,
            'search_value': search_value,
        })
        return context
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self._search_value == '':
            return redirect('blog:index')
        return super().get(request, *args, **kwargs)
    

def search(request):
    search_value = request.GET.get('search').strip()
    posts = (
        Post.objects.get_published()  #type:ignore
        .filter(
            # Título contém search_value OU
            # Excerpt contém search_value OU
            # Conteúdo contém search_value 
            Q(title__icontains=search_value) |
            Q(excerpt__icontains=search_value) |
            Q(content__icontains=search_value)
        )[:PER_PAGE]
    )

    page_title = f'{search_value[:30]} - '


    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': posts,
            'page_title': page_title,
            'search_value': search_value,
        }
    )

class PageDetailView(DetailView):
    model = Page
    template_name = 'blog/pages/page.html'
    slug_field = 'slug'
    context_object_name = 'page'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        page_title = f'{page.title} - Página - '  #type:ignore
        context.update({
            'page_title':page_title,
        })
        return context
    def get_queryset(self) -> QuerySet[Any]:
        return (
            super().get_queryset()
            .filter(is_published=True))


def post(request, slug):
    post_obj = Post.objects.get_published().filter(slug=slug).first() #type:ignore
    
    if post_obj is None:
        raise Http404()

    page_title = f'{post_obj.title} - '

    return render(
        request,
        'blog/pages/post.html', 
        {
            'post': post_obj,
            'page_title': page_title,
        }
    )