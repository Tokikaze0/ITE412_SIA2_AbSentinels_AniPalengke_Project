from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import get_all_products, get_all_articles, get_article
from .ai import chat_with_gemini, analyze_image
from .models import Article

def index(request):
    # Get first 4 products for display as featured
    all_products = get_all_products()
    featured_products = all_products[:4] if all_products else []
    return render(request, 'core/index.html', {'featured_products': featured_products})

def knowledge_base(request):
    articles = get_all_articles()
    return render(request, 'core/knowledge.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_article(article_id)
    if not article:
        return redirect('knowledge_base')
    return render(request, 'core/article_detail.html', {'article': article})

@login_required(login_url='login')
def ai_assistant(request):
    chat_history = request.session.get('chat_history', [])
    return render(request, 'core/ai_assistant.html', {'chat_history': chat_history})

@login_required(login_url='login')
def ai_chat(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        if prompt:
            # Get history
            chat_history = request.session.get('chat_history', [])
            
            # Add user message
            chat_history.append({'role': 'user', 'content': prompt})
            
            # Get AI response
            ai_response = chat_with_gemini(prompt)
            
            # Add AI message
            chat_history.append({'role': 'ai', 'content': ai_response})
            
            # Save back to session
            request.session['chat_history'] = chat_history
            
    return redirect('ai_assistant')

def ai_clear_chat(request):
    if 'chat_history' in request.session:
        del request.session['chat_history']
    return redirect('ai_assistant')

def ai_analyze(request):
    analysis_result = None
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        analysis_result = analyze_image(image)
        
        # Optional: Add analysis result to chat history too?
        # For now, let's keep it separate or pass it to context
        
    chat_history = request.session.get('chat_history', [])
    return render(request, 'core/ai_assistant.html', {
        'chat_history': chat_history,
        'analysis_response': analysis_result
    })
