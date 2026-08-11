import Contacts
import Foundation

enum ContactsError: LocalizedError {
    case accessDenied

    var errorDescription: String? {
        "Contacts access was denied. Please enable it in Settings > Privacy > Contacts."
    }
}

final class ContactsService {
    static let shared = ContactsService()
    private init() {}

    func fetchAll() async throws -> [ContactPerson] {
        let store = CNContactStore()

        let granted = try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Bool, Error>) in
            store.requestAccess(for: .contacts) { granted, error in
                if let error { cont.resume(throwing: error) } else { cont.resume(returning: granted) }
            }
        }
        guard granted else { throw ContactsError.accessDenied }

        let keys = [
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactPhoneNumbersKey,
            CNContactIdentifierKey,
        ] as [CNKeyDescriptor]

        let request = CNContactFetchRequest(keysToFetch: keys)
        request.sortOrder = .givenName

        var results: [ContactPerson] = []
        try store.enumerateContacts(with: request) { contact, _ in
            if let person = ContactPerson(from: contact) {
                results.append(person)
            }
        }
        return results
    }
}
