# 🔧 Smart Prescription System - Troubleshooting Guide

## Quick Diagnostics

### Issue: "Tesseract OCR not found on system"

**Symptoms:**
- Page loads fine
- Upload works
- Processing starts but fails with text extraction error

**Diagnosis:**
```bash
# Check if Tesseract is installed
where tesseract  # Windows
which tesseract  # Mac/Linux
```

**Solutions:**

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Download version 5.x
3. Run installer with admin rights
4. Install to: `C:\Program Files\Tesseract-OCR`
5. Restart Django server

**macOS:**
```bash
# If Homebrew not installed:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Tesseract:
brew install tesseract

# Verify:
tesseract --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr

# Verify:
tesseract --version
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install tesseract

# Verify:
tesseract --version
```

---

### Issue: ImportError - "No module named cv2" (OpenCV)

**Symptoms:**
- Prescription upload page loads
- Upload works but preprocessing fails
- Error mentions "cv2" or "opencv"

**Solution:**
```bash
# Install OpenCV
pip install opencv-python==4.11.0.86

# Or upgrade pip first
pip install --upgrade pip
pip install opencv-python

# Verify installation
python -c "import cv2; print(cv2.__version__)"
```

**If still failing:**
```bash
# Check Python version (should be 3.7+)
python --version

# Try specifying platform
pip install --target=/path/to/venv opencv-python
```

---

### Issue: ImportError - "No module named rapidfuzz"

**Symptoms:**
- Medicine matching fails with "No module named rapidfuzz"
- Falls back to slower difflib matching automatically
- Performance degraded

**Solution:**
```bash
# Install rapidfuzz
pip install rapidfuzz==3.10.1

# Or from source
pip install --upgrade rapidfuzz

# Verify
python -c "from rapidfuzz import fuzz; print('OK')"
```

**Note:** This is optional - system uses difflib fallback if unavailable, but rapidfuzz is 3-5x faster.

---

### Issue: ImportError - "No module named pandas"

**Symptoms:**
- Medicine dataset fails to load
- Error in ocr_processor.py

**Solution:**
```bash
# Install pandas
pip install pandas==2.2.3

# Verify
python -c "import pandas; print(pandas.__version__)"
```

---

### Issue: "Medicine dataset not found"

**Symptoms:**
- Fuzzy matching returns no results
- Warning in logs: "Medicine dataset not found"
- All medicines marked as "no match"

**Diagnosis:**
```bash
# Check if file exists
ls -la data/A_Z_medicines_dataset_of_India.csv  # Mac/Linux
dir data\A_Z_medicines_dataset_of_India.csv     # Windows
```

**Solution:**

1. **If file missing:** Download Kaggle dataset
   - Source: https://www.kaggle.com/
   - Search: "A-Z Medicine Dataset India"
   - Download CSV file
   - Place in: `data/` folder
   - File should have 'name' column

2. **If file exists but not found:**
   - Check file permissions
   - Ensure pathis correct
   - Try moving to different location

3. **Fix in ocr_processor.py:**
   ```python
   # Line 18, update path if needed:
   csv_path = base_dir / 'data' / 'A_Z_medicines_dataset_of_India.csv'
   
   # Or specify absolute path:
   csv_path = '/absolute/path/to/data/A_Z_medicines_dataset_of_India.csv'
   ```

---

### Issue: Image not Uploading

**Symptoms:**
- File input doesn't accept selection
- Upload button doesn't work
- No file preview shown

**Diagnosis:**
1. Check file format
   - File must be JPG, PNG, or JPEG
   - Check file extension: `.jpg`, `.jpeg`, `.png`

2. Check file size
   - Must be under 10 MB
   - Windows: Right-click file → Properties
   - Mac: Get Info
   - Linux: `ls -lh filename`

3. Check browser console
   - F12 → Console tab
   - Look for JavaScript errors

**Solution:**

```bash
# Convert file if needed (using ImageMagick)
convert image.bmp image.jpg

# Reduce size if needed (using ImageMagick)
convert -resize 50% image.jpg image_small.jpg

# Or using Python:
from PIL import Image
img = Image.open('image.jpg')
img.thumbnail((1280, 720))
img.save('image_small.jpg')
```

**Check file MIME type:**
```bash
# Mac/Linux
file image.jpg

# Windows (PowerShell)
(Get-Item image.jpg).VersionInfo
```

---

### Issue: "Invalid image file (corrupted or wrong format)"

**Symptoms:**
- File accepted by browser
- Gets rejected during processing
- Validation says corrupted

**Causes:**
- File is not actually JPG/PNG despite extension
- File is partially downloaded
- File was incorrectly converted

**Solution:**
```bash
# Verify file integrity (Mac/Linux)
file -i image.jpg

# Check file header (should start with specific bytes)
head -c 4 image.jpg | xxd

# For PNG: 89 50 4E 47 (hex)
# For JPG: FF D8 FF (hex)

# Re-save with Python
from PIL import Image
img = Image.open('corrupted.jpg')
img.save('repaired.jpg')
```

**Use different image:**
- Take new photo of prescription
- Ensure good lighting
- Focus camera clearly
- Avoid shadows/glare

---

### Issue: OCR Returns Empty Text / No Text Detected

**Symptoms:**
- Prescription accepted as valid
- Processing completes
- But extracted_text is empty

**Causes:**
1. Image too blurry
2. Text too small or faint
3. Tesseract quality issues
4. Preprocessing failed

**Solution:**

1. **Improve image quality:**
   - Use better lighting (window light, not flash)
   - Steady camera (use tripod)
   - Focus on text
   - Avoid gloss/shine

2. **Try preprocessing adjustment:**
   Edit `ocr_processor.py`, line 120:
   ```python
   # Increase blur kernel if image too noisy
   blurred = cv2.GaussianBlur(gray, (7, 7), 0)  # Was (5,5)
   
   # Adjust threshold if low contrast
   thresh = cv2.adaptiveThreshold(
       blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
       cv2.THRESH_BINARY, 13, 3  # Adjust 11 and 2
   )
   ```

3. **Debug preprocessing:**
   ```python
   from accounts.ocr_processor import preprocess_image
   import cv2
   
   # Step-by-step debugging
   processed = preprocess_image('path/to/image.jpg')
   
   if processed is not None:
       cv2.imwrite('debug_preprocessed.png', processed)
       # Compare original vs preprocessed
   ```

4. **Test OCR directly:**
   ```python
   import pytesseract
   from PIL import Image
   
   # Set Tesseract path
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   
   img = Image.open('image.jpg')
   text = pytesseract.image_to_string(img)
   print(text)
   ```

---

### Issue: High Confidence But Wrong Medicine Matched

**Symptoms:**
- Confidence shows 95%+
- But matched medicine is incorrect
- e.g., detected "Paracetamol" matched to different drug

**Causes:**
1. OCR misread medicine name
2. Fuzzy matching threshold too low
3. Dataset has similar-named medicines

**Solution:**

1. **Increase threshold:**
   Edit `accounts/views.py`, line ~1348:
   ```python
   # Change from 85 to 90 or 95
   matches = fuzzy_match_medicines(
       detected_medicines,
       medicine_dataset=medicine_dataset,
       user_medicines=user_medicines,
       threshold=90  # Stricter matching
   )
   ```

2. **Debug fuzzy matching:**
   ```python
   from accounts.ocr_processor import fuzzy_match_medicines
   from rapidfuzz import fuzz
   
   detected = "Paracetamol"
   database = load_medicine_dataset()
   
   # Check all close matches
   scores = {}
   for med in database:
       score = fuzz.token_sort_ratio(detected.lower(), med)
       if score > 80:
           scores[med] = score
   
   # Sort and show top matches
   for med, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
       print(f"{med}: {score}")
   ```

3. **Manually review OCR:**
   - Check extracted text in results
   - See what OCR actually extracted
   - May need better image

4. **Let user override:**
   - User can deselect wrong match
   - Can manually type correct medicine name
   - Add as custom medicine

---

### Issue: No Medicines Detected at All

**Symptoms:**
- Prescription correctly identified
- Text extracted (50+ chars)
- But "detected_medicines" array is empty

**Causes:**
1. OCR text doesn't match pattern expectations
2. Medicine names not in standard format
3. Extraction algorithm too strict

**Solution:**

1. **Debug extraction:**
   ```python
   from accounts.ocr_processor import extract_medicine_candidates
   
   extracted_text = """
   Rx
   Dr. Sharma's Clinic
   Tab Paracetamol 500mg OD
   ...
   """
   
   candidates = extract_medicine_candidates(extracted_text)
   print(f"Candidates: {candidates}")
   ```

2. **Check if OCR has keywords:**
   ```python
   from accounts.ocr_processor import PRESCRIPTION_KEYWORDS
   
   text = extracted_text.lower()
   for keyword in PRESCRIPTION_KEYWORDS:
       if keyword in text:
           print(f"Found: {keyword}")
   ```

3. **Relax extraction rules:**
   Edit `ocr_processor.py`, line 350:
   ```python
   # Current: words of 4+ chars after RX keywords
   # Could add: standalone ALL-CAPS words, etc.
   if word.isupper() and len(word) >= 3:  # Was >= 4
       candidates.add(word)
   ```

4. **Update OCR text:**
   - Tesseract may not recognize all medicines
   - Better image helps
   - Try different preprocessing

---

### Issue: Rate Limit Exceeded (429 Error)

**Symptoms:**
- Upload worked fine before
- Now returns "Rate limit exceeded"
- Max 10 scans per day

**Solution:**

1. **Check scan count:**
   ```python
   from django.utils import timezone
   from datetime import date
   from accounts.models import Prescription
   
   user = request.user
   today = date.today()
   
   count = Prescription.objects.filter(
       user=user,
       uploaded_at__date=today
   ).count()
   
   print(f"Scans today: {count}")
   ```

2. **Wait until tomorrow:**
   - Rate resets at midnight UTC
   - Check server timezone settings
   - Or use different user account for testing

3. **Increase limit if needed:**
   Edit `accounts/views.py`, line ~35:
   ```python
   MAX_PRESCRIPTION_PER_DAY = 10  # Change to 20, 50, etc.
   ```

4. **Set per IP instead of per user (advanced):**
   Implement custom rate limiting per IP address

---

### Issue: Medicines Not Appearing After Add

**Symptoms:**
- "✓ Medicines Added!" message shows
- Redirect to /medicine/manage/
- Page loads but medicines not there

**Causes:**
1. Page cache not cleared
2. Database transaction failed silently
3. User filter not matching

**Solution:**

1. **Hard refresh page:**
   - Ctrl+Shift+R (Windows)
   - Cmd+Shift+R (Mac)
   - Clear browser cache

2. **Check database:**
   ```python
   from accounts.models import Medicine
   from django.contrib.auth.models import User
   
   user = User.objects.get(username='testuser')
   medicines = Medicine.objects.filter(user=user)
   print(f"User has {medicines.count()} medicines")
   
   for med in medicines:
       print(f"- {med.name} ({med.status})")
   ```

3. **Check database logs:**
   ```python
   # Enable query logging in settings.py
   LOGGING = {
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
           },
       }
   }
   ```

4. **Verify API response:**
   - Open browser console (F12)
   - Check Network tab
   - Look at /prescription-reader/add-medicines/ response
   - Should show `"added_count": NUMBER`

---

### Issue: Slow Performance / Long Processing Time

**Symptoms:**
- OCR takes >30 seconds
- Fuzzy matching slow
- Page becomes unresponsive

**Causes:**
1. Large image (5-10 MB)
2. Poor Tesseract configuration
3. Large medicine dataset (10k+)
4. Server resources low

**Solution:**

1. **Compress image first:**
   ```python
   from PIL import Image
   
   img = Image.open('large.jpg')
   img.thumbnail((1280, 960))
   img.save('compressed.jpg', quality=85)
   ```

2. **Profile OCR performance:**
   ```python
   import time
   from accounts.ocr_processor import extract_text_with_ocr
   
   start = time.time()
   text, success, _ = extract_text_with_ocr('image.jpg')
   elapsed = time.time() - start
   
   print(f"OCR took {elapsed:.2f} seconds")
   ```

3. **Optimize fuzzy matching:**
   ```python
   # Current: checks all 10k+ medicines
   # Could: pre-filter by word boundaries
   # Could: use substring match first, then fuzzy
   
   # See: ocr_processor.py fuzzy_match_medicines()
   ```

4. **Check server resources:**
   ```bash
   # CPU usage
   top  # Mac/Linux
   tasklist /v  # Windows
   
   # Memory usage
   free -h  # Linux
   vm_stat  # Mac
   ```

5. **Async processing (advanced):**
   Convert to Celery task for background processing
   Store result in database
   Poll from frontend

---

### Issue: CSRF Token Missing

**Symptoms:**
- 403 FORBIDDEN error
- Message: "CSRF token missing"
- In browser console

**Cause:**
- X-CSRFToken header not sent
- Form doesn't have {% csrf_token %}

**Solution:**

**For AJAX requests:**
```javascript
// Get token from DOM
const csrfToken = document.getElementById('csrf-token').value;

// Or extract from cookie
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Send with token in header
fetch('/prescription-reader/process/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken
  },
  body: formData
});
```

---

### Issue: Multiple Recommendations / Different Matches

**Symptoms:**
- Same medicine matches to different names on retry
- Inconsistent fuzzy matching results
- One day it works, next day doesn't

**Cause:**
- Rapidfuzz version differences
- Threshold edge cases (84. vs 85%)
- Different image quality

**Solution:**
```python
# Increase threshold for consistency
threshold=88  # Instead of 85
```

---

## Debug Mode

### Enable Verbose Logging

Edit `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'accounts': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
}
```

### Test Endpoints Directly

```bash
# Process with curl
curl -X POST http://localhost:8000/prescription-reader/process/ \
  -H "X-CSRFToken: token123" \
  -F "image=@prescription.jpg" \
  -v  # verbose (shows headers)

# Add medicines with curl
curl -X POST http://localhost:8000/prescription-reader/add-medicines/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: token123" \
  -d '{"medicines": ["Paracetamol"]}' \
  -v
```

---

## Getting Help

### Check Logs
```bash
# Django logs
tail -f logs/debug.log

# Tesseract output
# Check pytesseract stderr

# Database logs (if enabled)
grep "OCR\|prescription\|medicine" logs/*.log
```

### Run Tests
```bash
python manage.py test accounts.tests
```

### Verify Installation
```bash
python -c "
import pytesseract
import cv2
from rapidfuzz import fuzz
import pandas as pd
print('✓ All modules installed')
"
```

---

**Last Updated:** March 7, 2026
