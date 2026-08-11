import SwiftUI

struct ComposeView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var contacts: [ContactPerson] = []
    @State private var selectedContact: ContactPerson?
    @State private var messageText = ""
    @State private var isLoadingContacts = false
    @State private var contactsError: String?
    @State private var didSend = false

    var body: some View {
        Form {
            Section("To") {
                if isLoadingContacts {
                    HStack {
                        ProgressView()
                        Text("Loading contacts\u{2026}")
                            .foregroundStyle(.secondary)
                    }
                } else if let error = contactsError {
                    Text(error)
                        .foregroundStyle(.red)
                        .font(.caption)
                } else {
                    Picker("Contact", selection: $selectedContact) {
                        Text("Select a contact")
                            .tag(nil as ContactPerson?)
                        ForEach(contacts) { contact in
                            Text(contact.fullName)
                                .tag(contact as ContactPerson?)
                        }
                    }
                }
            }

            Section("Message") {
                TextEditor(text: $messageText)
                    .frame(minHeight: 120)
            }

            Section {
                HStack {
                    Spacer()
                    Text("\(messageText.count) characters")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            if didSend {
                Section {
                    HStack(spacing: 8) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                        Text("Message copied! Paste it in KakaoTalk.")
                            .font(.footnote)
                    }
                }
            }

            Section {
                Button(action: sendAction) {
                    Label("Copy & Open KakaoTalk", systemImage: "paperplane.fill")
                        .frame(maxWidth: .infinity)
                        .fontWeight(.semibold)
                }
                .disabled(selectedContact == nil || messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                .foregroundStyle(.black)
                .listRowBackground(
                    (selectedContact == nil || messageText.isEmpty)
                        ? Color.yellow.opacity(0.4)
                        : Color.yellow
                )
            } footer: {
                Text("Your message is copied to the clipboard. Find the contact in KakaoTalk and paste to send.")
            }
        }
        .navigationTitle("Compose")
        .navigationBarTitleDisplayMode(.inline)
        .task { await loadContacts() }
    }

    private func loadContacts() async {
        isLoadingContacts = true
        contactsError = nil
        do {
            contacts = try await ContactsService.shared.fetchAll()
        } catch {
            contactsError = error.localizedDescription
        }
        isLoadingContacts = false
    }

    private func sendAction() {
        let trimmed = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        UIPasteboard.general.string = trimmed
        didSend = true

        if let url = URL(string: "kakaotalk://") {
            UIApplication.shared.open(url)
        }
    }
}
