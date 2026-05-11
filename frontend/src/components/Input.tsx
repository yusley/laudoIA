import { forwardRef } from "react";
import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input(props, ref) {
    return (
      <input
        ref={ref}
        {...props}
        className={`w-full rounded-2xl border border-black/10 bg-white px-4 py-3 outline-none transition focus:border-ember ${props.className || ""}`}
      />
    );
  },
);

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(
  function Textarea(props, ref) {
    return (
      <textarea
        ref={ref}
        {...props}
        className={`w-full rounded-2xl border border-black/10 bg-white px-4 py-3 outline-none transition focus:border-ember ${props.className || ""}`}
      />
    );
  },
);
