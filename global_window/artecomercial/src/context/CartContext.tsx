import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface CartItem {
    id: string;
    nome: string;
    preco: number;
    quantidade: number;
    imagem?: string;
    marca: string;
    categoria: string;
}

interface CartContextData {
    cartItens: CartItem[];
    addToCart: (item: Omit<CartItem, 'quantidade'>, qtd: number) => void;
    removeFromCart: (id: string) => void;
    updateQuantity: (id: string, quantidade: number) => void;
    clearCart: () => void;
    cartTotal: number;
    cartCount: number;
    isCartOpen: boolean;
    setIsCartOpen: (isOpen: boolean) => void;
}

const CartContext = createContext<CartContextData>({} as CartContextData);

export function CartProvider({ children }: { children: ReactNode }) {
    const [cartItens, setCartItens] = useState<CartItem[]>(() => {
        const stored = localStorage.getItem('@ArteComercial:cart');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                return [];
            }
        }
        return [];
    });

    const [isCartOpen, setIsCartOpen] = useState(false);

    useEffect(() => {
        localStorage.setItem('@ArteComercial:cart', JSON.stringify(cartItens));
    }, [cartItens]);

    const addToCart = (item: Omit<CartItem, 'quantidade'>, qtd: number) => {
        setCartItens(prev => {
            const existing = prev.find(p => p.id === item.id);
            if (existing) {
                return prev.map(p =>
                    p.id === item.id ? { ...p, quantidade: p.quantidade + qtd } : p
                );
            }
            return [...prev, { ...item, quantidade: qtd }];
        });
        setIsCartOpen(true); // Abre o carrinho automaticamente ao adicionar
    };

    const removeFromCart = (id: string) => {
        setCartItens(prev => prev.filter(item => item.id !== id));
    };

    const updateQuantity = (id: string, quantidade: number) => {
        if (quantidade <= 0) {
            removeFromCart(id);
            return;
        }
        setCartItens(prev => prev.map(item =>
            item.id === id ? { ...item, quantidade } : item
        ));
    };

    const clearCart = () => setCartItens([]);

    const cartTotal = cartItens.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
    const cartCount = cartItens.reduce((acc, item) => acc + item.quantidade, 0);

    return (
        <CartContext.Provider value={{
            cartItens,
            addToCart,
            removeFromCart,
            updateQuantity,
            clearCart,
            cartTotal,
            cartCount,
            isCartOpen,
            setIsCartOpen
        }}>
            {children}
        </CartContext.Provider>
    );
}

export function useCart() {
    const context = useContext(CartContext);
    if (!context) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
}
