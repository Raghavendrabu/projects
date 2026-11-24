import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Home, HardHat, Hammer, Brush, CheckCircle, ArrowRight, MessageSquare } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

const servicesList = [
  {
    id: "house-construction",
    icon: Home,
    title: "House Construction",
    subtitle: "Turnkey residential villa & independent bungalow contracting",
    img: "/images/house_construction.png",
    description: "We handle the complete execution of premium residential buildings. From footing excavation, plinth filling, RCC framing (columns & slabs), brickwork to final plastering and utility integrations.",
    deliverables: [
      "Soil investigation and load bearing assessment",
      "Structural designs & architectural layout blueprinting",
      "Steel reinforcement framing & concrete cast checks",
      "Concealed electrical plumbing & sanitization mapping",
      "Exterior plastering, painting, & weatherproof coatings"
    ]
  },
  {
    id: "civil-works",
    icon: HardHat,
    title: "Civil Contracting & Works",
    subtitle: "Large-scale concrete foundations & commercial contracting",
    img: "/images/civil_works.png",
    description: "Technical contracting services for commercial buildings, factories, warehouses, and road developments. Our teams operate with top-tier mixing plants, high-precision concrete testing, and experienced site managers.",
    deliverables: [
      "Heavy industrial machinery concrete foundations",
      "Multi-storey commercial shear wall & RCC structures",
      "Pre-engineered steel building (PEB) installations",
      "Stormwater drainage systems & internal road pavings",
      "Comprehensive site safety supervision & daily logs"
    ]
  },
  {
    id: "renovation",
    icon: Hammer,
    title: "Structural Renovation",
    subtitle: "Retrofitting, structural strengthening & updates",
    img: "/images/renovation.png",
    description: "Breathe new life into aging structures. We specialize in structural rehabilitation, retrofitting columns, expanding living zones, and updating structural components safely without affecting secondary load lines.",
    deliverables: [
      "Visual and ultrasonic structural health auditing",
      "Seismic retrofitting and carbon fiber wrapping",
      "Corrosion treatment for rusted structural rebars",
      "Wall removals & structural steel girder installations",
      "Dampness checks, leakage arrests & surface updates"
    ]
  },
  {
    id: "interior-design",
    icon: Brush,
    title: "Modern Interior Design",
    subtitle: "Bespoke spatial design & luxury modular layouts",
    img: "/images/interior_design.png",
    description: "Transform raw brick interiors into warm, elegant living and working environments. Our principal architects deliver photorealistic 3D renders, custom modern cabinetry designs, and premium ambient lighting layouts.",
    deliverables: [
      "Photorealistic 3D interior design & material boards",
      "Premium modular kitchen designs with acrylic finishes",
      "Bespoke wardrobes, TV panels, and space dividers",
      "Acoustic false ceiling panels and modern LED planning",
      "Curation of marble, wall panels, and accent paints"
    ]
  }
];

const steps = [
  { step: "01", title: "Consultation & Estimation", desc: "We review your site dimensions, discuss requirements, prepare detailed BOQ quotes, and sign project bounds." },
  { step: "02", title: "Structural Modeling", desc: "Our IIT-trained engineers prepare structural designs (STAAD Pro models, load distribution checks) and architectural layouts." },
  { step: "03", title: "Excavation & Foundation", desc: "We conduct soil verification checks, excavate footings, and construct the plinth foundation with anti-termite layers." },
  { step: "04", title: "Superstructure Frame", desc: "RCC framing (columns, beams, slabs) is cast under strict supervision. Concrete samples undergo compressive strength tests." },
  { step: "05", title: "Finishing & Interiors", desc: "Concealed utility lines, masonry plastering, customized premium interior installations, and final ISO quality sign-off." }
];

export default function Services() {
  const whatsappUrl = "https://wa.me/918951529291?text=Hi%20Sulakhe%20Constructions,%20I'm%20interested%20in%20your%20services.";

  return (
    <div className="w-full pt-28 pb-20">
      
      {/* 1. HERO HEADER */}
      <section className="relative py-16 bg-[#0f0f0f] border-b border-white/5 overflow-hidden">
        <div className="absolute inset-0 bg-stripes opacity-10 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
          <SectionHeader
            eyebrow="Specializations"
            title="Premium Engineering Services"
            subtitle="We handle complete structural contracting and spatial transformations, ensuring that every weld, beam, and tile is placed with high precision."
          />
        </div>
      </section>

      {/* 2. SERVICES LIST */}
      <section className="py-20 bg-dark">
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex flex-col gap-28">
          {servicesList.map((service, idx) => {
            const Icon = service.icon;
            const isEven = idx % 2 === 0;

            return (
              <div 
                key={service.id} 
                className={`grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center ${
                  isEven ? "" : "lg:flex-row-reverse"
                }`}
              >
                {/* Visual Frame */}
                <motion.div
                  initial={{ opacity: 0, x: isEven ? -40 : 40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                  className={`lg:col-span-6 relative aspect-[4/3] rounded-lg overflow-hidden border border-white/10 group ${
                    isEven ? "lg:order-1" : "lg:order-2"
                  }`}
                >
                  <img 
                    src={service.img} 
                    alt={service.title} 
                    className="w-full h-full object-cover grayscale transition-all duration-700 group-hover:scale-105 group-hover:grayscale-0"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-dark/90 via-dark/40 to-transparent"></div>
                  
                  {/* Floating Service Badge */}
                  <div className="absolute bottom-6 left-6 z-10 flex items-center gap-3 bg-dark/80 border border-white/10 px-5 py-3 rounded-lg backdrop-blur-md">
                    <Icon className="text-primary w-6 h-6" />
                    <div>
                      <span className="text-[10px] text-gray-500 uppercase tracking-widest block font-bold leading-none mb-1">Division</span>
                      <span className="text-xs font-semibold text-white tracking-wide">{service.title}</span>
                    </div>
                  </div>
                </motion.div>

                {/* Text Content */}
                <motion.div
                  initial={{ opacity: 0, x: isEven ? 40 : -40 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6 }}
                  className={`lg:col-span-6 flex flex-col items-start ${
                    isEven ? "lg:order-2" : "lg:order-1"
                  }`}
                >
                  <span className="text-xs text-primary font-bold uppercase tracking-widest mb-2 block">
                    {service.subtitle}
                  </span>
                  <h3 className="font-display font-extrabold text-2xl md:text-3xl text-white mb-6">
                    {service.title}
                  </h3>
                  <p className="text-gray-400 text-sm md:text-base leading-relaxed mb-6">
                    {service.description}
                  </p>

                  <ul className="flex flex-col gap-3.5 mb-8 w-full">
                    {service.deliverables.map((item, dIdx) => (
                      <li key={dIdx} className="flex gap-2.5 items-start text-xs md:text-sm text-gray-300">
                        <CheckCircle className="text-primary w-4.5 h-4.5 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="flex flex-wrap gap-4">
                    <Link
                      to="/contact"
                      className="bg-primary hover:bg-primary/95 text-dark font-display font-bold text-xs uppercase tracking-wider px-6 py-3 rounded transition-transform hover:-translate-y-0.5"
                    >
                      Book Consultation
                    </Link>
                    <a
                      href={whatsappUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 bg-transparent border border-white/10 hover:border-primary text-white font-display font-bold text-xs uppercase tracking-wider px-6 py-3 rounded transition-colors glass"
                    >
                      <MessageSquare className="w-4 h-4 text-green-500" />
                      Chat WhatsApp
                    </a>
                  </div>
                </motion.div>

              </div>
            );
          })}
        </div>
      </section>

      {/* 3. WORKFLOW METHODOLOGY */}
      <section className="py-24 bg-surface border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          
          <SectionHeader
            centered
            eyebrow="Our Process"
            title="Standard Construction Flow"
            subtitle="We implement a structured engineering pipeline to monitor structural milestones and guarantee quality."
          />

          <div className="grid grid-cols-1 md:grid-cols-5 gap-8 mt-12 relative">
            {/* Connecting line */}
            <div className="absolute top-1/2 left-10 right-10 h-[1px] bg-white/5 hidden md:block z-0"></div>

            {steps.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="bg-dark border border-white/5 p-6 rounded-lg relative z-10 flex flex-col group hover:border-primary/20 transition-colors"
              >
                <span className="font-display font-black text-2xl md:text-3xl text-primary/20 group-hover:text-primary transition-colors block mb-4">
                  {item.step}
                </span>
                <h4 className="font-display font-bold text-sm text-white uppercase tracking-wider mb-2">
                  {item.title}
                </h4>
                <p className="text-gray-500 text-xs leading-relaxed">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

    </div>
  );
}
