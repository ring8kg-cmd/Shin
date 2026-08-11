import AppIntents
import UIKit

struct SendKakaoMessageIntent: AppIntent {
    static var title: LocalizedStringResource = "Send KakaoTalk Message"
    static var description = IntentDescription(
        "Copies your message to the clipboard and opens KakaoTalk. Paste the message in the chat and tap Send.",
        categoryName: "Messaging"
    )

    @Parameter(title: "Recipient")
    var recipient: ContactEntity

    @Parameter(
        title: "Message",
        inputOptions: String.IntentInputOptions(
            capitalizationType: .sentences,
            multiline: true
        )
    )
    var message: String

    func perform() async throws -> some ProvidesDialog {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            throw $message.needsValueError("Please enter a message.")
        }

        await MainActor.run {
            UIPasteboard.general.string = trimmed
            if let url = URL(string: "kakaotalk://") {
                UIApplication.shared.open(url)
            }
        }

        return .result(
            dialog: "Message copied. Find \(recipient.fullName) in KakaoTalk and paste to send."
        )
    }
}
