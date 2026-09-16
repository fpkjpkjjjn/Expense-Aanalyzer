// Простое хранилище трат поверх AsyncStorage.
// Все траты хранятся одним JSON-массивом под одним ключом —
// для этого приложения этого достаточно и не нужна отдельная БД.

import AsyncStorage from "@react-native-async-storage/async-storage";

const STORAGE_KEY = "@expense_analyzer/entries";

// Возвращает массив трат из памяти устройства.
// Если ничего не сохранено или данные повреждены — пустой массив.
export async function loadEntries() {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.warn("Не удалось загрузить траты из хранилища:", error);
    return [];
  }
}

// Полностью перезаписывает сохранённый список трат.
export async function saveEntries(entries) {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  } catch (error) {
    console.warn("Не удалось сохранить траты:", error);
  }
}

// Полностью очищает историю трат.
export async function clearEntries() {
  try {
    await AsyncStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn("Не удалось очистить историю трат:", error);
  }
}
