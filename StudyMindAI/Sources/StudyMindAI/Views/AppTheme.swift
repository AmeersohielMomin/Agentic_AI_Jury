import SwiftUI

/// Cross-platform UI Color Palette supporting both macOS and iOS
public enum AppTheme {
    public static var cardBackground: Color {
        #if canImport(UIKit)
        return Color(uiColor: .secondarySystemBackground)
        #else
        return Color.gray.opacity(0.12)
        #endif
    }

    public static var nestedBackground: Color {
        #if canImport(UIKit)
        return Color(uiColor: .tertiarySystemBackground)
        #else
        return Color.gray.opacity(0.07)
        #endif
    }
}
