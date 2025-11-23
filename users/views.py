from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
import re
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from products.models import Order, DeliveryAddress
from products.forms import DeliveryAddressForm
from django.conf import settings
from django.urls import reverse
import requests
from datetime import datetime
from .models import UserProfile
import urllib.parse
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
import re


class CustomSetPasswordForm(SetPasswordForm):
    """Custom password form with simplified validation"""
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # Custom validation: at least 8 characters and 1 number
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        
        return password


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view that shows user-specific messages"""
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = '/password-reset/done/'  # Redirect to done page on success
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Check if user exists
        user_exists = User.objects.filter(email=email).exists()
        
        if user_exists:
            # User exists, send email and redirect to done page
            return super().form_valid(form)
        else:
            # User doesn't exist, stay on same page with error
            messages.error(self.request, f"No account found with email {email}. Please check and try again.")
            return self.form_invalid(form)

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password != cpassword:
            messages.error(request, "Passwords don't match. Please recheck and try again.")
            return render(request, 'users/register.html')

        try:
            EmailValidator()(email)
        except ValidationError:
            messages.error(request, "Invalid email format. Please recheck and try again.")
            return render(request, 'users/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'users/register.html')

        
        user = User.objects.create_user(
            username=email,  
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        user.save()

        # Success message
        messages.success(request, 'Account created. Please log in.')
        return redirect('login')  

    return render(request, 'users/register.html')


def login(request):
    # Clear any password reset messages when accessing login page via GET
    if request.method == "GET":
        storage = messages.get_messages(request)
        storage.used = True
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('homepage')  # Redirect to homepage after login
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'users/login.html')


def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    # Get user's orders sorted by latest first
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Get user's delivery addresses
    delivery_addresses = DeliveryAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    # Check if editing an address
    edit_address_id = request.GET.get('edit')
    edit_address = None
    if edit_address_id:
        edit_address = get_object_or_404(DeliveryAddress, id=edit_address_id, user=request.user)
    
    # Handle form submissions
    if request.method == "POST":
        if 'add_address' in request.POST:
            # Update existing address if present; otherwise create one
            existing_qs = DeliveryAddress.objects.filter(user=request.user).order_by('-updated_at')
            if existing_qs.exists():
                address = existing_qs.first()
                form = DeliveryAddressForm(request.POST, instance=address)
                if form.is_valid():
                    form.save()
                    # Remove duplicates if any
                    for extra in existing_qs[1:]:
                        extra.delete()
                    messages.success(request, "Delivery address updated successfully!")
                    return redirect('profile')
            else:
                form = DeliveryAddressForm(request.POST)
                if form.is_valid():
                    address = form.save(commit=False)
                    address.user = request.user
                    address.save()
                    messages.success(request, "Delivery address saved!")
                    return redirect('profile')
        
        elif 'update_address' in request.POST:
            address_id = request.POST.get('address_id')
            address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
            form = DeliveryAddressForm(request.POST, instance=address)
            if form.is_valid():
                form.save()
                messages.success(request, "Address updated successfully!")
                return redirect('profile')
        
        elif 'delete_address' in request.POST:
            address_id = request.POST.get('address_id')
            address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
            address.delete()
            messages.success(request, "Delivery address deleted successfully!")
            return redirect('profile')
        
        elif 'set_default' in request.POST:
            address_id = request.POST.get('address_id')
            address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
            # Unset all other default addresses
            DeliveryAddress.objects.filter(user=request.user).update(is_default=False)
            address.is_default = True
            address.save()
            messages.success(request, "Default address updated!")
            return redirect('profile')
    
    # Initialize form
    if edit_address:
        form = DeliveryAddressForm(instance=edit_address)
    else:
        form = DeliveryAddressForm()
    
    # Get user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    context = {
        'orders': orders,
        'delivery_addresses': delivery_addresses,
        'form': form,
        'edit_address': edit_address,
        'user_profile': user_profile,
    }
    return render(request, 'users/profile.html', context)


def google_oauth_test(request):
    """Test page to show redirect URI"""
    from django.urls import reverse
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    redirect_uri_clean = redirect_uri.split('?')[0].split('#')[0]
    if not redirect_uri_clean.endswith('/'):
        redirect_uri_clean += '/'
    
    # Generate localhost version
    redirect_uri_localhost = redirect_uri_clean.replace('127.0.0.1', 'localhost')
    if redirect_uri_localhost == redirect_uri_clean:
        # If already localhost, generate 127.0.0.1 version
        redirect_uri_localhost = redirect_uri_clean.replace('localhost', '127.0.0.1')
    
    context = {
        'redirect_uri': redirect_uri_clean,
        'redirect_uri_alt': redirect_uri_localhost,
        'current_host': request.get_host(),
        'current_scheme': request.scheme,
    }
    return render(request, 'users/oauth_test.html', context)


def google_login(request):
    """Initiate Google OAuth flow"""
    from django.conf import settings
    from django.urls import reverse
    
    # Dynamically build redirect URI to match exactly
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    # Remove any trailing query parameters or fragments that might cause issues
    redirect_uri = redirect_uri.split('?')[0].split('#')[0]
    # Ensure it ends with / (Google is strict about this)
    if not redirect_uri.endswith('/'):
        redirect_uri += '/'
    
    # Debug: Print the redirect URI (remove in production)
    print("=" * 80)
    print(f"DEBUG: Redirect URI being used: {redirect_uri}")
    print(f"DEBUG: Make sure this EXACT URI is added to Google Cloud Console!")
    print(f"DEBUG: Client ID: {settings.GOOGLE_OAUTH2_CLIENT_ID}")
    print("=" * 80)
    
    # Google OAuth endpoints
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # Scopes needed for profile info and DOB
    scopes = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/user.birthday.read"
    ]
    
    # Parameters for OAuth request
    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(scopes),
        'access_type': 'offline',
        'prompt': 'consent',
    }
    
    # Build the authorization URL
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    return redirect(auth_url_with_params)


def google_callback(request):
    """Handle Google OAuth callback"""
    from django.conf import settings
    from django.urls import reverse
    
    code = request.GET.get('code')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description', '')
    
    # Log error details for debugging
    if error:
        print("=" * 80)
        print(f"ERROR: Google OAuth error: {error}")
        print(f"ERROR Description: {error_description}")
        print(f"ERROR Full request GET params: {dict(request.GET)}")
        print("=" * 80)
        messages.error(request, f"Google authentication failed: {error}. Check terminal for details.")
        return redirect('login')
    
    if not code:
        messages.error(request, "No authorization code received from Google.")
        return redirect('login')
    
    # Dynamically build redirect URI to match exactly (must be same as in google_login)
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    # Clean the redirect URI (same as in google_login)
    redirect_uri = redirect_uri.split('?')[0].split('#')[0]
    if not redirect_uri.endswith('/'):
        redirect_uri += '/'
    
    print(f"DEBUG Callback: Using redirect_uri: {redirect_uri}")
    
    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            messages.error(request, "Failed to get access token from Google.")
            return redirect('login')
        
        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        # Get user's DOB from People API
        dob = None
        try:
            people_url = "https://people.googleapis.com/v1/people/me"
            people_params = {
                'personFields': 'birthdays,names,emailAddresses'
            }
            people_response = requests.get(people_url, headers=headers, params=people_params)
            if people_response.status_code == 200:
                people_data = people_response.json()
                # Extract birthday
                birthdays = people_data.get('birthdays', [])
                if birthdays:
                    for birthday in birthdays:
                        date = birthday.get('date', {})
                        if date:
                            year = date.get('year', 1900)
                            month = date.get('month', 1)
                            day = date.get('day', 1)
                            try:
                                dob = datetime(year, month, day).date()
                                break
                            except:
                                pass
        except Exception as e:
            # If People API fails, continue without DOB
            print(f"Could not fetch DOB from People API: {e}")
        
        # Extract user information
        google_id = userinfo.get('id')
        email = userinfo.get('email')
        first_name = userinfo.get('given_name', '')
        last_name = userinfo.get('family_name', '')
        picture_url = userinfo.get('picture')
        
        if not email:
            messages.error(request, "Could not get email from Google account.")
            return redirect('login')
        
        # Check if user exists by Google ID
        try:
            profile = UserProfile.objects.get(google_id=google_id)
            user = profile.user
        except UserProfile.DoesNotExist:
            # Check if user exists by email
            try:
                user = User.objects.get(email=email)
                # Update user with Google ID
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.google_id = google_id
                if dob:
                    profile.date_of_birth = dob
                if picture_url:
                    # Download and save profile picture
                    try:
                        pic_response = requests.get(picture_url)
                        if pic_response.status_code == 200:
                            from django.core.files.base import ContentFile
                            profile.profile_picture.save(
                                f"google_{google_id}.jpg",
                                ContentFile(pic_response.content),
                                save=False
                            )
                    except:
                        pass
                profile.email = email
                profile.save()
            except User.DoesNotExist:
                # Create new user
                username = email.split('@')[0] + '_' + google_id[:8]
                # Ensure username is unique
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                
                # Create profile
                profile = UserProfile.objects.create(
                    user=user,
                    google_id=google_id,
                    email=email,
                    date_of_birth=dob,
                )
                
                # Download and save profile picture
                if picture_url:
                    try:
                        pic_response = requests.get(picture_url)
                        if pic_response.status_code == 200:
                            from django.core.files.base import ContentFile
                            profile.profile_picture.save(
                                f"google_{google_id}.jpg",
                                ContentFile(pic_response.content),
                                save=False
                            )
                    except:
                        pass
                profile.save()
        
        # Login the user
        auth_login(request, user)
        messages.success(request, f"Logged in successfully with Google, {user.first_name}!")
        
        # Update DOB if we got it and it's not set
        if dob and not profile.date_of_birth:
            profile.date_of_birth = dob
            profile.save()
        
        return redirect('homepage')
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request exception: {e}")
        print(f"ERROR: Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        messages.error(request, f"Error during Google authentication: {str(e)}")
        return redirect('login')
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('login')
