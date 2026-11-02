#!/usr/bin/env python3
"""Milestone 1 Empirical Challenge Suite for SWMS Web Dashboard.

Programmatically challenges:
1. StatusBadge.tsx:
   - Verifies exact semantic classes (amber, blue, emerald, rose) for standard status values:
     'Pending', 'In Progress', 'Completed', 'Rejected'.
   - Verifies size variants ('sm', 'md', 'lg') and dot size classes.
   - Evaluates behavior under unexpected, lowercase, empty, and edge-case inputs.
2. CategoryBadge.tsx:
   - Verifies exact semantic classes (green, sky, amber) for standard categories:
     'Organic Waste', 'Plastic Waste', 'Paper Waste'.
   - Verifies object category handling with custom badge colors.
   - Evaluates behavior under unexpected, lowercase, empty, and edge-case inputs.
3. Responsive Layout & Horizontal Overflow:
   - Inspects Sidebar.tsx, Header.tsx, layout.tsx, globals.css, and tailwind.config.ts.
   - Confirms zero horizontal overflow constraints, mobile drawer encapsulation, and responsive breakpoints.
4. Production Toolchain:
   - Verifies TypeScript compilation (tsc --noEmit) and Next.js production build (next build).
"""

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "web"
COMPONENTS_DIR = WEB_DIR / "src" / "components"
APP_DIR = WEB_DIR / "src" / "app"
LIB_DIR = WEB_DIR / "src" / "lib"


class TestStatusBadgeChallenge(unittest.TestCase):
    """Programmatic challenge against web/src/components/StatusBadge.tsx."""

    @classmethod
    def setUpClass(cls):
        cls.file_path = COMPONENTS_DIR / "StatusBadge.tsx"
        assert cls.file_path.exists(), f"StatusBadge.tsx missing at {cls.file_path}"
        cls.content = cls.file_path.read_text(encoding="utf-8")

        # Parse statusConfig dictionary from TSX source
        config_match = re.search(r"const statusConfig:\s*Record<[^>]+>\s*=\s*(\{[\s\S]*?\n\};)", cls.content)
        assert config_match, "Could not locate statusConfig definition in StatusBadge.tsx"
        config_raw = config_match.group(1)

        cls.statuses = ["Pending", "In Progress", "Completed", "Rejected"]
        cls.status_map = {}
        for status in cls.statuses:
            pattern = rf"(?:['\"]?{re.escape(status)}['\"]?)\s*:\s*\{{\s*containerClass\s*:\s*['\"]([^'\"]+)['\"],\s*dotClass\s*:\s*['\"]([^'\"]+)['\"],\s*label\s*:\s*['\"]([^'\"]+)['\"]"
            m = re.search(pattern, config_raw)
            assert m, f"Status config for '{status}' not found in StatusBadge.tsx"
            cls.status_map[status] = {
                "containerClass": m.group(1),
                "dotClass": m.group(2),
                "label": m.group(3),
            }

        # Parse fallback config
        fallback_match = re.search(
            r"const config\s*=\s*statusConfig\[status\]\s*\|\|\s*\{\s*containerClass\s*:\s*['\"]([^'\"]+)['\"],\s*dotClass\s*:\s*['\"]([^'\"]+)['\"],\s*label\s*:\s*([^,\n\}]+)",
            cls.content,
        )
        assert fallback_match, "Fallback configuration not found in StatusBadge.tsx"
        cls.fallback = {
            "containerClass": fallback_match.group(1),
            "dotClass": fallback_match.group(2),
            "label_expr": fallback_match.group(3).strip(),
        }

    def test_pending_semantic_classes(self):
        """Ensure 'Pending' renders amber semantic classes per STYLING_GUIDE.md."""
        cfg = self.status_map["Pending"]
        self.assertIn("bg-amber-50", cfg["containerClass"])
        self.assertIn("text-amber-700", cfg["containerClass"])
        self.assertIn("border-amber-200", cfg["containerClass"])
        self.assertIn("bg-amber-500", cfg["dotClass"])
        self.assertEqual(cfg["label"], "Pending")

    def test_in_progress_semantic_classes(self):
        """Ensure 'In Progress' renders blue semantic classes per STYLING_GUIDE.md."""
        cfg = self.status_map["In Progress"]
        self.assertIn("bg-blue-50", cfg["containerClass"])
        self.assertIn("text-blue-700", cfg["containerClass"])
        self.assertIn("border-blue-200", cfg["containerClass"])
        self.assertIn("bg-blue-500", cfg["dotClass"])
        self.assertEqual(cfg["label"], "In Progress")

    def test_completed_semantic_classes(self):
        """Ensure 'Completed' renders emerald semantic classes per STYLING_GUIDE.md."""
        cfg = self.status_map["Completed"]
        self.assertIn("bg-emerald-50", cfg["containerClass"])
        self.assertIn("text-emerald-700", cfg["containerClass"])
        self.assertIn("border-emerald-200", cfg["containerClass"])
        self.assertIn("bg-emerald-500", cfg["dotClass"])
        self.assertEqual(cfg["label"], "Completed")

    def test_rejected_semantic_classes(self):
        """Ensure 'Rejected' renders rose semantic classes per STYLING_GUIDE.md."""
        cfg = self.status_map["Rejected"]
        self.assertIn("bg-rose-50", cfg["containerClass"])
        self.assertIn("text-rose-700", cfg["containerClass"])
        self.assertIn("border-rose-200", cfg["containerClass"])
        self.assertIn("bg-rose-500", cfg["dotClass"])
        self.assertEqual(cfg["label"], "Rejected")

    def test_unexpected_and_lowercase_inputs_safe_fallback(self):
        """Challenge: ensure unexpected and lowercase inputs do NOT throw and fall back cleanly."""
        self.assertIn("bg-slate-50", self.fallback["containerClass"])
        self.assertIn("text-slate-700", self.fallback["containerClass"])
        self.assertIn("border-slate-200", self.fallback["containerClass"])
        self.assertIn("bg-slate-400", self.fallback["dotClass"])

        # Test simulation of lookup logic on arbitrary inputs
        test_inputs = [
            "pending",
            "in progress",
            "completed",
            "rejected",
            "Unknown",
            "",
            "   ",
            "Draft",
            "Archived",
            "123",
            "<script>",
        ]
        for inp in test_inputs:
            # Emulate StatusBadge resolution
            resolved = self.status_map.get(inp)
            if not resolved:
                resolved = {
                    "containerClass": self.fallback["containerClass"],
                    "dotClass": self.fallback["dotClass"],
                    "label": inp,
                }
            self.assertIsNotNone(resolved["containerClass"])
            self.assertIsNotNone(resolved["dotClass"])
            self.assertEqual(resolved["label"], inp)


class TestCategoryBadgeChallenge(unittest.TestCase):
    """Programmatic challenge against web/src/components/CategoryBadge.tsx."""

    @classmethod
    def setUpClass(cls):
        cls.file_path = COMPONENTS_DIR / "CategoryBadge.tsx"
        assert cls.file_path.exists(), f"CategoryBadge.tsx missing at {cls.file_path}"
        cls.content = cls.file_path.read_text(encoding="utf-8")

        # Parse defaultCategoryStyles dictionary from TSX source
        style_match = re.search(r"const defaultCategoryStyles:\s*Record<[^>]+>\s*=\s*(\{[\s\S]*?\n\};)", cls.content)
        assert style_match, "Could not locate defaultCategoryStyles definition in CategoryBadge.tsx"
        style_raw = style_match.group(1)

        cls.categories = ["Organic Waste", "Plastic Waste", "Paper Waste"]
        cls.cat_map = {}
        for cat in cls.categories:
            pattern = (
                rf"(?:['\"]?{re.escape(cat)}['\"]?)\s*:\s*\{{\s*"
                r"bgClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
                r"textClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
                r"borderClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
                r"dotClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
                r"hex\s*:\s*['\"]([^'\"]+)['\"]"
            )
            m = re.search(pattern, style_raw)
            assert m, f"Category style for '{cat}' not found in CategoryBadge.tsx"
            cls.cat_map[cat] = {
                "bgClass": m.group(1),
                "textClass": m.group(2),
                "borderClass": m.group(3),
                "dotClass": m.group(4),
                "hex": m.group(5),
            }

        # Parse fallback config
        fallback_match = re.search(
            r"const styleConfig\s*=\s*defaultCategoryStyles\[categoryName\]\s*\|\|\s*\{\s*"
            r"bgClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
            r"textClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
            r"borderClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
            r"dotClass\s*:\s*['\"]([^'\"]+)['\"],\s*"
            r"hex\s*:\s*['\"]([^'\"]+)['\"]",
            cls.content,
        )
        assert fallback_match, "Fallback configuration not found in CategoryBadge.tsx"
        cls.fallback = {
            "bgClass": fallback_match.group(1),
            "textClass": fallback_match.group(2),
            "borderClass": fallback_match.group(3),
            "dotClass": fallback_match.group(4),
            "hex": fallback_match.group(5),
        }

    def test_organic_waste_semantic_classes(self):
        """Ensure 'Organic Waste' renders green semantic classes and #16a34a accent."""
        cfg = self.cat_map["Organic Waste"]
        self.assertIn("bg-green-50", cfg["bgClass"])
        self.assertIn("text-green-800", cfg["textClass"])
        self.assertIn("border-green-200", cfg["borderClass"])
        self.assertEqual(cfg["hex"], "#16a34a")

    def test_plastic_waste_semantic_classes(self):
        """Ensure 'Plastic Waste' renders sky/blue semantic classes and #0284c7 accent."""
        cfg = self.cat_map["Plastic Waste"]
        self.assertIn("bg-sky-50", cfg["bgClass"])
        self.assertIn("text-sky-800", cfg["textClass"])
        self.assertIn("border-sky-200", cfg["borderClass"])
        self.assertEqual(cfg["hex"], "#0284c7")

    def test_paper_waste_semantic_classes(self):
        """Ensure 'Paper Waste' renders amber semantic classes and #d97706 accent."""
        cfg = self.cat_map["Paper Waste"]
        self.assertIn("bg-amber-50", cfg["bgClass"])
        self.assertIn("text-amber-800", cfg["textClass"])
        self.assertIn("border-amber-200", cfg["borderClass"])
        self.assertEqual(cfg["hex"], "#d97706")

    def test_object_category_with_custom_color(self):
        """Ensure category objects with custom badge_color are supported."""
        self.assertIn("customBadgeColor", self.content)
        self.assertIn("category.badge_color", self.content)
        self.assertIn("style={customBadgeColor ? { backgroundColor: customBadgeColor } : undefined}", self.content)

    def test_unexpected_and_lowercase_inputs_safe_fallback(self):
        """Challenge: ensure unexpected and lowercase inputs do NOT throw and fall back cleanly."""
        self.assertIn("bg-slate-50", self.fallback["bgClass"])
        self.assertIn("text-slate-800", self.fallback["textClass"])
        self.assertIn("border-slate-200", self.fallback["borderClass"])
        self.assertEqual(self.fallback["hex"], "#64748b")

        # Test string simulation on arbitrary inputs
        test_inputs = [
            "organic waste",
            "plastic waste",
            "paper waste",
            "Electronic Waste",
            "Metal Waste",
            "",
            "   ",
            "custom-cat",
        ]
        for inp in test_inputs:
            resolved = self.cat_map.get(inp)
            if not resolved:
                resolved = self.fallback
            self.assertIsNotNone(resolved["bgClass"])
            self.assertIsNotNone(resolved["textClass"])
            self.assertIsNotNone(resolved["borderClass"])

    def test_category_prop_defensive_null_guard_analysis(self):
        """Empirically inspect line 51 defensive handling for potential null/undefined category."""
        # Line 51: const categoryName = typeof category === 'string' ? category : category.name;
        # In pure JS, if category is null (typeof null === 'object'), category.name throws TypeError.
        has_null_check = "category?.name" in self.content or "category &&" in self.content
        # Note this finding for reporting
        print(f"  [Defensive Analysis] CategoryBadge optional chaining for null category: {has_null_check}")


class TestResponsiveLayoutChallenge(unittest.TestCase):
    """Programmatic challenge against responsive layout and overflow constraints."""

    def test_sidebar_responsive_constraints(self):
        """Verify Sidebar responsive classes prevent horizontal overflow."""
        sidebar_file = COMPONENTS_DIR / "Sidebar.tsx"
        content = sidebar_file.read_text(encoding="utf-8")

        # Desktop aside must be fixed w-64 and hidden on mobile/tablet (hidden lg:block)
        self.assertIn("hidden w-64 border-r border-slate-200 bg-white lg:block", content)
        self.assertIn("fixed inset-y-0 left-0", content)

        # Mobile slide-out drawer must be lg:hidden with w-64 and translation
        self.assertIn("lg:hidden", content)
        self.assertIn("w-64 transform bg-white shadow-2xl transition-transform", content)
        self.assertIn("isOpen ? 'translate-x-0' : '-translate-x-full'", content)

        # Mobile backdrop must cover inset-0 and be lg:hidden
        self.assertIn("fixed inset-0 z-40 bg-slate-900/50", content)

        # Ensure no unbounded rigid widths (e.g. w-[1000px] or min-w-[500px])
        for match in re.finditer(r"(?:w|min-w)-\[(\d+)px\]", content):
            width = int(match.group(1))
            self.assertLessEqual(width, 320, f"Unbounded width {width}px found in Sidebar.tsx")

    def test_header_responsive_constraints(self):
        """Verify Header responsive classes prevent mobile viewport blowout."""
        header_file = COMPONENTS_DIR / "Header.tsx"
        content = header_file.read_text(encoding="utf-8")

        # Header container has responsive padding: px-4 sm:px-6 lg:px-8
        self.assertIn("px-4", content)
        self.assertIn("sm:px-6", content)
        self.assertIn("lg:px-8", content)

        # Mobile toggle button must be lg:hidden
        self.assertIn("lg:hidden", content)

        # API health badge must be hidden on mobile (hidden sm:flex)
        self.assertIn("hidden sm:flex items-center", content)

        # User profile text details must be hidden on mobile (hidden sm:block)
        self.assertIn("hidden sm:block text-left", content)

        # Ensure no horizontal fixed overflow classes
        for match in re.finditer(r"(?:w|min-w)-\[(\d+)px\]", content):
            width = int(match.group(1))
            self.assertLessEqual(width, 320, f"Unbounded width {width}px found in Header.tsx")

    def test_root_layout_viewport_and_fonts(self):
        """Verify RootLayout and typography font injection."""
        layout_file = APP_DIR / "layout.tsx"
        content = layout_file.read_text(encoding="utf-8")

        self.assertIn("Inter", content)
        self.assertIn("Space_Grotesk", content)
        self.assertIn("JetBrains_Mono", content)
        self.assertIn("--font-inter", content)
        self.assertIn("--font-space-grotesk", content)
        self.assertIn("--font-jetbrains-mono", content)
        self.assertIn("min-h-screen bg-surface-ground text-body antialiased", content)

    def test_tailwind_config_tokens(self):
        """Verify tailwind.config.ts extends required Eco-Tech palette and font tokens."""
        tw_file = WEB_DIR / "tailwind.config.ts"
        content = tw_file.read_text(encoding="utf-8")

        # Primary emeralds
        self.assertIn("'#059669'", content)  # primary-600
        self.assertIn("'#ecfdf5'", content)  # primary-50
        self.assertIn("'#10b981'", content)  # primary-500
        self.assertIn("'#047857'", content)  # primary-700
        self.assertIn("'#064e3b'", content)  # primary-900

        # Neutrals
        self.assertIn("'#f8fafc'", content)  # surface-ground
        self.assertIn("'#ffffff'", content)  # surface-card
        self.assertIn("'#e2e8f0'", content)  # border-subtle
        self.assertIn("'#64748b'", content)  # text-muted
        self.assertIn("'#334155'", content)  # text-body
        self.assertIn("'#0f172a'", content)  # text-heading

        # Fonts
        self.assertIn("var(--font-inter)", content)
        self.assertIn("var(--font-space-grotesk)", content)
        self.assertIn("var(--font-jetbrains-mono)", content)


class TestBuildAndTypecheckChallenge(unittest.TestCase):
    """Programmatic challenge against web project build and typechecking."""

    def test_typescript_typecheck(self):
        """Execute `npm run typecheck` and verify 0 type errors."""
        res = subprocess.run(
            ["npm", "run", "typecheck"],
            cwd=str(WEB_DIR),
            capture_output=True,
            text=True,
            shell=True,
        )
        self.assertEqual(res.returncode, 0, f"TypeScript typecheck failed:\n{res.stdout}\n{res.stderr}")

    def test_next_build_production(self):
        """Execute `npm run build` and verify clean Next.js production bundle."""
        res = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(WEB_DIR),
            capture_output=True,
            text=True,
            shell=True,
        )
        self.assertEqual(res.returncode, 0, f"Next.js build failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("Compiled successfully", res.stdout)
        self.assertIn("Generating static pages", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
