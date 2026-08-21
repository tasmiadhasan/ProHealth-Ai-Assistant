/**
 * ProHealth AI Assistant - Frontend Application Controller
 * Handles Bilingual Language Switching (Bangla/English), Hero Slider,
 * Async AI Triage, Voice Recognition, Doctor Directory & 100% Reliable PDF Referral Generation
 */

// Global State
let currentLang = "en"; // "bn" or "en"
let currentSlideIndex = 0;
let slideInterval = null;
let doctorsData = [];
let lastPredictionResult = null;
let recognition = null;
let isRecording = false;

// Google Authentication & User Dashboard State
const GOOGLE_CLIENT_ID = "458726147849-22uuib4q6n7ul0u321ed6833hu94vn3p.apps.googleusercontent.com";
let currentGoogleUser = null;
let pendingBookingAction = null;

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    switchLanguage("en");
    initHeroSlider();
    initVoiceRecognition();
    renderSampleChips();
    fetchDoctors("all");
    fetchFacilities();
    initDeptTabs();
    setDefaultAppointmentDate();
    initGoogleAuth();
});

/* =============================================================================
   OFFICIAL GOOGLE IDENTITY SERVICES (GIS) AUTHENTICATION CONTROLLER
   ============================================================================= */
function initGoogleAuth() {
    // 1. Check local session storage for instant persistence across refreshes
    const savedUser = localStorage.getItem("prohealth_google_user");
    if (savedUser) {
        try {
            currentGoogleUser = JSON.parse(savedUser);
            renderGoogleNavAuth(currentGoogleUser);
        } catch (e) {
            console.error("Local user load error:", e);
        }
    } else {
        renderGoogleNavAuth(null);
    }

    // 2. Initialize Google Identity Services
    if (window.google && google.accounts && google.accounts.id) {
        setupGoogleSignIn();
    } else {
        const checkInterval = setInterval(() => {
            if (window.google && google.accounts && google.accounts.id) {
                clearInterval(checkInterval);
                setupGoogleSignIn();
            }
        }, 300);
    }
}

function setupGoogleSignIn() {
    try {
        google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleGoogleCredentialResponse,
            auto_select: false,
            cancel_on_tap_outside: true
        });

        renderGoogleModalButton();
    } catch (err) {
        console.error("Google Auth initialization error:", err);
    }
}

function renderGoogleModalButton() {
    const container = document.getElementById("g_id_modal_signin_btn");
    if (!container || !window.google?.accounts?.id) return;

    container.innerHTML = "";
    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    google.accounts.id.renderButton(
        container,
        {
            theme: isLight ? "outline" : "filled_black",
            size: "large",
            shape: "pill",
            text: "signin_with",
            width: "320",
            logo_alignment: "left"
        }
    );
}

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("JWT parse error:", e);
        return null;
    }
}

function handleGoogleCredentialResponse(response) {
    if (!response || !response.credential) return;

    const payload = parseJwt(response.credential);
    if (!payload) return;

    currentGoogleUser = {
        name: payload.name || "Patient Member",
        firstName: payload.given_name || (payload.name ? payload.name.split(" ")[0] : "Patient"),
        email: payload.email || "",
        picture: payload.picture || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200",
        id: payload.sub || ""
    };

    localStorage.setItem("prohealth_google_user", JSON.stringify(currentGoogleUser));
    renderGoogleNavAuth(currentGoogleUser);
    closeSignInPrompt();

    // If user clicked book appointment before signing in, proceed seamlessly with booking
    if (pendingBookingAction) {
        const action = pendingBookingAction;
        pendingBookingAction = null;
        action();
    } else {
        openUserDashboard();
    }
}

function renderGoogleNavAuth(user) {
    const container = document.getElementById("googleAuthNav");
    if (!container) return;

    if (user) {
        const displayName = user.firstName || user.name || "Patient";
        const avatarUrl = user.picture || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=200";

        container.innerHTML = `
            <div class="user-nav-badge" onclick="openUserDashboard()" title="${currentLang === 'bn' ? 'গুগল প্রোফাইল ও ড্যাশবোর্ড খুলুন' : 'Open Google Patient Dashboard'}">
                <div class="user-nav-avatar">
                    <img src="${avatarUrl}" alt="${displayName}">
                    <span class="user-nav-dot"></span>
                </div>
                <span class="user-nav-name">${displayName}</span>
                <i class="fa-solid fa-chevron-down nav-dropdown-icon"></i>
            </div>
        `;
    } else {
        const loginText = currentLang === 'bn' ? 'লগইন / সাইন ইন' : 'Sign In';
        container.innerHTML = `
            <button class="btn btn-outline btn-login-nav" onclick="openSignInPrompt()">
                <i class="fa-solid fa-arrow-right-to-bracket"></i> <span id="navLoginText">${loginText}</span>
            </button>
        `;
    }
}

function openSignInPrompt(callbackAction = null) {
    pendingBookingAction = callbackAction;
    const modal = document.getElementById("signInPromptModal");
    if (modal) {
        modal.classList.add("open");
        renderGoogleModalButton();
    }
}

function closeSignInPrompt() {
    const modal = document.getElementById("signInPromptModal");
    if (modal) modal.classList.remove("open");
}

function handleGoogleSignOut() {
    localStorage.removeItem("prohealth_google_user");
    currentGoogleUser = null;
    pendingBookingAction = null;

    if (window.google && google.accounts && google.accounts.id) {
        google.accounts.id.disableAutoSelect();
    }

    renderGoogleNavAuth(null);
    closeUserDashboard();
}

/* =============================================================================
   PATIENT USER DASHBOARD (MY APPOINTMENTS) CONTROLLER
   ============================================================================= */
function openUserDashboard() {
    if (!currentGoogleUser) {
        openSignInPrompt();
        return;
    }

    const modal = document.getElementById("userDashboardModal");
    if (!modal) return;

    const nameEl = document.getElementById("dashUserName");
    const emailEl = document.getElementById("dashUserEmail");
    const avatarEl = document.getElementById("dashUserAvatar");

    if (nameEl) nameEl.innerText = currentGoogleUser.name || "Patient Member";
    if (emailEl) emailEl.innerHTML = `<i class="fa-regular fa-envelope"></i> ${currentGoogleUser.email || "patient@gmail.com"}`;
    if (avatarEl && currentGoogleUser.picture) avatarEl.src = currentGoogleUser.picture;

    loadUserAppointments();
    modal.classList.add("open");
}

function closeUserDashboard() {
    const modal = document.getElementById("userDashboardModal");
    if (modal) modal.classList.remove("open");
}

async function loadUserAppointments() {
    const container = document.getElementById("userAppointmentsContainer");
    const badgeText = document.getElementById("dashBookingCountText");
    if (!container) return;

    container.innerHTML = `
        <div class="dash-loading-state">
            <i class="fa-solid fa-spinner fa-spin"></i>
            <p>${currentLang === 'bn' ? 'অ্যাপয়েন্টমেন্ট লোড হচ্ছে...' : 'Loading appointments...'}</p>
        </div>
    `;

    try {
        const email = currentGoogleUser?.email || "";
        const url = `/api/user/appointments?email=${encodeURIComponent(email)}`;

        const res = await fetch(url);
        const appointments = await res.json();

        if (badgeText) {
            badgeText.innerText = currentLang === 'bn' ? `${appointments.length} টি অ্যাপয়েন্টমেন্ট` : `${appointments.length} Appointments`;
        }

        renderUserAppointments(appointments);
    } catch (err) {
        console.error("Error loading appointments:", err);
        container.innerHTML = `
            <div class="dash-empty-state">
                <i class="fa-solid fa-triangle-exclamation" style="color: #EF4444;"></i>
                <h4>${currentLang === 'bn' ? 'তথ্য লোড করা যায়নি' : 'Could not load bookings'}</h4>
                <button class="btn btn-sm btn-outline" onclick="loadUserAppointments()">${currentLang === 'bn' ? 'পুনরায় চেষ্টা করুন' : 'Try Again'}</button>
            </div>
        `;
    }
}

function renderUserAppointments(appointments) {
    const container = document.getElementById("userAppointmentsContainer");
    if (!container) return;

    if (!appointments || appointments.length === 0) {
        container.innerHTML = `
            <div class="dash-empty-state">
                <div class="dash-empty-icon"><i class="fa-regular fa-calendar-xmark"></i></div>
                <h4>${currentLang === 'bn' ? 'কোনো অ্যাপয়েন্টমেন্ট বুকিং পাওয়া যায়নি' : 'No Appointments Found'}</h4>
                <p>${currentLang === 'bn' ? 'আপনি এখনো কোনো ডাক্তারের অ্যাপয়েন্টমেন্ট বুক করেননি। নিচের বাটনে ক্লিক করে যেকোনো ডাক্তারের অ্যাপয়েন্টমেন্ট বুক করতে পারেন।' : 'You have not booked any appointments yet. Click below to book an appointment with our specialist doctors.'}</p>
                <button class="btn btn-primary btn-sm" onclick="closeUserDashboard(); openAppointmentModal();">
                    <i class="fa-regular fa-calendar-plus"></i> <span>${currentLang === 'bn' ? 'নতুন অ্যাপয়েন্টমেন্ট বুক করুন' : 'Book New Appointment'}</span>
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = "";
    appointments.forEach(apt => {
        const card = document.createElement("div");
        card.className = "dash-appointment-card";

        card.innerHTML = `
            <div class="apt-card-top">
                <div class="apt-doc-info">
                    <div class="apt-doc-avatar">${apt.avatar || "👨‍⚕️"}</div>
                    <div>
                        <h4 class="apt-doc-name">${apt.doctor_name}</h4>
                        <span class="apt-doc-dept">${apt.department}</span>
                    </div>
                </div>
                <div class="apt-status-badge">
                    <span class="pulse-dot-green"></span> ${apt.status || "Confirmed"}
                </div>
            </div>

            <div class="apt-card-body">
                <div class="apt-meta-item">
                    <i class="fa-regular fa-calendar"></i>
                    <div>
                        <span class="apt-meta-label">${currentLang === 'bn' ? 'তারিখ' : 'Date'}:</span>
                        <strong>${apt.date}</strong>
                    </div>
                </div>
                <div class="apt-meta-item">
                    <i class="fa-regular fa-clock"></i>
                    <div>
                        <span class="apt-meta-label">${currentLang === 'bn' ? 'সময়' : 'Time'}:</span>
                        <strong>${apt.time || "OPD Hours"}</strong>
                    </div>
                </div>
                <div class="apt-meta-item">
                    <i class="fa-solid fa-door-open"></i>
                    <div>
                        <span class="apt-meta-label">${currentLang === 'bn' ? 'রুম' : 'Room'}:</span>
                        <strong>${apt.room || "Desk 101"}</strong>
                    </div>
                </div>
                <div class="apt-meta-item">
                    <i class="fa-solid fa-receipt"></i>
                    <div>
                        <span class="apt-meta-label">${currentLang === 'bn' ? 'ফি' : 'Fee'}:</span>
                        <strong>${apt.fee || "৳ 1,000"}</strong>
                    </div>
                </div>
            </div>

            <div class="apt-card-footer">
                <span class="apt-ticket-id"><i class="fa-solid fa-hashtag"></i> ${apt.ticket_id}</span>
                <div class="apt-actions">
                    <button class="btn btn-sm btn-outline-danger" onclick="cancelUserAppointment('${apt.ticket_id}')">
                        <i class="fa-solid fa-trash-can"></i> <span>${currentLang === 'bn' ? 'বাতিল' : 'Cancel'}</span>
                    </button>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function cancelUserAppointment(ticketId) {
    const confirmMsg = currentLang === 'bn' ? 
        "আপনি কি নিশ্চিত যে এই অ্যাপয়েন্টমেন্টটি বাতিল করতে চান?" : 
        "Are you sure you want to cancel this appointment?";
    
    if (!confirm(confirmMsg)) return;

    try {
        const res = await fetch(`/api/user/appointments/${ticketId}`, { method: "DELETE" });
        if (res.ok) {
            loadUserAppointments();
        } else {
            alert("Could not cancel appointment.");
        }
    } catch (e) {
        console.error("Error cancelling appointment:", e);
    }
}

const I18N = {
    bn: {
        topEmergency: "২৪/৭ জরুরি ও ট্রমা সেবা চালু আছে (24/7 Trauma Care Active)",
        topHotline: '<i class="fa-solid fa-phone-volume"></i> জরুরি হটলাইন: <strong>10666</strong>',
        topAmbulance: '<i class="fa-solid fa-truck-medical"></i> অ্যাম্বুলেন্স: <strong>+880 1999-000000</strong>',
        navHome: "হোম",
        navTriage: "AI ডায়াগনোসিস",
        navDoctors: "ডাক্তারদের তালিকা",
        navFacilities: "সুবিধা ও সেবা",
        navAbout: "আমাদের সম্পর্কে",
        navBookBtn: "অ্যাপয়েন্টমেন্ট নিন",

        // Slide 1
        slide1Tag: '<i class="fa-solid fa-robot"></i> Bio_ClinicalBERT Powered AI',
        slide1Title: 'আপনার লক্ষণ বলুন, সঠিক ডাক্তার ও বিভাগ খুঁজে দেবে <span>ProHealth AI</span>',
        slide1Desc: 'বাংলা, বাংলিশ অথবা ইংরেজিতে আপনার শারীরিক সমস্যার কথা লিখুন। আমাদের অত্যাধুনিক মেডিকেল এআই তাৎক্ষণিক সঠিক বিভাগ ও বিশেষজ্ঞ ডাক্তার নির্ধারণ করবে।',
        slide1Cta1: '<i class="fa-solid fa-wand-magic-sparkles"></i> বিনামূল্যে এআই ডায়াগনোসিস করুন',
        slide1Cta2: '<i class="fa-solid fa-stethoscope"></i> বিশেষজ্ঞ তালিকা দেখুন',

        // Slide 2
        slide2Tag: '<i class="fa-solid fa-heart-circle-bolt"></i> 24/7 Advanced Cath-Lab & ICU',
        slide2Title: 'বিশ্বমানের হৃদরোগ চিকিৎসা ও <span>ইন্টেনসিভ কেয়ার ইউনিট</span>',
        slide2Desc: 'দক্ষ কার্ডিওলজিস্ট ও পালমোনোলজিস্টদের তত্ত্বাবধানে সর্বাধুনিক ইকুইপমেন্ট সম্বলিত ডেডিকেটেড সিসিইউ ও জরুরি ট্রমা সেবা।',
        slide2Cta1: '<i class="fa-solid fa-user-doctor"></i> কার্ডিওলজি ডাক্তার দেখুন',
        slide2Cta2: '<i class="fa-solid fa-phone"></i> জরুরি কল: 10666',

        // Slide 3
        slide3Tag: '<i class="fa-solid fa-bone"></i> Joint & Spine Reconstruction',
        slide3Title: 'হাড়, জয়েন্ট ও মেরুদণ্ডের সর্বাধুনিক <span>অর্থোপেডিক সার্জারি</span>',
        slide3Desc: 'কম্পিউটার-গাইডেড জয়েন্ট প্রতিস্থাপন, স্পোর্টস ইনজুরি ও ট্রমা ম্যানেজমেন্টে আন্তর্জাতিক মানের বিশেষজ্ঞ টিম।',
        slide3Cta1: '<i class="fa-solid fa-user-doctor"></i> অর্থোপেডিকস বিভাগ',
        slide3Cta2: '<i class="fa-solid fa-building-circle-check"></i> আধুনিক ওটি দেখুন',

        // Slide 4
        slide4Tag: '<i class="fa-solid fa-baby"></i> Child & Mother Care Center',
        slide4Title: 'মা ও শিশুর জন্য মমতাময়ী ও <span>বিশেষায়িত স্বাস্থ্যসেবা</span>',
        slide4Desc: 'নবজাতক আইসিইউ (NICU), শিশু বিশেষজ্ঞ ও অভিজ্ঞ গাইনিকোলজিস্টদের সার্বক্ষণিক সেবা ও মনিটরিং।',
        slide4Cta1: '<i class="fa-solid fa-hands-holding-child"></i> পেডিয়াট্রিক্স কেয়ার',
        slide4Cta2: '<i class="fa-solid fa-magnifying-glass"></i> লক্ষণ যাচাই করুন',

        // Stats
        stat1Label: "বিশেষায়িত বিভাগ (Departments)",
        stat2Label: "অভিজ্ঞ বিশেষজ্ঞ ডাক্তার (Specialists)",
        stat3Label: "সফল এআই ডায়াগনোসিস রেফারেল",
        stat4Label: "রোগী সন্তুষ্টির হার (Satisfaction)",

        // Triage Section
        triageSecBadge: '<i class="fa-solid fa-brain"></i> Intelligent Instant Diagnosis',
        triageSecTitle: "আপনার সমস্যার জন্য দ্রুত সমাধান নিন",
        triageSecSubtitle: "বাংলা, বাংলিশ বা ইংরেজিতে আপনার শারীরিক সমস্যা বা লক্ষণের বিবরণ দিন। আমাদের Bio_ClinicalBERT এআই মুহূর্তেই আপনাকে সঠিক বিভাগ ও পরামর্শক ডাক্তার সাজেস্ট করবে।",
        symptomBoxTitle: "রোগীর অভিযোগ / লক্ষণের বিবরণ (Patient Symptoms)",
        voiceBtnText: "ভয়েস ইনপুট",
        symptomPlaceholder: "উদাহরণ: আমার ২ দিন ধরে প্রচণ্ড বুকে ব্যথা হচ্ছে এবং শ্বাস নিতে কষ্ট হচ্ছে... অথবা 'amar matha ghure r bomi hocche' অথবা 'Severe knee pain after injury'",
        sampleChipsLabel: '<i class="fa-regular fa-lightbulb"></i> দ্রুত নমুনা ট্রাই করুন:',
        clearBtnText: "ক্লিয়ার",
        analyzeBtnText: "এআই দিয়ে বিশ্লেষণ করুন",

        emptyTitle: "আপনার লক্ষণের জন্য অপেক্ষা করা হচ্ছে",
        emptyDesc: 'বাম পাশের বক্সে সমস্যা লিখে <strong>"এআই দিয়ে বিশ্লেষণ করুন"</strong> বাটনে চাপুন। তাৎক্ষণিক ক্লিনিক্যাল ডায়াগনোসিস রিপোর্ট এখানে প্রদর্শিত হবে।',
        loadingTitle: "Bio_ClinicalBERT মডেল বিশ্লেষণ করছে...",
        loadingDesc: "ভাষা শনাক্তকরণ, মেডিকেল অ্যান্টোলজি ম্যাপিং এবং ইমার্জেন্সি লেভেল প্রসেস হচ্ছে...",
        resDeptMeta: "প্রস্তাবিত মেডিকেল বিভাগ (Recommended Department):",
        resSpecMeta: "পরামর্শক বিশেষজ্ঞ (Suggested Doctor):",
        resProbTitle: '<i class="fa-solid fa-chart-column"></i> শীর্ষ ৩টি সম্ভাব্য বিভাগ ও সম্ভাব্যতা:',
        resAdviceHeader: '<i class="fa-solid fa-circle-info"></i> তাৎক্ষণিক ক্লিনিক্যাল পরামর্শ:',
        recDocHeaderTitle: "সুপারিশকৃত বিশেষজ্ঞ ডাক্তারগণ (Recommended Doctors)",
        recDocHeaderSub: "AI পূর্বাভাস অনুযায়ী পদবী, রেটিং ও অভিজ্ঞতার ভিত্তিতে সেরা ডাক্তার তালিকা",
        recDeptPill: '<i class="fa-solid fa-star"></i> শীর্ষ ডাক্তার তালিকা',
        pdfBtnText: "অফিসিয়াল PDF টিকেট ডাউনলোড",
        bookDocBtnText: "এই বিভাগে ডাক্তার বুক করুন",

        // Doctors Section
        docSecBadge: '<i class="fa-solid fa-user-doctor"></i> Specialist Directory',
        docSecTitle: "আমাদের অভিজ্ঞ বিশেষজ্ঞ ডাক্তারবৃন্দ",
        docSecSubtitle: "আপনার প্রয়োজনীয় বিভাগ নির্বাচন করে ডাক্তারদের সময়সূচি, যোগ্যতা ও ভিজিটিং ফি দেখুন এবং সরাসরি অ্যাপয়েন্টমেন্ট নিন।",
        tabAll: "সকল বিভাগ (All)",
        tabCardiology: "কার্ডিওলজি (Cardiology)",
        tabOrthopedics: "অর্থোপেডিকস (Orthopedics)",
        tabNeurology: "নিউরোলজি (Neurology)",
        tabGastro: "গ্যাস্ট্রোএন্টারোলজি (Gastro)",
        tabDermatology: "ডার্মাটোলজি (Dermatology)",
        tabPediatrics: "শিশু রোগ (Pediatrics)",
        tabGynecology: "গাইনিকোলজি (Gynecology)",
        tabEnt: "ইএনটি / নাক কান গলা (ENT)",
        tabUrology: "ইউরোলজি ও কিডনি (Urology)",
        tabGeneral: "জেনারেল মেডিসিন (Medicine)",

        // Facilities Section
        facSecBadge: '<i class="fa-solid fa-hospital"></i> Infrastructure & Care',
        facSecTitle: "অত্যাধুনিক চিকিৎসা ও হাসপাতালের সুবিধাসমূহ",
        facSecSubtitle: "আন্তর্জাতিক মানের স্বাস্থ্যসেবা নিশ্চিত করতে আমাদের রয়েছে পূর্ণাঙ্গ ও হাই-টেক মেডিকেল সুযোগ-সুবিধা।",

        // About Section
        aboutBadge: '<i class="fa-solid fa-shield-halved"></i> AI Transparency & Safety',
        aboutTitle: "কীভাবে কাজ করে ProHealth AI Assistant?",
        aboutDesc: "আমাদের এআই সিস্টেমটি বিশ্বখ্যাত <strong>MTSamples (Medical Transcriptions)</strong> বেঞ্চমার্ক ক্লিনিক্যাল ডেটাসেটের উপর ফাইন-টিউন করা <strong>Bio_ClinicalBERT</strong> (যা MIMIC-III ও PubMed ক্লিনিক্যাল ডেটায় প্রি-ট্রেইনড) ডিপ লার্নিং ট্রান্সফরমার আর্কিটেকচার দ্বারা পরিচালিত। এটি রোগীর বাংলা, বাংলিশ ও ইংরেজি অভিযোগ প্রসেস করে ১৩টি প্রধান মেডিকেল বিভাগে নির্ভুলভাবে ক্লাসিফাই করে।",
        feat1: "<strong>প্রশিক্ষণ ডেটাসেট (MTSamples & MIMIC-III):</strong> হাজার হাজার বাস্তব ক্লিনিক্যাল কেস নোট ও ট্রান্সক্রিপশন ডেটাসেটে প্রশিক্ষিত।",
        feat2: "<strong>বহুভাষিক প্রসেসিং:</strong> বাংলা, বাংলিশ ও ইংরেজি টেক্সট সরাসরি বিশ্লেষণ করে তাৎক্ষণিক রেজাল্ট দেয়।",
        feat3: "<strong>স্বয়ংক্রিয় ইমার্জেন্সি ডিটেকশন:</strong> হার্ট অ্যাটাক, স্ট্রোক বা তীব্র শ্বাসকষ্টের মতো রেড-ফ্ল্যাগ লক্ষণ দেখলে তৎক্ষণাৎ লেভেল ১ ইমার্জেন্সি অ্যালার্ট দেয়।",
        // Sign-In Modal & Dashboard
        signInModalTitle: "গুগল দিয়ে সাইন ইন করুন",
        signInModalDesc: "ডাক্তার অ্যাপয়েন্টমেন্ট বুকিং করতে এবং আপনার পূর্বের বুকিং হিস্ট্রি সংরক্ষণ করতে গুগল অ্যাকাউন্ট দিয়ে সাইন ইন করুন।",
        signInFeat1: "১০০% নিরাপদ ও ভেরিফাইড গুগল অথেন্টিকেশন",
        signInFeat2: "১-ক্লিকে তাৎক্ষণিক অ্যাপয়েন্টমেন্ট বুকিং সুবিধা",
        signInFeat3: "সকল পূর্বের অ্যাপয়েন্টমেন্ট ও প্রেস্ক্রিপশন হিস্ট্রি",
        navLoginText: "সাইন ইন",
        dashVerifiedBadge: "ভেরিফাইড গুগল রোগী",
        dashHistoryTitle: '<i class="fa-solid fa-calendar-days"></i> আমার অ্যাপয়েন্টমেন্ট হিস্ট্রি (My Appointments)',
        dashRefreshBtn: '<i class="fa-solid fa-rotate-right"></i> রিফ্রেশ',
        dashSignOutText: "লগআউট",

        // Modal
        modalHeaderTitle: "ডাক্তার অ্যাপয়েন্টমেন্ট বুকিং",
        lblPatientName: "রোগীর পুরো নাম (Patient Full Name) *",
        lblPhone: "মোবাইল নম্বর (Phone Number) *",
        lblAge: "রোগীর বয়স (Age)",
        lblDept: "মেডিকেল বিভাগ (Department) *",
        lblDoctor: "পছন্দের ডাক্তার (Select Doctor)",
        lblDate: "অ্যাপয়েন্টমেন্টের তারিখ (Preferred Date) *",
        lblSymptoms: "সংক্ষিপ্ত সমস্যা বা উপসর্গ (Brief Symptoms)",
        modalCancelBtn: "বাতিল",
        modalSubmitBtn: '<i class="fa-solid fa-check"></i> নিশ্চিত করুন (Confirm Booking)',

        // Footer
        footerDesc: "আধুনিক কৃত্রিম বুদ্ধিমত্তা ও ক্লিনিক্যাল এক্সিলেন্সের সমন্বয়ে প্রস্তুতকৃত স্মার্ট হাসপাতাল পোর্টাল ও ডায়াগনোসিস সিস্টেম।",
        footerEmergencyHeader: "জরুরি যোগাযোগ (Emergency)",
        footerAddress: '<i class="fa-solid fa-location-dot"></i> প্লট ১৫, রোড ৭১, গুলশান-২, ঢাকা ১২১২',
        footerDeptsHeader: "বিশেষায়িত বিভাগসমূহ",
        footerHoursHeader: "হাসপাতাল খোলার সময়",
        footerOpdHours: "<strong>বহির্বিভাগ (OPD):</strong><br>শনিবার - বৃহস্পতিবার: ৮:০০ AM - ১০:০০ PM<br>শুক্রবার: ৩:০০ PM - ৯:০০ PM",
        footerEmergencyHours: '<strong>জরুরি বিভাগ (Emergency):</strong><br><span class="badge-active">২৪ ঘণ্টা খোলা (24 Hours Open)</span>',
        footerCopyright: "© 2026 ProHealth AI Assistant. All Rights Reserved. Built with Bio_ClinicalBERT & FastAPI.",
        footerDisclaimer: "Disclaimer: এই এআই ডায়াগনোসিস সিস্টেমটি প্রাথমিক রেফারেল সহায়তার জন্য। জরুরি অবস্থায় অবিলম্বে হাসপাতালের জরুরি বিভাগে যোগাযোগ করুন।"
    },
    en: {
        topEmergency: "24/7 Trauma & Emergency Center Active",
        topHotline: '<i class="fa-solid fa-phone-volume"></i> Emergency Hotline: <strong>10666</strong>',
        topAmbulance: '<i class="fa-solid fa-truck-medical"></i> Ambulance: <strong>+880 1999-000000</strong>',
        navHome: "Home",
        navTriage: "Instant Diagnosis",
        navDoctors: "Doctor Directory",
        navFacilities: "Facilities & Care",
        navAbout: "About AI",
        navBookBtn: "Book Appointment",

        // Slide 1
        slide1Tag: '<i class="fa-solid fa-robot"></i> Bio_ClinicalBERT Powered AI',
        slide1Title: 'Describe Your Symptoms, Let <span>ProHealth AI</span> Find the Right Doctor',
        slide1Desc: 'Enter your medical complaint in natural language (Bangla, Banglish, or English). Our clinical transformer model maps your symptoms to the exact medical specialty and doctor.',
        slide1Cta1: '<i class="fa-solid fa-wand-magic-sparkles"></i> Try Free Instant Diagnosis',
        slide1Cta2: '<i class="fa-solid fa-stethoscope"></i> View Specialists',

        // Slide 2
        slide2Tag: '<i class="fa-solid fa-heart-circle-bolt"></i> 24/7 Advanced Cath-Lab & ICU',
        slide2Title: 'World-Class Cardiovascular Care & <span>Critical Care Unit</span>',
        slide2Desc: 'State-of-the-art Coronary Care Unit (CCU) and emergency catheterization lab led by renowned cardiologists and pulmonologists.',
        slide2Cta1: '<i class="fa-solid fa-user-doctor"></i> View Cardiologists',
        slide2Cta2: '<i class="fa-solid fa-phone"></i> Emergency Call: 10666',

        // Slide 3
        slide3Tag: '<i class="fa-solid fa-bone"></i> Joint & Spine Reconstruction',
        slide3Title: 'Advanced Orthopedic, Joint & <span>Spine Reconstruction</span>',
        slide3Desc: 'Computer-navigated joint replacement, athletic injury recovery, and comprehensive trauma center.',
        slide3Cta1: '<i class="fa-solid fa-user-doctor"></i> Orthopedic Wing',
        slide3Cta2: '<i class="fa-solid fa-building-circle-check"></i> Explore Modern OTs',

        // Slide 4
        slide4Tag: '<i class="fa-solid fa-baby"></i> Child & Mother Care Center',
        slide4Title: 'Compassionate & Specialized <span>Maternal & Child Care</span>',
        slide4Desc: 'Level 3 Neonatal Intensive Care Unit (NICU), pediatric intensivists, and experienced gynecologists available 24/7.',
        slide4Cta1: '<i class="fa-solid fa-hands-holding-child"></i> Pediatrics Care',
        slide4Cta2: '<i class="fa-solid fa-magnifying-glass"></i> Check Symptoms',

        // Stats
        stat1Label: "Specialized Departments",
        stat2Label: "Senior Medical Specialists",
        stat3Label: "Instant Diagnoses Completed",
        stat4Label: "Patient Satisfaction Rate",

        // Triage Section
        triageSecBadge: '<i class="fa-solid fa-brain"></i> Intelligent Instant Diagnosis',
        triageSecTitle: "Instant AI Department Referral & Diagnosis",
        triageSecSubtitle: "Type your symptoms in English, Bangla, or Banglish. Our Bio_ClinicalBERT neural model instantly categorizes your case, assigns clinical urgency, and suggests appropriate specialists.",
        symptomBoxTitle: "Patient Complaint & Symptoms",
        voiceBtnText: "Voice Input",
        symptomPlaceholder: "e.g., 'Severe crushing chest pain radiating to left arm with shortness of breath' or 'High fever and rash on a 3-year-old child'...",
        sampleChipsLabel: '<i class="fa-regular fa-lightbulb"></i> Quick Sample Prompts:',
        clearBtnText: "Clear",
        analyzeBtnText: "Analyze with AI",

        emptyTitle: "Waiting for Patient Symptoms",
        emptyDesc: 'Describe your symptoms on the left and click <strong>"Analyze with AI"</strong>. Instant clinical department referral will appear here.',
        loadingTitle: "Bio_ClinicalBERT Model Analyzing...",
        loadingDesc: "Processing multilingual text, clinical ontology extraction, and emergency priority...",
        resDeptMeta: "Recommended Medical Specialty / Department:",
        resSpecMeta: "Suggested Consultant Doctor:",
        resProbTitle: '<i class="fa-solid fa-chart-column"></i> Top 3 Department Probability Breakdown:',
        resAdviceHeader: '<i class="fa-solid fa-circle-info"></i> Clinical Diagnosis Guidance:',
        recDocHeaderTitle: "AI Recommended Specialist Doctors",
        recDocHeaderSub: "Top medical specialists ranked by seniority, credentials & match score",
        recDeptPill: '<i class="fa-solid fa-star"></i> AI Ranked Specialists',
        pdfBtnText: "Download Official PDF Slip",
        bookDocBtnText: "Book Doctor in this Department",

        // Doctors Section
        docSecBadge: '<i class="fa-solid fa-user-doctor"></i> Specialist Directory',
        docSecTitle: "Meet Our Distinguished Medical Specialists",
        docSecSubtitle: "Filter by department to explore doctor schedules, credentials, consultation fees, and book direct appointments.",
        tabAll: "All Departments",
        tabCardiology: "Cardiology & Pulmonology",
        tabOrthopedics: "Orthopedics & Trauma",
        tabNeurology: "Neurology & Stroke",
        tabGastro: "Gastroenterology",
        tabDermatology: "Dermatology",
        tabPediatrics: "Pediatrics & Child Care",
        tabGynecology: "Gynecology & Obs",
        tabEnt: "ENT (Otolaryngology)",
        tabUrology: "Urology & Nephrology",
        tabGeneral: "General Internal Medicine",

        // Facilities Section
        facSecBadge: '<i class="fa-solid fa-hospital"></i> Infrastructure & Care',
        facSecTitle: "Cutting-Edge Medical Infrastructure",
        facSecSubtitle: "Providing tertiary healthcare excellence with advanced diagnostic labs, modular OTs, and critical care units.",

        // About Section
        aboutBadge: '<i class="fa-solid fa-shield-halved"></i> AI Transparency & Safety',
        aboutTitle: "How ProHealth AI Assistant Works?",
        aboutDesc: "Built on top of <strong>Bio_ClinicalBERT</strong> (pre-trained on MIMIC-III & PubMed) and fine-tuned on the gold-standard <strong>MTSamples (Medical Transcriptions) Benchmark Dataset</strong>, our AI system analyzes multilingual clinical complaints in real time to match patient symptoms to 13 specialized hospital wings.",
        feat1: "<strong>Training Dataset (MTSamples & MIMIC-III):</strong> Fine-tuned on real-world medical transcriptions across 13 clinical specialties.",
        feat2: "<strong>Multilingual NLP Engine:</strong> Native support for English, Bangla, and phonetic Banglish symptom inputs.",
        feat3: "<strong>Automated Red-Flag Urgency Triage:</strong> Detects acute life-threatening presentations for immediate Level 1 Emergency care routing.",
        // Sign-In Modal & Dashboard
        signInModalTitle: "Sign In with Google",
        signInModalDesc: "Sign in with your Google account to book specialist doctor appointments and access your personal medical history.",
        signInFeat1: "100% Secure & Verified Google Authentication",
        signInFeat2: "1-Click Instant Doctor Appointment Booking",
        signInFeat3: "Access Complete History & Referral Slips Anytime",
        navLoginText: "Sign In",
        dashVerifiedBadge: "Verified Google Patient",
        dashHistoryTitle: '<i class="fa-solid fa-calendar-days"></i> My Appointment History',
        dashRefreshBtn: '<i class="fa-solid fa-rotate-right"></i> Refresh',
        dashSignOutText: "Sign Out",

        // Modal
        modalHeaderTitle: "Book Doctor Appointment",
        lblPatientName: "Patient Full Name *",
        lblPhone: "Mobile Phone Number *",
        lblAge: "Patient Age (Years)",
        lblDept: "Medical Department *",
        lblDoctor: "Select Doctor",
        lblDate: "Appointment Date *",
        lblSymptoms: "Brief Symptoms / Medical Note",
        modalCancelBtn: "Cancel",
        modalSubmitBtn: '<i class="fa-solid fa-check"></i> Confirm Appointment',

        // Footer
        footerDesc: "AI-Powered Smart Instant Diagnosis and Hospital Management System built with Bio_ClinicalBERT & FastAPI.",
        footerEmergencyHeader: "Emergency Contacts",
        footerAddress: '<i class="fa-solid fa-location-dot"></i> Plot 15, Road 71, Gulshan-2, Dhaka 1212',
        footerDeptsHeader: "Specialized Wings",
        footerHoursHeader: "Visiting & OPD Hours",
        footerOpdHours: "<strong>Outpatient (OPD):</strong><br>Saturday - Thursday: 8:00 AM - 10:00 PM<br>Friday: 3:00 PM - 9:00 PM",
        footerEmergencyHours: '<strong>Emergency Wing:</strong><br><span class="badge-active">Open 24/7 Non-Stop</span>',
        footerCopyright: "© 2026 ProHealth AI Assistant. All Rights Reserved. Powered by Bio_ClinicalBERT.",
        footerDisclaimer: "Disclaimer: This AI system is designed for initial clinical department referral. In case of acute medical emergencies, immediately contact emergency services or visit the nearest ER."
    }
};

// Sample Chips Database (Pure Symptom Prompts without category labels)
const SAMPLE_CHIPS = {
    bn: [
        "বুকে তীব্র ব্যথা ও চাপ অনুভব করছি, বাম হাত অবশ হয়ে আসছে এবং নিঃশ্বাস নিতে খুব কষ্ট হচ্ছে।",
        "শরীরে ১০৪ ডিগ্রি তীব্র জ্বর, প্রচণ্ড দুর্বলতা লাগছে এবং কাঁপানি দিয়ে শরীর গরম হয়ে আছে।",
        "পেটে অসহ্য তীব্র ব্যথা, বুক জ্বালাপোড়া ও বারবার বমি হচ্ছে এবং খাবার হজম হচ্ছে না।",
        "হাঁটুর লিগামেন্ট মচকে জয়েন্ট ফুলে গেছে এবং তীব্র ব্যথায় পা ফেলতে পারছি না।",
        "চোখে প্রচণ্ড ব্যথা, চারপাশ ঝাপসা দেখতেছি এবং চোখ লাল হয়ে অনবরত পানি পড়ছে।",
        "বাচ্চার বয়স ৪ মাস, প্রচণ্ড জ্বর এবং অসুস্থ হয়ে অবিরাম কান্না করছে।",
        "প্রস্রাবে তীব্র জ্বালাপোড়া করছে এবং কোমরের ডান পাশে কিডনিতে প্রচণ্ড ব্যথা হচ্ছে।",
        "মাথায় প্রচণ্ড মাইগ্রেনের ব্যথা ও মাথা তীব্রভাবে ঘুরছে এবং সবকিছু অন্ধকার লাগছে।"
    ],
    en: [
        "Patient presents with severe chest pain, angina pectoris, shortness of breath, and left arm numbness.",
        "High body temperature 104 degree fever with severe chills, shivering, and body weakness.",
        "Patient suffering from acute abdominal pain, nausea, vomiting, and severe acid reflux.",
        "Severe right knee fracture and ligament tear after trauma with joint swelling and inability to bear weight.",
        "Severe eye pain with blurry vision, conjunctival redness, and excessive watering.",
        "4-month-old infant with high fever, respiratory distress, and continuous crying.",
        "Acute flank pain with severe burning sensation during urination and suspected kidney stones.",
        "Severe throbbing migraine headache with vertigo, dizziness, and sensitivity to light."
    ]
};

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    switchLanguage("en");
    initHeroSlider();
    initVoiceRecognition();
    renderSampleChips();
    fetchDoctors("all");
    fetchFacilities();
    initDeptTabs();
    setDefaultAppointmentDate();
});

/* =============================================================================
   1. LANGUAGE SWITCHING ENGINE
   ============================================================================= */
function switchLanguage(lang) {
    currentLang = lang;

    // Toggle active buttons
    const bnBtn = document.getElementById("langBnBtn");
    const enBtn = document.getElementById("langEnBtn");
    if (bnBtn) bnBtn.classList.toggle("active", lang === "bn");
    if (enBtn) enBtn.classList.toggle("active", lang === "en");

    document.documentElement.lang = lang;

    const dict = I18N[lang];
    if (!dict) return;

    // Apply translations by ID
    for (const [key, val] of Object.entries(dict)) {
        const el = document.getElementById(key);
        if (el) {
            if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
                el.placeholder = val;
            } else {
                el.innerHTML = val;
            }
        }
    }

    // Update Textarea Placeholder
    const symptomInput = document.getElementById("symptomInput");
    if (symptomInput) {
        symptomInput.placeholder = dict.symptomPlaceholder;
    }

    // Re-render Sample Chips
    renderSampleChips();

    // Re-render Doctors & Facilities in current language
    renderDoctorsGrid(doctorsData);
    fetchFacilities();

    // Refresh Google navbar auth and modal
    renderGoogleNavAuth(currentGoogleUser);
    renderGoogleModalButton();

    // If there is an active prediction, re-render triage display
    if (lastPredictionResult) {
        renderTriageResult(lastPredictionResult);
    }
}

function renderSampleChips() {
    const container = document.getElementById("chipsContainer");
    if (!container) return;

    container.innerHTML = "";
    const chips = SAMPLE_CHIPS[currentLang] || SAMPLE_CHIPS.bn;

    chips.forEach(promptText => {
        const btn = document.createElement("button");
        btn.className = "chip";
        btn.innerText = promptText;
        btn.title = "Click to try this symptom prompt";
        btn.onclick = () => setSample(promptText);
        container.appendChild(btn);
    });
}

/* =============================================================================
   2. HERO SLIDESHOW LOGIC
   ============================================================================= */
function initHeroSlider() {
    const slides = document.querySelectorAll(".slide");
    const dotsContainer = document.getElementById("sliderDots");
    if (!slides.length || !dotsContainer) return;

    dotsContainer.innerHTML = "";
    slides.forEach((_, idx) => {
        const dot = document.createElement("div");
        dot.classList.add("dot");
        if (idx === 0) dot.classList.add("active");
        dot.addEventListener("click", () => goToSlide(idx));
        dotsContainer.appendChild(dot);
    });

    const prevBtn = document.getElementById("prevSlide");
    const nextBtn = document.getElementById("nextSlide");

    if (prevBtn) prevBtn.addEventListener("click", prevSlide);
    if (nextBtn) nextBtn.addEventListener("click", nextSlide);

    startSlideTimer();

    const sliderContainer = document.getElementById("hero-slider");
    if (sliderContainer) {
        sliderContainer.addEventListener("mouseenter", stopSlideTimer);
        sliderContainer.addEventListener("mouseleave", startSlideTimer);
    }
}

function showSlide(index) {
    const slides = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");
    if (!slides.length) return;

    if (index >= slides.length) currentSlideIndex = 0;
    else if (index < 0) currentSlideIndex = slides.length - 1;
    else currentSlideIndex = index;

    slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === currentSlideIndex);
    });

    dots.forEach((dot, i) => {
        dot.classList.toggle("active", i === currentSlideIndex);
    });
}

function nextSlide() {
    showSlide(currentSlideIndex + 1);
}

function prevSlide() {
    showSlide(currentSlideIndex - 1);
}

function goToSlide(index) {
    showSlide(index);
}

function startSlideTimer() {
    stopSlideTimer();
    slideInterval = setInterval(nextSlide, 5500);
}

function stopSlideTimer() {
    if (slideInterval) clearInterval(slideInterval);
}

/* =============================================================================
   3. SPEECH RECOGNITION (VOICE INPUT)
   ============================================================================= */
function initVoiceRecognition() {
    const voiceBtn = document.getElementById("voiceInputBtn");
    const symptomInput = document.getElementById("symptomInput");
    if (!voiceBtn || !symptomInput) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtn.style.display = "none";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = currentLang === "bn" ? "bn-BD" : "en-US";

    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add("recording");
        voiceBtn.innerHTML = currentLang === "bn"
            ? `<i class="fa-solid fa-circle-stop"></i> <span>শুনছি...</span>`
            : `<i class="fa-solid fa-circle-stop"></i> <span>Listening...</span>`;
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        symptomInput.value = symptomInput.value ? symptomInput.value + " " + transcript : transcript;
    };

    recognition.onerror = () => stopRecording();
    recognition.onend = () => stopRecording();

    voiceBtn.addEventListener("click", () => {
        if (!isRecording) {
            try {
                recognition.lang = currentLang === "bn" ? "bn-BD" : "en-US";
                recognition.start();
            } catch (e) {
                console.error(e);
            }
        } else {
            recognition.stop();
        }
    });
}

function stopRecording() {
    isRecording = false;
    const voiceBtn = document.getElementById("voiceInputBtn");
    if (voiceBtn) {
        voiceBtn.classList.remove("recording");
        const btnText = currentLang === "bn" ? "ভয়েস ইনপুট" : "Voice Input";
        voiceBtn.innerHTML = `<i class="fa-solid fa-microphone"></i> <span>${btnText}</span>`;
    }
}

/* =============================================================================
   4. SAMPLE CHIPS & INPUT CONTROLS
   ============================================================================= */
function setSample(text) {
    const input = document.getElementById("symptomInput");
    if (input) {
        input.value = text;
        input.focus();
    }
}

function clearInput() {
    const input = document.getElementById("symptomInput");
    if (input) {
        input.value = "";
        input.focus();
    }
    const emptyState = document.getElementById("emptyState");
    const loadingState = document.getElementById("loadingState");
    const resultContent = document.getElementById("resultContent");
    const recSection = document.getElementById("aiRecDoctorsSection");

    if (emptyState) emptyState.style.display = "flex";
    if (loadingState) loadingState.style.display = "none";
    if (resultContent) resultContent.style.display = "none";
    if (recSection) recSection.style.display = "none";
    lastPredictionResult = null;
}

/* =============================================================================
   5. DOCTOR AVATAR HELPER
   ============================================================================= */
function getDoctorAvatarHTML(avatar) {
    if (avatar && (avatar.includes(".png") || avatar.includes(".jpg") || avatar.includes("/") || avatar.includes("http"))) {
        return `<img src="${avatar}" alt="Doctor" class="doc-img-avatar" onerror="this.onerror=null; this.src='/static/images/doctor_male_icon.png';" />`;
    }
    const defaultImg = (avatar && avatar.includes("👩"))
        ? "/static/images/doctor_female_icon.png"
        : "/static/images/doctor_male_icon.png";
    return `<img src="${defaultImg}" alt="Doctor" class="doc-img-avatar" />`;
}

/* =============================================================================
   6. ASYNC AI TRIAGE & PREDICTION ENGINE
   ============================================================================= */
async function analyzeSymptoms() {
    const input = document.getElementById("symptomInput");
    const complaint = input ? input.value.trim() : "";

    if (!complaint) {
        const msg = currentLang === "bn"
            ? "অনুগ্রহ করে আপনার সমস্যা বা লক্ষণ লিখুন।"
            : "Please enter your symptoms or complaint.";
        alert(msg);
        if (input) input.focus();
        return;
    }

    const emptyState = document.getElementById("emptyState");
    const loadingState = document.getElementById("loadingState");
    const resultContent = document.getElementById("resultContent");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const recSection = document.getElementById("aiRecDoctorsSection");

    if (emptyState) emptyState.style.display = "none";
    if (resultContent) resultContent.style.display = "none";
    if (recSection) recSection.style.display = "none";
    if (loadingState) loadingState.style.display = "flex";
    if (analyzeBtn) analyzeBtn.disabled = true;

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ complaint: complaint })
        });

        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }

        const data = await response.json();
        lastPredictionResult = data;
        renderTriageResult(data);
    } catch (err) {
        console.error("AI Analysis Error:", err);
        const errorMsg = currentLang === "bn"
            ? "বিশ্লেষণ করতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
            : "Failed to analyze symptoms. Please try again.";
        alert(errorMsg);
        if (emptyState) emptyState.style.display = "flex";
        if (resultContent) resultContent.style.display = "none";
        if (recSection) recSection.style.display = "none";
    } finally {
        if (loadingState) loadingState.style.display = "none";
        if (analyzeBtn) analyzeBtn.disabled = false;
    }
}

function renderTriageResult(data) {
    if (!data) return;

    const resultContent = document.getElementById("resultContent");
    const emptyState = document.getElementById("emptyState");
    const loadingState = document.getElementById("loadingState");
    const recSection = document.getElementById("aiRecDoctorsSection");

    if (emptyState) emptyState.style.display = "none";
    if (loadingState) loadingState.style.display = "none";
    if (resultContent) resultContent.style.display = "flex";
    if (recSection) recSection.style.display = "block";

    const triageBadge = document.getElementById("triageBadge");
    const triageIcon = document.getElementById("triageIcon");
    const triageLevelText = document.getElementById("triageLevelText");
    const confidenceText = document.getElementById("confidenceText");
    const deptTitleBn = document.getElementById("deptTitleBn");
    const deptTitleEn = document.getElementById("deptTitleEn");
    const probBarsContainer = document.getElementById("probBarsContainer");
    const adviceText = document.getElementById("adviceText");

    const triage = data.triage_urgency || {};
    const level = triage.level || "routine";

    // Set Triage Badge styling based on current language
    if (triageBadge) triageBadge.className = `triage-badge ${level}`;
    
    if (currentLang === "bn") {
        if (triageIcon && triageLevelText) {
            if (level === "emergency") {
                triageIcon.className = "fa-solid fa-triangle-exclamation";
                triageLevelText.innerText = "🔴 জরুরি ইমার্জেন্সি (লেভেল ১ - EMERGENCY)";
            } else if (level === "urgent") {
                triageIcon.className = "fa-solid fa-clock-rotate-left";
                triageLevelText.innerText = "🟡 অতি জরুরি কেয়ার (লেভেল ২ - URGENT)";
            } else {
                triageIcon.className = "fa-solid fa-circle-check";
                triageLevelText.innerText = "🟢 সাধারণ পরামর্শ (লেভেল ৩ - ROUTINE)";
            }
        }
        if (confidenceText) confidenceText.innerText = `কনফিডেন্স স্কোর: ${data.confidence_score}%`;
        if (deptTitleBn) deptTitleBn.innerText = data.recommended_department_bn || data.recommended_department;
        if (deptTitleEn) deptTitleEn.innerText = `${data.recommended_department} Department`;
        if (adviceText) {
            adviceText.innerText = triage.guidance_bn || "রোগীর অবস্থা পর্যবেক্ষণ করে শীঘ্রই চিকিৎসকের পরামর্শ গ্রহণ করুন।";
        }
    } else {
        if (triageIcon && triageLevelText) {
            if (level === "emergency") {
                triageIcon.className = "fa-solid fa-triangle-exclamation";
                triageLevelText.innerText = "🔴 LEVEL 1 - EMERGENCY CARE";
            } else if (level === "urgent") {
                triageIcon.className = "fa-solid fa-clock-rotate-left";
                triageLevelText.innerText = "🟡 LEVEL 2 - URGENT CONSULTATION";
            } else {
                triageIcon.className = "fa-solid fa-circle-check";
                triageLevelText.innerText = "🟢 LEVEL 3 - ROUTINE CHECKUP";
            }
        }
        if (confidenceText) confidenceText.innerText = `Confidence Score: ${data.confidence_score}%`;
        if (deptTitleBn) deptTitleBn.innerText = `${data.recommended_department} Department`;
        if (deptTitleEn) deptTitleEn.innerText = data.recommended_department_bn || "";
        if (adviceText) {
            adviceText.innerText = triage.guidance_en || "Patient should consult the specialist doctor at the earliest convenience.";
        }
    }

    // Render Top Recommended Doctor in the Prediction Card's Dedicated Div
    const predDocCardInner = document.getElementById("predDocCardInner");
    const predDocTopMatchBadge = document.getElementById("predDocTopMatchBadge");
    const recDocs = data.recommended_doctors || [];
    
    if (predDocCardInner && recDocs.length) {
        const topDoc = recDocs[0];
        const name = currentLang === "bn" ? (topDoc.name_bn || topDoc.name) : topDoc.name;
        const rankText = currentLang === "bn" ? (topDoc.rank_badge_bn || topDoc.rank_badge || "বিশেষজ্ঞ ডাক্তার") : (topDoc.rank_badge || "Specialist Doctor");
        
        if (predDocTopMatchBadge) {
            predDocTopMatchBadge.innerHTML = currentLang === "bn"
                ? `<i class="fa-solid fa-star"></i> শীর্ষ বিশেষজ্ঞ`
                : `<i class="fa-solid fa-star"></i> Top Specialist`;
        }
        
        const expLabel = currentLang === "bn" ? "অভিজ্ঞতা" : "Exp";
        const feeSub = currentLang === "bn" ? "/ কনসালটেশন" : "/ Consultation";
        const bookBtnText = currentLang === "bn" ? "অ্যাপয়েন্টমেন্ট বুক করুন" : "Book Doctor";
        const avatarImg = getDoctorAvatarHTML(topDoc.avatar);
        
        predDocCardInner.innerHTML = `
            <div class="pred-doc-card-body">
                <div class="pred-doc-avatar-wrapper">
                    <div class="pred-doc-avatar">${avatarImg}</div>
                    <span class="pred-doc-status ${topDoc.available_today ? 'online' : 'offline'}"></span>
                </div>
                <div class="pred-doc-info">
                    <div class="pred-doc-rank-row">
                        <span class="pred-doc-rank-badge"><i class="fa-solid fa-award"></i> ${rankText}</span>
                        <span class="pred-doc-rating"><i class="fa-solid fa-star" style="color: #F59E0B;"></i> <strong>${topDoc.rating}</strong> (${topDoc.reviews})</span>
                    </div>
                    <h3 class="pred-doc-name">${name}</h3>
                    <div class="pred-doc-title">${topDoc.title}</div>
                    <div class="pred-doc-degrees">${topDoc.degrees}</div>
                    <div class="pred-doc-meta-row">
                        <span><i class="fa-solid fa-briefcase-medical"></i> ${topDoc.experience} ${expLabel}</span>
                        <span><i class="fa-solid fa-door-open"></i> ${topDoc.room}</span>
                        <span><i class="fa-regular fa-clock"></i> ${topDoc.days}</span>
                    </div>
                </div>
            </div>
            <div class="pred-doc-footer">
                <div class="pred-doc-fee">
                    <span class="fee-val">${topDoc.fee}</span>
                    <span class="fee-sub">${feeSub}</span>
                </div>
                <button class="btn btn-primary btn-sm pred-doc-book-btn" onclick="openAppointmentModalForDoctor('${topDoc.id}', '${name}', '${topDoc.department}')">
                    <i class="fa-regular fa-calendar-check"></i> ${bookBtnText}
                </button>
            </div>
        `;
    }

    // Render Probabilities
    if (probBarsContainer) {
        probBarsContainer.innerHTML = "";
        if (data.top_3_recommendations) {
            data.top_3_recommendations.forEach((item) => {
                const label = currentLang === "bn" ? (item.department_bn || item.department) : item.department;
                const probItem = document.createElement("div");
                probItem.classList.add("prob-item");
                probItem.innerHTML = `
                    <div class="prob-header">
                        <span>${label}</span>
                        <strong>${item.confidence_percentage}%</strong>
                    </div>
                    <div class="prob-bar-track">
                        <div class="prob-bar-fill" style="width: 0%"></div>
                    </div>
                `;
                probBarsContainer.appendChild(probItem);

                setTimeout(() => {
                    const fill = probItem.querySelector(".prob-bar-fill");
                    if (fill) fill.style.width = `${item.confidence_percentage}%`;
                }, 100);
            });
        }
    }

    // Render Recommended Specialist Doctors in Separate Full-Width Section
    const recGrid = document.getElementById("aiRecDoctorsGrid");
    const recDeptHighlight = document.getElementById("aiRecDeptHighlight");

    if (recSection && recGrid) {
        recGrid.innerHTML = "";
        const deptName = currentLang === "bn" ? (data.recommended_department_bn || data.recommended_department) : data.recommended_department;
        if (recDeptHighlight) recDeptHighlight.innerText = deptName;

        if (!recDocs.length) {
            recGrid.innerHTML = `<p class="rec-empty-msg" style="grid-column: 1/-1;">${currentLang === "bn" ? "এই মুহূর্তে সরাসরি ডাক্তার তালিকা পাওয়া যায়নি।" : "No specialized doctors currently found for this department."}</p>`;
        } else {
            recDocs.forEach((doc, idx) => {
                const name = currentLang === "bn" ? (doc.name_bn || doc.name) : doc.name;
                const rankText = currentLang === "bn" ? (doc.rank_badge_bn || doc.rank_badge || "বিশেষজ্ঞ ডাক্তার") : (doc.rank_badge || "Specialist Doctor");
                const isTopMatch = idx === 0;
                const matchBadgeClass = isTopMatch ? "rec-match-pill top" : "rec-match-pill";
                const matchBadgeText = isTopMatch 
                    ? (currentLang === "bn" ? `★ শীর্ষ বাছাই` : `★ Top Pick`)
                    : (currentLang === "bn" ? `সুপারিশকৃত বিশেষজ্ঞ` : `Recommended Specialist`);
                const expLabel = currentLang === "bn" ? "অভিজ্ঞতা" : "Exp";
                const chamberStatus = doc.available_today 
                    ? (currentLang === "bn" ? "● চেম্বার খোলা" : "● Chamber Open") 
                    : (currentLang === "bn" ? "অফলাইন" : "Offline");
                const bookBtnText = currentLang === "bn" ? "সরাসরি বুকিং নিন" : "Book Appointment";
                const avatarImg = getDoctorAvatarHTML(doc.avatar);
                
                const card = document.createElement("div");
                card.className = `ai-rec-doctor-card ${isTopMatch ? 'highlight-top' : ''}`;
                card.innerHTML = `
                    <div class="rec-card-top">
                        <div class="rec-badges-row">
                            <span class="${matchBadgeClass}"><i class="fa-solid fa-star"></i> ${matchBadgeText}</span>
                            <span class="rec-rank-pill"><i class="fa-solid fa-award"></i> ${rankText}</span>
                        </div>
                        <span class="rec-status-badge ${doc.available_today ? 'open' : 'closed'}">${chamberStatus}</span>
                    </div>

                    <div class="rec-card-body">
                        <div class="rec-avatar-col">
                            <div class="rec-avatar-circle">${avatarImg}</div>
                        </div>
                        <div class="rec-info-col">
                            <h4 class="rec-doc-name">${name}</h4>
                            <div class="rec-doc-title">${doc.title}</div>
                            <div class="rec-doc-degrees">${doc.degrees}</div>
                            
                            <div class="rec-doc-meta">
                                <span><i class="fa-solid fa-star" style="color: #F59E0B;"></i> <strong>${doc.rating}</strong> (${doc.reviews})</span>
                                <span><i class="fa-solid fa-briefcase-medical"></i> ${doc.experience} ${expLabel}</span>
                                <span><i class="fa-solid fa-door-open"></i> ${doc.room}</span>
                                <span><i class="fa-regular fa-clock"></i> ${doc.days}</span>
                            </div>
                        </div>
                    </div>

                    <div class="rec-card-footer">
                        <div class="rec-fee-tag">
                            <span class="rec-fee-amount">${doc.fee}</span>
                            <span class="rec-fee-label">${currentLang === "bn" ? "/ কনসালটেশন" : "/ Consultation"}</span>
                        </div>
                        <button class="btn btn-primary btn-sm rec-book-btn" onclick="openAppointmentModalForDoctor('${doc.id}', '${name}', '${doc.department}')">
                            <i class="fa-regular fa-calendar-check"></i> ${bookBtnText}
                        </button>
                    </div>
                `;
                recGrid.appendChild(card);
            });
        }

        recSection.style.display = "block";
    }
}

/* =============================================================================
   7. DOCTORS DIRECTORY & DEPARTMENT TABS
   ============================================================================= */
async function fetchDoctors(deptKey = "all") {
    const grid = document.getElementById("doctorsGrid");
    if (!grid) return;

    grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding: 2rem; color: var(--text-muted);">
        <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; color: var(--primary);"></i>
        <p style="margin-top: 0.8rem;">${currentLang === "bn" ? "শীর্ষ বিশেষজ্ঞ ডাক্তারদের তথ্য লোড হচ্ছে..." : "Loading Featured Specialists..."}</p>
    </div>`;

    try {
        const url = deptKey === "all" ? "/api/doctors?featured=true" : `/api/doctors?department=${deptKey}`;
        const res = await fetch(url);
        doctorsData = await res.json();
        renderDoctorsGrid(doctorsData);
    } catch (e) {
        console.error("Error fetching doctors:", e);
        grid.innerHTML = `<p style="grid-column: 1/-1; text-align:center; color: var(--emergency-red);">Failed to load doctor directory.</p>`;
    }
}

function renderDoctorsGrid(doctors) {
    const grid = document.getElementById("doctorsGrid");
    if (!grid) return;

    grid.innerHTML = "";
    if (!doctors.length) {
        const emptyMsg = currentLang === "bn"
            ? "এই বিভাগে বর্তমানে কোনো ডাক্তার পাওয়া যায়নি।"
            : "No doctors found in this department.";
        grid.innerHTML = `<p style="grid-column: 1/-1; text-align:center; color: var(--text-muted); padding: 2rem;">${emptyMsg}</p>`;
        return;
    }

    doctors.forEach((doc) => {
        const name = currentLang === "bn" ? (doc.name_bn || doc.name) : doc.name;
        const availableText = currentLang === "bn"
            ? (doc.available_today ? "● চেম্বার খোলা" : "অফলাইন")
            : (doc.available_today ? "● Chamber Active" : "Offline");
        const expLabel = currentLang === "bn" ? "অভিজ্ঞতা" : "Exp";
        const feeSub = currentLang === "bn" ? "/ কনসালটেশন" : "/ Consultation";
        const bookBtnText = currentLang === "bn" ? "বুকিং" : "Book";
        const avatarImg = getDoctorAvatarHTML(doc.avatar);

        const card = document.createElement("div");
        card.classList.add("doctor-card");
        card.innerHTML = `
            <div class="doc-badge-status">${availableText}</div>
            <div class="doc-avatar-wrapper">${avatarImg}</div>
            <h3 class="doc-name">${name}</h3>
            <div class="doc-title">${doc.title}</div>
            <div class="doc-degrees">${doc.degrees}</div>

            <div class="doc-meta-list">
                <div><i class="fa-solid fa-door-open"></i> <span>${doc.room}</span></div>
                <div><i class="fa-regular fa-clock"></i> <span>${doc.days}</span></div>
                <div><i class="fa-solid fa-star" style="color: #F59E0B;"></i> <span>${doc.rating} (${doc.reviews}) | ${doc.experience} ${expLabel}</span></div>
            </div>

            <div class="doc-footer">
                <div class="doc-fee">${doc.fee} <span>${feeSub}</span></div>
                <button class="btn btn-primary btn-sm" onclick="openAppointmentModalForDoctor('${doc.id}', '${name}', '${doc.department}')">
                    <i class="fa-regular fa-calendar-check"></i> ${bookBtnText}
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function initDeptTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");
            const dept = tab.getAttribute("data-dept");
            fetchDoctors(dept);
        });
    });
}

function filterDeptAndScroll(deptKey) {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach((tab) => {
        if (tab.getAttribute("data-dept") === deptKey) {
            tab.click();
        }
    });
    const section = document.getElementById("doctors");
    if (section) section.scrollIntoView({ behavior: "smooth" });
}

/* =============================================================================
   7. HOSPITAL FACILITIES
   ============================================================================= */
async function fetchFacilities() {
    const grid = document.getElementById("facilitiesGrid");
    if (!grid) return;

    try {
        const res = await fetch("/api/facilities");
        const facilities = await res.json();
        grid.innerHTML = "";

        facilities.forEach((fac) => {
            const title = currentLang === "bn" ? (fac.title_bn || fac.title) : fac.title;
            const card = document.createElement("div");
            card.classList.add("facility-card");
            card.innerHTML = `
                <div class="facility-badge">${fac.badge}</div>
                <span class="facility-icon">${fac.icon}</span>
                <h3 class="facility-title">${title}</h3>
                <p class="facility-desc">${fac.desc}</p>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Error fetching facilities:", e);
    }
}

/* =============================================================================
   8. APPOINTMENT BOOKING MODAL (Guarded by Google Sign-In)
   ============================================================================= */
function openAppointmentModal(deptName = null, docName = null) {
    if (!currentGoogleUser) {
        openSignInPrompt(() => openAppointmentModal(deptName, docName));
        return;
    }

    const modal = document.getElementById("appointmentModal");
    if (modal) {
        // Pre-fill patient name if available from Google
        const nameInput = document.getElementById("patientName");
        if (nameInput && currentGoogleUser.name && !nameInput.value) {
            nameInput.value = currentGoogleUser.name;
        }

        if (deptName) {
            const deptSelect = document.getElementById("modalDeptSelect");
            if (deptSelect) {
                for (let i = 0; i < deptSelect.options.length; i++) {
                    if (deptSelect.options[i].value.toLowerCase().includes(deptName.toLowerCase()) || deptName.toLowerCase().includes(deptSelect.options[i].value.toLowerCase())) {
                        deptSelect.selectedIndex = i;
                        break;
                    }
                }
            }
        }

        updateModalDoctorOptions(docName);
        modal.classList.add("open");
    }
}

function closeAppointmentModal() {
    const modal = document.getElementById("appointmentModal");
    if (modal) modal.classList.remove("open");
}

function openAppointmentModalForDoctor(docId, docName, dept) {
    openAppointmentModal(dept, docName);
}

function bookWithPredictedDept() {
    if (!lastPredictionResult) return;
    const dept = lastPredictionResult.recommended_department;
    openAppointmentModal(dept);
    const symptomsInput = document.getElementById("modalSymptoms");
    const mainInput = document.getElementById("symptomInput");
    if (symptomsInput && mainInput) {
        symptomsInput.value = mainInput.value;
    }
}

function updateModalDoctorOptions(selectedDocName = null) {
    const deptSelect = document.getElementById("modalDeptSelect");
    const docSelect = document.getElementById("modalDoctorSelect");
    if (!deptSelect || !docSelect) return;

    const currentDept = deptSelect.value;
    docSelect.innerHTML = "";

    const matchedDoctors = doctorsData.filter(d => 
        d.department.toLowerCase().includes(currentDept.toLowerCase()) || currentDept.toLowerCase().includes(d.department.toLowerCase())
    );

    if (matchedDoctors.length) {
        matchedDoctors.forEach(doc => {
            const name = currentLang === "bn" ? (doc.name_bn || doc.name) : doc.name;
            const opt = document.createElement("option");
            opt.value = name;
            opt.innerText = `${name} (${doc.degrees.split(",")[0]})`;
            if (selectedDocName && opt.value.includes(selectedDocName)) opt.selected = true;
            docSelect.appendChild(opt);
        });
    } else {
        const opt = document.createElement("option");
        opt.value = "Available Specialist Doctor";
        opt.innerText = currentLang === "bn" ? "উপযুক্ত অন-কল বিশেষজ্ঞ ডাক্তার" : "Available On-Call Specialist";
        docSelect.appendChild(opt);
    }
}

function setDefaultAppointmentDate() {
    const dateInput = document.getElementById("appointmentDate");
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split("T")[0];
        dateInput.min = new Date().toISOString().split("T")[0];
    }
}

async function submitAppointment(event) {
    event.preventDefault();
    const patientName = document.getElementById("patientName").value;
    const patientPhone = document.getElementById("patientPhone").value;
    const patientAge = document.getElementById("patientAge").value;
    const department = document.getElementById("modalDeptSelect").value;
    const doctorName = document.getElementById("modalDoctorSelect").value;
    const date = document.getElementById("appointmentDate").value;
    const symptoms = document.getElementById("modalSymptoms").value;

    const payload = {
        patient_name: patientName,
        patient_phone: patientPhone,
        patient_age: patientAge,
        department: department,
        doctor_name: doctorName,
        preferred_date: date,
        symptoms: symptoms,
        user_email: currentGoogleUser ? currentGoogleUser.email : ""
    };

    try {
        const res = await fetch("/api/book-appointment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        closeAppointmentModal();
        showConfirmationModal(result);
        if (currentGoogleUser) {
            loadUserAppointments();
        }
    } catch (e) {
        console.error("Booking error:", e);
        alert(currentLang === "bn" ? "বুকিং করতে সমস্যা হয়েছে।" : "Booking failed. Please try again.");
    }
}

function showConfirmationModal(result) {
    const confirmModal = document.getElementById("confirmationModal");
    const ticketId = document.getElementById("confirmTicketId");
    const detailsBox = document.getElementById("confirmDetailsBox");

    if (ticketId) ticketId.innerText = result.ticket_id;
    if (detailsBox) {
        if (currentLang === "bn") {
            detailsBox.innerHTML = `
                <p><strong>রোগীর নাম:</strong> ${result.patient_name}</p>
                <p><strong>মোবাইল:</strong> ${result.phone}</p>
                <p><strong>বিভাগ:</strong> ${result.department}</p>
                <p><strong>ডাক্তার:</strong> ${result.doctor_name}</p>
                <p><strong>তারিখ:</strong> ${result.date}</p>
            `;
        } else {
            detailsBox.innerHTML = `
                <p><strong>Patient Name:</strong> ${result.patient_name}</p>
                <p><strong>Phone:</strong> ${result.phone}</p>
                <p><strong>Department:</strong> ${result.department}</p>
                <p><strong>Doctor:</strong> ${result.doctor_name}</p>
                <p><strong>Appointment Date:</strong> ${result.date}</p>
            `;
        }
    }
    if (confirmModal) confirmModal.classList.add("open");
}

function closeConfirmationModal() {
    const confirmModal = document.getElementById("confirmationModal");
    if (confirmModal) confirmModal.classList.remove("open");
}

/* =============================================================================
   9. 100% RELIABLE BACKEND PDF GENERATOR (REPORTLAB STREAMING)
   ============================================================================= */
async function downloadReferralSlipPDF() {
    if (!lastPredictionResult) {
        alert(currentLang === "bn" ? "আগে লক্ষণ লিখে এআই দিয়ে বিশ্লেষণ করুন।" : "Please analyze symptoms first.");
        return;
    }

    const btn = document.getElementById("downloadSlipBtn");
    const originalHtml = btn ? btn.innerHTML : "";
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>${currentLang === "bn" ? "PDF তৈরি হচ্ছে..." : "Generating PDF..."}</span>`;
    }

    try {
        const payload = {
            prediction_result: lastPredictionResult,
            language: currentLang,
            patient_name: currentGoogleUser ? (currentGoogleUser.name || "") : "",
            patient_email: currentGoogleUser ? (currentGoogleUser.email || "") : "",
            patient_id: currentGoogleUser ? (currentGoogleUser.id || "") : ""
        };

        const response = await fetch("/api/generate-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`PDF generation failed with status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        const randomId = Math.floor(100000 + Math.random() * 900000);
        a.download = `ProHealth_Referral_Ticket_${randomId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (err) {
        console.error("PDF Download Error:", err);
        alert(currentLang === "bn" ? "PDF তৈরিতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।" : "Failed to generate PDF. Please try again.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }
    }
}

/* =============================================================================
   10. LIGHT / DARK THEME TOGGLE
   ============================================================================= */
function toggleTheme() {
    const htmlEl = document.documentElement;
    const themeBtn = document.getElementById("themeToggleBtn");
    if (htmlEl.getAttribute("data-theme") === "light") {
        htmlEl.removeAttribute("data-theme");
        if (themeBtn) themeBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
    } else {
        htmlEl.setAttribute("data-theme", "light");
        if (themeBtn) themeBtn.innerHTML = '<i class="fa-solid fa-sun" style="color: #F59E0B;"></i>';
    }
}
