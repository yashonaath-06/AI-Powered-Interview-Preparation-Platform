"use client";
import { ButtonHTMLAttributes, forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "outline" | "danger";
type Size = "sm" | "md" | "lg";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-brand-500 text-white hover:bg-brand-600 disabled:bg-brand-300 shadow-sm",
  secondary:
    "bg-slate-900 text-white hover:bg-slate-800 disabled:bg-slate-400",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
  outline:
    "border border-slate-200 hover:border-slate-300 text-slate-800 bg-white",
  danger: "bg-red-500 text-white hover:bg-red-600",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
};

export const Button = forwardRef<HTMLButtonElement, Props>(
  (
    { className, variant = "primary", size = "md", loading, disabled, children, ...rest },
    ref,
  ) => (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium",
        "transition-colors focus:outline-none focus:ring-2 focus:ring-brand-300",
        "disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className,
      )}
      {...rest}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";
