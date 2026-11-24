import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Phone, HardHat } from "lucide-react";

const navLinks = [
  { name: "Home", path: "/" },
  { name: "About", path: "/about" },
  { name: "Services", path: "/services" },
  { name: "Projects", path: "/projects" },
  { name: "Contact", path: "/contact" }
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu on page transition
  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  return (
    <>
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
            ? "glass-nav py-4 shadow-lg shadow-black/10"
            : "bg-transparent py-6"
          }`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <img
              src="/images/logo.png"
              alt="Sulakhe Constructions Logo"
              className="w-10 h-10 object-cover object-left rounded-lg border border-white/10 group-hover:border-primary/30 transition-all duration-300"
              style={{ mixBlendMode: "screen" }}
            />
            <div>
              <span className="font-display font-extrabold text-lg md:text-xl tracking-wider block leading-tight text-white group-hover:text-primary transition-colors duration-300">
                SULAKHE
              </span>
              <span className="text-[10px] md:text-xs text-primary font-semibold uppercase tracking-[0.2em] -mt-1 block">
                CONSTRUCTIONS
              </span>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-8">
            <ul className="flex items-center gap-8">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path;
                return (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className={`relative font-medium text-sm tracking-wider uppercase transition-colors duration-300 py-2 ${isActive ? "text-primary font-semibold" : "text-gray-300 hover:text-primary"
                        }`}
                    >
                      {link.name}
                      {isActive && (
                        <motion.span
                          layoutId="activeNavIndicator"
                          className="absolute bottom-0 left-0 right-0 h-[2px] bg-primary"
                          transition={{ type: "spring", stiffness: 380, damping: 30 }}
                        />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>

            <Link
              to="/contact"
              id="nav-cta-btn"
              className="flex items-center gap-2 bg-primary hover:bg-primary/95 text-dark font-display font-bold text-xs uppercase tracking-wider px-5 py-3 rounded transition-all duration-300 hover:-translate-y-0.5"
            >
              <Phone className="w-4 h-4" />
              Call Now
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            id="mobile-menu-toggle"
            className="lg:hidden text-white hover:text-primary p-2 focus:outline-none"
            aria-label="Toggle navigation menu"
          >
            {isOpen ? <X className="w-7 h-7" /> : <Menu className="w-7 h-7" />}
          </button>
        </div>
      </motion.nav>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 top-0 z-40 bg-dark/95 backdrop-blur-lg flex flex-col justify-center items-center lg:hidden"
          >
            <ul className="flex flex-col gap-6 text-center">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path;
                return (
                  <motion.li
                    key={link.name}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Link
                      to={link.path}
                      onClick={() => setIsOpen(false)}
                      className={`text-2xl font-display font-bold uppercase tracking-wider transition-colors ${isActive ? "text-primary" : "text-gray-300 hover:text-primary"
                        }`}
                    >
                      {link.name}
                    </Link>
                  </motion.li>
                );
              })}
            </ul>

            <div className="mt-12 flex flex-col gap-4 w-64">
              <a
                href="tel:+918951529291"
                className="flex items-center justify-center gap-3 bg-primary text-dark font-display font-bold text-sm uppercase tracking-wider py-4 rounded-lg transition-transform hover:scale-105 active:scale-95"
              >
                <Phone className="w-4 h-4" />
                Call Now
              </a>
              <a
                href="https://wa.me/918951529291?text=Hi%20Sulakhe%20Constructions,%20I'm%20interested%20in%20your%20services."
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-3 bg-emerald-600 hover:bg-emerald-500 text-white font-display font-bold text-sm uppercase tracking-wider py-4 rounded-lg transition-transform hover:scale-105 active:scale-95"
              >
                {/* Custom WhatsApp Icon */}
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.724-1.458L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.37 9.864-9.799.002-2.63-1.023-5.101-2.885-6.97C16.387 1.968 13.916 1.01 11.999 1.01c-5.442 0-9.87 4.372-9.874 9.802-.001 1.762.476 3.486 1.381 5.014L2.43 20.4l4.217-1.246zM17.8 14.5c-.32-.16-1.89-.93-2.18-1.04-.3-.11-.51-.17-.72.15-.22.32-.83 1.04-1.02 1.25-.19.21-.38.24-.7.08-1.16-.58-1.93-1.03-2.69-2.35-.2-.35-.2-.73-.08-1.08.11-.33.32-.7.48-.96.16-.26.21-.43.32-.72.11-.29.05-.54-.03-.7-.08-.16-.72-1.73-.99-2.39-.26-.64-.52-.55-.72-.56-.19-.01-.41-.01-.63-.01-.22 0-.58.08-.88.41-.3.33-1.15 1.13-1.15 2.75s1.18 3.19 1.34 3.41c.16.22 2.33 3.55 5.63 4.98.79.34 1.4.55 1.88.71.8.25 1.52.22 2.1.13.64-.1 1.89-.77 2.15-1.52.26-.75.26-1.4.19-1.52-.07-.12-.27-.24-.59-.4z" />
                </svg>
                WhatsApp Us
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
