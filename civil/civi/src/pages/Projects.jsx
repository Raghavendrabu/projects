import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MapPin, Calendar, CircleDollarSign, X, ArrowUpRight, Scale } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

const categories = ["All", "Commercial", "Infrastructure", "Residential", "Interior"];

const projectsList = [
  {
    id: 1,
    title: "Skyline Corporate Tower",
    category: "Commercial",
    location: "Pune, MH",
    date: "2023",
    cost: "₹4.2 Cr",
    scope: "12-storey corporate complex, structural engineering, foundation design, and site contracting.",
    details: "Built using post-tensioned slabs and shear wall core structures to maximize interior space layout. High-strength M50 concrete mix tested directly at site.",
    img: "/images/hero_construction.png"
  },
  {
    id: 2,
    title: "NH-48 Overpass Bridge",
    category: "Infrastructure",
    location: "Bengaluru, KA",
    date: "2022",
    cost: "₹12 Cr",
    scope: "Design and construction supervision of a 120m prestressed concrete overpass bridge on National Highway 48.",
    details: "Utilized precast girder segments launched via hydraulic gantry. Heavy soil consolidation conducted prior to pile foundation capping.",
    img: "/images/civil_works.png"
  },
  {
    id: 3,
    title: "Green Valley Township",
    category: "Residential",
    location: "Nashik, MH",
    date: "2021",
    cost: "₹18 Cr",
    scope: "Residential township with 200 units, internal road network, and stormwater drainage systems.",
    details: "Implemented energy-efficient rainwater harvesting channels and customized structural layouts for independent duplex rows.",
    img: "/images/house_construction.png"
  },
  {
    id: 4,
    title: "Tata Industrial Warehouse",
    category: "Commercial",
    location: "Chakan, MH",
    date: "2023",
    cost: "₹6.8 Cr",
    scope: "Pre-engineered steel structure warehouse of 25,000 sq ft with deep concrete foundation work.",
    details: "Features a portal frame design spanning 40m without central columns. Multi-layered structural paint protects against industrial humidity.",
    img: "/images/renovation.png"
  },
  {
    id: 5,
    title: "Luxury Baner Penthouse",
    category: "Interior",
    location: "Pune, MH",
    date: "2024",
    cost: "₹85 Lakhs",
    scope: "Full-scale interior architecture, customized modular cabinetry, and automated ambient lighting systems.",
    details: "Italian Statuario marble flooring combined with acoustic veneered walls and concealed warm lighting lines.",
    img: "/images/interior_design.png"
  },
  {
    id: 6,
    title: "Koregaon Park Office",
    category: "Interior",
    location: "Pune, MH",
    date: "2024",
    cost: "₹1.2 Cr",
    scope: "Premium modern co-working and office space layout covering 6,000 sq ft.",
    details: "Glassmorphism office partition panels, custom acoustic board ceilings, and bespoke executive desk suites.",
    img: "/images/interior_design.png"
  }
];

export default function Projects() {
  const [activeFilter, setActiveFilter] = useState("All");
  const [selectedProject, setSelectedProject] = useState(null);

  const filteredProjects = activeFilter === "All"
    ? projectsList
    : projectsList.filter(p => p.category === activeFilter);

  return (
    <div className="w-full pt-28 pb-20">
      
      {/* 1. HERO HEADER */}
      <section className="relative py-16 bg-[#0f0f0f] border-b border-white/5 overflow-hidden">
        <div className="absolute inset-0 bg-stripes opacity-10 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
          <SectionHeader
            eyebrow="Our Work"
            title="Structural Landmark Portfolio"
            subtitle="Explore our projects spanning industrial, heavy civil infrastructure, residential, and corporate designs."
          />
        </div>
      </section>

      {/* 2. GALLERY SECTION */}
      <section className="py-16 bg-dark">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          
          {/* Filtering Buttons */}
          <div className="flex flex-wrap items-center gap-3 mb-12 border-b border-white/5 pb-6">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveFilter(cat)}
                className={`px-5 py-2.5 rounded font-display font-semibold text-xs uppercase tracking-wider transition-all duration-300 border ${
                  activeFilter === cat
                    ? "bg-primary border-primary text-dark font-extrabold shadow-lg shadow-primary/10"
                    : "bg-surface border-white/5 text-gray-400 hover:border-primary/30 hover:text-white"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Masonry Grid */}
          <motion.div 
            layout
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            <AnimatePresence mode="popLayout">
              {filteredProjects.map((project) => (
                <motion.div
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.4 }}
                  key={project.id}
                  onClick={() => setSelectedProject(project)}
                  className="group bg-surface border border-white/5 hover:border-primary/20 rounded-lg overflow-hidden cursor-pointer card-glow flex flex-col justify-between"
                >
                  <div>
                    {/* Image wrap with zoom */}
                    <div className="relative aspect-[16/10] overflow-hidden bg-dark">
                      <img 
                        src={project.img} 
                        alt={project.title} 
                        className="w-full h-full object-cover grayscale group-hover:grayscale-0 group-hover:scale-105 transition-all duration-500"
                      />
                      <div className="absolute inset-0 bg-dark/40 group-hover:bg-dark/10 transition-colors"></div>
                      
                      {/* Top Category Badge */}
                      <span className="absolute top-4 left-4 bg-dark/80 border border-white/10 text-primary text-[10px] uppercase font-bold tracking-widest px-3 py-1.5 rounded backdrop-blur-md">
                        {project.category}
                      </span>
                    </div>

                    <div className="p-6">
                      <span className="text-[10px] text-gray-500 uppercase tracking-widest flex items-center gap-1.5 mb-2 font-semibold">
                        <MapPin className="w-3.5 h-3.5" />
                        {project.location}
                      </span>
                      <h3 className="font-display font-bold text-lg text-white group-hover:text-primary transition-colors leading-tight mb-3">
                        {project.title}
                      </h3>
                      <p className="text-gray-400 text-xs md:text-sm leading-relaxed line-clamp-2">
                        {project.scope}
                      </p>
                    </div>
                  </div>

                  <div className="px-6 pb-6 pt-2 flex justify-between items-center border-t border-white/5 mt-auto">
                    <span className="font-display text-xs text-primary font-bold tracking-wider uppercase">
                      Budget: {project.cost}
                    </span>
                    <span className="text-xs text-gray-500 group-hover:text-primary transition-colors font-semibold flex items-center gap-1">
                      Details
                      <ArrowUpRight className="w-3.5 h-3.5 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        </div>
      </section>

      {/* 3. DETAILS MODAL DRAWER */}
      <AnimatePresence>
        {selectedProject && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4"
            onClick={() => setSelectedProject(null)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ duration: 0.3 }}
              className="bg-surface border border-white/10 rounded-lg max-w-2xl w-full overflow-hidden shadow-2xl relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedProject(null)}
                className="absolute top-4 right-4 bg-dark/80 hover:bg-dark border border-white/10 hover:border-primary text-white p-2 rounded-full z-20 transition-colors"
                aria-label="Close modal dialog"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Modal Image */}
              <div className="relative aspect-[16/9] w-full bg-dark">
                <img 
                  src={selectedProject.img} 
                  alt={selectedProject.title} 
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-dark/95 to-transparent"></div>
                <div className="absolute bottom-6 left-6 right-6">
                  <span className="bg-primary text-dark text-[10px] uppercase font-black tracking-widest px-3 py-1 rounded mb-2 inline-block">
                    {selectedProject.category}
                  </span>
                  <h2 className="font-display font-extrabold text-2xl md:text-3xl text-white leading-tight">
                    {selectedProject.title}
                  </h2>
                </div>
              </div>

              {/* Modal Details */}
              <div className="p-6 md:p-8 flex flex-col gap-6">
                
                {/* Meta Rows */}
                <div className="grid grid-cols-3 gap-4 bg-dark/50 border border-white/5 rounded-lg p-4 text-center">
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-1">Location</span>
                    <span className="text-xs font-bold text-white flex justify-center items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-primary shrink-0" />
                      {selectedProject.location}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-1">Delivered</span>
                    <span className="text-xs font-bold text-white flex justify-center items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-primary shrink-0" />
                      {selectedProject.date}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold block mb-1">Valuation</span>
                    <span className="text-xs font-bold text-white flex justify-center items-center gap-1">
                      <CircleDollarSign className="w-3.5 h-3.5 text-primary shrink-0" />
                      {selectedProject.cost}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col gap-4">
                  <div>
                    <h4 className="font-display font-bold text-xs uppercase tracking-wider text-primary mb-1">Scope of Work</h4>
                    <p className="text-gray-300 text-xs md:text-sm leading-relaxed">
                      {selectedProject.scope}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-display font-bold text-xs uppercase tracking-wider text-primary mb-1">Structural Details</h4>
                    <p className="text-gray-400 text-xs md:text-sm leading-relaxed">
                      {selectedProject.details}
                    </p>
                  </div>
                </div>

                <div className="border-t border-white/5 pt-6 flex justify-end gap-3">
                  <button
                    onClick={() => setSelectedProject(null)}
                    className="bg-transparent border border-white/10 hover:border-white/20 text-gray-400 hover:text-white px-5 py-2.5 rounded font-display font-bold text-xs uppercase tracking-wider transition-colors"
                  >
                    Close Dialog
                  </button>
                  <a
                    href="https://wa.me/918951529291?text=Hi%20Sulakhe%20Constructions,%20I'd%20like%20to%20inquire%20about%20your%20project%20architecture."
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-primary hover:bg-primary/95 text-dark px-5 py-2.5 rounded font-display font-bold text-xs uppercase tracking-wider transition-transform hover:-translate-y-0.5"
                  >
                    Inquire Similar Build
                  </a>
                </div>

              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
