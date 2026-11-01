---
name: flutter-architecture-and-state
description: Flutter application architecture, state management (Bloc, Riverpod), widget tree optimization, memory leak prevention, platform integration, and Dart best practices. Use when building Flutter apps, refactoring widget hierarchies, or diagnosing performance drops.
---

# Flutter Architecture and State Management

Use this skill when developing cross-platform Flutter applications, structuring state management, avoiding rebuild bottlenecks, and maintaining high rendering frame rates (60/120 fps).

## 1. Architectural Layers & Separation
- **Domain Layer:** Pure Dart entities and use-cases. No Flutter UI dependencies (`import 'package:flutter/...'` is forbidden here).
- **Data Layer:** Repositories and DataSources (REST APIs, SQLite/Isar, SharedPreferences). Handles network serialization and caching.
- **Presentation Layer:** Widgets, Controllers/Notifiers/Blocs. Widgets must remain thin: they declare UI and delegate user intentions to the state container.

## 2. State Management Rules (Riverpod / Bloc)
- **Scope state tightly:** Avoid putting entire application state at the root `App` widget. Place providers/blocs as close as possible to the consumer widgets that read them.
- **Immutable State:** Always use immutable state classes (`freezed` or Dart records) so changes trigger deterministic rebuilds.
- **Separate events/intents from mutations:**
  - In Riverpod: use `AsyncNotifier` or `Notifier` with explicit public methods.
  - In Bloc: use distinct `Event` classes and emit new states using `on<Event>((event, emit) => ...)`.
- **Side Effects (Navigation / SnackBars):** Trigger side-effects in listeners (`ref.listen` in Riverpod, `BlocListener` in Bloc), never inside the `build()` method.

## 3. Widget Tree Optimization & Performance
- **Use `const` constructors aggressively:** Mark widgets `const` wherever properties do not change. This allows Flutter to bypass rebuilds entirely during frame rendering.
- **Granular Widgets over Big Build Methods:** Split large monolithic `build()` methods into separate private `StatelessWidget` classes rather than helper methods returning `Widget`. Helper methods re-evaluate with the parent; small widget classes maintain independent rebuild scopes.
- **Rebuild containment:** Use `Consumer` or `BlocBuilder` around only the specific text or icon that updates, not wrapping the entire screen scaffold.
- **Repaint Boundaries:** Wrap complex animations or custom canvas painters in `RepaintBoundary` to prevent invalidating the entire screen raster cache.

## 4. Disposal and Memory Leak Prevention
- Always dispose `TextEditingController`, `AnimationController`, `ScrollController`, and `StreamSubscription` inside `dispose()`.
- Cancel async operations if the widget is no longer mounted: check `if (!mounted) return;` before calling `setState` or touching context.
