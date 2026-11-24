import React from "react";
import { Link } from "react-router-dom";
import { HardHat, Phone, Mail, MapPin, ArrowUpRight, Facebook, Linkedin, Instagram } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-surface border-t border-white/5 pt-16 pb-8 text-gray-400">
      <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">

        {/* Column 1: Company Logo & Pitch */}
        <div className="flex flex-col gap-5">
          <Link to="/" className="flex items-center gap-2.5 group w-fit">
            <img
              src="/images/logo.png"
              alt="Sulakhe Constructions Logo"
              className="w-10 h-10 object-cover object-left rounded-lg border border-white/10 group-hover:border-primary/30 transition-all duration-300"
              style={{ mixBlendMode: "screen" }}
            />
            <div>
              <span className="font-display font-extrabold text-lg tracking-wider text-white">
                SULAKHE
              </span>
              <span className="text-[10px] text-primary font-semibold uppercase tracking-[0.2em] -mt-1 block">
                CONSTRUCTIONS
              </span>
            </div>
          </Link>
          <p className="text-sm leading-relaxed">
            Leading engineering contractor and interior designing firm in India. We design and build high-performance infrastructure and premium modern living spaces.
          </p>
          <div className="flex items-center gap-3 mt-2">
            <a href="#" className="w-8 h-8 rounded bg-dark border border-white/5 flex items-center justify-center hover:border-primary hover:text-primary transition-all">
              <Linkedin className="w-4 h-4" />
            </a>
            <a href="https://www.instagram.com/sulakhe_constructions?igsh=aHZ2ZnZobWZyaXdm" target="_blank" rel="noopener noreferrer" className="w-8 h-8 rounded bg-dark border border-white/5 flex items-center justify-center hover:border-primary hover:text-primary transition-all" aria-label="Instagram Profile">
              <Instagram className="w-4 h-4" />
            </a>
            <a href="#" className="w-8 h-8 rounded bg-dark border border-white/5 flex items-center justify-center hover:border-primary hover:text-primary transition-all">
              <Facebook className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Column 2: Quick Links */}
        <div>
          <h3 className="font-display font-bold text-white uppercase tracking-wider text-sm mb-6 border-l-2 border-primary pl-3">
            Navigation
          </h3>
          <ul className="flex flex-col gap-3 text-sm">
            <li>
              <Link to="/" className="hover:text-primary transition-colors flex items-center gap-1 group">
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                Home
              </Link>
            </li>
            <li>
              <Link to="/about" className="hover:text-primary transition-colors flex items-center gap-1 group">
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                About Us
              </Link>
            </li>
            <li>
              <Link to="/services" className="hover:text-primary transition-colors flex items-center gap-1 group">
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                Our Services
              </Link>
            </li>
            <li>
              <Link to="/projects" className="hover:text-primary transition-colors flex items-center gap-1 group">
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                Featured Projects
              </Link>
            </li>
            <li>
              <Link to="/contact" className="hover:text-primary transition-colors flex items-center gap-1 group">
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                Contact
              </Link>
            </li>
          </ul>
        </div>

        {/* Column 3: Services */}
        <div>
          <h3 className="font-display font-bold text-white uppercase tracking-wider text-sm mb-6 border-l-2 border-primary pl-3">
            Services
          </h3>
          <ul className="flex flex-col gap-3 text-sm">
            <li>
              <Link to="/services" className="hover:text-primary transition-colors">
                House Construction
              </Link>
            </li>
            <li>
              <Link to="/services" className="hover:text-primary transition-colors">
                Civil Contracting & Works
              </Link>
            </li>
            <li>
              <Link to="/services" className="hover:text-primary transition-colors">
                Structural Renovation
              </Link>
            </li>
            <li>
              <Link to="/services" className="hover:text-primary transition-colors">
                Modern Interior Design
              </Link>
            </li>
          </ul>
        </div>

        {/* Column 4: Contact Info */}
        <div>
          <h3 className="font-display font-bold text-white uppercase tracking-wider text-sm mb-6 border-l-2 border-primary pl-3">
            Get in touch
          </h3>
          <ul className="flex flex-col gap-4 text-sm">
            <li className="flex gap-3">
              <Phone className="w-5 h-5 text-primary shrink-0" />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-0.5">Call Us</p>
                <a href="tel:+918951529291" className="text-white hover:text-primary transition-colors font-medium">
                  +91 89515 29291
                </a>
              </div>
            </li>
            <li className="flex gap-3">
              <Mail className="w-5 h-5 text-primary shrink-0" />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-0.5">Email Support</p>
                <a href="mailto:nsulakhe.5@gmail.com" className="text-white hover:text-primary transition-colors font-medium">
                  nsulakhe.5@gmail.com
                </a>
              </div>
            </li>
            <li className="flex gap-3">
              <MapPin className="w-5 h-5 text-primary shrink-0" />
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-0.5">Headquarters</p>
                <span className="text-white text-xs leading-normal">

                </span>
              </div>
            </li>
          </ul>
        </div>

      </div>

      {/* Bottom Footer Section */}
      <div className="max-w-7xl mx-auto px-6 md:px-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-xs">
        <p>© 2026 Sulakhe Constructions. All rights reserved.</p>
        <p className="flex items-center gap-1.5">
          Building trust with quality construction • ISO 9001:2015 Certified
        </p>
      </div>
    </footer>
  );
}
