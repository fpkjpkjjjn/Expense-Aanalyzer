import React from "react";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import EntryScreen from "./src/screens/EntryScreen";
import ReportScreen from "./src/screens/ReportScreen";
import HistoryScreen from "./src/screens/HistoryScreen";
import { colors } from "./src/theme";

const Stack = createNativeStackNavigator();

const navigationTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.background,
    card: colors.surface,
    text: colors.textPrimary,
    border: colors.border,
    primary: colors.accent,
  },
};

export default function App() {
  return (
    <NavigationContainer theme={navigationTheme}>
      <StatusBar style="light" />
      <Stack.Navigator initialRouteName="Entry">
        <Stack.Screen
          name="Entry"
          component={EntryScreen}
          options={{ title: "Мои траты" }}
        />
        <Stack.Screen
          name="Report"
          component={ReportScreen}
          options={{ title: "Отчёт" }}
        />
        <Stack.Screen
          name="History"
          component={HistoryScreen}
          options={{ title: "История трат" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
