from django.contrib.auth.models import AnonymousUser

class FirebaseUser:
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.name = user_data.get('name', user_data.get('username')) # Add name
        self.email = user_data.get('email')
        self.is_authenticated = True
        self.is_active = True
        self.role = user_data.get('role', 'buyer')
        self.is_verified = user_data.get('is_verified', False)
        self.profile_image = user_data.get('profile_image')
        self.is_staff = user_data.get('role') == 'admin'
        self.is_superuser = user_data.get('role') == 'admin'
        
        # Mimic Profile
        class Profile:
            def __init__(self, role, is_verified):
                self.role = role
                self.is_verified = is_verified
        
        self.profile = Profile(user_data.get('role', 'buyer'), user_data.get('is_verified', False))

    def __str__(self):
        return self.name or self.username # Return name if available

class FirebaseUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('user_id')
        
        if user_id:
            # In a real app, you might cache this or store minimal info in session
            # For now, we trust the session data if it has role/username
            user_data = {
                'id': user_id,
                'username': request.session.get('username'),
                'name': request.session.get('name'), # Get name from session
                'role': request.session.get('role'),
                'is_verified': request.session.get('is_verified', False),
                'profile_image': request.session.get('profile_image')
            }
            request.user = FirebaseUser(user_data)
        else:
            request.user = AnonymousUser()
            
        response = self.get_response(request)
        return response
