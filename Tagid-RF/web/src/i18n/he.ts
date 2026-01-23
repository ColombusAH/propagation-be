// Hebrew translations
import type { TranslationKeys } from './en';

export const he: TranslationKeys = {
    // Common
    app: {
        name: 'Tagid RF',
        title: 'מערכת ניהול RFID',
        logout: 'יציאה',
    },

    // Navigation
    nav: {
        scan: 'סריקה',
        catalog: 'קטלוג',
        cart: 'עגלה',
        orders: 'הזמנות',
        transactions: 'טרנזקציות',
        qrGenerator: 'יצירת QR',
        containers: 'מיכלים',
        tagMapping: 'סנכרון תגיות',
        admin: 'ניהול',
        // New Sidebar Items
        dashboard: 'סקירה כללית',
        main: 'ראשי',
        shopping: 'קניות',
        tagManagement: 'ניהול תגים',
        operations: 'תפעול',
        settings: 'הגדרות',
        readers: 'קוראים',
        general: 'כללי',
        users: 'משתמשים',
        tagScanner: 'סריקה',
        tagLinking: 'צימוד',
        tubs: 'אמבטים',
        exitGate: 'שער יציאה',
        bathSetup: 'אמבטים',
    },

    // Scan Page
    scan: {
        title: 'סרוק ברקוד או קוד QR',
        cameraUnavailable: 'המצלמה לא זמינה',
        manualEntry: 'הזנה ידנית',
        placeholder: 'הזן ברקוד או קוד QR ידנית...',
        add: 'הוסף',
        browseCatalog: 'עיין בקטלוג',
        productAdded: '{product} נוסף לעגלה',
        productNotFound: 'המוצר לא נמצא',
        barcodeNotRecognized: 'הברקוד לא מזוהה במערכת',
        containerAdded: 'נוספו {count} מוצרים מהמיכל',
        containerFound: 'מיכל: {container}',
        containerEmpty: 'מיכל ריק',
        containerEmptyMessage: 'המיכל לא מכיל מוצרים',
        productFound: 'מוצר נוסף',
        product: 'מוצר',
    },

    // Catalog Page
    catalog: {
        title: 'קטלוג מוצרים',
        searchPlaceholder: 'חיפוש מוצרים...',
        noProducts: 'לא נמצאו מוצרים',
        addToCart: 'הוסף לעגלה',
    },

    // Cart Page
    cart: {
        title: 'עגלת קניות',
        empty: 'העגלה ריקה',
        emptyMessage: 'סרוק מוצרים או עיין בקטלוג להוספת פריטים.',
        total: 'סה"כ',
        checkout: 'המשך לתשלום',
        remove: 'הסר',
        continueShopping: 'המשך בקניות',
    },

    // Checkout Page
    checkout: {
        title: 'תשלום',
        customerInfo: 'פרטי לקוח',
        name: 'שם',
        email: 'אימייל',
        notes: 'הערות (אופציונלי)',
        paymentMethod: 'אמצעי תשלום',
        orderSummary: 'סיכום הזמנה',
        items: 'פריטים',
        subtotal: 'סכום ביניים',
        tax: 'מע"מ',
        total: 'סה"כ',
        payNow: 'שלם עכשיו',
        processing: 'מעבד...',
    },

    // Orders Page
    orders: {
        title: 'היסטוריית הזמנות',
        empty: 'אין הזמנות עדיין',
        emptyMessage: 'ההזמנות המושלמות שלך יופיעו כאן.',
        orderNumber: 'הזמנה',
        status: 'סטטוס',
        paid: 'שולם',
        date: 'תאריך',
    },

    // QR Generator
    qr: {
        title: 'יצירת קוד QR',
        inputLabel: 'הזן טקסט או קוד',
        inputPlaceholder: 'הזן מחרוזת להמרה ל-QR...',
        generate: 'צור QR',
        download: 'הורד',
        print: 'הדפס',
        size: 'גודל',
        type: 'סוג',
        typeProduct: 'מוצר',
        typeContainer: 'מיכל',
        typeCustom: 'מותאם אישית',
    },

    // Containers
    containers: {
        title: 'מיכלים',
        create: 'צור מיכל',
        name: 'שם המיכל',
        barcode: 'ברקוד המיכל',
        products: 'מוצרים',
        addProduct: 'הוסף מוצר',
        removeProduct: 'הסר',
        empty: 'אין מיכלים עדיין',
        generateQR: 'צור QR',
    },

    // Currency
    currency: {
        ils: '₪ (שקל)',
        usd: '$ (דולר)',
        eur: '€ (יורו)',
    },

    // Banks
    banks: {
        leumi: 'בנק לאומי',
        hapoalim: 'בנק הפועלים',
        discount: 'בנק דיסקונט',
        mizrahi: 'בנק מזרחי טפחות',
        fibi: 'הבנק הבינלאומי',
        mercantile: 'בנק מרכנתיל',
        otsar: 'בנק אוצר החייל',
        igud: 'בנק איגוד',
        yahav: 'בנק יהב',
        massad: 'בנק מסד',
    },

    // Language
    language: {
        he: 'עברית',
        en: 'English',
    },

    // Dashboard
    dashboard: {
        title: 'דשבורד מכירות',
        subtitle: 'סקירה כללית של העסק שלך',
        revenue: 'הכנסות היום',
        sales: 'מכירות',
        items: 'פריטים נמכרו',
        avgTransaction: 'ממוצע טרנזקציה',
        recentTransactions: 'טרנזקציות אחרונות',
        fromLastWeek: 'מהשבוע שעבר',
        logout: 'התנתק',
    },

    // Settings
    settings: {
        title: 'הגדרות',
        subtitle: 'נהל את ההעדפות והאפשרויות שלך',
        general: 'הגדרות כלליות',
        language: 'שפה',
        languageDesc: 'בחר את שפת הממשק (עברית ⇄ English)',
        currency: 'מטבע',
        currencyDesc: 'בחר את המטבע המועדף',
        darkMode: 'מצב כהה',
        darkModeDesc: 'החלף בין מצב בהיר לכהה (בפיתוח)',
        notifications: 'התראות',
        notificationsDesc: 'קבל התראות על פעילות חשובה',
        notificationsPush: 'התראות פוש (Push)',
        notificationsPushDesc: 'קבל התראות ישירות לדפדפן או לנייד',
        notificationsSms: 'התראות SMS',
        notificationsSmsDesc: 'קבל עדכונים חשובים בהודעת טקסט',
        notificationsEmail: 'התראות אימייל (Email)',
        notificationsEmailDesc: 'קבל דוחות וסיכומי פעילות לתיבת הדואר',
        receipts: 'הגדרות קבלות',
        autoPrint: 'הדפסה אוטומטית',
        autoPrintDesc: 'הדפס קבלה אוטומטית לאחר כל עסקה (בפיתוח)',
        reports: 'הגדרות דוחות',
        reportFormat: 'פורמט דוח',
        reportFormatDesc: 'בחר פורמט ברירת מחדל לייצוא דוחות (בפיתוח)',
        system: 'הגדרות מערכת',
        userManagement: 'ניהול משתמשים',
        userManagementDesc: 'הוסף, ערוך או הסר משתמשים מהמערכת (בפיתוח)',
        manageUsers: 'נהל משתמשים',
        backup: 'גיבוי מערכת',
        backupDesc: 'צור גיבוי של כל נתוני המערכת (בפיתוח)',
        createBackup: 'צור גיבוי',
        account: 'פרטי חשבון',
        currentRole: 'תפקיד נוכחי',
        roleDesc: 'רמת ההרשאה שלך במערכת',
        saveSettings: 'שמור הגדרות',
        settingsSaved: 'הגדרות נשמרו בהצלחה!',

        // Network Settings
        networkDetails: 'פרטי הרשת',
        networkProfileCompletion: 'השלמת פרופיל הרשת',
        missingFields: 'חסרים:',
        networkName: 'שם הרשת',
        networkNameDesc: 'שם רשת החנויות שלך',
        networkLogo: 'לוגו הרשת',
        networkLogoDesc: 'העלה את הלוגו של הרשת (PNG, JPG)',
        uploadLogo: 'העלה לוגו',
        deleteLogo: 'מחק לוגו',
        businessId: 'ח.פ / מספר עוסק',
        businessIdDesc: 'מספר הזיהוי העסקי שלך (9 ספרות)',
        contactDetails: 'פרטי קשר',
        phone: 'טלפון',
        phoneDesc: 'מספר הטלפון הראשי של הרשת',
        email: 'דוא"ל',
        emailDesc: 'כתובת האימייל הראשית',
        address: 'כתובת',
        addressDesc: 'כתובת המשרד הראשי',
        website: 'אתר אינטרנט',
        websiteDesc: 'כתובת האתר של הרשת',
        bankDetails: 'פרטי בנק',
        bankName: 'שם הבנק',
        bankNameDesc: 'הבנק בו מנוהל חשבון העסק',
        bankBranch: 'מספר סניף',
        bankBranchDesc: 'מספר הסניף של הבנק (3 ספרות)',
        bankAccount: 'מספר חשבון',
        bankAccountDesc: 'מספר חשבון הבנק של העסק',

        // Placeholders & Fields
        networkNamePlaceholder: 'לדוגמה: רשת סופר-פארם',
        businessIdPlaceholder: '000000000',
        phonePlaceholder: '03-1234567',
        emailPlaceholder: 'info@company.co.il',
        addressPlaceholder: 'רחוב הרצל 1, תל אביב',
        websitePlaceholder: 'https://www.example.co.il',
        bankPlaceholder: 'בחר בנק...',
        bankBranchPlaceholder: '000',
        bankAccountPlaceholder: '000000000',
    },

    // Roles
    roles: {
        superAdmin: 'מנהל על',
        networkAdmin: 'מנהל רשת',
        storeManager: 'מנהל חנות',
        seller: 'מוכר',
        customer: 'לקוח',
    },

    // Common actions
    actions: {
        save: 'שמור',
        cancel: 'ביטול',
        delete: 'מחק',
        edit: 'ערוך',
        close: 'סגור',
        back: 'חזרה',
        next: 'הבא',
        confirm: 'אישור',
        loading: 'טוען...',
    },

    // Errors
    errors: {
        generic: 'משהו השתבש',
        notFound: 'לא נמצא',
        networkError: 'שגיאת רשת',
        cameraPermission: 'אין גישה למצלמה. אנא אפשר גישה למצלמה בהגדרות הדפדפן.',
        scanError: 'שגיאת סריקה',
        manualEntry: 'הזנה ידנית',
    },
};
