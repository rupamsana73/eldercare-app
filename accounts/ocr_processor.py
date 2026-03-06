"""
Smart Prescription Detection System - OCR & Medicine Extraction
Handles image preprocessing, OCR, prescription validation, and fuzzy medicine matching.
"""

import os
import re
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

# ===== PRESCRIPTION VALIDATION KEYWORDS =====
PRESCRIPTION_KEYWORDS = {
    'rx', 'tab', 'tablet', 'capsule', 'cap', 'cap.', 'mg', 'ml',
    'doctor', 'clinic', 'hospital', 'prescription', 'sig',
    'dose', 'dosage', 'frequency', 'mane', 'nocte', 'bd', 'tds',
    'od', 'bid', 'tid', 'qid', 'four times', 'three times', 'twice',
    'once', 'daily', 'gm', 'units', 'mcg', 'strength',
    'ointment', 'drops', 'cream', 'syrup', 'suspension', 'inj', 'injection'
}

# ===== MEDICINE DATASET CACHE =====
_medicine_cache = None


def load_medicine_dataset(csv_path: str = None) -> List[str]:
    """
    Load medicine names from CSV dataset.
    Returns a list of medicine names (lowercase).
    Uses in-memory cache to avoid reloading.
    """
    global _medicine_cache
    
    if _medicine_cache is not None:
        return _medicine_cache
    
    try:
        # Default path: data folder in project root
        if csv_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            csv_path = base_dir / 'data' / 'A_Z_medicines_dataset_of_India.csv'
        
        if not os.path.exists(csv_path):
            logger.warning(f"Medicine dataset not found at {csv_path}")
            _medicine_cache = []
            return []
        
        import pandas as pd
        
        # Load CSV and extract medicine names
        df = pd.read_csv(csv_path)
        
        # Extract from 'name' column (primary source)
        if 'name' in df.columns:
            medicines = df['name'].dropna().unique().tolist()
        else:
            # Fallback: try other common column names
            possible_cols = ['drug_name', 'medicine_name', 'product_name']
            medicines = []
            for col in possible_cols:
                if col in df.columns:
                    medicines = df[col].dropna().unique().tolist()
                    break
        
        # Convert to lowercase for matching
        medicine_list = [str(m).strip().lower() for m in medicines if m]
        
        # Remove duplicates while preserving some order
        medicine_list = list(dict.fromkeys(medicine_list))
        
        logger.info(f"Loaded {len(medicine_list)} medicines from dataset")
        _medicine_cache = medicine_list
        return medicine_list
        
    except ImportError:
        logger.error("pandas not installed - cannot load medicine dataset")
        _medicine_cache = []
        return []
    except Exception as e:
        logger.error(f"Error loading medicine dataset: {e}")
        _medicine_cache = []
        return []


def preprocess_image(image_path: str) -> Optional[np.ndarray]:
    """
    Preprocess image using OpenCV for better OCR accuracy.
    Steps:
    1. Convert to grayscale
    2. Gaussian blur for noise reduction
    3. Adaptive threshold for better contrast
    4. Morphological operations for noise removal
    5. Contrast enhancement
    
    Returns: Preprocessed image as numpy array, or None if error
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Cannot read image: {image_path}")
            return None
        
        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Gaussian blur (reduce noise)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Step 3: Adaptive threshold for text detection
        # Works better for varying lighting conditions
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Step 4: Morphological operations (remove noise, fill gaps)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Step 5: Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(closed)
        
        logger.info("Image preprocessing completed successfully")
        return enhanced
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None


def validate_prescription(ocr_text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if extracted text looks like a medical prescription.
    Checks for presence of prescription-related keywords.
    
    Returns: (is_valid, error_message)
    """
    if not ocr_text or not isinstance(ocr_text, str):
        return False, "No text detected in image. Please upload a valid prescription."
    
    text_lower = ocr_text.lower().strip()
    
    if len(text_lower) < 10:
        return False, "Text is too short. Please upload a clearer prescription image."
    
    # Count keyword matches
    keyword_matches = 0
    for keyword in PRESCRIPTION_KEYWORDS:
        if keyword in text_lower:
            keyword_matches += 1
    
    # Need at least 2 prescription keywords to validate
    if keyword_matches < 2:
        return False, (
            "This doesn't look like a medical prescription. "
            "Please ensure the image clearly shows medicine names with dosages. "
            "Look for keywords like: Rx, Tab, Tablet, Capsule, mg, Doctor, etc."
        )
    
    return True, None


def extract_text_with_ocr(image_path: str, use_preprocessing: bool = True) -> Tuple[str, bool, Optional[str]]:
    """
    Extract text from image using pytesseract with preprocessing.
    
    Args:
        image_path: Path to the prescription image
        use_preprocessing: Whether to apply OpenCV preprocessing
    
    Returns: (extracted_text, ocr_success, error_message)
    """
    try:
        import pytesseract
        
        # Configure Tesseract path on Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        tesseract_found = False
        for tp in tesseract_paths:
            if os.path.isfile(tp):
                pytesseract.pytesseract.tesseract_cmd = tp
                tesseract_found = True
                break
        
        if not tesseract_found:
            logger.warning("Tesseract OCR not found on system")
            return "", False, "Tesseract OCR is not installed. Please install it to enable prescription scanning."
        
        # Preprocess image if enabled
        if use_preprocessing:
            preprocessed = preprocess_image(image_path)
            if preprocessed is not None:
                # Save preprocessed image to temporary file
                temp_path = image_path.replace('.', '_processed.')
                cv2.imwrite(temp_path, preprocessed)
                ocr_image_path = temp_path
            else:
                ocr_image_path = image_path
        else:
            ocr_image_path = image_path
        
        # Open image
        img = Image.open(ocr_image_path)
        
        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(img, lang='eng')
        
        # Clean up temporary file if created
        if use_preprocessing and ocr_image_path != image_path:
            try:
                os.remove(ocr_image_path)
            except:
                pass
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            return "", False, "No text detected in the image. Please upload a clearer prescription."
        
        # Limit text length
        extracted_text = extracted_text.strip()[:5000]
        
        return extracted_text, True, None
        
    except ImportError:
        return "", False, "pytesseract is not installed. Please install required OCR packages."
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return "", False, f"OCR processing failed: {str(e)[:100]}"


def extract_medicine_candidates(text: str) -> List[str]:
    """
    Extract candidate medicine names from OCR text.
    Uses pattern matching and heuristics.
    
    Returns: List of candidate medicine names
    """
    if not text or not isinstance(text, str):
        return []
    
    text = text[:50000]  # Limit processing size
    
    noise_words = {
        'the', 'and', 'for', 'with', 'take', 'after', 'before',
        'food', 'daily', 'once', 'twice', 'morning', 'evening',
        'night', 'days', 'weeks', 'patient', 'name', 'date',
        'doctor', 'hospital', 'prescription', 'pharmacy', 'address',
        'phone', 'age', 'sex', 'male', 'female', 'diagnosis',
        'time', 'hour', 'day', 'week', 'month', 'year', 'dr',
        'rx', 'sig', 'prn', 'bid', 'tid', 'qid', 'hs', 'od',
        'clinic', 'signature', 'patient', 'reg', 'nr', 'b', 'no'
    }
    
    try:
        # Extract words
        words = re.findall(r'[A-Za-z][A-Za-z0-9\-]{2,}', text)
        if not words:
            return []
        
        candidates = set()
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Skip noise words
            if word_lower in noise_words:
                continue
            
            # If preceded by prescription keywords, likely a medicine
            if i > 0 and words[i - 1].lower() in PRESCRIPTION_KEYWORDS:
                candidates.add(word)
                continue
            
            # Capitalized words of sufficient length
            if word[0].isupper() and len(word) >= 4:
                candidates.add(word)
                continue
            
            # Words followed by dosage numbers
            if i + 1 < len(words):
                next_word = words[i + 1]
                if re.match(r'^\d+', next_word):  # Followed by number (dosage)
                    candidates.add(word)
                    continue
        
        # Return sorted list, limit to top 100
        result = sorted(list(candidates))[:100]
        logger.info(f"Extracted {len(result)} medicine candidates")
        return result
        
    except Exception as e:
        logger.error(f"Error extracting medicine candidates: {e}")
        return []


def fuzzy_match_medicines(
    detected_names: List[str],
    medicine_dataset: List[str] = None,
    user_medicines: List[str] = None,
    threshold: int = 85
) -> List[Dict]:
    """
    Fuzzy match detected medicine names with dataset and user medicines.
    Uses rapidfuzz for better matching accuracy.
    
    Args:
        detected_names: List of medicine names from OCR
        medicine_dataset: List of medicines from CSV (if None, loads from file)
        user_medicines: List of user's existing medicines
        threshold: Similarity threshold (0-100)
    
    Returns: List of match results with confidence scores
    """
    if not detected_names:
        return []
    
    # Load dataset if not provided
    if medicine_dataset is None:
        medicine_dataset = load_medicine_dataset()
    
    # Combine sources for matching
    all_medicines = set(medicine_dataset or [])
    if user_medicines:
        all_medicines.update([m.lower() for m in user_medicines])
    
    if not all_medicines:
        logger.warning("No medicines available for matching")
        return [{"detected": d, "matched": None, "confidence": 0} for d in detected_names]
    
    results = []
    
    try:
        from rapidfuzz import fuzz
        
        for detected in detected_names:
            if not detected or not isinstance(detected, str):
                continue
            
            detected_lower = detected.lower().strip()
            best_match = None
            best_confidence = 0
            
            # Quick exact match check
            if detected_lower in all_medicines:
                best_match = detected
                best_confidence = 100
            else:
                # Fuzzy matching with rapidfuzz
                for medicine in list(all_medicines)[:1000]:  # Limit for performance
                    # Use token_sort_ratio for better matching with word order variations
                    confidence = fuzz.token_sort_ratio(detected_lower, medicine)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = medicine
            
            # Only include matches above threshold
            final_confidence = best_confidence if best_confidence >= threshold else 0
            
            results.append({
                "detected": detected,
                "matched": best_match if final_confidence > 0 else None,
                "confidence": final_confidence
            })
        
        logger.info(f"Fuzzy matched {len([r for r in results if r['matched']])} medicines")
        return results
        
    except ImportError:
        logger.warning("rapidfuzz not installed - using fallback matching")
        return _fallback_match(detected_names, all_medicines, threshold)
    except Exception as e:
        logger.error(f"Error in fuzzy matching: {e}")
        return [{"detected": d, "matched": None, "confidence": 0} for d in detected_names]


def _fallback_match(detected_names: List[str], medicines: set, threshold: int = 85) -> List[Dict]:
    """
    Fallback fuzzy matching using difflib when rapidfuzz is not available.
    """
    import difflib
    
    results = []
    for detected in detected_names:
        if not detected:
            continue
        
        detected_lower = detected.lower().strip()
        matches = difflib.get_close_matches(
            detected_lower, list(medicines), n=1, cutoff=threshold/100
        )
        
        if matches:
            confidence = int(
                difflib.SequenceMatcher(None, detected_lower, matches[0]).ratio() * 100
            )
            results.append({
                "detected": detected,
                "matched": matches[0],
                "confidence": confidence
            })
        else:
            results.append({
                "detected": detected,
                "matched": None,
                "confidence": 0
            })
    
    return results
