import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { loadEntries, clearEntries } from "../storage";
import { colors, spacing, radius, typography } from "../theme";

export default function HistoryScreen() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  // Перечитываем историю каждый раз, когда экран получает фокус —
  // так она всегда актуальна, даже если траты добавили только что.
  useFocusEffect(
    useCallback(() => {
      let isActive = true;
      setLoading(true);
      loadEntries().then((stored) => {
        if (!isActive) return;
        // Показываем сначала самые свежие траты.
        const sorted = [...stored].sort((a, b) => (a.date < b.date ? 1 : -1));
        setEntries(sorted);
        setLoading(false);
      });
      return () => {
        isActive = false;
      };
    }, [])
  );

  const handleClear = () => {
    if (entries.length === 0) return;
    Alert.alert(
      "Очистить историю?",
      "Все сохранённые траты будут удалены без возможности восстановления.",
      [
        { text: "Отмена", style: "cancel" },
        {
          text: "Очистить",
          style: "destructive",
          onPress: async () => {
            await clearEntries();
            setEntries([]);
          },
        },
      ]
    );
  };

  const total = entries.reduce((sum, entry) => sum + entry.amount, 0);

  return (
    <View style={styles.container}>
      <FlatList
        data={entries}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.headerTitle}>
              {loading
                ? "Загрузка..."
                : entries.length === 0
                ? "История пуста"
                : `${entries.length} ${entries.length === 1 ? "запись" : "записей"} · всего ${total.toFixed(2)}`}
            </Text>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Text style={styles.emptyState}>
              Здесь появится вся история трат, которые ты когда-либо добавлял(а).
            </Text>
          ) : null
        }
        renderItem={({ item }) => (
          <View style={styles.entryRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.entryDescription}>{item.description}</Text>
              <Text style={styles.entryDate}>{item.date}</Text>
            </View>
            <Text style={styles.entryAmount}>{item.amount.toFixed(2)}</Text>
          </View>
        )}
      />

      <TouchableOpacity
        style={[styles.clearButton, entries.length === 0 && styles.clearButtonDisabled]}
        onPress={handleClear}
        disabled={entries.length === 0}
      >
        <Text style={styles.clearButtonText}>Очистить историю</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  listContent: {
    padding: spacing.md,
    paddingBottom: spacing.xl,
  },
  header: {
    marginBottom: spacing.sm,
  },
  headerTitle: {
    ...typography.caption,
    color: colors.textSecondary,
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
  },
  clearButton: {
    margin: spacing.md,
    backgroundColor: colors.danger,
    borderRadius: radius.md,
    paddingVertical: 16,
    alignItems: "center",
  },
  clearButtonDisabled: {
    backgroundColor: colors.surfaceElevated,
  },
  clearButtonText: {
    color: colors.textPrimary,
    fontWeight: "700",
    fontSize: 16,
  },
});
