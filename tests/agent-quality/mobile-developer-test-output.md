# React Native Tab Bar İskelet Uygulama

> React Native 0.82+ | TypeScript | React Navigation v6 Bottom Tabs

Bu belge, 3 sekmeli (Ana Sayfa, Keşfet, Profil) bir React Native iskelet uygulamasının tüm kaynak kodunu ve açıklamalarını içerir.

---

## 1. Proje Bağımlılıkları

Projeyi oluşturduktan sonra aşağıdaki paketleri yükleyin:

```bash
# React Navigation çekirdeği ve bottom tabs
npm install @react-navigation/native @react-navigation/bottom-tabs

# React Navigation gereksinimleri
npm install react-native-screens react-native-safe-area-context

# İkon paketi (tab ikonları için)
npm install react-native-vector-icons
npm install -D @types/react-native-vector-icons

# iOS için pod kurulumu
cd ios && pod install && cd ..
```

---

## 2. TypeScript Tip Tanımları

Tüm navigasyon parametreleri ve ekran prop'ları için merkezi tip dosyası. Bu dosya sayesinde ekranlar arası parametre geçişi tip-güvenli hale gelir.

```typescript
// src/types/navigation.ts

import type { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import type { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

/**
 * Bottom Tab Navigator için rota parametre haritası.
 * Her rota undefined alıyor çünkü bu iskelet yapıda
 * ekranlar arası parametre geçişi henüz yok.
 */
export type RootTabParamList = {
  Home: undefined;
  Explore: undefined;
  Profile: undefined;
};

/**
 * Her ekranın navigation ve route prop'larını
 * tek seferde çözümlemek için yardımcı tipler.
 */
export type HomeScreenProps = BottomTabScreenProps<RootTabParamList, 'Home'>;
export type ExploreScreenProps = BottomTabScreenProps<RootTabParamList, 'Explore'>;
export type ProfileScreenProps = BottomTabScreenProps<RootTabParamList, 'Profile'>;

/**
 * Eğer ileride bir NativeStack navigator eklenirse,
 * aşağıdaki composite tip kullanılabilir.
 */
export type RootStackParamList = {
  MainTabs: NavigatorScreenParams<RootTabParamList>;
};

export type RootStackScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;

/**
 * React Navigation'ın global tip desteği.
 * Bu sayede useNavigation() hook'u otomatik olarak
 * doğru tipleri döndürür.
 */
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootTabParamList {}
  }
}
```

---

## 3. Ekranlar (Screens)

### 3.1 HomeScreen — Ana Sayfa

```typescript
// src/screens/HomeScreen.tsx

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Platform,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import type { HomeScreenProps } from '../types/navigation';

const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar
        barStyle={Platform.OS === 'ios' ? 'dark-content' : 'light-content'}
        backgroundColor="#6200ee"
      />
      <View style={styles.container}>
        <Text style={styles.icon}>🏠</Text>
        <Text style={styles.title}>Ana Sayfa</Text>
        <Text style={styles.subtitle}>
          Hoş geldiniz! Burası uygulamanızın ana ekranıdır.
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  icon: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 8,
    // Platform-spesifik font ailesi
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
});

export default HomeScreen;
```

### 3.2 ExploreScreen — Keşfet

```typescript
// src/screens/ExploreScreen.tsx

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Platform,
  SafeAreaView,
} from 'react-native';
import type { ExploreScreenProps } from '../types/navigation';

const ExploreScreen: React.FC<ExploreScreenProps> = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.icon}>🔍</Text>
        <Text style={styles.title}>Keşfet</Text>
        <Text style={styles.subtitle}>
          Yeni içerikleri keşfedin ve ilgi alanlarınıza göre filtreleme yapın.
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  icon: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 8,
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
});

export default ExploreScreen;
```

### 3.3 ProfileScreen — Profil

```typescript
// src/screens/ProfileScreen.tsx

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Platform,
  SafeAreaView,
} from 'react-native';
import type { ProfileScreenProps } from '../types/navigation';

const ProfileScreen: React.FC<ProfileScreenProps> = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.icon}>👤</Text>
        <Text style={styles.title}>Profil</Text>
        <Text style={styles.subtitle}>
          Hesap ayarlarınızı yönetin ve profil bilgilerinizi güncelleyin.
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  icon: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 8,
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 24,
    ...Platform.select({
      ios: { fontFamily: 'System' },
      android: { fontFamily: 'Roboto' },
    }),
  },
});

export default ProfileScreen;
```

---

## 4. Bottom Tab Navigator Konfigürasyonu

Tab navigator'ı burada tanımlıyoruz. iOS ve Android için farklı tab bar stilleri `Platform.select` ile ayrıştırılıyor.

```typescript
// src/navigation/BottomTabNavigator.tsx

import React from 'react';
import { Platform, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/Ionicons';

import HomeScreen from '../screens/HomeScreen';
import ExploreScreen from '../screens/ExploreScreen';
import ProfileScreen from '../screens/ProfileScreen';
import type { RootTabParamList } from '../types/navigation';

const Tab = createBottomTabNavigator<RootTabParamList>();

/**
 * Tab ikonlarını rota adına göre döndüren yardımcı fonksiyon.
 * focused durumuna göre dolu/boş ikon varyantı seçilir.
 */
const getTabBarIcon = (
  routeName: keyof RootTabParamList,
  focused: boolean,
  color: string,
  size: number,
): React.ReactNode => {
  const iconMap: Record<keyof RootTabParamList, { focused: string; default: string }> = {
    Home: { focused: 'home', default: 'home-outline' },
    Explore: { focused: 'compass', default: 'compass-outline' },
    Profile: { focused: 'person', default: 'person-outline' },
  };

  const iconName = focused ? iconMap[routeName].focused : iconMap[routeName].default;
  return <Icon name={iconName} size={size} color={color} />;
};

const BottomTabNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      initialRouteName="Home"
      screenOptions={({ route }) => ({
        // --- İkon konfigürasyonu ---
        tabBarIcon: ({ focused, color, size }) =>
          getTabBarIcon(route.name, focused, color, size),

        // --- Renk ayarları ---
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: '#999999',

        // --- Header ayarları ---
        headerShown: true,
        headerTitleAlign: 'center',
        headerStyle: {
          backgroundColor: '#6200ee',
          // Android'de elevation ile gölge, iOS'ta shadow ile
          ...Platform.select({
            android: { elevation: 4 },
            ios: {
              shadowColor: '#000000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.15,
              shadowRadius: 4,
            },
          }),
        },
        headerTintColor: '#ffffff',
        headerTitleStyle: {
          fontWeight: '600' as const,
          fontSize: 18,
          ...Platform.select({
            ios: { fontFamily: 'System' },
            android: { fontFamily: 'Roboto' },
          }),
        },

        // --- Tab bar platform-spesifik stiller ---
        tabBarStyle: {
          // iOS: yarı saydam arka plan, blur efekti ile
          // Android: katı beyaz arka plan, elevation gölgesi ile
          ...Platform.select({
            ios: {
              backgroundColor: 'rgba(255, 255, 255, 0.92)',
              borderTopWidth: 0.5,
              borderTopColor: 'rgba(0, 0, 0, 0.12)',
              height: 88, // safe area dahil
              paddingBottom: 28, // home indicator alanı
              paddingTop: 8,
            },
            android: {
              backgroundColor: '#ffffff',
              borderTopWidth: 0,
              elevation: 8,
              height: 64,
              paddingBottom: 8,
              paddingTop: 8,
            },
          }),
        },

        // --- Tab label stili ---
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600' as const,
          ...Platform.select({
            ios: {
              fontFamily: 'System',
              marginBottom: 0,
            },
            android: {
              fontFamily: 'Roboto',
              marginBottom: 4,
            },
          }),
        },

        // --- Tab item'a basıldığında ripple/highlight ---
        tabBarPressColor: 'rgba(98, 0, 238, 0.12)', // Android ripple
        tabBarPressOpacity: 0.7, // iOS opacity
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarLabel: 'Ana Sayfa',
          headerTitle: 'Ana Sayfa',
          tabBarBadge: 3, // Örnek: bildirim rozeti
        }}
      />
      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{
          tabBarLabel: 'Keşfet',
          headerTitle: 'Keşfet',
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profil',
          headerTitle: 'Profil',
        }}
      />
    </Tab.Navigator>
  );
};

export default BottomTabNavigator;
```

---

## 5. Uygulama Giriş Noktası (App.tsx)

```typescript
// App.tsx

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import BottomTabNavigator from './src/navigation/BottomTabNavigator';

const App: React.FC = () => {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <BottomTabNavigator />
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
```

---

## 6. Dosya Yapısı Özeti

```
project-root/
├── App.tsx                              # Uygulama giriş noktası
├── src/
│   ├── types/
│   │   └── navigation.ts               # Tüm navigasyon tip tanımları
│   ├── screens/
│   │   ├── HomeScreen.tsx               # Ana Sayfa ekranı
│   │   ├── ExploreScreen.tsx            # Keşfet ekranı
│   │   └── ProfileScreen.tsx            # Profil ekranı
│   └── navigation/
│       └── BottomTabNavigator.tsx       # Tab navigator konfigürasyonu
├── package.json
└── tsconfig.json
```

---

## 7. Platform Farkları Özeti

| Özellik | iOS | Android |
|---|---|---|
| **Tab bar yüksekliği** | 88px (safe area dahil) | 64px |
| **Tab bar arka plan** | Yarı saydam (`rgba`) | Katı beyaz |
| **Tab bar kenarlık** | 0.5px üst çizgi | Yok (elevation kullanılır) |
| **Gölge efekti** | `shadowColor/Offset/Opacity/Radius` | `elevation: 8` |
| **Basma geri bildirimi** | Opacity azalması (0.7) | Material ripple efekti |
| **Alt padding** | 28px (home indicator) | 8px |
| **Font ailesi** | System (SF Pro) | Roboto |
| **StatusBar stili** | `dark-content` | `light-content` + renkli arka plan |
| **Header gölgesi** | iOS shadow özellikleri | `elevation: 4` |

---

## 8. Notlar

- **React Navigation v6** bottom tabs API'si kullanılmıştır. v7'ye geçişte `screenOptions` yapısı değişebilir.
- **react-native-vector-icons** paketi Ionicons setini kullanır. Alternatif olarak `@expo/vector-icons` da tercih edilebilir.
- `RootTabParamList` genişletilerek ekranlar arası parametre geçişi tip-güvenli şekilde yapılabilir.
- `declare global` bloğu sayesinde `useNavigation()` hook'u projenin herhangi bir yerinde doğru tipleri otomatik çözümler.
- Tab bar badge örneği (`tabBarBadge: 3`) HomeScreen'de gösterilmiştir; gerçek uygulamada bu değer state'ten gelmelidir.
