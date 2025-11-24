# Google OAuth Setup Instructions

## Error: redirect_uri_mismatch Fix

### Step 1: Check Your Current Redirect URI

When you click "Continue with Google", check your terminal/console. You should see:
```
DEBUG: Redirect URI being used: http://127.0.0.1:2219/auth/google/callback/
```

### Step 2: Add Redirect URI to Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click on your **OAuth 2.0 Client ID** (the one with Client ID: `242474501721-he2h1p6k0ji6ijj3hflrv1kiljnu78qs`)
5. Under **Authorized redirect URIs**, click **+ ADD URI**
6. Add these EXACT URIs (one by one):

```
http://127.0.0.1:2219/auth/google/callback/
http://localhost:2219/auth/google/callback/
http://127.0.0.1:8000/auth/google/callback/
http://localhost:8000/auth/google/callback/
```

**IMPORTANT:**
- ✅ Include the trailing slash `/`
- ✅ Use exact port number (2219 or 8000)
- ✅ No spaces before or after
- ✅ Use lowercase

7. Click **SAVE**

### Step 3: Wait a Few Minutes

Google sometimes takes 1-2 minutes to propagate the changes.

### Step 4: Test Again

1. Restart your Django server
2. Clear your browser cache (Ctrl+Shift+Delete)
3. Try "Continue with Google" again

### Step 5: Verify the Redirect URI

Check your terminal when clicking the button. The DEBUG message will show the exact redirect URI being used. Make sure this EXACT URI (with exact port number) is in Google Cloud Console.

## Common Issues

### Issue 1: Still Getting Error
- Wait 2-3 minutes after saving in Google Cloud Console
- Clear browser cache completely
- Try in incognito/private window
- Make sure you're using the correct Google account (developer account)

### Issue 2: Port Changed
If your port changes (e.g., from 2219 to 8000):
1. Update Google Cloud Console with new redirect URI
2. Or run server on specific port: `python manage.py runserver 8000`

### Issue 3: Trailing Slash
Google is very strict about the trailing slash. Make sure:
- Your redirect URI in Google Cloud Console ends with `/`
- The code generates URI ending with `/`

## Current Configuration




