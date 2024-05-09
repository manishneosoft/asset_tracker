from typing import Dict, Optional, Union
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse
from django.core.paginator import Paginator, Page
from .models import AssetType, Asset, AssetImage
from .models import Role, CustomUser
import csv 
from django.http import HttpResponse,HttpRequest
from django.utils.encoding import smart_str
from django.db.models import QuerySet


def login_view(request: HttpRequest) -> HttpResponse:
    """ Login view renders the login page and handles the login process

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: HttpResponseRedirect if login is successful,
        else renders the login page with error message
    """
    if request.method == "POST":
        # Get email and password from request
        email: str = request.POST['email']
        password: str = request.POST['password']

        # Authenticate user
        user: CustomUser = authenticate(request, email=email, password=password)

        # If user is not None, redirect to appropriate dashboard
        if user is not None:
            login(request, user)
            if user.role == Role.objects.get(name='system_admin'):
                return HttpResponseRedirect(reverse('sysadmin_dashboard'))
            if user.role == Role.objects.get(name='seeder'):
                return HttpResponseRedirect(reverse('seeder'))
        else:
            # Render login page with error message
            return render(request, 'tracker/index.html', {'error_message': 'Invalid Credentials'})
    else:
        # If request method is GET, render login page
        return render(request, 'tracker/index.html')



def logout_user(request: HttpRequest) -> HttpResponse:
    """Logs out the user and redirects them to the homepage.

    This function logs the user out of their session and displays a message
    to the user confirming that they have been logged out.

    Args:
        request (HttpRequest): The current HttpRequest.

    Returns:
        HttpResponse: A redirect to the homepage.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('/')  # Redirect to homepage.


@login_required
def seeder_dashboard(request: HttpRequest) -> HttpResponse:
    """Renders the seeder dashboard page.

    This function renders the seeder dashboard page for logged in seeders.
    If the user is not a seeder, they are redirected to the index page.

    Args:
        request (HttpRequest): The current HttpRequest.

    Returns:
        HttpResponse: A rendered template response.
    """
    # If the user is not a seeder, redirect to index page
    if request.user.role.name != 'seeder':
        return HttpResponseRedirect(reverse('index'))

    # Get all system admins
    try:
        sys_admin: Optional[QuerySet[CustomUser]] = CustomUser.objects.filter(role__name='system_admin')
    except CustomUser.DoesNotExist:
        sys_admin = None

    # Render the seeder dashboard template
    return render(request, 'tracker/seeder_dashboard.html', {'users': sys_admin})


@login_required
def addsysadmin(request: HttpRequest) -> HttpResponse:
    """Addsysadmin view renders the add sys admin page and handles the add process

    This function renders the add sys admin page for logged in seeders.
    If the user is not a seeder, they are redirected to the index page.
    If the request method is GET, render the add sys admin page.
    If the request method is POST, create a new sys admin user with the given email
    and password, and redirect the user to the seeder dashboard page.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: HttpResponseRedirect if add is successful,
        else renders the add sys admin page with error message
    """
    if request.user.role.name != 'seeder':
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'GET':
        return render(request, 'tracker/seeder_addsysadmin.html')

    elif request.method == 'POST':
        email: str = request.POST['email']
        password: str = request.POST['password']

        try:
            role: Role = Role.objects.get(name='system_admin')
            existing_user: Optional[CustomUser] = CustomUser.objects.get(email=email)
            if existing_user.role == role:
                data = {'error_message': 'System Admin already exists with this email'}
            else:
                data = {'error_message': 'User already exists with this email'}
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create_user(email=email, password=password, role=role)
            user.save()
            data = {'success_message': 'User created successfully'}
        return render(request, 'tracker/seeder_addsysadmin.html', data)

@login_required
def update_sysadmin_profile(request: HttpRequest, pk: int) -> HttpResponse:
    """Update sysadmin profile view renders the edit sysadmin page and handles the update process

    This function renders the edit sysadmin page for logged in seeders.
    If the user is not a seeder, they are redirected to the index page.
    If the request method is GET, render the edit sysadmin page with the current user details.
    If the request method is POST, update the user with the given email and password,
    and redirect the user to the seeder dashboard page.

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Primary key of the sysadmin user

    Returns:
        HttpResponse: HttpResponseRedirect if update is successful,
        else renders the edit sysadmin page with error message
    """
    if request.user.role.name != 'seeder':
        return HttpResponseRedirect(reverse('index'))
    user: CustomUser = get_object_or_404(CustomUser, id=pk)

    if request.method == 'POST':
        email: str = request.POST.get('email', user.email)
        password: str = request.POST.get('password', None)

        if CustomUser.objects.exclude(id=pk).filter(email=email).exists():
            messages.error(request, 'This email is already in use.')
        elif password and not user.check_password(password):
            user.set_password(password)

        user.email = email
        user.save()

        messages.success(request, 'User profile has been updated successfully.')
        return redirect('/seeder')  # Redirect to the seeder page
    if request.method == 'GET':
        return render(request, 'tracker/seeder_editsysadmin.html', {'user': user})



@login_required
def sysadmin_dashboard(request: HttpRequest) -> HttpResponse:
    """System Admin dashboard view renders the system admin dashboard page

    This function renders the system admin dashboard page for logged in system admins.
    If the user is not a system admin, they are redirected to the index page.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: A rendered template response
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))

    # Generate data for PIE Chart - Number of assets per asset type
    asset_type_counts: QuerySet = Asset.objects.values('asset_type__name').annotate(count=Count('id'))
    # Generate data for BAR Chart - Number of active and inactive assets
    active_assets_count: int = Asset.objects.filter(is_active=True).count()
    inactive_assets_count: int = Asset.objects.filter(is_active=False).count()

    # Data for PIE Chart
    pie_chart_data: Dict = {
        'labels': [item['asset_type__name'] for item in asset_type_counts],
        'data': [item['count'] for item in asset_type_counts]
    }
    # Data for BAR Chart
    bar_chart_data: Dict = {
        'labels': ['Active Assets', 'Inactive Assets'],
        'data': [active_assets_count, inactive_assets_count]
    }

    return render(request, 'tracker/sys_admin_dashboard.html',
                  {'pie_chart_data': pie_chart_data, 'bar_chart_data': bar_chart_data})




@login_required
def manage_asset_types(request: HttpRequest) -> HttpResponse:
    """View function for system admins to manage asset types

    This view renders the manage asset types page for system admins.
    If the user is not a system admin, they are redirected to the index page.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: A rendered template response
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))
    asset_types: QuerySet = AssetType.objects.all().order_by('-created_at')
    paginator: Paginator = Paginator(asset_types, 5)  # 5 records per page
    page_number: Optional[str] = request.GET.get('page')
    asset_types_page: Page = paginator.get_page(page_number)
    context: Dict = {
        'asset_types': asset_types_page,
    }
    return render(request, 'tracker/manage_asset_types.html', context)





@login_required
def update_asset_type(request: HttpRequest, pk: int) -> HttpResponse:
    """View function for system admins to update an asset type

    If the user is not a system admin, they are redirected to the index page.
    If the request method is POST, the asset type is updated with the data
    from the request and the user is redirected to the manage asset types page.
    If the request method is GET, the asset type is retrieved from the database
    and passed to a template for rendering.

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Primary key of the asset type to update

    Returns:
        HttpResponse: A rendered template response
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))
    asset_type: AssetType = get_object_or_404(AssetType, id=pk)

    if request.method == 'POST':
        # Get the data from the request and update the asset type
        name: str = request.POST.get('name', asset_type.name)
        description: str = request.POST.get('description', asset_type.description)
        asset_type.name = name
        asset_type.description = description
        asset_type.save()

        # Add a success message and redirect to the manage asset types page
        messages.success(request, 'Asset type has been updated successfully.')
        return redirect('manage_asset_types')

    if request.method == 'GET':
        # Render a template with the asset type
        return render(request, 'tracker/edit_asset_type.html', {'asset_type': asset_type})

@login_required
def delete_assettype(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    """View function for system admins to delete an asset type

    If the user is not a system admin, they are redirected to the index page.
    If the asset type is deleted, the user is redirected to the manage asset types page.

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Primary key of the asset type to delete

    Returns:
        HttpResponseRedirect: A redirect to the manage asset types page
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))

    asset_type = get_object_or_404(AssetType, id=pk)

    asset_type.delete()
    return HttpResponseRedirect(reverse('manage_asset_types'))


def addassettype(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    """View function for system admins to add an asset type

    If the user is not a system admin, they are redirected to the index page.
    If the request method is POST, the asset type is created with the data
    from the request and the user is redirected to the manage asset types page.
    If the request method is GET, the user is shown a form to add a new asset type.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        Union[HttpResponseRedirect, HttpResponse]: A redirect to the manage asset types page or a rendered template response
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        # Get the data from the request and create a new asset type
        name: str = request.POST['name']
        description: str = request.POST['description']
        try:
            new_asset_type: AssetType = AssetType.objects.create(name=name, description=description)
            new_asset_type.save()
            return HttpResponseRedirect(reverse('manage_asset_types'))
        except Exception as e:
            # If there's an error, show the form again with an error message
            return render(request, 'tracker/add_asset_type.html', {'error_message': str(e)})
    else:
        # If the request method is GET, just show the form
        return render(request, 'tracker/add_asset_type.html')



@login_required
def manage_assets(request: HttpRequest) -> HttpResponse:
    """View function for system admins to manage assets

    If the user is not a system admin, they are redirected to the index page.
    If the request method is POST, the method handles create/update/delete
    operations for assets. The actual implementation is left to the developer.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: A rendered template response
    """
    if request.user.role.name != 'system_admin':
        return HttpResponseRedirect(reverse('index'))

    # if request.method == 'POST':
    #     # Handle create/update/delete operations for assets (implementation required)
    #     if 'create_asset' in request.POST:
    #         # Create a new asset with image handling
    #         name: str = request.POST['name']
    #         asset_type_id: int = int(request.POST['asset_type'])
    #         asset_type: AssetType = AssetType.objects.get(pk=asset_type_id)
    #         is_active: bool = 'is_active' in request.POST

    #         new_asset: Asset = Asset.objects.create(name=name, asset_type=asset_type, is_active=is_active)

    #         # Handle image uploads
    #         for image_file in request.FILES.getlist('images'):
    #             AssetImage.objects.create(asset=new_asset, image=image_file)

    # import time 
    # print(time.ctime())
    assets = Asset.objects.all().order_by('-created_at')  # Fetch all assets and order by latest
    # print(time.ctime())
    asset_types = AssetType.objects.all() 
    # print(time.ctime())
    paginator = Paginator(assets, 5)  # Show 5 assets per page
    # print(time.ctime())
    page = request.GET.get('page')
    assets = paginator.get_page(page)
    # print(time.ctime())
    context = {
        'assets': assets,
        'asset_types': asset_types,
    }
    # print(time.ctime())
    dd = render(request, 'tracker/manage_assets.html', context)
    # print(time.ctime())
    return dd





def add_asset(request: HttpRequest) -> HttpResponseRedirect:
    """Add asset view

    This view handles POST requests to create a new asset.
    It redirects the user to the manage assets page on success.

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponseRedirect: Redirects the user to the manage assets page
    """
    if request.method == 'POST':
        name: str = request.POST['name']
        asset_type_id: int = int(request.POST['asset_type'])
        asset_type: AssetType = AssetType.objects.get(pk=asset_type_id)
        is_active: bool = 'is_active' in request.POST
        new_asset: Asset = Asset.objects.create(name=name, asset_type=asset_type, is_active=is_active)
        new_asset.save()
        return HttpResponseRedirect(reverse('manage_assets'))
    elif request.method == 'GET':
        asset_types = AssetType.objects.all()
        context = {
            'asset_types': asset_types,
        }
        """Render the add asset page

        This function renders the add asset page
        passing the asset types to the template.

        Args:
            request (HttpRequest): Django HttpRequest

        Returns:
            HttpResponse: A rendered template response
        """
        return render(request, 'tracker/add_asset.html', context)


def edit_asset(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit asset view

    This view handles GET and POST requests to edit an existing asset.
    If the request method is GET, the asset is retrieved from the database
    and passed to a template for rendering. If the request method is POST,
    the asset is updated with the data from the request and the user is
    redirected to the manage assets page.

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Primary key of the asset to edit

    Returns:
        HttpResponse: A rendered template response
    """
    asset: Asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        name: str = request.POST['name']
        asset_type_id: int = int(request.POST['asset_type'])
        asset_type: AssetType = AssetType.objects.get(pk=asset_type_id)
        is_active: bool = 'is_active' in request.POST
        asset.name = name
        asset.asset_type = asset_type
        asset.is_active = is_active
        asset.save()
        return HttpResponseRedirect(reverse('manage_assets'))
    elif request.method == 'GET':
        asset_types: QuerySet = AssetType.objects.all()
        context: Dict = {
            'asset': asset,
            'asset_types': asset_types,
        }
        return render(request, 'tracker/edit_asset.html', context)



@login_required
def delete_asset(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    """Delete asset view

    This view handles DELETE requests to delete an existing asset.
    The asset is retrieved from the database and deleted.
    The user is redirected to the manage assets page.

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Primary key of the asset to delete

    Returns:
        HttpResponseRedirect: Redirects the user to the manage assets page
    """
    asset: Asset = get_object_or_404(Asset, pk=pk)
    asset.delete()
    return HttpResponseRedirect(reverse('manage_assets'))


@login_required
def assets_csv(request: HttpRequest) -> HttpResponse:
    """View function for generating a CSV of all assets

    This view generates a CSV file of all assets in the system.
    The file is downloaded as 'data.csv'

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: An HttpResponse with a CSV file of all assets
    """
    response: HttpResponse = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer: csv.writer = csv.writer(response)
    Assets: QuerySet = Asset.objects.all()

    # Write header row
    writer.writerow([
        smart_str(field.name)
        for field in Asset._meta.fields 
    ])

    # Write data rows
    for obj in Assets:
        writer.writerow([
            smart_str(getattr(obj, field.name))
            for field in Asset._meta.fields  
        ])

    return response


