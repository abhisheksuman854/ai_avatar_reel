import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const AvatarReelApp());
}

class AvatarReelApp extends StatelessWidget {
  const AvatarReelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Avatar Reel Generator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C47FF),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
