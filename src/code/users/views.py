from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import random
import csv
from django.http import HttpResponse
from core.utils import get_all_products, update_product_status, get_product, create_user_firestore, authenticate_user_firestore, get_all_farmers, verify_farmer_firestore, update_user_firestore, change_password_firestore, get_user_by_id, get_dashboard_stats, approve_product, check_expired_products, get_user_notifications, mark_notification_read, get_db, get_user_by_email, reset_password_firestore
from core.ai import validate_crop
import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
import uuid
from firebase_admin import firestore
from datetime import datetime

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate_user_firestore(username, password)
        if user:
            # Set session data
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            request.session['name'] = user.get('name', user['username']) # Store name
            request.session['role'] = user.get('role', 'buyer')
            request.session['location'] = user.get('location', '')
            request.session['is_verified'] = user.get('is_verified', False)
            request.session['profile_image'] = user.get('profile_image')
            
            display_name = user.get('name') or user['username']
            messages.success(request, f"Welcome back, {display_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'users/login.html')

def google_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            display_name = data.get('displayName')
            uid = data.get('uid')
            
            if not email:
                return JsonResponse({'success': False, 'error': 'Email required'})
                
            # Check if user exists
            db = get_db()
            if not db:
                 return JsonResponse({'success': False, 'error': 'Database unavailable'})

            users_ref = db.collection('users')
            # Check by email
            docs = users_ref.where('email', '==', email).stream()
            user_doc = None
            for doc in docs:
                user_doc = doc
                break
                
            if user_doc:
                # Login existing user
                user_data = user_doc.to_dict()
                request.session['user_id'] = user_doc.id
                request.session['username'] = user_data.get('username')
                request.session['name'] = user_data.get('name', user_data.get('username'))
                request.session['role'] = user_data.get('role', 'buyer')
                request.session['location'] = user_data.get('location', '')
                request.session['is_verified'] = user_data.get('is_verified', False)
                request.session['profile_image'] = user_data.get('profile_image')
                return JsonResponse({'success': True})
            else:
                # Create new user
                username = display_name.replace(' ', '') if display_name else email.split('@')[0]
                # Check if username exists
                if len(list(users_ref.where('username', '==', username).stream())) > 0:
                    username = f"{username}{random.randint(1000, 9999)}"
                
                new_user_data = {
                    'username': username,
                    'email': email,
                    'password': make_password(str(uuid.uuid4())), # Random password
                    'role': 'buyer', # Force buyer role
                    'is_verified': False,
                    'location': '',
                    'name': display_name or username, # Save display name
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'auth_provider': 'google'
                }
                
                doc_ref = users_ref.add(new_user_data)
                user_id = doc_ref[1].id
                
                request.session['user_id'] = user_id
                request.session['username'] = username
                request.session['name'] = display_name or username
                request.session['role'] = 'buyer'
                request.session['location'] = ''
                request.session['is_verified'] = False
                
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'buyer')
        location = request.POST.get('location', '')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'users/register.html')
            
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store registration data in session
        request.session['pending_registration'] = {
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'role': role,
            'location': location,
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
                pending_reg['role'],
                is_verified=False,
                location=pending_reg.get('location', ''),
                name=pending_reg.get('name', '')
            )
            
            if user_id:
                # Auto login
                request.session['user_id'] = user_id
                request.session['username'] = pending_reg['username']
                request.session['name'] = pending_reg.get('name', '') # Store name in session
                request.session['role'] = pending_reg['role']
                request.session['location'] = pending_reg.get('location', '')
                request.session['is_verified'] = False
                request.session['profile_image'] = None
                
                # Clear pending session
                del request.session['pending_registration']
                
                messages.success(request, "Registration successful.")
                return redirect('dashboard')
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
    
    # Get AI Check Result (Pop to show only once)
    ai_check_result = request.session.pop('ai_check_result', None)
    ai_check_id = request.session.pop('ai_check_id', None)
    
    return render(request, 'users/admin_dashboard.html', {
        'products': pending_products,
        'farmers': pending_farmers,
        'stats': stats,
        'ai_check_result': ai_check_result,
        'ai_check_id': ai_check_id
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
        print(f"Checking AI for product: {product.get('name')}")
        ai_result = validate_crop(product.get('name'), product.get('description'), product.get('image'))
        print(f"AI Result: {ai_result}")
        
        # Clean up markdown code blocks if present
        if "```json" in ai_result:
            ai_result = ai_result.split("```json")[1].split("```")[0]
        elif "```" in ai_result:
            ai_result = ai_result.split("```")[1].split("```")[0]
            
        try:
            result_json = json.loads(ai_result)
            request.session['ai_check_result'] = result_json
            request.session['ai_check_id'] = product_id
            print("Session updated with AI result")
        except Exception as e:
            print(f"JSON Parse Error: {e}")
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
            name = request.POST.get('name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            location = request.POST.get('location', '')
            
            update_data = {
                'name': name,
                'username': username,
                'email': email,
                'location': location
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
                request.session['name'] = name
                request.session['username'] = username
                request.session['location'] = location
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
        print(f"POST data: {request.POST}")
        expiration_date = request.POST.get('expiration_date')
        
        if not expiration_date:
            messages.error(request, "Expiration date is required.")
            return redirect('admin_product_list')
            
        # Validate date
        try:
            exp_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
            if exp_date < datetime.now().date():
                messages.error(request, "Expiration date must be today or in the future.")
                return redirect('admin_product_list')
        except ValueError:
             messages.error(request, "Invalid date format.")
             return redirect('admin_product_list')
            
        print(f"Approving product {product_id} with expiration {expiration_date}")
        if approve_product(product_id, expiration_date):
            messages.success(request, f"Product approved. Expires on {expiration_date}.")
        else:
            messages.error(request, "Failed to approve product. Check console for errors.")
            
    return redirect('admin_product_list')

def mark_notification_read_view(request, notification_id):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if mark_notification_read(notification_id):
        pass
    else:
        messages.error(request, "Failed to dismiss notification.")
        
    return redirect('dashboard')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_user_by_email(email)
        
        if user:
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Store in session
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['reset_user_id'] = user['id']
            
            # Send Email
            try:
                send_mail(
                    'Password Reset Code - AniPalengke',
                    f'Your password reset code is: {otp}',
                    'noreply@anipalengke.com',
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f"Reset code sent to {email}")
                return redirect('verify_reset_otp')
            except Exception as e:
                messages.error(request, f"Failed to send email: {e}")
        else:
            messages.error(request, "Email not found.")
            
    return render(request, 'users/forgot_password.html')

def verify_reset_otp_view(request):
    if 'reset_otp' not in request.session:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == request.session.get('reset_otp'):
            request.session['reset_verified'] = True
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid code.")
            
    return render(request, 'users/verify_reset_otp.html', {'email': request.session.get('reset_email')})

def reset_password_view(request):
    if not request.session.get('reset_verified'):
        return redirect('forgot_password')
        
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user_id = request.session.get('reset_user_id')
            if reset_password_firestore(user_id, new_password):
                # Clear session
                del request.session['reset_otp']
                del request.session['reset_email']
                del request.session['reset_user_id']
                del request.session['reset_verified']
                
                messages.success(request, "Password reset successfully. Please login.")
                return redirect('login')
            else:
                messages.error(request, "Failed to reset password.")
                
    return render(request, 'users/reset_password.html')

def admin_reports(request):
    if not request.user.is_authenticated or request.session.get('role') != 'admin':
        return redirect('index')

    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

        writer = csv.writer(response)
        db = get_db()

        if report_type == 'users':
            writer.writerow(['Username', 'Email', 'Role', 'Is Verified', 'Date Joined'])
            users = db.collection('users').stream()
            for user in users:
                u = user.to_dict()
                # Simple date filtering could be added here if 'created_at' is consistent
                writer.writerow([u.get('username'), u.get('email'), u.get('role'), u.get('is_verified'), u.get('created_at', 'N/A')])

        elif report_type == 'products':
            writer.writerow(['Name', 'Farmer', 'Category', 'Price', 'Stock', 'Status', 'Expiration Date'])
            products = db.collection('products').stream()
            for product in products:
                p = product.to_dict()
                writer.writerow([p.get('name'), p.get('farmer_name'), p.get('category'), p.get('price'), p.get('stock'), p.get('status'), p.get('expiration_date', 'N/A')])

        elif report_type == 'orders':
            writer.writerow(['Order ID', 'Buyer', 'Total Amount', 'Status', 'Date'])
            orders = db.collection('orders').stream()
            for order in orders:
                o = order.to_dict()
                writer.writerow([order.id, o.get('buyer_name'), o.get('total_amount'), o.get('status'), o.get('created_at', 'N/A')])

        return response

    return render(request, 'users/admin_reports.html')


