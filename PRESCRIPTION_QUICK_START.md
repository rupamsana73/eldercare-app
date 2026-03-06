# 🚀 Smart Prescription System - Quick Start Guide

## ⚡ Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer as Administrator
3. Keep default path: `C:\Program Files\Tesseract-OCR`
4. Done! ✓

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 3: Verify Setup
```bash
python manage.py runserver
```
Visit: http://localhost:8000/prescription-reader/

---

## 📋 Step-by-Step Testing

### Test 1: Upload a Prescription Image

1. **Access the feature:**
   - Go to Dashboard → Prescription Reader
   - Or directly: `/prescription-reader/`

2. **Prepare test image:**
   - Print a prescription or take a photo of a real one
   - Or create one with medicine names clearly written
   - Must be JPG or PNG format
   - File size < 10MB

3. **Upload:**
   - Click "Upload Prescription" area
   - Or drag-drop an image
   - Image preview should appear
   - Click "Process Prescription"

### Test 2: View Results

1. **Processing:**
   - See spinning animation
   - "Processing Prescription..." message
   - Wait 10-30 seconds

2. **Results displayed:**
   - ✓ Green alert: "Prescription Detected!"
   - Extracted text shown
   - List of detected medicines with confidence scores

### Test 3: Select Medicines

1. **Checkboxes appear:**
   - Shows each detected medicine
   - Shows source + confidence %
   - High confidence (>85%) pre-selected

2. **Select options:**
   - Check/uncheck medicines to add
   - Button updates: "Add 2 Medicines"
   - Leave unchecked to skip

### Test 4: Add to Medicine List

1. **Click "Add Medicines":**
   - Processing spinner appears
   - Calls API endpoint

2. **Success message:**
   - "✅ Medicines Added!"
   - "Your medicines have been added..."
   - Auto-redirects to "Manage Medicines" in 2 seconds

3. **Verify in Manage Medicines:**
   - New medicines appear in list
   - Status: "Active"
   - Notes: "Added from prescription scan"
   - Reminder enabled
   - Classification assigned

---

## 🧪 Test Cases

### Test Case 1: Typical Clear Prescription
**Input:** Photo of well-written prescription
**Expected:**
- ✓ Text extracted correctly (95%+)
- ✓ Medicines matched (85%+ confidence)
- ✓ User selects and adds
- ✓ Appears in dashboard

**Pass/Fail:** ___

### Test Case 2: Handwritten Prescription
**Input:** Handwritten prescription photo
**Expected:**
- ✓ Preprocessing improves detection
- ✓ Some ambiguous text handled
- ✓ Main medicines identified
- ✓ User confirms matches

**Pass/Fail:** ___

### Test Case 3: Blurry Image
**Input:** Out-of-focus prescription
**Expected:**
- ✓ Still processes (preprocessing helps)
- ✓ May have lower confidence
- ✓ User can adjust selections
- ✓ Option to re-upload clearer image

**Pass/Fail:** ___

### Test Case 4: Non-Prescription Image
**Input:** Photo of something that's not a prescription
**Expected:**
- ✓ Error: "This doesn't look like a medical prescription"
- ✓ User redirected to upload
- ✓ Graceful failure

**Pass/Fail:** ___

### Test Case 5: Duplicate Medicines
**Input:** Upload prescription with medicine already in user's list
**Expected:**
- ✓ Skipped in confirmation
- ✓ Message shows "Already exists"
- ✓ Only new medicines added

**Pass/Fail:** ___

### Test Case 6: Rate Limiting
**Input:** 10+ prescription uploads in same day
**Expected:**
- ✓ First 10 succeed
- ✓ 11th returns: "Rate limit exceeded. Max 10 scans per day."
- ✓ User can try again next day

**Pass/Fail:** ___

---

## 🔍 Feature Checklist

### Upload Section
- [ ] Drag-drop upload works
- [ ] Click upload works
- [ ] File size validation works
- [ ] File type validation works
- [ ] Image preview displays

### Processing
- [ ] Loading animation displays
- [ ] Processing completes
- [ ] Success/error alerts shown

### Results Display
- [ ] Extracted text shown
- [ ] Detected medicines listed
- [ ] Confidence scores accurate
- [ ] Database matches shown

### User Selection
- [ ] Checkboxes functional
- [ ] Selection state updates
- [ ] Button text updates
- [ ] Pre-selection works (>85%)

### Medicine Addition
- [ ] API call succeeds
- [ ] Medicines created in database
- [ ] MedicineTime entries created
- [ ] Drug classification assigned
- [ ] Reminders enabled

### Integration
- [ ] Appears in "Manage Medicines"
- [ ] Appears in "Smart Dashboard"
- [ ] Appears in adherence tracking
- [ ] Drug stats updated

---

## 🐛 Debugging Tips

### Check if OCR Working
```python
# In Django shell
from accounts.ocr_processor import load_medicine_dataset

# Should return list of medicines
medicines = load_medicine_dataset()
print(f"Loaded {len(medicines)} medicines")
```

### Check CSV Loading
```python
import pandas as pd

df = pd.read_csv('data/A_Z_medicines_dataset_of_India.csv')
print(df.columns)
print(f"Medicines: {len(df)}")
print(df['name'].head(10))
```

### Check Fuzzy Matching
```python
from accounts.ocr_processor import fuzzy_match_medicines

results = fuzzy_match_medicines(
    ["Paracetamol", "Azithromycin", "Metformin"],
    threshold=85
)
for r in results:
    print(f"{r['detected']} → {r['matched']} ({r['confidence']}%)")
```

### View API Response
```bash
# In browser console
fetch('/prescription-reader/process/', {
    method: 'POST',
    body: formData,
    headers: {...}
})
.then(r => r.json())
.then(d => console.log(d))
```

---

## 📊 Sample Test Data

### Prescription 1 (Print & Photograph)
```
Rx
Dr. Sharma's Clinic
Date: 7-Mar-2026

Tab Paracetamol 500mg - 2 OD (twice daily)
Tab Azithromycin 500mg - 1 OD x 5 days
Tab Metformin 500mg - 1 BD (before meals)
Syrup Cough Suppressant - 5ml TDS (three times)

Sig: Follow instructions
Dr. Rajesh Sharma
License: 12345
```

**Expected Matches:**
- Paracetamol (95%)
- Azithromycin (95%)
- Metformin (95%)
- (Cough Suppressant may not match exactly)

### Prescription 2 (Quick Text Test)
```
Rx Tab Ibuprofen 400mg OD
Tab Enalapril 5mg OD  
Inj Insulin SC
```

**Expected Matches:**
- Ibuprofen (>85%)
- Enalapril (>85%)
- (Insulin may match but form is different)

---

## ✨ Demo Workflow

### Complete Flow (2-3 minutes)

1. **Start:** Click "Prescription Reader" from menu
2. **Upload:** Drag prescription image to upload area
3. **Preview:** Image shows with preview
4. **Process:** Click "Process Prescription" button
5. **Wait:** Watch loading animation (10-30 sec)
6. **Results:** See detected medicines with matches
7. **Confirm:** Check medicines to add (pre-selected >85%)
8. **Add:** Click "Add 2 Medicines" button
9. **Success:** See "✓ Medicines Added!" message
10. **View:** Auto-redirects to "Manage Medicines"
11. **Verify:** See new medicines in list

---

## 📞 FAQ During Testing

**Q: How do I reset/clear medicines added from test?**
A: Go to "Manage Medicines" → Delete each test medicine

**Q: Can I test without Tesseract installed?**
A: OCR will fail gracefully, but you won't be able to test text extraction. Install it first.

**Q: Image upload stuck?**
A: Check file size (<10MB), format (JPG/PNG), browser console for errors

**Q: Medicines not appearing after add?**
A: Refresh the page or check "Manage Medicines" - page auto-redirects after 2 sec

**Q: How do I test rate limiting?**
A: Upload 11+ prescriptions in same day - 11th will be rejected

**Q: Can I see the extracted text?**
A: Yes, in results section before selecting medicines

---

## 🎯 Success Criteria

### System is Working if:
- ✅ Image uploads successfully  
- ✅ OCR extracts text (at least 50 chars)
- ✅ Medicines detected (at least 2)
- ✅ Fuzzy matching shows confidences  
- ✅ Checkboxes select/deselect medicines
- ✅ Button click adds medicines
- ✅ New medicines appear in "Manage Medicines"
- ✅ Drug classifications assigned
- ✅ Appear in "Smart Dashboard"

### Performance:
- ⏱️ Upload completes in <1 second
- ⏱️ OCR completes in 10-30 seconds (depends on Tesseract)
- ⏱️ Fuzzy matching completes in <1 second
- ⏱️ UI responsive on mobile

---

## 🚀 Going Live

Once testing is complete:

1. **Update any settings needed** (already done)
2. **Test with real user data** (use test account)
3. **Monitor logs** for any errors
4. **Train users** on how to use feature
5. **Gather feedback** for improvements
6. **Monitor API** for rate limits/errors

---

## 📝 Testing Notes Template

```
Test Date: _______________
Tester: ___________________
OS: Windows / Mac / Linux
Browser: __________________

Test Results:
- Upload: PASS / FAIL
- Processing: PASS / FAIL
- Results Display: PASS / FAIL
- Medicine Selection: PASS / FAIL
- Medicine Addition: PASS / FAIL
- Dashboard Integration: PASS / FAIL

Issues Found:
1. ________________________________
2. ________________________________
3. ________________________________

Overall Status: WORKING / NEEDS FIX
```

---

## 🎓 Next Steps

After successful testing:

1. **Read:** SMART_PRESCRIPTION_SYSTEM.md (comprehensive guide)
2. **Deploy:** To production environment
3. **Monitor:** Check logs for any OCR/matching issues
4. **Iterate:** Gather user feedback for improvements
5. **Optimize:** Tune thresholds based on real data

---

**Ready to test? Let's go! 🚀**
