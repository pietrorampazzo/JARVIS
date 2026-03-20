import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { CartProvider } from "./context/CartContext";
import Layout from "./components/common/Layout";
import CartSidebar from "./components/carrinho/CartSidebar";
import Home from "./pages/Home";
import Sobre from "./pages/Sobre";
import Contato from "./pages/Contato";
import Checkout from "./pages/Checkout";
import Marcas from "./pages/Marcas";
import Atas from "./pages/Atas";
import ItensAtas from "./pages/ItensAtas";
import Produtos from "./pages/Produtos";

export default function App() {
  return (
    <CartProvider>
      <HashRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/atas" element={<ItensAtas />} />
            <Route path="/atas-vigentes" element={<Atas />} />
            <Route path="/produtos" element={<Produtos />} />
            <Route path="/marcas" element={<Marcas />} />
            <Route path="/sobre" element={<Sobre />} />
            <Route path="/contato" element={<Contato />} />
            <Route path="/checkout" element={<Checkout />} />
          </Routes>
          <CartSidebar />
        </Layout>
      </HashRouter>
    </CartProvider>
  );
}
