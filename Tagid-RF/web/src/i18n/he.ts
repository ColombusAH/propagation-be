// Hebrew translations
import type { TranslationKeys } from './en';

export const he: TranslationKeys = {
    // Common
    app: {
        name: 'סרוק ושלם',
    },

    // Navigation
    nav: {
        scan: 'סריקה',
        catalog: 'קטלוג',
        cart: 'עגלה',
        orders: 'הזמנות',
        qrGenerator: 'יצירת QR',
        containers: 'מיכלים',
        tagMapping: 'סנכרון תגיות',
        admin: 'ניהול',
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
        containerAdded: 'מיכל {container} נוסף לעגלה',
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

    // Language
    language: {
        he: 'עברית',
        en: 'English',
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
    },
};
