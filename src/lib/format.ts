export const pad = (n: number) => String(n).padStart(2, '0');

export const todayLabel = () => new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
