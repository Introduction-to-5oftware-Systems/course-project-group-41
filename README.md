# ISS_Assignment_1

# Pages

1. Landing page: The user enters the website through this page.

2. Sign in page: The user signs in through this page.

3. Sign up page: The user signs up through this page.

4. Admin page: Shows details of all users to the admins.

5. Home page: allows for the user to add images via drag-and-drop and start the process of creating a video.

6. Video creation page: Allows the user to customize the video settings, and edit the actual video.

7. Output page: When the video is finally created, this page pops up allowing the user to download.



# follow this file order  thingy in your html for your html pages
group 41
    /static
        /css
            style.css
        /js
            script.js
        /images
            image.jpg
    /templates
        index.html
    app.py
## link it like this
<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
<img src="{{ url_for('static', filename='images/my_image.jpg') }}" alt="My Image">
# images like this


# What routes to render html pages
- /video to go to video editor
- /output for output page

# random
- ishan -you will have to change the code for the /login  route to check for the usernames and password in the data base
- passwords will be hashed using bcrypt
- I have username and password variab

# bugs
- not able to go from login page to sign up page
- need add the case when user tries accessing protected routes they are redirected to home
- dont need login button in any other page other than index as they are  only accessible once logged in



# questions
- do we need to have a different login system for admins