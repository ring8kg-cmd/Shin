import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 32) {
                Spacer()

                VStack(spacing: 16) {
                    ZStack {
                        RoundedRectangle(cornerRadius: 24)
                            .fill(Color(red: 1.0, green: 0.898, blue: 0.0))
                            .frame(width: 100, height: 100)
                        Image(systemName: "message.fill")
                            .font(.system(size: 48))
                            .foregroundStyle(.black)
                    }

                    Text("KakaoShortcuts")
                        .font(.largeTitle.bold())

                    Text("Quickly send KakaoTalk messages\nfrom Apple Shortcuts or Siri.")
                        .font(.body)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }

                Spacer()

                VStack(spacing: 12) {
                    NavigationLink(destination: ComposeView()) {
                        Label("Compose a Message", systemImage: "square.and.pencil")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color(red: 1.0, green: 0.898, blue: 0.0))
                            .foregroundStyle(.black)
                            .fontWeight(.semibold)
                            .cornerRadius(14)
                    }

                    Text("Or use the Shortcuts app / Siri:\n\"Send KakaoTalk message with KakaoShortcuts\"")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.horizontal, 32)

                Spacer()
                    .frame(height: 24)
            }
            .padding()
            .navigationTitle("KakaoShortcuts")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}
