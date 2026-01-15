# Google Places API Key Setup Guide

## Issue: "API keys with referer restrictions cannot be used with this API"

Your current API key has **HTTP referrer restrictions** that prevent it from being used in server-side applications. This is common for API keys created for web applications.

## Solution: Remove Referrer Restrictions

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/apis/credentials
2. Sign in with your Google account

### Step 2: Find Your API Key

1. Look for your API key in the list (it starts with `AIzaSyA...`)
2. Click on the API key name to edit it

### Step 3: Update Restrictions

You have two options:

#### Option A: Remove All Restrictions (Easiest)
1. Under "Application restrictions", select **"None"**
2. Click **"Save"**
3. Wait 1-2 minutes for changes to propagate

#### Option B: Use IP Address Restriction (More Secure)
1. Under "Application restrictions", select **"IP addresses"**
2. Click **"Add an item"**
3. Add your computer's IP address or use `0.0.0.0/0` for testing (less secure)
4. Click **"Save"**
5. Wait 1-2 minutes for changes to propagate

### Step 4: Verify API is Enabled

1. In Google Cloud Console, go to: https://console.cloud.google.com/apis/library
2. Search for **"Places API"**
3. Make sure it shows **"API Enabled"**
4. If not, click **"Enable"**

### Step 5: Check Billing

The Places API requires a billing account:

1. Go to: https://console.cloud.google.com/billing
2. Make sure billing is enabled
3. Google provides $200/month free credit which is usually enough for testing

## Alternative: Create a New API Key

If you want to keep your existing key restricted for web use, create a new one:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"API key"**
4. Click **"Close"** (don't restrict it yet)
5. Copy the new API key
6. Update `interactive_void_report.py` or pass it when running the script

## Testing Your API Key

After making changes, test with a simple curl command:

```bash
curl "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=34.0522,-118.2437&radius=1000&type=store&key=YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual key.

**Success response:**
```json
{
  "results": [...],
  "status": "OK"
}
```

**Still restricted:**
```json
{
  "error_message": "API keys with referer restrictions cannot be used with this API.",
  "status": "REQUEST_DENIED"
}
```

## Cost Estimate

Places API (Nearby Search) pricing:
- $32 per 1,000 requests
- Each search typically uses 1-3 requests (due to pagination)
- Google gives $200/month free credit

**Example:**
- 10 searches per day = ~30 requests/day = ~900 requests/month
- Cost: ~$28.80/month
- **With free credit: $0** (covered by Google's $200/month credit)

## Security Best Practices

1. **Don't share your API key publicly**
2. **Use IP restrictions** when possible
3. **Set up API quotas** to prevent unexpected charges:
   - Go to: https://console.cloud.google.com/apis/api/places-backend.googleapis.com/quotas
   - Set daily limits

4. **Monitor usage**:
   - Go to: https://console.cloud.google.com/apis/api/places-backend.googleapis.com/metrics
   - Check daily usage

## Need Help?

If you're still having issues:

1. **Check API Status**: https://status.cloud.google.com/
2. **View Quota Usage**: https://console.cloud.google.com/apis/dashboard
3. **Check Error Logs**: https://console.cloud.google.com/logs

## Quick Reference

- **Console**: https://console.cloud.google.com
- **API Credentials**: https://console.cloud.google.com/apis/credentials
- **Places API**: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
- **Billing**: https://console.cloud.google.com/billing
