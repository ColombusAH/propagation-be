import { StateCreator } from 'zustand';
import type { Container } from '../types';

export interface ContainerSlice {
    containers: Container[];

    // CRUD Operations
    addContainer: (container: Omit<Container, 'id' | 'createdAt' | 'updatedAt'>) => Container;
    updateContainer: (id: string, updates: Partial<Container>) => void;
    removeContainer: (id: string) => void;

    // Query Operations
    getContainerById: (id: string) => Container | undefined;
    getContainerByBarcode: (barcode: string) => Container | undefined;

    // Product Management within Container
    addProductToContainer: (containerId: string, productId: string, qty?: number) => void;
    removeProductFromContainer: (containerId: string, productId: string) => void;
    updateProductQtyInContainer: (containerId: string, productId: string, qty: number) => void;

    // Utility
    isContainer: (barcode: string) => boolean;
}

const generateId = (): string => {
    return 'container-' + Math.random().toString(36).substring(2, 11);
};

export const createContainerSlice: StateCreator<ContainerSlice> = (set, get) => ({
    containers: [],

    addContainer: (containerData) => {
        const now = new Date().toISOString();
        const newContainer: Container = {
            ...containerData,
            id: generateId(),
            createdAt: now,
            updatedAt: now,
        };

        set((state) => ({
            containers: [...state.containers, newContainer],
        }));

        return newContainer;
    },

    updateContainer: (id, updates) => {
        set((state) => ({
            containers: state.containers.map((container) =>
                container.id === id
                    ? { ...container, ...updates, updatedAt: new Date().toISOString() }
                    : container
            ),
        }));
    },

    removeContainer: (id) => {
        set((state) => ({
            containers: state.containers.filter((container) => container.id !== id),
        }));
    },

    getContainerById: (id) => {
        return get().containers.find((container) => container.id === id);
    },

    getContainerByBarcode: (barcode) => {
        return get().containers.find((container) => container.barcode === barcode);
    },

    addProductToContainer: (containerId, productId, qty = 1) => {
        set((state) => ({
            containers: state.containers.map((container) => {
                if (container.id !== containerId) return container;

                const existingProduct = container.products.find((p) => p.productId === productId);

                if (existingProduct) {
                    return {
                        ...container,
                        products: container.products.map((p) =>
                            p.productId === productId ? { ...p, qty: p.qty + qty } : p
                        ),
                        updatedAt: new Date().toISOString(),
                    };
                }

                return {
                    ...container,
                    products: [...container.products, { productId, qty }],
                    updatedAt: new Date().toISOString(),
                };
            }),
        }));
    },

    removeProductFromContainer: (containerId, productId) => {
        set((state) => ({
            containers: state.containers.map((container) =>
                container.id === containerId
                    ? {
                        ...container,
                        products: container.products.filter((p) => p.productId !== productId),
                        updatedAt: new Date().toISOString(),
                    }
                    : container
            ),
        }));
    },

    updateProductQtyInContainer: (containerId, productId, qty) => {
        if (qty <= 0) {
            get().removeProductFromContainer(containerId, productId);
            return;
        }

        set((state) => ({
            containers: state.containers.map((container) =>
                container.id === containerId
                    ? {
                        ...container,
                        products: container.products.map((p) =>
                            p.productId === productId ? { ...p, qty } : p
                        ),
                        updatedAt: new Date().toISOString(),
                    }
                    : container
            ),
        }));
    },

    isContainer: (barcode) => {
        return get().containers.some((container) => container.barcode === barcode);
    },
});
