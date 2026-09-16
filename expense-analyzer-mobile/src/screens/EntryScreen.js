import React, { useState, useRef, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { analyzeTransactions } from "../localAnalyzer";
import { loadEntries, saveEntries } from "../storage";
import { colors, spacing, radius, typography } from "../theme";

function todayString() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function EntryScreen({ navigation }) {
  const [date, setDate] = useState(todayString());
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);
  const nextIdRef = useRef(1);

  // Подгружаем сохранённые траты при каждом открытии экрана — в том числе
  // при первом запуске приложения и при возврате с экрана истории
  // (например, после того как там нажали «Очистить»).
  useFocusEffect(
    useCallback(() => {
      let isActive = true;
      loadEntries().then((stored) => {
        if (!isActive) return;
        setEntries(stored);
        const maxId = stored.reduce((max, entry) => Math.max(max, entry.id || 0), 0);
        nextIdRef.current = maxId + 1;
        setReady(true);
      });
      return () => {
        isActive = false;
      };
    }, [])
  );

  const addEntry = () => {
    const parsedAmount = parseFloat(amount.replace(",", "."));

    if (!description.trim()) {
      Alert.alert("Заполни описание", "Например: «Пятёрочка» или «Такси»");
      return;
    }
    if (!amount || Number.isNaN(parsedAmount) || parsedAmount <= 0) {
      Alert.alert("Некорректная сумма", "Введи сумму больше нуля");
      return;
    }

    const newEntry = {
      id: nextIdRef.current++,
      date,
      description: description.trim(),
      amount: parsedAmount,
    };
    const updated = [newEntry, ...entries];
    setEntries(updated);
    saveEntries(updated); // сохраняем сразу, чтобы трата пережила перезапуск приложения
    setDescription("");
    setAmount("");
  };

  const removeEntry = (id) => {
    const updated = entries.filter((entry) => entry.id !== id);
    setEntries(updated);
    saveEntries(updated);
  };

  const handleAnalyze = async () => {
    if (entries.length === 0) {
      Alert.alert("Нет трат", "Добавь хотя бы одну трату перед анализом");
      return;
    }

    setLoading(true);
    try {
      const payload = entries.map(({ date, description, amount }) => ({
        date,
        description,
        amount,
      }));
      const data = analyzeTransactions(payload);
      navigation.navigate("Report", { data });
    } catch (error) {
      Alert.alert("Ошибка", "Не удалось выполнить локальный анализ. Проверь данные трат.");
    } finally {
      setLoading(false);
    }
  };

  const total = entries.reduce((sum, entry) => sum + entry.amount, 0);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.form}>
        <TouchableOpacity
          style={styles.historyButton}
          onPress={() => navigation.navigate("History")}
        >
          <Text style={styles.historyButtonText}>📜 История трат</Text>
        </TouchableOpacity>

        <Text style={styles.label}>Дата</Text>
        <TextInput
          style={styles.input}
          value={date}
          onChangeText={setDate}
          placeholder="ГГГГ-ММ-ДД"
          placeholderTextColor={colors.textMuted}
        />

        <Text style={styles.label}>Описание</Text>
        <TextInput
          style={styles.input}
          value={description}
          onChangeText={setDescription}
          placeholder="Например: Пятёрочка"
          placeholderTextColor={colors.textMuted}
        />

        <Text style={styles.label}>Сумма</Text>
        <TextInput
          style={styles.input}
          value={amount}
          onChangeText={setAmount}
          placeholder="0.00"
          placeholderTextColor={colors.textMuted}
          keyboardType="decimal-pad"
        />

        <TouchableOpacity style={styles.addButton} onPress={addEntry}>
          <Text style={styles.addButtonText}>+ Добавить трату</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={entries}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        ListHeaderComponent={
          entries.length > 0 ? (
            <Text style={styles.listHeader}>
              {entries.length} {entries.length === 1 ? "трата" : "трат"} · всего{" "}
              {total.toFixed(2)}
            </Text>
          ) : (
            <Text style={styles.emptyState}>
              Пока ничего не добавлено — заполни форму выше
            </Text>
          )
        }
        renderItem={({ item }) => (
          <View style={styles.entryRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.entryDescription}>{item.description}</Text>
              <Text style={styles.entryDate}>{item.date}</Text>
            </View>
            <Text style={styles.entryAmount}>{item.amount.toFixed(2)}</Text>
            <TouchableOpacity onPress={() => removeEntry(item.id)} style={styles.removeButton}>
              <Text style={styles.removeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>
        )}
      />

      <TouchableOpacity
        style={[styles.analyzeButton, entries.length === 0 && styles.analyzeButtonDisabled]}
        onPress={handleAnalyze}
        disabled={loading || entries.length === 0}
      >
        {loading ? (
          <ActivityIndicator color={colors.textPrimary} />
        ) : (
          <Text style={styles.analyzeButtonText}>Проанализировать</Text>
        )}
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  form: {
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  label: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    marginTop: spacing.sm,
  },
  input: {
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: 12,
    color: colors.textPrimary,
    fontSize: 15,
    borderWidth: 1,
    borderColor: colors.border,
  },
  historyButton: {
    marginTop: spacing.sm,
    marginBottom: spacing.xs,
    backgroundColor: colors.surfaceElevated,
    borderRadius: radius.md,
    paddingVertical: 10,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  historyButtonText: {
    color: colors.textSecondary,
    fontWeight: "600",
    fontSize: 14,
  },
  addButton: {
    marginTop: spacing.md,
    backgroundColor: colors.accentMuted,
    borderRadius: radius.md,
    paddingVertical: 12,
    alignItems: "center",
  },
  addButtonText: {
    color: colors.textPrimary,
    fontWeight: "600",
    fontSize: 15,
  },
  listContent: {
    padding: spacing.md,
    paddingBottom: spacing.xl,
  },
  listHeader: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  emptyState: {
    ...typography.body,
    color: colors.textMuted,
    textAlign: "center",
    marginTop: spacing.xl,
  },
  entryRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  entryDescription: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "500",
  },
  entryDate: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: 2,
  },
  entryAmount: {
    color: colors.danger,
    fontSize: 15,
    fontWeight: "600",
    marginRight: spacing.sm,
  },
  removeButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.surfaceElevated,
    alignItems: "center",
    justifyContent: "center",
  },
  removeButtonText: {
    color: colors.textSecondary,
    fontSize: 14,
  },
  analyzeButton: {
    margin: spacing.md,
    backgroundColor: colors.accent,
    borderRadius: radius.md,
    paddingVertical: 16,
    alignItems: "center",
  },
  analyzeButtonDisabled: {
    backgroundColor: colors.surfaceElevated,
  },
  analyzeButtonText: {
    color: colors.textPrimary,
    fontWeight: "700",
    fontSize: 16,
  },
});
