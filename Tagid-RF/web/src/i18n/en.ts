// English translations
export const en = {
    // Common
    app: {
        name: 'Scan & Pay',
    },

    // Navigation
    nav: {
        scan: 'Scan',
        catalog: 'Catalog',
        cart: 'Cart',
        orders: 'Orders',
        qrGenerator: 'QR Generator',
        containers: 'Containers',
        tagMapping: 'Tag Sync',
        admin: 'Admin',
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
        containerAdded: 'Added container {container} to cart',
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

    // Language
    language: {
        he: 'עברית',
        en: 'English',
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
    },
};

export type TranslationKeys = typeof en;
