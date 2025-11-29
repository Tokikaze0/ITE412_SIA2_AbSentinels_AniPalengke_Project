from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import get_all_posts, create_post_firestore, get_post, add_comment_firestore

def community_feed(request):
    if not request.user.is_authenticated:
        return redirect('login')
    posts = get_all_posts()
    return render(request, 'community/feed.html', {'posts': posts})

def create_post(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        post_type = request.POST.get('post_type', 'discussion')
        
        # Only admin can create announcements
        if post_type == 'announcement' and getattr(request.user, 'role', '') != 'admin':
            messages.error(request, "Only admins can create announcements.")
            return redirect('community_feed')
            
        create_post_firestore(
            title=title,
            content=content,
            author_id=request.user.id,
            author_name=request.user.name,
            post_type=post_type
        )
        messages.success(request, "Post created successfully.")
        return redirect('community_feed')
        
    return render(request, 'community/create_post.html')

def post_detail(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    post = get_post(post_id)
    if not post:
        messages.error(request, "Post not found.")
        return redirect('community_feed')
        
    return render(request, 'community/post_detail.html', {'post': post})

def add_comment(request, post_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        content = request.POST.get('content')
        
        add_comment_firestore(
            post_id=post_id,
            content=content,
            author_id=request.user.id,
            author_name=request.user.name
        )
        messages.success(request, "Comment added.")
        return redirect('post_detail', post_id=post_id)
    return redirect('community_feed')
