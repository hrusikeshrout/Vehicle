from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Vehicle, Guardian
from .forms import RegisterForm, LoginForm, VehicleForm
from django.contrib import messages
from django.http import HttpResponse


def home_page(request):
    return render(request, 'home_page.html')

# 1. Register User
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registered successfully!")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# 2. Login User
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# 3. Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# 4. Dashboard
@login_required
def dashboard_view(request):
    vehicles = Vehicle.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'vehicles': vehicles})



# 5. Add Vehicle
@login_required
def add_vehicle_view(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, "Vehicle added!")
            return redirect('dashboard')
    else:
        form = VehicleForm()
    return render(request, 'add_vehicle.html', {'form': form})


# 6. View Vehicle from QR token
def scan_qr_view(request, qr_token):
    vehicle = get_object_or_404(Vehicle, qr_token=qr_token)
    return render(request, 'contact_vehicle.html', {'vehicle': vehicle})


# 7. Send Contact Alert (fake for now)
def contact_owner_view(request, vehicle_id, mode):
    vehicle = Vehicle.objects.get(id=vehicle_id)

    if mode == "emergency":
        guardian = Guardian.objects.filter(user=vehicle.owner).first()
        number = guardian.phone_number if guardian else None
    else:
        number = vehicle.owner.phone_number

    # You would integrate Twilio or MessageBird here
    messages.success(request, f"{mode.capitalize()} contact sent to {number}")
    return redirect('scan_qr', id=vehicle_id)



def scan_qr_view(request, qr_token):
    vehicle = get_object_or_404(Vehicle, id=qr_token)
    return render(request, 'contact_vehicle.html', {'vehicle': vehicle})
