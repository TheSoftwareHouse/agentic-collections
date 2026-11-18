#!/usr/bin/env bash
# An Expo Router app with routes under src/app/ and components under src/components/:
# the new screen is a route, its reusable row is not. Nothing is installed.
set -euo pipefail
mkdir -p src/app src/components src/theme
cat > package.json <<'JSON'
{
  "name": "field-app",
  "private": true,
  "main": "expo-router/entry",
  "scripts": { "start": "expo start", "typecheck": "tsc --noEmit", "lint": "eslint src" },
  "dependencies": {
    "expo": "~58.0.0",
    "expo-router": "~58.0.0",
    "react": "19.3.1",
    "react-native": "0.88.0",
    "react-native-safe-area-context": "5.6.0",
    "react-native-screens": "4.16.0"
  },
  "devDependencies": {
    "typescript": "6.0.3"
  }
}
JSON
cat > app.json <<'JSON'
{
  "expo": { "name": "field-app", "slug": "field-app", "scheme": "fieldapp", "plugins": ["expo-router"] }
}
JSON
cat > tsconfig.json <<'JSON'
{
  "extends": "expo/tsconfig.base",
  "include": ["src", ".expo/types/**/*.ts", "expo-env.d.ts"]
}
JSON
cat > src/theme/tokens.ts <<'TS'
export const colors = { background: '#ffffff', text: '#111111', muted: '#6b7280', border: '#e5e7eb' };
export const spacing = { sm: 8, md: 16, lg: 24 };
TS
cat > src/components/Heading.tsx <<'TSX'
import { Text } from 'react-native';
import { colors } from '../theme/tokens';

export function Heading({ title }: { title: string }) {
  return <Text style={{ color: colors.text, fontSize: 24, fontWeight: '600' }}>{title}</Text>;
}
TSX
cat > src/app/_layout.tsx <<'TSX'
import { Stack } from 'expo-router';

export default function RootLayout() {
  return <Stack />;
}
TSX
cat > src/app/index.tsx <<'TSX'
import { View } from 'react-native';
import { Heading } from '../components/Heading';

export default function HomeScreen() {
  return (
    <View>
      <Heading title="Home" />
    </View>
  );
}
TSX
