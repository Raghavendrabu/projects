import React from "react";
import { motion } from "framer-motion";

export default function SectionHeader({ eyebrow, title, subtitle, centered = false }) {
  return (
    <div className={`mb-12 md:mb-16 ${centered ? "text-center flex flex-col items-center" : ""}`}>
      {eyebrow && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2 mb-3"
        >
          {centered && <span className="w-8 h-[2px] bg-primary"></span>}
          <span className="text-primary font-display font-bold text-xs md:text-sm tracking-[0.25em] uppercase">
            {eyebrow}
          </span>
          <span className="w-8 h-[2px] bg-primary"></span>
        </motion.div>
      )}

      {title && (
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="font-display font-extrabold text-3xl md:text-4xl lg:text-5xl text-white tracking-tight leading-tight mb-4"
        >
          {title}
        </motion.h2>
      )}

      {subtitle && (
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-gray-400 max-w-2xl text-sm md:text-base leading-relaxed"
        >
          {subtitle}
        </motion.p>
      )}
    </div>
  );
}
