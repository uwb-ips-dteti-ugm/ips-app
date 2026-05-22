"use client";

import Image from "next/image";
import {
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  useId,
} from "react";

import chevronDownIcon from "../assets/ChevronDownIcon.svg";

type FieldBaseProps = {
  className?: string;
  label: string;
};

type TextFieldProps = FieldBaseProps &
  InputHTMLAttributes<HTMLInputElement> & {
    inputClassName?: string;
  };

type SelectFieldProps = FieldBaseProps &
  SelectHTMLAttributes<HTMLSelectElement> & {
    children: ReactNode;
    selectClassName?: string;
  };

export function TextField({
  className = "",
  id,
  inputClassName = "",
  label,
  ...inputProps
}: TextFieldProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;

  return (
    <label
      className={`flex flex-col gap-1.5 text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5] ${className}`}
      htmlFor={inputId}
    >
      {label}
      <input
        id={inputId}
        className={`h-10 min-w-0 rounded-md border border-[#D9EEF7] bg-white px-3 text-sm font-normal normal-case text-[#0F2854] outline-none transition placeholder:text-[#4988C4] focus:border-[#4988C4] focus:ring-2 focus:ring-[#BDE8F5] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white dark:placeholder:text-[#BDE8F5]/70 ${inputClassName}`}
        {...inputProps}
      />
    </label>
  );
}

export function SelectField({
  children,
  className = "",
  id,
  label,
  selectClassName = "",
  ...selectProps
}: SelectFieldProps) {
  const generatedId = useId();
  const selectId = id ?? generatedId;

  return (
    <label
      className={`flex flex-col gap-1.5 text-xs font-semibold uppercase text-[#4988C4] dark:text-[#BDE8F5] ${className}`}
      htmlFor={selectId}
    >
      {label}
      <div className="relative min-w-0">
        <select
          id={selectId}
          className={`h-10 w-full appearance-none rounded-md border border-[#D9EEF7] bg-white px-3 pr-9 text-sm font-medium normal-case text-[#0F2854] outline-none transition focus:border-[#4988C4] focus:ring-2 focus:ring-[#BDE8F5] disabled:cursor-not-allowed disabled:opacity-60 dark:border-[#1C4D8D] dark:bg-[#07111F] dark:text-white ${selectClassName}`}
          {...selectProps}
        >
          {children}
        </select>
        <Image
          src={chevronDownIcon}
          alt=""
          width={16}
          height={16}
          className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 dark:brightness-0 dark:invert"
        />
      </div>
    </label>
  );
}
