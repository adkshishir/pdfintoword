import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "outline" }
>(({ className, variant = "primary", ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50",
      variant === "primary" && "bg-cta text-white hover:bg-primary",
      variant === "secondary" && "bg-slate-200 text-slate-900 hover:bg-slate-300",
      variant === "outline" && "border border-slate-300 bg-white hover:bg-slate-50",
      className
    )}
    {...props}
  />
));
Button.displayName = "Button";
