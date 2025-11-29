
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
