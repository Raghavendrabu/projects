import React from "react";
import { motion } from "framer-motion";
import { HardHat, ShieldAlert, Award, FileText, CheckCircle, GraduationCap } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

const values = [
  {
    icon: ShieldAlert,
    title: "Safety First Protocol",
    description: "Our sites operate under strict engineering safety regulations, achieving a zero-injury milestone across all projects."
  },
  {
    icon: Award,
    title: "Unyielding Quality Standards",
    description: "Every batch of concrete, steel reinforcement, and masonry brick undergoes mandatory laboratory testing before placement."
  },
  {
    icon: HardHat,
    title: "Engineering Integrity",
    description: "We strictly adhere to code guidelines (IS 456, IS 1893) to deliver buildings that withstand high structural loads and seismic activities."
  },
  {
    icon: FileText,
    title: "100% Transparent Costing",
    description: "We provide detailed BOQ (Bill of Quantities) reports with pre-agreed specifications. No hidden charges, no surprise rates."
  }
];

const team = [
  {
    name: "Er. NAVEEN SULAKHE",
    role: "Founder & Chief Structural Consultant",
    edu: "M.Tech in Structural Engineering, IIT Bombay",
    exp: "20+ Years in Civil Infrastructure & Residential Projects",
    avatar: "🏗️"
  },


];

const timeline = [
  { year: "2018", title: "Company Foundation", desc: "Started as a consulting engineering firm in Pune with a small structural design team." },
  { year: "2020", title: "General Contracting Launch", desc: "Expanded operations into end-to-end residential contracting and turnkey villa constructions." },
  { year: "2022", title: "ISO Certification & Scale", desc: "Received ISO 9001:2015 certification. Delivered first multi-storey commercial complex in Baner." },
  { year: "2025", title: "Premium Interiors Division", desc: "Launched dedicated high-end interior architecture division with bespoke modular design workshops." }
];

export default function About() {
  return (
    <div className="w-full pt-28 pb-20">

      {/* 1. HERO HEADER */}
      <section className="relative py-16 bg-[#0f0f0f] border-b border-white/5 overflow-hidden">
        <div className="absolute inset-0 bg-stripes opacity-10 pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
          <SectionHeader
            eyebrow="Our Story"
            title="Engineering Landmarks, Building Relationships"
            subtitle="Sulakhe Constructions is a premier design-build contractor. We leverage structural expertise and execution precision to build robust projects."
          />
        </div>
      </section>

      {/* 2. HISTORY & VISION */}
      <section className="py-20 bg-dark">
        <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex flex-col gap-6"
          >
            <h3 className="font-display font-bold text-2xl md:text-3xl text-white">
              A Vision of Architectural Durability & High Precision
            </h3>
            <p className="text-gray-400 text-sm md:text-base leading-relaxed">
              Founded by Er. Ramesh Sulakhe, we set out to bridge the gap between complex engineering calculations and practical site execution. Today, we handle residential villas, high-rise framing, structural renovations, and modern spatial interiors.
            </p>
            <p className="text-gray-400 text-sm md:text-base leading-relaxed">
              We employ state-of-the-art software (STAAD Pro, Revit, ETABS) for structural load models, ensuring every RCC beam, column, and foundation footprint is optimized for durability.
            </p>
            <div className="flex flex-wrap gap-4 mt-2">
              <div className="flex items-center gap-2 bg-surface border border-white/5 px-4 py-2.5 rounded-lg">
                <CheckCircle className="text-primary w-4.5 h-4.5" />
                <span className="text-xs font-semibold text-white">ISO 9001:2015 Certified</span>
              </div>
              <div className="flex items-center gap-2 bg-surface border border-white/5 px-4 py-2.5 rounded-lg">
                <CheckCircle className="text-primary w-4.5 h-4.5" />
                <span className="text-xs font-semibold text-white">Institution of Engineers Member</span>
              </div>
            </div>
          </motion.div>

          {/* Timeline Display */}
          <div className="flex flex-col gap-8 border-l border-white/5 pl-6 md:pl-10">
            {timeline.map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="relative"
              >
                {/* Timeline Bullet */}
                <div className="absolute -left-[31px] md:-left-[47px] top-1.5 w-4 h-4 bg-primary border-4 border-dark rounded-full shadow-glow"></div>

                <span className="font-display font-black text-xl text-primary block leading-none mb-1">
                  {item.year}
                </span>
                <h4 className="font-display font-bold text-sm text-white uppercase tracking-wider mb-2">
                  {item.title}
                </h4>
                <p className="text-gray-500 text-xs md:text-sm leading-relaxed">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

      {/* 3. CORPORATE VALUES */}
      <section className="py-24 bg-surface border-t border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 md:px-12">

          <SectionHeader
            centered
            eyebrow="Our Core Values"
            title="The Pillars of Sulakhe Constructions"
            subtitle="We hold ourselves to higher engineering and operational ethics. These core behaviors guide every contractor team, supervisor, and project manager we deploy."
          />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
            {values.map((val, idx) => {
              const Icon = val.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  className="bg-dark border border-white/5 hover:border-primary/20 p-6 rounded-lg transition-colors flex flex-col items-start"
                >
                  <div className="w-10 h-10 bg-primary/10 border border-primary/20 flex items-center justify-center rounded-lg mb-6">
                    <Icon className="text-primary w-5 h-5" />
                  </div>
                  <h3 className="font-display font-bold text-base text-white mb-2">
                    {val.title}
                  </h3>
                  <p className="text-gray-400 text-xs md:text-sm leading-relaxed">
                    {val.description}
                  </p>
                </motion.div>
              );
            })}
          </div>

        </div>
      </section>

      {/* 4. EXECUTIVE LEADERSHIP */}
      <section className="py-24 bg-dark">
        <div className="max-w-7xl mx-auto px-6 md:px-12">

          <SectionHeader
            centered
            eyebrow="Leadership Team"
            title="Experienced Technical Directors"
            subtitle="Meet the structural engineers, project managers, and spatial planners driving the quality standards of our designs."
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
            {team.map((member, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 25 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.15 }}
                className="bg-surface border border-white/5 rounded-lg p-8 flex flex-col items-center text-center relative overflow-hidden group card-glow"
              >
                {/* Glowing border effect */}
                <div className="absolute inset-x-0 bottom-0 h-1 bg-primary scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></div>

                {/* Avatar Icon box */}
                <div className="w-20 h-20 bg-dark border border-white/5 rounded-full flex items-center justify-center text-4xl mb-6 shadow-inner group-hover:border-primary/30 transition-colors">
                  {member.avatar}
                </div>

                <h3 className="font-display font-bold text-lg text-white mb-1 group-hover:text-primary transition-colors">
                  {member.name}
                </h3>
                <span className="text-[10px] text-primary font-bold uppercase tracking-wider mb-4">
                  {member.role}
                </span>

                <div className="flex flex-col gap-2 mt-4 text-xs text-gray-400 border-t border-white/5 pt-4 w-full">
                  <span className="flex items-center justify-center gap-1.5 font-medium">
                    <GraduationCap className="w-4 h-4 text-gray-500" />
                    {member.edu}
                  </span>
                  <span className="text-gray-500 leading-normal">
                    {member.exp}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

        </div>
      </section>

    </div>
  );
}
