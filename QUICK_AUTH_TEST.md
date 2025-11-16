# Quick Setup for Authentication

## Step 1: Restart Flask Server
The .env file has been updated with:
- `SECRET_KEY` - for JWT token encryption
- `GOOGLE_CLIENT_ID` - placeholder for Google OAuth

**Restart your Flask server now:**
```bash
# Stop current Flask server (Ctrl+C)
# Then restart:
flask run
```

## Step 2: Test Email/Password Registration

1. Open http://localhost:5173
2. Click **"Sign Up"** button in navbar
3. Fill in the form:
   - Full Name: Your Name
   - Email: test@example.com
   - Password: password123
   - Confirm Password: password123
4. Click **"Create Account"**
5. You should be logged in automatically!

## Step 3: Test Login

1. Click **"Logout"** 
2. Click **"Login"** button
3. Enter your credentials
4. Click **"Sign In"**

## Google OAuth Setup (Optional)

To enable "Sign in with Google":

1. Go to https://console.cloud.google.com/
2. Create a project or select existing
3. Enable "Google+ API"
4. Go to Credentials → Create OAuth Client ID
5. Choose "Web application"
6. Add authorized JavaScript origins:
   - http://localhost:5173
   - http://localhost:3000
7. Copy the Client ID
8. Update `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-actual-client-id-here.apps.googleusercontent.com
   ```
9. Restart Flask server

## Troubleshooting

### "Registration failed" or "Login failed"
- Make sure Flask server is running
- Check Flask terminal for errors
- MongoDB must be running

### Modal not showing
- Check browser console for errors
- Make sure frontend dev server is running

### Can't connect to backend
- Backend: http://localhost:5000
- Frontend: http://localhost:5173
- Check CORS settings in app.py

## What's Working Now:
✅ Email/Password Registration
✅ Email/Password Login  
✅ JWT Token Authentication
✅ User Session Management
✅ Logout Functionality
✅ User Profile Display (name, email)

## What Needs Google Setup:
⏳ Google OAuth Login (needs GOOGLE_CLIENT_ID)

---

**Try it now! Click "Sign Up" in your navbar!** 🚀
