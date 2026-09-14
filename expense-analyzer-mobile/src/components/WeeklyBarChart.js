import React from "react";
import { Dimensions, View } from "react-native";
import { BarChart } from "react-native-chart-kit";
import { colors, radius } from "../theme";

const screenWidth = Dimensions.get("window").width;

// react-native-chart-kit принимает цвета через rgba-функцию с параметром opacity
function hexToRgba(hex, opacity) {
  const parsed = hex.replace("#", "");
  const r = parseInt(parsed.substring(0, 2), 16);
  const g = parseInt(parsed.substring(2, 4), 16);
  const b = parseInt(parsed.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * @param {{byWeek: Array<{week: number, amount: number}>}} props
 */
export default function WeeklyBarChart({ byWeek }) {
  const chartData = {
    labels: byWeek.map((item) => `Нед. ${item.week}`),
    datasets: [{ data: byWeek.map((item) => item.amount) }],
  };

  return (
    <View>
      <BarChart
        data={chartData}
        width={screenWidth - 64}
        height={220}
        fromZero
        showValuesOnTopOfBars
        yAxisLabel=""
        yAxisSuffix=""
        chartConfig={{
          backgroundGradientFrom: colors.surface,
          backgroundGradientTo: colors.surface,
          decimalPlaces: 0,
          color: (opacity = 1) => hexToRgba(colors.accent, opacity),
          labelColor: (opacity = 1) => hexToRgba(colors.textSecondary, opacity),
          barPercentage: 0.6,
          propsForBackgroundLines: {
            stroke: colors.border,
          },
        }}
        style={{ borderRadius: radius.md }}
      />
    </View>
  );
}
