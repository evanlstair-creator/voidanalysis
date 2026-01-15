# Fix Google Places API Key - Step by Step

## Problem
Getting error: "The provided API key is invalid"

## Root Cause
The API key exists, but the **Places API (New)** might not be enabled for your project.

## Solution: Enable Places API

### Step 1: Enable the API

1. Go to: https://console.cloud.google.com/apis/library
2. Search for: **"Places API (New)"**
3. Click on **"Places API (New)"**
4. Click **"Enable"** button
5. Wait 1-2 minutes for it to activate

### Step 2: Verify API Key Access

1. Go back to: https://console.cloud.google.com/apis/credentials
2. Click on **"API key 1"** (the name, not "Show key")
3. Scroll to **"API restrictions"** section
4. You should see two options:
   - ⭕ **Don't restrict key** (currently selected - this is fine)
   - ⚪ Restrict key (optional for security)

### Step 3: Optional - Restrict Key for Security

While "Don't restrict key" works, it's recommended to restrict it:

1. Select ⚪ **"Restrict key"**
2. In the dropdown that appears, search and check:
   - ✅ **Places API (New)**
3. Click **"Save"**
4. Wait 1 minute for changes to propagate

### Step 4: Test the Key

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"

# Test with your key
python interactive_void_report.py
```

Enter when prompted:
- **API Key:** [Click "Show key" and paste it]
- **Coordinates:** 33.423248658058945, -96.5887672571626
- **Radius:** 5

## If Still Not Working

### Option A: Create Brand New Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ Create credentials"** → **"API Key"**
3. A dialog shows your new key - **COPY IT IMMEDIATELY**
4. Click **"Restrict Key"**
5. Name it: "Retail Void Tool Key"
6. Under **API restrictions**:
   - Select "Restrict key"
   - Check ✅ "Places API (New)"
7. Under **Application restrictions**:
   - Leave as "None" (for command-line use)
8. Click **"Save"**
9. Test with the new key

### Option B: Check Billing

The API key might be disabled due to billing:

1. Go to: https://console.cloud.google.com/billing
2. Make sure billing is enabled
3. You get $200/month free credit (enough for ~300 location searches)

## Cost Information

### Per Coordinate Search:
- **Typical cost:** $0.50 - $0.75
- **API calls:** 16-24 Nearby Search requests
- **Pricing:** $32 per 1,000 requests

### Free Tier:
- **$200/month free** from Google
- Covers ~260-400 location searches per month
- Resets monthly

### Example Costs:
- 10 locations: ~$5-7 (FREE with monthly credit)
- 50 locations: ~$25-37 (FREE with monthly credit)
- 100 locations: ~$50-75 (FREE with monthly credit)
- 500 locations: ~$250-375 (need to pay ~$50-175)

### Ways to Reduce Costs:

1. **Reduce place types** - Edit `void_report.py` line 317:
   ```python
   # Current: 8 types
   place_types = ['store', 'restaurant', 'cafe', 'shopping_mall',
                  'supermarket', 'clothing_store', 'convenience_store',
                  'department_store']

   # Reduced: 4 types (cuts cost in half)
   place_types = ['store', 'restaurant', 'supermarket', 'clothing_store']
   ```

2. **Smaller radius** - Use 3 miles instead of 5 miles

3. **Cache results** - Don't re-run same locations

## Quick Test URL

Test if your API key works in a browser:

```
https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=33.4232,-96.5888&radius=8000&type=store&key=YOUR_API_KEY_HERE
```

Replace `YOUR_API_KEY_HERE` with your actual key. If it works, you'll see JSON results. If not, you'll see an error message.

## Summary

**Most likely issue:** Places API (New) not enabled for your project

**Fix:** Enable it at https://console.cloud.google.com/apis/library

**Cost:** ~$0.50-0.75 per location, with $200/month free (covers 260+ locations)
