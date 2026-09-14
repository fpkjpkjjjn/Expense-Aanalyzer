import React from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import CategoryPieChart from "../components/CategoryPieChart";
import WeeklyBarChart from "../components/WeeklyBarChart";
import { colors, spacing, radius, typography } from "../theme";

export default function ReportScreen({ route, navigation }) {
  const { data } = route.params;
  const { total, by_category, by_week, top_transactions } = data;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.totalLabel}>Всего потрачено</Text>
      <Text style={styles.totalAmount}>{total.toFixed(2)}</Text>

      {by_category.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>По категориям</Text>
          <CategoryPieChart byCategory={by_category} />
        </View>
      ) : null}

      {by_week.length > 0 ? (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>По неделям</Text>
          <WeeklyBarChart byWeek={by_week} />
        </View>
      ) : null}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Топ трат</Text>
        {top_transactions.map((tx, index) => (
          <View key={index} style={styles.transactionRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.transactionDescription}>{tx.description}</Text>
              <Text style={styles.transactionMeta}>
                {tx.date} · {tx.category}
              </Text>
            </View>
            <Text style={styles.transactionAmount}>{tx.amount.toFixed(2)}</Text>
          </View>
        ))}
      </View>

      <TouchableOpacity
        style={styles.newButton}
        onPress={() => navigation.navigate("Entry")}
      >
        <Text style={styles.newButtonText}>Добавить ещё траты</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.md,
    paddingBottom: spacing.xl * 1.5,
  },
  totalLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
    marginTop: spacing.sm,
  },
  totalAmount: {
    fontSize: 40,
    fontWeight: "700",
    color: colors.textPrimary,
    textAlign: "center",
    marginBottom: spacing.lg,
  },
  section: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionTitle: {
    ...typography.sectionTitle,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  transactionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  transactionDescription: {
    fontSize: 15,
    color: colors.textPrimary,
    fontWeight: "500",
  },
  transactionMeta: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
  },
  transactionAmount: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.danger,
    marginLeft: spacing.sm,
  },
  newButton: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: 14,
    alignItems: "center",
  },
  newButtonText: {
    color: colors.accent,
    fontWeight: "600",
    fontSize: 15,
  },
});
