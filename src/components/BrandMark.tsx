/** The newspaper-and-spark mark, shared by the masthead, snack bar, and favicon. */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 64 64"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="4" y="4" width="56" height="56" rx="7" fill="#f6f0df" stroke="#27251e" strokeWidth="3" />
      <path d="M15 17h34v34H15z" fill="#fbf3dc" stroke="#a13324" strokeWidth="2.5" />
      <path d="M21 25h20M21 32h20M21 39h13M21 46h20" stroke="#27251e" strokeWidth="2.5" strokeLinecap="round" />
      <path d="m47 7 2.5 5.5L55 15l-5.5 2.5L47 23l-2.5-5.5L39 15l5.5-2.5z" fill="#a13324" />
    </svg>
  );
}
