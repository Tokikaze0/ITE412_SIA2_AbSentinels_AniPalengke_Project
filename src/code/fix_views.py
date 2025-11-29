
content = r'''from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import random
from core.utils import get_all_products, update_product_status, get_product, create_user_firestore, authenticate_user_firestore, get_all_farmers, verify_farmer_firestore, update_user_firestore, change_password_firestore, get_user_by_id, get_dashboard_stats, approve_product, check_expired_products, get_user_notifications
from core.ai import validate_crop
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate_user_firestore(username, password)
        if user:
            # Set session data
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            request.session['role'] = user.get('role', 'buyer')
            request.session['is_verified'] = user.get('is_verified', False)
            request.session['profile_image'] = user.get('profile_image')
            
            messages.success(request, f"Welcome back, {user['username']}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'users/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'buyer')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/register.html')
            
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store registration data in session
        request.session['pending_registration'] = {
            'username': username,
            'email': email,
            'password': password,
            'role': role,
            'otp': otp
        }
        
        # Send Verification Email
        try:
            send_mail(
                'Verify your AniPalengke Account',
                f'Your verification code is: {otp}',
                'noreply@anipalengke.com',
                [email],
                fail_silently=False,
            )
            messages.info(request, "A verification code has been sent to your email.")
            return redirect('verify_registration')
        except Exception as e:
            messages.error(request, f"Failed to send verification email: {e}")
            return render(request, 'users/register.html')

    return render(request, 'users/register.html')

def verify_registration_view(request):
    pending_reg = request.session.get('pending_registration')
    if not pending_reg:
        messages.error(request, "No pending registration found.")
        return redirect('register')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == pending_reg['otp']:
            # Create User
            user_id, error = create_user_firestore(
                pending_reg['username'], 
                pending_reg['email'], 
                pending_reg['password'], 
                pending_reg['role']
            )
            
            if user_id:
                # Auto login
                request.session['user_id'] = user_id
                request.session['username'] = pending_reg['username']
                request.session['role'] = pending_reg['role']
                request.session['is_verified'] = False
                request.session['profile_image'] = None
                
                # Clear pending session
                del request.session['pending_registration']
                
                messages.success(request, "Registration successful.")
                return redirect('index')
            else:
                messages.error(request, f"Registration failed: {error}")
                return redirect('register')
        else:
            messages.error(request, "Invalid verification code.")
            
    return render(request, 'users/verify_email.html', {
        'email': pending_reg['email'],
        'cancel_url': '/register/'
    })

def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('index')

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Run expiration check
    check_expired_products()
    
    role = request.session.get('role', 'buyer')

    if role == 'farmer':
        stats = get_dashboard_stats('farmer', username=request.user.username)
        notifications = get_user_notifications(request.user.id)
        return render(request, 'users/farmer_dashboard.html', {'stats': stats, 'notifications': notifications})
    elif role == 'admin':
        return redirect('admin_product_list')
    else:
        stats = get_dashboard_stats('buyer', user_id=request.user.id)
        return render(request, 'users/buyer_dashboard.html', {'stats': stats})

def admin_product_list(request):
    # Check if user is admin
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        messages.error(request, "Access denied.")
        return redirect('index')
        
    # Run expiration check
    check_expired_products()
        
    # Fetch pending products
    pending_products = get_all_products(status='pending')
    
    # Fetch pending farmers
    all_farmers = get_all_farmers(verified_only=False)
    pending_farmers = [f for f in all_farmers if not f.get('is_verified')]
    
    # Fetch Stats
    stats = get_dashboard_stats('admin')
    
    return render(request, 'users/admin_dashboard.html', {
        'products': pending_products,
        'farmers': pending_farmers,
        'stats': stats
    })

def admin_verify_farmer(request, user_id):
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        return redirect('index')
        
    if verify_farmer_firestore(user_id):
        messages.success(request, "Farmer verified successfully.")
    else:
        messages.error(request, "Failed to verify farmer.")
        
    return redirect('admin_product_list')

def admin_product_action(request, product_id, action):
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        return redirect('index')
        
    if action in ['approved', 'rejected']:
        if update_product_status(product_id, action):
            messages.success(request, f"Product {action}.")
        else:
            messages.error(request, "Failed to update status.")
            
    return redirect('admin_product_list')

def admin_check_ai(request, product_id):
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        return redirect('index')
        
    product = get_product(product_id)
    if product:
        ai_result = validate_crop(product.get('name'), product.get('description'), product.get('image'))
        # Clean up markdown code blocks if present
        if "```json" in ai_result:
            ai_result = ai_result.split("```json")[1].split("```")[0]
        elif "```" in ai_result:
            ai_result = ai_result.split("```")[1].split("```")[0]
            
        try:
            result_json = json.loads(ai_result)
            request.session['ai_check_result'] = result_json
            request.session['ai_check_id'] = product_id
        except:
            request.session['ai_check_result'] = {'is_valid': False, 'reason': "Raw AI response: " + ai_result}
            request.session['ai_check_id'] = product_id
            
    return redirect('admin_product_list')

def profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_id = request.session.get('user_id')
    user = get_user_by_id(user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            update_data = {
                'username': username,
                'email': email
            }
            
            if request.FILES.get('profile_image'):
                image = request.FILES['profile_image']
                fs = FileSystemStorage()
                filename = fs.save(f"profiles/{user_id}_{image.name}", image)
                update_data['profile_image'] = fs.url(filename)
            
            # Check if email is being changed
            if email != user.get('email'):
                otp = str(random.randint(100000, 999999))
                request.session['pending_email_change'] = {
                    'user_id': user_id,
                    'update_data': update_data,
                    'otp': otp
                }
                
                try:
                    send_mail(
                        'Verify Email Change',
                        f'Your verification code is: {otp}',
                        'noreply@anipalengke.com',
                        [email],
                        fail_silently=False,
                    )
                    messages.info(request, "A verification code has been sent to your new email.")
                    return redirect('verify_email_change')
                except Exception as e:
                    messages.error(request, f"Failed to send verification email: {e}")
                    return redirect('profile_settings')

            if update_user_firestore(user_id, update_data):
                # Update session data
                request.session['username'] = username
                if 'profile_image' in update_data:
                    request.session['profile_image'] = update_data['profile_image']
                messages.success(request, "Profile updated successfully.")
            else:
                messages.error(request, "Failed to update profile.")
                
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                success, msg = change_password_firestore(user_id, old_password, new_password)
                if success:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
        
        return redirect('profile_settings')
        
    return render(request, 'users/profile_settings.html', {'user_data': user})

def verify_email_change_view(request):
    pending_change = request.session.get('pending_email_change')
    if not pending_change:
        messages.error(request, "No pending email change found.")
        return redirect('profile_settings')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == pending_change['otp']:
            user_id = pending_change['user_id']
            update_data = pending_change['update_data']
            
            if update_user_firestore(user_id, update_data):
                # Update session data
                request.session['username'] = update_data['username']
                if 'profile_image' in update_data:
                    request.session['profile_image'] = update_data['profile_image']
                
                # Clear pending session
                del request.session['pending_email_change']
                
                messages.success(request, "Email verified and profile updated successfully.")
                return redirect('profile_settings')
            else:
                messages.error(request, "Failed to update profile.")
                return redirect('profile_settings')
        else:
            messages.error(request, "Invalid verification code.")
            
    return render(request, 'users/verify_email.html', {
        'email': pending_change['update_data']['email'],
        'cancel_url': '/settings/'
    })

def approve_product_view(request, product_id):
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        return redirect('index')
        
    if request.method == 'POST':
        expiration_date = request.POST.get('expiration_date')
        if approve_product(product_id, expiration_date):
            messages.success(request, "Product approved and published.")
        else:
            messages.error(request, "Failed to approve product.")
            
    return redirect('admin_product_list')
'''

with open('users/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
