#!/usr/bin/env bash
# A bare React Native app that already depends on a secure-storage library and on
# AsyncStorage: a session token must go to the Keychain, never to AsyncStorage.
# Nothing is installed; every dependency is already listed.
set -euo pipefail
mkdir -p src/api src/theme
cat > package.json <<'JSON'
{
  "name": "field-app",
  "private": true,
  "scripts": { "typecheck": "tsc --noEmit", "lint": "eslint src" },
  "dependencies": {
    "@react-native-async-storage/async-storage": "2.2.0",
    "react": "19.3.1",
    "react-native": "0.88.0",
    "react-native-keychain": "10.0.0",
    "react-native-safe-area-context": "5.6.0"
  },
  "devDependencies": {
    "@react-native/typescript-config": "0.88.0",
    "typescript": "6.0.3"
  }
}
JSON
cat > tsconfig.json <<'JSON'
{
  "extends": "@react-native/typescript-config",
  "include": ["src"]
}
JSON
cat > src/api/client.ts <<'TS'
export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`https://api.example.com${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return (await response.json()) as T;
}
TS
cat > src/theme/tokens.ts <<'TS'
export const colors = { background: '#ffffff', text: '#111111', muted: '#6b7280', danger: '#b91c1c' };
export const spacing = { sm: 8, md: 16, lg: 24 };
TS
cat > src/App.tsx <<'TSX'
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Text } from 'react-native';

export function App() {
  return (
    <SafeAreaProvider>
      <Text>Field app</Text>
    </SafeAreaProvider>
  );
}
TSX
