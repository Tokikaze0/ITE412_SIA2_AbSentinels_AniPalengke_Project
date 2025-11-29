from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from core.utils import get_all_products, save_product, get_product, update_product, delete_product, get_reviews, add_review, check_user_bought_product
import json

def product_list(request):
    q = request.GET.get('q')
    category = request.GET.get('category')
    location = request.GET.get('location')
    products = get_all_products(q, category, location)
    
    # Search History Logic
    if q:
        history = request.session.get('search_history', [])
        if q not in history:
            history.insert(0, q)
            request.session['search_history'] = history[:5] # Keep last 5
    
    search_history = request.session.get('search_history', [])
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'search_history': search_history
    })

def product_detail(request, product_id):
    product = get_product(product_id)
    if not product:
        messages.error(request, "Product not found.")
        return redirect('product_list')
    
    # Handle Review Submission
    if request.method == 'POST' and 'rating' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to review.")
            return redirect('login')
            
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # Verify purchase
        if check_user_bought_product(request.session.get('user_id'), product_id):
            user_name = request.session.get('name') or request.session.get('username')
            if add_review(product_id, request.session.get('user_id'), user_name, rating, comment):
                messages.success(request, "Review submitted successfully!")
                # Refresh product data to get new rating
                product = get_product(product_id)
            else:
                messages.error(request, "Failed to submit review.")
        else:
            messages.error(request, "You can only review products you have purchased and received.")

    # Get Reviews
    reviews = get_reviews(product_id)
    
    # Check if user can review
    can_review = False
    if request.user.is_authenticated:
        can_review = check_user_bought_product(request.session.get('user_id'), product_id)
        # Optional: Check if already reviewed to prevent duplicates
        # for r in reviews:
        #     if r['user_id'] == request.session.get('user_id'):
        #         can_review = False
        #         break

    # Recommendations (Item 2)
    recommendations = get_all_products(category=product.get('category'))
    # Filter out current product
    recommendations = [p for p in recommendations if p['id'] != product_id][:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'recommendations': recommendations,
        'reviews': reviews,
        'can_review': can_review
    })

def add_product(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add products.")
        return redirect('login')
    
    if getattr(request.user, 'role', '') != 'farmer':
        messages.error(request, "Only farmers can add products.")
        return redirect('index')

    if not getattr(request.user, 'is_verified', False):
        messages.error(request, "Your account is not verified by admin yet.")
        return redirect('index')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        price = float(request.POST.get('price'))
        stock = int(request.POST.get('stock'))
        category = request.POST.get('category')
        location = request.POST.get('location')
        description = request.POST.get('description')
        
        # Parse JSON fields
        variations = []
        wholesale_prices = []
        try:
            v_json = request.POST.get('variations_json')
            if v_json:
                variations = json.loads(v_json)
            
            w_json = request.POST.get('wholesale_json')
            if w_json:
                wholesale_prices = json.loads(w_json)
        except json.JSONDecodeError:
            pass
        
        image_url = ''
        if request.FILES.get('image'):
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(f"products/{image.name}", image)
            image_url = fs.url(filename)
            
        product_data = {
            'name': name,
            'price': price,
            'stock': stock,
            'category': category,
            'location': location,
            'description': description,
            'image': image_url,
            'farmer_id': request.user.id,
            'farmer_name': request.user.username, # Or profile name
            'status': 'pending',
            'variations': variations,
            'wholesale_prices': wholesale_prices
        }
        
        save_product(product_data)
        messages.success(request, "Product submitted for approval.")
        return redirect('product_list') # Or farmer dashboard
        
    return render(request, 'products/add_product.html')

def edit_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    product = get_product(product_id)
    if not product:
        messages.error(request, "Product not found.")
        return redirect('product_list')
        
    # Check ownership
    if product.get('farmer_name') != request.user.username:
        messages.error(request, "You can only edit your own products.")
        return redirect('product_list')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        price = float(request.POST.get('price'))
        stock = int(request.POST.get('stock'))
        category = request.POST.get('category')
        location = request.POST.get('location')
        description = request.POST.get('description')
        
        update_data = {
            'name': name,
            'price': price,
            'stock': stock,
            'category': category,
            'location': location,
            'description': description,
            'status': 'pending' # Re-submit for approval on edit? Or keep status? Let's keep status for now or reset to pending. Usually edits require re-approval.
        }
        
        if request.FILES.get('image'):
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(f"products/{image.name}", image)
            update_data['image'] = fs.url(filename)
            
        if update_product(product_id, update_data):
            messages.success(request, "Product updated successfully.")
            return redirect('product_list')
        else:
            messages.error(request, "Failed to update product.")
            
    return render(request, 'products/edit_product.html', {'product': product})

def delete_product_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    product = get_product(product_id)
    if not product:
        messages.error(request, "Product not found.")
        return redirect('product_list')
        
    # Check ownership
    if product.get('farmer_name') != request.user.username:
        messages.error(request, "You can only delete your own products.")
        return redirect('product_list')
        
    if delete_product(product_id):
        messages.success(request, "Product deleted successfully.")
    else:
        messages.error(request, "Failed to delete product.")
        
    return redirect('product_list')
