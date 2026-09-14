import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { analyzeStatement } from "../api/client";

export default function UploadScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState(null);

  const pickAndAnalyze = async () => {
    const result = await DocumentPicker.getDocumentAsync({
      type: [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      ],
      copyToCacheDirectory: true,
    });

    if (result.canceled) {
      return;
    }

    const file = result.assets[0];
    setFileName(file.name);
    setLoading(true);

    try {
      const data = await analyzeStatement(file);
      navigation.navigate("Report", { data });
    } catch (error) {
      const message =
        error.response?.data?.error ||
        "Не удалось связаться с сервером. Проверь, что backend запущен и адрес в src/config.js указан верно.";
      Alert.alert("Ошибка", message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Анализ трат</Text>
      <Text style={styles.subtitle}>
        Выбери CSV или Excel файл с колонками date, description, amount
      </Text>

      <TouchableOpacity
        style={styles.button}
        onPress={pickAndAnalyze}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Выбрать файл</Text>
        )}
      </TouchableOpacity>

      {fileName && !loading ? (
        <Text style={styles.fileName}>Последний файл: {fileName}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f7f8fa",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
    color: "#6b7280",
    textAlign: "center",
    marginBottom: 32,
  },
  button: {
    backgroundColor: "#2563eb",
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
    minWidth: 200,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  fileName: {
    marginTop: 16,
    fontSize: 13,
    color: "#9ca3af",
  },
});
