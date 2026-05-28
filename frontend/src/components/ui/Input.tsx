"use client";
import { forwardRef, InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string | null;
}

export const Input = forwardRef<HTMLInputElement, Props>(
  ({ label, error, className, id, ...rest }, ref) => {
    const inputId = id || rest.name;
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-slate-700 mb-1.5"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "block w-full rounded-lg border border-slate-200 bg-white px-3 py-2",
            "text-sm placeholder:text-slate-400",
            "focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200",
            "disabled:bg-slate-50 disabled:text-slate-500",
            error && "border-red-300 focus:border-red-400 focus:ring-red-200",
            className,
          )}
          {...rest}
        />
        {error && <p className="mt-1.5 text-xs text-red-600">{error}</p>}
      </div>
    );
  },
);
Input.displayName = "Input";
