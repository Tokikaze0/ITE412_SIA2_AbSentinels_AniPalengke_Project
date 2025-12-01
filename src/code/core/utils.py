import firebase_admin
from firebase_admin import firestore
from django.conf import settings

def get_db():
    try:
        if not firebase_admin._apps:
            return None
        return firestore.client()
    except Exception as e:
        print(f"Firestore error: {e}")
        return None

# Mock Data
MOCK_PRODUCTS = [
    {'id': '1', 'name': 'Tomatoes', 'price': 50, 'stock': 100, 'category': 'Gulay', 'location': 'Bulacan', 'farmer_name': 'Farmer John', 'image': '/static/images/kamatis.jpg'},
    {'id': '2', 'name': 'Cassava', 'price': 35, 'stock': 50, 'category': 'Root Crops', 'location': 'Pampanga', 'farmer_name': 'Farmer Jane', 'image': '/static/images/cassava.jpg'},
    {'id': '4', 'name': 'Eggplant', 'price': 40, 'stock': 80, 'category': 'Gulay', 'location': 'Batangas', 'farmer_name': 'Farmer Mario', 'image': '/static/images/eggplant.jpg'},
]

MOCK_CART = {} # user_id -> list of items

def get_all_products(query=None, category=None, location=None, status='approved'):
    db = get_db()
    if db:
        try:
            ref = db.collection('products')
            # Filter by status (default: approved)
            if status:
                ref = ref.where('status', '==', status)
                
            if category:
                ref = ref.where('category', '==', category)
            if location:
                ref = ref.where('location', '==', location)
            
            docs = ref.stream()
            products = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
            if query:
                q = query.lower()
                products = [p for p in products if q in p.get('name', '').lower() or q in p.get('farmer_name', '').lower()]
            
            return products
        except Exception as e:
            print(f"Firestore read error: {e}")
    
    # Fallback to mock
    res = MOCK_PRODUCTS
    if category:
        res = [p for p in res if p['category'] == category]
    if location:
        res = [p for p in res if p['location'] == location]
    if query:
        q = query.lower()
        res = [p for p in res if q in p['name'].lower() or q in p['farmer_name'].lower()]
    return res

def get_flash_sale_products():
    db = get_db()
    if db:
        try:
            ref = db.collection('products')
            # Filter by is_flash_sale = True
            ref = ref.where('is_flash_sale', '==', True).where('status', '==', 'approved')
            
            docs = ref.stream()
            products = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            return products
        except Exception as e:
            print(f"Firestore read error (flash sales): {e}")
            return []
    return []

def save_product(product_data):
    db = get_db()
    if db:
        try:
            # Add timestamp
            import datetime
            product_data['created_at'] = datetime.datetime.now()
            if 'status' not in product_data:
                product_data['status'] = 'pending'
            
            # Save to 'products' collection
            doc_ref = db.collection('products').add(product_data)
            return doc_ref[1].id
        except Exception as e:
            print(f"Firestore write error: {e}")
            return None
    return "mock_product_id"

def update_product_status(product_id, status):
    db = get_db()
    if db:
        try:
            db.collection('products').document(product_id).update({'status': status})
            return True
        except Exception as e:
            print(f"Firestore update error: {e}")
            return False
    return True

def update_product_stock(product_id, quantity_sold):
    """Deducts quantity_sold from product stock."""
    db = get_db()
    if db:
        try:
            ref = db.collection('products').document(product_id)
            # Use transaction for atomic update in real app, simple get/update for now
            doc = ref.get()
            if doc.exists:
                current_stock = doc.to_dict().get('stock', 0)
                new_stock = max(0, current_stock - quantity_sold)
                ref.update({'stock': new_stock})
                return True
        except Exception as e:
            print(f"Firestore stock update error: {e}")
    return False

def update_product(product_id, data):
    db = get_db()
    if db:
        try:
            db.collection('products').document(product_id).update(data)
            return True
        except Exception as e:
            print(f"Update product error: {e}")
            return False
    return False

def delete_product(product_id):
    db = get_db()
    if db:
        try:
            db.collection('products').document(product_id).delete()
            return True
        except Exception as e:
            print(f"Delete product error: {e}")
            return False
    return False

def get_product(product_id):
    db = get_db()
    if db:
        try:
            doc = db.collection('products').document(product_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
        except Exception:
            pass
    
    for p in MOCK_PRODUCTS:
        if p['id'] == product_id:
            return p
    return None

from django.contrib.auth.hashers import make_password, check_password

def create_user_firestore(username, email, password, role='buyer', is_verified=False, location='', name=''):
    db = get_db()
    if db:
        try:
            # Check if username exists
            users_ref = db.collection('users')
            if users_ref.where('username', '==', username).get():
                return None, "Username already exists"
            
            # Check if email exists
            if users_ref.where('email', '==', email).get():
                return None, "Email already exists"
            
            user_data = {
                'username': username,
                'email': email,
                'password': make_password(password),
                'role': role,
                'is_verified': is_verified,
                'location': location,
                'name': name, # Save name
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref = users_ref.add(user_data)
            return doc_ref[1].id, None
        except Exception as e:
            return None, str(e)
    return None, "Database unavailable"

def authenticate_user_firestore(username, password):
    db = get_db()
    if db:
        try:
            users_ref = db.collection('users')
            docs = users_ref.where('username', '==', username).stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                if check_password(password, user_data.get('password')):
                    return {'id': doc.id, **user_data}
            return None
        except Exception as e:
            print(f"Auth error: {e}")
            return None
    return None

def update_user_firestore(user_id, data):
    db = get_db()
    if db:
        try:
            db.collection('users').document(user_id).update(data)
            return True
        except Exception as e:
            print(f"Update user error: {e}")
            return False
    return False

def change_password_firestore(user_id, old_password, new_password):
    db = get_db()
    if db:
        try:
            doc_ref = db.collection('users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                user_data = doc.to_dict()
                if check_password(old_password, user_data.get('password')):
                    doc_ref.update({'password': make_password(new_password)})
                    return True, "Password updated successfully"
                else:
                    return False, "Incorrect old password"
            return False, "User not found"
        except Exception as e:
            return False, str(e)
    return False, "Database error"

def reset_password_firestore(user_id, new_password):
    db = get_db()
    if db:
        try:
            db.collection('users').document(user_id).update({
                'password': make_password(new_password)
            })
            return True
        except Exception as e:
            print(f"Reset password error: {e}")
            return False
    return False

def get_user_by_email(email):
    db = get_db()
    if db:
        try:
            users_ref = db.collection('users')
            docs = users_ref.where('email', '==', email).stream()
            for doc in docs:
                return {'id': doc.id, **doc.to_dict()}
        except Exception as e:
            print(f"Get user by email error: {e}")
    return None

def get_user_by_id(user_id):
    db = get_db()
    if db:
        try:
            doc = db.collection('users').document(user_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
        except Exception:
            pass
    return None

def get_all_farmers(verified_only=False):
    db = get_db()
    if db:
        try:
            ref = db.collection('users').where('role', '==', 'farmer')
            if verified_only:
                ref = ref.where('is_verified', '==', True)
            docs = ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            pass
    return []

def verify_farmer_firestore(user_id):
    db = get_db()
    if db:
        try:
            db.collection('users').document(user_id).update({'is_verified': True})
            return True
        except Exception:
            pass
    return False

def save_order(order_data):
    db = get_db()
    if db:
        try:
            # Add timestamp
            import datetime
            order_data['created_at'] = datetime.datetime.now()
            
            # Save to 'orders' collection
            doc_ref = db.collection('orders').add(order_data)
            return doc_ref[1].id # Return document ID
        except Exception as e:
            print(f"Firestore write error: {e}")
            return None
    return "mock_order_id"

def get_user_orders(user_id):
    db = get_db()
    if db:
        try:
            orders_ref = db.collection('orders')
            query = orders_ref.where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Firestore read error: {e}")
            # Fallback if index is missing or other error
            try:
                orders_ref = db.collection('orders')
                query = orders_ref.where('user_id', '==', user_id)
                docs = query.stream()
                return sorted([{'id': doc.id, **doc.to_dict()} for doc in docs], key=lambda x: x.get('created_at', ''), reverse=True)
            except Exception:
                pass
    return []

def get_farmer_orders(farmer_id):
    db = get_db()
    if db:
        try:
            orders_ref = db.collection('orders')
            # Note: array-contains requires an index in Firestore usually
            query = orders_ref.where('farmer_ids', 'array_contains', farmer_id).order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Firestore farmer read error: {e}")
            # Fallback: Get all orders and filter in python (inefficient but works for prototype)
            try:
                orders_ref = db.collection('orders')
                docs = orders_ref.stream()
                orders = []
                for doc in docs:
                    data = doc.to_dict()
                    if farmer_id in data.get('farmer_ids', []):
                        orders.append({'id': doc.id, **data})
                return sorted(orders, key=lambda x: x.get('created_at', ''), reverse=True)
            except Exception:
                pass
    return []

def add_to_cart(user_id, product_id, quantity):
    # In a real app, store in Firestore 'carts' collection
    # For prototype with session auth, we can use session or a mock dict
    # Let's use session in the view, but here we simulate DB logic
    pass 

def get_all_posts():
    db = get_db()
    if db:
        try:
            posts_ref = db.collection('posts').order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = posts_ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception:
            # Fallback if index missing
            try:
                docs = db.collection('posts').stream()
                return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            except:
                pass
    return []

def create_post_firestore(title, content, author_id, author_name, post_type='discussion', image_url=None):
    db = get_db()
    if db:
        try:
            data = {
                'title': title,
                'content': content,
                'author_id': author_id,
                'author_name': author_name,
                'post_type': post_type,
                'created_at': firestore.SERVER_TIMESTAMP,
                'comments': [],
                'image_url': image_url
            }
            db.collection('posts').add(data)
            return True
        except Exception:
            pass
    return False

def get_post(post_id):
    db = get_db()
    if db:
        try:
            doc = db.collection('posts').document(post_id).get()
            if doc.exists:
                data = doc.to_dict()
                # Convert comment timestamps from string to datetime
                if 'comments' in data:
                    import datetime
                    for comment in data['comments']:
                        if isinstance(comment.get('created_at'), str):
                            try:
                                comment['created_at'] = datetime.datetime.fromisoformat(comment['created_at'])
                            except ValueError:
                                pass
                return {'id': doc.id, **data}
        except Exception:
            pass
    return None

def add_comment_firestore(post_id, content, author_id, author_name):
    db = get_db()
    if db:
        try:
            import datetime
            comment = {
                'content': content,
                'author_id': author_id,
                'author_name': author_name,
                'created_at': datetime.datetime.now().isoformat()
            }
            # Use arrayUnion to add comment to 'comments' array field
            db.collection('posts').document(post_id).update({
                'comments': firestore.ArrayUnion([comment])
            })
            return True
        except Exception:
            pass
    return False


def get_dashboard_stats(role, user_id=None, username=None):
    db = get_db()
    stats = {}
    
    if not db:
        return stats

    try:
        if role == 'admin':
            # Users
            users_ref = db.collection('users')
            # Note: stream() gets all docs, count() aggregation is better but requires newer SDK/indexes
            # For prototype, len(list()) is fine
            all_users = list(users_ref.stream())
            stats['total_users'] = len(all_users)
            stats['farmers'] = len([u for u in all_users if u.to_dict().get('role') == 'farmer'])
            stats['buyers'] = len([u for u in all_users if u.to_dict().get('role') == 'buyer'])
            
            # Products
            products_ref = db.collection('products')
            all_products = list(products_ref.stream())
            
            # Helper to safely get status
            def get_status(p):
                return p.to_dict().get('status', 'pending')

            stats['total_products'] = len(all_products)
            stats['active_products'] = len([p for p in all_products if get_status(p) == 'approved'])
            stats['rejected_products'] = len([p for p in all_products if get_status(p) == 'rejected'])
            stats['pending_products'] = len([p for p in all_products if get_status(p) == 'pending'])
            stats['expired_products'] = len([p for p in all_products if get_status(p) == 'expired'])
            
            # Get expiration dates for the chart
            expired_dates = []
            for p in all_products:
                data = p.to_dict()
                if data.get('status') == 'expired' and data.get('expiration_date'):
                    expired_dates.append(data.get('expiration_date'))
            stats['expired_dates'] = expired_dates
            
            # Orders
            orders_ref = db.collection('orders')
            stats['total_orders'] = len(list(orders_ref.stream()))
            
        elif role == 'farmer':
            # Products
            products_ref = db.collection('products')
            # Assuming username is the farmer_name stored in products
            my_products = list(products_ref.where('farmer_name', '==', username).stream())
            
            # Filter products by status
            approved_products = [p for p in my_products if p.to_dict().get('status') == 'approved']
            rejected_products = [p for p in my_products if p.to_dict().get('status') == 'rejected']
            expired_products = [p for p in my_products if p.to_dict().get('status') == 'expired']
            pending_products = [p for p in my_products if p.to_dict().get('status') == 'pending']
            
            stats['total_products'] = len(approved_products)
            stats['rejected_products'] = [{'id': p.id, **p.to_dict()} for p in rejected_products]
            stats['expired_products'] = [{'id': p.id, **p.to_dict()} for p in expired_products]
            stats['pending_products'] = [{'id': p.id, **p.to_dict()} for p in pending_products]
            
            # For Charts: Product Names and Stock
            stats['product_names'] = []
            stats['product_stocks'] = []
            
            low_stock = 0
            for doc in my_products:
                p_data = doc.to_dict()
                
                # Only include approved products in the stock chart and low stock count
                if p_data.get('status') == 'approved':
                    stock = p_data.get('stock', 0)
                    if stock < 20:
                        low_stock += 1
                    stats['product_names'].append(p_data.get('name', 'Unknown'))
                    stats['product_stocks'].append(stock)
                
            stats['low_stock'] = low_stock
            
            # Orders/Sales (Inefficient but functional for demo)
            orders_ref = db.collection('orders')
            all_orders = orders_ref.stream()
            
            total_sales = 0
            orders_count = 0
            
            # Get IDs of my products
            my_product_ids = [p.id for p in my_products]
            
            for order_doc in all_orders:
                order = order_doc.to_dict()
                items = order.get('items', [])
                order_relevant = False
                for item in items:
                    if item.get('product_id') in my_product_ids:
                        total_sales += item.get('subtotal', 0)
                        order_relevant = True
                
                if order_relevant:
                    orders_count += 1
                    
            stats['total_sales'] = total_sales
            stats['total_orders'] = orders_count

        elif role == 'buyer':
            # Orders
            orders_ref = db.collection('orders')
            my_orders = list(orders_ref.where('user_id', '==', user_id).stream())
            
            # Sort by date descending
            # Handle cases where created_at might be missing or in different formats
            def get_order_date(doc):
                data = doc.to_dict()
                val = data.get('created_at')
                if val:
                    return val
                return datetime.datetime.min

            import datetime
            my_orders.sort(key=get_order_date, reverse=True)

            stats['total_orders'] = len(my_orders)
            
            total_spent = 0
            monthly_spending = {}
            
            for order_doc in my_orders:
                order = order_doc.to_dict()
                total_spent += order.get('total_amount', 0)
                
                # Analytics: Monthly Spending
                created_at = order.get('created_at')
                if created_at:
                    # Firestore Timestamp or datetime
                    if hasattr(created_at, 'strftime'):
                        month_key = created_at.strftime('%b %Y') # e.g., "Dec 2023"
                        # We need a sortable key for sorting, but display key for chart
                        # Let's use a tuple or just sort keys differently later
                        sort_key = created_at.strftime('%Y-%m')
                        
                        if sort_key not in monthly_spending:
                            monthly_spending[sort_key] = {'label': month_key, 'amount': 0}
                        monthly_spending[sort_key]['amount'] += order.get('total_amount', 0)

            stats['total_spent'] = total_spent
            
            # Recent Orders (Top 5)
            stats['recent_orders'] = [{'id': doc.id, **doc.to_dict()} for doc in my_orders[:5]]
            
            # Prepare chart data (sorted by date)
            sorted_keys = sorted(monthly_spending.keys())
            stats['chart_labels'] = [monthly_spending[k]['label'] for k in sorted_keys]
            stats['chart_data'] = [monthly_spending[k]['amount'] for k in sorted_keys]

    except Exception as e:
        print(f'Stats error: {e}')
        
    return stats

def approve_product(product_id, expiration_date):
    db = get_db()
    if db:
        try:
            print(f"Updating Firestore for product {product_id}")
            db.collection('products').document(product_id).update({
                'status': 'approved',
                'expiration_date': expiration_date
            })
            print("Firestore update successful")
            return True
        except Exception as e:
            print(f"Firestore update error: {e}")
            return False
    return False

def check_expired_products():
    db = get_db()
    if db:
        try:
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Get approved products
            products_ref = db.collection('products').where('status', '==', 'approved')
            docs = products_ref.stream()
            
            count = 0
            for doc in docs:
                data = doc.to_dict()
                exp_date = data.get('expiration_date')
                
                if exp_date and exp_date < now:
                    # Expire product
                    doc.reference.update({'status': 'expired'})
                    
                    # Notify Farmer
                    farmer_id = data.get('farmer_id')
                    product_name = data.get('name')
                    if farmer_id:
                        create_notification(
                            farmer_id, 
                            f"Your product '{product_name}' has expired and was removed from the market."
                        )
                    count += 1
            return count
        except Exception as e:
            print(f"Expiration check error: {e}")
            return 0
    return 0

def create_notification(user_id, message):
    db = get_db()
    if db:
        try:
            import datetime
            db.collection('notifications').add({
                'user_id': user_id,
                'message': message,
                'read': False,
                'created_at': datetime.datetime.now()
            })
            return True
        except Exception as e:
            print(f"Notification error: {e}")
            return False
    return False

def get_user_notifications(user_id):
    db = get_db()
    if db:
        try:
            ref = db.collection('notifications').where('user_id', '==', user_id).where('read', '==', False).order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Get notifications error: {e}")
            return []
    return []

def mark_notification_read(notification_id):
    db = get_db()
    if db:
        try:
            db.collection('notifications').document(notification_id).update({'read': True})
            return True
        except Exception as e:
            print(f"Mark notification read error: {e}")
            return False
    return False

def add_review(product_id, user_id, user_name, rating, comment):
    db = get_db()
    if db:
        try:
            import datetime
            review_data = {
                'user_id': user_id,
                'user_name': user_name,
                'rating': int(rating),
                'comment': comment,
                'created_at': datetime.datetime.now()
            }
            # Add to subcollection
            db.collection('products').document(product_id).collection('reviews').add(review_data)
            
            # Update product average rating
            update_product_rating(product_id)
            return True
        except Exception as e:
            print(f"Add review error: {e}")
            return False
    return False

def get_reviews(product_id):
    db = get_db()
    if db:
        try:
            reviews_ref = db.collection('products').document(product_id).collection('reviews').order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = reviews_ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Get reviews error: {e}")
            return []
    return []

def update_product_rating(product_id):
    db = get_db()
    if db:
        try:
            reviews_ref = db.collection('products').document(product_id).collection('reviews')
            docs = list(reviews_ref.stream())
            
            if not docs:
                return
                
            total_rating = sum([doc.to_dict().get('rating', 0) for doc in docs])
            avg_rating = total_rating / len(docs)
            
            db.collection('products').document(product_id).update({
                'rating': avg_rating,
                'review_count': len(docs)
            })
        except Exception as e:
            print(f"Update rating error: {e}")

def check_user_bought_product(user_id, product_id):
    db = get_db()
    if db:
        try:
            # Check orders where user_id matches and status is delivered
            orders_ref = db.collection('orders')
            query = orders_ref.where('user_id', '==', user_id).where('status', '==', 'delivered')
            docs = query.stream()
            
            for doc in docs:
                order = doc.to_dict()
                for item in order.get('items', []):
                    if item.get('product_id') == product_id:
                        return True
            return False
        except Exception as e:
            print(f"Check bought error: {e}")
            return False
    return False

def get_all_articles():
    db = get_db()
    if db:
        try:
            articles_ref = db.collection('articles').order_by('created_at', direction=firestore.Query.DESCENDING)
            docs = articles_ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Get articles error: {e}")
            return []
    return []

def get_article(article_id):
    db = get_db()
    if db:
        try:
            doc = db.collection('articles').document(article_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
        except Exception as e:
            print(f"Get article error: {e}")
            return None
    return None

def update_order_status(order_id, new_status):
    db = get_db()
    if db:
        try:
            db.collection('orders').document(order_id).update({'status': new_status})
            return True
        except Exception as e:
            print(f"Update order error: {e}")
            return False
    return False
