import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Phone, ArrowRight, ShieldCheck, Clock, Award, Hammer, HardHat, Home as HomeIcon, Brush, ClipboardCheck, ArrowUpRight } from "lucide-react";
import AnimatedCounter from "../components/AnimatedCounter";
import SectionHeader from "../components/SectionHeader";

const stats = [
  { value: "8", suffix: "+", label: "Years of Experience" },
  { value: "45", suffix: "+", label: "Projects Completed" },
  { value: "12", suffix: "+", label: "Corporate Clients" },
  { value: "100", suffix: "%", label: "Safety Record" }
];

const featuredServices = [
  {
    icon: HomeIcon,
    title: "House Construction",
    description: "End-to-end residential building contracting from structural planning to final brickwork and keys handover.",
    img: "/images/house_construction.png"
  },
  {
    icon: HardHat,
    title: "Civil Works",
    description: "Reinforced concrete foundations, high-rise framing, structural steel design, and industrial civil contracts.",
    img: "/images/civil_works.png"
  },
  {
    icon: Hammer,
    title: "Structural Renovation",
    description: "Upgrading outdated infrastructure, retrofitting, seismic strengthening, and structural additions.",
    img: "/images/renovation.png"
  },
  {
    icon: Brush,
    title: "Modern Interior Design",
    description: "Premium spatial planning, custom modern cabinetry, ambient false ceilings, and bespoke layouts.",
    img: "/images/interior_design.png"
  }
];

const features = [
  {
    icon: ShieldCheck,
    title: "Unmatched Build Quality",
    description: "We use top-grade structural steel and premium aggregate concrete conforming to ISI standards."
  },
  {
    icon: Clock,
    title: "Strict Deadline Adherence",
    description: "Our engineered project schedules ensure your commercial or home project finishes exactly on time."
  },

  {
    icon: ClipboardCheck,
    title: "Hassle-Free Approvals",
    description: "We coordinate all blueprint signing, regulatory permits, and structural audit clearances for you."
  }
];

const testimonials = [
  {
    quote: "Sulakhe Constructions delivered our premium commercial building in Pune ahead of schedule. The structural work and concrete finish are flawless. Highly recommended engineering partner.",
    author: "Rajesh Kulkarni",
    role: "CEO, Kulkarni Ventures",
    rating: 5
  },
  {
    quote: "Our modern villa was built exactly as shown in the 3D renders. The interior layout is spacious, and the structural detailing was handled with absolute professionalism.",
    author: "Smita Deshmukh",
    role: "Homeowner, Baner",
    rating: 5
  },
  {
    quote: "Their team managed our industrial warehouse project from soil testing to PEB installation. The transparency in billing and material testing reports was remarkable.",
    author: "Amit Sulgule",
    role: "Operations Director, LogiCorp",
    rating: 5
  }
];

export default function Home() {
  const whatsappUrl = "https://wa.me/918951529291?text=Hi%20Sulakhe%20Constructions,%20I'm%20interested%20in%20your%20services.";

  return (
    <div className="w-full">
      {/* 1. HERO SECTION */}
      <section className="relative min-height-[90vh] lg:min-h-screen flex items-center pt-24 pb-16 lg:py-0 overflow-hidden bg-[#0a0a0a]">
        {/* Background Image & Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="/images/hero_construction.png"
            alt="Sulakhe Constructions Construction Site"
            className="w-full h-full object-cover object-center opacity-30 select-none pointer-events-none"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-dark via-dark/80 to-transparent"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-dark via-dark/60 to-transparent"></div>
          {/* Diagonal overlay stripes */}
          <div className="absolute inset-0 bg-stripes opacity-20 pointer-events-none"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-12 w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-8 flex flex-col items-start text-left mt-8 lg:mt-0">
            {/* Tagline Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-full px-4 py-1.5 mb-6"
            >
              <span className="w-2 h-2 rounded-full bg-primary animate-ping"></span>
              <span className="text-[10px] md:text-xs text-primary font-bold uppercase tracking-wider">
                Consulting Engineer • Contractor • Interior Designer
              </span>
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.15 }}
              className="font-display font-extrabold text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-white tracking-tight leading-none mb-6"
            >
              Building Trust With <br />
              <span className="text-primary text-glow font-black">Quality Construction</span>
            </motion.h1>

            {/* Subtitle / Pitch */}
            <motion.p
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="text-gray-300 max-w-2xl text-base md:text-lg lg:text-xl leading-relaxed mb-10"
            >
              Sulakhe Constructions brings engineering excellence, precision site contracting, and luxurious interior aesthetics together to build tomorrow's landmarks today.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 25 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.45 }}
              className="flex flex-wrap gap-4 w-full sm:w-auto"
            >
              <a
                href="tel:+918951529291"
                id="hero-cta-call"
                className="flex items-center justify-center gap-3 bg-primary hover:bg-primary/95 text-dark font-display font-bold text-sm uppercase tracking-wider px-8 py-4 rounded transition-all duration-300 hover:-translate-y-1 w-full sm:w-auto"
              >
                <Phone className="w-4.5 h-4.5" />
                Call Now
              </a>
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                id="hero-cta-whatsapp"
                className="flex items-center justify-center gap-3 bg-[#111111] hover:bg-[#1a1a1a] text-white border border-white/10 hover:border-primary font-display font-bold text-sm uppercase tracking-wider px-8 py-4 rounded transition-all duration-300 hover:-translate-y-1 w-full sm:w-auto glass"
              >
                {/* SVG WhatsApp icon */}
                <svg className="w-5 h-5 fill-current text-green-500" viewBox="0 0 24 24">
                  <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.514 2.266 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.724-1.458L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.37 9.864-9.799.002-2.63-1.023-5.101-2.885-6.97C16.387 1.968 13.916 1.01 11.999 1.01c-5.442 0-9.87 4.372-9.874 9.802-.001 1.762.476 3.486 1.381 5.014L2.43 20.4l4.217-1.246zM17.8 14.5c-.32-.16-1.89-.93-2.18-1.04-.3-.11-.51-.17-.72.15-.22.32-.83 1.04-1.02 1.25-.19.21-.38.24-.7.08-1.16-.58-1.93-1.03-2.69-2.35-.2-.35-.2-.73-.08-1.08.11-.33.32-.7.48-.96.16-.26.21-.43.32-.72.11-.29.05-.54-.03-.7-.08-.16-.72-1.73-.99-2.39-.26-.64-.52-.55-.72-.56-.19-.01-.41-.01-.63-.01-.22 0-.58.08-.88.41-.3.33-1.15 1.13-1.15 2.75s1.18 3.19 1.34 3.41c.16.22 2.33 3.55 5.63 4.98.79.34 1.4.55 1.88.71.8.25 1.52.22 2.1.13.64-.1 1.89-.77 2.15-1.52.26-.75.26-1.4.19-1.52-.07-.12-.27-.24-.59-.4z" />
                </svg>
                WhatsApp Us
              </a>
            </motion.div>
          </div>
        </div>

        {/* Diagonal border accent */}
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-primary/50 to-transparent"></div>
      </section>

      {/* 2. STATS SECTION */}
      <section className="bg-surface relative z-20 py-12 border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            {stats.map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="flex flex-col items-center justify-center p-4"
              >
                <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                <p className="text-gray-400 font-display text-xs md:text-sm uppercase tracking-wider mt-2">
                  {stat.label}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. ABOUT TEASER SECTION */}
      <section id="about-teaser" className="py-24 bg-dark relative">
        <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

          {/* Visual Stack */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="relative"
          >
            {/* Main Image Frame */}
            <div className="relative aspect-[4/3] rounded-lg overflow-hidden border border-white/10 group">
              <div className="absolute inset-0 bg-primary/10 mix-blend-overlay z-10 transition-opacity group-hover:opacity-0"></div>
              <img
                src="/images/hero_construction.png"
                alt="Construction execution blueprint"
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
            </div>

            {/* Accent Frame */}
            <div className="absolute -bottom-6 -right-6 w-1/2 aspect-square rounded-lg overflow-hidden border border-primary/20 bg-surface p-2 shadow-2xl hidden md:block">
              <div className="w-full h-full bg-[#111111] flex flex-col justify-center items-center text-center p-4">
                <HardHat className="text-primary w-10 h-10 mb-2" />
                <span className="text-xs uppercase tracking-wider text-gray-400 font-bold block mb-1">Safety First</span>
                <span className="text-[10px] text-gray-500 leading-tight">Zero incident record since inception</span>
              </div>
            </div>

            {/* Glowing Accent Ring */}
            <div className="absolute -inset-4 border border-dashed border-primary/20 rounded-lg -z-10 pointer-events-none"></div>
          </motion.div>

          {/* Text Content */}
          <div className="flex flex-col items-start">
            <SectionHeader
              eyebrow="About Our Firm"
              title="8+ Years of Structural Integrity & Trust"
              subtitle="At Sulakhe Constructions, we translate complex blueprints into landmarks. From structural core designs to high-end interior decorations, we maintain top-tier builds."
            />

            <motion.p
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-gray-400 text-sm md:text-base leading-relaxed -mt-6 mb-8"
            >
              We are headquartered in Pune, specializing in consulting engineering, general contracting, and customized interior spaces. Our focus is quality materials, detailed planning, and transparency.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <Link
                to="/about"
                className="flex items-center gap-2 group text-primary font-display font-bold text-sm uppercase tracking-wider border-b border-primary/30 hover:border-primary pb-1 transition-all"
              >
                Learn More About Us
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </motion.div>
          </div>

        </div>
      </section>

      {/* 4. SERVICES GRID SECTION */}
      <section id="services-teaser" className="py-24 bg-surface border-t border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 md:px-12">

          <SectionHeader
            centered
            eyebrow="What We Do"
            title="Premium Building Services"
            subtitle="Explore our comprehensive divisions covering architectural design, foundation work, updates, and custom luxury interiors."
          />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
            {featuredServices.map((service, idx) => {
              const Icon = service.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 25 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: idx * 0.1 }}
                  className="group bg-dark border border-white/5 hover:border-primary/30 p-6 rounded-lg flex flex-col justify-between transition-all duration-300 card-glow h-full min-h-[350px] relative overflow-hidden"
                >
                  {/* Background Service Image Hover */}
                  <div className="absolute inset-0 z-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500">
                    <img
                      src={service.img}
                      alt={service.title}
                      className="w-full h-full object-cover grayscale"
                    />
                  </div>

                  <div className="relative z-10 flex flex-col">
                    <div className="w-12 h-12 bg-white/5 border border-white/10 group-hover:bg-primary group-hover:border-primary flex items-center justify-center rounded-lg mb-6 transition-all duration-300">
                      <Icon className="text-primary group-hover:text-dark w-6 h-6 transition-colors" />
                    </div>
                    <h3 className="font-display font-bold text-lg text-white mb-3 group-hover:text-primary transition-colors">
                      {service.title}
                    </h3>
                    <p className="text-gray-400 text-xs md:text-sm leading-relaxed">
                      {service.description}
                    </p>
                  </div>

                  <div className="relative z-10 pt-6">
                    <Link
                      to="/services"
                      className="inline-flex items-center gap-1.5 text-xs text-gray-500 group-hover:text-primary font-semibold uppercase tracking-wider transition-colors"
                    >
                      Read Details
                      <ArrowUpRight className="w-3.5 h-3.5 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                    </Link>
                  </div>
                </motion.div>
              );
            })}
          </div>

        </div>
      </section>

      {/* 5. WHY CHOOSE US */}
      <section className="py-24 bg-dark relative">
        <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-1 lg:grid-cols-12 gap-16 items-center">

          <div className="lg:col-span-5">
            <SectionHeader
              eyebrow="Why Choose Sulakhe"
              title="Crafting Pillars of Quality Since Day One"
              subtitle="We set high benchmarks for civil projects. Our client satisfaction is backed by careful engineering and clear costing models."
            />
            <div className="mt-8">
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-primary hover:bg-primary/95 text-dark font-display font-bold text-xs uppercase tracking-wider px-6 py-3.5 rounded transition-transform hover:-translate-y-0.5"
              >
                Discuss Project Costing
                <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </div>

          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-6">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  className="bg-surface border border-white/5 p-6 rounded-lg glass"
                >
                  <Icon className="text-primary w-8 h-8 mb-4" />
                  <h4 className="font-display font-bold text-base text-white mb-2">
                    {feat.title}
                  </h4>
                  <p className="text-gray-400 text-xs md:text-sm leading-relaxed">
                    {feat.description}
                  </p>
                </motion.div>
              );
            })}
          </div>

        </div>
      </section>

      {/* 6. TESTIMONIALS SECTION */}
      <section className="py-24 bg-surface border-t border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 md:px-12">

          <SectionHeader
            centered
            eyebrow="Reviews"
            title="Trusted By Industry Leaders"
            subtitle="Read client testimonials regarding our structural construction, timely execution, and custom interior fit-outs."
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
            {testimonials.map((test, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.15 }}
                className="bg-dark border border-white/5 hover:border-primary/20 p-8 rounded-lg flex flex-col justify-between transition-colors relative"
              >
                {/* Quote Icon Background */}
                <span className="absolute top-4 right-6 text-7xl font-serif text-white/5 select-none pointer-events-none">
                  “
                </span>

                <div className="flex flex-col gap-4 relative z-10">
                  {/* Rating Stars */}
                  <div className="flex gap-1">
                    {[...Array(test.rating)].map((_, i) => (
                      <span key={i} className="text-primary text-sm">★</span>
                    ))}
                  </div>
                  <p className="text-gray-300 text-xs md:text-sm leading-relaxed italic">
                    "{test.quote}"
                  </p>
                </div>

                <div className="mt-8 border-t border-white/5 pt-4">
                  <h4 className="font-display font-semibold text-sm text-white">{test.author}</h4>
                  <span className="text-[11px] text-gray-500">{test.role}</span>
                </div>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

      {/* 7. QUICK CONTACT CTA */}
      <section className="py-20 bg-dark relative overflow-hidden">
        {/* Diagonal accents */}
        <div className="absolute inset-0 bg-stripes opacity-10 pointer-events-none"></div>
        <div className="max-w-5xl mx-auto px-6 text-center relative z-10 flex flex-col items-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="w-12 h-12 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-full mb-6"
          >
            <HardHat className="text-primary w-6 h-6" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="font-display font-extrabold text-3xl md:text-4xl lg:text-5xl text-white mb-4"
          >
            Have a blueprint or idea in mind?
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-gray-400 text-sm md:text-base max-w-xl mb-10 leading-relaxed"
          >
            Let's connect. Talk to our chief consulting engineer to discuss soil testing, cost estimations, and interior modeling.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-wrap gap-4 justify-center"
          >
            <Link
              to="/contact"
              className="bg-primary hover:bg-primary/95 text-dark font-display font-bold text-xs uppercase tracking-wider px-8 py-4 rounded transition-all hover:-translate-y-0.5 shadow-lg shadow-primary/15"
            >
              Get Free Consultation
            </Link>
            <a
              href="tel:+918951529291"
              className="bg-transparent border border-white/10 hover:border-primary text-white font-display font-bold text-xs uppercase tracking-wider px-8 py-4 rounded transition-all hover:-translate-y-0.5 glass"
            >
              Request A Quote
            </a>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
