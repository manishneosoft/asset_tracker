# Django Tracker App

This is a Django web application for tracking Asset. It provides functionality to Manage users, Manage asset types and assets.

## Installation

1. Git Clone from GitHub

    ```bash
    git clone https://github.com/manishneosoft/asset_tracker
    ```


2. Create a virtual environment:

    ```bash
    python3 -m venv myenv
    ```

3. Activate the virtual environment:

    - On Windows:

    ```bash
    myenv\Scripts\activate
    ```

    - On Unix or MacOS:

    ```bash
    source myenv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Make sure you have set up your database configuration in `settings.py`.

2. Run the Django development server:

    ```bash
    python manage.py runserver
    ```

3. If running for the first time, execute the following commands inside the Django shell to set up initial roles and users:

    ```bash
    python manage.py shell
    ```

    ```python
    from tracker.models import CustomUser, Role

    # Create roles
    role = Role.objects.create(name="seeder")
    role.save()
    role = Role.objects.create(name="system_admin")
    role.save()

    # Create a user with a role
    user = CustomUser.objects.create_user(email='Manish.j@neosoftmail.com', role=Role.objects.get(name='seeder'))
    user.set_password('1234')
    user.save()

    exit()
    ```

4. You can now access the application at `http://localhost:8000` in your web browser.

