/**
 * Sahakar Mandal - Language Translations
 * Marathi/Hindi and English translations
 */

const translations = {
    en: {
        // Common
        home: 'Home',
        about: 'About',
        contact: 'Contact',
        login: 'Login',
        signup: 'Sign Up',
        logout: 'Logout',
        dashboard: 'Dashboard',
        settings: 'Settings',
        profile: 'Profile',
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        add: 'Add',
        search: 'Search',
        filter: 'Filter',
        export: 'Export',
        import: 'Import',
        close: 'Close',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        warning: 'Warning',
        info: 'Info',
        
        // Navigation
        donations: 'Donations',
        receipts: 'Receipts',
        expenses: 'Expenses',
        events: 'Events',
        gallery: 'Gallery',
        members: 'Members',
        inventory: 'Inventory',
        reports: 'Reports',
        analytics: 'Analytics',
        
        // Donation
        donationAmount: 'Donation Amount',
        donationType: 'Donation Type',
        donorName: 'Donor Name',
        donorEmail: 'Donor Email',
        donorPhone: 'Donor Phone',
        purpose: 'Purpose',
        status: 'Status',
        date: 'Date',
        
        // Payment
        payment: 'Payment',
        paymentMethod: 'Payment Method',
        paymentStatus: 'Payment Status',
        onlinePayment: 'Online Payment',
        upiPayment: 'UPI Payment',
        cardPayment: 'Card Payment',
        
        // Receipt
        receipt: 'Receipt',
        receiptId: 'Receipt ID',
        receiptDate: 'Receipt Date',
        downloadPdf: 'Download PDF',
        printReceipt: 'Print Receipt',
        shareReceipt: 'Share Receipt',
        
        // Event
        eventName: 'Event Name',
        eventDate: 'Event Date',
        eventLocation: 'Event Location',
        eventDescription: 'Event Description',
        upcomingEvents: 'Upcoming Events',
        
        // User
        userName: 'User Name',
        userEmail: 'User Email',
        userPhone: 'User Phone',
        userRole: 'User Role',
        
        // Dashboard
        totalDonations: 'Total Donations',
        totalExpenses: 'Total Expenses',
        balance: 'Balance',
        topDonors: 'Top Donors',
        recentActivity: 'Recent Activity',
        
        // Forms
        requiredField: 'This field is required',
        invalidEmail: 'Please enter a valid email',
        passwordMismatch: 'Passwords do not match',
        passwordWeak: 'Password is too weak',
        
        // Messages
        confirmDelete: 'Are you sure you want to delete this item?',
        operationSuccess: 'Operation completed successfully',
        operationFailed: 'Operation failed. Please try again.',
        networkError: 'Network error. Please check your connection.',
        sessionExpired: 'Your session has expired. Please login again.',
        
        // Roles
        admin: 'Administrator',
        finance: 'Finance Team',
        collection: 'Collection Team',
        event: 'Event Team',
        volunteer: 'Volunteer',
    },
    
    hi: {
        // Common
        home: 'घर',
        about: 'परिचय',
        contact: 'संपर्क करें',
        login: 'लॉगिन करें',
        signup: 'खाता बनाएं',
        logout: 'लॉगआउट',
        dashboard: 'डैशबोर्ड',
        settings: 'सेटिंग्स',
        profile: 'प्रोफाइल',
        save: 'सहेजें',
        cancel: 'रद्द करें',
        delete: 'हटाएं',
        edit: 'संपादित करें',
        add: 'जोड़ें',
        search: 'खोजें',
        filter: 'फ़िल्टर',
        export: 'निर्यात',
        import: 'आयात',
        close: 'बंद करें',
        loading: 'लोड हो रहा है...',
        error: 'त्रुटि',
        success: 'सफल',
        warning: 'चेतावनी',
        info: 'जानकारी',
        
        // Navigation
        donations: 'दान',
        receipts: 'रसीदें',
        expenses: 'खर्च',
        events: 'कार्यक्रम',
        gallery: 'गैलरी',
        members: 'सदस्य',
        inventory: 'इन्वेंटरी',
        reports: 'रिपोर्ट',
        analytics: 'विश्लेषण',
        
        // Donation
        donationAmount: 'दान राशि',
        donationType: 'दान का प्रकार',
        donorName: 'दानकर्ता का नाम',
        donorEmail: 'दानकर्ता का ईमेल',
        donorPhone: 'दानकर्ता का फोन',
        purpose: 'उद्देश्य',
        status: 'स्थिति',
        date: 'तारीख',
        
        // Payment
        payment: 'भुगतान',
        paymentMethod: 'भुगतान विधि',
        paymentStatus: 'भुगतान स्थिति',
        onlinePayment: 'ऑनलाइन भुगतान',
        upiPayment: 'UPI भुगतान',
        cardPayment: 'कार्ड भुगतान',
        
        // Receipt
        receipt: 'रसीद',
        receiptId: 'रसीद आईडी',
        receiptDate: 'रसीद की तारीख',
        downloadPdf: 'PDF डाउनलोड करें',
        printReceipt: 'रसीद प्रिंट करें',
        shareReceipt: 'रसीद साझा करें',
        
        // Event
        eventName: 'कार्यक्रम का नाम',
        eventDate: 'कार्यक्रम की तारीख',
        eventLocation: 'कार्यक्रम का स्थान',
        eventDescription: 'कार्यक्रम विवरण',
        upcomingEvents: 'आने वाले कार्यक्रम',
        
        // User
        userName: 'उपयोगकर्ता नाम',
        userEmail: 'उपयोगकर्ता ईमेल',
        userPhone: 'उपयोगकर्ता फोन',
        userRole: 'उपयोगकर्ता भूमिका',
        
        // Dashboard
        totalDonations: 'कुल दान',
        totalExpenses: 'कुल खर्च',
        balance: 'शेष',
        topDonors: 'शीर्ष दानकर्ता',
        recentActivity: 'हाल की गतिविधि',
        
        // Forms
        requiredField: 'यह क्षेत्र आवश्यक है',
        invalidEmail: 'कृपया एक वैध ईमेल दर्ज करें',
        passwordMismatch: 'पासवर्ड मेल नहीं खाते',
        passwordWeak: 'पासवर्ड बहुत कमजोर है',
        
        // Messages
        confirmDelete: 'क्या आप वाकई इस आइटम को हटाना चाहते हैं?',
        operationSuccess: 'ऑपरेशन सफलतापूर्वक पूरा हुआ',
        operationFailed: 'ऑपरेशन विफल। कृपया फिर से प्रयास करें।',
        networkError: 'नेटवर्क त्रुटि। कृपया अपने कनेक्शन की जांच करें।',
        sessionExpired: 'आपका सत्र समाप्त हो गया। कृपया फिर से लॉगिन करें।',
        
        // Roles
        admin: 'प्रशासक',
        finance: 'वित्त टीम',
        collection: 'संग्रह टीम',
        event: 'कार्यक्रम टीम',
        volunteer: 'स्वयंसेवक',
    }
};

/**
 * Get translation
 */
function t(key, lang = null) {
    if (!lang) {
        lang = localStorage.getItem('language') || 'en';
    }
    
    return translations[lang]?.[key] || translations['en']?.[key] || key;
}

/**
 * Get all translations for a language
 */
function getTranslations(lang = 'en') {
    return translations[lang] || translations['en'];
}

/**
 * Set language
 */
function setLanguage(lang) {
    if (translations[lang]) {
        localStorage.setItem('language', lang);
        return true;
    }
    return false;
}

/**
 * Get current language
 */
function getCurrentLanguage() {
    return localStorage.getItem('language') || 'en';
}
