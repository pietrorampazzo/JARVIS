import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Minus, Plus, ShoppingBag } from 'lucide-react';
import { useCart } from '@/context/CartContext';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { createPageUrl } from '@/utils';

export default function CartSidebar() {
    const { isCartOpen, setIsCartOpen, cartItens, updateQuantity, removeFromCart, cartTotal } = useCart();

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
    };

    return (
        <AnimatePresence>
            {isCartOpen && (
                <>
                    {/* Overlay */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsCartOpen(false)}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100]"
                    />

                    {/* Sidebar */}
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-[101] flex flex-col"
                    >
                        <div className="flex items-center justify-between p-6 border-b">
                            <div className="flex items-center gap-2">
                                <ShoppingBag className="w-6 h-6 text-blue-600" />
                                <h2 className="text-xl font-bold text-gray-900">Seu Orçamento</h2>
                            </div>
                            <button
                                onClick={() => setIsCartOpen(false)}
                                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6">
                            {cartItens.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-gray-500">
                                    <ShoppingBag className="w-16 h-16 mb-4 opacity-50" />
                                    <p>Seu carrinho está vazio</p>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {cartItens.map((item) => (
                                        <div key={item.id} className="flex gap-4 p-4 bg-gray-50 rounded-xl">
                                            {item.imagem ? (
                                                <img src={item.imagem} alt={item.nome} className="w-20 h-20 object-contain rounded-lg bg-white p-1" />
                                            ) : (
                                                <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center">
                                                    <ShoppingBag className="w-8 h-8 text-gray-400" />
                                                </div>
                                            )}

                                            <div className="flex-1">
                                                <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">{item.nome}</h3>
                                                <p className="text-blue-600 font-bold mt-1">{formatCurrency(item.preco)}</p>

                                                <div className="flex items-center justify-between mt-3">
                                                    <div className="flex items-center gap-3 bg-white border rounded-lg px-2 py-1">
                                                        <button
                                                            onClick={() => updateQuantity(item.id, item.quantidade - 1)}
                                                            className="text-gray-500 hover:text-blue-600"
                                                        >
                                                            <Minus className="w-4 h-4" />
                                                        </button>
                                                        <span className="font-medium text-sm w-4 text-center">{item.quantidade}</span>
                                                        <button
                                                            onClick={() => updateQuantity(item.id, item.quantidade + 1)}
                                                            className="text-gray-500 hover:text-blue-600"
                                                        >
                                                            <Plus className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                    <button
                                                        onClick={() => removeFromCart(item.id)}
                                                        className="text-xs text-red-500 hover:underline"
                                                    >
                                                        Remover
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {cartItens.length > 0 && (
                            <div className="border-t p-6 bg-gray-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-gray-600 font-medium">Total Estimado</span>
                                    <span className="text-2xl font-bold text-gray-900">{formatCurrency(cartTotal)}</span>
                                </div>
                                <Link to={createPageUrl("Checkout")} onClick={() => setIsCartOpen(false)}>
                                    <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg">
                                        Finalizar Orçamento
                                    </Button>
                                </Link>
                            </div>
                        )}
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
