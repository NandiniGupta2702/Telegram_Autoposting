import asyncio
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,login as auth_login,logout as auth_logout
from .forms import LoginForm, SignUpForm, TelegramBotForm,ApiInputForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from apps.authentication.models import TelegramBotCredentials # Updated import
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
from django.contrib.auth.models import User
import os,subprocess,re,json
from .models import ApiCredentials
from django.conf import settings
from telethon import TelegramClient, events
import pandas as pd
from telethon.sessions import StringSession


def login_view(request):
    if request.user.is_authenticated:
        # User is already logged in, redirect to index
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('user_type')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if role == 'admin' and user.is_superuser:
                    login(request, user)
                    return redirect('index')
                elif role == 'user':
                    login(request, user)
                    return redirect('index')
                else:
                    messages.error(request, 'Invalid role or admin role not found.')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user registration data
            messages.success(request, 'User created successfully! Please login.')  # Flash success message
            return redirect('login')  # Redirect to the login page after successful registration
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@login_required
def configure_bot(request):
    success_message = None
    error_message = None

    if request.method == 'POST':
        form = TelegramBotForm(request.POST, request.FILES)
        if form.is_valid():
            
            api_id = form.cleaned_data['api_id']
            api_hash = form.cleaned_data['api_hash']
            phone_number = form.cleaned_data['phone_number']

            try:
                asyncio.run(start_telegram_client(api_id, api_hash, phone_number))
                session_file = f"session_{phone_number.replace('+', '')}.txt"

                if os.path.exists(session_file):
                    bot = form.save(commit=False)
                    bot.user = request.user  
                    bot.save()

                    success_message = "Bot created and Telegram client started successfully!"
                    messages.success(request, success_message)
                    return redirect('user_bot_data')
                else:
                    error_message = "Failed to create a valid session."
                    messages.error(request, "Failed to create a valid session.")
            except Exception as e:
                messages.error(request, f"Error starting Telegram client: {str(e)}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TelegramBotForm()

    return render(request, 'home/data.html', {'form': form, 'success_message': success_message,'error_message': error_message})

async def start_telegram_client(api_id, api_hash, phone_number):
    session_file = f"session_{phone_number.replace('+', '')}.txt"

    if os.path.exists(session_file):
        print(f"Session file '{session_file}' already exists. Using existing session.")
        with open(session_file, "r") as file:
            session_string = file.read()
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.start()  
    else:
        print(f"Session file '{session_file}' not found. Creating a new session.")
        client = TelegramClient(StringSession(), api_id, api_hash)
        
        try:
            
            await client.start(phone=phone_number)
            print("We've sent you a verification code via SMS. Please check your messages.")

            verification_code = input("Enter the code: ")

            await client.sign_in(code=verification_code)
            print("You are now logged in!")
             
            session_string = client.session.save()
            with open(session_file, "w") as file:
                file.write(session_string)

            print(f"Your session string has been saved.")
            return True  
        except Exception as e:
            print(f"Error during login: {e}")
            return False  

    return True
# 
# Example usage (ensure you run it in an asyncio event loop)
# asyncio.run(start_telegram_client(api_id, api_hash, phone_number))

# async def start_telegram_client(api_id, api_hash, phone_number):
#     session_file = f"session_{phone_number.replace('+', '')}.txt"

#     if os.path.exists(session_file):
#         print(f"Session file '{session_file}' already exists. Using existing session.")
#         with open(session_file, "r") as file:
#             session_string = file.read()
#         client = TelegramClient(StringSession(session_string), api_id, api_hash)
#         await client.start()
#     else:
#         print(f"Session file '{session_file}' not found. Creating a new session.")
#         client = TelegramClient(StringSession(), api_id, api_hash)

#         try:
#             await client.connect()
#             if not await client.is_user_authorized():
#                 # Phase 1: Send phone number and request OTP
#                 await client.send_code_request(phone_number)

#                 # Custom message for OTP input
#                 verification_code = input("Please enter the OTP sent to your phone: ")

#                 # Phase 2: Sign in with the OTP code
#                 await client.sign_in(phone_number, verification_code)

#             print("You are now logged in!")

#             session_string = client.session.save()
#             with open(session_file, "w") as file:
#                 file.write(session_string)

#             print(f"Your session string has been saved.")
#             return True
#         except Exception as e:
#             print(f"Error during login: {e}")
#             return False

#     return True
  

# async def start_telegram_client(api_id, api_hash, phone_number):
#     session_file = f"session_{phone_number.replace('+', '')}.txt"

#     if os.path.exists(session_file):
#         print(f"Session file '{session_file}' already exists. Using existing session.")
#         with open(session_file, "r") as file:
#             session_string = file.read()
#         client = TelegramClient(StringSession(session_string), api_id, api_hash)
#         await client.start()  # Start using the existing session
#     else:
#         print(f"Session file '{session_file}' not found. Creating a new session.")
#         client = TelegramClient(StringSession(), api_id, api_hash)
        
#         try:
#             # Start client with the phone number
#             await client.start(phone=phone_number)
            
#             # Save session string after successful login
#             session_string = client.session.save()
#             with open(session_file, "w") as file:
#                 file.write(session_string)

#             print(f"Your session string has been saved.")
#             return True  
#         except Exception as e:
#             print(f"Error during login: {e}")
#             return False  

#     return True  # Return True if the session is already active



@login_required
def bot_details(request, bot_id):
    bot = get_object_or_404(TelegramBotCredentials, id=bot_id)
    user = get_object_or_404(User, id=bot.user_id)
    if request.user != bot.user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this bot.')
        return redirect('user_bot_data')
    if request.method == 'POST':
        form = TelegramBotForm(request.POST, instance=bot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bot details updated successfully!')
            return redirect('bot_details', bot_id=bot.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TelegramBotForm(instance=bot)

    return render(request, 'home/bot_details.html', {'bot': bot,'user':user,'form': form})

@login_required
def view_logins(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    
    users = User.objects.all().order_by('-date_joined')  # Fetch all registered users
    
    return render(request, 'home/tables.html', {'users': users})

@login_required
def login_as_user(request, user_id):
    admin = request.user

    if not admin.is_superuser:
        return HttpResponseForbidden("You do not have permission to perform this action.")

    try:
        user = User.objects.get(pk=user_id)  # Use `pk` for primary key lookup
    except User.DoesNotExist:
        return HttpResponseForbidden("User not found.")

    if user != admin:
        admin_session_data = {
            'is_admin_login_as': True,
            'admin_id': admin.id,
            'admin_referrer': request.META.get('HTTP_REFERER', '/registered-users/'),  # Use trailing slash for consistency
        }

        auth_login(request, user)
        request.session.update(admin_session_data)
        request.session.save()

        print(f"Session data after login_as_user: {request.session.items()}")

    return redirect('index')

@login_required
def logout_view(request):
    print(f"Session data before check: {request.session.items()}")

    if not request.session.get('is_admin_login_as', False):
        # Normal user logout (no admin login_as involved)
        auth_logout(request)
        return redirect('login')  # Consider redirecting to a relevant page

    admin_id = request.session.get('admin_id')
    if not admin_id:
        print("Admin ID not found in session")
        return HttpResponseForbidden("You are not currently logged in as another user.")

    try:
        admin = User.objects.get(pk=admin_id)
    except User.DoesNotExist:
        print("Admin user does not exist")
        return HttpResponseForbidden("Admin user does not exist.")

    # Logout the currently logged-in user (which is not the admin)
    auth_logout(request)

    # Restore admin session data and log in as the admin
    request.session.clear()  # Clear the entire session for complete reset
    request.session['is_admin_login_as'] = False
    request.session['admin_id'] = admin.id
    request.session['admin_referrer'] = request.session.get('admin_referrer', '/registered-users/')  # Use default if not found

    request.session.save()

    auth_login(request, admin)

    print(f"Session data after restore: {request.session.items()}")

    return redirect(request.session.get('admin_referrer', '/'))  # Redirect to default or saved referrer

@login_required
def run_csv(request, bot_id):
    success_message = None
    error_message = None
    bot = None  # Initialize bot to avoid UnboundLocalError

    try:
        bot = get_object_or_404(TelegramBotCredentials, id=bot_id,)

        if request.method == 'POST':
            # Get the page the user came from
            source_page = request.POST.get('source_page', 'bot_details')

            # Get the CSV file from the form
            csv_file = request.FILES.get('csv_file')

            if not csv_file or not csv_file.name.endswith('.csv'):
                error_message = 'Please upload a valid CSV file.'
            else:
                # Save the uploaded CSV file to a temporary location
                csv_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', csv_file.name)
                os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
                with open(csv_file_path, 'wb+') as destination:
                    for chunk in csv_file.chunks():
                        destination.write(chunk)

                try:
                    # Retrieve credentials from the database
                    bot_credentials = TelegramBotCredentials.objects.filter(id=bot_id).first()
                    if bot_credentials is None:
                        error_message = 'No Telegram bot credentials found.'
                    else:
                        # token = bot_credentials.token
                        api_id = str(bot_credentials.api_id) 
                        api_hash = bot_credentials.api_hash
                        channel_username = bot_credentials.channel_username
                        phone_number = bot_credentials.phone_number
                        if not api_id.isdigit():
                            error_message = 'Invalid API ID. It must be a numeric value.'
                        else:
                            channel_path = os.path.join( 'channel.py')
                            command = [
                                'python', channel_path,
                                # '--token', token,
                                '--api_id', api_id,
                                '--api_hash', api_hash,
                                '--channel_username', channel_username,
                                '--csv', csv_file_path,
                                '--phone_number',phone_number
                            ]

                            print(f"Executing command: {' '.join(command)}")  # Log the command for debugging

                            result = subprocess.run(command, capture_output=True, text=True)

                            # Log stdout and stderr for debugging
                            print(f"stdout: {result.stdout}")
                            print(f"stderr: {result.stderr}")

                            if result.returncode == 0:
                                success_message = 'CSV file processed and members added to the channel successfully.'
                            else:
                                error_message = f'Error in channel.py execution: {result.stderr}'

                except Exception as e:
                    error_message = f'Error running channel.py: {str(e)}'
                    print(f'Exception: {str(e)}')  # Log the exception for debugging

                # Clean up the uploaded CSV file
                if os.path.exists(csv_file_path):
                    os.remove(csv_file_path)

    except TelegramBotCredentials.DoesNotExist:
        error_message = "Bot not found."

    # Pass the bot object if it exists to avoid UnboundLocalError in the template
    context = {
        'bot': bot,
        'success_message': success_message,
        'error_message': error_message,
        'user': request.user,
        'bot_data': TelegramBotCredentials.objects.filter(user=request.user)  # Ensure you pass only the user's bot data
    }
# Get the referrer and the current path
    referrer = request.META.get('HTTP_REFERER', '')
    referrer_path = request.path

    # Check if the referrer contains 'bot-data'
    if 'bot-data' in referrer:
        # Redirect back to /bot-data/ if deleting from the bot_data page
        return redirect(referrer)

    # Check if the current path is already a bot-details page
    elif re.match(r'^/bot-details/\d+/$', referrer_path):
        # If on bot-details page, do nothing or handle as needed
        return redirect(referrer_path)

    else:
        return redirect('bot_details', bot_id=bot.id)
    

@login_required
def use_api_key(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key_id = data.get('api_key')

            if api_key_id:
                selected_api = ApiCredentials.objects.get(id=api_key_id)
                request.session['selected_api_key'] = selected_api.api_key
                request.session.modified = True
                return JsonResponse({'status': 'success', 'message': 'API key set successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'API key ID not found.'}, status=400)
        except (json.JSONDecodeError, ApiCredentials.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid API key or data.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

bot_processes={}
@login_required
def run_bot(request, bot_id):
    bot = get_object_or_404(TelegramBotCredentials, id=bot_id)

    api_key = request.session.get('selected_api_key', ApiCredentials.get_active_key())
    if not api_key:
        return JsonResponse({'status': 'error', 'message': 'API key not found'}, status=400)

    if not request.user.is_superuser and bot.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'You do not have permission to control this bot'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')

            

            if action == 'start':
                if bot_id in bot_processes:
                    return JsonResponse({'status': 'error', 'message': 'Bot is already running'}, status=400)

                channel_path = os.path.join( 'bot.py')

                # Properly format the command with spaces between arguments
                command = (
        f'python {channel_path} '
        f'--token {bot.token} '
        f'--api_id {bot.api_id} '
        f'--api_hash {bot.api_hash} '
        f'--group_username {bot.group_username} '
        f'--channel_username {bot.channel_username} '
        f'--api_key {api_key} '
        f'--phone_number {bot.phone_number} '  # Add a space here
    )

                

                try:
                    process = subprocess.Popen(command)
                    bot_processes[bot_id] = process
                    return JsonResponse({'status': 'success', 'message': 'Bot is running'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            elif action == 'stop':
                if bot_id not in bot_processes:
                    return JsonResponse({'status': 'error', 'message': 'Bot is not running'}, status=400)

                process = bot_processes.pop(bot_id)
                process.terminate()
                process.wait()
                return JsonResponse({'status': 'success', 'message': 'Bot has stopped'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def upload_csv_page(request):

    api_form = ApiInputForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')  # Detect which button was clicked

        # Action: Save API
        if action == 'save_api':
            api_key = request.POST.get('api_key')

            if api_key:
                # Ensure no duplicate API keys get saved in the database
                if not ApiCredentials.objects.filter(api_key=api_key).exists():
                    ApiCredentials.objects.create(api_key=api_key)
                    messages.success(request, f'API key "{api_key}" saved successfully.')
                else:
                    messages.warning(request, 'This API key already exists in the database.')
            else:
                messages.error(request, 'Please enter an API key.')

        # Action: Set API
        elif action == 'set_api':
            previous_api_id = request.POST.get('previous_apis')

            if previous_api_id:
                # Deactivate all other APIs
                ApiCredentials.objects.update(is_active=False)

                selected_api = ApiCredentials.objects.get(id=previous_api_id)
                selected_api.is_active = True
                selected_api.save()

                # Save the selected API key as the active API key in the session
                request.session['selected_api_key'] = selected_api.api_key
                request.session.modified = True
                messages.success(request, f'API key "{selected_api.api_key}" set as active.')
            else:
                messages.error(request, 'Please select an API key from the dropdown.')

        return redirect('upload_csv_page')

    # Set active API key to display
    active_api = request.session.get('selected_api_key', ApiCredentials.get_active_key())

    return render(request, 'home/upload_csv.html', {
        'api_form': api_form,
        'active_api': active_api,
        'available_apis': ApiCredentials.objects.all()  # Display all available API keys
    })


@login_required
def save_api_key(request):
    api_form = ApiInputForm(request.POST or None)

    if api_form.is_valid():
        api_key = api_form.cleaned_data.get('api_key')
        previous_api = api_form.cleaned_data.get('previous_apis')

        # Save new API key or use the selected one
        if not previous_api:
            ApiCredentials.objects.create(api_key=api_key)
        else:
            api_key = previous_api.api_key  # Use the selected previous API

        # Set the new active API key in session
        request.session['selected_api_key'] = api_key
        request.session.modified = True
        messages.success(request, 'API key saved successfully.')
        return redirect('upload_csv_page')

    messages.error(request, 'Failed to save API key.')
    return redirect('upload_csv_page')


@login_required
def upload_csv_file(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('upload_csv_page')

        df = pd.read_csv(csv_file)
        # Process the CSV file here (same logic as before)

        messages.success(request, 'CSV file uploaded and processed successfully.')
        return redirect('upload_csv_page')

    messages.error(request, 'Failed to upload CSV.')
    return redirect('upload_csv_page')

@login_required
def user_bot_data(request):
    bots = TelegramBotCredentials.objects.filter(user=request.user)
    bot_data = []

    # Initialize bot variable to None in case no bot is found
    bot = None

    if bots.exists():
        for bot in bots:
            bot_data.append({
                'id': bot.id,
                'token': bot.token,
                'api_id': bot.api_id,
                'api_hash': bot.api_hash,
                'group_username': bot.group_username,
                'channel_username': bot.channel_username,
                'phone_number':bot.phone_number,
            })
    
    return render(request, 'home/data.html', {'bot_data': bot_data, 'bot': bot, 'user': request.user})

 # For regular expression matching


@login_required
def delete_bot(request, bot_id):
    # Admins can delete any bot, regular users can delete their own bots
    if request.user.is_superuser:
        bot = get_object_or_404(TelegramBotCredentials, id=bot_id)
    else:
        bot = get_object_or_404(TelegramBotCredentials, id=bot_id, user=request.user)

    if request.method == 'POST':
        bot.delete()
        messages.success(request, "Bot deleted successfully")
        session_file = f"session_{bot.phone_number.replace('+', '')}.txt"  # Adjust as needed
        session_file_path = os.path.join(settings.MEDIA_ROOT, session_file)  # Ensure correct path

        # Delete the session file if it exists
        if os.path.exists(session_file_path):
            os.remove(session_file_path)
            print(f"Deleted session file: {session_file_path}")
        # Get the referrer URL path
        referrer = request.META.get('HTTP_REFERER', '')
        print(f"Referrer: {referrer}") 
        referrer_path = referrer.split('://')[-1].split('/', 1)[-1]  # Remove the domain portion
        print(f"Referrer Path: {referrer_path}")  # Debugging: print the referrer path

        # Redirect based on the referrer path or fallback
        if 'bot-data' in referrer:
            # Redirect back to /bot-data/ if deleting from bot_data page
            return redirect(referrer) # Ensure 'bot_data' is the correct name for your URL pattern
         
        elif re.match(r'^bot-details/\d+/$', referrer_path):
            # Redirect back to /bot-details/<bot_id>/ if the referrer path contains a bot ID
            return redirect(user_list)
        else:
            # Else part for URLs containing /bot-details/ with a unique bot ID
            if '/bot-details/' in referrer_path and re.search(r'\d+', referrer_path):
                # Handle bot-details/<bot_id> URL case here
                return redirect(referrer_path)
            else:
                # Default redirect if no match
               return redirect('bot_data')

    return HttpResponse('Method not allowed', status=405)

def user_list(request):
    users = User.objects.filter(is_superuser=False) 
    context = {
        'users': users
    }
    return render(request, 'home/tables.html', context)


@user_passes_test(lambda u: u.is_superuser)  # Ensure only superusers can delete
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list')  # Replace with your actual URL name for the user list


@login_required
def update_bot(request, bot_id):
    
    bot = get_object_or_404(TelegramBotCredentials, id=bot_id)

    if not request.user.is_superuser and bot.user != request.user:
        return HttpResponseForbidden("You do not have permission to update this bot")

    if request.method == 'POST':
        form = TelegramBotForm(request.POST, instance=bot)  # Removed user argument
        if form.is_valid():
            form.save()
            messages.success(request, "Data Saved successfully!")
            return redirect('user_bot_data')
    else:
        form = TelegramBotForm(instance=bot)

    # return render(request, 'home/update_bot.html', {'form': form, 'bot': bot})
BOT_RUNNING_FLAG = "bot_running.flag"

def check_if_bot_running():
    return os.path.isfile(BOT_RUNNING_FLAG)

def set_bot_running():
    with open(BOT_RUNNING_FLAG, 'w') as f:
        f.write("Bot is running")

def remove_bot_running():
    if os.path.isfile(BOT_RUNNING_FLAG):
        os.remove(BOT_RUNNING_FLAG)