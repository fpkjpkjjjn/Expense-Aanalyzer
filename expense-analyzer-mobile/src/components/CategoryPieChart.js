import React from "react";
import { Dimensions, View } from "react-native";
import { PieChart } from "react-native-chart-kit";
import { colors } from "../theme";

const screenWidth = Dimensions.get("window").width;

/**
 * @param {{byCategory: Array<{category: string, amount: number}>}} props
 */
export default function CategoryPieChart({ byCategory }) {
  const chartData = byCategory.map((item, index) => ({
    name: item.category,
    amount: item.amount,
    color: colors.categoryPalette[index % colors.categoryPalette.length],
    legendFontColor: colors.textSecondary,
    legendFontSize: 13,
  }));

  return (
    <View>
      <PieChart
        data={chartData}
        width={screenWidth - 64}
        height={220}
        chartConfig={{
          color: () => colors.textPrimary,
        }}
        accessor="amount"
        backgroundColor="transparent"
        paddingLeft="8"
        absolute={false}
      />
    </View>
  );
}
