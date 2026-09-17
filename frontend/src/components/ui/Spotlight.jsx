import React, { useRef, useState, useEffect } from "react";
import { cn } from "../../lib/utils";

export const Spotlight = ({
  className,
  fill = "rgba(0, 242, 254, 0.12)",
  size = 400,
}) => {
  const containerRef = useRef(null);
  const [position, setPosition] = useState({ x: -1000, y: -1000 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (
        x >= -size &&
        x <= rect.width + size &&
        y >= -size &&
        y <= rect.height + size
      ) {
        setPosition({ x, y });
        setIsHovered(true);
      } else {
        setIsHovered(false);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [size]);

  return (
    <div
      ref={containerRef}
      className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}
    >
      <div
        className="pointer-events-none absolute rounded-full transition-opacity duration-300"
        style={{
          width: `${size}px`,
          height: `${size}px`,
          left: `${position.x - size / 2}px`,
          top: `${position.y - size / 2}px`,
          background: `radial-gradient(circle, ${fill} 0%, rgba(0,0,0,0) 70%)`,
          opacity: isHovered ? 1 : 0,
        }}
      />
    </div>
  );
};
