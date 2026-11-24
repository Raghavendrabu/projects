import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Phone, Mail, MapPin, Clock, Send, MessageSquare, CheckCircle, AlertCircle, Linkedin, Instagram } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

export default function Contact() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    projectType: "House Construction",
    message: ""
  });

  const [status, setStatus] = useState("idle"); // idle | sending | success | error
  const [isRedirecting, setIsRedirecting] = useState(false);

  const whatsappUrl = `https://wa.me/918951529291?text=Hi%20Sulakhe%20Constructions,%20my%20name%20is%20${encodeURIComponent(formData.name || "visitor")}.%20I'm%20interested%20in%20${encodeURIComponent(formData.projectType)}.%20Message:%20${encodeURIComponent(formData.message || "Hi!")}`;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.phone) {
      setStatus("error");
      return;
    }

    setStatus("sending");
    setIsRedirecting(true);

    const text = `Hi Sulakhe Constructions,
I would like to make an inquiry.
Name: ${formData.name}
Phone: ${formData.phone}
Email: ${formData.email}
Project Division: ${formData.projectType}
Message: ${formData.message || "No message provided."}`;

    const url = `https://wa.me/918951529291?text=${encodeURIComponent(text)}`;

    setTimeout(() => {
      window.open(url, "_blank");
      setIsRedirecting(false);
      setStatus("success");
      setFormData({
        name: "",
        email: "",
        phone: "",
        projectType: "House Construction",
        message: ""
      });
    }, 2500);
  };

  return (
    <div className="w-full pt-28 pb-20">

      {/* 1. HERO HEADER */}
      <section className="relative py-16 bg-[#0f0f0f] border-b border-white/5 overflow-hidden">
        <div className="absolute inset-0 bg-stripes opacity-10 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
          <SectionHeader
            eyebrow="Get In Touch"
            title="Let's Build Something Great Together!"
            subtitle="We're here to answer your questions and discuss your next project. Reach out to us anytime."
          />
        </div>
      </section>

      {/* 2. CONTACT DETAILS, FORM & CONTACT PERSON CARD */}
      <section className="py-20 bg-dark">
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex flex-col gap-12">
          
          {/* Main 3-Column Card */}
          <div className="bg-surface border border-white/5 rounded-[32px] overflow-hidden shadow-2xl grid grid-cols-1 lg:grid-cols-12 gap-0 items-stretch min-h-[580px]">
            
            {/* Column 1: Contact Details */}
            <div className="lg:col-span-3 p-8 md:p-10 flex flex-col gap-8 text-white">
              <h3 className="font-display font-black text-xs uppercase tracking-[0.2em] text-gray-400">
                Contact Details
              </h3>
              
              <div className="flex flex-col gap-6">
                {/* Phone */}
                <div className="flex gap-4 items-start">
                  <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center shrink-0">
                    <Phone className="text-primary w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold block mb-1">Phone</span>
                    <a href="tel:+918951529291" className="text-sm font-bold text-white hover:text-primary transition-colors">
                      +91 89515 29291
                    </a>
                  </div>
                </div>

                {/* Email */}
                <div className="flex gap-4 items-start">
                  <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center shrink-0">
                    <Mail className="text-primary w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold block mb-1">Email</span>
                    <a href="mailto:nsulakhe.5@gmail.com" className="text-xs font-bold text-white hover:text-primary transition-colors block break-all">
                      nsulakhe.5@gmail.com
                    </a>
                  </div>
                </div>

                {/* Address */}
                <div className="flex gap-4 items-start">
                  <div className="w-12 h-12 bg-white/5 border border-white/10 rounded-xl flex items-center justify-center shrink-0">
                    <MapPin className="text-primary w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold block mb-1">Address</span>
                    <span className="text-xs font-bold text-gray-300 leading-relaxed block">
                      Naveen Sulakhe<br />
                      #31, Laxmi estate, Sundar colony,<br />
                      near pradeep shettar house,<br />
                      keshwapur, hubli
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Column 2: Send Us a Message */}
            <div className="lg:col-span-5 p-8 md:p-10 border-t lg:border-t-0 lg:border-l border-white/5 flex flex-col gap-6 text-white">
              <h3 className="font-display font-black text-xs uppercase tracking-[0.2em] text-gray-400">
                Send Us a Message
              </h3>

              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <input
                    type="text"
                    name="name"
                    placeholder="Your Name"
                    value={formData.name}
                    onChange={handleChange}
                    className="bg-dark border border-white/10 text-white placeholder-gray-550 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors font-medium"
                    required
                  />
                  <input
                    type="email"
                    name="email"
                    placeholder="Email Address"
                    value={formData.email}
                    onChange={handleChange}
                    className="bg-dark border border-white/10 text-white placeholder-gray-550 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors font-medium"
                    required
                  />
                </div>

                <input
                  type="tel"
                  name="phone"
                  placeholder="Phone Number"
                  value={formData.phone}
                  onChange={handleChange}
                  className="bg-dark border border-white/10 text-white placeholder-gray-550 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors font-medium"
                  required
                />

                <select
                  name="projectType"
                  value={formData.projectType}
                  onChange={handleChange}
                  className="bg-dark border border-white/10 text-white rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors cursor-pointer font-medium"
                >
                  <option value="House Construction">House Construction</option>
                  <option value="Civil Works">Civil Contracting / Works</option>
                  <option value="Renovation">Structural Renovation</option>
                  <option value="Interior Design">Modern Interior Design</option>
                </select>

                <textarea
                  name="message"
                  rows="4"
                  placeholder="Your Message"
                  value={formData.message}
                  onChange={handleChange}
                  className="bg-dark border border-white/10 text-white placeholder-gray-550 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary transition-colors resize-none font-medium"
                />

                <button
                  type="submit"
                  disabled={status === "sending"}
                  className="w-full sm:w-auto bg-primary hover:bg-primary/95 text-dark font-display font-bold text-xs uppercase tracking-widest px-6 py-3.5 rounded-lg transition-transform active:scale-95 flex items-center justify-center gap-2 cursor-pointer"
                >
                  <Send className="w-4 h-4 text-dark" />
                  SEND MESSAGE
                </button>
              </form>

              <AnimatePresence>
                {status === "success" && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="bg-emerald-950/20 border border-emerald-500/20 rounded-lg p-4 flex gap-3 text-emerald-400"
                  >
                    <CheckCircle className="w-5 h-5 shrink-0 text-emerald-500 mt-0.5" />
                    <div>
                      <h4 className="font-bold text-sm">Message Sent Successfully!</h4>
                      <p className="text-xs text-emerald-500/80 leading-normal mt-0.5">
                        Redirecting to WhatsApp to send your inquiry details...
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Column 3: Contact Person (Dark Accent) */}
            <div className="lg:col-span-4 bg-[#1c120c] p-8 md:p-10 text-white rounded-t-[32px] lg:rounded-t-none lg:rounded-r-[32px] lg:rounded-l-[40px] relative overflow-hidden flex flex-col justify-between min-h-[480px]">
              {/* Background Accent Grid / Overlay */}
              <div className="absolute inset-0 bg-stripes opacity-5 pointer-events-none"></div>

              <div className="relative z-10 w-full flex flex-col gap-6">
                <div>
                  <span className="text-[10px] text-primary font-black uppercase tracking-[0.2em] block mb-2">
                    Contact Person
                  </span>
                  <h3 className="font-display font-extrabold text-xl sm:text-2xl lg:text-2xl text-white leading-tight">
                    Er. Naveenkumar<br />
                    Sulakhe
                  </h3>
                  <p className="text-[11px] text-gray-400 mt-1 font-medium">
                    Consulting Engineer<br />&amp; Project Consultant
                  </p>
                </div>

                <p className="text-xs text-gray-300 leading-relaxed italic">
                  "Have a project in mind? Let's discuss how we can turn your ideas into reality."
                </p>
              </div>

              {/* Logo and Social links Row */}
              <div className="relative z-10 border-t border-white/10 pt-6 mt-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                
                {/* Brand logo image instead of SVG */}
                <div className="flex items-center gap-2 bg-black/45 border border-white/10 rounded-2xl p-2.5 w-fit backdrop-blur-sm shadow-xl">
                  <img
                    src="/images/logo.png"
                    alt="Sulakhe Constructions Logo"
                    className="w-44 h-auto object-contain"
                    style={{ mixBlendMode: "screen" }}
                  />
                </div>
                
                {/* Social links (Rounded) */}
                <div className="flex items-center gap-2 shrink-0">
                  <a
                    href="#"
                    className="w-8 h-8 rounded-full border border-white/15 hover:border-primary hover:text-primary flex items-center justify-center transition-all bg-white/5"
                    aria-label="LinkedIn Profile"
                  >
                    <Linkedin className="w-3.5 h-3.5" />
                  </a>
                  <a
                    href="https://www.instagram.com/sulakhe_constructions?igsh=aHZ2ZnZobWZyaXdm"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-8 h-8 rounded-full border border-white/15 hover:border-primary hover:text-primary flex items-center justify-center transition-all bg-white/5"
                    aria-label="Instagram Profile"
                  >
                    <Instagram className="w-3.5 h-3.5" />
                  </a>
                  <a
                    href={whatsappUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-8 h-8 rounded-full border border-white/15 hover:border-primary hover:text-primary flex items-center justify-center transition-all bg-white/5"
                    aria-label="WhatsApp Chat"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            </div>

          </div>

          {/* Highlights Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center bg-white/5 border border-white/5 rounded-2xl p-6 md:py-8">
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-full">
                <Clock className="text-primary w-4.5 h-4.5" />
              </div>
              <h4 className="text-sm font-bold text-white mt-1">Quick Support</h4>
              <p className="text-[11px] text-gray-500">We reply within 24 hours</p>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-full">
                <CheckCircle className="text-primary w-4.5 h-4.5" />
              </div>
              <h4 className="text-sm font-bold text-white mt-1">Trusted Service</h4>
              <p className="text-[11px] text-gray-500">Quality &amp; Safety First</p>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-full">
                <Send className="text-primary w-4.5 h-4.5" />
              </div>
              <h4 className="text-sm font-bold text-white mt-1">Expert Team</h4>
              <p className="text-[11px] text-gray-500">Experienced Professionals</p>
            </div>
            
            <div className="flex flex-col items-center gap-2">
              <div className="w-10 h-10 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-full">
                <MapPin className="text-primary w-4.5 h-4.5" />
              </div>
              <h4 className="text-sm font-bold text-white mt-1">On-Time Delivery</h4>
              <p className="text-[11px] text-gray-500">We Value Your Time</p>
            </div>
          </div>

        </div>
      </section>

      {/* Redirect Splash Overlay */}
      <AnimatePresence>
        {isRedirecting && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] bg-black flex flex-col items-center justify-center p-6 text-center"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="flex flex-col items-center gap-6"
            >
              {/* Brand Logo image instead of SVG */}
              <div className="flex flex-col items-center text-center">
                <img
                  src="/images/logo.png"
                  alt="Sulakhe Constructions Logo"
                  className="w-64 md:w-80 h-auto object-contain"
                  style={{ mixBlendMode: "screen" }}
                />
              </div>

              {/* Connecting/Pulsing Message */}
              <div className="flex flex-col items-center gap-2 mt-6">
                <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                <p className="text-primary text-sm font-display font-bold uppercase tracking-widest mt-2 animate-pulse">
                  Redirecting to WhatsApp
                </p>
                <p className="text-gray-400 text-xs mt-1 max-w-xs leading-relaxed">
                  Connecting to Er. Naveenkumar Sulakhe with your inquiry details.
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
