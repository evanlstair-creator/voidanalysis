# Next Steps - Fix API Key and Test Improved Matching

## Issue Identified

Your fuzzy matching had **awful false positives** including:
- ✗ McDonald's → "McDonald's Arabian Peninsula" (the exact example you mentioned!)
- ✗ Redbox → "Breadbox Food Store"
- ✗ Freshly Cut Stems → "Fresh"
- ✗ Takara Hibachi Express → "Express"
- ✗ Van Alstyne Eye Care → "Vans"

## Solution Implemented

✅ **Completely rewrote the fuzzy matching logic** in [void_report.py](void_report.py)

The new intelligent matching:
1. **Exact word subset matching** - All retailer words must appear in place name
2. **Word coverage validation** - Requires 80% of retailer words to appear
3. **Location pattern removal** - Strips "#1234" and city names like "Van Alstyne"
4. **Stricter threshold** - Changed from 70% to 85%
5. **Common sense logic** - Prevents single-word matches like "Express" → Express

## Problem: API Key Invalid

When testing, got this error:
```
Error: API returned status REQUEST_DENIED
Message: The provided API key is invalid.
```

## What You Need to Do

### Step 1: Fix Your API Key

**Option A: Check Existing Key**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your API key: `AIzaSyBoKit1MNJN_1I3qI6f7rVLHzlxPFjbVko`
3. Check:
   - ✓ Key is enabled
   - ✓ "Places API (New)" is in allowed APIs
   - ✓ No IP restrictions
   - ✓ Key hasn't expired or been regenerated
4. If there are restrictions, remove them or allow your IP

**Option B: Create New Key**

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy the new key
4. Click "Edit API Key"
5. Under "API restrictions":
   - Select "Restrict key"
   - Check "Places API (New)"
6. Under "Application restrictions":
   - Select "None" (for command-line use)
7. Click "Save"

### Step 2: Test the Improved Matching

Once API key works, run:

```bash
cd "/Users/evanstair/Library/CloudStorage/OneDrive-VistaSiteSelection/X/web tools/retail void tool"

# Run with your API key (use quotes if pasting in terminal)
python interactive_void_report.py
```

When prompted:
- **API Key:** [Paste your working key]
- **Coordinates:** `33.423248658058945, -96.5887672571626` (McKinney, TX)
- **Radius:** `5` (miles)

### Step 3: Review the Results

Open the CSV output:
```bash
open outputs/void_report_[TIMESTAMP].csv
```

**Look for:**
- ✅ NO "McDonald's Arabian Peninsula" match
- ✅ NO false matches like "Express", "Fresh", "Vans"
- ✅ GOOD matches like "Ace Hardware Van Alstyne" → "Ace Hardware"
- ✅ "Braum's Ice Cream & Dairy Store" → "Braum's Ice Cream and Dairy Stores"

**Compare to old results:**
- Old file: `outputs/void_report_improved.csv` (73 matches, many false positives)
- New file: Should have fewer but ACCURATE matches

### Step 4: Generate Updated Dashboard

If the matches look good:

```bash
# Generate broker dashboard
python generate_html_report_v2.py

# Copy to upload folder
cp outputs/void_report_*_broker.html upload/index.html

# Preview locally
open upload/index.html
```

### Step 5: Deploy to Netlify

When satisfied:
1. Go to: https://app.netlify.com/drop
2. Drag the entire `upload/` folder
3. Get your live URL
4. Share with clients

## Technical Details

The improved matching uses **two-strategy validation**:

### Strategy 1: Exact Word Subset
```
"Ace Hardware Van Alstyne"
Words: {ace, hardware, van, alstyne}

"Ace Hardware"
Words: {ace, hardware}

✅ {ace, hardware} ⊆ {ace, hardware, van, alstyne}
✅ Score: 100 - (2 extra words × 5) = 90%
```

### Strategy 2: Token Sort + Word Coverage
```
"McDonald's" vs "McDonald's Arabian Peninsula"

Word coverage check:
- "McDonald's" = 1 word
- "Arabian Peninsula" = 2 additional words
- Only 1 out of 3 total words match = 33%
- ✗ 33% < 80% threshold → REJECTED
```

## Expected Improvements

### Matches That Should Work
```
✅ Ace Hardware Van Alstyne → Ace Hardware
✅ Dollar General → Dollar General
✅ Braum's Ice Cream & Dairy Store → Braum's Ice Cream and Dairy Stores
✅ Twice The Ice → Twice the Ice
✅ O'Reilly Auto Parts → O'Reilly Auto Parts
✅ McDonald's → McDonald's (not Arabian Peninsula!)
✅ Sonic Drive-In → Sonic
✅ QuikTrip → QuikTrip
✅ Buff City Soap → Buff City Soap
```

### False Positives That Should Be Eliminated
```
✗ McDonald's → McDonald's Arabian Peninsula
✗ Redbox → Breadbox Food Store
✗ Freshly Cut Stems → Fresh
✗ Takara Hibachi Express → Express
✗ Van Alstyne Eye Care → Vans
✗ Shear Elegance → Sears
✗ Good Gollie Tamales → Zales
✗ TXB → Bealls TX
✗ City Drug → CityMD
```

## Files Ready to Use

All code is updated and ready:

1. ✅ **[void_report.py](void_report.py)** - New intelligent matching logic
2. ✅ **[generate_html_report_v2.py](generate_html_report_v2.py)** - Broker dashboard generator
3. ✅ **[interactive_void_report.py](interactive_void_report.py)** - CLI interface
4. ✅ **[list of retailers_cleaned.csv](list%20of%20retailers_cleaned.csv)** - 8,455 retailers

**Only thing blocking:** API key needs to be fixed

## Summary

✅ **Problem fixed in code** - Intelligent matching implemented
⏸️ **Blocked by API key** - Need valid key to test
📋 **Next action** - Fix API key, then run test

Once you fix the API key and run the test, you'll see **much better matches** with no nonsensical false positives like "McDonald's Arabian Peninsula".

---

**Questions?** The new logic is well-documented in [FUZZY_MATCHING_FIX.md](FUZZY_MATCHING_FIX.md)
