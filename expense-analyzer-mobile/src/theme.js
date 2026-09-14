// Единая тёмная минималистичная палитра — меняй здесь, если захочешь
// перекрасить всё приложение разом.

export const colors = {
  background: "#0B0B0F",
  surface: "#16161D",
  surfaceElevated: "#1E1E27",
  border: "#2A2A34",

  textPrimary: "#F5F5F7",
  textSecondary: "#9CA3AF",
  textMuted: "#6B7280",

  accent: "#8B5CF6", // фиолетовый — основной акцент
  accentMuted: "#5B21B6",

  danger: "#F87171", // для сумм трат
  success: "#34D399",

  categoryPalette: [
    "#8B5CF6", // фиолетовый
    "#38BDF8", // голубой
    "#FBBF24", // жёлтый
    "#F472B6", // розовый
    "#34D399", // зелёный
    "#F87171", // красный
    "#60A5FA", // синий
    "#FB923C", // оранжевый
  ],
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
};

export const typography = {
  title: { fontSize: 28, fontWeight: "700" },
  subtitle: { fontSize: 15, fontWeight: "400" },
  sectionTitle: { fontSize: 16, fontWeight: "600" },
  body: { fontSize: 15, fontWeight: "500" },
  caption: { fontSize: 12, fontWeight: "400" },
};
