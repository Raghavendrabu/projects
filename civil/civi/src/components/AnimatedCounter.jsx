import React, { useEffect, useState, useRef } from "react";
import { useInView } from "framer-motion";

export default function AnimatedCounter({ value, suffix = "", duration = 1.5 }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  useEffect(() => {
    if (isInView) {
      let start = 0;
      const end = parseInt(value, 10);
      if (isNaN(end)) {
        setCount(value);
        return;
      }
      if (end === 0) return;

      const totalMiliseconds = duration * 1000;
      // We want to update count in steps. Let's make updates every 30ms.
      const stepTime = 30;
      const steps = totalMiliseconds / stepTime;
      const increment = end / steps;

      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setCount(end);
          clearInterval(timer);
        } else {
          setCount(Math.floor(start));
        }
      }, stepTime);

      return () => clearInterval(timer);
    }
  }, [isInView, value, duration]);

  return (
    <span ref={ref} className="font-display font-black text-4xl md:text-5xl lg:text-6xl text-primary text-glow select-none">
      {count}
      {suffix}
    </span>
  );
}
