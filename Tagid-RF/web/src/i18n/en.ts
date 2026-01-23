// English translations
export const en = {
    // Common
    app: {
        name: 'Tagid RF',
        title: 'RFID Management System',
        logout: 'Logout',
    },

    // Navigation
    nav: {
        scan: 'Scan',
        catalog: 'Catalog',
        cart: 'Cart',
        orders: 'Orders',
        transactions: 'Transactions',
        qrGenerator: 'QR Generator',
        containers: 'Containers',
        tagMapping: 'Tag Sync',
        admin: 'Admin',
        // New Sidebar Items
        dashboard: 'Dashboard',
        main: 'Main',
        shopping: 'Shopping',
        tagManagement: 'Tag Management',
        operations: 'Operations',
        settings: 'Settings',
        readers: 'Readers',
        general: 'General',
        users: 'Users',
        tagScanner: 'Scanner',
        tagLinking: 'Linking',
        tubs: 'Tubs',
        exitGate: 'Exit Gate',
        bathSetup: 'Bath Setup',
    },

    // Scan Page
    scan: {
        title: 'Scan Barcode or QR Code',
        cameraUnavailable: 'Camera Unavailable',
        manualEntry: 'Manual Entry',
        placeholder: 'Enter barcode or QR code manually...',
        add: 'Add',
        browseCatalog: 'Browse Catalog',
        productAdded: 'Added {product} to cart',
        productNotFound: 'Product not found',
        barcodeNotRecognized: 'Barcode not recognized',
        containerAdded: 'Added {count} products from container',
        containerFound: 'Container: {container}',
        containerEmpty: 'Empty Container',
        containerEmptyMessage: 'This container has no products',
        productFound: 'Product Added',
        product: 'Product',
    },

    // Catalog Page
    catalog: {
        title: 'Product Catalog',
        searchPlaceholder: 'Search products...',
        noProducts: 'No products found',
        addToCart: 'Add to Cart',
    },

    // Cart Page
    cart: {
        title: 'Shopping Cart',
        empty: 'Your cart is empty',
        emptyMessage: 'Scan products or browse the catalog to add items.',
        total: 'Total',
        checkout: 'Proceed to Checkout',
        remove: 'Remove',
        continueShopping: 'Continue Shopping',
    },

    // Checkout Page
    checkout: {
        title: 'Checkout',
        customerInfo: 'Customer Information',
        name: 'Name',
        email: 'Email',
        notes: 'Notes (optional)',
        paymentMethod: 'Payment Method',
        orderSummary: 'Order Summary',
        items: 'items',
        subtotal: 'Subtotal',
        tax: 'Tax',
        total: 'Total',
        payNow: 'Pay Now',
        processing: 'Processing...',
    },

    // Orders Page
    orders: {
        title: 'Order History',
        empty: 'No orders yet',
        emptyMessage: 'Your completed orders will appear here.',
        orderNumber: 'Order',
        status: 'Status',
        paid: 'Paid',
        date: 'Date',
    },

    // QR Generator
    qr: {
        title: 'QR Code Generator',
        inputLabel: 'Enter text or code',
        inputPlaceholder: 'Enter string to convert to QR...',
        generate: 'Generate QR',
        download: 'Download',
        print: 'Print',
        size: 'Size',
        type: 'Type',
        typeProduct: 'Product',
        typeContainer: 'Container',
        typeCustom: 'Custom',
    },

    // Containers
    containers: {
        title: 'Containers',
        create: 'Create Container',
        name: 'Container Name',
        barcode: 'Container Barcode',
        products: 'Products',
        addProduct: 'Add Product',
        removeProduct: 'Remove',
        empty: 'No containers yet',
        generateQR: 'Generate QR',
    },

    // Currency
    currency: {
        ils: 'ILS (₪)',
        usd: 'USD ($)',
        eur: 'EUR (€)',
    },

    // Banks
    banks: {
        leumi: 'Bank Leumi',
        hapoalim: 'Bank Hapoalim',
        discount: 'Bank Discount',
        mizrahi: 'Mizrahi Tefahot Bank',
        fibi: 'The First International Bank',
        mercantile: 'Mercantile Bank',
        otsar: 'Otsar HaHayal Bank',
        igud: 'Union Bank',
        yahav: 'Bank Yahav',
        massad: 'Bank Massad',
    },

    // Language
    language: {
        he: 'עברית',
        en: 'English',
    },

    // Dashboard
    dashboard: {
        title: 'Sales Dashboard',
        subtitle: 'Overview of your business',
        revenue: 'Today\'s Revenue',
        sales: 'Sales',
        items: 'Items Sold',
        avgTransaction: 'Avg Transaction',
        recentTransactions: 'Recent Transactions',
        fromLastWeek: 'from last week',
        logout: 'Logout',
    },

    // Settings
    settings: {
        title: 'Settings',
        subtitle: 'Manage your preferences and options',
        general: 'General Settings',
        language: 'Language',
        languageDesc: 'Select interface language (Hebrew ⇄ English)',
        currency: 'Currency',
        currencyDesc: 'Select preferred currency',
        darkMode: 'Dark Mode',
        darkModeDesc: 'Switch between light and dark mode (in development)',
        notifications: 'Notifications',
        notificationsDesc: 'Receive notifications about important activity',
        notificationsPush: 'Push Notifications',
        notificationsPushDesc: 'Receive notifications directly to browser or mobile',
        notificationsSms: 'SMS Notifications',
        notificationsSmsDesc: 'Receive important updates via text message',
        notificationsEmail: 'Email Notifications',
        notificationsEmailDesc: 'Receive reports and activity summaries to email',
        receipts: 'Receipt Settings',
        autoPrint: 'Auto Print',
        autoPrintDesc: 'Automatically print receipt after each transaction (in development)',
        reports: 'Report Settings',
        reportFormat: 'Report Format',
        reportFormatDesc: 'Select default format for exporting reports (in development)',
        system: 'System Settings',
        userManagement: 'User Management',
        userManagementDesc: 'Add, edit, or remove users from the system (in development)',
        manageUsers: 'Manage Users',
        backup: 'System Backup',
        backupDesc: 'Create a backup of all system data (in development)',
        createBackup: 'Create Backup',
        account: 'Account Details',
        currentRole: 'Current Role',
        roleDesc: 'Your permission level in the system',
        saveSettings: 'Save Settings',
        settingsSaved: 'Settings saved successfully!',

        // Network Settings
        networkDetails: 'Network Details',
        networkProfileCompletion: 'Profile Completion',
        missingFields: 'Missing:',
        networkName: 'Network Name',
        networkNameDesc: 'Name of your store chain',
        networkLogo: 'Network Logo',
        networkLogoDesc: 'Upload chain logo (PNG, JPG)',
        uploadLogo: 'Upload Logo',
        deleteLogo: 'Delete Logo',
        businessId: 'Business ID',
        businessIdDesc: 'Your business identification number (9 digits)',
        contactDetails: 'Contact Details',
        phone: 'Phone',
        phoneDesc: 'Main chain phone number',
        email: 'Email',
        emailDesc: 'Main email address',
        address: 'Address',
        addressDesc: 'Head office address',
        website: 'Website',
        websiteDesc: 'Chain website URL',
        bankDetails: 'Bank Details',
        bankName: 'Bank Name',
        bankNameDesc: 'Bank where business account is managed',
        bankBranch: 'Branch Number',
        bankBranchDesc: 'Bank branch number (3 digits)',
        bankAccount: 'Account Number',
        bankAccountDesc: 'Business bank account number',

        // Placeholders & Fields
        networkNamePlaceholder: 'Example: Super Pharm Chain',
        businessIdPlaceholder: '000000000',
        phonePlaceholder: '03-1234567',
        emailPlaceholder: 'info@company.co.il',
        addressPlaceholder: '1 Herzl St, Tel Aviv',
        websitePlaceholder: 'https://www.example.com',
        bankPlaceholder: 'Select Bank...',
        bankBranchPlaceholder: '000',
        bankAccountPlaceholder: '000000000',
    },

    // Roles
    roles: {
        superAdmin: 'Super Admin',
        networkAdmin: 'Network Admin',
        storeManager: 'Store Manager',
        seller: 'Seller',
        customer: 'Customer',
    },

    // Common actions
    actions: {
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        close: 'Close',
        back: 'Back',
        next: 'Next',
        confirm: 'Confirm',
        loading: 'Loading...',
    },

    // Errors
    errors: {
        generic: 'Something went wrong',
        notFound: 'Not found',
        networkError: 'Network error',
        cameraPermission: 'Camera permission denied. Please allow camera access in your browser settings.',
        scanError: 'Scan Error',
        manualEntry: 'Manual Entry',
    },
};

export type TranslationKeys = typeof en;
