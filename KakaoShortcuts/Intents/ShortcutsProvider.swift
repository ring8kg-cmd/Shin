import AppIntents

struct KakaoShortcutsProvider: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: SendKakaoMessageIntent(),
            phrases: [
                "Send KakaoTalk message with \(.applicationName)",
                "KakaoTalk someone via \(.applicationName)",
                "Message a contact on KakaoTalk with \(.applicationName)",
            ],
            shortTitle: "Send KakaoTalk",
            systemImageName: "message.fill"
        )
    }
}
