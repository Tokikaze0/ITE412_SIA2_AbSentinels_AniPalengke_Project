from django.shortcuts import render, redirect
from django.contrib import messages
from core.utils import get_product, save_order, get_user_orders, get_farmer_orders, update_product_stock, update_order_status
from .logistics import calculate_shipping_fee, generate_tracking_number, get_tracking_status
from .payments import create_gcash_payment_link, verify_gcash_payment
import datetime
import json
import uuid

# Mock Vouchers
VOUCHERS = {
    'WELCOME10': {'type': 'percent', 'value': 10}, # 10% off
    'FREESHIP': {'type': 'fixed', 'value': 50},    # 50 pesos off
    'ANIPALENGKE': {'type': 'fixed', 'value': 100} # 100 pesos off
}

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        p = get_product(pid)
        if p:
            subtotal = p['price'] * float(qty)
            total += subtotal
            cart_items.append({
                'product_id': pid,
                'product_name': p['name'],
                'price': p['price'],
                'quantity': qty,
                'subtotal': subtotal
            })
            
    # Voucher Logic
    voucher_code = request.session.get('voucher_code')
    discount = 0
    if voucher_code and voucher_code in VOUCHERS:
        voucher = VOUCHERS[voucher_code]
        if voucher['type'] == 'percent':
            discount = total * (voucher['value'] / 100)
        elif voucher['type'] == 'fixed':
            discount = voucher['value']
            
    # Ensure discount doesn't exceed total
    discount = min(discount, total)
    final_total = total - discount
            
    return render(request, 'orders/cart.html', {
        'cart_items': cart_items, 
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'voucher_code': voucher_code
    })

def apply_voucher(request):
    if request.method == 'POST':
        code = request.POST.get('voucher_code', '').strip().upper()
        if code in VOUCHERS:
            request.session['voucher_code'] = code
            messages.success(request, f"Voucher {code} applied successfully!")
        else:
            messages.error(request, "Invalid voucher code.")
            if 'voucher_code' in request.session:
                del request.session['voucher_code']
    return redirect('cart')

def remove_voucher(request):
    if 'voucher_code' in request.session:
        del request.session['voucher_code']
        messages.info(request, "Voucher removed.")
    return redirect('cart')

def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            qty = float(request.POST.get('quantity', 1))
            product = get_product(product_id)
            
            if not product:
                messages.error(request, "Product not found.")
                return redirect('product_list')
                
            current_stock = product.get('stock', 0)
            cart = request.session.get('cart', {})
            current_cart_qty = cart.get(product_id, 0)
            
            if current_cart_qty + qty > current_stock:
                messages.error(request, f"Not enough stock. Available: {current_stock}")
                return redirect('product_list')

            if product_id in cart:
                cart[product_id] += qty
            else:
                cart[product_id] = qty
            request.session['cart'] = cart
            messages.success(request, "Added to cart.")
        except ValueError:
            messages.error(request, "Invalid quantity.")
    return redirect('product_list')

def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            qty = float(request.POST.get('quantity', 0))
            cart = request.session.get('cart', {})
            if qty > 0:
                cart[product_id] = qty
            else:
                if product_id in cart:
                    del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, "Cart updated.")
        except ValueError:
            pass
    return redirect('cart')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, "Removed from cart.")
    return redirect('cart')

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Cart is empty.")
        return redirect('product_list')
    
    cart_items = []
    subtotal = 0
    farmer_ids = set()
    for pid, qty in cart.items():
        p = get_product(pid)
        if p:
            item_total = p['price'] * float(qty)
            subtotal += item_total
            cart_items.append({
                'product_id': pid,
                'product_name': p['name'],
                'price': p['price'],
                'quantity': qty,
                'subtotal': item_total,
                'farmer_id': p.get('farmer_id'),
                'farmer_name': p.get('farmer_name')
            })
            if p.get('farmer_id'):
                farmer_ids.add(p.get('farmer_id'))
    
    # Mock location for fee calculation (in real app, get from selected address)
    location = "Alcate" 
    delivery_fee = calculate_shipping_fee(location)
    
    # Voucher Logic
    voucher_code = request.session.get('voucher_code')
    discount = 0
    if voucher_code and voucher_code in VOUCHERS:
        voucher = VOUCHERS[voucher_code]
        if voucher['type'] == 'percent':
            discount = subtotal * (voucher['value'] / 100)
        elif voucher['type'] == 'fixed':
            discount = voucher['value']
            
    # Ensure discount doesn't exceed subtotal
    discount = min(discount, subtotal)
    
    total = subtotal + delivery_fee - discount
    
    # Mock addresses
    addresses = [
        {'id': '1', 'label': 'Home', 'address': '123 Main St, Alcate', 'is_default': True},
        {'id': '2', 'label': 'Office', 'address': '456 Work Ave, Bayani', 'is_default': False},
    ]
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Prepare order data
        order_data = {
            'user_id': request.user.id if request.user.is_authenticated else 'guest',
            'user_name': request.user.username if request.user.is_authenticated else 'Guest',
            'items': cart_items,
            'farmer_ids': list(farmer_ids),
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'discount': discount,
            'total': total,
            'payment_method': payment_method,
            'status': 'Pending',
            'address': "123 Main St, Alcate", # Mock
            'tracking_number': generate_tracking_number(),
            'courier': 'J&T Express' # Default mock courier
        }
        
        if payment_method == 'gcash':
            # Use PayMongo to create a payment link
            payment_id, checkout_url = create_gcash_payment_link(total, f"Order for {request.user.username}")
            
            if checkout_url:
                # Store order data in session to save after payment
                request.session['pending_order'] = order_data
                request.session['payment_id'] = payment_id
                return redirect(checkout_url)
            else:
                messages.error(request, "Failed to initialize payment. Please try again.")
                return redirect('checkout')
        else:
            # COD
            order_data['payment_status'] = 'Pending'
            order_data['is_escrow'] = False
            
            # Deduct stock
            for item in cart_items:
                update_product_stock(item['product_id'], item['quantity'])
                
            save_order(order_data)
            
            # Clear cart
            request.session['cart'] = {}
            if 'voucher_code' in request.session:
                del request.session['voucher_code']
                
            messages.success(request, "Order placed successfully!")
            return redirect('order_history')
    
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'discount': discount,
        'voucher_code': voucher_code,
        'total': total,
        'addresses': addresses
    })

def payment_success(request):
    """
    Callback for successful payment.
    """
    # In a real integration, PayMongo would call a webhook.
    # For this simple flow, we check the session or query params.
    
    # If using the mock flow or redirect flow
    pending_order = request.session.get('pending_order')
    payment_id = request.session.get('payment_id')
    
    if pending_order and payment_id:
        # Verify payment status
        if verify_gcash_payment(payment_id):
            pending_order['status'] = 'Paid'
            pending_order['payment_status'] = 'Escrow'
            pending_order['is_escrow'] = True
            
            save_order(pending_order)
            
            # Update stock
            for item in pending_order['items']:
                update_product_stock(item['product_id'], item['quantity'])
            
            # Clear session
            del request.session['pending_order']
            del request.session['payment_id']
            request.session['cart'] = {}
            if 'voucher_code' in request.session:
                del request.session['voucher_code']
                
            messages.success(request, "Payment successful! Order placed.")
            return redirect('order_history')
        else:
            messages.error(request, "Payment verification failed.")
            return redirect('checkout')
            
    return redirect('home')

def payment_failed(request):
    messages.error(request, "Payment was cancelled or failed.")
    return redirect('checkout')

def process_payment(request):
    if request.method == 'POST':
        order_data_json = request.POST.get('order_data')
        if order_data_json:
            order_data = json.loads(order_data_json)
            
            # Simulate payment success
            order_data['payment_status'] = 'Escrow' # Funds held
            order_data['is_escrow'] = True
            order_data['status'] = 'Paid' # Or 'Processing'
            
            # Deduct stock
            for item in order_data['items']:
                update_product_stock(item['product_id'], item['quantity'])
            
            save_order(order_data)
            
            # Clear cart
            request.session['cart'] = {}
            if 'voucher_code' in request.session:
                del request.session['voucher_code']
                
            messages.success(request, "Payment successful! Funds are held in Escrow until delivery.")
            return redirect('order_history')
    return redirect('checkout')

def release_funds(request, order_id):
    # In a real app, verify user owns order and update Firestore
    # For prototype, we just show a message
    messages.success(request, "Funds released to seller. Transaction completed.")
    return redirect('order_history')

def track_order(request, order_id):
    # Mock order retrieval
    if getattr(request.user, 'profile', None) and request.user.profile.role == 'farmer':
        orders = get_farmer_orders(request.user.id)
    else:
        orders = get_user_orders(request.user.id)
        
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order:
        messages.error(request, "Order not found.")
        return redirect('order_history')
        
    return render(request, 'orders/track_order.html', {'order': order})

def print_waybill(request, order_id):
    # Mock order retrieval
    if getattr(request.user, 'profile', None) and request.user.profile.role == 'farmer':
        orders = get_farmer_orders(request.user.id)
    else:
        orders = get_user_orders(request.user.id)
        
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order:
        messages.error(request, "Order not found.")
        return redirect('order_history')
        
    return render(request, 'orders/waybill.html', {'order': order})

def _create_order_data(request, payment_method, tracking_number):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0
    for pid, qty in cart.items():
        p = get_product(pid)
        if p:
            item_total = p['price'] * float(qty)
            subtotal += item_total
            cart_items.append({
                'product_id': pid,
                'product_name': p['name'],
                'price': p['price'],
                'quantity': qty,
                'subtotal': item_total,
                'image': p.get('image', '')
            })
            # Deduct stock
            update_product_stock(pid, qty)
    
    # Use Lalamove for delivery fee calculation
    from .lalamove import LalamoveService
    location = "Alcate" # Mock destination
    pickup = "Farm Location" # Mock pickup
    
    try:
        lalamove_quote = LalamoveService.get_quotation(pickup, location)
        delivery_fee = lalamove_quote['price_breakdown']['total']
        carrier_ref = lalamove_quote['quotation_id']
    except:
        delivery_fee = calculate_shipping_fee(location)
        carrier_ref = "INTERNAL"

    total = subtotal + delivery_fee
    
    user_id = request.user.id if request.user.is_authenticated else 'guest'
    username = request.user.username if request.user.is_authenticated else 'Guest'

    return {
        'user_id': user_id,
        'username': username,
        'items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'payment_method': payment_method,
        'tracking_number': tracking_number,
        'status': 'Placed',
        'shipping_address': '123 Main St, Alcate', # Mock
        'carrier': 'Lalamove',
        'carrier_ref': carrier_ref,
        'created_at': datetime.datetime.now()
    }

def place_order(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Recalculate total for payment link
        cart = request.session.get('cart', {})
        subtotal = 0
        for pid, qty in cart.items():
            p = get_product(pid)
            if p:
                subtotal += p['price'] * float(qty)
        location = "Alcate"
        total_amount = subtotal + calculate_shipping_fee(location)

        if payment_method == 'gcash':
            payment_id, redirect_url = create_gcash_payment_link(total_amount, "Order Payment")
            return redirect(redirect_url)
        
        # COD
        tracking_number = generate_tracking_number()
        order_data = _create_order_data(request, 'COD', tracking_number)
        save_order(order_data)
        
        request.session['cart'] = {}
        messages.success(request, f"Order placed successfully! Tracking No: {tracking_number}")
        return redirect('order_history') 
    return redirect('checkout')

def gcash_mock_view(request, payment_id):
    amount = request.GET.get('amount', '0.00')
    return render(request, 'orders/gcash_mock.html', {'payment_id': payment_id, 'amount': amount})

def gcash_confirm_view(request, payment_id):
    if request.method == 'POST':
        tracking_number = generate_tracking_number()
        order_data = _create_order_data(request, 'GCash', tracking_number)
        order_data['payment_id'] = payment_id
        order_data['status'] = 'Paid'
        save_order(order_data)
        
        request.session['cart'] = {}
        messages.success(request, f"Payment Successful! Order placed. Tracking No: {tracking_number}")
        return redirect('order_history')
    return redirect('index')

def order_history(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to view order history.")
        return redirect('login')
    
    if getattr(request.user, 'profile', None) and request.user.profile.role == 'farmer':
        orders = get_farmer_orders(request.user.id)
        # Filter items in each order to only show products from this farmer
        for order in orders:
            order['items'] = [item for item in order.get('items', []) if item.get('farmer_id') == request.user.id]
            # Recalculate total for this farmer's portion (optional, but good for display)
            order['farmer_total'] = sum(item['subtotal'] for item in order['items'])
            
        return render(request, 'orders/farmer_order_history.html', {'orders': orders})
    else:
        orders = get_user_orders(request.user.id)
        return render(request, 'orders/order_history.html', {'orders': orders})

def update_order_status_view(request, order_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in.")
            return redirect('login')
            
        # Check if user is farmer
        if not (getattr(request.user, 'profile', None) and request.user.profile.role == 'farmer'):
             messages.error(request, "Only farmers can update order status.")
             return redirect('order_history')

        new_status = request.POST.get('status')
        if new_status:
            if update_order_status(order_id, new_status):
                messages.success(request, f"Order status updated to {new_status}.")
            else:
                messages.error(request, "Failed to update order status.")
        
    return redirect('track_order', order_id=order_id)

def cancel_order(request, order_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in.")
            return redirect('login')
        
        orders = get_user_orders(request.user.id)
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if not order:
            messages.error(request, "Order not found.")
            return redirect('order_history')
            
        if order['status'] == 'Pending':
            if update_order_status(order_id, 'Cancelled'):
                messages.success(request, "Order cancelled successfully.")
            else:
                messages.error(request, "Failed to cancel order.")
        else:
            messages.error(request, "Cannot cancel order at this stage.")
            
    return redirect('order_history')

def request_refund(request, order_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in.")
            return redirect('login')
            
        orders = get_user_orders(request.user.id)
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if not order:
            messages.error(request, "Order not found.")
            return redirect('order_history')
            
        # Allow refund request if Delivered
        if order['status'] == 'Delivered':
            if update_order_status(order_id, 'Refund Requested'):
                messages.success(request, "Refund requested successfully.")
            else:
                messages.error(request, "Failed to request refund.")
        else:
            messages.error(request, "Cannot request refund for this order.")
            
    return redirect('order_history')

