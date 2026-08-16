import re
from typing import Dict, Any, List, Tuple
from src.config import EMERGENCY_KEYWORDS, URGENT_KEYWORDS

# Department Names Translation Map (English -> Bangla)
BANGLA_DEPARTMENT_MAP = {
    "Cardiology": "কার্ডিওলজি (হৃদরোগ বিভাগ)",
    "Cardiology & Pulmonology": "কার্ডিওলজি ও পালমোনোলজি (হৃদরোগ ও বক্ষব্যাধি বিভাগ)",
    "Neurology": "নিউরোলজি (মস্তিষ্ক ও স্নায়ুরোগ বিভাগ)",
    "Orthopedics": "অর্থোপেডিকস (হাড়, জয়েন্ট ও ট্রমা বিভাগ)",
    "Gastroenterology": "গ্যাস্ট্রোএন্টারোলজি (পাকস্থলী ও পরিপাকতন্ত্র বিভাগ)",
    "Dermatology": "ডার্মাটোলজি (চর্ম ও যৌনরোগ বিভাগ)",
    "Pulmonology": "পালমোনোলজি (ফুসফুস ও বক্ষব্যাধি বিভাগ)",
    "ENT (Otolaryngology)": "ইএনটি (নাক, কান ও গলা বিভাগ)",
    "Urology": "ইউরোলজি (মূত্রতন্ত্র বিভাগ)",
    "Urology & Nephrology": "ইউরোলজি ও নেফ্রোলজি (কিডনি ও মূত্রনালী বিভাগ)",
    "Gynecology & Obstetrics": "গাইনিকোলজি ও অবসটেট্রিক্স (নারী ও প্রসূতি বিভাগ)",
    "Pediatrics": "পেডিয়াট্রিক্স (শিশু বিভাগ)",
    "Ophthalmology": "অপথালমোলজি (চক্ষু বিভাগ)",
    "General Medicine": "জেনারেল মেডিসিন (সাধারণ চিকিৎসা ও ইন্টারনাল মেডিসিন)",
    "Hematology & Oncology": "হেমাটোলজি ও অনকোলজি (রক্ত ও ক্যান্সার বিভাগ)",
    "Psychiatry & Behavioral Health": "সাইকিয়াট্রি (মানসিক স্বাস্থ্য বিভাগ)"
}

# Specialist Title in Bangla
BANGLA_SPECIALIST_MAP = {
    "Cardiology": "কার্ডিওলজিস্ট (হৃদরোগ বিশেষজ্ঞ)",
    "Cardiology & Pulmonology": "কার্ডিওলজিস্ট / পালমোনোলজিস্ট (হৃদরোগ ও বক্ষব্যাধি বিশেষজ্ঞ)",
    "Neurology": "নিউরোলজিস্ট (মস্তিষ্ক ও স্নায়ুরোগ বিশেষজ্ঞ)",
    "Orthopedics": "অর্থোপেডিক সার্জন (হাড় ও জয়েন্ট বিশেষজ্ঞ)",
    "Gastroenterology": "গ্যাস্ট্রোএন্টারোলজিস্ট (পরিপাকতন্ত্র বিশেষজ্ঞ)",
    "Dermatology": "ডার্মাটোলজিস্ট (চর্মরোগ বিশেষজ্ঞ)",
    "Pulmonology": "পালমোনোলজিস্ট (বক্ষব্যাধি বিশেষজ্ঞ)",
    "ENT (Otolaryngology)": "ইএনটি স্পেশালিস্ট (নাক-কান-গলা বিশেষজ্ঞ)",
    "Urology": "ইউরোলজিস্ট (কিডনি ও মূত্রনালী বিশেষজ্ঞ)",
    "Urology & Nephrology": "ইউরোলজিস্ট / নেফ্রোলজিস্ট (কিডনি ও মূত্র বিশেষজ্ঞ)",
    "Gynecology & Obstetrics": "গাইনিকোলজিস্ট (স্ত্রী ও প্রসূতি বিশেষজ্ঞ)",
    "Pediatrics": "পেডিয়াট্রিশিয়ান (শিশু বিশেষজ্ঞ)",
    "Ophthalmology": "অপথালমোলজিস্ট (চক্ষু বিশেষজ্ঞ)",
    "General Medicine": "জেনারেল ফিজিশিয়ান / মেডিসিন বিশেষজ্ঞ",
    "Hematology & Oncology": "হেমাটোলজিস্ট ও অনকোলজিস্ট (ক্যান্সার বিশেষজ্ঞ)",
    "Psychiatry & Behavioral Health": "সাইকিয়াট্রিস্ট (মানসিক রোগ বিশেষজ্ঞ)"
}

# Direct Pure Bangla Medical Keywords Map (for instant & offline translation)
BANGLA_MEDICAL_LEXICON = [
    # General Medicine & Fever
    (r'(?:১০[০-৬](?:\.[০-৯]+)?\s*(?:ডিগ্রি)?|১০৪|১০৩|১০২|১০১|১০০|তীব্র\s*জ্বর|গা\s*গরম|শরীরে\s*জ্বর|জ্বর\s*জ্বর|কাঁপানি|দুর্বলতা|ক্লান্তি|শরীর\s*খারাপ)', 'high fever hyperpyrexia high body temperature severe malaise fatigue weakness'),
    (r'(?:জ্বর|গায়ে\s*ব্যথা|গা\s*ব্যথা|শরীর\s*ব্যথা|দুর্বল\s*লাগে)', 'fever generalized body ache muscle pain malaise'),

    # Cardiology (Heart & Chest)
    (r'(?:বুকে\s*ব্যথা|বুকে\s*চাপ|বুক\s*ধড়ফড়|হৃদরোগ|হার্ট\s*অ্যাটাক|বামে\s*ব্যথা|বুকে\s*জ্বালাপোড়া)', 'acute chest pain cardiac angina heart palpitation myocardial infarction'),

    # Neurology (Brain & Spine)
    (r'(?:মাথা\s*ব্যথা|মাইগ্রেন|মাথা\s*ঘোরা|মাথা\s*ঘুরায়|হাত\s*পা\s*অবশ|জ্ঞান\s*হারানো|প্যারালাইসিস|মস্তিষ্কে|খিঁচুনি)', 'severe headache migraine vertigo dizziness neurological numbness paralysis syncope seizure'),

    # Gastroenterology (Stomach & Digestion)
    (r'(?:পেটে\s*ব্যথা|পেট\s*ব্যথা|বমি\s*বমি|বমি\s*হচ্ছে|পাতলা\s*পায়খানা|ডায়েরিয়া|গ্যাসের\s*সমস্যা|বদহজম|পেট\s*ফাঁপা|অম্লতা)', 'acute abdominal pain stomach ache nausea vomiting watery diarrhea gastritis acid reflux'),

    # Orthopedics (Bones & Joints)
    (r'(?:হাড়\s*ভাঙা|কোমর\s*ব্যথা|মাজা\s*ব্যথা|হাঁটু\s*ব্যথা|জয়েন্টে\s*ব্যথা|হাতে\s*ব্যথা|পায়ে\s*ব্যথা|মচকে\s*গেছে|বাত\s*ব্যথা)', 'bone fracture dislocation severe lumbar back pain knee joint pain arthritis trauma sprain'),

    # Dermatology (Skin & Allergy)
    (r'(?:চুলকানি|চুলকায়|ফুসকুড়ি|এলার্জি|দাদ|একজিমা|মুখে\s*ব্রণ|চামড়া\s*লাল|চর্মরোগ)', 'severe skin itching rash allergy pruritus eczema facial acne dermatitis cutaneous lesion'),

    # ENT (Ear, Nose, Throat)
    (r'(?:গলা\s*ব্যথা|গলায়\s*ব্যথা|টনসিল|নাক\s*বন্ধ|নাক\s*দিয়ে\s*পানি|কানে\s*ব্যথা|কানে\s*শুনতে\s*সমস্যা|সর্দি|কাশি)', 'sore throat pharyngitis tonsillitis nasal congestion ear pain earache acute cough cold'),

    # Respiratory & Pulmonology
    (r'(?:শ্বাসকষ্ট|শ্বাস\s*নিতে\s*কষ্ট|হাঁপানি|বুকের\s*ভেতর\s*শব্দ|দম\s*বন্ধ|কাশি\s*কাশি|কফ)', 'shortness of breath dyspnea acute asthma respiratory distress wheezing severe cough sputum'),

    # Urology & Nephrology
    (r'(?:প্রস্রাবে\s*জ্বালাপোড়া|প্রস্রাবে\s*রক্ত|কিডনিতে\s*ব্যথা|ঘন\s*ঘন\s*প্রস্রাব|মূত্রনালীর\s*সমস্যা)', 'painful burning urination dysuria UTI infection hematuria renal flank kidney pain'),

    # Ophthalmology (Eyes)
    (r'(?:চোখ\s*লাল|চোখে\s*ব্যথা|চোখে\s*ঝাপসা|চোখ\s*দিয়ে\s*পানি|দৃষ্টি\s*কমে\s*গেছে|চোখ\s*চুলকায়)', 'eye redness conjunctivitis eye pain blurred vision impaired visual acuity watering'),

    # Gynecology (Women's Health)
    (r'(?:মাসিকের\s*ব্যথা|অনিয়মিত\s*পিরিয়ড|গর্ভবতী|গর্ভকালীন|তলপেটে\s*ব্যথা|প্রসূতি)', 'dysmenorrhea irregular menstruation pelvic pain pregnancy obstetric prenatal consultation'),

    # Pediatrics (Children)
    (r'(?:বাচ্চার\s*বয়স|বাচ্চার\s*জ্বর|শিশুর\s*জ্বর|বাচ্চা\s*অসুস্থ|নবজাতক|ছোট\s*বাচ্চার|বাচ্চা|শিশু|শিশুর|বাচ্চার)', 'pediatric child specialist illness infant newborn crying distress neonatology'),

    # Psychiatry (Mental Health)
    (r'(?:বিষণ্ণতা|অস্থিরতা|ঘুম\s*হয়\s*না|প্যানিক|মানসিক\s*চাপ|ভয়\s*লাগে|ডিপ্রেশন)', 'depression severe anxiety insomnia panic disorder psychiatric behavioral disturbance')
]

# Common Banglish medical terms to English phrases
BANGLISH_MEDICAL_PATTERNS = [
    # Fever & General Illness
    (r'\b(?:10[0-6](?:\.[0-9]+)?(?:\s*(?:degree|deg|f|°f))?|high\s*temparature|high\s*temperature|ga\s*gorom|sorir(?:e)?\s*gorom|shorir(?:e)?\s*gorom)\b', 'high fever hyperpyrexia high body temperature'),
    (r'\b(?:sorir(?:e)?|shorir(?:e)?|ga)\s*(?:onk\s*|khub\s*)?(?:kharap|bhalo\s*na|durbol|jhimsano|ashanti)\b', 'general malaise severe fatigue weakness body ache'),
    (r'\b(?:onk\s*|khub\s*)?kharap\s*lag(?:tese|che|e)\b', 'feeling very sick malaise severe discomfort'),
    (r'\b(?:durbol|durbolota|weak|weakness|clanto|shorire\s*shokti\s*nai)\b', 'fatigue generalized body weakness malaise'),
    (r'\b(?:jor|jhor|fever)\b', 'fever high body temperature chills'),
    (r'\b(?:sorir(?:e)?|shorir(?:e)?|ga(?:ye)?)\s*(?:onk\s*|khub\s*)?beth?a\b', 'generalized body ache muscle pain fatigue'),

    # Cardiac & Chest (High Priority)
    (r'\b(?:buk(?:e)?\s*(?:onk\s*|khub\s*|prochur\s*)?beth?a.*(?:bam\s*hat|hath|obosh)|(?:bam\s*hat|hath|obosh).*(?:buk(?:e)?\s*beth?a))\b', 'acute myocardial infarction ischemic heart attack severe crushing chest pain radiating to left arm cardiac arrest'),
    (r'\bbuk(?:e)?\s*(?:onk\s*|khub\s*|prochur\s*)?beth?a\b', 'acute severe chest pain cardiac angina ischemic heart disease'),
    (r'\bbuk\s*(?:dhorfash|dhorfor|dhukdhuk|kapche)\b', 'heart palpitation tachycardia arrhythmia cardiac flutter'),
    (r'\bbuk(?:e)?\s*(?:jala|porapora|chap|bhaari)\b', 'heartburn chest burning acid reflux angina chest pressure'),
    (r'\b(?:heart\s*er\s*problem|heart\s*attack)\b', 'myocardial infarction coronary artery disease heart failure'),

    # Respiratory & Lungs
    (r'\b(?:sh?ash?|shas)\s*(?:nite\s*)?(?:kosh?to|problem)\b', 'shortness of breath dyspnea respiratory distress'),
    (r'\b(?:haph?ani|dam\s*atke|dam\s*bondho|shash\s*atke)\b', 'asthma acute wheezing respiratory difficulty'),
    (r'\b(?:kash?i|kash|cough|koph)\b', 'severe cough sputum respiratory chest congestion'),
    (r'\b(?:sordi|th?anda|shordi|hachi)\b', 'cold viral flu coryza chills sneezing'),

    # Brain & Neurology
    (r'\bmath?a\s*(?:onk\s*|khub\s*)?beth?a\b', 'severe headache migraine neurological pain'),
    (r'\bmath?a\s*(?:ghur(?:e|acche|ano|tese)|jhim\s*jhim)\b', 'dizziness vertigo cerebral syncope'),
    (r'\b(?:hat\s*pa\s*obosh?|obosh\s*lagtese|paralysis|khichuni)\b', 'limb numbness paralysis neurological deficit seizure'),
    (r'\b(?:mritsubhab|behus|ogyan|senseless)\b', 'syncope loss of consciousness seizure'),

    # Stomach & Gastroenterology
    (r'\bpet(?:e)?\s*(?:onk\s*|khub\s*)?beth?a\b', 'acute abdominal pain severe stomach ache gastritis'),
    (r'\bpet(?:e)?\s*(?:jala|gas|fapa|faapa|bad\s*hazom)\b', 'acid reflux gastritis dyspepsia stomach burning indigestion'),
    (r'\b(?:bomi|bomy)\s*(?:hocche|bhab|lagtese|kortese)\b', 'severe vomiting nausea gastrointestinal distress'),
    (r'\b(?:patla\s*paikhana|diarrhea|daireya|loose\s*motion)\b', 'acute watery diarrhea dehydration gastroenteritis'),

    # Bones, Joints & Orthopedics
    (r'\b(?:hater|payer|hate|paye)\s*beth?a\b', 'limb extremity joint bone pain'),
    (r'\b(?:komor|komore|majha|murdho)\s*(?:onk\s*|khub\s*)?beth?a\b', 'severe low back pain lumbar spine ache'),
    (r'\b(?:hat|pa|angul|haar)\s*(?:bhenge|fracture|morske|bhanga)\b', 'bone fracture dislocation joint trauma sprain'),
    (r'\b(?:hathu|haatu|joint|gite\s*gite)\s*beth?a\b', 'knee joint pain arthritis swelling inflammation'),

    # Dermatology & Skin
    (r'\b(?:chulkani|chulkacche|rash|khosh\s*pachra|khujli)\b', 'severe skin itching rash pruritus dermatitis'),
    (r'\b(?:chamra|torko)\s*(?:lal|chulkani|ghao|fushkuri)\b', 'skin redness eczema allergy erythema cutaneous lesion'),
    (r'\b(?:mukhe|mukher)\s*(?:bron|acne|daag)\b', 'facial acne pimples vulgaris dermatological lesion'),

    # ENT (Ear, Nose, Throat)
    (r'\b(?:gola|golay)\s*beth?a\b', 'sore throat pharyngitis tonsillitis pain'),
    (r'\b(?:kan|kane)\s*beth?a\b', 'severe ear pain earache otitis media'),
    (r'\b(?:nak\s*diye\s*rokto|nak\s*bondho|nak\s*diye\s*pani)\b', 'epistaxis nasal congestion sinus obstruction rhinorrhea'),

    # Urology & Nephrology
    (r'\b(?:pros?r[ao]b(?:e)?|mutro|peshab)\s*(?:jala|porapora|porashona|betha|prochur|kom|beshi|atke|problem)?\b', 'painful burning urination dysuria UTI infection hematuria renal kidney stone'),
    (r'\b(?:pros?r[ao]b(?:e)?\s*rokto|rokto\s*pros?r[ao]b)\b', 'hematuria blood in urine kidney stone'),
    (r'\b(?:kidney|kidnite|kole)\s*beth?a\b', 'renal flank pain nephrolithiasis kidney ache'),

    # Ophthalmology (Eyes)
    (r'\b(?:chokh|chokhe)\s*(?:lal|pani|chulkani|betha)\b', 'eye redness conjunctivitis eye pain watering irritation'),
    (r'\b(?:chokhe\s*jhapsa|dekhte\s*somossya|dekhte\s*paina)\b', 'blurred vision impaired visual acuity ophthalmology'),

    # Gynecology & Pregnancy
    (r'\b(?:masik|period|menstrual)\s*(?:er\s*)?(?:betha|oniyomito|somossya)\b', 'dysmenorrhea irregular menstruation pelvic pain'),
    (r'\b(?:garbhoboti|pregnant|pregnancy|baccha\s*hobe)\b', 'pregnancy obstetric prenatal consultation'),

    # Pediatrics (Children - High Priority)
    (r'\b(?:bach?a|bach?ar|shishu|babu|baacha|chotoder|choto\s*baccha|shishuder)\b', 'pediatric child illness pediatric neonatology infant distress consultation'),
    (r'\b(?:bach?a|bach?ar|shishu|babu|baacha)\s*(?:onk\s*|khub\s*)?(?:jor|betha|kanna|oshustho)\b', 'pediatric child illness infant high fever crying'),

    # Psychiatry (Mental Health)
    (r'\b(?:mon\s*kharap|depression|tension|chinta|ghum\s*hoy\s*na|bhoi\s*lage|panic)\b', 'depression severe anxiety insomnia panic disorder psychiatric behavioral disturbance')
]

# Banglish stopwords & filler remover to purify clinical signal
BANGLISH_FILLERS = [
    r'\b(?:amar|amr|amader|apnar|amar\s*mone\s*hocche|bhai|vai|doctor|sir|please|kisu|onk|khub|onek|ektu|beshi|hothat|prochur)\b',
    r'\b(?:lagtese|lagche|hocche|hoise|kore|korsi|kortese|ache|ase|hoy|hoye|jani|bujhte|somossya|problem)\b'
]

def is_bangla_text(text: str) -> bool:
    """Checks if the string contains Bengali Unicode characters."""
    return bool(re.search(r'[\u0980-\u09FF]', text))

def normalize_bangla_lexicon(text: str) -> str:
    """Translates pure Bangla medical concepts into rich clinical English concepts."""
    processed = text
    for pattern, replacement in BANGLA_MEDICAL_LEXICON:
        processed = re.sub(pattern, replacement, processed)
    return processed

def normalize_banglish(text: str) -> str:
    """Translates common Banglish medical expressions to English keywords."""
    processed = text.lower()
    for pattern, replacement in BANGLISH_MEDICAL_PATTERNS:
        processed = re.sub(pattern, replacement, processed)
    # Strip unnecessary fillers
    for filler in BANGLISH_FILLERS:
        processed = re.sub(filler, ' ', processed)
    return ' '.join(processed.split())

def translate_to_english_if_needed(text: str) -> Tuple[str, str]:
    """
    Detects language (Pure Bangla, Banglish, or English).
    Translates into standard clinical English text for the BERT model.
    Returns (english_text, original_language).
    """
    if not text or not text.strip():
        return "", "en"
        
    text_clean = text.strip()
    
    # 1. Pure Bangla Detection
    if is_bangla_text(text_clean):
        # First translate with offline medical lexicon
        lexicon_translated = normalize_bangla_lexicon(text_clean)
        try:
            from deep_translator import GoogleTranslator
            google_trans = GoogleTranslator(source='bn', target='en').translate(text_clean)
            combined = f"{google_trans}. {lexicon_translated}"
            return combined, "bn"
        except Exception:
            return lexicon_translated, "bn"
            
    # 2. Banglish Detection & Normalization
    normalized_banglish = normalize_banglish(text_clean)
    if normalized_banglish != text_clean.lower():
        return normalized_banglish, "banglish"
        
    return text_clean, "en"

def clean_text(text: str) -> str:
    """Cleans input text by removing extra spaces and special characters."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^\w\s\.,\?-]', '', text)
    return ' '.join(text.split())

def evaluate_triage_urgency(complaint_text: str, lang: str = "en") -> Dict[str, Any]:
    """
    Evaluates clinical urgency/triage level based on red-flag keywords.
    Returns urgency level, color code, action advice in English and Bangla.
    """
    text_lower = complaint_text.lower()
    
    matched_emergency = [kw for kw in EMERGENCY_KEYWORDS if kw in text_lower]
    if matched_emergency:
        return {
            "level": "Emergency (Level 1)",
            "level_bn": "জরুরি / ইমার্জেন্সি (লেভেল ১)",
            "priority": 1,
            "badge_color": "#FF4B4B",
            "action": "Immediate ICU / Emergency Room attention required!",
            "action_bn": "অবিলম্বে ইমার্জেন্সি বা আইসিইউ বিভাগে যোগাযোগ করুন!",
            "triggers": matched_emergency
        }
        
    matched_urgent = [kw for kw in URGENT_KEYWORDS if kw in text_lower]
    if matched_urgent:
        return {
            "level": "Urgent (Level 2)",
            "level_bn": "অতি জরুরি (লেভেল ২)",
            "priority": 2,
            "badge_color": "#FFA500",
            "action": "Priority consultation within 2-4 hours recommended.",
            "action_bn": "২-৪ ঘণ্টার মধ্যে ডাক্তারের পরামর্শ নেওয়ার অনুরোধ করা হলো।",
            "triggers": matched_urgent
        }
        
    return {
        "level": "Routine (Level 3)",
        "level_bn": "সাধারণ / রুটিন চেকআপ (লেভেল ৩)",
        "priority": 3,
        "badge_color": "#28A745",
        "action": "Standard Outpatient Department (OPD) appointment.",
        "action_bn": "নিয়মিত আউটডোর (OPD) টিকিট কেটে ডাক্তার দেখান।",
        "triggers": []
    }
