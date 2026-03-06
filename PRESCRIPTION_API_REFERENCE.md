# 🔌 Smart Prescription System - API Reference

## Overview

The Smart Prescription Detection System exposes three main API endpoints:
1. **GET** `/prescription-reader/` - Display prescription reader page
2. **POST** `/prescription-reader/process/` - Process prescription image
3. **POST** `/prescription-reader/add-medicines/` - Add medicines to user list

---

## 1. Prescription Reader Page

### Endpoint
```
GET /prescription-reader/
```

### Description
Displays the prescription reader interface with upload form and recent prescriptions.

### Authentication
- ✓ Required: `@login_required`
- User must be authenticated

### Response
**Content-Type:** `text/html`

**Template:** `prescription_reader_smart.html`

**Context Variables:**
```python
{
    'form': PrescriptionUploadForm(),
    'recent_prescriptions': Prescription objects,  # Last 5
}
```

### Example
```bash
curl -X GET http://localhost:8000/prescription-reader/
```

### Response Codes
- `200 OK` - Page loaded successfully
- `302 REDIRECT` - Not authenticated, redirects to login
- `500 INTERNAL SERVER ERROR` - Server error (logs recorded)

---

## 2. Process Prescription Image

### Endpoint
```
POST /prescription-reader/process/
```

### Description
Uploads a prescription image, performs OCR with preprocessing, detects medicines, and matches them against the medicine database with fuzzy matching.

### Authentication
- ✓ Required: `@login_required`
- ✓ Rate Limited: Max 10 scans per day per user

### Request

**Content-Type:** `multipart/form-data`

**Parameters:**
```
image (file, required)
  - Type: JPEG, PNG, JPG
  - Max Size: 10 MB
  - Description: Prescription image file
```

### Processing Steps
1. **File Validation**
   - Check MIME type
   - Verify file size
   - Verify magic bytes (PDF header)

2. **Create Database Record**
   - Prescription object created
   - Associated with current user
   - Image stored to `media/prescriptions/`

3. **Image Preprocessing (OpenCV)**
   - Grayscale conversion
   - Gaussian blur (5x5)
   - Adaptive threshold
   - Morphological operations
   - CLAHE enhancement

4. **OCR Extraction (Pytesseract)**
   - Auto-detect Tesseract path
   - Extract text from preprocessed image
   - Limit to 5000 characters
   - Save extracted text to database

5. **Prescription Validation**
   - Check for 50+ prescription keywords
   - Require minimum 2 keyword matches
   - Reject invalid images with user message

6. **Medicine Extraction**
   - Pattern-based extraction
   - Identify words after prescription keywords
   - Filter noise words
   - Return up to 100 candidates

7. **Fuzzy Matching**
   - Load medicine dataset from CSV
   - Compare with rapidfuzz.fuzz.token_sort_ratio()
   - Threshold: 85% similarity
   - Include user's existing medicines
   - Return confidence scores

### Response

**Content-Type:** `application/json`

**Success Response (200 OK):**
```json
{
  "success": true,
  "prescription_id": 123,
  "image_url": "/media/prescriptions/image_abc123.png",
  "extracted_text": "Rx\nTab Paracetamol 500mg...",
  "ocr_available": true,
  "detected_medicines": [
    "Paracetamol",
    "Azithromycin", 
    "Metformin"
  ],
  "matches": [
    {
      "detected": "Paracetamol",
      "matched": "paracetamol",
      "confidence": 95
    },
    {
      "detected": "Azithromycin",
      "matched": "azithromycin",
      "confidence": 98
    },
    {
      "detected": "Metformin",
      "matched": "metformin",
      "confidence": 92
    },
    {
      "detected": "XYZ",
      "matched": null,
      "confidence": 0
    }
  ],
  "message": "✓ Detected 3 medicine(s) from prescription"
}
```

**Error Response (400 BAD REQUEST):**
```json
{
  "success": false,
  "error": "This doesn't look like a medical prescription. Please ensure...",
  "prescription_id": 123,
  "image_url": "/media/prescriptions/..."
}
```

**Validation Error (400 BAD REQUEST):**
```json
{
  "success": false,
  "error": "Invalid form: File size must be under 10 MB."
}
```

**Rate Limit Error (429 TOO MANY REQUESTS):**
```json
{
  "success": false,
  "error": "Rate limit exceeded. Max 10 scans per day.",
  "retry_after": 3600
}
```

**Server Error (500 INTERNAL SERVER ERROR):**
```json
{
  "success": false,
  "error": "An unexpected error occurred. Please try again."
}
```

### Example Request

**Using curl:**
```bash
curl -X POST http://localhost:8000/prescription-reader/process/ \
  -H "X-CSRFToken: your_csrf_token" \
  -F "image=@prescription.jpg"
```

**Using JavaScript/Fetch:**
```javascript
const formData = new FormData();
formData.append('image', fileInputElement.files[0]);

fetch('/prescription-reader/process/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': document.getElementById('csrf-token').value
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Detected medicines:', data.detected_medicines);
    console.log('Matches:', data.matches);
  } else {
    console.error('Error:', data.error);
  }
});
```

**Using Python/Requests:**
```python
import requests

with open('prescription.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        'http://localhost:8000/prescription-reader/process/',
        files=files,
        headers={'X-CSRFToken': csrf_token}
    )
    
result = response.json()
print(result)
```

### Response Codes
- `200 OK` - Successfully processed
- `400 BAD REQUEST` - Invalid file or prescription
- `429 TOO MANY REQUESTS` - Rate limit exceeded
- `500 INTERNAL SERVER ERROR` - Server error

### Time Complexity
- File upload: O(1) ~< 1s
- Image preprocessing: O(n × m) where n,m = image dimensions ~2-5s
- OCR extraction: O(text_length) ~5-20s (depends on Tesseract)
- Fuzzy matching: O(detected × dataset) with optimization ~< 1s
- **Total:** 10-30 seconds

---

## 3. Add Medicines to List

### Endpoint
```
POST /prescription-reader/add-medicines/
```

### Description
Creates Medicine records for selected medicines with schedule details, integrating them into the user's medicine management system.

### Authentication
- ✓ Required: `@login_required`

### Request

**Content-Type:** `application/json`

**Body Schema:**
```json
{
  "medicines": [
    {
      "name": "Paracetamol",
      "dose_per_day": 2,
      "frequency_type": "daily",
      "food_timing": "After Food",
      "duration_days": 7,
      "times_per_day": "8:00,20:00",
      "notes": "For fever"
    },
    {
      "name": "Azithromycin",
      "dose_per_day": 1,
      "frequency_type": "daily",
      "food_timing": "Before Food",
      "duration_days": 5,
      "times_per_day": "8:00",
      "notes": ""
    }
  ]
}
```

**Field Definitions:**

| Field | Type | Required | Values | Default | Description |
|-------|------|----------|--------|---------|-------------|
| `name` | string | Yes | Any | - | Medicine name (sanitized) |
| `dose_per_day` | integer | No | 1-10 | 1 | Doses per day |
| `frequency_type` | string | No | daily, weekly, custom_week | daily | Frequency pattern |
| `food_timing` | string | No | Before Food, After Food | After Food | Meal timing |
| `duration_days` | integer | No | 1-365 | null | Course duration |
| `times_per_day` | string | No | HH:MM format | Auto | Scheduled times (comma-separated) |
| `notes` | string | No | Any | empty | Additional notes |

### Processing Steps

1. **Validation**
   - Check medicine list not empty
   - Max 50 medicines per request
   - Parse JSON correctly

2. **Duplicate Prevention**
   - Check against user's existing medicines
   - Case-insensitive comparison
   - Skip duplicates with feedback

3. **Medicine Creation** (Atomic Transaction)
   - Create Medicine record
   - Auto-classify drug type
   - Set status to 'active'
   - Enable reminders

4. **Schedule Creation**
   - Parse times_per_day field
   - Fallback to defaults if invalid:
     - 1 dose: 08:00
     - 2 doses: 08:00, 20:00
     - 3 doses: 08:00, 14:00, 20:00
     - 4+ doses: 08:00, 12:00, 16:00, 20:00
   - Create MedicineTime entries

5. **Status Tracking**
   - Create MedicineStatus for today
   - Initialize as untaken
   - Integrate with adherence tracking

### Response

**Content-Type:** `application/json`

**Success Response (200 OK):**
```json
{
  "success": true,
  "added_count": 2,
  "skipped_count": 0,
  "skipped_names": [],
  "message": "✓ Added 2 medicine(s) to your list."
}
```

**With Skipped Medicines:**
```json
{
  "success": true,
  "added_count": 2,
  "skipped_count": 1,
  "skipped_names": ["Aspirin"],
  "message": "✓ Added 2 medicine(s) to your list. 1 medicine(s) were skipped (duplicates or invalid).",
  "errors": {
    "Aspirin": "Already exists"
  }
}
```

**Validation Error (400 BAD REQUEST):**
```json
{
  "success": false,
  "error": "No medicines provided"
}
```

**Server Error (500 INTERNAL SERVER ERROR):**
```json
{
  "success": false,
  "error": "An unexpected error occurred"
}
```

### Example Request

**Using JavaScript/Fetch:**
```javascript
const medicines = [
  {
    name: 'Paracetamol',
    dose_per_day: 2,
    frequency_type: 'daily',
    food_timing: 'After Food',
    times_per_day: '8:00,20:00'
  },
  {
    name: 'Azithromycin',
    dose_per_day: 1,
    frequency_type: 'daily',
    food_timing: 'Before Food',
    times_per_day: '8:00'
  }
];

fetch('/prescription-reader/add-medicines/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': document.getElementById('csrf-token').value
  },
  body: JSON.stringify({ medicines: medicines })
})
.then(response => response.json())
.then(data => {
  console.log(`Added ${data.added_count} medicines`);
  if (data.skipped_count > 0) {
    console.log('Skipped:', data.skipped_names);
  }
});
```

**Using Python/Requests:**
```python
import requests
import json

medicines = [
    {
        'name': 'Paracetamol',
        'dose_per_day': 2,
        'times_per_day': '8:00,20:00'
    }
]

response = requests.post(
    'http://localhost:8000/prescription-reader/add-medicines/',
    json={'medicines': medicines},
    headers={'X-CSRFToken': csrf_token}
)

result = response.json()
print(f"Added: {result['added_count']}")
```

### Response Codes
- `200 OK` - Successfully added medicines
- `400 BAD REQUEST` - Validation error
- `500 INTERNAL SERVER ERROR` - Server error

### Time Complexity
- Database writes: O(n) where n = number of medicines ~< 1s
- Duplicate checking: O(n × m) where m = user's medicines ~< 100ms
- **Total:** < 1 second (typically)

---

## Error Handling

### Common Errors & Solutions

| Error | Code | Cause | Solution |
|-------|------|-------|----------|
| File size exceeds limit | 400 | Image > 10MB | Compress image or use smaller file |
| Invalid image format | 400 | Not JPG/PNG | Convert to JPG or PNG format |
| This doesn't look like a prescription | 400 | No prescription keywords | Upload actual prescription or clearer image |
| OCR module not available | 400 | Tesseract not installed | Install Tesseract OCR |
| Rate limit exceeded | 429 | >10 scans per day | Try again tomorrow |
| Database integrity error | 500 | Race condition | Retry request (rare) |
| Unexpected error | 500 | Unknown error | Check logs, contact support |

### Error Logging

All errors are logged with:
- Timestamp
- User ID
- Error type
- Stack trace
- Request details

Access logs at: `logs/` directory or Django admin

---

## Performance Optimization

### Caching
- **Medicine Dataset:** Cached in memory after first load
- **User Medicines:** Queried once per request
- **Drug Classifications:** Pre-computed and stored

### Query Optimization
- Single query for user medicines: `select_related`, `values_list`
- Batch processing for multiple medicines
- Atomic transactions for data consistency

### Benchmark Results
```
Operation              Time      Notes
─────────────────────────────────────────
File Upload           < 1 sec   Depends on file size
Image Preprocessing   2-5 sec   OpenCV processing
OCR Extraction       10-20 sec  Tesseract (main bottleneck)
Fuzzy Matching       < 500ms   Against 10k+ medicines
API Response         2-30 sec   Total (mostly OCR)
Medicine Add         < 100ms    Database write
```

---

## Security

### CSRF Protection
- ✓ All POST requests require `X-CSRFToken` header
- ✓ Token available in `{% csrf_token %}` template tag

### Rate Limiting
- ✓ 10 scans per user per day
- ✓ Returns 429 status with `Retry-After` header

### Input Validation
- ✓ File type check (MIME)
- ✓ File size check (10MB max)
- ✓ Magic byte verification
- ✓ Medicine name sanitization
- ✓ SQL injection prevention via ORM

### Authentication
- ✓ All endpoints require `@login_required`
- ✓ User isolation (can only access own medicines)

---

## Integration Examples

### Example 1: Complete Prescription Processing Flow

```javascript
// 1. Upload prescription
async function uploadAndProcess() {
  const file = document.getElementById('prescriptionFile').files[0];
  const formData = new FormData();
  formData.append('image', file);
  
  const processResp = await fetch('/prescription-reader/process/', {
    method: 'POST',
    body: formData,
    headers: {'X-CSRFToken': getCsrfToken()}
  });
  
  const processed = await processResp.json();
  
  if (!processed.success) {
    alert('Error: ' + processed.error);
    return;
  }
  
  // 2. Display results to user
  displayResults(processed.matches);
  
  // 3. User selects medicines (in UI)
  const selected = getUserSelection();
  
  // 4. Add medicines to system
  const addResp = await fetch('/prescription-reader/add-medicines/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({medicines: selected})
  });
  
  const added = await addResp.json();
  
  if (added.success) {
    alert(`Added ${added.added_count} medicines!`);
    window.location.href = '/medicine/manage/';
  }
}
```

### Example 2: Backend Integration

```python
from accounts.ocr_processor import (
    load_medicine_dataset,
    extract_text_with_ocr,
    fuzzy_match_medicines
)

def analyze_prescription(image_path):
    # Extract text
    text, success, error = extract_text_with_ocr(image_path)
    if not success:
        return None, error
    
    # Load medicines
    dataset = load_medicine_dataset()
    
    # Match medicines
    matches = fuzzy_match_medicines(
        ['Medicine1', 'Medicine2'],
        medicine_dataset=dataset,
        threshold=85
    )
    
    return matches, None
```

---

## Webhooks (Future)

### Planned Webhooks
```
POST /webhooks/prescription
  - Triggered when prescription processed
  - Includes medicine matches
  - Allows external integration
```

---

## Rate Limits

### Current Limits
- 10 prescription scans per user per day
- Resets at midnight UTC
- No API key needed (authenticated users)

### Response Headers
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1646872800
Retry-After: 3600
```

---

## Versioning

### Current Version
- **v1.0** - Smart Prescription Detection System
- Released: March 7, 2026
- Status: Production Ready

### Future Versions
- v1.1 - Multi-language OCR support
- v1.2 - Medicine interaction checking
- v2.0 - AI-powered dose optimization

---

## Support

### Troubleshooting
- Check OCR logs if text extraction fails
- Verify Tesseract installation
- Check file permissions on media folder
- Monitor rate limit headers

### Contact
- Issues: Check logs or Django admin
- Feedback: Contribute to project
- Questions: Refer to SMART_PRESCRIPTION_SYSTEM.md

---

**Last Updated:** March 7, 2026
**API Version:** 1.0
