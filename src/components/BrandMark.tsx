/** The story-bubble mark, shared by the masthead, snack bar, and favicon. */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 64 64"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
    >
      <path
        d="M9 9h46v36H30L16 56l2-11H9z"
        fill="#f6f0df"
        stroke="#27251e"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <path d="M45 9h10v10z" fill="#a13324" />
      <text
        x="13"
        y="39"
        fill="#27251e"
        fontFamily="Georgia, 'Times New Roman', serif"
        fontSize="27"
        fontWeight="700"
        letterSpacing="-3.5"
      >
        GT
      </text>
      <path d="M14 42h28" stroke="#a13324" strokeWidth="2.5" />
    </svg>
  );
}
